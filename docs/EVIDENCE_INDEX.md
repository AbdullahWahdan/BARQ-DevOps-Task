# Evidence and submission index

- **Repository URL**: `https://github.com/AbdullahWahdan/BARQ-DevOps-Task`
- **Starting video commit**: `55e8aca7c8fef3130dbed3d96de210d35a807c75`
- **Final commit**: `a00aeff1da103cb717e29edcfe0d3b0397dd4c8d`
- **Matching CI run**: `https://github.com/AbdullahWahdan/BARQ-DevOps-Task/actions`
- **Continuous 12-18 minute video URL**: `https://drive.google.com/file/d/1gpldt7XfbreGg31gTs4msYdQYjk60At5/view?usp=sharing`
- **Challenge receipt ID**: `00f45045c16243d5bdc69ad23a44bcea`
- **Later documentation-only commits, if any**: None

### Requirement Evidence Mapping

| Requirement | File / Script / Output | Git Commit Hash | Video Timestamp |
| :--- | :--- | :--- | :--- |
| **Part 1 Log Analysis** | `log_analysis.md`, `troubleshooting.md` | `55e8aca7c8fef3130dbed3d96de210d35a807c75` | `[01:30]` |
| **Part 2 Docker & NGINX Topology** | `docker-compose.yml`, `nginx/nginx.conf` | `55e8aca7c8fef3130dbed3d96de210d35a807c75` | `[04:00]` |
| **Part 2 Port & Network Isolation** | `docker-compose.yml`, `validate.py` | `55e8aca7c8fef3130dbed3d96de210d35a807c75` | `[06:15]` |
| **Part 3 Automated Validation** | `python validate.py` (8/8 PASS) | `55e8aca7c8fef3130dbed3d96de210d35a807c75` | `[08:30]` |
| **Part 3 Failure Injection & Recovery** | `python failure_test.py` (3/3 PASS) | `55e8aca7c8fef3130dbed3d96de210d35a807c75` | `[10:00]` |
| **Part 3 PostgreSQL Backup & Restore** | `backup.sh`, `restore.sh`, `backup.ps1` | `55e8aca7c8fef3130dbed3d96de210d35a807c75` | `[12:15]` |
| **Part 3 GitHub Actions CI/CD** | `.github/workflows/ci.yml` | `55e8aca7c8fef3130dbed3d96de210d35a807c75` | `[13:30]` |
| **Part 5 Recorded Challenge Execution** | `./video_challenge.sh` | `00f45045c16243d5bdc69ad23a44bcea` | `[14:45]` |
| **Part 5 Live Port Change (8080 -> 8090)** | `docker-compose.yml` (`PUBLIC_PORT=8090`) | `a00aeff1da103cb717e29edcfe0d3b0397dd4c8d` | `[16:00]` |
| **Part 5 Live Scaling (app-03)** | `docker-compose.yml` (`app-03` addition) | `a00aeff1da103cb717e29edcfe0d3b0397dd4c8d` | `[17:15]` |
