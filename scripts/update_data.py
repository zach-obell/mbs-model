import json, os, urllib.request
from datetime import datetime, timezone

API_KEY = os.environ["FRED_API_KEY"]
SERIES = {
    "mortgage_30y": "MORTGAGE30US",  # Freddie Mac PMMS, weekly
    "treasury_5y": "DGS5",           # 5-yr Treasury, daily
    "treasury_10y": "DGS10",         # 10-yr Treasury, daily
}

def latest(series_id):
    url = ("https://api.stlouisfed.org/fred/series/observations"
           f"?series_id={series_id}&api_key={API_KEY}"
           "&file_type=json&sort_order=desc&limit=10")
    with urllib.request.urlopen(url) as r:
        obs = json.load(r)["observations"]
    for o in obs:                     # skip missing days, shown as "."
        if o["value"] != ".":
            return {"value": float(o["value"]), "date": o["date"]}
    raise ValueError(f"No data for {series_id}")

market = {k: latest(v) for k, v in SERIES.items()}
market["fetched_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

os.makedirs("data", exist_ok=True)
with open("data/market.json", "w") as f:
    json.dump(market, f, indent=2)

# History: add a row only when a value's date is new (no duplicates)
path = "data/history.json"
history = json.load(open(path)) if os.path.exists(path) else []
row = {k: market[k] for k in SERIES}
if not history or any(history[-1][k]["date"] != row[k]["date"] for k in SERIES):
    history.append(row)
    with open(path, "w") as f:
        json.dump(history, f, indent=2)

print(json.dumps(market, indent=2))
