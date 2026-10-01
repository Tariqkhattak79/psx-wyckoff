import pandas as pd 
import sys 
 
LOOKBACK = 60 
TOUCH_PCT = 0.02 
MIN_SC_AGE = 20 
 
def detect_range(sym): 
    df = pd.read_csv("data/" + sym + ".csv") 
    df = df.sort_values("date").reset_index(drop=True) 
    if len(df) < LOOKBACK: 
        print(sym + ": not enough data") 
        return 
    w = df.tail(LOOKBACK).reset_index(drop=True) 
    sc_idx = w["low"].idxmin() 
    sc_low = w["low"].iloc[sc_idx] 
    sc_date = w["date"].iloc[sc_idx] 
    sc_age = LOOKBACK - 1 - sc_idx 
    if sc_age < MIN_SC_AGE: 
        print("--- " + sym + " ---") 
        print("SC too recent (" + str(sc_age) + " days). Skip.") 
        return 
    after_sc = w.iloc[sc_idx+1:].reset_index(drop=True) 
    if len(after_sc) < 3: 
        print(sym + ": not enough data after SC") 
        return 
    ar_idx = after_sc["high"].idxmax() 
    ar_high = after_sc["high"].iloc[ar_idx] 
    ar_date = after_sc["date"].iloc[ar_idx] 
    st_candidates = after_sc[after_sc["low"] <= sc_low * 1.03] 
    if len(st_candidates) > 0: 
        st_row = st_candidates.loc[st_candidates["low"].idxmin()] 
        st_date = st_row["date"] 
        st_low = st_row["low"] 
        st_vol = st_row["volume"] 
        sc_vol = w["volume"].iloc[sc_idx] 
        st_ok = st_vol < sc_vol 
    else: 
        st_date = "none" 
        st_low = 0 
        st_vol = 0 
        st_ok = False 
    resistance = ar_high 
    support = sc_low 
    width_pct = 100.0 * (resistance - support) / support 
    near_hi = int((w["high"] >= resistance * (1 - TOUCH_PCT)).sum()) 
    near_lo = int((w["low"] <= support * (1 + TOUCH_PCT)).sum()) 
    is_range = (near_hi >= 2) and (near_lo >= 2) and (width_pct >= 8) 
    print("--- " + sym + " ---") 
    print("SC:  " + str(sc_date) + " low=" + str(round(sc_low,2)) + " age=" + str(sc_age)) 
    print("AR:  " + str(ar_date) + " high=" + str(round(ar_high,2))) 
    print("ST:  " + str(st_date) + " low=" + str(round(st_low,2)) + " vol_ok=" + str(st_ok)) 
    print("Res=" + str(round(resistance,2)) + " (" + str(near_hi) + " touches)  Sup=" + str(round(support,2)) + " (" + str(near_lo) + " touches)") 
    print("Width=" + str(round(width_pct,1)) + " pct  IsRange=" + str(is_range)) 
 
if __name__ == "__main__": 
    for s in sys.argv[1:]: 
        detect_range(s) 
