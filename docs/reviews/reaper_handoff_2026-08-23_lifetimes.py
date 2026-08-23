"""Recompute the worktree-lifetime distribution from the 16:34 measurement.

The claim under review is "median useful life: ten minutes". Prove It says
recompute, do not eyeball -- so this reads the recorded born/last-write pairs
and reports the actual distribution.
"""
import csv
import statistics
from datetime import datetime
from pathlib import Path

SRC = Path(__file__).with_name("reaper_handoff_2026-08-23_worktree_lifetimes.csv")
FMT = "%Y-%m-%d %H:%M"

rows = []
with SRC.open() as fh:
    for r in csv.DictReader(fh):
        born = datetime.strptime(r["born"], FMT)
        last = datetime.strptime(r["last_write"], FMT)
        rows.append((r["name"], (last - born).total_seconds() / 60))

rows.sort(key=lambda t: t[1])
mins = [m for _, m in rows]
n = len(mins)

print(f"n = {n}")
print(f"median = {statistics.median(mins):.0f} min")
print(f"mean   = {statistics.mean(mins):.0f} min")
for q, label in ((0.25, "p25"), (0.75, "p75"), (0.90, "p90")):
    idx = min(int(q * n), n - 1)
    print(f"{label}    = {mins[idx]:.0f} min")
print(f"min/max = {mins[0]:.0f} / {mins[-1]:.0f} min")

print("\nbimodality check -- counts by bucket")
buckets = [(0, 20, "under 20 min"), (20, 60, "20-60 min"),
           (60, 240, "1-4 h"), (240, 1440, "4-24 h"), (1440, 1e9, "over a day")]
for lo, hi, label in buckets:
    k = sum(1 for m in mins if lo <= m < hi)
    print(f"  {label:<12} {k:>2}  {'#' * k}")

short = [m for m in mins if m < 60]
print(f"\nunder an hour: {len(short)} of {n} ({100*len(short)/n:.0f}%), "
      f"median of those {statistics.median(short):.0f} min")
