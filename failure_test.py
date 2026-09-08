#!/usr/bin/env python3
"""Failure Injection & Recovery Test Script for BARQ Systems DevOps Task."""

import json
import os
import subprocess
import sys
import time

try:
    import urllib.request as urllib_request
except ImportError:
    import urllib2 as urllib_request

PUBLIC_PORT = os.getenv("PUBLIC_PORT", "8080")
BASE_URL = os.getenv("BASE_URL", "http://localhost:{}".format(PUBLIC_PORT))

def log_step(name, success, details=""):
    status = "PASS" if success else "FAIL"
    msg = "[{}] {}".format(status, name)
    if details:
        msg += " - {}".format(details)
    print(msg)
    return success

def run_cmd(cmd):
    try:
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        return proc.returncode == 0, stdout.decode("utf-8").strip() if stdout else stderr.decode("utf-8").strip()
    except Exception as e:
        return False, str(e)

def http_get(path):
    try:
        url = "{}{}".format(BASE_URL, path)
        resp = urllib_request.urlopen(url, timeout=3)
        data = resp.read().decode("utf-8")
        status = resp.getcode() if hasattr(resp, 'getcode') else resp.status
        return status, json.loads(data)
    except Exception as e:
        return 0, str(e)

def main():
    print("=== Starting Scoped Failure & Recovery Test ===")
    results = []

    # 1. Baseline check
    instances_before = set()
    for _ in range(6):
        s, body = http_get("/instance")
        if s == 200 and isinstance(body, dict) and "instance_id" in body:
            instances_before.add(body["instance_id"])
        time.sleep(0.1)
    results.append(log_step("Baseline Readiness Check", len(instances_before) >= 2, "Active instances: {}".format(sorted(list(instances_before)))))

    # 2. Stop app-01
    print("\n--> Stopping app-01 container...")
    stop_ok, _ = run_cmd("docker compose stop app-01")
    if not stop_ok:
        log_step("Stop app-01 Container", False, "Failed to execute docker compose stop app-01")
        sys.exit(1)

    time.sleep(2)

    # 3. Test availability during failure
    success_count = 0
    fail_count = 0
    instances_during_failure = set()
    total_requests = 10

    for _ in range(total_requests):
        s, body = http_get("/instance")
        if s == 200 and isinstance(body, dict):
            success_count += 1
            instances_during_failure.add(body.get("instance_id"))
        else:
            fail_count += 1
        time.sleep(0.1)

    failover_ok = (success_count == total_requests and
                   instances_during_failure == {"app-02"})
    results.append(log_step("Traffic Failover to app-02 During app-01 Down", failover_ok,
                            "Successful requests: {}/{}, Active instance: {}".format(success_count, total_requests, list(instances_during_failure))))

    # 4. Restore app-01
    print("\n--> Restoring app-01 container...")
    start_ok, _ = run_cmd("docker compose start app-01")
    if not start_ok:
        log_step("Restore app-01 Container", False, "Failed to execute docker compose start app-01")
        sys.exit(1)

    # Bounded wait for app-01 to recover health
    recovered = False
    for _ in range(15):
        time.sleep(1)
        instances_after = set()
        for _ in range(6):
            s, body = http_get("/instance")
            if s == 200 and isinstance(body, dict):
                instances_after.add(body.get("instance_id"))
        if "app-01" in instances_after and "app-02" in instances_after:
            recovered = True
            break

    results.append(log_step("Full Recovery & Load Balancing Resumption", recovered, "Both app-01 and app-02 responding again"))

    # Summary
    passed = sum(1 for r in results if r)
    total = len(results)
    print("\n" + "=" * 60)
    print("Failure Test Summary: {}/{} steps PASSED".format(passed, total))
    print("=" * 60)

    if passed == total:
        print("RESULT: FAILURE & RECOVERY TEST PASSED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("RESULT: FAILURE TEST FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
