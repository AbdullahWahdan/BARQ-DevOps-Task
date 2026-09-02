# Application contract

The service is a small Python HTTP API backed by PostgreSQL. Keep this public behavior intact while implementing the DevOps solution.

## HTTP interface

| Request | Expected behavior |
| --- | --- |
| `GET /` | HTTP 200 JSON containing `service`, `version`, `instance_id`, and `message`. |
| `GET /api/info` | HTTP 200 JSON with the same fields plus non-negative `uptime_seconds`. |
| `GET /health` | Runs `SELECT 1`; HTTP 200 with `status: "ok"`, `database: "ready"` and instance identity when SQL is reachable; otherwise HTTP 503. |
| `GET /api/items` | Queries the SQL `items` table; HTTP 200 with instance identity and the seeded item list; otherwise HTTP 503. |
| An unknown path | HTTP 404 JSON with `error: "not_found"`. |

Responses include `X-Instance-ID` and `X-Request-ID`. The instance identity must remain visible through the proxy so a request sequence can establish which instances served it. A direct process health check alone does not establish proxy reachability or failure handling.

## Runtime configuration

| Variable | Application default | Meaning |
| --- | --- | --- |
| `APP_HOST` | `0.0.0.0` | Listening address inside the application's runtime. |
| `APP_PORT` | `8080` | HTTP listening port inside that runtime. |
| `INSTANCE_ID` | `local` | Instance identity: 1–64 letters, digits, hyphens or underscores. |
| `APP_MESSAGE` | `Welcome to BARQ Systems` | Message returned by the application. |
| `DATABASE_URL` | None | PostgreSQL connection URI used by the application; required for SQL-backed endpoints. |

Configuration is read at process startup. The table describes the application's interface, not the correctness of the supplied deployment configuration. The `database` service runs PostgreSQL on its standard internal port, 5432. `database/init.sql` creates the `items` table and synthetic starting rows when a new data volume is initialized. This app is read-only; do not replace SQL-backed endpoints with hardcoded responses.

## Logs

The application emits JSON Lines to standard output. Events include startup, requests, client disconnections, database errors and shutdown. Request records have a UTC timestamp, instance ID, request ID, method, path, status and duration in milliseconds. An acceptable `X-Request-ID` is preserved; otherwise one is generated. All accounts and data in this exercise are synthetic.

The supplied historical log is described separately in [logs/README.md](../logs/README.md). Do not assume a historical incident and the current configuration are identical.
