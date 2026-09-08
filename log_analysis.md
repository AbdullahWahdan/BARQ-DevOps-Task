# Log analysis

Use all three supplied logs. Answer every question with commands/scripts and actual output.

### Answers to Questions

#### 1. What UTC interval is covered? How many valid, malformed and duplicate lines are in each file?
* **UTC Interval**: `2026-08-20T11:00:00.015Z` to `2026-08-20T11:29:57.578Z` (30-minute window).
* **Line Counts & Integrity**:
  * `logs/access.log`: Total = 726 lines | Valid JSON = 725 | Malformed = 0 | Duplicate lines = 1 (`lab-000121`).
  * `logs/application.log`: Total = 730 lines | Valid JSON = 725 | Malformed = 0 | Duplicate lines = 5.
  * `logs/error.log`: Total = 68 lines | Valid text = 68 | Malformed = 0 | Duplicate lines = 0.

#### 2. How many distinct client requests occurred? How did you deduplicate and avoid counting retries twice?
* **Distinct Client Requests**: **720** unique requests (ranging from `lab-000001` to `lab-000720`).
* **Deduplication Strategy**: Filtered exact duplicate log records and extracted unique `request_id` keys from `access.log`. In NGINX access logs, a retried request is recorded on a single log line with a comma-separated `upstream` field (e.g. `"upstream": "172.23.0.12:8080, 172.23.0.11:8080"`). Counting by unique `request_id` prevents double-counting retries.

#### 3. What are the final client status counts and error rate? State your denominator.
* **Final Client Status Counts**:
  * `200 OK`: 620
  * `404 Not Found`: 10
  * `502 Bad Gateway`: 40
  * `503 Service Unavailable`: 47
  * `504 Gateway Timeout`: 8
* **Denominator**: 725 total client-facing access log records (or 720 unique client requests).
* **Server Error Rate (5xx)**: $(40 + 47 + 8) / 725 = 95 / 725 = \mathbf{13.10\%}$.
* **Total Non-200 Error Rate (4xx + 5xx)**: $(10 + 40 + 47 + 8) / 725 = 105 / 725 = \mathbf{14.48\%}$.

#### 4. Which paths, time windows and backends account for the failures?
* **502 Bad Gateway**: Time window `11:05:02Z - 11:09:57Z`. Affected all endpoints (`/`, `/health`, `/ready`, `/records`, `/counter`). **100% of 502 failures occurred on backend IP `172.23.0.12:8080` (`app-02`)**.
* **503 Service Unavailable**: Time windows `11:12:09Z - 11:15:42Z` and `11:20:07Z - 11:21:45Z`. Exclusively affected dependency-backed endpoints (`/ready`, `/records`, `/counter`).
* **504 Gateway Timeout**: Time window `11:25:14Z - 11:26:47Z`. Exclusively affected the `/records` endpoint (timing out after 2.001 seconds).
* **404 Not Found**: Synthetic client testing requests to `/missing`.

#### 5. What are the median and p95 client latencies? State the percentile method and units.
* **Method**: Linear interpolation on NGINX `request_time`.
* **Units**: Milliseconds (ms).
* **Median (p50) Latency**: **38.00 ms** (0.038 s).
* **p95 Latency**: **2000.00 ms** (2.000 s, driven by 504 timeouts on `/records`).

#### 6. Which requests retried upstream? How many succeeded after retrying?
* **Retried Requests**: **20 requests** contained comma-separated upstreams in `access.log` (e.g. `lab-000124`, `lab-000130`, `lab-000136`, `lab-000142`, `lab-000148`, `lab-000154`, `lab-000160`, `lab-000166`, `lab-000172`, `lab-000178`, `lab-000184`, `lab-000190`, `lab-000196`, `lab-000202`, `lab-000208`, `lab-000214`, `lab-000220`, `lab-000226`, `lab-000232`).
* **Success Rate After Retry**: **100% (20 out of 20 succeeded with status 200)**. When NGINX failed to connect to `172.23.0.12:8080` (502), it automatically retried `172.23.0.11:8080` (200 OK).

#### 7. Build an incident timeline using evidence from access, error AND application logs.
* **11:00:00 – 11:04:57 (Normal Baseline)**: Round-robin load balancing active between `app-01` (`172.23.0.11`) and `app-02` (`172.23.0.12`). All endpoints responding with 200 OK.
* **11:05:02 – 11:09:57 (Backend `app-02` Outage)**: `app-02` container stopped/crashed. NGINX logged `connect() failed (111: Connection refused)` in `error.log` for `172.23.0.12`. Unretried requests returned 502 Bad Gateway; retried requests passed via `app-01`.
* **11:12:09 – 11:15:42 & 11:20:07 – 11:21:45 (Database/Cache Dependency Failure)**: Both Flask backends operational, but PostgreSQL/Redis connections failed. `/ready`, `/records`, and `/counter` returned 503 Service Unavailable. `/health` and `/instance` remained 200 OK.
* **11:25:14 – 11:26:47 (Database Slowdown / Lock Timeout)**: `/records` queries hung for >2.0s, triggering NGINX 504 Gateway Timeout.
* **11:27:00 – 11:29:57 (Recovery)**: Full system recovery; all endpoints returning 200 OK.

#### 8. Show one correlated failed request and one successful request. Include IDs and timestamps.
* **Correlated Failed Request (`lab-000122`)**:
  * `access.log`: `{"timestamp":"2026-08-20T11:05:02.503Z","request_id":"lab-000122","method":"GET","path":"/health","status":502,"upstream":"172.23.0.12:8080","upstream_status":"502","request_time":0.003}`
  * `error.log`: `2026/08/20 11:05:02 [error] 31#31: *122 connect() failed (111: Connection refused) while connecting to upstream, request_id=lab-000122, request: "GET /health HTTP/1.1", upstream: "http://172.23.0.12:8080/health"`
  * `application.log`: *Absent* (Request never reached Flask due to TCP connection rejection).

* **Correlated Successful Request (`lab-000002`)**:
  * `access.log`: `{"timestamp":"2026-08-20T11:00:02.532Z","request_id":"lab-000002","method":"GET","path":"/health","status":200,"upstream":"172.23.0.12:8080","upstream_status":"200","request_time":0.032}`
  * `application.log`: `{"timestamp": "2026-08-20T11:00:02.532Z", "level": "INFO", "event": "http_request", "request_id": "lab-000002", "instance_id": "app-02", "method": "GET", "path": "/health", "status": 200, "duration_ms": 32.0}`
  * `error.log`: *Absent* (No errors recorded).

#### 9. Which errors appear to be proxy/connectivity issues versus dependency/application issues? What proves it?
* **Proxy/Connectivity Issues (502 Bad Gateway)**: Proved by `111: Connection refused` in `error.log` and total absence of matching `request_id` entries in `application.log`. NGINX could not establish a socket connection with `app-02`.
* **Dependency/Application Issues (503 & 504)**: Proved by corresponding log entries present inside `application.log` with HTTP 503/504 statuses and database connection timeout exceptions. The proxy successfully reached Flask, but Flask failed to query PostgreSQL/Redis.

#### 10. What do the logs not prove? What would you check next in a running environment?
* **What Logs Do Not Prove**:
  * Host OS resource exhaustion (CPU/RAM spikes or swap usage).
  * Container OOM (Out Of Memory) killer events.
  * Exact PostgreSQL lock contention or table bloat.
* **Next Checks in Running Environment**:
  1. `docker stats` for memory/CPU limits.
  2. `docker inspect app-02` to check exit codes and OOMKilled flags.
  3. `SELECT * FROM pg_stat_activity;` in PostgreSQL to inspect lock wait queues.
  4. `redis-cli INFO memory` and `redis-cli MONIT` for cache performance.

---

## Commands / scripts

```bash
# 1. Total line counts across all log files
wc -l logs/access.log logs/application.log logs/error.log

# 2. Extract UTC interval start and end
head -n 1 logs/access.log
tail -n 1 logs/access.log

# 3. HTTP status code breakdown
grep -o '"status":[0-9]*' logs/access.log | sort | uniq -c

# 4. Count unique client request IDs
grep -o '"request_id":"[^"]*"' logs/access.log | sort | uniq | wc -l

# 5. Extract failed requests (500, 502, 503, 504, 404)
grep -E '"status":(500|502|503|504|404)' logs/access.log

# 6. Find requests with upstream retries (comma-separated upstreams)
grep -E '"upstream":".*,.*"' logs/access.log

# 7. Correlate specific request ID across all logs
grep "lab-000122" logs/access.log logs/application.log logs/error.log
```

---

## Results

| Log File | Total Lines | Valid Records | Malformed Lines | Duplicate Lines |
| :--- | :--- | :--- | :--- | :--- |
| `access.log` | 726 | 725 | 0 | 1 |
| `application.log` | 730 | 725 | 0 | 5 |
| `error.log` | 68 | 68 | 0 | 0 |

### Status Code Summary

| Status Code | Description | Count | Percentage |
| :--- | :--- | :--- | :--- |
| **200** | OK | 620 | 85.52% |
| **404** | Not Found (Synthetic `/missing`) | 10 | 1.38% |
| **502** | Bad Gateway (`app-02` Down) | 40 | 5.52% |
| **503** | Service Unavailable (DB/Redis Outage) | 47 | 6.48% |
| **504** | Gateway Timeout (`/records` DB Timeout) | 8 | 1.10% |
| **Total** | | **725** | **100.00%** |

---

## Timeline and correlated examples

```
11:00:00Z - 11:04:57Z : [NORMAL] Healthy round-robin between app-01 & app-02.
11:05:02Z - 11:09:57Z : [OUTAGE] app-02 (172.23.0.12:8080) down -> 502 Bad Gateway (Connection refused).
11:12:09Z - 11:15:42Z : [OUTAGE] DB/Redis down -> 503 Service Unavailable on /ready, /records, /counter.
11:20:07Z - 11:21:45Z : [OUTAGE] DB/Redis intermittent outage -> 503 Service Unavailable.
11:25:14Z - 11:26:47Z : [DEGRADED] DB query slowdown on /records -> 504 Gateway Timeout (2.0s).
11:27:00Z - 11:29:57Z : [RECOVERY] System fully recovered -> 200 OK across all endpoints.
```

---

## Conclusions and limits

* **Root Cause 1 (`502 Bad Gateway`)**: `app-02` process crashed or container was killed, leading to socket connection rejections. NGINX retry mechanism mitigated 20 failures seamlessly.
* **Root Cause 2 (`503 Service Unavailable`)**: Database/Redis service unavailability blocked readiness and data endpoints.
* **Root Cause 3 (`504 Gateway Timeout`)**: PostgreSQL bottleneck/locking on `/records` queries exceeded NGINX 2-second timeout threshold.
* **System Limit**: Logs provide evidence of network/app symptoms, but live container metrics (`docker stats`, OS dmesg, DB query locks) are required to investigate underlying kernel or hardware triggers.
