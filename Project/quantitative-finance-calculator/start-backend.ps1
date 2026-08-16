# Start Backend Server - Uses full Python path

$python = "C:\Users\muhds\AppData\Local\Programs\Python\Python312\python.exe"

Write-Host "Starting Backend API Server..." -ForegroundColor Cyan
Write-Host "API will be at: http://localhost:8000" -ForegroundColor Green
Write-Host "Docs will be at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow

Set-Location -Path ".\server"
& $python -m uv run uvicorn app.main:app --reload
