#!/usr/bin/env bash
set -euo pipefail

BACKUP_FILE="./database/backups/latest_backup.sql"

# Detect docker command (docker or docker.exe)
DOCKER_CMD="docker"
if ! command -v docker >/dev/null 2>&1 && command -v docker.exe >/dev/null 2>&1; then
    DOCKER_CMD="docker.exe"
fi

echo "=== Restoring PostgreSQL Database Backup ==="

if [[ ! -f "${BACKUP_FILE}" ]]; then
    echo "[FAIL] Backup file ${BACKUP_FILE} not found!" >&2
    exit 1
fi

if ${DOCKER_CMD} exec -i postgres psql -U barq_app -d barq_tasks < "${BACKUP_FILE}"; then
    echo "[PASS] PostgreSQL database successfully restored from ${BACKUP_FILE}"
    exit 0
else
    echo "[FAIL] PostgreSQL restore failed" >&2
    exit 1
fi
