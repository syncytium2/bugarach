"""Task 3 (murderboard 2026-10-29, roles 1, 4, 6): like-for-like residual statistics, hard-core
form against the general form, from theory.check() records. Also the table task 2 needs.

For each record pair (hard-core `theory_check*.json` and the general form's
`theory_check*_empirical.json`, whose rows also carry the hard-core prediction as "page"), per
background, events of 10+ cells, for participants (k), rate (lam) and share:

* residual = condition median of measured / planted minus predicted / planted, per
  condition-window (16 conditions x 3 windows = 48 per background; the windows reuse the same
  recordings, so window-level counts are not independent);
* median |residual|, median signed residual, worst |residual|;
* condition-windows with measured ABOVE predicted, and the two-sided sign-test p over 48;
* condition-windows beyond 2 SE (SE of a median of 5 = 1.2533 SD / sqrt(n), as theory.summary();
  its null rate at n = 5 is simulated there, 0.118), with the binomial P of that many or more;
* per condition (residual averaged over the 3 windows, as theory.summary() does for k): conditions
  with measured BELOW predicted, of 16, and the two-sided sign-test p.

And the joint fit's per-condition ranges (median ratio to planted) for sigma >= 0.2 s, events of
10+ cells, and for sigma 0.05 s and 5-cell events.

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/like_for_like.py
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
NULL_2SE = None


def null_rate():
    global NULL_2SE
    if NULL_2SE is None:
        x = np.random.default_rng(0).standard_normal((400_000, 5))
        NULL_2SE = float(np.mean(np.abs(np.median(x, 1) / (1.2533 * x.std(1) / np.sqrt(5))) > 2))
    return NULL_2SE


def residual_table(rec: dict, key: str, label: str) -> list[dict]:
    """key: 'exact' (the record's own form) or 'page' (hard-core prediction in a general record)."""
    p2 = null_rate()
    out = []
    for bg in (0.01, 0.05):
        for q in ("k", "lam", "share"):
            rs = [r for r in rec["coord_rates"] if r["bg"] == bg and r["k"] >= 10
                  and np.isfinite(r["meas"][q])]
            res = np.array([r["meas"][q] - r[key][q] for r in rs])
            z = np.array([(r["meas"][q] - r[key][q]) / (1.2533 * max(r["meas_sd"][q], 1e-9)
                                                        / np.sqrt(r["n"] - r["n_nan"])) for r in rs])
            nz = int(np.sum(np.abs(z) > 2))
            above = int(np.sum(res > 0))
            byc = defaultdict(list)
            for r, d in zip(rs, res):
                byc[(r["sigma"], r["k"], r["n_events"])].append(d)
            below_c = int(sum(np.mean(v) < 0 for v in byc.values()))
            above_c = int(sum(np.mean(v) > 0 for v in byc.values()))
            out.append(dict(form=label, bg=bg, qty=q, n=int(res.size),
                            median_abs=float(np.median(np.abs(res))),
                            median_signed=float(np.median(res)), worst_abs=float(np.max(np.abs(res))),
                            above=above, sign_p=float(stats.binomtest(above, res.size).pvalue),
                            beyond_2se=nz, expected_2se=p2 * res.size,
                            p_beyond_2se=float(stats.binom.sf(nz - 1, res.size, p2)),
                            n_cond=len(byc), cond_below=below_c, cond_above=above_c,
                            cond_sign_p=float(stats.binomtest(below_c, len(byc)).pvalue)))
    return out


def joint_ranges(rec: dict) -> dict:
    jf = rec["joint_fit"]
    out = {}
    for bg in (0.01, 0.05):
        rr = [r for r in jf if r["bg"] == bg and r["k"] >= 10 and r["sigma"] >= 0.2]
        r05 = [r for r in jf if r["bg"] == bg and r["k"] >= 10 and r["sigma"] == 0.05]
        r5 = [r for r in jf if r["bg"] == bg and r["k"] == 5]
        rng = lambda v: [float(min(v)), float(max(v))]  # noqa: E731
        out[str(bg)] = dict(
            sigma_ratio=rng([r["sigma_q"][1] / r["sigma"] for r in rr]),
            k_ratio=rng([r["k_ratio_q"][1] for r in rr]),
            lam_ratio=rng([r["lam_ratio_q"][1] for r in rr]),
            at_bound_sigma_ge_0_2=int(sum(r["n_at_bound"] for r in rr)),
            sigma_0_05_median_sec=float(np.median([r["sigma_q"][1] for r in r05])),
            sigma_0_05_at_bound=int(sum(r["n_at_bound"] for r in r05)),
            sigma_0_05_n=int(sum(r["n"] for r in r05)),
            five_cell_sigma_ratio=rng([r["sigma_q"][1] / r["sigma"] for r in r5]))
    return out


def report(name: str, hard: dict, gen: dict) -> dict:
    rows = residual_table(hard, "exact", "hard-core") + residual_table(gen, "exact", "general")
    # consistency: the general record's "page" prediction must equal the hard-core record's
    pg = residual_table(gen, "page", "page-in-general")
    same = all(abs(a["median_signed"] - b["median_signed"]) < 1e-12 for a, b in
               zip(rows[:6], pg))
    print(f"\n=== {name}: events of 10+ cells; residual = measured/planted - predicted/planted "
          f"(hard-core record's prediction equals the general record's 'page' column: {same})")
    print(f"  {'form':>9} {'bg':>5} {'qty':>5} | {'med|res|':>8} {'med res':>8} {'worst':>6} | "
          f"{'above':>9} {'p':>6} | {'>2SE':>4} {'exp':>4} {'P(>=)':>6} | {'cond below':>10} {'p':>5}")
    for r in sorted(rows, key=lambda r: (r["bg"], ["k", "lam", "share"].index(r["qty"]), r["form"] != "hard-core")):
        print(f"  {r['form']:>9} {r['bg']:>5} {r['qty']:>5} | {r['median_abs']:8.4f} "
              f"{r['median_signed']:+8.4f} {r['worst_abs']:6.3f} | {r['above']:>3} of {r['n']:<3} "
              f"{r['sign_p']:6.3f} | {r['beyond_2se']:>4} {r['expected_2se']:4.1f} "
              f"{r['p_beyond_2se']:6.3f} | {r['cond_below']:>3} of {r['n_cond']:<4} "
              f"{r['cond_sign_p']:5.3f}")
    jr = dict(hard_core=joint_ranges(hard), general=joint_ranges(gen))
    print("  joint fit, per-condition median ratio to planted (events of 10+ cells, sigma >= 0.2 s);"
          " sigma 0.05 s; 5-cell events")
    for form, d in jr.items():
        for bg, v in d.items():
            print(f"    {form:9s} bg {bg}: sigma {v['sigma_ratio'][0]:.2f}-{v['sigma_ratio'][1]:.2f}, "
                  f"k {v['k_ratio'][0]:.2f}-{v['k_ratio'][1]:.2f}, rate {v['lam_ratio'][0]:.2f}-"
                  f"{v['lam_ratio'][1]:.2f} (at sigma bound {v['at_bound_sigma_ge_0_2']}); "
                  f"0.05 s reads {v['sigma_0_05_median_sec']:.3f} s, {v['sigma_0_05_at_bound']} of "
                  f"{v['sigma_0_05_n']} at bound; 5-cell sigma ratio {v['five_cell_sigma_ratio'][0]:.2f}-"
                  f"{v['five_cell_sigma_ratio'][1]:.2f}")
    return dict(residuals=rows, joint_fit_ranges=jr)


if __name__ == "__main__":
    print(f"null rate of |z| > 2 for a median of 5 (simulated as theory.summary): {null_rate():.4f}")
    pairs = [("original Aim 1a record (aim1_one_source.json)", SV / "theory_check.json",
              SV / "theory_check_empirical.json"),
             ("HELD-OUT record (ch1_followups/aim1_one_source_heldout.json)",
              HERE / "theory_check_heldout.json", HERE / "theory_check_heldout_empirical.json")]
    out = {}
    for name, h, g in pairs:
        if not (h.exists() and g.exists()):
            print(f"\n(skipping {name}: {h.name} or {g.name} missing)")
            continue
        out[name] = report(name, json.loads(h.read_text()), json.loads(g.read_text()))
    (HERE / "like_for_like.json").write_text(json.dumps(out, indent=1))
