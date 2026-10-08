import os, json
from datetime import date

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

import resend

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
EMAIL_TO = os.environ.get("EMAIL_TO", "")
FROM_ADDR = os.environ.get("FROM_ADDR", "PSX Signals <onboarding@resend.dev>")

def fmt(v):
    if v is None: return "—"
    try:
        f = float(v)
        if f >= 1e6: return f"{f/1e6:.1f}M"
        if f >= 1e3: return f"{f/1e3:.0f}K"
        return f"{f:.2f}"
    except:
        return str(v)

def esc(s):
    if s is None: return ""
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def status_color(st):
    if st == "FRESH": return "#e3b341"
    if st == "VALID": return "#3fb950"
    if st == "LATE": return "#f0883e"
    if st == "FAILED": return "#f85149"
    return "#7d8590"

def type_color(t):
    if t == "Type1": return "#d4af37"
    if t == "Type2": return "#c0c0c0"
    if t == "Type3": return "#cd7f32"
    return "#7d8590"

def c2_table(rows):
    if not rows: return "<p style='color:#8b949e'>No signals.</p>"
    h = "<table cellpadding='6' cellspacing='0' style='border-collapse:collapse;font-family:Arial,sans-serif;font-size:12px;width:100%'>"
    h += "<tr style='background:#161b22;color:#c9d1d9'>"
    for col in ["Symbol","Price","FULL","HALF","QUARTER","Stop","Target","Status","Type","Spring"]:
        h += f"<th style='border:1px solid #30363d;padding:6px;text-align:left'>{col}</th>"
    h += "</tr>"
    for r in rows:
        gap = r.get("entry_gap_pct")
        gap_s = f"{gap:+.1f}%" if gap is not None else ""
        st = r.get("status","")
        tp = r.get("spring_type","")
        h += "<tr>"
        h += f"<td style='border:1px solid #30363d;padding:6px;font-weight:bold'>{esc(r.get('symbol'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px'>{fmt(r.get('last_close'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px;color:#3fb950;font-weight:bold'>{fmt(r.get('entry_aggressive'))} <span style='color:#8b949e;font-size:10px'>{gap_s}</span></td>"
        h += f"<td style='border:1px solid #30363d;padding:6px;color:#e3b341'>{fmt(r.get('entry_balanced'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px;color:#58a6ff'>{fmt(r.get('entry_conservative'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px'>{fmt(r.get('stop'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px'>{fmt(r.get('target'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px;color:{status_color(st)};font-weight:bold'>{esc(st)} — {r.get('days_since_spring','')}d</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px;color:{type_color(tp)};font-weight:bold'>{esc(tp)}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px'>{esc(r.get('spring_date'))}</td>"
        h += "</tr>"
    h += "</table>"
    return h

def c1_table(rows):
    if not rows: return "<p style='color:#8b949e'>No signals.</p>"
    h = "<table cellpadding='6' cellspacing='0' style='border-collapse:collapse;font-family:Arial,sans-serif;font-size:12px;width:100%'>"
    h += "<tr style='background:#161b22;color:#c9d1d9'>"
    for col in ["Symbol","Price","Entry","Stop","Target","SC Date"]:
        h += f"<th style='border:1px solid #30363d;padding:6px;text-align:left'>{col}</th>"
    h += "</tr>"
    for r in rows:
        h += "<tr>"
        h += f"<td style='border:1px solid #30363d;padding:6px;font-weight:bold'>{esc(r.get('symbol'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px'>{fmt(r.get('last_close'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px;color:#7ee787;font-weight:bold'>{fmt(r.get('entry'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px'>{fmt(r.get('stop'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px'>{fmt(r.get('target'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px'>{esc(r.get('sc_date'))}</td>"
        h += "</tr>"
    h += "</table>"
    return h

def dt_table(rows, is_bull):
    if not rows: return "<p style='color:#8b949e'>No signals.</p>"
    h = "<table cellpadding='6' cellspacing='0' style='border-collapse:collapse;font-family:Arial,sans-serif;font-size:12px;width:100%'>"
    h += "<tr style='background:#161b22;color:#c9d1d9'>"
    cols = ["Symbol","Price","BUY AT","Stop","Target","R:R","Buy On"] if is_bull else ["Symbol","Price","SELL AT","R:R"]
    for col in cols:
        h += f"<th style='border:1px solid #30363d;padding:6px;text-align:left'>{col}</th>"
    h += "</tr>"
    for r in rows:
        h += "<tr>"
        h += f"<td style='border:1px solid #30363d;padding:6px;font-weight:bold'>{esc(r.get('symbol'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px'>{fmt(r.get('last_close'))}</td>"
        color = "#00d26a" if is_bull else "#f85149"
        h += f"<td style='border:1px solid #30363d;padding:6px;color:{color};font-weight:bold'>{fmt(r.get('entry'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px'>{fmt(r.get('stop'))}</td>"
        if is_bull:
            h += f"<td style='border:1px solid #30363d;padding:6px'>{fmt(r.get('target'))}</td>"
        h += f"<td style='border:1px solid #30363d;padding:6px'>{esc(r.get('rr'))}</td>"
        if is_bull:
            h += f"<td style='border:1px solid #30363d;padding:6px'>{esc(r.get('buy_on'))}</td>"
        h += "</tr>"
    h += "</table>"
    return h

def build_email():
    today = str(date.today())
    signals = json.load(open("signals.json"))
    daytrade = json.load(open("daytrade.json"))

    c2 = [s for s in signals if s.get("stage") == "C2"]
    c1 = [s for s in signals if s.get("stage") == "C1"]

    ord_st = {"FRESH":0,"VALID":1,"LATE":2,"FAILED":3}
    c2.sort(key=lambda x: (ord_st.get(x.get("status",""),9), abs(x.get("entry_gap_pct") or 0)))
    c1.sort(key=lambda x: x.get("symbol",""))

    bulls = [d for d in daytrade if d.get("direction") == "bullish"]
    bears = [d for d in daytrade if d.get("direction") == "bearish"]
    bulls.sort(key=lambda x: -(x.get("rr") or 0))
    bears.sort(key=lambda x: -(x.get("rr") or 0))

    subj = f"PSX Signals — {today} — {len(c2)} Strong Buys | {len(c1)} Buys | {len(bulls)} Day Trades"

    body = f"""
<html><body style='background:#0a0f1e;color:#e6edf3;font-family:Arial,sans-serif;padding:20px;max-width:900px;margin:auto'>
<h1 style='color:#e6edf3;margin-bottom:4px'>PSX Signals — {today}</h1>
<p style='color:#8b949e;font-size:13px'>Wyckoff: {len(c2)} strong buys + {len(c1)} buys | Hougaard: {len(bulls)} bull + {len(bears)} bear</p>

<h2 style='color:#2ea043;border-bottom:2px solid #2ea043;padding-bottom:4px;margin-top:24px'>WYCKOFF — STRONG BUY (C2)</h2>
{c2_table(c2)}

<h2 style='color:#7ee787;border-bottom:2px solid #7ee787;padding-bottom:4px;margin-top:24px'>WYCKOFF — BUY (C1)</h2>
{c1_table(c1)}

<h2 style='color:#00d26a;border-bottom:2px solid #00d26a;padding-bottom:4px;margin-top:24px'>HOUGAARD — BULLISH (BUY)</h2>
{dt_table(bulls, True)}

<h2 style='color:#f85149;border-bottom:2px solid #f85149;padding-bottom:4px;margin-top:24px'>HOUGAARD — BEARISH (AVOID)</h2>
{dt_table(bears, False)}

<p style='color:#6e7681;font-size:11px;margin-top:24px'>Auto-generated from psx-wyckoff. Not financial advice.</p>
</body></html>
"""
    return subj, body

def send():
    resend.api_key = RESEND_API_KEY
    subj, body = build_email()
    recipients = [e.strip() for e in EMAIL_TO.split(",") if e.strip()]
    params = {
        "from": FROM_ADDR,
        "to": recipients,
        "subject": subj,
        "html": body,
    }
    result = resend.Emails.send(params)
    print("Sent:", result)

if __name__ == "__main__":
    send()
