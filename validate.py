#!/usr/bin/env python3
"""Environment Validation Script for BARQ Systems DevOps Task."""

import json
import os
import socket
import sys
import time

try:
    import urllib.request as urllib_request
    import urllib.error as urllib_error
except ImportError:
    import urllib2 as urllib_request
    import urllib2 as urllib_error

PUBLIC_PORT = os.getenv("PUBLIC_PORT", "8090")
BASE_URL = os.getenv("BASE_URL", "http://localhost:{}".format(PUBLIC_PORT))

def log_result(test_name, success, details=""):
    status = "PASS" if success else "FAIL"
    msg = "[{}] {}".format(status, test_name)
    if details:
        msg += " - {}".format(details)
    print(msg)
    return success

def http_get(path, timeout=5):
    url = "{}{}".format(BASE_URL, path)
    req = urllib_request.Request(url, headers={"User-Agent": "BARQ-Validator"})
    try:
        resp = urllib_request.urlopen(req, timeout=timeout)
        data = resp.read().decode("utf-8")
        status = resp.getcode() if hasattr(resp, 'getcode') else resp.status
        try:
            body = json.loads(data)
        except Exception:
            body = data
        return status, body, resp.headers
    except urllib_error.HTTPError as e:
        data = e.read().decode("utf-8")
        try:
            body = json.loads(data)
        except Exception:
            body = data
        return e.code, body, e.headers
    except Exception as e:
        return 0, str(e), {}

def http_post(path, payload, timeout=5):
    url = "{}{}".format(BASE_URL, path)
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib_request.Request(
        url, data=data_bytes,
        headers={"Content-Type": "application/json", "User-Agent": "BARQ-Validator"}
    )
    try:
        resp = urllib_request.urlopen(req, timeout=timeout)
        data = resp.read().decode("utf-8")
        status = resp.getcode() if hasattr(resp, 'getcode') else resp.status
        body = json.loads(data)
        return status, body, resp.headers
    except urllib_error.HTTPError as e:
        return e.code, e.read().decode("utf-8"), e.headers
    except Exception as e:
        return 0, str(e), {}

def check_port_closed(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.5)
    result = sock.connect_ex((host, port))
    sock.close()
    return result != 0

def main():
    print("=== Starting Environment Validation on {} ===".format(BASE_URL))
    results = []

    # 1. Public NGINX Access (/)
    status, body, _ = http_get("/")
    ok = status == 200 and isinstance(body, dict) and body.get("service") == "barq-api"
    results.append(log_result("Public NGINX Access (/)", ok, "Status: {}".format(status)))

    # 2. Process Liveness Check (/health)
    status, body, _ = http_get("/health")
    ok = status == 200 and isinstance(body, dict) and body.get("status") == "alive"
    results.append(log_result("Process Liveness Check (/health)", ok, "Status: {}".format(status)))

    # 3. Database & Cache Readiness Check (/ready)
    status, body, _ = http_get("/ready")
    deps = body.get("dependencies", {}) if isinstance(body, dict) else {}
    ok = (status == 200 and body.get("status") == "ready" and
          deps.get("postgres") == "ready" and deps.get("redis") == "ready")
    results.append(log_result("Database & Cache Readiness Check (/ready)", ok, "PostgreSQL: {}, Redis: {}".format(deps.get('postgres'), deps.get('redis'))))

    # 4. Load Balancing Check (/instance)
    seen_instances = set()
    for _ in range(10):
        status, body, _ = http_get("/instance")
        if status == 200 and isinstance(body, dict) and "instance_id" in body:
            seen_instances.add(body["instance_id"])
        time.sleep(0.1)
    ok = len(seen_instances) >= 2
    results.append(log_result("Load Balancing Check (/instance)", ok, "Instances responded: {}".format(sorted(list(seen_instances)))))

    # 5. Redis Counter Check (/counter)
    status1, body1, _ = http_get("/counter")
    status2, body2, _ = http_get("/counter")
    c1 = body1.get("counter", 0) if isinstance(body1, dict) else 0
    c2 = body2.get("counter", 0) if isinstance(body2, dict) else 0
    ok = status1 == 200 and status2 == 200 and c2 > c1
    results.append(log_result("Redis Counter Increment Check (/counter)", ok, "Counter value: {} -> {}".format(c1, c2)))

    # 6. PostgreSQL Record Creation & Retrieval (/records)
    test_title = "Validation Record {}".format(int(time.time()))
    p_status, p_body, _ = http_post("/records", {"title": test_title})
    g_status, g_body, _ = http_get("/records")
    records = g_body.get("records", []) if isinstance(g_body, dict) else []
    created_ok = p_status == 201 and isinstance(p_body, dict) and "record" in p_body
    retrieved_ok = g_status == 200 and any(r.get("title") == test_title for r in records)
    results.append(log_result("PostgreSQL Record Creation & Retrieval (/records)", created_ok and retrieved_ok, "Created status: {}, Listed count: {}".format(p_status, len(records))))

    # 7. Prohibited Direct Host Ports Check (5432 for Postgres, 6379 for Redis)
    pg_closed = check_port_closed("127.0.0.1", 5432) and check_port_closed("127.0.0.1", 15432)
    redis_closed = check_port_closed("127.0.0.1", 6379) and check_port_closed("127.0.0.1", 16379)
    results.append(log_result("Network Isolation: Prohibited Host Port 5432 (PostgreSQL)", pg_closed, "Port 5432 is isolated from host"))
    results.append(log_result("Network Isolation: Prohibited Host Port 6379 (Redis)", redis_closed, "Port 6379 is isolated from host"))

    # Final Summary
    passed = sum(1 for r in results if r)
    total = len(results)
    print("=" * 60)
    print("Validation Summary: {}/{} checks PASSED".format(passed, total))
    print("=" * 60)

    if passed == total:
        print("RESULT: ALL CHECKS PASSED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("RESULT: VALIDATION FAILED ({} checks failed)".format(total - passed))
        sys.exit(1)

if __name__ == "__main__":
    main()
