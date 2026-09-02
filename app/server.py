"""Small HTTP and SQL service for the BARQ DevOps assessment."""

import json
import os
import re
import signal
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


VERSION = "1.0.0"


def log_event(level, event, **fields):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "level": level,
        "service": "barq-status-api",
        "event": event,
        **fields,
    }
    print(json.dumps(record, separators=(",", ":")), flush=True)


class ApplicationServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, instance_id, message, database_url="", query_function=None):
        self.instance_id = instance_id
        self.message = message
        self.database_url = database_url
        self.query = query_function or self.database_query
        self.started_at = time.monotonic()
        super().__init__(address, Handler)

    def database_query(self, statement):
        import psycopg
        with psycopg.connect(self.database_url, connect_timeout=2, options="-c statement_timeout=2000") as connection:
            with connection.cursor() as cursor:
                cursor.execute(statement)
                return cursor.fetchall()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "BARQ-Status-API/1.0"

    def log_message(self, *_args):
        # Requests are emitted below as structured JSON rather than access text.
        pass

    def do_GET(self):
        self.respond(send_body=True)

    def do_HEAD(self):
        self.respond(send_body=False)

    def respond(self, send_body):
        started = time.perf_counter()
        path = urlsplit(self.path).path
        incoming = self.headers.get("X-Request-ID", "")
        request_id = incoming if re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", incoming) else uuid.uuid4().hex
        common = {"service": "barq-status-api", "instance_id": self.server.instance_id, "version": VERSION}

        if path == "/":
            status, body = 200, {**common, "message": self.server.message}
        elif path == "/api/info":
            status, body = 200, {**common, "message": self.server.message, "uptime_seconds": round(time.monotonic() - self.server.started_at, 3)}
        elif path in {"/health", "/api/items"}:
            try:
                if path == "/health":
                    if self.server.query("SELECT 1") != [(1,)]:
                        raise RuntimeError("Unexpected database readiness result")
                    status, body = 200, {**common, "status": "ok", "database": "ready"}
                else:
                    rows = self.server.query("SELECT id, title, done FROM items ORDER BY id")
                    status, body = 200, {**common, "items": [{"id": row[0], "title": row[1], "done": row[2]} for row in rows]}
            except Exception as exc:
                log_event("ERROR", "database_error", instance_id=self.server.instance_id, request_id=request_id,
                          error_type=type(exc).__name__, detail=str(exc))
                status, body = 503, {**common, "error": "database_unavailable"}
        else:
            status, body = 404, {**common, "error": "not_found", "path": path}

        payload = (json.dumps(body, sort_keys=True) + "\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Instance-ID", self.server.instance_id)
        self.send_header("X-Request-ID", request_id)
        self.end_headers()
        try:
            if send_body:
                self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            log_event("WARN", "client_disconnected", instance_id=self.server.instance_id, request_id=request_id, path=path)
        finally:
            log_event("INFO" if status < 400 else "WARN", "http_request", instance_id=self.server.instance_id,
                      request_id=request_id, method=self.command, path=path, status=status,
                      duration_ms=round((time.perf_counter() - started) * 1000, 3))


def main():
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = int(os.environ.get("APP_PORT", "8080"))
    instance = os.environ.get("INSTANCE_ID", "local")
    message = os.environ.get("APP_MESSAGE", "Welcome to BARQ Systems")
    database_url = os.environ.get("DATABASE_URL", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", instance):
        raise ValueError("INSTANCE_ID must contain 1-64 letters, digits, underscores or hyphens")
    server = ApplicationServer((host, port), instance, message, database_url=database_url)

    def stop(_signum, _frame):
        log_event("INFO", "shutdown_requested", instance_id=instance)
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    log_event("INFO", "configuration_loaded", instance_id=instance, database_url=database_url)
    log_event("INFO", "listening", instance_id=instance, host=host, port=server.server_port, version=VERSION)
    try:
        server.serve_forever(poll_interval=0.1)
    finally:
        server.server_close()
        log_event("INFO", "stopped", instance_id=instance)


if __name__ == "__main__":
    main()
