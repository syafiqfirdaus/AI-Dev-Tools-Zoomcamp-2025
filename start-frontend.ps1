# Start Frontend Server - Uses full Node.js path

# Add Node.js to PATH for this session so Vite can find 'node'
$nodePath = "C:\Program Files\nodejs"
$env:Path = "$nodePath;$env:Path"

Write-Host "Starting Frontend Development Server..." -ForegroundColor Cyan
Write-Host "App will be at: http://localhost:5173" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow

Set-Location -Path ".\client"
npm run dev
