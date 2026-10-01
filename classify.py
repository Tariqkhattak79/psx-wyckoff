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
    prev_close=float(w["close"].iloc[-2]) if len(w)>1 else last_close
    change_pct=round(100.0*(last_close-prev_close)/prev_close, 2) if prev_close else 0

    if sc_age < MIN_SC_AGE:
        lo=round(sc_low*1.01,2)
        st=round(sc_low*0.97,2)
        hi=round(w["high"].tail(30).max(),2)
        rsn="Climax "+str(sc_age)+"d ago. If price drops to "+str(round(sc_low,2))+" (support) and closes back above, BUY near "+str(lo)+". Stop "+str(st)+". Target "+str(hi)+"."
        return dict(symbol=sym,stage="A",action="Wait",last_close=round(last_close,2),prev_close=round(prev_close,2),change_pct=change_pct,entry=lo,stop=st,target=hi,reason=rsn)

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

    target=round(res+width,2)

    if spring is not None:
        stop=round(spring["low"]*0.98,2)
        rsn=spring["type"]+" spring on "+spring["date"]+". BUY now at "+str(round(spring["close"],2))+". Stop "+str(stop)+". Target "+str(target)+". Lowest-risk entry."
        return dict(symbol=sym,stage="C",action="BUY",last_close=round(last_close,2),prev_close=round(prev_close,2),change_pct=change_pct,entry=round(spring["close"],2),stop=stop,target=target,reason=rsn)

    if sos is not None and last_close>res:
        stop=round(res*0.98,2)
        rsn="SOS breakout on "+sos["date"]+" (vol "+str(sos["vr"])+"x). BUY-add at "+str(round(last_close,2))+". Stop "+str(stop)+". Target "+str(target)+"."
        return dict(symbol=sym,stage="D",action="BUY-add",last_close=round(last_close,2),prev_close=round(prev_close,2),change_pct=change_pct,entry=round(last_close,2),stop=stop,target=target,reason=rsn)

    if last_close>res*1.2:
        rsn="Trending >20pct above range. HOLD if held. Sell at target "+str(target)+" or on upthrust/volume spike with no progress."
        return dict(symbol=sym,stage="E",action="HOLD-SELL",last_close=round(last_close,2),prev_close=round(prev_close,2),change_pct=change_pct,entry=None,stop=round(res,2),target=target,reason=rsn)

    if near_hi>=2 and near_lo>=2 and width_pct>=8:
        lo=round(sup*1.01,2)
        st=round(sup*0.97,2)
        rsn="Range "+str(round(width_pct,1))+"pct ("+str(round(sup,2))+" to "+str(round(res,2))+"). Wait for dip to "+str(round(sup,2))+" then recovery -> BUY near "+str(lo)+". Stop "+str(st)+". Target "+str(target)+". Or if breaks up over "+str(round(res,2))+" on volume -> BUY-add."
        return dict(symbol=sym,stage="B",action="Watch",last_close=round(last_close,2),prev_close=round(prev_close,2),change_pct=change_pct,entry=lo,stop=st,target=target,reason=rsn)

    return dict(symbol=sym,stage="A",action="Wait",last_close=round(last_close,2),prev_close=round(prev_close,2),change_pct=change_pct,entry=None,stop=None,target=None,reason="No clean range. Monitor for support/resistance.")

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

