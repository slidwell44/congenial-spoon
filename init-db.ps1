# Database Initialization Script
# This script initializes the database schema and seeds test data

param(
    [string]$Host = "localhost",
    [string]$Port = "5432",
    [string]$Database = "PeopleDb",
    [string]$User = "postgres",
    [string]$Password = "postgres"
)

Write-Host "Initializing database..." -ForegroundColor Green

# Set PGPASSWORD environment variable
$env:PGPASSWORD = $Password

# Check if database exists, create if not
Write-Host "Checking if database exists..." -ForegroundColor Yellow
$dbExists = psql -h $Host -p $Port -U $User -lqt | Select-String -Pattern "^\s*$Database\s"

if (-not $dbExists) {
    Write-Host "Creating database $Database..." -ForegroundColor Cyan
    createdb -h $Host -p $Port -U $User $Database
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to create database. Please create it manually." -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Database created" -ForegroundColor Green
} else {
    Write-Host "✓ Database already exists" -ForegroundColor Green
}

# Initialize schema using Python script (which will also seed if empty)
Write-Host "`nInitializing schema and seeding data..." -ForegroundColor Yellow
Set-Location src/api

# First, try to run the schema SQL files if psql is available
if (Get-Command psql -ErrorAction SilentlyContinue) {
    Write-Host "Running schema SQL files..." -ForegroundColor Cyan
    Get-Content "person_tool/db/sql/schema.pgsql" | psql -h $Host -p $Port -U $User -d $Database
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Schema initialized" -ForegroundColor Green
    }
}

# Run seed script
Write-Host "Running seed script..." -ForegroundColor Cyan
uv run python -m person_tool.db.seed_data
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database seeded with test data" -ForegroundColor Green
} else {
    Write-Host "⚠ Seed script had issues. Check the output above." -ForegroundColor Yellow
}

Set-Location ../..

Write-Host "`n✓ Database initialization complete!" -ForegroundColor Green

