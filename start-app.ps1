# Start Application Script
# This script starts the People Tool application using Docker Compose

Write-Host "Starting People Tool..." -ForegroundColor Green

# Check if Docker is available
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "`n✗ Docker is not installed or not in PATH." -ForegroundColor Red
    Write-Host "`nPlease install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Write-Host "`nAlternatively, you can run the app locally without Docker:" -ForegroundColor Yellow
    Write-Host "  1. Run '.\setup-local.ps1' to set up dependencies" -ForegroundColor White
    Write-Host "  2. Run '.\init-db.ps1' to initialize the database" -ForegroundColor White
    Write-Host "  3. Run '.\start-local.ps1' to start the app" -ForegroundColor White
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "`n✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker is available and running" -ForegroundColor Green

# Check if docker-compose.yml exists
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "`n✗ docker-compose.yml not found in current directory." -ForegroundColor Red
    exit 1
}

Write-Host "`nStarting services with Docker Compose..." -ForegroundColor Yellow
Write-Host "This may take a few minutes on first run (downloading images, building containers)..." -ForegroundColor Cyan

# Start docker-compose
try {
    docker compose up --build
} catch {
    Write-Host "`n✗ Failed to start Docker Compose." -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Make sure Docker Desktop is running" -ForegroundColor White
    Write-Host "  2. Check if ports 3000, 8000, and 5432 are available" -ForegroundColor White
    Write-Host "  3. Try: docker compose down (to clean up) then docker compose up again" -ForegroundColor White
    Write-Host "  4. See DOCKER_TROUBLESHOOTING.md for more help" -ForegroundColor White
    exit 1
}

