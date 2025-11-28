# Local Setup Script for People Tool
# This script sets up the local development environment

Write-Host "Setting up People Tool for local development..." -ForegroundColor Green

# Check prerequisites
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.13+" -ForegroundColor Red
    exit 1
}

# Check Node
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 20+" -ForegroundColor Red
    exit 1
}

# Check PostgreSQL (optional - will warn if not found)
try {
    $pgVersion = psql --version 2>&1
    Write-Host "✓ PostgreSQL client found: $pgVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ PostgreSQL client not found. You may need to install PostgreSQL or use Docker for the database." -ForegroundColor Yellow
}

# Setup Backend
Write-Host "`nSetting up backend..." -ForegroundColor Yellow
Set-Location src/api

# Install uv if not present
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..." -ForegroundColor Cyan
    pip install uv
}

# Sync dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
uv sync

# Create .env if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file..." -ForegroundColor Cyan
    @"
APP_VERSION=0.1.0
APP_NAME=person-tool
APP_PORT=8000
APP_HOST=0.0.0.0
APP_RELOAD=true
APP_LOG_LEVEL=INFO
APP_BASE_API_URL=/api/v1

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=PeopleDb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_MIN_POOL_SIZE=1
POSTGRES_MAX_POOL_SIZE=10
"@ | Out-File -FilePath .env -Encoding utf8
    Write-Host "✓ Created .env file. Please update with your PostgreSQL credentials if needed." -ForegroundColor Green
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Set-Location ../..

# Setup Frontend
Write-Host "`nSetting up frontend..." -ForegroundColor Yellow
Set-Location src/ui/person-tool

if (-not (Test-Path node_modules)) {
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Cyan
    npm install
} else {
    Write-Host "✓ Node modules already installed" -ForegroundColor Green
}

Set-Location ../..

Write-Host "`n✓ Setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Make sure PostgreSQL is running and create the PeopleDb database" -ForegroundColor White
Write-Host "2. Initialize the database schema (see LOCAL_SETUP.md)" -ForegroundColor White
Write-Host "3. Run '.\start-local.ps1' to start the application" -ForegroundColor White

