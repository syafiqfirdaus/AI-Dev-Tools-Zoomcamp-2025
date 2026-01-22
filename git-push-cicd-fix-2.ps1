# Git Push CI/CD Fix 2
$gitPath = "C:\Program Files\Git\cmd\git.exe"

Write-Host "=== Pushing CI/CD Fixes (Round 2) ===" -ForegroundColor Cyan

# 1. Add changes
& $gitPath add .github/workflows/ci-cd.yml
& $gitPath add client/src/App.test.tsx

# 2. Commit
& $gitPath commit -m "Fix CI/CD: Install dev extras and fix test import path"

# 3. Push
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
& $gitPath push origin main

Write-Host "`n=== Done! Check Actions tab again. ===" -ForegroundColor Green
