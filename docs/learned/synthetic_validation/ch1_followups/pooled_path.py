"""Round 3, task 7 (blind review role 6): the coordination-rates tool's shipped pooled reporting
path against the per-recording path the chapter validates.

Three readings per condition-window (events of 10+ cells, 16 conditions x 3 windows per
background, 5 recordings each), all as ratios to planted, from the run records' per-recording
cumulants (no new simulation):

  per-rec  : solve() on each recording's own (f2, f3), median of the 5 (theory.check's "meas";
             what the chapter validates);
  pooled   : solve() on the condition's mean (f2, f3) (theory.check's "pooled" column; a
             ratio-of-means reading);
  shipped  : measure_coordination_rates.per_recording() as summarize() calls it: k from the
             window-weighted pooled f3/f2 (all recordings have the same length here, so the weights
             cancel), each recording's lambda from its own f2 at that k, then the median over
             recordings (summarize()'s nanmedian). Participants are the pooled k.

Residual = reading - prediction (theory_check*.json's "exact": the hard-core form, and the
general form with the generator's empirical train), for the original and held-out records.
Also the median-of-ratio vs ratio-of-means gap for RATE (per-rec minus pooled; derivation.md
section 7.2 quotes about 0.008).

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/pooled_path.py
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
SV = HERE.parent
ROOT = SV.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import measure_coordination_rates as mcr  # noqa: E402

WS = ("1.0", "2.0", "4.0")
RECORDS = {
    "original": (SV / "aim1_one_source.json", {"hard-core": SV / "theory_check.json",
                                               "general": SV / "theory_check_empirical.json"}),
    "held-out": (HERE / "aim1_one_source_heldout.json", {"hard-core": HERE / "theory_check_heldout.json",
                                                         "general": HERE / "theory_check_heldout_empirical.json"}),
}


def readings(rows, N, T):
    cond = defaultdict(list)
    for r in rows:
        t = r["true"]
        if int(round(t["k"])) >= 10:
            cond[(t["bg_rate"], t["jitter"], int(round(t["k"])), t["n_events"])].append(r)
    out = {}
    for key, rs in cond.items():
        bg, s, k, ne = key
        lam = ne / T
        for w in WS:
            per_k = [x["coord_rates"][w]["k"] / x["true"]["k"] for x in rs]
            per_l = [x["coord_rates"][w]["lam"] / x["true"]["lam"] for x in rs]
            f2 = np.mean([x["cum"][w]["f2"] for x in rs])
            f3 = np.mean([x["cum"][w]["f3"] for x in rs])
            pv = mcr.solve(f2, f3, N, float(w), "fixed")
            recs = [dict(N=N, cum={w: dict(f2=x["cum"][w]["f2"], f3=x["cum"][w]["f3"], n_win=1)}) for x in rs]
            sh = mcr.per_recording(recs, float(w), "fixed")
            out[(bg, s, k, ne, float(w))] = dict(
                per_rec=dict(k=float(np.nanmedian(per_k)), lam=float(np.nanmedian(per_l))),
                pooled=dict(k=pv["k"] / k, lam=pv["lam"] / lam),
                shipped=dict(k=float(np.nanmedian([x["k"] for x in sh])) / k,
                             lam=float(np.nanmedian([x["lam"] for x in sh])) / lam))
    return out


if __name__ == "__main__":
    res = {}
    print("events of 10+ cells; residual = reading / planted - prediction / planted; 48 condition-windows "
          "per background. median |res| / median signed res / above of 48 (sign p)")
    print("record   form      bg   qty  | per-rec (chapter)              | pooled solve (ratio of means)  "
          "| shipped per_recording+median")
    gaps = {}
    for rname, (rp, forms) in RECORDS.items():
        rec = json.loads(rp.read_text())
        rd = readings(rec["rows"], rec["n_roi"], rec["duration_sec"])
        for form, cp in forms.items():
            chk = json.loads(cp.read_text())["coord_rates"]
            pred = {(c["bg"], c["sigma"], c["k"], c["n_events"], c["w"]): c["exact"] for c in chk if c["k"] >= 10}
            for c in chk:   # consistency: our per-rec median equals the check record's "meas"
                if c["k"] >= 10:
                    m = rd[(c["bg"], c["sigma"], c["k"], c["n_events"], c["w"])]["per_rec"]
                    assert all(abs(m[q] - c["meas"][q]) < 1e-12 or not np.isfinite(c["meas"][q]) for q in ("k", "lam"))
            for bg in (0.01, 0.05):
                for q in ("k", "lam"):
                    keys = sorted(kk for kk in rd if kk[0] == bg)
                    line = f"{rname:8s} {form:9s} {bg:4} {q:4s} |"
                    row = {}
                    for path in ("per_rec", "pooled", "shipped"):
                        r = np.array([rd[kk][path][q] - pred[kk][q] for kk in keys])
                        r = r[np.isfinite(r)]
                        ab = int(np.sum(r > 0))
                        p = float(stats.binomtest(ab, r.size).pvalue)
                        row[path] = dict(median_abs=float(np.median(np.abs(r))), median=float(np.median(r)),
                                         worst=float(np.max(np.abs(r))), above=ab, n=int(r.size), sign_p=p)
                        line += f" {np.median(np.abs(r)):.4f} {np.median(r):+.4f} {ab:2d}/{r.size} ({p:.3f}) |"
                    res[f"{rname},{form},{bg},{q}"] = row
                    print(line)
        for bg in (0.01, 0.05):
            keys = [kk for kk in rd if kk[0] == bg]
            g1 = np.array([rd[kk]["per_rec"]["lam"] - rd[kk]["pooled"]["lam"] for kk in keys])
            g2 = np.array([rd[kk]["per_rec"]["lam"] - rd[kk]["shipped"]["lam"] for kk in keys])
            g3 = np.array([rd[kk]["per_rec"]["k"] - rd[kk]["pooled"]["k"] for kk in keys])
            gaps[f"{rname},{bg}"] = dict(rate_perrec_minus_pooled=[float(np.nanmedian(g1)), float(np.nanpercentile(g1, 25)), float(np.nanpercentile(g1, 75))],
                                        rate_perrec_minus_shipped=[float(np.nanmedian(g2)), float(np.nanpercentile(g2, 25)), float(np.nanpercentile(g2, 75))],
                                        k_perrec_minus_pooled=[float(np.nanmedian(g3)), float(np.nanpercentile(g3, 25)), float(np.nanpercentile(g3, 75))])
    print("\nmedian-of-ratio minus ratio-of-means, median [IQR] over the 48 condition-windows (form-free: "
          "no prediction involved)")
    for kk, g in gaps.items():
        a, b, c = g["rate_perrec_minus_pooled"], g["rate_perrec_minus_shipped"], g["k_perrec_minus_pooled"]
        print(f"  {kk}: rate per-rec - pooled {a[0]:+.4f} [{a[1]:+.4f}, {a[2]:+.4f}] | rate per-rec - shipped "
              f"{b[0]:+.4f} [{b[1]:+.4f}, {b[2]:+.4f}] | participants per-rec - pooled {c[0]:+.4f} [{c[1]:+.4f}, {c[2]:+.4f}]")
    (HERE / "pooled_path.json").write_text(json.dumps(dict(residuals=res, gaps=gaps), indent=1))
