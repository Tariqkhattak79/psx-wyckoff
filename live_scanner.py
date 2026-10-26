import pandas as pd
import os
import json

DATA_FOLDER = "data"
MIN_DROP_PCT = 3.0     
LOOKBACK_DAYS = 60     

def run_scan():
    results = []
    if not os.path.exists(DATA_FOLDER): return
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv')]
    
    for i, filename in enumerate(files):
        sym = filename.replace(".csv", "")
        path = os.path.join(DATA_FOLDER, filename)
        try:
            df = pd.read_csv(path)
            df = df.sort_values("date").reset_index(drop=True)
            if len(df) < 20: continue
            
            today = df.iloc[-1]
            yesterday = df.iloc[-2]
            
            prev_is_red = yesterday['close'] < yesterday['open']
            is_green = today['close'] > today['open']
            low_vol = today['volume'] < yesterday['volume']
            
            lookback_window = df.tail(LOOKBACK_DAYS)
            high_idx = lookback_window['high'].idxmax()
            recent_high = df.loc[high_idx, 'high']
            drop_pct = ((recent_high - yesterday['low']) / recent_high) * 100
            is_downtrend = drop_pct >= MIN_DROP_PCT
            days_since_high = len(df) - 1 - high_idx

            avg_vol20 = df['volume'].tail(20).mean()
            is_cat_a = (yesterday['volume'] > (avg_vol20 * 1.2)) and (today['volume'] < (yesterday['volume'] * 0.6))
            
            if prev_is_red and is_green and low_vol and is_downtrend:
                entry = round(today['close'], 2)
                
                # FIX: Stop must be BELOW entry
                calculated_stop = round(yesterday['low'] * 0.99, 2)
                stop = calculated_stop if calculated_stop < entry else round(entry * 0.98, 2)
                
                risk = entry - stop
                target = round(entry + (risk * 2), 2)
                
                category = "CAT A" if is_cat_a else "CAT B"
                
                results.append({
                    "symbol": sym,
                    "entry": entry,
                    "stop": stop,
                    "target": target,
                    "today_vol": int(today['volume']),
                    "prev_vol": int(yesterday['volume']),
                    "drop_pct": round(drop_pct, 1),
                    "drop_days": int(days_since_high),
                    "category": category
                })
        except Exception: pass

    if os.path.exists("live_scan.json"): os.remove("live_scan.json")
    with open("live_scan.json", "w") as f: json.dump(results, f, indent=4)
    print(f"Found {len(results)} signals.")

if __name__ == "__main__": run_scan()
