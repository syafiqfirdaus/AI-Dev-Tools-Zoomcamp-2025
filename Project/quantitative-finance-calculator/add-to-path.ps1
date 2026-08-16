# Add Python and Node.js to PATH
# Run this script in PowerShell as Administrator

# Python paths
$pythonPath = "C:\Users\muhds\AppData\Local\Programs\Python\Python312"
$pythonScriptsPath = "C:\Users\muhds\AppData\Local\Programs\Python\Python312\Scripts"

# Node.js path
$nodePath = "C:\Program Files\nodejs"

# Get current User PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

# Add paths if not already present
$pathsToAdd = @($pythonPath, $pythonScriptsPath, $nodePath)

foreach ($path in $pathsToAdd) {
    if ($currentPath -notlike "*$path*") {
        Write-Host "Adding to PATH: $path" -ForegroundColor Green
        $currentPath = "$currentPath;$path"
    } else {
        Write-Host "Already in PATH: $path" -ForegroundColor Yellow
    }
}

# Set the new PATH
[Environment]::SetEnvironmentVariable("Path", $currentPath, "User")

Write-Host "`nPATH updated successfully!" -ForegroundColor Green
Write-Host "`nIMPORTANT: Close and reopen your terminal for changes to take effect." -ForegroundColor Cyan
Write-Host "`nThen verify with:" -ForegroundColor Cyan
Write-Host "  python --version" -ForegroundColor White
Write-Host "  node --version" -ForegroundColor White
Write-Host "  npm --version" -ForegroundColor White
