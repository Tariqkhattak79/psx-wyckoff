import pandas as pd 
import sys 
 
LOOKBACK = 60 
MIN_SC_AGE = 20 
 
def detect(sym): 
    df = pd.read_csv("data/" + sym + ".csv") 
    df = df.sort_values("date").reset_index(drop=True) 
    if len(df) < LOOKBACK: return 
    w = df.tail(LOOKBACK).reset_index(drop=True) 
    sc_idx = w["low"].idxmin() 
    sc_age = LOOKBACK - 1 - sc_idx 
    if sc_age < MIN_SC_AGE: return 
    after = w.iloc[sc_idx+1:].reset_index(drop=True) 
    resistance = after["high"].max() 
    support = w["low"].iloc[sc_idx] 
    width = resistance - support 
    avg_vol20 = w["volume"].tail(20).mean() 
    sos_idx = None 
    for i in range(len(after)): 
        r = after.iloc[i] 
        if r["close"] > resistance and r["volume"] > avg_vol20 * 1.5: 
            sos_idx = i 
            break 
    if sos_idx is None: return 
    sos = after.iloc[sos_idx] 
    post = after.iloc[sos_idx+1:].reset_index(drop=True) 
    lps = None 
    for i in range(len(post)): 
        r = post.iloc[i] 
        if r["low"] <= sos["close"] * 1.02 and r["close"] > resistance: 
            lps = r 
            break 
    target = resistance + width 
    print("--- " + sym + " ---") 
    print("Range: sup=" + str(round(support,2)) + " res=" + str(round(resistance,2))) 
    print("SOS:  " + str(sos["date"]) + " close=" + str(round(sos["close"],2)) + " volRatio=" + str(round(sos["volume"]/avg_vol20,2))) 
    if lps is not None: 
        print("LPS:  " + str(lps["date"]) + " close=" + str(round(lps["close"],2))) 
        print("  Entry(add)=" + str(round(lps["close"],2)) + " Stop=" + str(round(resistance*0.98,2)) + " Target=" + str(round(target,2))) 
    else: 
        print("LPS:  none yet (wait for pullback)") 
 
if __name__ == "__main__": 
    for s in sys.argv[1:]: 
        detect(s) 
