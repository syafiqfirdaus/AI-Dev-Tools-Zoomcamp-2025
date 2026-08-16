# Git Push Fix Script
$gitPath = "C:\Program Files\Git\cmd\git.exe"

Write-Host "=== Pushing Fixes to GitHub ===" -ForegroundColor Cyan

# 1. Add all changes (including the Dockerfile fix)
Write-Host "Adding files..." -ForegroundColor Cyan
& $gitPath add .

# 2. Check if there are changes to commit
$status = & $gitPath status --porcelain
if ($status) {
    Write-Host "Committing changes..." -ForegroundColor Cyan
    & $gitPath commit -m "Fix Dockerfile build: Include README.md"
} else {
    Write-Host "No new changes to commit." -ForegroundColor Yellow
}

# 3. Push
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
& $gitPath branch -M main
& $gitPath push -u origin main

Write-Host "`n=== Done! ===" -ForegroundColor Green
