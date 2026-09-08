# Security and production-readiness review

Record at least 8 concrete risks or improvements relevant to your final solution.

---

### Finding 1: Unrestricted Host Port Bindings (Exposed Database & Cache Ports)
- **Risk and evidence**: Starter code published PostgreSQL (`15432:5432`) and Redis (`16379:6379`) to host loopback/interfaces.
- **Impact**: External network attackers or unauthorized local users could bypass NGINX and Flask authentication to query/modify raw database tables and cache records directly.
- **Implemented fix / commit**: Removed all published `ports` definitions for `postgres` and `redis` in `docker-compose.yml`. Only `nginx` port `8080` is published to host.
- **Production follow-up**: Enforce strict firewall (iptables/UFW) rules blocking database ports on worker nodes.
- **How to verify**: Tested via `validate.py` socket check. Confirmed port 5432 and 6379 connections are rejected on host.

---

### Finding 2: Privileged Root Container Execution
- **Risk and evidence**: `Dockerfile` specified `USER root`, running Flask as superuser inside the container.
- **Impact**: Container escape vulnerabilities (e.g. Linux kernel exploits) could grant root privilege over the host system.
- **Implemented fix / commit**: Added `USER app` (`uid 10001`) in `Dockerfile` and set file ownership via `COPY --chown=app:app`.
- **Production follow-up**: Enable Docker `userns-remap` and enforce `readOnlyRootFilesystem` in Kubernetes pod security contexts.
- **How to verify**: Executed `docker exec app-01 whoami` -> Returns `app` (UID 10001).

---

### Finding 3: Cross-Network Contamination & Direct NGINX Access to DB
- **Risk and evidence**: NGINX service was attached to both `frontend` and `backend` networks in starter configuration.
- **Impact**: A compromised NGINX reverse proxy could pivot directly to attack PostgreSQL or Redis services on the internal network.
- **Implemented fix / commit**: Restricted NGINX service strictly to `networks: [frontend]` in `docker-compose.yml`. Set `internal: true` on `backend` network.
- **Production follow-up**: Implement mTLS (Mutual TLS) between proxy and application pods using service meshes (Istio/Linkerd).
- **How to verify**: Verified NGINX container cannot resolve or connect to `postgres:5432` or `redis:6379`.

---

### Finding 4: Ephemeral Database Storage Data Loss Risk
- **Risk and evidence**: `docker-compose.yml` mounted PostgreSQL data to a temporary in-memory filesystem (`tmpfs: [/var/lib/postgresql/data]`).
- **Impact**: All customer records and database transactions were lost whenever the PostgreSQL container restarted or crashed.
- **Implemented fix / commit**: Removed `tmpfs` RAM mount and attached persistent named volume `postgres-data:/var/lib/postgresql/data`.
- **Production follow-up**: Automate snapshot backups to remote object storage (AWS S3) with encryption at rest.
- **How to verify**: Executed `./backup.sh` and `./restore.sh`; verified database records persist across container restarts.

---

### Finding 5: Hardcoded Database Secrets in Repository Files
- **Risk and evidence**: Plaintext credentials (`BarqLabOnly_7qN2vK8c`) were checked into git in `docker-compose.yml` and `config/app.env`.
- **Impact**: Committing production passwords to source control leads to credential leakage and unauthorized data access.
- **Implemented fix / commit**: Added `.env.example` template, ignored `.env` and secret files in `.gitignore`.
- **Production follow-up**: Inject database credentials dynamically via HashiCorp Vault or AWS Secrets Manager into container environments.
- **How to verify**: Verified git tracking ignores sensitive `.env` local configurations.

---

### Finding 6: Unbounded Container Memory & CPU Consumption
- **Risk and evidence**: Starter `docker-compose.yml` defined no memory or CPU limits for containers.
- **Impact**: A memory leak or high-traffic spike in one container could trigger host kernel OOM kills, crashing all co-located services.
- **Implemented fix / commit**: Added resource limits (`cpus: '0.50'`, `memory: 256M` / `128M`) across all Compose services.
- **Production follow-up**: Configure Kubernetes resource `requests` and `limits` alongside Horizontal Pod Autoscalers (HPA).
- **How to verify**: Inspected container limits via `docker stats`.

---

### Finding 7: Unvalidated Upstream Failover & Missing Circuit Breaking
- **Risk and evidence**: Starter `nginx.conf` set `proxy_next_upstream off;`, disabling proxy failover when a backend crashed.
- **Impact**: 50% of client requests received HTTP 502 Bad Gateway during single-instance outages.
- **Implemented fix / commit**: Configured `proxy_next_upstream error timeout http_502 http_503 http_504;` in `nginx.conf`.
- **Production follow-up**: Implement circuit breaker patterns (e.g., Envoy circuit breaking / Resilience4j) to prevent cascading failures.
- **How to verify**: Executed `failure_test.py` during `app-01` stoppage. Confirmed 100% traffic failover to `app-02`.

---

### Finding 8: Unpinned Container Base Image Vulnerabilities
- **Risk and evidence**: Generic image tags without hash digest pinning risk pulling updated images containing breaking changes or unvetted upstream vulnerabilities.
- **Impact**: Supply chain vulnerability risk during automated CI/CD builds.
- **Implemented fix / commit**: Pinned container base images to exact SHA256 immutable digests (`postgres:16-alpine@sha256:...`, `redis:7.4-alpine@sha256:...`, `python:3.12-slim-bookworm@sha256:...`).
- **Production follow-up**: Run automated vulnerability scanners (Trivy / Grype / Docker Scout) in CI/CD pipeline.
- **How to verify**: Verified `docker-compose.yml` and `Dockerfile` utilize immutable SHA256 image digests.
