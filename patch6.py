src = open("classify.py").read()
# Find Stage A (sc_age < MIN_SC_AGE) block and add target guard
old = '''hi=round(w["high"].tail(30).max(),2)
        rsn="Climax "+str(sc_age)+"d ago @ "+str(round(sc_low,2))+". If price drops to "+str(round(sc_low,2))+" and closes back above, BUY near "+str(lo)+". Stop "+str(st)+". Target "+str(hi)+"."
        return {**base, "stage":"A","action":"Wait","entry":lo,"stop":st,"target":hi,"range_low":round(sc_low,2),"range_high":hi,"range_pct":None,"reason":rsn}'''
new = '''hi=round(w["high"].tail(30).max(),2)
        if hi > lo * 1.5:
            hi = None
            rsn="Climax "+str(sc_age)+"d ago @ "+str(round(sc_low,2))+". If price drops to "+str(round(sc_low,2))+" and closes back above, BUY near "+str(lo)+". Stop "+str(st)+". Target not reliable (range too wide)."
        else:
            rsn="Climax "+str(sc_age)+"d ago @ "+str(round(sc_low,2))+". If price drops to "+str(round(sc_low,2))+" and closes back above, BUY near "+str(lo)+". Stop "+str(st)+". Target "+str(hi)+"."
        return {**base, "stage":"A","action":"Wait","entry":lo,"stop":st,"target":hi,"range_low":round(sc_low,2),"range_high":hi if hi else round(w["high"].tail(30).max(),2),"range_pct":None,"reason":rsn}'''
if old in src:
    src = src.replace(old, new)
    open("classify.py","w").write(src)
    print("patched")
else:
    print("marker not found")
