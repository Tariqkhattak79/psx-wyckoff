import pandas as pd, os 
LOOKBACK=60 
files=[f[:-4] for f in os.listdir("data") if f.endswith(".csv")] 
below=0 
close_back=0 
for sym in files: 
    df=pd.read_csv("data/"+sym+".csv").sort_values("date").reset_index(drop=True) 
    if len(df)<LOOKBACK: continue 
    w=df.tail(LOOKBACK).reset_index(drop=True) 
    sc_idx=w["low"].idxmin() 
    sc_low=w["low"].iloc[sc_idx] 
    if LOOKBACK-1-sc_idx < 20: continue 
    rec=w.tail(15) 
    for _,r in rec.iterrows(): 
        if r["low"] < sc_low: 
            below += 1 
            if r["close"] > sc_low: 
                close_back += 1 
                print(sym, r["date"], "low", round(r["low"],2), "sc", round(sc_low,2), "close", round(r["close"],2)) 
print("Below SC:", below, "Closed back:", close_back) 
