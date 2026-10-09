with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

old = """  if(s.quality){
    var qcls = s.quality==="A"?"qa":(s.quality==="B"?"qb":"qc");
    var qdir = isBull?"qbull":"qbear";
    h+="<div><span class='"+(qcls+" "+qdir)+"'>GRADE "+s.quality+"</span></div>";
  }"""
new = """  if(s.quality){
    var qcls = s.quality==="A"?"qa":(s.quality==="B"?"qb":"qc");
    var qdir = isBull?"qbull":"qbear";
    h+="<div><span class='"+(qcls+" "+qdir)+"'>GRADE "+s.quality+"</span>";
    var trendIcon = s.trend_ok ? "&#10003;" : "&#10007;";
    var volIcon = s.vol_ok ? "&#10003;" : "&#10007;";
    var gapIcon = s.gap_ok ? "&#10003;" : "&#10007;";
    var trendCls = s.trend_ok ? "qfyes" : "qfno";
    var volCls = s.vol_ok ? "qfyes" : "qfno";
    var gapCls = s.gap_ok ? "qfyes" : "qfno";
    h+="<span class='qflag "+trendCls+"'>TREND "+trendIcon+"</span>";
    h+="<span class='qflag "+volCls+"'>VOL "+volIcon+"</span>";
    h+="<span class='qflag "+gapCls+"'>GAP "+gapIcon+"</span>";
    h+="</div>";
  }"""
html = html.replace(old, new, 1)

css_old = ".empty{text-align:center"
css_new = """.qflag{display:inline-block;padding:2px 8px;border-radius:3px;font-size:10px;font-weight:700;margin-top:6px;margin-right:6px;letter-spacing:0.5px}
.qflag.qfyes{background:#0d2a1a;color:#3fb950;border:1px solid #2ea043}
.qflag.qfno{background:#2a0d0d;color:#f85149;border:1px solid #da3633}
.empty{text-align:center"""
html = html.replace(css_old, css_new, 1)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched")
