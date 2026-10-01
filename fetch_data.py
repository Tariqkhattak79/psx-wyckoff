import psxdata 
import pandas as pd 
from datetime import date, timedelta 
import os 
 
OUT = "data" 
os.makedirs(OUT, exist_ok=True) 
 
syms = psxdata.indices("KSE100")["symbol"].tolist()
EXTRA = ['LUCK', 'SHEZ', 'LOTCHEM', 'SPWL', 'SITC', 'PREMA', 'APL', 'NRL', 'TRG', 'ADMM', 'POL', 'NETSOL', 'NATF', 'NCL', 'SPSL', 'FATIMA', 'WAHDAT', 'ASTL', 'AICL', 'GDL', 'ASC', 'AHL', 'DOL', 'COLG', 'STL', 'BAFL', 'PIBTL', 'FFL', 'IMAGE', 'NCPL', 'SYS', 'FCCL', 'ATRL', 'BECO', 'PAKQAT', 'HUMNL', 'FECTC', 'PNSC', 'NPL', 'AGTL', 'IREIT', 'PIAHCLA', 'MLCF', 'TSBL', 'IBLHL', 'AKBL', 'BIPL', 'ATLH', 'ACPL', 'FLYNG', 'POWER', 'GWLC', 'KEL', 'GCIL', 'GGGL', 'BFAGRO', 'SHFA', 'MCB', 'MEBL', 'DCR', 'TPLT', 'ICIBL', 'TREET', 'HASCOL', 'ILP', 'ITTEFAQ', 'IGIHL', 'BIFO', 'ISL', 'CSAP', 'HIRAT', 'BNL', 'GLAXO', 'HALEON', 'FCL', 'TBL', 'CLOV', 'SYM', 'LCI', 'PTC', 'TOWL', 'SGF', 'BWHL', 'AGHA', 'OTSU', 'HINOON', 'ABOT', 'JVDC', 'EPCL', 'WAFI', 'BBFL', 'BGL', 'SBL', 'MTL', 'DGKC', 'HBL', 'ASL', 'SSGC', 'BERG', 'GHNI', 'GAL', 'DFML', 'AIRLINK', 'GGL', 'AGL', 'THCCL', 'GHGL', 'MERIT', 'PPP', 'MARI', 'ENGROH', 'SNGP', 'FFC', 'HUBC', 'SAZEW', 'UBL', 'BOP', 'TOMCL', 'NBP', 'LOADS', 'PAEL', 'WAVESAPP', 'CNERGY', 'KOHC', 'MUGHAL', 'SEARL', 'BFBIO', 'GCWL', 'HTL', 'NML', 'PRL', 'CPHL', 'WAVES', 'BWCL', 'GATI', 'SLGL', 'PAKRI', 'ORM', 'HCAR', 'ABL', 'FABL', 'DCL', 'UNITY', 'SPEL']
for e in EXTRA:
    if e not in syms:
        syms.append(e) 
print("KSE100 count:", len(syms)) 
 
end = date.today() 
start = end - timedelta(days=400) 
 
ok = 0 
fail = 0 
for sym in syms: 
    try: 
        df = psxdata.stocks(sym, start=str(start), end=str(end)) 
        if df is None or len(df) == 0: 
            print(sym + ": EMPTY") 
            fail += 1 
            continue 
        df = df.sort_values("date").reset_index(drop=True) 
        df.to_csv(OUT + "/" + sym + ".csv", index=False) 
        ok += 1 
    except Exception as e: 
        print(sym + ": ERROR " + str(e)) 
        fail += 1 
 
print("DONE ok=" + str(ok) + " fail=" + str(fail)) 
