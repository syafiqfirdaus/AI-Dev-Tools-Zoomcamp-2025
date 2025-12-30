# Deploy to GitHub Script (Fixed)
$gitPath = "C:\Program Files\Git\cmd\git.exe"

Write-Host "=== Setting up Git Repository ===" -ForegroundColor Cyan

# 1. CLEANUP: Remove broken .git directory if it exists
if (Test-Path ".git") {
    Write-Host "Found existing .git directory. Removing it to fix permission issues..." -ForegroundColor Yellow
    Remove-Item -Path ".git" -Recurse -Force
}

# 2. CONFIG: Check/Set User
$email = & $gitPath config --global user.email
if (-not $email) {
    Write-Host "Git user.email not set. Please enter it:" -ForegroundColor Yellow
    $userEmail = Read-Host "Email"
    & $gitPath config --global user.email $userEmail
    
    Write-Host "Git user.name not set. Please enter it:" -ForegroundColor Yellow
    $userName = Read-Host "Name"
    & $gitPath config --global user.name $userName
}

# 3. INIT & COMMIT
Write-Host "Initializing new repository..." -ForegroundColor Cyan
& $gitPath init

Write-Host "Adding files (this might take a moment)..." -ForegroundColor Cyan
& $gitPath add .

Write-Host "Committing..." -ForegroundColor Cyan
& $gitPath commit -m "Initial commit of Quantitative Finance Calculator"

# 4. PUSH
Write-Host "Connecting to GitHub..." -ForegroundColor Cyan
& $gitPath branch -M main
& $gitPath remote add origin "https://github.com/syafiqfirdaus/quantitative-finance-calculator.git"

Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "Note: A browser window or login prompt might appear." -ForegroundColor Yellow
& $gitPath push -u origin main -f

Write-Host "`n=== Done! ===" -ForegroundColor Green
