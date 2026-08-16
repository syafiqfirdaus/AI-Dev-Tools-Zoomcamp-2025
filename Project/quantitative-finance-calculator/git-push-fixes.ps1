# Git Push Final Fixes
$gitPath = "C:\Program Files\Git\cmd\git.exe"

Write-Host "=== Pushing Final Documentation Updates ===" -ForegroundColor Cyan

# 1. Add changes (specifically README)
& $gitPath add README.md

# 2. Commit
& $gitPath commit -m "Update README with live project URLs"

# 3. Push
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
& $gitPath push origin main

Write-Host "`n=== Done! Project is fully deployed and documented. ===" -ForegroundColor Green
