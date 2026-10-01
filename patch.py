import re
src = open("classify.py").read()
# Add the 3 fields after stage="X",action="..." in every return dict
pattern = re.compile(r'return dict\(symbol=sym,stage="([A-Z])",action=("(?:[^"\\]|\\.)*"),')
src = pattern.sub(lambda m: 'return dict(symbol=sym,stage="'+m.group(1)+'",action='+m.group(2)+',last_close=round(last_close,2),prev_close=round(prev_close,2),change_pct=change_pct,', src)
open("classify.py","w").write(src)
print("done")
