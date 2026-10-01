import re
src = open("classify.py").read()

# Extract sc_date, sc_price at SC detection point
src = src.replace(
    'sc_low=float(w["low"].iloc[sc_idx])\n    sc_age=int(LOOKBACK-1-sc_idx)',
    'sc_low=float(w["low"].iloc[sc_idx])\n    sc_date=str(w["date"].iloc[sc_idx])\n    sc_age=int(LOOKBACK-1-sc_idx)'
)

# After after=... line, capture res/sup/width_pct
src = src.replace(
    'width_pct=100.0*width/sup',
    'width_pct=100.0*width/sup\n    sc_extra="sc_date=sc_date,sc_age=sc_age,sc_price=round(sc_low,2),range_low=round(sup,2),range_high=round(res,2),range_pct=round(width_pct,1),"'
)

# Inject the extra into every return dict (via stage marker)
src = re.sub(
    r'return dict\(symbol=sym,stage="([A-Z])",action=("(?:[^"\\]|\\.)*"),',
    lambda m: 'return dict(symbol=sym,stage="'+m.group(1)+'",action='+m.group(2)+','
              + ('' if False else 'sc_date=sc_date,sc_age=sc_age,sc_price=round(sc_low,2),range_low=round(sup,2),range_high=round(res,2),range_pct=round(width_pct,1),'),
    src
)

open("classify.py","w").write(src)
print("patched")
