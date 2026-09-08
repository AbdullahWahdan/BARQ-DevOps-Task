import json
import math
from datetime import datetime
from collections import Counter, defaultdict

def percentile(data, percent):
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (percent / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    d0 = sorted_data[int(f)] * (c - k)
    d1 = sorted_data[int(c)] * (k - f)
    return d0 + d1

def parse_logs():
    access_path = "logs/access.log"
    app_path = "logs/application.log"
    error_path = "logs/error.log"

    print("==================================================")
    print("1. FILE & LINE COUNTS")
    print("==================================================")
    files = {"access.log": access_path, "application.log": app_path, "error.log": error_path}
    
    parsed_access = []
    parsed_app = []
    parsed_error = []

    file_stats = {}

    for name, path in files.items():
        valid = 0
        malformed = 0
        lines_seen = set()
        duplicate_lines = 0
        total_lines = 0

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                total_lines += 1
                line_str = line.strip()
                if not line_str:
                    continue
                if line_str in lines_seen:
                    duplicate_lines += 1
                else:
                    lines_seen.add(line_str)
                
                if name != "error.log":
                    try:
                        data = json.loads(line_str)
                        valid += 1
                        if name == "access.log":
                            parsed_access.append(data)
                        else:
                            parsed_app.append(data)
                    except Exception:
                        malformed += 1
                else:
                    valid += 1
                    parsed_error.append(line_str)

        file_stats[name] = {
            "total_lines": total_lines,
            "valid": valid,
            "malformed": malformed,
            "duplicate_lines": duplicate_lines
        }
        print(f"{name:15s}: Total={total_lines}, Valid={valid}, Malformed={malformed}, Duplicate Lines={duplicate_lines}")

    print("\n==================================================")
    print("UTC TIME INTERVALS")
    print("==================================================")
    access_ts = [datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00")) for d in parsed_access if "timestamp" in d]
    app_ts = [datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00")) for d in parsed_app if "timestamp" in d]
    
    print(f"access.log      : {min(access_ts)} to {max(access_ts)}")
    print(f"application.log : {min(app_ts)} to {max(app_ts)}")

    print("\n==================================================")
    print("2 & 3. REQUEST COUNTS, DEDUPLICATION, STATUS & ERRORS")
    print("==================================================")
    access_req_ids = [d.get("request_id") for d in parsed_access if "request_id" in d]
    unique_req_ids = set(access_req_ids)
    print(f"Total access.log entries       : {len(parsed_access)}")
    print(f"Unique request_ids in access log: {len(unique_req_ids)}")
    
    status_counts = Counter(d.get("status") for d in parsed_access)
    print(f"Status counts (access.log)     : {dict(sorted(status_counts.items()))}")
    
    total_reqs = len(parsed_access)
    server_errors = sum(count for status, count in status_counts.items() if status >= 500)
    client_errors = sum(count for status, count in status_counts.items() if 400 <= status < 500)
    print(f"Denominator                    : {total_reqs} client-facing NGINX access records")
    print(f"Server Error Count (5xx)       : {server_errors} ({server_errors / total_reqs * 100:.2f}%)")
    print(f"Client Error Count (4xx)       : {client_errors} ({client_errors / total_reqs * 100:.2f}%)")
    print(f"Overall Error Rate (4xx + 5xx) : {(server_errors + client_errors) / total_reqs * 100:.2f}%")

    print("\n==================================================")
    print("4. FAILURES BY PATH & UPSTREAM & TIME WINDOWS")
    print("==================================================")
    path_status = defaultdict(Counter)
    upstream_status = defaultdict(Counter)
    time_status = defaultdict(Counter)

    for d in parsed_access:
        path = d.get("path")
        st = d.get("status")
        up = str(d.get("upstream"))
        ts_str = d.get("timestamp")[:16] # YYYY-MM-THH:MM
        
        path_status[path][st] += 1
        upstream_status[up][st] += 1
        if st >= 500 or st == 404:
            time_status[ts_str][st] += 1
    
    print("Path status breakdown:")
    for path, counts in sorted(path_status.items()):
        print(f"  {path:12s}: {dict(sorted(counts.items()))}")
    
    print("\nUpstream status breakdown:")
    for up, counts in sorted(upstream_status.items()):
        print(f"  {up:35s}: {dict(sorted(counts.items()))}")
        
    print("\nFailure occurrences by minute:")
    for minute, counts in sorted(time_status.items()):
        print(f"  {minute}: {dict(sorted(counts.items()))}")

    print("\n==================================================")
    print("5. LATENCY PERCENTILES")
    print("==================================================")
    req_times_ms = [d.get("request_time") * 1000.0 for d in parsed_access if "request_time" in d]
    p50 = percentile(req_times_ms, 50)
    p95 = percentile(req_times_ms, 95)
    print(f"Method: Linear interpolation (math.floor / math.ceil)")
    print(f"Units: milliseconds (ms)")
    print(f"Median (p50) client latency: {p50:.2f} ms")
    print(f"95th percentile (p95) latency: {p95:.2f} ms")

    print("\n==================================================")
    print("6. UPSTREAM RETRIES")
    print("==================================================")
    retried_reqs = [d for d in parsed_access if "," in str(d.get("upstream", ""))]
    retried_succeeded = [d for d in retried_reqs if d.get("status") < 400]
    print(f"Requests that retried upstream : {len(retried_reqs)}")
    print(f"Retried requests that succeeded : {len(retried_succeeded)}")
    print("Retried requests detail:")
    for r in retried_reqs:
        print(f"  ID: {r.get('request_id')} | Path: {r.get('path')} | Upstream: {r.get('upstream')} | Upstream Status: {r.get('upstream_status')} | Final: {r.get('status')}")

    print("\n==================================================")
    print("8. CORRELATED EXAMPLES")
    print("==================================================")
    success_ex = next(d for d in parsed_access if d.get("status") == 200)
    fail_ex = next(d for d in parsed_access if d.get("status") in (500, 502, 503, 504))
    
    print("--- SUCCESSFUL REQUEST ---")
    print("Access Log:", json.dumps(success_ex))
    app_s = [a for a in parsed_app if a.get("request_id") == success_ex["request_id"]]
    print("App Log   :", json.dumps(app_s[0]) if app_s else "None")

    print("\n--- FAILED REQUEST ---")
    print("Access Log:", json.dumps(fail_ex))
    app_f = [a for a in parsed_app if a.get("request_id") == fail_ex["request_id"]]
    print("App Log   :", json.dumps(app_f[0]) if app_f else "None")
    err_f = [e for e in parsed_error if fail_ex["request_id"] in e]
    print("Error Log :", err_f[0] if err_f else "None")

if __name__ == "__main__":
    parse_logs()
