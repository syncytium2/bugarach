"""Would windows at every position beat the tool's two? A check behind one paragraph of the page.

The tool counts onsets in back-to-back windows at two offsets, half a window apart, and averages
the two (``population_cumulants``). This counts at every frame offset instead (fully sliding) and
compares, on the page's own simulated recordings:

- **false pairs** from a field-wide busy stretch with nothing planted (1 and 5 minutes, sharp
  edges, the bench's stretch level), the excess *f*₂ per window after subtracting the shifted
  copies;
- **the planted share** on the mixed set at the quiet background, fixed model, *f*₃/*f*₂ pooled
  over the set as the tool pools it.

Both variants use the tool's ``shifted`` copies (20, slides at least two windows apart), so the
only difference is where the windows fall. Simulated recordings only; no real recording is read.

Run: python docs/learned/coordination_share_explainer/check_window_placement.py
  Writes ``window_placement.json`` beside this script.
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(ROOT / "src"), str(ROOT / "tools")]

import numpy as np  # noqa: E402

import explain_coordination_share as e  # noqa: E402
import measure_coordination_rates as mcr  # noqa: E402

WF = int(round(1.0 / e.DT))         # frames in a 1 s window, as the page computes it
VARIANTS = {"two offsets (the tool)": (0, WF // 2), "every offset (sliding)": tuple(range(WF))}
STRETCHES_SEC = (60.0, 300.0)
STRETCH_HZ = e.HOT["hot_rate_hz"]   # the bench's elevated-rate level, as Figure 5A uses it


def cumulants(trains, n_frames, offsets):
    onsets = np.concatenate(trains)
    out = []
    for off in offsets:
        n = (n_frames - off) // WF
        f = onsets[(onsets >= off) & (onsets < off + n * WF)] - off
        out.append(mcr.factorial_cumulants(np.bincount(f // WF, minlength=n)[:n]))
    return np.mean(out, axis=0)


def excess(job):
    seed, kw = job
    r = e.recording(seed, **kw)
    n_frames = r["L"]
    rate = np.mean([len(t) for t in r["trains"]]) / e.T
    res = {}
    for name, offsets in VARIANTS.items():
        f2, f3 = cumulants(r["trains"], n_frames, offsets)
        rng = np.random.RandomState(seed)
        s = np.array([cumulants(mcr.shifted(r["trains"], n_frames, 2 * WF, rng), n_frames, offsets)
                      for _ in range(20)])
        res[name] = (f2 - s[:, 0].mean(), f3 - s[:, 1].mean(), r["truth"]["share"], rate)
    return res


def recovered_over_planted(rows, name):
    f2 = np.array([x[name][0] for x in rows])
    f3 = np.array([x[name][1] for x in rows])
    k = f3.sum() / f2.sum() + 2                      # pooled ratio, fixed model
    lam = f2 / (1.0 * k * (k - 1))
    share = lam * k / e.N / np.array([x[name][3] for x in rows])
    return share / np.array([x[name][2] for x in rows])


def main():
    out = {"recordings_per_set": len(e.SEEDS), "false_pairs_per_window": {}, "planted_share": {}}
    with ProcessPoolExecutor() as pool:
        planted = list(pool.map(excess, [(s, dict(bg_hz=e.QUIET)) for s in e.SEEDS]))
        for d in STRETCHES_SEC:
            kw = dict(bg_hz=e.QUIET, n_total=0, hot_window=(1200.0, 1200.0 + d),
                      hot_rate_hz=STRETCH_HZ, ramp_sec=0.0)
            rows = list(pool.map(excess, [(s, kw) for s in e.SEEDS]))
            out["false_pairs_per_window"][f"{d:.0f} s stretch"] = {
                name: round(float(np.median([x[name][0] for x in rows])), 4) for name in VARIANTS}
    for name in VARIANTS:
        r = recovered_over_planted(planted, name)
        out["planted_share"][name] = {
            "median_error": round(float(np.median(r) - 1), 4),
            "p10": round(float(np.percentile(r, 10)), 3),
            "p90": round(float(np.percentile(r, 90)), 3)}
    (HERE / "window_placement.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
