import psxdata
import pandas as pd
import datetime
import json

def run_scan():
    results = []
    print("Fetching live data directly from PSX...")
    
    try:
        syms = psxdata.indices("KSE100")["symbol"].tolist()
    except:
        syms = ['LUCK', 'SHEZ', 'LOTCHEM', 'OGDC', 'PPL', 'MARI', 'MCB', 'MEBL', 'HBL', 'UBL'] # Fallback
        
    print(f"Scanning {len(syms)} symbols...")
    end = datetime.date.today()
    start = end - datetime.timedelta(days=20)

    for sym in syms:
        try:
            df = psxdata.stocks(sym, start=str(start), end=str(end))
            if df is None or len(df) < 6:
                continue
                
            df = df.sort_values("date").reset_index(drop=True)
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
                print(f"SIGNAL: {sym}")
        except Exception as e:
            pass

    with open("live_scan.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"Done. Found {len(results)} signals.")

if __name__ == "__main__":
    run_scan()
