import pandas as pd
import os
import json

DATA_FOLDER = "data"
MIN_DROP_PCT = 3.0   # Lowered to 3% to catch everything
LOOKBACK_DAYS = 60   # Look back 2 months (approx 60 trading days)

def run_scan():
    results = []
    if not os.path.exists(DATA_FOLDER):
        return
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv')]
    print(f"Starting Scan of {len(files)} symbols...")
    
    for i, filename in enumerate(files):
        sym = filename.replace(".csv", "")
        path = os.path.join(DATA_FOLDER, filename)
        try:
            df = pd.read_csv(path)
            df = df.sort_values("date").reset_index(drop=True)
            if len(df) < 10: continue
            
            today = df.iloc[-1]
            
            # MACRO DOWNTREND (60 Days)
            lookback_window = df.tail(LOOKBACK_DAYS)
            high_idx = lookback_window['high'].idxmax()
            recent_high = df.loc[high_idx, 'high']
            
            # Calculate drop from high to today's low
            drop_pct = ((recent_high - today['low']) / recent_high) * 100
            is_downtrend = drop_pct >= MIN_DROP_PCT
            days_since_high = len(df) - 1 - high_idx
            
            # EXHAUSTION BOUNCE
            is_green = today['close'] > today['open']
            
            # Today's volume must be lower than the average of the last 3 days
            avg_prev_vol = df['volume'].iloc[-4:-1].mean()
            low_vol = today['volume'] < avg_prev_vol
            
            # At least 3 red days in the last 5 days (choppy downtrend)
            last_5_days = df.iloc[-6:-1]
            red_days_count = sum(last_5_days['close'] < last_5_days['open'])
            recent_red = red_days_count >= 3

            if is_green and low_vol and is_downtrend and recent_red:
                entry = round(today['close'], 2)
                stop = round(df['low'].iloc[-3:].min() * 0.99, 2)
                target = round(entry + ((entry - stop) * 2), 2)
                
                results.append({
                    "symbol": sym,
                    "entry": entry,
                    "stop": stop,
                    "target": target,
                    "today_vol": int(today['volume']),
                    "prev_vol": int(avg_prev_vol),
                    "drop_pct": round(drop_pct, 1),
                    "drop_days": int(days_since_high)
                })
                print(f"SIGNAL: {sym} (Drop {drop_pct:.1f}% over {days_since_high} days)")
        except Exception: pass

    with open("live_scan.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"\nScan Complete. Found {len(results)} signals.")

if __name__ == "__main__":
    run_scan()
