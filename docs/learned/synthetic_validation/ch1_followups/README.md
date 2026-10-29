# Chapter 1 follow-ups demanded by the 2026-10-29 murderboard

Written 2026-10-29 for Chapter 1 (Aim 0) of the synthetic-validation goal
([goal page](../../../goals/synthetic-validation.md)). The review is in
[`docs/reviews/chapter-1-aim0_2026-10-29-roles/`](../../../reviews/chapter-1-aim0_2026-10-29-roles/)
(roles 1, 4, 6 and 7). **Synthetic only.** Aim 0 is theory checked by simulation, so nothing here
reads a recording. Task 4 uses lab-like parameter values, and its event trains resample the gap
lists in `runs/2026-09-25-real-intervals/gaps.csv`, exactly as `theory.py --check-real` does. It
says nothing about the lab's recordings themselves.

No existing script or record was edited. Every script here imports the existing ones
(`aim1_one_source`, `theory`, `event_train`, `order_limit`, `tools/measure_jitter_correlogram`).
Where `theory.check()` writes into its own folder, the new scripts point its `HERE` at this folder
for that run.

Rerun from the repository root, with the main checkout's venv python (the worktree has no numpy).
Each run takes about 1–8 min on the lab workstation:

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/correlogram_vs_joint.py --workers 24 > .../correlogram_vs_joint.txt
    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/held_out.py --workers 36     # grid + both checks
    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/held_out.py --summary-only > .../held_out_summary.txt
    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/like_for_like.py > .../like_for_like.txt
    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/lab_values.py --workers 36 > .../lab_values.txt
    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/order_power.py > .../order_power.txt
    # original_summary.txt = theory.py --from-record, then theory.py --train empirical --from-record

| file | what |
|---|---|
| `correlogram_vs_joint.py` → `.txt`, `.json` | Task 1: the correlogram jitter tool beside the joint fit, on the 240 Aim 1a recordings |
| `held_out.py` → `aim1_one_source_heldout.json`, `theory_check_heldout.json`, `theory_check_heldout_empirical.json`, `held_out_summary.txt` | Task 2: the Aim 1a grid rerun on fresh seeds, and `theory.check()` against it (hard-core form, and general form `--train empirical`) |
| `original_summary.txt` | the original records' `theory.py --from-record` and `--train empirical --from-record` printouts, kept for side-by-side reading |
| `like_for_like.py` → `.txt`, `.json` | Task 3 (and Task 2's table): residual statistics computed the same way for the hard-core and general forms, on the original and the held-out records |
| `lab_values.py` → `.txt`, `.json` | Task 4: `theory.check_real()` with every recording's joint fit kept, at lab-like parameter values, for the fast gap list (σ = 0.105 s) and the slow one (σ = 0.131 s) |
| `order_power.py` → `.txt`, `.json` | Task 6: order-detection power at E = 1, 2, 3, 5 events, by Table 1.2's method and two size-corrected variants |

Task 5 (event counts in the baseline windows, from `windows.csv`) was **dropped** on Tony's scope
change of 2026-10-29: Aim 0 is not a real-data chapter. A reviewer (role 1) also asked for a
per-group breakdown (DI, OVX, MALE, ORX). It was deliberately not done, because group comparisons
belong to `fireflies` by default
([ADR-0017](../../../adr/0017-group-and-treatment-comparisons-default-to-fireflies.md)) and need
Tony's yes.

Symbols: σ is the planted jitter (s); k is the number of cells per event; b is the background rate
(Hz per cell); E is the number of events per recording; λ is the event rate. A "residual" is the
condition median of measured ÷ planted minus predicted ÷ planted.

## Task 1: the correlogram tool against the joint fit (role 7)

**Recordings.** `simulate_coordination` is called with `aim1_one_source.py`'s own arguments and
seed path (1000 + 100·condition + seed). The generator was not re-implemented. All 240 regenerated
recordings match the run record's onset counts (0 of 240 differ).

**Correlogram, as shipped.** For each recording, the tool's `pairs` and `hwhm` give the half-width
at half height. The width is converted to σ through the tool's own calibration: `_sim` on its fast
bench (`bugarach.bench`, regimes baseline_quiet and baseline_busy, seeds 1–24), with σ read by
linear interpolation and NaN off the curve. The curve came out as

    0.05→0.098, 0.1→0.178, 0.15→0.262, 0.2→0.351, 0.3→0.514, 0.36→0.617, 0.46→0.840, 0.6→1.024, 0.8→1.162, 1.0→1.467 s

**That calibration was made on the bench, not on this generator.** The bench differs from Aim 1a's
flat field in participation, event rate and background (silent and hot cells, distractors, an
elevated-rate stretch). Its grid also stops at σ = 1.0 s. It was used as shipped. The table also
gives two other readings of the same width:
- the Gaussian conversion with no calibration, σ = HWHM / (√2·√(2 ln 2)) = HWHM / 1.665;
- a per-condition pooled width.

**Joint fit.** `theory.fit_joint` (hard-core form) on each recording's stored cumulants.

Recovered ÷ planted σ, per recording, median [IQR] (`correlogram_vs_joint.txt`). "off" counts
recordings without a correlogram σ: the width fell below the curve (it reads under 0.05 s), above
it (over 1.0 s), or had no peak. **The IQR is taken over the recordings with a value, so it is
censored where "off" is large.**

| b (Hz) | σ (s) | cells | correlogram, shipped calibration | off | correlogram, Gaussian | joint fit | joint at σ bound |
|---|---|---|---|---|---|---|---|
| 0.01 | 0.05 | 10+ | 1.06 [1.02, 1.10] | 8 below | 1.19 [1.11, 1.26] | 1.33 [0.98, 1.79] | 1 |
| 0.01 | 0.2 | 10+ | 0.97 [0.94, 1.02] | 0 | 1.03 [0.99, 1.07] | 1.07 [1.02, 1.19] | 0 |
| 0.01 | 0.5 | 10+ | 0.92 [0.86, 0.94] | 0 | 1.01 [0.93, 1.03] | 0.98 [0.94, 1.06] | 0 |
| 0.01 | 1.0 | 10+ | 0.86 [0.43, 0.87] | 15 above | 0.97 [0.91, 1.08] | 1.01 [0.98, 1.03] | 0 |
| 0.05 | 0.05 | 10+ | 1.07 [1.02, 1.07] | 15 below | 1.12 [1.09, 1.16] | 0.89 [0.48, 1.64] | 4 |
| 0.05 | 0.2 | 10+ | 0.93 [0.83, 1.01] | 0 | 0.97 [0.87, 1.07] | 0.99 [0.65, 1.13] | 0 |
| 0.05 | 0.5 | 10+ | 0.81 [0.64, 0.88] | 2 below | 0.83 [0.58, 0.96] | 1.04 [0.98, 1.12] | 0 |
| 0.05 | 1.0 | 10+ | 0.42 [0.27, 0.55] | 5 above, 3 below | 0.48 [0.20, 0.84] | 1.01 [0.95, 1.07] | 0 |

Each 10+ row has n = 20 recordings. The 5-cell rows (n = 10 each) are in the `.txt` file. In
brief:
- At 0.01 Hz the correlogram reads 0.84 (σ 0.2 s), 0.72 (0.5 s) and 0.26 (1.0 s) [IQR 0.15–0.65].
- At 0.05 Hz it reads 0.45 (0.2 s), 0.55 (0.5 s) and 0.08 (1.0 s), so it fails there.
- The joint fit's 5-cell IQRs are very wide: 0.28–1.07 at 0.2 s and 0.01 Hz, 0.44–3.62 at 0.2 s
  and 0.05 Hz, and 0.10–3.73 or 0.10–4.06 at 0.05 s.

**Where each works and where it fails** (events of 10+ cells):
- **Small jitter, 0.05–0.2 s: the correlogram is the better estimator.** At 0.05 s it is within
  about 7 % with a tight IQR at both backgrounds. Many widths fall below the calibration's lowest
  point, though (8 of 20 at 0.01 Hz, 15 of 20 at 0.05 Hz), so it reports "under 0.05 s" for those.
  The joint fit does not resolve 0.05 s:
  - IQR 0.98–1.79 at 0.01 Hz and 0.48–1.64 at 0.05 Hz;
  - 1 and 4 recordings at its lower bound.

  At 0.2 s both are near 1. The correlogram's IQR is narrower (0.94–1.02 against 1.02–1.19 at
  0.01 Hz; 0.83–1.01 against 0.65–1.13 at 0.05 Hz).
- **Large jitter, 0.5–1.0 s: the joint fit is the better estimator, and the shipped correlogram
  fails.**
  - At 1.0 s and 0.01 Hz, 15 of 20 widths sit above the calibration's top (σ = 1.0 s), so the
    shipped σ is mostly missing. This is a range limit of the shipped calibration; the Gaussian
    conversion of the same widths reads 0.97 [0.91, 1.08].
  - At 0.05 Hz the correlogram reads low and noisy whatever the conversion: 0.81 at 0.5 s and 0.42
    at 1.0 s. The broad peak sinks into the busier background.
  - The joint fit stays at 0.98–1.04 with IQRs within 0.94–1.12.
- **Calibration bias.** Read through the bench curve, the correlogram is 3–14 % low at 0.2–1.0 s on
  this generator. The uncalibrated Gaussian conversion is closer to 1 at 0.01 Hz (1.03, 1.01,
  0.97). So the bench calibration does not transfer exactly to this generator, as the goal page's
  plan item 1 anticipated.
- **The chapter's claim "recovers jitter where the existing tools cannot"** is not supported for
  0.05–0.2 s, where the existing correlogram tool does as well or better. The joint fit's
  advantage is at 0.5–1 s, and most clearly at 0.05 Hz.

## Task 2: held-out check (role 4)

The run used fresh seeds and changed nothing else. `held_out.py` calls `aim1_one_source.cell` with
the condition index offset by 1000 (generator seeds 101000–105704, surrogate seeds 100007–104711)
and `chance_cell` with seeds 100–199. All of these are disjoint from the original seeds. The run
took 88 s for 240 recordings plus 200 background-only recordings. The full printouts are
`held_out_summary.txt` (held-out) and `original_summary.txt`. The side-by-side table is
`like_for_like.txt`.

Events of 10+ cells. Each cell is original → **held-out**. "2 SE" counts the condition-windows
beyond 2 SE out of 48; about 5.7 are expected if the prediction is exact. "cond. below" counts the
conditions, out of 16, where measured is below predicted, with the two-sided sign-test p.

| b | qty | form | median \|res\| | worst | > 2 SE (P) | cond. below (p) |
|---|---|---|---|---|---|---|
| 0.01 | participants | hard-core | 0.0073 → **0.0115** | 0.037 → **0.056** | 7 (0.34) → **17 (<0.001)** | 12 (0.077) → **12 (0.077)** |
| 0.01 | participants | general | 0.0065 → **0.0096** | 0.041 → **0.055** | 6 (0.51) → **12 (0.009)** | 9 (0.80) → **9 (0.80)** |
| 0.01 | rate | hard-core | 0.0324 → **0.0236** | 0.182 → **0.134** | 17 → **12** | 2 (0.004) → **6 (0.45)** |
| 0.01 | rate | general | 0.0196 → **0.0141** | 0.176 → **0.110** | 5 → **3** | 5 (0.21) → **8 (1.00)** |
| 0.01 | share | hard-core | 0.0175 → **0.0112** | 0.071 → **0.067** | 18 → **8** | 2 (0.004) → **5 (0.21)** |
| 0.01 | share | general | 0.0068 → **0.0084** | 0.065 → **0.071** | 6 → **5** | 3 (0.021) → **10 (0.45)** |
| 0.05 | participants | hard-core | 0.0161 → **0.0209** | 0.106 → **0.132** | 10 (0.052) → **10 (0.052)** | 9 (0.80) → **11 (0.21)** |
| 0.05 | participants | general | 0.0146 → **0.0170** | 0.108 → **0.131** | 7 → **6** | 9 (0.80) → **10 (0.45)** |
| 0.05 | rate | hard-core | 0.0553 → **0.0471** | 0.384 → **0.619** | 7 → **10** | 5 → **6** |
| 0.05 | rate | general | 0.0587 → **0.0504** | 0.441 → **0.613** | 7 → **5** | 5 → **7** |
| 0.05 | share | hard-core | 0.0238 → **0.0296** | 0.284 → **0.195** | 6 → **4** | 6 → **7** |
| 0.05 | share | general | 0.0175 → **0.0202** | 0.289 → **0.199** | 6 → **4** | 8 → **8** |

**Joint fit**, per-condition median ratio to planted, events of 10+ cells, σ ≥ 0.2 s, hard-core
form (`like_for_like.txt`):

| | σ | participants | rate | σ = 0.05 s reads | 5-cell σ ratio |
|---|---|---|---|---|---|
| 0.01 Hz, original | 0.91–1.13 | 0.94–1.02 | 0.96–1.14 | 0.075 s, 1 of 20 at bound | 0.37–2.47 |
| 0.01 Hz, **held-out** | **0.86–1.22** | **0.98–1.06** | **0.94–1.04** | **0.041 s, 3 of 20 at bound** | **0.66–1.31** |
| 0.05 Hz, original | 0.88–1.12 | 0.96–1.14 | 0.73–1.08 | 0.039 s, 4 of 20 at bound | 0.10–3.56 |
| 0.05 Hz, **held-out** | **0.86–1.36** | **0.89–1.16** | **0.87–1.45** | **0.030 s, 7 of 20 at bound** | **0.10–3.71** |

The general form gives the same ranges to within 0.01.

Planted 0.2, 0.5 and 1.0 s read as follows on the held-out record (condition medians pooled as in
`theory.summary`):
- 0.01 Hz: 0.199, 0.506 and 1.071 s;
- 0.05 Hz: 0.206, 0.510 and 1.067 s.

**What held and what did not on fresh seeds:**
- **The participant prediction's median residual held at about 0.01–0.02**: 0.0115 at 0.01 Hz and
  0.0209 at 0.05 Hz, against 0.007 and 0.016 in-sample.
- **Its agreement within noise did not hold at 0.01 Hz.** 17 of 48 condition-windows lie beyond
  2 SE (P < 0.001), against 7 in-sample. 12 of 48 lie beyond under the general form (P = 0.009).
  - The excess comes mostly from 20-cell conditions. Their 5 recordings vary so little that a 1–2 %
    shortfall (measured below predicted) is significant.
  - Combining the two independent records, measured is below predicted in 24 of 32
    condition-backgrounds at 0.01 Hz under the hard-core form (two-sided sign test p = 0.007).
    Under the general form it is 18 of 32 (p = 0.60).
  - **So a high bias of about 1 % in the hard-core participant prediction at 0.01 Hz is now
    established. The general form removes it as a direction (9 of 16 below in both records), but
    not the excess spread beyond 2 SE.**
- **Rate and share at 0.01 Hz**: the hard-core form's upward excess is smaller on the held-out
  record (33 of 48 above, against 43). The general form removes it entirely (18 of 48 above,
  p = 0.11; per condition 8 of 16).
- **The joint fit's ranges widened on fresh seeds**: σ 0.86–1.36 and rate 0.87–1.45 at 0.05 Hz,
  against 0.88–1.12 and 0.73–1.08. **The in-sample ranges should be called in-sample.** σ = 0.05 s
  stays unresolved.

## Task 3: like-for-like statistics (roles 1, 4, 6)

From `theory_check.json` and `theory_check_empirical.json`, printed by `like_for_like.py`
(`like_for_like.txt`, first block). Events of 10+ cells.

- **(a) Per-condition sign test, participants** (16 conditions per background; conditions with
  measured below predicted):
  - 0.01 Hz: hard-core **12 of 16, p = 0.077**; general **9 of 16, p = 0.804**. Role 6 confirmed.
  - 0.05 Hz: 9 of 16 (p = 0.804) under both forms.
- **(b) Per condition-window, participants** (48 per background; condition-windows with measured
  above predicted):
  - 0.01 Hz: hard-core **14 of 48, p = 0.006**; general **19 of 48, p = 0.193**. Confirmed.
  - 0.05 Hz: 17 of 48 (p = 0.059) and 19 of 48 (p = 0.193).
  - The three windows reuse the same recordings, so these 48 are not independent and the
    window-level p is anti-conservative.
- **(c) Rate, 0.01 Hz:**

  | | hard-core | general (empirical) |
  |---|---|---|
  | median absolute residual | **0.0324** | **0.0196** |
  | median signed residual | **+0.0298** | **+0.0129** |
  | worst | 0.182 | 0.176 |
  | above predicted | 43 of 48 (p < 0.001) | **35 of 48, p = 0.002** |
  | per condition, below predicted | 2 of 16 (p = 0.004) | 5 of 16 (p = 0.21) |

  The expected values are confirmed: 0.032 → 0.020 absolute (a 40 % fall) and 0.030 → 0.013
  signed. The held-out record does not reproduce the remaining excess under the general form
  (18 of 48 above, p = 0.11). **The 35 of 48 is therefore not a stable property of the general
  form; it may be a feature of the original seeds.**
- **(d) Rate, 0.05 Hz:**

  | | hard-core | general |
  |---|---|---|
  | median absolute residual | 0.0553 | **0.0587** (slightly worse) |
  | median signed residual | +0.0272 | +0.0124 |
  | worst | 0.384 | 0.441 |
  | above predicted | 30 of 48 (p = 0.11) | 27 of 48 (p = 0.47) |
  | per condition, below predicted | 5 of 16 (p = 0.21) | 5 of 16 (p = 0.21) |

  The general form does not improve rate at 0.05 Hz.
- Share at 0.01 Hz: 0.0175 → 0.0068 absolute, +0.0136 → +0.0027 signed, 41 → 30 of 48 above.

## Task 4: the joint fit at realistic parameter values (role 4)

A synthetic check at σ = 0.105 s (fast gap list) and σ = 0.131 s (slow gap list), with k = 7 and
13 of 33 cells, b = 0.0096 Hz, 45 min and 40 recordings per (list, k). It is not a statement about
the lab's recordings. Printed by `lab_values.py` (`lab_values.txt`). The fast arm uses
`check_real`'s seeds and reproduces `theory_check_real.json` exactly. The slow arm is new
(`theory.REAL` is switched to the slow values in each worker).

**λ used.** The run plants events as a renewal train of the listed gaps, so the rate is set to
λ = 1 / mean gap:
- fast list: 0.00994 Hz, or 35.8 per hour (planted 0.00944 Hz, 25.5 events per recording);
- slow list: 0.01947 Hz, or 70.1 per hour (planted 0.01985 Hz, 53.6 events per recording).

The gap lists hold only gaps between events in the same window, so 1 / mean gap is not an event
rate of the data. The same run's README tabulates 9.7 per hour (fast) and 22.0 per hour (slow), so
these simulations hold about 3.7 and 3.2 times as many events as that. Fewer events would make the
per-recording fit worse, not better. This was not simulated.

**Coordination-rates tool**, ratio to planted. "Measured" is `solve()` on the mean f2 and f3 over
the 40 recordings; the per-recording medians agree to within 0.03.

| list, k | w (s) | rate: measured / page / general | participants: measured / page / general |
|---|---|---|---|
| fast, 7 | 1, 2, 4 | 1.005/1.017/1.003; 1.026/1.064/1.045; 0.989/1.158/1.029 | 0.933/0.931/0.933; 0.940/0.934/0.937; 0.966/0.902/0.957 |
| fast, 13 | 1, 2, 4 | 1.006/1.030/1.015; 1.026/1.066/1.046; 0.998/1.148/1.027 | 0.928/0.923/0.926; 0.941/0.932/0.935; 0.967/0.904/0.957 |
| slow, 7 | 1, 2, 4 | 1.052/1.053/1.046; 1.141/1.145/1.121; 1.365/1.366/1.306 | 0.892/0.896/0.897; 0.881/0.887/0.889; 0.803/0.816/0.823 |
| slow, 13 | 1, 2, 4 | 1.056/1.069/1.061; 1.104/1.142/1.116; 1.235/1.334/1.273 | 0.887/0.887/0.887; 0.892/0.885/0.889; 0.841/0.820/0.830 |

- The general form predicts the tool to within 0.01–0.04 everywhere.
- The hard-core (page) form misses the fast list's 4 s window by 0.15 (rate) and 0.06
  (participants).
- On the slow list's denser train, the tool itself reads rate up to 1.37 times planted and
  participants down to 0.80 at the 4 s window. Both forms predict that.

**Joint fit per recording**, fitted ÷ planted, median [IQR]. Bounds: σ 0.005–5 s, k 2.001–33,
λ 10⁻⁶–1 Hz. No recording hit a k or λ bound; σ hit only its lower bound.

| list, k | form | σ | participants | rate | σ at lower bound | σ within 0.8–1.25× |
|---|---|---|---|---|---|---|
| fast, 7 | page | 1.62 [1.07, 2.04] | 1.06 [1.01, 1.10] | 0.90 [0.82, 0.94] | 4 of 40 | 3 of 40 |
| fast, 7 | general | 1.06 [0.39, 1.53] | 1.01 [0.97, 1.04] | 0.98 [0.86, 1.02] | 8 of 40 | 10 of 40 |
| fast, 7 | Palm | 1.10 [0.50, 1.58] | 1.02 [0.98, 1.05] | 0.97 [0.85, 1.01] | 6 of 40 | 11 of 40 |
| fast, 13 | page | 1.43 [1.08, 1.93] | 1.04 [1.01, 1.11] | 0.92 [0.86, 0.96] | 0 | 10 of 40 |
| fast, 13 | general | 0.88 [0.40, 1.48] | 0.99 [0.97, 1.05] | 0.98 [0.90, 1.03] | 2 of 40 | 9 of 40 |
| fast, 13 | Palm | 0.90 [0.41, 1.52] | 1.00 [0.97, 1.06] | 0.97 [0.90, 1.02] | 1 of 40 | 9 of 40 |
| slow, 7 | page | 0.83 [0.52, 1.10] | 0.99 [0.97, 1.01] | 0.98 [0.94, 0.99] | 1 of 40 | 15 of 40 |
| slow, 7 | general | 0.90 [0.69, 1.20] | 1.00 [0.97, 1.01] | 1.01 [0.97, 1.03] | 0 | 17 of 40 |
| slow, 7 | Palm | 0.97 [0.77, 1.28] | 1.02 [0.99, 1.03] | 0.98 [0.94, 0.99] | 0 | 19 of 40 |
| slow, 13 | page | 1.00 [0.78, 1.22] | 1.02 [0.99, 1.04] | 0.95 [0.90, 0.98] | 0 | 23 of 40 |
| slow, 13 | general | 1.10 [0.84, 1.26] | 1.01 [0.99, 1.03] | 0.98 [0.93, 1.01] | 0 | 19 of 40 |
| slow, 13 | Palm | 1.17 [0.91, 1.30] | 1.03 [1.01, 1.05] | 0.95 [0.90, 0.98] | 0 | 16 of 40 |

**Is the joint fit usable per recording at these values?**
- **Participants and rate: yes.** The per-recording IQRs lie within 0.82–1.11 of planted under
  every form, and within 0.86–1.05 under the general form.
- **Jitter at σ = 0.105 s with the fast list: no.** Under the general form the IQR spans
  0.39–1.53, 2–8 of 40 recordings sit at the 0.005 s floor, and only 9–10 of 40 land within
  0.8–1.25 of planted. The median over recordings is near 1, so the fit is usable only pooled.
- **Jitter at σ = 0.131 s with the slow list: marginal.** The IQR is about 0.7–1.3 (general form),
  nothing hits a bound, and 17–23 of 40 land within 0.8–1.25. Its denser train gives more events
  per recording.
- These figures are at 3–4 times the tabulated event rates (see λ above), so per-recording jitter
  would be worse at the lower rates.

## Task 6: order-detection power at small event counts (roles 4, 6)

`order_power.py` imports `order_limit.py`'s `simulate` and score-sort `indicators`. Settings: 33
cells, 7 and 13 cells per event, M = 1 and 2 templates, r = 1, 2.5 and 5 (σ = 0.2 s), 300
recordings per side. The power is the share of recordings with F above the 95th percentile of 300
order-free recordings of the same size (Table 1.2's method). The full grid is in
`order_power.json`.

**F is discrete at these sizes, so Table 1.2's method is unstable.** The 95th percentile of 300
null draws lands on a lattice value, the realized size is below 5 % (0.013–0.050 here), and float
ties at that value compare arbitrarily. Two extra columns are therefore given:
- the same test against a 3000-recording null;
- an exact-size randomized 5 % test on that null.

The table gives Table 1.2's method / exact 5 %:

| cells | E | r = 1, M=1 | r = 1, M=2 | r = 2.5, M=1 | r = 2.5, M=2 | r = 5, M=1 | r = 5, M=2 |
|---|---|---|---|---|---|---|---|
| 7 | 1 | 0.00 / 0.05 | 0.00 / 0.05 | 0.00 / 0.05 | 0.00 / 0.05 | 0.00 / 0.05 | 0.00 / 0.05 |
| 7 | 2 | 0.00 / 0.05 | 0.00 / 0.06 | 0.00 / 0.08 | 0.00 / 0.05 | 0.00 / 0.06 | 0.00 / 0.06 |
| 7 | 3 | 0.04 / 0.08 | 0.03 / 0.06 | 0.12 / 0.20 | 0.02 / 0.07 | 0.12 / 0.24 | 0.07 / 0.13 |
| 7 | 5 | 0.26 / 0.27 | 0.12 / 0.13 | 0.67 / 0.68 | 0.24 / 0.26 | 0.78 / 0.80 | 0.29 / 0.30 |
| 13 | 1 | 0.00 / 0.05 | 0.00 / 0.05 | 0.00 / 0.05 | 0.00 / 0.05 | 0.00 / 0.05 | 0.00 / 0.05 |
| 13 | 2 | 0.14 / 0.13 | 0.07 / 0.06 | 0.33 / 0.30 | 0.17 / 0.16 | 0.48 / 0.45 | 0.26 / 0.25 |
| 13 | 3 | 0.40 / 0.36 | 0.25 / 0.21 | 0.91 / 0.89 | 0.42 / 0.39 | 0.99 / 0.98 | 0.52 / 0.49 |
| 13 | 5 | 0.86 / 0.85 | 0.37 / 0.36 | 1.00 / 1.00 | 0.68 / 0.67 | 1.00 / 1.00 | 0.78 / 0.77 |

- **E = 1 carries no order information.** The score sort orders a single event perfectly, so F = 1
  under the null as well, and the exact test's power equals its size, 0.05.
- **At 7 cells, E = 2 also has no power.** 21 % of null recordings already reach F = 1, so the 300
  draw threshold is 1.000.
- **Table 1.2's 7-cell, 5-event, one-template entry (0.43) is a low draw.** Repeating its method
  six times (seeds 100–105) gives 0.73, 0.56, 0.66, 0.61, 0.52 and 0.63, depending on the lattice
  value the threshold lands on. The exact-size power on this grid is 0.68. **Table 1.2's entries
  near the lattice's coarse end carry this spread, about ±0.1. They should be recomputed with a
  larger null or an exact-size test before being quoted.**
