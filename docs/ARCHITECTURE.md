# System Architecture Overview

```
                          [ Client Request ]
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │  Host Port 8080 (or 8090)    │
                   └──────────────┬───────────────┘
                                  │
                       [ FRONTEND NETWORK ]
                                  │
                                  ▼
                        ┌───────────────────┐
                        │   nginx Proxy     │
                        │ (Listen Port 80)  │
                        └─────────┬─────────┘
                                  │
                     Load Balanced (Round Robin)
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
     ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
     │    app-01     │    │    app-02     │    │    app-03     │
     │ (Port 8080)   │    │ (Port 8080)   │    │ (Port 8080)   │
     └───────┬───────┘    └───────┬───────┘    └───────┬───────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                        [ BACKEND NETWORK ]
                         (internal: true)
                                  │
             ┌────────────────────┴────────────────────┐
             │                                         │
             ▼                                         ▼
   ┌───────────────────┐                     ┌───────────────────┐
   │     postgres      │                     │       redis       │
   │   (Port 5432)     │                     │    (Port 6379)    │
   │ Volume: postgres- │                     │  AOF/RDB Persistence
   │      data         │                     └───────────────────┘
   └───────────────────┘
```

## Network Isolation Rules
1. **Frontend Network (`barq-assessment_frontend`)**: Connects `nginx` + `app-01` + `app-02` (+ `app-03`). Only NGINX port `8080`/`8090` is exposed to the public host.
2. **Backend Network (`barq-assessment_backend`)**: `internal: true`. Connects `app-01` + `app-02` + `app-03` + `postgres` + `redis`. Direct NGINX access to PostgreSQL/Redis is blocked.

## Health & Readiness Checks
- `/health` checks process liveness of Flask instances.
- `/ready` executes `SELECT 1` on PostgreSQL and `PING` on Redis.
- `docker-compose` `depends_on: { service_healthy }` ensures database and cache are healthy before application instances start.
