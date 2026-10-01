src = open("classify.py").read()
old = 'if near_hi>=2 and near_lo>=2 and width_pct>=8:'
new = 'if near_hi>=2 and near_lo>=2 and 4<=width_pct<=35:'
if old in src:
    src = src.replace(old, new)
    open("classify.py","w").write(src)
    print("patched 4-35")
else:
    print("marker not found")
