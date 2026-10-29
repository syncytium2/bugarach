"""Round 2, task 6 (murderboard 2026-10-29 round 2, role 6): the correlogram as shipped, tabulated.

Reads correlogram_vs_joint.json (no new simulation) and prints, per background and planted
jitter, recovered / planted jitter:
  * per recording, shipped calibration: median [IQR] over recordings with a value, and the
    off-curve count split into below the curve (HWHM under its 0.05 s point), above it (over its
    1.0 s point) and no peak;
  * pooled as shipped: the tool pools pairs over recordings before taking the width
    (`measure_jitter_correlogram.main()` -> `pooled`); here per condition (5 recordings each),
    median [range] over the conditions, and how many conditions fell off the curve;
  * per recording, plain Gaussian conversion sigma = HWHM / 1.665: median [IQR], no-peak count;
  * the joint fit (hard-core form) per recording: median [IQR], count at its sigma bound.
The pooled Gaussian conversion is not given: the record keeps the pooled reading only after the
calibration, not the pooled width.

    python docs/learned/synthetic_validation/ch1_followups/correlogram_table.py
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
rec = json.loads((HERE / "correlogram_vs_joint.json").read_text())
ws = rec["calibration"]["hwhm"]
per = rec["per_recording"]


def q(v):
    v = np.asarray([x for x in v if x is not None], float)
    if not v.size:
        return "-"
    a, b, c = np.percentile(v, [25, 50, 75])
    return f"{b:.2f} [{a:.2f}, {c:.2f}]"


print("recovered / planted jitter. per-recording columns: median [IQR] over recordings with a "
      "value; off = below / above the calibration curve / no peak. pooled: per condition "
      "(5 recordings pooled), median [range] over conditions")
print(f"{'b':>5} {'sigma':>5} {'cells':>5} {'n':>3} | {'per rec., shipped cal.':>22} "
      f"{'off b/a/np':>10} | {'pooled as shipped':>24} | {'per rec., Gaussian':>18} {'np':>2} | "
      f"{'joint fit':>18} {'bnd':>3}")
for s in rec["summary"]:
    bg, sig, lab = s["bg"], s["sigma"], s["cells"]
    ps = [p for p in per if p["bg"] == bg and p["sigma"] == sig
          and ((p["k"] >= 10) if lab == "10+" else (p["k"] == 5))]
    cal = [None if p["corr_sigma"] is None else p["corr_sigma"] / sig for p in ps]
    gau = [None if p["gauss_sigma"] is None else p["gauss_sigma"] / sig for p in ps]
    jf = [None if p["joint_sigma"] is None else p["joint_sigma"] / sig for p in ps]
    nopk = sum(p["hwhm"] is None for p in ps)
    below = sum(p["hwhm"] is not None and p["corr_sigma"] is None and p["hwhm"] < ws[0] for p in ps)
    above = sum(p["hwhm"] is not None and p["corr_sigma"] is None and p["hwhm"] > ws[-1] for p in ps)
    pc = s["pooled_condition_correlogram_ratio"]
    pcf = [v for v in pc if v is not None]
    pooled = (f"{np.median(pcf):.2f} [{min(pcf):.2f}-{max(pcf):.2f}] {len(pc) - len(pcf)}/{len(pc)} off"
              if pcf else f"- {len(pc)}/{len(pc)} off")
    nb = sum(bool(p["joint_at_bound"]) for p in ps)
    print(f"{bg:>5} {sig:>5} {lab:>5} {len(ps):>3} | {q(cal):>22} {f'{below}/{above}/{nopk}':>10} | "
          f"{pooled:>24} | {q(gau):>18} {nopk:>2} | {q(jf):>18} {nb:>3}")
