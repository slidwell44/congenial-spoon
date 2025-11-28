# Start Local Development Script
# This script starts the backend and frontend in separate terminals

Write-Host "Starting People Tool locally..." -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path "src/api/.env")) {
    Write-Host "✗ .env file not found. Please run '.\setup-local.ps1' first." -ForegroundColor Red
    exit 1
}

# Start Backend
Write-Host "`nStarting backend on http://localhost:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\src\api'; Write-Host 'Backend starting...' -ForegroundColor Green; uv run uvicorn person_tool.main:app --reload"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting frontend on http://localhost:3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\src\ui\person-tool'; Write-Host 'Frontend starting...' -ForegroundColor Green; npm start"

Write-Host "`n✓ Backend and frontend are starting in separate windows." -ForegroundColor Green
Write-Host "`nAccess the application:" -ForegroundColor Yellow
Write-Host "- Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "- Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "- API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`nTo seed test data, run in a new terminal:" -ForegroundColor Yellow
Write-Host "  cd src/api" -ForegroundColor White
Write-Host "  uv run python -m person_tool.db.seed_data" -ForegroundColor White

