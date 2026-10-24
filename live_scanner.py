import pandas as pd
import os
import json

DATA_FOLDER = "data"
MIN_DROP_PCT = 3.0     # Minimum total drop over 2 months
MIN_RED_CANDLE = 2.0   # Yesterday's red candle must drop at least 2%
LOOKBACK_DAYS = 60     # Look back 2 months

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
            yesterday = df.iloc[-2]
            
            # 1. MACRO DOWNTREND (60 Days)
            lookback_window = df.tail(LOOKBACK_DAYS)
            high_idx = lookback_window['high'].idxmax()
            recent_high = df.loc[high_idx, 'high']
            drop_pct = ((recent_high - today['low']) / recent_high) * 100
            is_downtrend = drop_pct >= MIN_DROP_PCT
            days_since_high = len(df) - 1 - high_idx
            
            # 2. YESTERDAY WAS A BIG RED CANDLE
            # Calculate the size of yesterday's candle body (open to close)
            red_candle_size = ((yesterday['open'] - yesterday['close']) / yesterday['open']) * 100
            is_big_red = (yesterday['close'] < yesterday['open']) and (red_candle_size >= MIN_RED_CANDLE)
            
            # 3. TODAY IS A LOW VOLUME GREEN CANDLE
            is_green = today['close'] > today['open']
            avg_prev_vol = df['volume'].iloc[-4:-1].mean()
            low_vol = today['volume'] < avg_prev_vol

            if is_green and low_vol and is_downtrend and is_big_red:
                entry = round(today['close'], 2)
                stop = round(yesterday['low'] * 0.99, 2) # Stop below the big red candle
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
                print(f"SIGNAL: {sym} (Yesterday Dropped {red_candle_size:.1f}%)")
        except Exception: pass

    with open("live_scan.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"\nScan Complete. Found {len(results)} signals.")

if __name__ == "__main__":
    run_scan()
