"""The floor + 1 review's summary tables, from detect_with_floors' windows.csv.

    python floor_plus_one_summary.py <run folder>     # prints markdown tables

Per stream x detector x group (DI, OVX, MALE, ORX) x window kind: calls at the window's own floor,
calls at own floor + 1, and the share of calls lost, summed over windows. Only windows with a
floor are counted. Descriptive only.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

run = Path(sys.argv[1])
res = json.loads((run / "results.json").read_text(encoding="utf-8"))
groups = res["groups"]
acc = defaultdict(lambda: [0, 0, 0, set()])      # calls at floor, at floor+1, windows, recordings
with (run / "windows.csv").open(encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        if r["variant"] not in ("own_floor", "own_plus_1") or r["n_calls"] in ("", None):
            continue
        k = (r["stream"], r["detector"], r["group"], r["window_kind"])
        a = acc[k]
        a[0 if r["variant"] == "own_floor" else 1] += int(r["n_calls"])
        if r["variant"] == "own_floor":
            a[2] += 1
            a[3].add(r["slice_id"])
NAME = {"coact": "CoactDetect", "chorus_norm": "chorus_norm", "chorus_gain_norm": "chorus_gain_norm"}


def calls(n: int) -> str:
    return f"{n:,} call" + ("" if n == 1 else "s")


def cell(a) -> str:
    if not a:
        return "—"
    lost = f"{100 * (a[0] - a[1]) / a[0]:.0f}% lost" if a[0] else "no calls at the floor"
    return f"{calls(a[0])} → {a[1]:,} ({lost})"


for stream in ("fast", "slow", "combined"):
    print(f"\n**{stream.capitalize()} stream**: calls at own floor → at own floor + 1, summed over "
          f"windows\n")
    print("| Detector | Group | Recordings | Baseline windows | Treatment windows |")
    print("|---|---|---|---|---|")
    for det in ("coact", "chorus_norm", "chorus_gain_norm"):
        tb, tt = [0, 0], [0, 0]
        for g in groups:
            b, t = acc.get((stream, det, g, "baseline")), acc.get((stream, det, g, "treatment"))
            n = len((b[3] if b else set()) | (t[3] if t else set()))
            for tot, a in ((tb, b), (tt, t)):
                if a:
                    tot[0] += a[0]
                    tot[1] += a[1]
            print(f"| {NAME[det]} | {g} | {n} | {cell(b)} | {cell(t)} |")
        print(f"| **{NAME[det]}** | **all** | | **{cell(tb)}** | **{cell(tt)}** |")
tot = defaultdict(lambda: [0, 0])
for (stream, det, g, kind), a in acc.items():
    tot[(stream, det)][0] += a[0]
    tot[(stream, det)][1] += a[1]
print("\nTOTALS")
for (stream, det), (f0, f1) in sorted(tot.items()):
    print(stream, det, f0, f1, f"{100 * (f0 - f1) / f0:.1f}%" if f0 else "-")
