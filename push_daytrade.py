import os, json, requests
from datetime import date

URL = os.environ["SUPABASE_URL"] + "/rest/v1/daytrade_signals"
KEY = os.environ["SUPABASE_SERVICE_KEY"]
HEADERS = {"apikey": KEY, "Authorization": "Bearer " + KEY, "Content-Type": "application/json", "Prefer": "return=minimal"}

run_date = str(date.today())

r = requests.delete(URL + "?run_date=eq." + run_date, headers=HEADERS)
print("Delete old:", r.status_code)

rows = json.load(open("daytrade.json"))
for row in rows:
    row["run_date"] = run_date

if rows:
    r = requests.post(URL, headers=HEADERS, json=rows)
    print("Insert:", r.status_code, r.text[:200])
else:
    print("No rows to push")
