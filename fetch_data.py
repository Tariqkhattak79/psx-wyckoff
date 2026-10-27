import pypsx_toolkit as pt
import pandas as pd
import os

OUT = "data"
os.makedirs(OUT, exist_ok=True)

# Read strictly from your symbols.txt file
if not os.path.exists("symbols.txt"):
    print("ERROR: symbols.txt not found!")
    exit()

with open("symbols.txt", "r") as f:
    syms = [line.strip() for line in f if line.strip()]

print("Total count from symbols.txt:", len(syms))

ok = 0
fail = 0
for i, sym in enumerate(syms):
    try:
        # Download last 400 days of data
        df = pt.download(sym, period="400d")
        
        if df is None or df.empty:
            fail += 1
            continue
            
        # Flatten multi-index columns if necessary
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
        
        # Ensure standard column names
        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]
        
        # Save to CSV
        df.to_csv(OUT + "/" + sym + ".csv", index=False)
        ok += 1
    except Exception as e:
        print(sym + ": ERROR " + str(e))
        fail += 1

print("DONE ok=" + str(ok) + " fail=" + str(fail))
