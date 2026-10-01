import pandas as pd, os, json
from datetime import datetime, timedelta

MIN_RR = 1.5
STOP_PCT = 0.98
MIN_AVG_VALUE = 5_000_000  # PKR per day

def next_trading_day(d):
    # naive: next weekday (Mon-Fri). Doesn't account for PSX holidays.
    dt = datetime.strptime(d, "%Y-%m-%d") + timedelta(days=1)
    while dt.weekday() >= 5:
        dt += timedelta(days=1)
    return dt.strftime("%Y-%m-%d")

def analyze(sym):
    df = pd.read_csv("data/"+sym+".csv").sort_values("date").reset_index(drop=True)
    if len(df) < 25: return None
    w = df.tail(20)
    avg_vol = float(w["volume"].mean())
    avg_val = float((w["volume"] * w["close"]).mean())
    if avg_val < MIN_AVG_VALUE:
        return None

    d1 = df.iloc[-1]
    d2 = df.iloc[-2]
    d1_date = str(d1["date"])[:10]
    d2_date = str(d2["date"])[:10]
    d1_h, d1_l, d1_c = float(d1["high"]), float(d1["low"]), float(d1["close"])
    d2_h, d2_l = float(d2["high"]), float(d2["low"])
    last_close = d1_c

    weekday_map = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    try:
        d2_wd = weekday_map[datetime.strptime(d2_date, "%Y-%m-%d").weekday()]
        d1_wd = weekday_map[datetime.strptime(d1_date, "%Y-%m-%d").weekday()]
    except:
        d2_wd, d1_wd = "?", "?"
    pair = d2_wd + " to " + d1_wd
    buy_on = next_trading_day(d1_date)

    common = dict(symbol=sym, pair=pair, buy_on=buy_on,
                  last_close=round(last_close,2),
                  avg_volume=round(avg_vol),
                  avg_value_pkr=round(avg_val),
                  d1_date=d1_date, d1_high=round(d1_h,2), d1_low=round(d1_l,2),
                  d2_date=d2_date, d2_high=round(d2_h,2), d2_low=round(d2_l,2))

    bullish = (d2_h > d1_h) and (d1_l > d2_l)
    bearish = (d2_h < d1_h) and (d1_l < d2_l)

    if bullish:
        entry = round(d1_l, 2)
        stop = round(d1_l * STOP_PCT, 2)
        target = round(d2_h, 2)
        risk = entry - stop
        reward = target - entry
        if risk <= 0: return None
        rr = round(reward / risk, 2)
        if rr < MIN_RR: return None
        rsn = "Bullish "+pair+". Buy on "+buy_on+" at "+str(entry)+" ("+d1_date+" low). Stop "+str(stop)+". Target "+str(target)+" ("+d2_date+" high). RR "+str(rr)+"."
        return {**common, "direction":"bullish","entry":entry,"stop":stop,"target":target,"rr":rr,"reason":rsn}

    if bearish:
        entry = round(d1_h, 2)
        stop = round(d1_h * 1.02, 2)
        target = round(d2_l, 2)
        risk = stop - entry
        reward = entry - target
        if risk <= 0: return None
        rr = round(reward / risk, 2)
        if rr < MIN_RR: return None
        rsn = "Bearish "+pair+". Exit longs on "+buy_on+". Stop "+str(stop)+". Target "+str(target)+". RR "+str(rr)+"."
        return {**common, "direction":"bearish","entry":entry,"stop":stop,"target":target,"rr":rr,"reason":rsn}

    return None

files = [f[:-4] for f in os.listdir("data") if f.endswith(".csv")]
out = []
for s in files:
    try:
        r = analyze(s)
        if r: out.append(r)
    except Exception as e:
        print(s, "ERR", e)

out.sort(key=lambda x: (0 if x["direction"]=="bullish" else 1, -x["rr"]))
json.dump(out, open("daytrade.json","w"), indent=2)
bull = [x for x in out if x["direction"]=="bullish"]
bear = [x for x in out if x["direction"]=="bearish"]
print("DONE bullish="+str(len(bull))+" bearish="+str(len(bear))+" total="+str(len(out)))
for r in out[:15]:
    print(r["direction"][:4].upper(), r["symbol"], r["pair"], "BUY_ON="+r["buy_on"], "RR="+str(r["rr"]), "entry="+str(r["entry"]), "avgVal="+str(round(r["avg_value_pkr"]/1e6,1))+"M")
