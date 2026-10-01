src = open("fetch_data.py").read()
import re
EXTRA = ["LUCK","SHEZ","LOTCHEM","SPWL","SITC","PREMA","APL","NRL","TRG","ADMM","POL","NETSOL","NATF","NCL","SPSL","FATIMA","WAHDAT","ASTL","AICL","GDL","ASC","AHL","DOL","COLG","STL","BAFL","PIBTL","FFL","IMAGE","NCPL","SYS","FCCL","ATRL","BECO","PAKQAT","HUMNL","FECTC","PNSC","NPL","AGTL","IREIT","PIAHCLA","MLCF","TSBL","IBLHL","AKBL","BIPL","ATLH","ACPL","FLYNG","POWER","GWLC","KEL","GCIL","GGGL","BFAGRO","SHFA","MCB","MEBL","DCR","TPLT","ICIBL","TREET","HASCOL","ILP","ITTEFAQ","IGIHL","BIFO","ISL","CSAP","HIRAT","BNL","GLAXO","HALEON","FCL","TBL","CLOV","SYM","LCI","PTC","TOWL","SGF","BWHL","AGHA","OTSU","HINOON","ABOT","JVDC","EPCL","WAFI","BBFL","BGL","SBL","MTL","DGKC","HBL","ASL","SSGC","BERG","GHNI","GAL","DFML","AIRLINK","GGL","AGL","THCCL","GHGL","MERIT","PPP","MARI","ENGROH","SNGP","FFC","HUBC","SAZEW","UBL","BOP","TOMCL","NBP","LOADS","PAEL","WAVESAPP","CNERGY","KOHC","MUGHAL","SEARL","BFBIO","GCWL","HTL","NML","PRL","CPHL","WAVES","BWCL","GATI","SLGL","PAKRI","ORM","HCAR","ABL","FABL","DCL","UNITY","SPEL"]
# dedupe while preserving order
seen=set()
EXTRA=[x for x in EXTRA if not (x in seen or seen.add(x))]
extra_str = 'EXTRA = ' + repr(EXTRA)
if 'EXTRA =' in src:
    src = re.sub(r'EXTRA = \[[^\]]*\]', extra_str, src)
else:
    src = src.replace(
        'syms = psxdata.indices("KSE100")["symbol"].tolist()',
        'syms = psxdata.indices("KSE100")["symbol"].tolist()\n' + extra_str + '\nfor e in EXTRA:\n    if e not in syms:\n        syms.append(e)'
    )
open("fetch_data.py","w").write(src)
print("patched", len(EXTRA), "extras (deduped)")
