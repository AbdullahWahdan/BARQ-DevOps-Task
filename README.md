<img src="assets/barq-logo.svg" alt="BARQ Systems" width="180">

# DevOps Internship Acceptance Task — Starter Pack

**Release:** `barq-devops-starter-v1.0.0`  
**Starting Git tag:** `starter-v1.0.0`  
**Due date:** __________________________

Start with [the assessment](assessment/TASK.md) and [the application contract](assessment/APPLICATION.md).
This is an intentionally broken training environment. The number and types of hidden issues are not disclosed.
Investigate the supplied application and environment; do not substitute a different project.

## What you receive

- A small Python HTTP application and application-only contract tests.
- A Dockerfile, Docker Compose configuration and NGINX configuration.
- A historical training incident log at `logs/application.log`, with format notes.
- Empty documentation templates under `docs/`.

The application uses PostgreSQL for a small seeded item list. This is an isolated local lab, not a production deployment; all supplied accounts and data are synthetic and must not be reused for real services. It uses Linux containers on Linux or Docker Desktop; Windows users should use a WSL2 Linux terminal for the assessment commands. No cloud account or private registry is required.

## Prerequisites

Git, Docker Engine/Desktop with the Compose plugin, a terminal, and Python 3.12 for local tests/log analysis. Allow about 2 CPU cores, 2 GB available RAM and 2 GB disk for the lab, plus Docker Desktop's own requirements. Internet is needed for initial image/package downloads and GitHub submission. Use the same supplied baseline as the other candidates.

## Get started

Clone the shared starter repository, or follow the Git bundle instructions supplied with the student ZIP. Keep its baseline commit and tag. Connect your working repository to your own empty GitHub repository; do not squash the starting history.

From the repository root in a Linux/WSL terminal:

```bash
git status
git log -1 --oneline
cp .env.example .env
docker version
docker compose version
docker compose up --build -d
docker compose ps -a
docker compose logs --no-color
```

The initial environment is not expected to pass the acceptance criteria. Preserve the actual observations and your investigation in Git and the troubleshooting report. Startup output is evidence, not a promise that every service is ready.

The intended entry point is `http://127.0.0.1:8088`. If that host port is occupied, select another unused `PUBLIC_PORT` in your local `.env` and document it; this is a workstation adjustment, not a diagnosis of the supplied environment. Use only the training accounts and data, never real credentials or customer data.

Application-only checks, independent of Docker/NGINX:

```bash
python3 -m unittest discover -s tests -v
```

These tests use a fake database-query function and do **not** replace the automated environment-validation script you must write. The actual application connects to PostgreSQL using the pinned dependency in `requirements.txt`, installed during the Docker build.

To stop only this project's containers and network, run `docker compose down` from this directory. Its SQL data volume is retained. Do not use global cleanup/prune commands on a shared machine.

## Your submission

Implement and document the requirements in [TASK.md](assessment/TASK.md). Write your own validation script and GitHub Actions workflow; they are candidate deliverables, not supplied solutions. Complete the templates (empty templates are not evidence), add an architecture diagram, and turn this README into a complete guide for your final solution.

Use these starting files:

- [Troubleshooting and log analysis](docs/TROUBLESHOOTING.md)
- [Technical decision log](docs/DECISIONS.md)
- [AI usage disclosure](docs/AI_USAGE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Evidence and submission links](docs/EVIDENCE_INDEX.md)
- [Validation-script requirements](scripts/README.md)

## Final README sections to complete

Replace this section with your setup/start/stop commands, architecture link, validation command and output, CI run link, endpoint/load-balancing tests, failure and recovery behavior, important decisions and limitations, final commit hash, and continuous video link. Map video timestamps and report findings to the corresponding commits. Preserve the original incident log as evidence.
