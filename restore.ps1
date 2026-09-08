# PostgreSQL Restore Script for PowerShell
$BackupFile = ".\database\backups\latest_backup.sql"

Write-Host "=== Restoring PostgreSQL Database Backup ==="

if (!(Test-Path $BackupFile)) {
    Write-Host "[FAIL] Backup file $BackupFile not found!"
    exit 1
}

Get-Content $BackupFile | docker exec -i postgres psql -U barq_app -d barq_tasks
if ($LASTEXITCODE -eq 0) {
    Write-Host "[PASS] PostgreSQL database successfully restored from $BackupFile"
    exit 0
} else {
    Write-Host "[FAIL] PostgreSQL restore failed"
    exit 1
}
