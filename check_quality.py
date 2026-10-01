import pandas as pd 
import os 
D = "data" 
files = [f for f in os.listdir(D) if f.endswith(".csv")] 
print("Files:", len(files)) 
bad = [] 
for f in files: 
    df = pd.read_csv(os.path.join(D, f)) 
    n = len(df) 
    if n == 0: 
        bad.append((f, "empty")) 
        continue 
    zeros = int((df["volume"] == 0).sum()) 
    anom = int(df["is_anomaly"].sum()) if "is_anomaly" in df.columns else 0 
    pct = 100.0 * (zeros + anom) / n 
    if pct > 10: 
        bad.append((f, str(round(pct,1)) + " pct bad")) 
print("BAD over 10 pct:", len(bad)) 
for b in bad: print(b) 
