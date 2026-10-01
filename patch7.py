src = open("classify.py").read()

# Add MIN_AVG_VALUE constant
src = src.replace(
    'SPRING_WINDOW=30',
    'SPRING_WINDOW=30\nMIN_AVG_VALUE=5000000'
)

# Add liquidity filter right after "if len(df)<LOOKBACK: return None"
src = src.replace(
    'if len(df)<LOOKBACK: return None',
    '''if len(df)<LOOKBACK: return None
    _w=df.tail(20)
    _avgval=float((_w["volume"]*_w["close"]).mean())
    if _avgval < MIN_AVG_VALUE: return None
    _avgvol=float(_w["volume"].mean())'''
)

# Add avg_volume/avg_value into base dict
src = src.replace(
    'base=dict(symbol=sym,last_close=round(last_close,2),prev_close=round(prev_close,2),change_pct=change_pct,sc_date=sc_date,sc_age=sc_age,sc_price=round(sc_low,2))',
    'base=dict(symbol=sym,last_close=round(last_close,2),prev_close=round(prev_close,2),change_pct=change_pct,sc_date=sc_date,sc_age=sc_age,sc_price=round(sc_low,2),avg_volume=round(_avgvol),avg_value_pkr=round(_avgval))'
)

open("classify.py","w").write(src)
print("patched")
