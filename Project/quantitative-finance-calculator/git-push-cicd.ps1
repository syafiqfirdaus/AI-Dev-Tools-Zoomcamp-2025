# Git Push CICD Fixes
$gitPath = "C:\Program Files\Git\cmd\git.exe"

Write-Host "=== Pushing CI/CD Fixes ===" -ForegroundColor Cyan

# 1. Add changes
& $gitPath add .github/workflows/ci-cd.yml
& $gitPath add client/src/App.test.tsx

# 2. Commit
& $gitPath commit -m "Fix CI/CD: Add README copy for backend and initial test for frontend"

# 3. Push
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
& $gitPath push origin main

Write-Host "`n=== Done! Check Actions tab on GitHub. ===" -ForegroundColor Green
