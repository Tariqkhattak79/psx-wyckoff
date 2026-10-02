import pandas as pd, os, json

LOOKBACK=60
MIN_SC_AGE=20
SPRING_WINDOW=30
MIN_AVG_VALUE=5000000

def classify(sym):
    df=pd.read_csv("data/"+sym+".csv").sort_values("date").reset_index(drop=True)
    if len(df)<LOOKBACK: return None
    _w=df.tail(20)
    _avgval=float((_w["volume"]*_w["close"]).mean())
    if _avgval < MIN_AVG_VALUE: return None
    _avgvol=float(_w["volume"].mean())
    w=df.tail(LOOKBACK).reset_index(drop=True)
    sc_idx=w["low"].idxmin()
    sc_low=float(w["low"].iloc[sc_idx])
    sc_date=str(w["date"].iloc[sc_idx])
    sc_age=int(LOOKBACK-1-sc_idx)
    last=w.iloc[-1]
    last_close=float(last["close"])
    prev_close=float(w["close"].iloc[-2]) if len(w)>1 else last_close
    change_pct=round(100.0*(last_close-prev_close)/prev_close, 2) if prev_close else 0

    base=dict(symbol=sym,last_close=round(last_close,2),prev_close=round(prev_close,2),change_pct=change_pct,sc_date=sc_date,sc_age=sc_age,sc_price=round(sc_low,2),avg_volume=round(_avgvol),avg_value_pkr=round(_avgval))

    if sc_age < MIN_SC_AGE:
        lo=round(sc_low*1.01,2)
        st=round(sc_low*0.97,2)
        recent_es=w.tail(5).reset_index(drop=True)
        for i in range(len(recent_es)):
            r=recent_es.iloc[i]
            if r["low"]<=sc_low*1.005 and r["close"]>sc_low:
                st_es=round(float(r["low"])*0.98,2)
                tgt_es=round(w["high"].tail(30).max(),2)
                rsn="EARLY spring on "+str(r["date"])+" (low "+str(round(float(r["low"]),2))+" vs SC "+str(round(sc_low,2))+"). BUY near "+str(round(float(r["close"]),2))+". Stop "+str(st_es)+". Target "+str(tgt_es)+"."
                return {**base,"stage":"C","action":"BUY","entry":round(float(r["close"]),2),"stop":st_es,"target":tgt_es,"range_low":round(sc_low,2),"range_high":round(w["high"].tail(30).max(),2),"range_pct":None,"reason":rsn}
        hi=round(w["high"].tail(30).max(),2)
        if hi > lo * 1.5:
            hi = None
            rsn="Climax "+str(sc_age)+"d ago @ "+str(round(sc_low,2))+". If price drops to "+str(round(sc_low,2))+" and closes back above, BUY near "+str(lo)+". Stop "+str(st)+". Target not reliable (range too wide)."
        else:
            rsn="Climax "+str(sc_age)+"d ago @ "+str(round(sc_low,2))+". If price drops to "+str(round(sc_low,2))+" and closes back above, BUY near "+str(lo)+". Stop "+str(st)+". Target "+str(hi)+"."
        return {**base, "stage":"A","action":"Wait","entry":lo,"stop":st,"target":hi,"range_low":round(sc_low,2),"range_high":hi if hi else round(w["high"].tail(30).max(),2),"range_pct":None,"reason":rsn}

    after=w.iloc[sc_idx+1:].reset_index(drop=True)
    res=float(after["high"].max())
    sup=sc_low
    width=res-sup
    width_pct=round(100.0*width/sup, 1)
    near_hi=int((w["high"]>=res*0.98).sum())
    near_lo=int((w["low"]<=sup*1.02).sum())
    avg_vol20=float(w["volume"].tail(20).mean())
    recent=w.tail(SPRING_WINDOW).reset_index(drop=True)

    base["range_low"]=round(sup,2)
    base["range_high"]=round(res,2)
    base["range_pct"]=width_pct

    spring=None
    for i in range(len(recent)):
        r=recent.iloc[i]
        if r["low"]<sup*1.005 and r["close"]>sup:
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
        return {**base,"stage":"C","action":"BUY","entry":round(spring["close"],2),"stop":stop,"target":target,"reason":rsn}

    if sos is not None and last_close>res:
        stop=round(res*0.98,2)
        rsn="SOS breakout on "+sos["date"]+" (vol "+str(sos["vr"])+"x). BUY-add at "+str(round(last_close,2))+". Stop "+str(stop)+". Target "+str(target)+"."
        return {**base,"stage":"D","action":"BUY-add","entry":round(last_close,2),"stop":stop,"target":target,"reason":rsn}

    if last_close>res*1.2:
        rsn="Trending >20pct above range. HOLD if held. Sell at target "+str(target)+" or on upthrust/volume spike with no progress."
        return {**base,"stage":"E","action":"HOLD-SELL","entry":None,"stop":round(res,2),"target":target,"reason":rsn}

    if near_hi>=2 and near_lo>=2 and 8<=width_pct<=35:
        lo=round(sup*1.01,2)
        st=round(sup*0.97,2)
        rsn="Range "+str(width_pct)+"pct ("+str(round(sup,2))+" to "+str(round(res,2))+"). Wait for dip to "+str(round(sup,2))+" then recovery -> BUY near "+str(lo)+". Stop "+str(st)+". Target "+str(target)+". Or if breaks up over "+str(round(res,2))+" on volume -> BUY-add."
        return {**base,"stage":"B","action":"Watch","entry":lo,"stop":st,"target":target,"reason":rsn}

    return {**base,"stage":"A","action":"Wait","entry":None,"stop":None,"target":None,"reason":"No clean range. Monitor for support/resistance."}

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
