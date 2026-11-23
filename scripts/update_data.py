import json, os, urllib.request
from datetime import datetime, timezone, date, timedelta

API_KEY = os.environ["FRED_API_KEY"]
SERIES = {
    "mortgage_30y": "MORTGAGE30US",  # Freddie Mac PMMS, weekly
    "treasury_5y": "DGS5",           # 5-yr Treasury, daily
    "treasury_10y": "DGS10",         # 10-yr Treasury, daily
}
HISTORY_START = "2026-10-01"         # history chart starts here and grows from then on

def fetch(series_id, start):
    """All observations since `start`, oldest first, skipping missing days ('.')."""
    url = ("https://api.stlouisfed.org/fred/series/observations"
           f"?series_id={series_id}&api_key={API_KEY}"
           f"&file_type=json&sort_order=asc&observation_start={start}")
    with urllib.request.urlopen(url) as r:
        obs = json.load(r)["observations"]
    return [(o["date"], float(o["value"])) for o in obs if o["value"] != "."]

def build(data, today):
    # Latest value of each series -> market.json
    market = {k: {"value": v[-1][1], "date": v[-1][0]} for k, v in data.items()}
    market["fetched_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # One history row per Treasury trading day in the window.
    # The weekly mortgage rate is carried forward to each day until the next release.
    cutoff = HISTORY_START
    t5, t10, mort = dict(data["treasury_5y"]), dict(data["treasury_10y"]), data["mortgage_30y"]
    history = []
    for d in sorted(set(t5) & set(t10)):
        if d < cutoff:
            continue
        prior = [m for m in mort if m[0] <= d]
        if not prior:
            continue
        history.append({
            "date": d,
            "mortgage_30y": {"value": prior[-1][1], "date": prior[-1][0]},
            "treasury_5y": {"value": t5[d], "date": d},
            "treasury_10y": {"value": t10[d], "date": d},
        })
    return market, history

if __name__ == "__main__":
    today = date.today()
    start = (date.fromisoformat(HISTORY_START) - timedelta(days=14)).isoformat()  # extra so a mortgage reading precedes the start
    data = {k: fetch(v, start) for k, v in SERIES.items()}
    market, history = build(data, today)
    os.makedirs("data", exist_ok=True)
    with open("data/market.json", "w") as f:
        json.dump(market, f, indent=2)
    with open("data/history.json", "w") as f:
        json.dump(history, f, indent=2)
    print(json.dumps(market, indent=2))
    print(f"history rows: {len(history)} ({history[0]['date']} to {history[-1]['date']})" if history else "history rows: 0")
