Write-Host "Starting PSX Exhaustion Scan..." -ForegroundColor Cyan
python live_scanner.py

if (Test-Path "live_scan.json") {
    Write-Host "Scan finished. Pushing to GitHub..." -ForegroundColor Yellow
    git add live_scan.json
    git commit -m "Manual live scan update"
    git push
    Write-Host "Done! Open your app to see the results." -ForegroundColor Green
} else {
    Write-Host "Error: live_scan.json was not created." -ForegroundColor Red
}