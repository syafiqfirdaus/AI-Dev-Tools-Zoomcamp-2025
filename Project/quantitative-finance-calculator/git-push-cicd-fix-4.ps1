# Git Push CI/CD Fix 4
$gitPath = "C:\Program Files\Git\cmd\git.exe"

Write-Host "=== Pushing CI/CD Fixes (Round 4) ===" -ForegroundColor Cyan

# 1. Add changes
& $gitPath add .github/workflows/ci-cd.yml
& $gitPath add SOCIAL_MEDIA.md

# 2. Commit
& $gitPath commit -m "Fix CI/CD: Remove redundant Docker Hub build steps (using Render Auto-Deploy)"

# 3. Push
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
& $gitPath push origin main

Write-Host "`n=== Done! Pipeline should be 100% Green now. ===" -ForegroundColor Green
