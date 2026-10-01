import psxdata 
import pandas as pd 
from datetime import date, timedelta 
import os 
 
OUT = "data" 
os.makedirs(OUT, exist_ok=True) 
 
syms = psxdata.indices("KSE100")["symbol"].tolist() 
print("KSE100 count:", len(syms)) 
 
end = date.today() 
start = end - timedelta(days=400) 
 
ok = 0 
fail = 0 
for sym in syms: 
    try: 
        df = psxdata.stocks(sym, start=str(start), end=str(end)) 
        if df is None or len(df) == 0: 
            print(sym + ": EMPTY") 
            fail += 1 
            continue 
        df = df.sort_values("date").reset_index(drop=True) 
        df.to_csv(OUT + "/" + sym + ".csv", index=False) 
        ok += 1 
    except Exception as e: 
        print(sym + ": ERROR " + str(e)) 
        fail += 1 
 
print("DONE ok=" + str(ok) + " fail=" + str(fail)) 
