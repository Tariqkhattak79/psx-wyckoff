import pandas as pd
import json
from classify import classify, order, quality_rank

# The specific stocks you want
force_syms = ['PPL', 'OGDC', 'PSO', 'HTL', 'SHFA', 'DOL']
out = []

print("Force-classifying specific stocks...")
for sym in force_syms:
    try:
        r = classify(sym)
        if r:
            out.append(r)
            print(f"✅ {sym}: Stage {r['stage']} - {r['reason'][:50]}...")
        else:
            print(f"❌ {sym}: Not enough data or failed volume check.")
    except Exception as e:
        print(f"❌ {sym}: Error - {e}")

# Sort and save
out.sort(key=lambda x: (order.get(x["stage"],9), quality_rank(x)))
json.dump(out, open("signals.json","w"), indent=2)
print("Saved to signals.json")
