import pandas as pd
import os
import json

# --- CONFIGURATION ---
DATA_FOLDER = "data"

def run_scan():
    results = []
    
    if not os.path.exists(DATA_FOLDER):
        print("ERROR: 'data' folder not found. Please run fetch_data.py first.")
        return

    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv')]
    print(f"Starting Scan of {len(files)} symbols from PSX data...")
    
    for i, filename in enumerate(files):
        sym = filename.replace(".csv", "")
        path = os.path.join(DATA_FOLDER, filename)
        
        try:
            # 1. Load the CSV
            df = pd.read_csv(path)
            df = df.sort_values("date").reset_index(drop=True)
            
            # Need at least 6 days of data to check the last 5 days + today
            if len(df) < 6:
                continue

            # 2. Get Today and Yesterday Data
            today = df.iloc[-1]
            yesterday = df.iloc[-2]
            
            # 3. The Logic
            # Condition A: Yesterday was RED
            prev_is_red = yesterday['close'] < yesterday['open']
            
            # Condition B: Today is GREEN
            is_green = today['close'] > today['open']
            
            # Condition C: Today's Volume is LOWER than yesterday's
            low_vol = today['volume'] < yesterday['volume']
            
            # Condition D: At least 3 red candles in the 5 days before today
            last_5_days = df.iloc[-6:-1] 
            red_days_count = sum(last_5_days['close'] < last_5_days['open'])
            continuous_drop = red_days_count >= 3

            if prev_is_red and is_green and low_vol and continuous_drop:
                entry = round(today['close'], 2)
                stop = round(yesterday['low'] * 0.99, 2) # 1% below yesterday's low
                risk = entry - stop
                target = round(entry + (risk * 2), 2) # 1:2 Risk Reward
                
                results.append({
                    "symbol": sym,
                    "entry": entry,
                    "stop": stop,
                    "target": target,
                    "today_vol": int(today['volume']),
                    "prev_vol": int(yesterday['volume']),
                    "red_days": int(red_days_count)
                })
                print(f"\nSIGNAL FOUND: {sym}")

        except Exception as e:
            pass # Skip files that are empty or have bad data
            
        print(f"Scanning {i+1}/{len(files)}...", end="\r")

    # --- THE FIX: DELETE OLD FILE, THEN WRITE FRESH DATA ---
    if os.path.exists("live_scan.json"):
        os.remove("live_scan.json")
        
    with open("live_scan.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"\nScan Complete. Found {len(results)} signals. Saved to live_scan.json")
    print("You can now open psx_app.html to view the results!")

if __name__ == "__main__":
    run_scan()