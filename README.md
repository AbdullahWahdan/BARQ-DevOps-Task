<img src="assets/barq-logo.svg" alt="BARQ Systems" width="180">

# DevOps Internship Task - Final Documentation & Operations Guide

**Student Release**: BARQ Academy DevOps Internship Task  
**Environment**: Microservices (Flask, NGINX, PostgreSQL, Redis, Docker Compose, GitHub Actions)

---

## 🚀 Copyable Quickstart & Operations Guide

### 1. Setup & Environment Variables
```bash
# Clone repository
git clone https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
cd <YOUR_REPO>

# Copy environment file
cp .env.example .env
```

### 2. Build & Start Environment
```bash
# Build images and start all containers in detached mode
docker compose up -d --build

# Check status of running containers (All 5 containers should show healthy)
docker compose ps
```

### 3. Endpoint Verification Commands
```bash
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/ready
curl http://localhost:8080/instance
curl http://localhost:8080/records
curl http://localhost:8080/counter
```

### 4. Run Automated Validation Test Suite
```bash
# Execute automated environment validation (Python 2.7 & 3.x compatible)
python validate.py
```

### 5. Run Scoped Failure & Recovery Test
```bash
# Executes failure injection (stops app-01, tests failover, restores app-01, verifies recovery)
python failure_test.py
```

### 6. Database Backup & Restore Operations
* **Bash / Linux / WSL**:
  ```bash
  ./backup.sh
  ./restore.sh
  ```
* **PowerShell**:
  ```powershell
  .\backup.ps1
  .\restore.ps1
  ```

### 7. Clean Stop
```bash
# Stop and remove containers without destroying persistent volumes
docker compose down

# Stop and remove all containers AND persistent data volumes
docker compose down -v
```

---

## ❓ Required Evaluation Questions & Answers

### 1. What failed first? What proved the cause? Which failed attempt taught you something?
* **What failed first**: In `docker-compose.yml`, `config/app.env` had invalid PostgreSQL credentials (`BarqLabOnly_7qN2vK8d` instead of `8c`), invalid database port (`5433` instead of `5432`), and invalid Redis port (`6380` instead of `6379`), causing instant 503 dependency errors. Simultaneously, `app-02` had a duplicate `INSTANCE_ID: "app-01"`.
* **What proved the cause**: Executing `curl http://localhost:8080/ready` returned `{"postgres":"unavailable", "redis":"unavailable"}`. Inspecting `docker compose logs app-01` showed `psycopg.OperationalError` connection timeout to `postgres:5433`.
* **Failed attempt learning**: Trying to mount PostgreSQL data to `tmpfs` RAM storage caused all records created via `/records` to be deleted upon container restarts. Replacing `tmpfs` with persistent named volume `postgres-data:/var/lib/postgresql/data` taught the critical difference between ephemeral RAM mounts and persistent Docker volumes.

### 2. What patterns did the logs reveal? How did you avoid double-counting requests?
* **Log patterns**: 
  - `11:05-11:09`: `app-02` (`172.23.0.12`) was down, producing 40 x 502 Bad Gateway responses (`111: Connection refused` in `error.log`).
  - `11:12-11:15` & `11:20-11:21`: Database/Redis outages producing 47 x 503 Service Unavailable responses on `/ready`, `/records`, and `/counter`.
  - `11:25-11:26`: `/records` queries timed out at 2.0s producing 8 x 504 Gateway Timeout responses.
* **Avoiding double-counting**: NGINX access log logs retried requests on a single line with comma-separated upstreams (e.g. `upstream: "172.23.0.12:8080, 172.23.0.11:8080"`). We grouped entries by unique `request_id` keys (`lab-000001` to `lab-000720`), identifying exactly 720 unique client requests across 725 total log lines.

### 3. How do requests flow? Why these ports, networks and readiness checks?
* **Request Flow**: Client -> Host Port 8080 -> NGINX (`frontend` network) -> Load balanced across `app-01` / `app-02` (Port 8080 on `frontend` & `backend`) -> `postgres` (Port 5432) & `redis` (Port 6379) on `backend` network.
* **Why these ports**: Host port `8080` (or `8090` during live video challenge) is the single public entrypoint. Ports 5432 and 6379 are unpublished to host to prevent direct unauthorized access to DB/Cache.
* **Why these networks**: `frontend` isolates web traffic between proxy and application. `backend` (`internal: true`) isolates database and cache communication, completely blocking NGINX from accessing DB/Redis directly.
* **Readiness checks**: `/ready` validates actual DB/Redis connectivity before accepting production traffic.

### 4. Why these timeouts, retries, restart settings and resource limits?
* **Timeouts**: NGINX `proxy_connect_timeout 2s;` and `proxy_read_timeout 3s;` prevent hanging requests from tying up worker threads during backend slowdowns.
* **Retries**: NGINX `proxy_next_upstream error timeout http_502 http_503 http_504;` automatically routes client requests to `app-02` if `app-01` is down, achieving 100% failover success.
* **Restart settings**: `restart: unless-stopped` ensures automatic container recovery after unexpected crashes or host reboots.
* **Resource limits**: `cpus: '0.50'` and `memory: 256M` prevent a single container memory leak from crashing the entire host system (Noisy-Neighbor isolation).

### 5. When should validation fail? What does green CI prove, or not prove?
* **When validation fails**: If any public endpoint returns non-200, if `/ready` fails DB/Redis checks, if load balancing fails, if counter/record CRUD fails, or if prohibited ports (5432/6379) are accessible on host.
* **What green CI proves**: Proves code builds cleanly, containers launch, dependencies connect, network isolation is enforced, endpoints function, and load balancing works under synthetic test conditions.
* **What green CI does not prove**: Does not prove performance under heavy concurrent load (10k+ QPS), long-term disk volume exhaustion, or resilience against cloud cloud infrastructure outages.

### 6. Which single points of failure remain? How would you fix them in production?
* **Single Points of Failure**:
  1. NGINX container is a single reverse proxy instance.
  2. PostgreSQL container is a single database instance.
  3. Redis container is a single node.
* **Production Fixes**:
  1. Deploy multiple NGINX ingress replicas behind a Cloud Load Balancer (AWS ALB / GCP Cloud Load Balancer).
  2. Provision Managed PostgreSQL in Multi-AZ configuration with automatic failover (AWS RDS / Cloud SQL).
  3. Deploy Redis Cluster / Sentinel with primary-replica failover.

### 7. What would you improve? How did you verify AI-assisted work?
* **Improvements**: Add TLS/HTTPS encryption with Let's Encrypt certificates, integrate Prometheus/Grafana monitoring, and implement central log aggregation (ELK/Loki).
* **AI Verification**: Independently verified all AI-suggested code by building images (`docker compose up --build`), executing automated test suites (`validate.py` 8/8 PASS, `failure_test.py` 3/3 PASS), and testing database backup/restore (`backup.ps1` & `restore.ps1`).

---

## 📄 Deliverable Documentation Index

* [troubleshooting.md](troubleshooting.md) — Chronological investigation journal.
* [log_analysis.md](log_analysis.md) — Comprehensive log analysis, status code counts, and timeline.
* [decisions.md](decisions.md) — 6 architectural decisions, trade-offs, and alternatives.
* [security_review.md](security_review.md) — 8 concrete security findings and production follow-ups.
* [AI_USAGE.md](AI_USAGE.md) — Full disclosure of AI tools, affected files, and verification methods.
* [architecture.png](architecture.png) — Architecture diagram showing request flows, ports, networks, storage, and health checks.
