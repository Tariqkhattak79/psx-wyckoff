import pandas as pd, os, json
from datetime import datetime

LOOKBACK=120
SPRING_WINDOW=30
MIN_SC_AGE=5
MIN_SPRING_GAP=5
SPRING_TOL=0.02
MIN_AVG_VALUE=5000000
FRESH_DAYS=5
AGED_DAYS=20
LATE_PCT=5.0
CLASSIC_SC_DAYS=10
CLASSIC_SPRING_GAP=10
EMA_TREND=200

def trading_days_between(d1_str, d2_str):
    try:
        d1 = datetime.strptime(d1_str, "%Y-%m-%d")
        d2 = datetime.strptime(d2_str, "%Y-%m-%d")
        return int((d2 - d1).days)
    except:
        return 0

def classify(sym):
    df=pd.read_csv("data/"+sym+".csv").sort_values("date").reset_index(drop=True)
    if len(df)<max(LOOKBACK,EMA_TREND): return None
    df["ema200"]=df["close"].ewm(span=EMA_TREND, adjust=False).mean()
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
    last_ema200=float(w["ema200"].iloc[-1])
    trend_ok=last_close>last_ema200

    base=dict(symbol=sym,last_close=round(last_close,2),prev_close=round(prev_close,2),change_pct=change_pct,
        sc_date=sc_date,sc_age=sc_age,sc_price=round(sc_low,2),avg_volume=round(_avgvol),avg_value_pkr=round(_avgval),
        ema200=round(last_ema200,2),trend_ok=bool(trend_ok),
        spring_date=None,spring_low=None,spring_close=None,spring_type=None,post_spring_low=None,
        test_ok=None,test_date=None,status=None,days_since_spring=None,
        entry_aggressive=None,entry_balanced=None,entry_conservative=None,entry_gap_pct=None,
        entry_aggressive_lo=None,entry_aggressive_hi=None,entry_balanced_lo=None,entry_balanced_hi=None,entry_conservative_lo=None,entry_conservative_hi=None,
        range_low=round(sc_low,2),range_high=None,range_pct=None)

    if sc_age < MIN_SC_AGE:
        hi=round(w["high"].tail(30).max(),2)
        base["range_high"]=hi
        rsn="Climax "+str(sc_age)+"d ago @ "+str(round(sc_low,2))+". Range still forming."
        return {**base,"stage":"A","action":"Wait","entry":None,"stop":None,"target":None,"reason":rsn}

    after=w.iloc[sc_idx+1:].reset_index(drop=True)
    res=float(after["high"].max())
    sup=float(after["low"].min()) if len(after) else sc_low
    width=res-sup
    if width<=0: width=res*0.05
    width_pct=round(100.0*width/sup, 1) if sup>0 else 0
    near_hi=int((w["high"]>=res*0.98).sum())
    near_lo=int((w["low"]<=sup*1.02).sum())
    avg_vol20=float(w["volume"].tail(20).mean())
    avg_vol_range=float(after["volume"].mean()) if len(after) else avg_vol20
    recent=w.tail(SPRING_WINDOW).reset_index(drop=True)

    base["range_low"]=round(sup,2)
    base["range_high"]=round(res,2)
    base["range_pct"]=width_pct

    spring=None
    spring_idx=None
    spring_days_after_sc=0
    for i in range(len(recent)):
        r=recent.iloc[i]
        days_after_sc = (LOOKBACK - SPRING_WINDOW) + i - sc_idx
        if days_after_sc < MIN_SPRING_GAP: continue
        if r["low"]<=sup*(1+SPRING_TOL) and r["close"]>sup:
            depth=100.0*(sup-r["low"])/sup
            vr=float(r["volume"])/avg_vol20 if avg_vol20>0 else 0
            t="Type1" if depth>5 else ("Type2" if vr>1.0 else "Type3")
            spring=dict(date=str(r["date"]),low=float(r["low"]),close=float(r["close"]),high=float(r["high"]),type=t,depth=round(depth,1),vr=round(vr,2))
            spring_idx=i
            spring_days_after_sc=days_after_sc

    sos=None
    for i in range(len(after)):
        r=after.iloc[i]
        if r["close"]>res and r["volume"]>avg_vol20*1.5:
            sos=dict(date=str(r["date"]),close=float(r["close"]),vr=round(float(r["volume"])/avg_vol20,2))
            break

    target=round(res+width,2)

    if spring is not None and spring["type"] in ("Type1","Type2"):
        stop=round(spring["low"]*0.98,2)
        spring_date=spring["date"]
        days_since=trading_days_between(spring_date, str(last["date"]))
        post=recent.iloc[spring_idx+1:]
        if len(post)>0:
            post_low=float(post["low"].min())
        else:
            post_low=spring["low"]
        test_row=None
        for _, t in post.iterrows():
            near_low=abs(float(t["low"])-spring["low"])/spring["low"]<0.02 if spring["low"]>0 else False
            lower_vol=float(t["volume"])<float(spring["vr"]*avg_vol20)
            holds=float(t["close"])>sup
            if near_low and lower_vol and holds:
                test_row=t
                break
        test_ok=test_row is not None
        test_date=str(test_row["date"]) if test_ok else None
        if post_low < spring["low"]*0.995:
            status="FAILED"
        elif days_since<=FRESH_DAYS:
            status="FRESH"
        else:
            status="VALID"
        entry_aggressive=round(spring["close"],2)
        entry_balanced=round((spring["close"]+sup)/2,2)
        entry_conservative=round(res,2)
        entry_aggressive_lo=round(spring["low"],2)
        entry_aggressive_hi=round(spring["high"],2)
        entry_balanced_lo=round(sup,2)
        entry_balanced_hi=round(spring["low"],2)
        entry_conservative_lo=round(res*0.99,2)
        entry_conservative_hi=round(res*1.01,2)
        gap_pct=round(100.0*(last_close-entry_aggressive)/entry_aggressive,2)
        if gap_pct>LATE_PCT:
            status="LATE"
        if status=="FAILED" or (days_since>AGED_DAYS and gap_pct>LATE_PCT):
            return {**base,"stage":"E","action":"EXPIRED","entry":None,"stop":None,"target":None,
                "spring_date":spring_date,"spring_low":round(spring["low"],2),"spring_close":round(spring["close"],2),"spring_type":spring["type"],
                "status":status,"days_since_spring":days_since,"entry_gap_pct":gap_pct,"test_ok":test_ok,"test_date":test_date,
                "reason":spring["type"]+" spring on "+spring_date+" — "+status+" ("+str(days_since)+"d, "+str(gap_pct)+"% above entry). No longer actionable."}
        is_classic = (sc_age >= CLASSIC_SC_DAYS and spring_days_after_sc >= CLASSIC_SPRING_GAP and status!="LATE")
        final_stage = "C2" if is_classic else "C1"
        rsn=spring["type"]+" spring on "+spring_date+" ("+status+", "+str(days_since)+"d). FULL "+str(entry_aggressive_lo)+"-"+str(entry_aggressive_hi)+" / HALF "+str(entry_balanced_lo)+"-"+str(entry_balanced_hi)+" / QUARTER "+str(entry_conservative_lo)+"-"+str(entry_conservative_hi)+". Stop "+str(stop)+". Target "+str(target)+". Current "+str(round(last_close,2))+" ("+str(gap_pct)+"% vs agg)."
        return {**base,"stage":final_stage,"action":"BUY","entry":entry_aggressive,
            "entry_aggressive":entry_aggressive,"entry_balanced":entry_balanced,"entry_conservative":entry_conservative,
            "entry_aggressive_lo":entry_aggressive_lo,"entry_aggressive_hi":entry_aggressive_hi,
            "entry_balanced_lo":entry_balanced_lo,"entry_balanced_hi":entry_balanced_hi,
            "entry_conservative_lo":entry_conservative_lo,"entry_conservative_hi":entry_conservative_hi,
            "stop":stop,"target":target,"spring_date":spring_date,"spring_low":round(spring["low"],2),"spring_close":round(spring["close"],2),
            "spring_type":spring["type"],"post_spring_low":round(post_low,2),"status":status,"days_since_spring":days_since,
            "test_ok":test_ok,"test_date":test_date,"entry_gap_pct":gap_pct,"reason":rsn}

    if sos is not None and last_close>res:
        stop=round(res*0.98,2)
        rsn="SOS breakout on "+sos["date"]+" (vol "+str(sos["vr"])+"x). BUY-add at "+str(round(last_close,2))+". Stop "+str(stop)+". Target "+str(target)+"."
        return {**base,"stage":"D","action":"BUY-add","entry":round(last_close,2),"stop":stop,"target":target,"reason":rsn}

    if last_close>res*1.2:
        rsn="Trending >20pct above range. HOLD if held."
        return {**base,"stage":"E","action":"HOLD-SELL","entry":None,"stop":round(res,2),"target":target,"reason":rsn}

    if near_hi>=2 and near_lo>=2 and 8<=width_pct<=35:
        lo=round(sup*1.01,2)
        st=round(sup*0.97,2)
        rsn="Range "+str(width_pct)+"pct ("+str(round(sup,2))+" to "+str(round(res,2))+"). Wait for dip to "+str(round(sup,2))+" then recovery -> BUY near "+str(lo)+". Stop "+str(st)+". Target "+str(target)+"."
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

order={"C2":0,"C1":1,"D":2,"B":3,"A":4,"E":5}
def quality_rank(x):
    t = 1 if x.get("trend_ok") else 0
    s = 1 if x.get("test_ok") else 0
    f = 1 if x.get("status")=="FRESH" else 0
    return -(t*100 + s*10 + f)
out.sort(key=lambda x: (order.get(x["stage"],9), quality_rank(x)))
json.dump(out, open("signals.json","w"), indent=2)
for r in out:
    print(r["stage"], r["symbol"], r["action"], "| TREND="+("Y" if r.get("trend_ok") else "N"), "TEST="+("Y" if r.get("test_ok") else ("N" if r.get("test_ok") is False else "-")), "|", r["reason"])
