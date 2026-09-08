# Technical decisions

Record at least 5 decisions. Include assumptions and limits.

## Decision 1: Restricted Network Topology & Strict Port Isolation
- **Choice**: Separated microservices into two isolated networks (`frontend` and `backend`). NGINX is restricted strictly to `frontend`, while PostgreSQL and Redis are attached strictly to `backend`. Host port publishing was disabled for all backend services (PostgreSQL `5432` & Redis `6379`).
- **Why**: Prevents direct external access to database/cache infrastructure and prevents NGINX from bypassing backend application security layers.
- **Alternative**: Single flat network exposing database and Redis ports on `localhost` for developer debugging.
- **Trade-off**: Internal container management requires `docker exec` rather than direct host GUI connections (e.g. pgAdmin/TablePlus).
- **Evidence / commit**: `docker-compose.yml` (`networks: [frontend]` for NGINX; `internal: true` for `backend`).
- **Production improvement**: Use Kubernetes NetworkPolicies or cloud VPC security groups with Mutual TLS (mTLS).

## Decision 2: NGINX Upstream Load Balancing & Failover Retries
- **Choice**: Configured NGINX upstream block with `max_fails=3 fail_timeout=5s` and enabled `proxy_next_upstream error timeout http_502 http_503 http_504;`.
- **Why**: Ensures zero-downtime client traffic flow when a single Flask instance fails or is being updated.
- **Alternative**: `proxy_next_upstream off;` (default setting in starter code), causing client requests to fail with 502 when hitting a down instance.
- **Trade-off**: Slightly increased latency on the first failed request before proxy failover completes (~100ms penalty).
- **Evidence / commit**: `nginx/nginx.conf` (`proxy_next_upstream` configuration). Verified by `failure_test.py` (100% pass during backend failure).
- **Production improvement**: Integrate active NGINX health checks (`health_check`) or Kubernetes ingress controllers with readiness probes.

## Decision 3: Non-Root Execution in Container Images
- **Choice**: Explicitly set `USER app` (`uid 10001`) in `Dockerfile` for Flask app execution.
- **Why**: Follows the principle of least privilege. Prevents potential container breakout vulnerabilities from gaining host root access.
- **Alternative**: Running container entrypoints as `root` user (starter code `USER root`).
- **Trade-off**: Requires explicit permission management (`COPY --chown=app:app`) during Docker image build.
- **Evidence / commit**: `Dockerfile` (`USER app` directive).
- **Production improvement**: Enforce PodSecurityStandards (`restricted` profile) and read-only root filesystems in production.

## Decision 4: PostgreSQL Named Volume Persistence & Redis Persistence
- **Choice**: Replaced PostgreSQL `tmpfs` RAM storage with named volume `postgres-data` mounted to `/var/lib/postgresql/data`. Enabled Redis AOF/RDB persistence (`--save 60 1 --appendonly yes`).
- **Why**: Guarantees database state and cache counters survive container restarts and crash recoveries.
- **Alternative**: Using ephemeral `tmpfs` (starter code), which wipes database state whenever containers stop.
- **Trade-off**: Slight disk I/O overhead on Redis writes due to Append-Only File logging.
- **Evidence / commit**: `docker-compose.yml` (`volumes: [postgres-data:/var/lib/postgresql/data]`). Tested via `backup.ps1` and `restore.ps1`.
- **Production improvement**: Provision managed cloud database instances (AWS RDS / GCP Cloud SQL) with multi-AZ replication and automated point-in-time recovery.

## Decision 5: Explicit Container Healthchecks & Bounded Resource Limits
- **Choice**: Added native healthchecks (`pg_isready`, `redis-cli ping`, Python `urllib`) and defined CPU (`0.50`) & Memory (`256M` / `128M`) resource limits across all services in Compose.
- **Why**: Prevents a single noisy-neighbor service from starving the host node and ensures dependent services wait until upstream services are ready (`condition: service_healthy`).
- **Alternative**: Unbounded container memory/CPU allocation without healthchecks.
- **Trade-off**: Hard memory limits will trigger OOM kills if traffic exceeds allocations, requiring proper capacity planning.
- **Evidence / commit**: `docker-compose.yml` (`healthcheck` and `deploy.resources.limits` sections).
- **Production improvement**: Implement Horizontal Pod Autoscaling (HPA) and Prometheus alerts on container resource saturation.

## Decision 6: Environment Credentials & Connection Strings Correction
- **Choice**: Corrected database user credentials (`barq_app`), password (`BarqLabOnly_7qN2vK8c`), and internal service ports (`5432` for Postgres, `6379` for Redis) in `config/app.env`.
- **Why**: Fixes immediate 503 dependency connection errors caused by credential/port mismatches in starter configuration.
- **Alternative**: Storing database passwords in Dockerfile environment variables or git code.
- **Trade-off**: Requires loading environment configuration via Compose `env_file`.
- **Evidence / commit**: `config/app.env` and `.env.example`.
- **Production improvement**: Use secret managers (HashiCorp Vault or AWS Secrets Manager) injected dynamically at runtime.
