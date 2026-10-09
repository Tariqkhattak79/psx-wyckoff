import pandas as pd, os, json
from datetime import date, timedelta

MIN_AVG_VALUE = 5000000
VOL_LOOKBACK = 20
ATR_PERIOD = 14
ATR_MULT = 1.5
EMA_PERIOD = 20
GAP_TOL = 0.02
MIN_RR = 1.5
VOL_MULT = 1.0

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def atr(df, period):
    h = df["high"]; l = df["low"]; c = df["close"].shift(1)
    tr = pd.concat([h - l, (h - c).abs(), (l - c).abs()], axis=1).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()

def next_trading_day(d):
    nd = d + timedelta(days=1)
    while nd.weekday() >= 5:
        nd += timedelta(days=1)
    return nd

def fmt(v):
    if v is None: return "—"
    try:
        f = float(v)
        if f >= 1e6: return f"{f/1e6:.1f}M"
        if f >= 1e3: return f"{f/1e3:.0f}K"
        return f"{f:.2f}"
    except:
        return str(v)

def analyze(sym):
    path = "data/" + sym + ".csv"
    if not os.path.exists(path): return None
    df = pd.read_csv(path).sort_values("date").reset_index(drop=True)
    if len(df) < 50: return None
    _w = df.tail(VOL_LOOKBACK)
    avg_val = float((_w["volume"] * _w["close"]).mean())
    if avg_val < MIN_AVG_VALUE: return None
    df["ema20"] = ema(df["close"], EMA_PERIOD)
    df["atr14"] = atr(df, ATR_PERIOD)
    avg_vol20 = float(df["volume"].tail(VOL_LOOKBACK).mean())

    d1 = df.iloc[-1]
    d2 = df.iloc[-2]
    d1_h, d1_l, d1_c = float(d1["high"]), float(d1["low"]), float(d1["close"])
    d2_h, d2_l = float(d2["high"]), float(d2["low"])
    d1_open = float(d1["open"])
    d1_vol = float(d1["volume"])
    d2_vol = float(d2["volume"])
    last_close = float(d1["close"])
    ema20_val = float(d1["ema20"])
    atr_val = float(d1["atr14"])
    d1_date = str(d1["date"])[:10]
    d2_date = str(d2["date"])[:10]
    pair = "Wed to Thu"
    try:
        dt = pd.to_datetime(d1["date"]).date()
        buy_on = str(next_trading_day(dt))
    except:
        buy_on = "next trading day"

    bullish = (d2_h > d1_h) and (d1_l > d2_l)
    bearish = (d2_h < d1_h) and (d1_l < d2_l)

    if not (bullish or bearish):
        return None

    if bullish:
        entry = d1_l
        stop = round(entry * 0.98, 2)
        target = d2_h
        risk = entry - stop
        reward = target - entry
        rr = round(reward / risk, 2) if risk > 0 else 0
        trend_ok = last_close > ema20_val
        vol_ok = d1_vol < avg_vol20 * VOL_MULT
        gap_pct = abs(d1_open - d2_l) / d2_l if d2_l else 0
        gap_ok = gap_pct <= GAP_TOL
        passes = sum([trend_ok, vol_ok, gap_ok])
        if passes == 3:
            quality = "A"
        elif trend_ok and passes >= 2:
            quality = "B"
        else:
            quality = "C"
        if rr < MIN_RR: return None
        rsn = "Bullish "+pair+". "+quality+"-grade. Entry "+str(round(entry,2))+" (D1 low). Stop "+str(stop)+" (ATR). Target "+str(round(target,2))+" (D2 high). RR "+str(rr)+". "+\
            ("Trend OK. " if trend_ok else "Trend down. ")+("Vol quiet. " if vol_ok else "Vol high. ")+("Gap OK." if gap_ok else "Gap wide.")
        return dict(symbol=sym, direction="bullish", pair=pair, last_close=round(last_close,2),
            entry=round(entry,2), stop=stop, target=round(target,2), rr=rr,
            d1_date=d1_date, d1_high=round(d1_h,2), d1_low=round(d1_l,2),
            d2_date=d2_date, d2_high=round(d2_h,2), d2_low=round(d2_l,2),
            avg_volume=round(avg_vol20), avg_value_pkr=round(avg_val),
            atr14=round(atr_val,2), ema20=round(ema20_val,2),
            trend_ok=bool(trend_ok), vol_ok=bool(vol_ok), gap_ok=bool(gap_ok),
            quality=quality, buy_on=buy_on, reason=rsn)

    entry = d1_l
    stop = round(entry * 1.02, 2)
    target = round(entry - (d2_h - d1_l), 2)
    risk = stop - entry
    reward = entry - target
    rr = round(reward / risk, 2) if risk > 0 else 0
    trend_ok = last_close < ema20_val
    vol_ok = d2_vol < avg_vol20 * VOL_MULT
    gap_pct = abs(d1_open - d2_l) / d2_l if d2_l else 0
    gap_ok = gap_pct <= GAP_TOL
    passes = sum([trend_ok, vol_ok, gap_ok])
    if passes == 3:
        quality = "A"
    elif trend_ok and passes >= 2:
        quality = "B"
    else:
        quality = "C"
    if rr < MIN_RR: return None
    rsn = "Bearish "+pair+". "+quality+"-grade. Breakdown "+str(round(entry,2))+". Stop "+str(stop)+" (ATR). Target "+str(target)+". RR "+str(rr)+". "+\
        ("Trend OK. " if trend_ok else "Trend up. ")+("Vol quiet. " if vol_ok else "Vol high. ")+("Gap OK." if gap_ok else "Gap wide.")
    return dict(symbol=sym, direction="bearish", pair=pair, last_close=round(last_close,2),
        entry=round(entry,2), stop=stop, target=target, rr=rr,
        d1_date=d1_date, d1_high=round(d1_h,2), d1_low=round(d1_l,2),
        d2_date=d2_date, d2_high=round(d2_h,2), d2_low=round(d2_l,2),
        avg_volume=round(avg_vol20), avg_value_pkr=round(avg_val),
        atr14=round(atr_val,2), ema20=round(ema20_val,2),
        trend_ok=bool(trend_ok), vol_ok=bool(vol_ok), gap_ok=bool(gap_ok),
        quality=quality, buy_on=buy_on, reason=rsn)

files = [f[:-4] for f in os.listdir("data") if f.endswith(".csv")]
out = []
for s in files:
    try:
        r = analyze(s)
        if r: out.append(r)
    except Exception as e:
        print(s, "ERR", e)

q_order = {"A": 0, "B": 1, "C": 2}
out.sort(key=lambda x: (q_order.get(x.get("quality", "C"), 3), -x.get("rr", 0)))

json.dump(out, open("daytrade.json", "w"), indent=2)

bulls = [r for r in out if r["direction"] == "bullish"]
bears = [r for r in out if r["direction"] == "bearish"]
print("DONE bullish=" + str(len(bulls)) + " bearish=" + str(len(bears)) + " total=" + str(len(out)))
for r in out:
    print(r["quality"], r["direction"].upper(), r["symbol"], "RR=" + str(r["rr"]), "entry=" + str(r["entry"]),
          "atr=" + str(r["atr14"]), "trend=" + ("Y" if r["trend_ok"] else "N"),
          "vol=" + ("Y" if r["vol_ok"] else "N"), "gap=" + ("Y" if r["gap_ok"] else "N"))
