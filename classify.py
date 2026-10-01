import pandas as pd, os, json 
 
LOOKBACK=60 
MIN_SC_AGE=20 
SPRING_WINDOW=30 
 
def classify(sym): 
    df=pd.read_csv("data/"+sym+".csv").sort_values("date").reset_index(drop=True) 
    if len(df)<LOOKBACK: return None 
    w=df.tail(LOOKBACK).reset_index(drop=True) 
    sc_idx=w["low"].idxmin() 
    sc_low=float(w["low"].iloc[sc_idx]) 
    sc_age=int(LOOKBACK-1-sc_idx) 
    last=w.iloc[-1] 
    last_close=float(last["close"]) 
    if sc_age < MIN_SC_AGE: 
        return dict(symbol=sym,stage="A",action="Wait",entry=None,stop=None,target=None,reason="SC "+str(sc_age)+"d ago, no range yet") 
    after=w.iloc[sc_idx+1:].reset_index(drop=True) 
    res=float(after["high"].max()) 
    sup=sc_low 
    width=res-sup 
    width_pct=100.0*width/sup 
    near_hi=int((w["high"]>=res*0.98).sum()) 
    near_lo=int((w["low"]<=sup*1.02).sum()) 
    avg_vol20=float(w["volume"].tail(20).mean()) 
    recent=w.tail(SPRING_WINDOW).reset_index(drop=True) 
    spring=None 
    for i in range(len(recent)): 
        r=recent.iloc[i] 
        if r["low"]<sup and r["close"]>sup: 
            depth=100.0*(sup-r["low"])/sup 
            vr=float(r["volume"])/avg_vol20 if avg_vol20>0 else 0 
            t="Shakeout" if depth>5 else ("Type3" if vr<=1.0 else "Type2") 
            spring=dict(date=str(r["date"]),low=float(r["low"]),close=float(r["close"]),type=t,depth=round(depth,1),vr=round(vr,2)) 
    sos=None 
    for i in range(len(after)): 
        r=after.iloc[i] 
        if r["close"]>res and r["volume"]>avg_vol20*1.5: 
            sos=dict(date=str(r["date"]),close=float(r["close"]),vr=round(float(r["volume"])/avg_vol20,2)) 
            break 
    target=res+width 
    if spring is not None: 
        stop=spring["low"]*0.98 
        return dict(symbol=sym,stage="C",action="BUY",entry=round(spring["close"],2),stop=round(stop,2),target=round(target,2),reason=spring["type"]+" spring on "+spring["date"]) 
    if sos is not None and last_close>res: 
        return dict(symbol=sym,stage="D",action="BUY-add",entry=round(last_close,2),stop=round(res*0.98,2),target=round(target,2),reason="SOS on "+sos["date"]+" vr="+str(sos["vr"])) 
    if last_close>res*1.2: 
        return dict(symbol=sym,stage="E",action="HOLD-SELL",entry=None,stop=round(res,2),target=None,reason="Trending, over 20 pct above range") 
    if near_hi>=2 and near_lo>=2 and width_pct>=8: 
        entry_lvl=round(sup*1.01,2) 
        stop_lvl=round(sup*0.97,2) 
        return dict(symbol=sym,stage="B",action="Watch",entry=entry_lvl,stop=stop_lvl,target=round(target,2),reason="Range "+str(round(width_pct,1))+"pct. Buy if breaks "+str(round(sup,2))+" and recovers") 
    return dict(symbol=sym,stage="A",action="Wait",entry=None,stop=None,target=None,reason="No clean range") 
 
files=[f[:-4] for f in os.listdir("data") if f.endswith(".csv")] 
out=[] 
for s in files: 
    try: 
        r=classify(s) 
        if r: out.append(r) 
    except Exception as e: 
        print(s,"ERR",e) 
order={"C":0,"D":1,"B":2,"A":3,"E":4} 
out.sort(key=lambda x: order.get(x["stage"],9)) 
json.dump(out, open("signals.json","w"), indent=2) 
for r in out: 
    print(r["stage"], r["symbol"], r["action"], "|", r["reason"]) 
