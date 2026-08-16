# Setup Frontend - Uses full Node.js path

# Add Node.js to PATH for this session
$nodePath = "C:\Program Files\nodejs"
$env:Path = "$nodePath;$env:Path"

Write-Host "=== Setting up Frontend ===" -ForegroundColor Cyan

Set-Location -Path ".\client"

Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
npm install

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "`nTo start the frontend, run:" -ForegroundColor Cyan
Write-Host "  .\start-frontend.ps1" -ForegroundColor White
