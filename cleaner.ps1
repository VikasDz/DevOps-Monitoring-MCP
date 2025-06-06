# Save this as reset-docker.ps1 in your project root

Write-Host "=== Docker Compose Reset Script ===" -ForegroundColor Cyan
Write-Host "This will:"
Write-Host "1. Stop and remove all containers"
Write-Host "2. Remove all unused images"
Write-Host "3. Rebuild services with no cache"
Write-Host "4. Start services in detached mode"

$ErrorActionPreference = "Stop"

try {
    # Step 1: Clean up containers
    Write-Host "`n[1/4] Stopping and removing containers..." -ForegroundColor Yellow
    docker-compose down -v
    if ($LASTEXITCODE -ne 0) { throw "docker-compose down failed" }

    # Step 2: Prune system
    Write-Host "`n[2/4] Pruning Docker system..." -ForegroundColor Yellow
    docker system prune -a -f
    if ($LASTEXITCODE -ne 0) { throw "docker prune failed" }

    # Step 3: Rebuild
    Write-Host "`n[3/4] Rebuilding services with no cache..." -ForegroundColor Yellow
    docker-compose build --no-cache
    if ($LASTEXITCODE -ne 0) { throw "docker-compose build failed" }

    # Step 4: Start services
    Write-Host "`n[4/4] Starting services..." -ForegroundColor Yellow
    docker-compose up -d
    if ($LASTEXITCODE -ne 0) { throw "docker-compose up failed" }

    Write-Host "`nSUCCESS: All operations completed" -ForegroundColor Green
    Write-Host "Check running containers with: docker-compose ps" -ForegroundColor Cyan
}
catch {
    Write-Host "`nERROR: $_" -ForegroundColor Red
    Write-Host "Script failed at step $step" -ForegroundColor Red
    exit 1
}