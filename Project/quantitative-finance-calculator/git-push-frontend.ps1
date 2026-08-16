# Git Push Frontend Fix
$gitPath = "C:\Program Files\Git\cmd\git.exe"

Write-Host "=== Pushing Frontend Fixes ===" -ForegroundColor Cyan

# 1. Add changes
& $gitPath add client/src/components/InvestmentReturnCalculator.tsx

# 2. Commit
& $gitPath commit -m "Fix TypeScript build error: Remove unused variables"

# 3. Push
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
& $gitPath push origin main

Write-Host "`n=== Done! Check Render for new build. ===" -ForegroundColor Green
