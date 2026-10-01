import pandas as pd 
import sys 
 
LOOKBACK = 60 
SPRING_WINDOW = 30 
MIN_SC_AGE = 20 
 
def detect_spring(sym): 
    df = pd.read_csv("data/" + sym + ".csv") 
    df = df.sort_values("date").reset_index(drop=True) 
    if len(df) < LOOKBACK: return 
    w = df.tail(LOOKBACK).reset_index(drop=True) 
    sc_idx = w["low"].idxmin() 
    sc_low = w["low"].iloc[sc_idx] 
    sc_age = LOOKBACK - 1 - sc_idx 
    if sc_age < MIN_SC_AGE: return 
    after_sc = w.iloc[sc_idx+1:].reset_index(drop=True) 
    ar_high = after_sc["high"].max() 
    resistance = ar_high 
    support = sc_low 
    width = resistance - support 
    recent = w.tail(SPRING_WINDOW).reset_index(drop=True) 
    avg_vol20 = w["volume"].tail(20).mean() 
    found = [] 
    for i in range(len(recent)): 
        r = recent.iloc[i] 
        if r["low"] < support and r["close"] > support: 
            depth_pct = 100.0 * (support - r["low"]) / support 
            vol_ratio = r["volume"] / avg_vol20 if avg_vol20 > 0 else 0 
            if depth_pct > 5: 
                typ = "Shakeout" 
            elif vol_ratio <= 1.0: 
                typ = "Type3" 
            else: 
                typ = "Type2" 
            found.append((r["date"], r["low"], r["close"], vol_ratio, depth_pct, typ)) 
    if not found: return 
    print("--- " + sym + " ---") 
    print("Range: sup=" + str(round(support,2)) + " res=" + str(round(resistance,2)) + " width=" + str(round(width,2))) 
    for f in found: 
        entry = f[2] 
        stop = f[1] * 0.98 
        target = resistance + width 
        print("Spring " + f[5] + " on " + str(f[0]) + " low=" + str(round(f[1],2)) + " close=" + str(round(f[2],2)) + " volRatio=" + str(round(f[3],2)) + " depth=" + str(round(f[4],1)) + " pct") 
        print("   Entry=" + str(round(entry,2)) + " Stop=" + str(round(stop,2)) + " Target=" + str(round(target,2))) 
 
if __name__ == "__main__": 
    for s in sys.argv[1:]: 
        detect_spring(s) 
