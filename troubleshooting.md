# Troubleshooting journal

Keep chronological entries. Copy this block for each meaningful investigation.

## Entry 01 - Historical Log Analysis & Incident Correlation
- **Date / Time**: 2026-09-08 05:45:00 UTC
- **Symptom**: NGINX client access logs contained HTTP 502 Bad Gateway, 503 Service Unavailable, and 504 Gateway Timeout responses during a 30-minute window (`11:00:00Z` to `11:29:57Z`).
- **Hypothesis**:
  1. 502 errors are caused by backend container `app-02` crashing or refusing connections.
  2. 503 errors are caused by PostgreSQL/Redis service outages impacting readiness endpoints.
  3. 504 errors are caused by slow PostgreSQL transactions on the `/records` path.
- **Command or test**:
  ```bash
  wc -l logs/*.log
  grep -o '"status":[0-9]*' logs/access.log | sort | uniq -c
  grep "lab-000122" logs/access.log logs/application.log logs/error.log
  grep -E '"upstream":".*,.*"' logs/access.log
  ```
- **Actual output**:
  - `access.log`: 726 lines total, 720 unique client request IDs (`lab-000001` to `lab-000720`).
  - Status counts: 620 x 200, 10 x 404, 40 x 502, 47 x 503, 8 x 504.
  - Request `lab-000122`: `access.log` status 502, `error.log` `connect() failed (111: Connection refused)`, missing from `application.log`.
  - 20 retried requests logged with comma-separated upstreams; 100% of retries succeeded with 200 OK.
- **Failed attempt and what changed your thinking**:
  - *Initial thought*: Assumed HTTP 502 errors were caused by Flask application code exceptions.
  - *Correction*: Checking `logs/application.log` revealed zero entries for request `lab-000122`. Cross-referencing `logs/error.log` proved `111: Connection refused` at the TCP layer before the request could reach Flask.
- **Root cause**:
  1. `app-02` container (`172.23.0.12`) was down/stopped between `11:05:02Z` and `11:09:57Z`.
  2. Database/Redis dependency failure between `11:12` and `11:21` caused `/ready`, `/records`, and `/counter` endpoints to return 503.
  3. `/records` query slowdown between `11:25` and `11:26` exceeded NGINX 2.0s proxy timeout.
- **Fix**: Part 1 is analytical. Recommendations for Part 2 environment build include adding container healthchecks, restart policies (`unless-stopped`), NGINX upstream retries, and database connection pooling.
- **Retest evidence**: Automated log parsing script (`scripts/analyze_logs.py`) verified all status code counts and correlated timelines across all 3 log files.
- **Related commit**: Pending Part 1 documentation commit.
- **Remaining uncertainty**: Logs do not record underlying host kernel events (e.g. OOM killer) or exact database transaction locks.
