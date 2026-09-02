"""Application contract tests only; these do not validate the DevOps environment."""

import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app.server import ApplicationServer


class ApplicationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def query(statement):
            return [(1,)] if statement == "SELECT 1" else [(1, "Review service readiness", False)]
        cls.server = ApplicationServer(("127.0.0.1", 0), "test-instance", "Test message", query_function=query)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def get(self, path, headers=None, method="GET"):
        return urlopen(Request(self.base_url + path, headers=headers or {}, method=method), timeout=3)

    def test_root_contract(self):
        with self.get("/") as response:
            data = json.load(response)
            self.assertEqual(response.status, 200)
            self.assertEqual(data["instance_id"], "test-instance")
            self.assertEqual(data["message"], "Test message")
            self.assertEqual(response.headers["X-Instance-ID"], data["instance_id"])

    def test_health(self):
        with self.get("/health") as response:
            self.assertEqual(json.load(response)["status"], "ok")

    def test_info(self):
        with self.get("/api/info") as response:
            self.assertGreaterEqual(json.load(response)["uptime_seconds"], 0)

    def test_items(self):
        with self.get("/api/items") as response:
            self.assertEqual(json.load(response)["items"][0]["title"], "Review service readiness")

    def test_database_unavailable(self):
        original = self.server.query
        def unavailable(_statement):
            raise ConnectionError("Simulated database unavailable")
        self.server.query = unavailable
        try:
            for path in ["/health", "/api/items"]:
                with self.assertRaises(HTTPError) as caught:
                    self.get(path)
                self.assertEqual(caught.exception.code, 503)
                self.assertEqual(json.load(caught.exception)["error"], "database_unavailable")
                caught.exception.close()
        finally:
            self.server.query = original

    def test_unknown_path(self):
        with self.assertRaises(HTTPError) as caught:
            self.get("/unknown")
        self.assertEqual(caught.exception.code, 404)
        self.assertEqual(json.load(caught.exception)["error"], "not_found")
        caught.exception.close()

    def test_request_correlation(self):
        with self.get("/", {"X-Request-ID": "contract-test-1"}) as response:
            self.assertEqual(response.headers["X-Request-ID"], "contract-test-1")

    def test_query_string_does_not_change_route(self):
        with self.get("/health?check=1") as response:
            self.assertEqual(response.status, 200)

    def test_head(self):
        with self.get("/health", method="HEAD") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.read(), b"")


if __name__ == "__main__":
    unittest.main()
