# PostgreSQL Backup Script for PowerShell
$BackupDir = ".\database\backups"
$BackupFile = "$BackupDir\latest_backup.sql"

Write-Host "=== Creating PostgreSQL Database Backup ==="
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

docker exec postgres pg_dump -U barq_app -d barq_tasks > $BackupFile
if ($LASTEXITCODE -eq 0) {
    Write-Host "[PASS] PostgreSQL backup successfully saved to $BackupFile"
    Write-Host "Backup file size: $((Get-Item $BackupFile).Length) bytes"
    exit 0
} else {
    Write-Host "[FAIL] PostgreSQL backup failed"
    exit 1
}
