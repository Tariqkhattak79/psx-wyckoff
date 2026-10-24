import pandas as pd
import os
import json
import datetime

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
            df = pd.read_csv(path)
            df = df.sort_values("date").reset_index(drop=True)
            
            if len(df) < 6:
                continue

            today = df.iloc[-1]
            yesterday = df.iloc[-2]
            
            prev_is_red = yesterday['close'] < yesterday['open']
            is_green = today['close'] > today['open']
            low_vol = today['volume'] < yesterday['volume']
            
            last_5_days = df.iloc[-6:-1] 
            red_days_count = sum(last_5_days['close'] < last_5_days['open'])
            continuous_drop = red_days_count >= 3

            if prev_is_red and is_green and low_vol and continuous_drop:
                entry = round(today['close'], 2)
                stop = round(yesterday['low'] * 0.99, 2)
                target = round(entry + ((entry - stop) * 2), 2)
                
                results.append({
                    "symbol": sym,
                    "entry": entry,
                    "stop": stop,
                    "target": target,
                    "today_vol": int(today['volume']),
                    "prev_vol": int(yesterday['volume']),
                    "red_days": int(red_days_count)
                })
                print(f"SIGNAL FOUND: {sym}")

        except Exception as e:
            pass 
            
        print(f"Scanning {i+1}/{len(files)}...", end="\r")

    if os.path.exists("live_scan.json"):
        os.remove("live_scan.json")
        
    with open("live_scan.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"\nScan Complete. Found {len(results)} signals. Saved to live_scan.json")

if __name__ == "__main__":
    run_scan()