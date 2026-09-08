#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="./database/backups"
BACKUP_FILE="${BACKUP_DIR}/latest_backup.sql"

# Detect docker command (docker or docker.exe)
DOCKER_CMD="docker"
if ! command -v docker >/dev/null 2>&1 && command -v docker.exe >/dev/null 2>&1; then
    DOCKER_CMD="docker.exe"
fi

echo "=== Creating PostgreSQL Database Backup ==="
mkdir -p "${BACKUP_DIR}"

if ${DOCKER_CMD} exec postgres pg_dump -U barq_app -d barq_tasks > "${BACKUP_FILE}"; then
    echo "[PASS] PostgreSQL backup successfully saved to ${BACKUP_FILE}"
    echo "Backup file size: $(wc -c < "${BACKUP_FILE}") bytes"
    exit 0
else
    echo "[FAIL] PostgreSQL backup failed" >&2
    exit 1
fi
