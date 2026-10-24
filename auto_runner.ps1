Set-Location "C:\Users\Tariq Usman\Desktop\psx-wyckoff"

# 1. Run the Python scanner
python live_scanner.py

# 2. Push to GitHub safely
if (Test-Path "live_scan.json") {
    # Sync with GitHub first to avoid errors
    git pull origin main --rebase
    
    # Add, Commit, and Push
    git add live_scan.json
    git commit -m "Automated 3PM scan update"
    git push origin main
}