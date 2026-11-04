"""Build latest.json: a small first-paint payload for the dashboard.

Carries the latest and previous snapshots with the heavy market-feed fields
stripped, plus headline index numbers, so the page renders the header, stat
cards and tables before the multi-MB snapshots.json finishes loading in the
background. Run after build_comparison.py (needs comparison_data.json).
"""
import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STRIP = ("gpuEconomy", "gpuEconomyStatus", "gpuPriceTests", "gpuPriceTestsStatus")


def lite(snapshot):
    return {k: v for k, v in snapshot.items() if k not in STRIP}


snapshots = json.loads((ROOT / "snapshots.json").read_text())["snapshots"]
dates = sorted(snapshots)
latest = snapshots[dates[-1]]
previous = snapshots[dates[-2]] if len(dates) > 1 else None

out = {
    "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "snapshotCount": len(dates),
    "latest": lite(latest),
    "previous": lite(previous) if previous else None,
}


def index_headline(points, key):
    pts = [p for p in points if p.get(key) is not None]
    if not pts:
        return None
    last = pts[-1]
    cutoff = datetime.date.fromisoformat(last["date"]) - datetime.timedelta(days=30)
    ref = next((p for p in reversed(pts[:-1]) if datetime.date.fromisoformat(p["date"]) <= cutoff), None)
    return {
        "date": last["date"],
        "value": last[key],
        "refDate": ref["date"] if ref else None,
        "changePct": round((last[key] - ref[key]) / ref[key] * 100, 2) if ref and ref[key] else None,
    }


try:
    comparison = json.loads((ROOT / "comparison_data.json").read_text())
    semi = comparison.get("semiAnalysis", [])
    h100 = next((p for p in latest["latitude"]["plans"] if p["id"] == "g3.h100.small"), None)
    out["headlines"] = {
        "b200Index": index_headline(semi, "b200"),
        "h100Index": index_headline(semi, "h100"),
        "latitudeH100": {
            "plan": "g3.h100.small",
            "hourly": h100["hourly"],
            "capturedAt": latest["latitude"].get("capturedAt") or latest.get("capturedAt"),
        } if h100 else None,
    }
except FileNotFoundError:
    out["headlines"] = None

(ROOT / "latest.json").write_text(json.dumps(out, separators=(",", ":")) + "\n")
print("latest.json written:", (ROOT / "latest.json").stat().st_size, "bytes;",
      len(dates), "snapshots; latest", dates[-1])
