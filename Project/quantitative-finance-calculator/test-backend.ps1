# Test Backend - Uses full Python path
# No need to restart PC or VS Code!

$python = "C:\Users\muhds\AppData\Local\Programs\Python\Python312\python.exe"
$pip = "C:\Users\muhds\AppData\Local\Programs\Python\Python312\Scripts\pip.exe"

Write-Host "=== Setting up Backend ===" -ForegroundColor Cyan

# Navigate to server folder
Set-Location -Path ".\server"

# Install UV if not installed
Write-Host "`nInstalling UV..." -ForegroundColor Yellow
& $pip install uv

# Install dependencies
Write-Host "`nInstalling dependencies with UV..." -ForegroundColor Yellow  
& $python -m uv sync

# Run tests
Write-Host "`n=== Running Backend Tests ===" -ForegroundColor Cyan
& $python -m uv run pytest --cov=app tests/ -v

Write-Host "`n=== Tests Complete ===" -ForegroundColor Green
Write-Host "`nTo start the backend server, run:" -ForegroundColor Cyan
Write-Host "  .\start-backend.ps1" -ForegroundColor White
