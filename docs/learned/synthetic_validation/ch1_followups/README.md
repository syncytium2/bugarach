# Chapter 1 follow-ups demanded by the 2026-10-29 murderboard

Written 2026-10-29 for Chapter 1 (Aim 0) of the synthetic-validation goal
([goal page](../../../goals/synthetic-validation.md)). The review is in
[`docs/reviews/chapter-1-aim0-2026-10-29-round1-roles/`](../../../reviews/chapter-1-aim0-2026-10-29-round1-roles/)
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

## Round 2 follow-ups

Demanded by the round-2 review,
[`docs/reviews/chapter-1-aim0-2026-10-29-round2-roles/`](../../../reviews/chapter-1-aim0-2026-10-29-round2-roles/)
(roles 1, 4, 6, 7 and 11). Written 2026-10-29. **Synthetic only.** As before, no existing script or
record was edited. The new scripts import `theory`, `event_train`, `aim1_one_source`, `order_limit`
and the shipped `bugarach.assess` and `bugarach.simulate`. Rerun from the repository root with the
worktree's venv python (`.venv/Scripts/python.exe`, which now has numpy) and `PYTHONPATH=src`:

    python .../ch1_followups/realistic_counts.py --workers 44 > .../realistic_counts.txt   # tasks 1, 2 (about 3 min)
    python .../ch1_followups/assessor_jitter.py --workers 40 > .../assessor_jitter.txt     # task 3 (under 1 min)
    python .../ch1_followups/order_rounding.py --workers 16 > .../order_rounding.txt       # task 4 (a few min)
    python .../ch1_followups/correlogram_table.py > .../correlogram_table.txt              # task 6 (reads a record)

| file | what |
|---|---|
| `realistic_counts.py` → `.txt`, `.json` | R2 tasks 1 and 2: round 1's Task 4 at the tabulated event counts, and the joint fit given a Poisson or a 20 s hard-core train instead of the true one |
| `assessor_jitter.py` → `.txt`, `.json` | R2 task 3: chance-cluster share and SDs, and a two-part mixture against the assessor's jitter reading |
| `order_rounding.py` → `.txt`, `.json` | R2 task 4: order power and mean F with onsets on the 0.1 s frame |
| `correlogram_table.py` → `.txt` | R2 task 6: the correlogram per recording, pooled as shipped, and Gaussian, beside the joint fit (from `correlogram_vs_joint.json`) |

### R2 task 1: realistic values at realistic event counts (role 4, blocking)

**How the count was lowered.** The train is drawn exactly as `theory._realgap_recording` draws it:
a stationary renewal train of resampled gaps, with a 4000 s run-in. Each event is then kept
independently, with probability p = target rate × mean gap. That gives p = 0.271 for the fast list
(9.7 per hour) and p = 0.314 for the slow list (22.0 per hour).

Independent thinning keeps the pair correlation g_E(τ) exactly, because ρ₂ and λ² both scale by p².
So the close pairs in the list stay close pairs. The "true train" given to the general form is
still `EventTrain.renewal(intervals=gaps)`; only λ falls. The thinned train is again a renewal
train, with CV² = p·CV²_list + (1 − p), and that CV² is the one the fixed-count term uses.

Everything else is as in `lab_values.py`: σ 0.105 / 0.131 s, k = 7 and 13 of 33 cells,
b = 0.0096 Hz, 45 min, 0.1 s frame, 40 recordings per (list, k), on new seeds. The recordings
held these event counts:
- **fast:** mean 7.28 (median 6, range 2–19), against 7.25 expected;
- **slow:** mean 16.46 (median 16, range 2–35), against 16.44 expected.

**Coordination-rates tool**, ratio to planted. "Measured" is `solve()` on the mean f2 and f3 over
the 40 recordings, with its bootstrap SE in brackets (`realistic_counts.txt`). It is followed by the
hard-core (page) prediction and the general (thinned-train) prediction.

| list, k | w | rate: measured (SE) / page / general | participants: measured (SE) / page / general |
|---|---|---|---|
| fast, 7 | 1 s | 0.977 (0.041) / 0.991 / 0.989 | 0.958 (0.013) / 0.946 / 0.946 |
| fast, 7 | 2 s | 1.032 (0.054) / 1.008 / 1.007 | 0.958 (0.015) / 0.966 / 0.965 |
| fast, 7 | 4 s | 1.085 (0.081) / 1.034 / 1.011 | 0.944 (0.022) / 0.966 / 0.977 |
| fast, 13 | 1 s | 0.997 (0.008) / 1.005 / 1.003 | 0.936 (0.005) / 0.938 / 0.938 |
| fast, 13 | 2 s | 1.001 (0.010) / 1.014 / 1.012 | 0.955 (0.005) / 0.962 / 0.961 |
| fast, 13 | 4 s | 1.009 (0.026) / 1.034 / 1.013 | 0.964 (0.016) / 0.964 / 0.975 |
| slow, 7 | 1 s | 1.027 (0.020) / 1.001 / 1.001 | 0.915 (0.007) / 0.925 / 0.924 |
| slow, 7 | 2 s | 1.074 (0.025) / 1.031 / 1.028 | 0.928 (0.009) / 0.945 / 0.944 |
| slow, 7 | 4 s | 1.160 (0.043) / 1.088 / 1.081 | 0.909 (0.013) / 0.933 / 0.932 |
| slow, 13 | 1 s | 1.030 (0.005) / 1.020 / 1.020 | 0.909 (0.003) / 0.914 / 0.914 |
| slow, 13 | 2 s | 1.052 (0.006) / 1.037 / 1.034 | 0.932 (0.004) / 0.941 / 0.940 |
| slow, 13 | 4 s | 1.107 (0.010) / 1.084 / 1.077 | 0.920 (0.005) / 0.933 / 0.932 |

- **The page and general forms now nearly coincide** (within 0.025, and 0.01 at 1–2 s). At these
  rates there are few close pairs per recording, so the at-most-one-event correction matters less.
- **Fast list:** both forms agree with the measurement within 1.5 SE everywhere.
- **Slow list: the tool reads above both predictions in rate, and below them in participants, in
  all 6 of 6 (k, window) cases each.** Each miss is small:
  - rate: 0.010–0.079, or 1.3–2.5 SE;
  - participants: 0.005–0.024, or 1.4–2.6 SE.

  The largest miss is at 4 s, k = 7: rate 1.160 measured against 1.081, participants 0.909
  against 0.932. It runs the same way as round 1's slow arm under the general form, which at
  54 events per recording read 1.365 against 1.306 and 0.803 against 0.823 there. **This is an
  unexplained residual of the general form on the slow list.**

**Joint fit per recording**, fitted ÷ planted, median [IQR]. "Bound" counts recordings within 2 %
of the fit's limits. "Band" counts recordings within 0.8–1.25 of planted, out of 40. Rate is taken
against each recording's own planted rate. Under the true train (general form, thinned renewal,
fixed count):

| list, k | σ | σ at lower bound | σ band | participants (band) | rate (band) |
|---|---|---|---|---|---|
| fast, 7 | 0.05 [0.05, 1.52] | **21** | **2** | 0.97 [0.88, 1.07] (35) | 1.06 [0.75, 1.39] (13) |
| fast, 13 | 0.57 [0.05, 1.17] | 11 | 8 | 0.98 [0.94, 1.00] (39) | 1.00 [0.95, 1.08] (36) |
| slow, 7 | 1.00 [0.80, 1.34] | 4 | 18 | 0.99 [0.94, 1.04] (39) | 1.04 [0.93, 1.18] (30) |
| slow, 13 | 0.97 [0.76, 1.25] | 1 | 16 | 1.00 [0.98, 1.02] (40) | 1.01 [0.98, 1.04] (39) |

No recording hit a k or λ bound, and σ hit only its lower bound. The σ median of 0.05 means 0.005 s
on 0.105 s, the floor.

- **Jitter at the fast list's realistic count: not recoverable per recording.**
  - With 7 cells, more than half of the recordings (21 of 40) sit at the 0.005 s floor, and only 2
    of 40 land within 0.8–1.25. At 25.5 events per recording, round 1 had 8 at the floor and 10 in
    the band.
  - With 13 cells, 11 sit at the floor and 8 land in the band.
- **Jitter at the slow list's realistic count: about as marginal as at 54 events.** The IQR is
  about 0.76–1.34, 1–4 recordings sit at the floor, and 16–18 of 40 land in the band (round 1:
  17–19).
- **Participants stay usable per recording**: IQRs within 0.88–1.07, and 35–40 of 40 in the band.
- **Rate is usable with 13 cells** (36 and 39 of 40 in the band). **With 7 cells it is not on the
  fast list** (IQR 0.75–1.39, 13 of 40 in the band); on the slow list it is 30 of 40.

### R2 task 2: the fit without knowing the train (roles 4, 6)

These are the same recordings, fitted as an analyst who does not know the train would fit them.
The fits are (`realistic_counts.txt`, the rows other than `true`):
- **page:** the 20 s hard core, in `theory.py`'s form (`train=None`, the form `theory.check` runs);
- **hardcore20:** `EventTrain.hard_core(20)` through the general machinery, with the tool's
  surrogate;
- **poisson:** `EventTrain.poisson()`, without the fixed-count term;
- **poisson_fixed:** the same, with the fixed-count term at the expected count.

| list, k | train given | σ (bound; band) | participants (band) | rate (band) |
|---|---|---|---|---|
| fast, 7 | true | 0.05 [0.05, 1.52] (21; 2) | 0.97 [0.88, 1.07] (35) | 1.06 [0.75, 1.39] (13) |
| fast, 7 | 20 s hard core (page) | 0.23 [0.05, 1.68] (18; 4) | 0.98 [0.89, 1.08] (35) | 1.04 [0.74, 1.37] (14) |
| fast, 7 | Poisson | 0.05 [0.05, 1.44] (22; 2) | 0.96 [0.86, 1.06] (34) | 1.08 [0.75, 1.41] (12) |
| fast, 13 | true | 0.57 [0.05, 1.17] (11; 8) | 0.98 [0.94, 1.00] (39) | 1.00 [0.95, 1.08] (36) |
| fast, 13 | 20 s hard core (page) | 0.80 [0.13, 1.32] (9; 8) | 0.99 [0.95, 1.02] (39) | 0.97 [0.93, 1.06] (36) |
| fast, 13 | Poisson | 0.51 [0.05, 1.13] (13; 7) | 0.96 [0.92, 0.99] (40) | 1.02 [0.96, 1.09] (38) |
| slow, 7 | true | 1.00 [0.80, 1.34] (4; 18) | 0.99 [0.94, 1.04] (39) | 1.04 [0.93, 1.18] (30) |
| slow, 7 | 20 s hard core (page) | 0.97 [0.77, 1.30] (4; 17) | 0.98 [0.93, 1.04] (39) | 1.03 [0.93, 1.17] (31) |
| slow, 7 | Poisson | **0.55 [0.28, 0.92]** (6; 11) | **0.91** [0.86, 1.00] (38) | **1.11** [1.02, 1.29] (27) |
| slow, 13 | true | 0.97 [0.76, 1.25] (1; 16) | 1.00 [0.98, 1.02] (40) | 1.01 [0.98, 1.04] (39) |
| slow, 13 | 20 s hard core (page) | 0.95 [0.73, 1.22] (2; 16) | 1.00 [0.98, 1.01] (40) | 1.00 [0.97, 1.04] (39) |
| slow, 13 | Poisson | **0.62 [0.33, 0.83]** (5; 9) | **0.93** [0.92, 0.96] (40) | **1.08** [1.06, 1.14] (39) |

`hardcore20` matches `page` to within 0.02 everywhere. `poisson_fixed` matches `poisson` to within
0.04.

- **At realistic counts, the 20 s hard core loses almost nothing against the true train.**
  - Participants and rate agree with the true-train fit to within 0.03.
  - σ is the same on the slow list.
  - On the fast list σ reads somewhat higher (median 0.23 against the floor at 7 cells; 0.80
    against 0.57 at 13 cells), but it is unresolved either way.
  - Round 1's 1.62× and 1.43× hard-core jitter bias came from the denser trains of 25–54 events
    per recording. It does not appear at 7–16 events.
- **A Poisson train is the wrong default.** On the slow list, whose intervals rarely fall under
  4 s (5th percentile 7.1 s), it reads:
  - σ at 0.55–0.62 of planted (11 and 9 of 40 in the band, against 18 and 16);
  - participants 0.91–0.93;
  - rate 1.08–1.11.

  On the fast list it is close to the true train, because σ is unresolved there anyway, apart
  from participants about 0.02 lower.
- **So the oracle input matters little at these counts if the analyst assumes a hard core, and a
  great deal if the analyst assumes Poisson.** This is not the Palm-from-detected-events run that
  role 4 asked for (#6); that was not done.

### R2 task 3: why the assessor's jitter reading goes flat (roles 4, 7, 11)

**The existing records could not answer this.** `aim1_one_source.json`'s background-only arm keeps
only clusters per minute, and its event rows keep only each recording's `jit_obs`. Two new sets of
recordings were therefore used (`assessor_jitter.py`):
- **40 new background-only recordings per background**, simulated exactly as `chance_cell` does,
  on new seeds.
- **The 240 Aim 1a recordings, regenerated** through `aim1_one_source`'s own seed path. Onset
  counts match the record in all 240, and `jit_obs` matches it to 0 s in every recording and K.

Clusters come from the shipped `_coact_count` and `_clusters`. A copy of `_clusters`' loop also
returns each cluster's gathered onsets; its SDs are asserted equal to the shipped function's,
cluster by cluster. `jit_obs` is also checked against `assess_coactivity` itself.

A cluster is labelled an **event cluster** when at least half of its gathered onsets are planted
onsets, and a **chance cluster** otherwise.

**(i) Chance share.** Chance clusters per minute are predicted as c = 60 q (1 − q)², with
q = P(Binomial(33, 1 − e^(−b·1 s)) ≥ K), 1 s bins and merge_bins 2 (`theory.chance_clusters_per_min`).
The planted events per minute are e = E/45. Assuming each event gives exactly one cluster, the
**chance share is c / (c + e)**.

| b | K | c predicted / measured (per min) | chance share, E = 15 / 45: predicted | measured (10+ cells, pooled) |
|---|---|---|---|---|
| 0.01 | 3 | 0.256 / 0.249 | 0.43 / 0.20 | 0.26–0.29 (predicted pooled 0.32) |
| 0.01 | 4 | 0.019 / 0.016 | 0.05 / 0.02 | 0.02–0.04 (0.04) |
| 0.01 | 6 | 0.0002 / 0.001 | 0.00 | 0.00 |
| 0.05 | 3 | 7.97 / 8.01 | 0.96 / 0.89 | 0.92–0.93 (0.92) |
| 0.05 | 4 | 3.86 / 3.89 | 0.92 / 0.79 | 0.85 (0.86) |
| 0.05 | 6 | 0.284 / 0.277 | 0.46 / 0.22 | 0.28–0.37 (0.34) |

Per condition, the predicted share matches the label-based share to within about 0.05. The
exceptions are σ = 1 s at 0.05 Hz with K = 6 (0.46 → 0.61 and 0.22 → 0.34, 10-cell events) and
some 0.01 Hz, K = 3 conditions. Wide events do not give exactly one cluster each.

**(ii) The jitter of chance clusters alone** (background-only recordings; per-cluster SD median
[IQR], and `jit_obs`, the median over recordings):

| b | K | per-cluster SD | jit_obs | clusters |
|---|---|---|---|---|
| 0.01 | 3 | 0.380 [0.251, 0.591] | 0.397 s | 448 |
| 0.01 | 4 | 0.374 [0.294, 0.518] | 0.377 s (26 of 40 recordings had a cluster) | 29 |
| 0.01 | 6 | 0.475 | one recording had one cluster | 1 |
| 0.05 | 3 | 0.733 [0.580, 0.877] | **0.733 s** | 14 425 |
| 0.05 | 4 | 0.680 [0.549, 0.802] | **0.680 s** | 6 996 |
| 0.05 | 6 | 0.596 [0.505, 0.695] | **0.600 s** | 498 |

**(iii) The mixture.** The reading is predicted as the median of a mixture of two parts:
- **chance clusters**, with weight c/(c + e): their empirical SDs from (ii);
- **event clusters**, with weight e/(c + e): the SD of k truncated-Gaussian onsets, N(0, σ²) kept
  within ±1.5 s, plus one uniform onset on ±1.5 s from each other cell with probability
  1 − e^(−3b), rounded to 0.1 s, and kept only if at least K onsets are gathered.

The mixture is pooled as Figure 1.1 D/H pools (10+ cells, four conditions, equal weight). In the
table, each cell is the Figure's measured value (median `jit_obs` over the 20 recordings) / the
mixture's prediction.

| b | K | σ = 0.05 | 0.2 | 0.5 | 1.0 s |
|---|---|---|---|---|---|
| 0.01 | 3 | 0.158 / 0.139 | 0.258 / 0.239 | 0.473 / 0.485 | 0.705 / 0.688 |
| 0.01 | 4 | **0.068 / 0.067** | **0.226 / 0.222** | **0.486 / 0.500** | **0.725 / 0.736** |
| 0.01 | 6 | 0.068 / 0.067 | 0.229 / 0.218 | 0.485 / 0.501 | 0.711 / 0.742 |
| 0.05 | 3 | **0.715 / 0.711** | **0.711 / 0.713** | **0.717 / 0.717** | **0.733 / 0.738** |
| 0.05 | 4 | **0.644 / 0.642** | **0.646 / 0.640** | **0.657 / 0.652** | **0.692 / 0.698** |
| 0.05 | 6 | 0.430 / 0.399 | 0.461 / 0.429 | 0.565 / 0.568 | 0.683 / 0.719 |

**What matches:**
- **At 0.01 Hz, K = 4** (Figure 1.1 D: 0.07/0.23/0.49/0.72 s), the mixture reproduces the reading
  to within 0.015 s. With almost no chance clusters (2–4 %), the reading is simply the SD of a
  Gaussian truncated at ±1.5 s.
  - That truncation is the ceiling: 0.743 s for σ = 1 s.
  - It also explains why the assessor tracks the identity line up to 0.5 s.
- **At 0.05 Hz, K = 3 and 4** (Figure 1.1 H: 0.64–0.73 s), the mixture reproduces the reading to
  within 0.006 s.
  - 85–93 % of clusters are chance clusters, so the median is the chance clusters' own SD: 0.73 s
    at K = 3 and 0.68 s at K = 4, the background-only values of (ii).
  - The flat reading is therefore the median of the chance clusters, as role 7 said, and the
    chance-cluster rate predicts the share.

**What does not match as well:**
- **At 0.05 Hz, K = 6** (0.43–0.68 s), the mixture is 0.03 s low at σ ≤ 0.2 s and 0.036 s high at
  1 s. The shape is right, a rise only from 0.5 s, but there are two compensating misses:
  - The measured chance share at small σ is 0.28–0.29, below the predicted 0.34.
  - Real event clusters at 0.05 Hz are wider than the model: at K = 6 and σ ≤ 0.2 s, their
    measured median SD is 0.33–0.38 s against the model's 0.31–0.36 s. The uniform-background term undercounts the
    background onsets that the gather catches, and the cluster centre is not the event time.
- **At σ = 1 s, the event part runs high**:
  - At 0.01 Hz, K = 6, 10-cell events, the reading is 0.58–0.62 against the mixture's 0.74. A
    10-cell event spread over ±2 s reaches 6 cells in one bin only when its onsets happen to bunch,
    so the clusters that form are narrower than the truncated Gaussian. The model has no such
    selection.
  - Wide events also split into more than one cluster, which is the share miss in (i).
- **The 0.05 Hz event-cluster model is about 0.1 s too narrow at small σ** (K = 3: 0.408 measured
  against 0.309 modelled). It does not show in the reading only because chance clusters dominate
  there.

### R2 task 4: frame rounding in the order test (roles 6, 7)

Each event gets a continuous time (uniform on 100–200 s, so its phase against the frame is
uniform). Its onsets are rounded with the production quantizer `bugarach.simulate._quantize(…,
0.1)`. F is scored on the same draw with and without rounding.

**Ties.** `order_limit.pair_matrices` scores sign(t_j − t_i), so a tied pair adds 0 to D, neither
cell leading, and still adds 1 to the co-participation count n. Ties therefore pull F toward 0.

**Power**: one template, r = 2.5, 13 of 33 cells, score sort, 2000 recordings per point. Each test
uses an order-free null of the same size, rounded the same way. The table gives Table 1.2's method
(300-draw null) / the exact 5 % test (3000-draw null) (`order_rounding.txt`).

| σ | E | unrounded | rounded | mean F unrounded → rounded | null mean F | tied pairs (signal / null) |
|---|---|---|---|---|---|---|
| 0.105 s | 3 | 0.873 / 0.909 | **0.985 / 0.992** | 0.797 → 0.768 | 0.611 → 0.546 | 9.9 % / 25.9 % |
| 0.105 s | 5 | 1.000 / 1.000 | 1.000 / 1.000 | 0.759 → 0.740 | 0.478 → 0.443 | 10.0 % / 25.9 % |
| 0.2 s | 3 | 0.934 / 0.918 | **0.983 / 0.970** | 0.799 → 0.785 | 0.610 → 0.580 | 5.2 % / 13.9 % |
| 0.2 s | 5 | 1.000 / 1.000 | 1.000 / 1.000 | 0.759 → 0.751 | 0.479 → 0.464 | 5.2 % / 14.0 % |

- **Rounding does not cost power here. It raises it at E = 3**: 0.91 → 0.99 at σ = 0.105 s, and
  0.92 → 0.97 at 0.2 s (exact test).
  - Without a template, all of an event's onsets sit within about ±σ, so 26 % of null pairs tie
    and the null F falls by 0.065. Under the template, only 10 % tie and F falls by 0.03.
  - The null shrinks more than the signal does.
- **E = 5 is saturated either way.**
- The unrounded σ = 0.2 s, E = 3 power (0.92) matches `order_power.txt`'s 0.89 (exact test) within
  noise.

**Mean F with many events** (10 of 33 cells, 200 events, one template, 200 recordings, paired):

| δ, σ | F unrounded → rounded | change (SE) | tied pairs |
|---|---|---|---|
| **δ = σ = 0.1 s (r = 1)** | 0.5037 → 0.4776 | **−5.2 % (0.08 %)** | 19.6 % |
| δ = 0.263, σ = 0.105 s (r = 2.5) | 0.7525 → 0.7367 | −2.1 % (0.05 %) | 9.9 % |
| δ = σ = 0.2 s (r = 1) | 0.5029 → 0.4963 | −1.3 % (0.06 %) | 9.9 % |
| δ = 0.5, σ = 0.2 s (r = 2.5) | 0.7538 → 0.7494 | −0.6 % (0.03 %) | 5.2 % |

**The unkept "about 9 %" does not reproduce.** At δ = σ = 0.1 s, the measured drop is 5.2 %, with
ties scored as here. The r-scaling of F breaks once ties appear: at fixed r = 1, the drop is 5.2 % at
σ = 0.1 s and 1.3 % at 0.2 s.

### R2 task 5: the Kreuz normalization through `synfire_scan._indicator` (role 7)

**Not run. PySpike is not installed** in any Python on this workstation: not in the main checkout's
`.venv`, the worktree's `.venv`, `venvs/coordination-share`, `venvs/surrogate-screen`, or the
system and uv Pythons 3.11–3.14. As the task allowed, the check was not attempted. F_Kreuz =
F (k − 1)/(N − 1), with N = trains scored, therefore stays derived, not run.

### R2 task 6: the correlogram as shipped (role 6)

Extracted from `correlogram_vs_joint.json` by `correlogram_table.py`; no new simulation. The table
gives recovered ÷ planted jitter:
- **per recording, shipped calibration:** median [IQR] over the recordings with a value. Off counts
  are given as below the curve / above it / no peak, and the IQR is censored where they are large.
- **pooled as shipped:** pairs summed over each condition's 5 recordings before taking the width,
  as `measure_jitter_correlogram.main()` pools. It gives median [range] over the conditions, and
  how many conditions fell off the curve.
- **per recording, Gaussian:** HWHM / 1.665, with no calibration.
- **joint fit:** per recording, hard-core form.

| b | σ (s) | cells | per recording, shipped cal. (off b/a/np) | pooled as shipped (conditions off) | per recording, Gaussian | joint fit (at bound) |
|---|---|---|---|---|---|---|
| 0.01 | 0.05 | 10+ | 1.06 [1.02, 1.10] (8/0/0) | 1.04 [1.02–1.06] (2 of 4) | 1.19 [1.11, 1.26] | 1.33 [0.98, 1.79] (1) |
| 0.01 | 0.2 | 10+ | 0.97 [0.94, 1.02] (0) | 0.96 [0.89–1.00] (0 of 4) | 1.03 [0.99, 1.07] | 1.07 [1.02, 1.19] (0) |
| 0.01 | 0.5 | 10+ | 0.92 [0.86, 0.94] (0) | 0.92 [0.90–0.97] (0 of 4) | 1.01 [0.93, 1.03] | 0.98 [0.94, 1.06] (0) |
| 0.01 | 1.0 | 10+ | 0.86 [0.43, 0.87] (0/15/0) | – (4 of 4 above the curve) | 0.97 [0.91, 1.08] | 1.01 [0.98, 1.03] (0) |
| 0.05 | 0.05 | 10+ | 1.07 [1.02, 1.07] (15/0/0) | – (4 of 4) | 1.12 [1.09, 1.16] | 0.89 [0.48, 1.64] (4) |
| 0.05 | 0.2 | 10+ | 0.93 [0.83, 1.01] (0) | 0.96 [0.85–1.02] (0 of 4) | 0.97 [0.87, 1.07] | 0.99 [0.65, 1.13] (0) |
| 0.05 | 0.5 | 10+ | 0.81 [0.64, 0.88] (2/0/0) | **0.89 [0.83–1.11]** (0 of 4) | 0.83 [0.58, 0.96] | 1.04 [0.98, 1.12] (0) |
| 0.05 | 1.0 | 10+ | 0.42 [0.27, 0.55] (3/5/0) | **0.94 [0.88–0.99]** (2 of 4) | 0.48 [0.20, 0.84] | 1.01 [0.95, 1.07] (0) |

The 5-cell rows are in `correlogram_table.txt`. The record keeps the pooled reading only after the
calibration, so no pooled Gaussian conversion can be extracted.

- **Pooled as shipped, the correlogram does not fail at 0.05 Hz.** It reads 0.89 at 0.5 s and 0.94
  at 1.0 s, against 0.81 and 0.42 per recording. At 1.0 s, though, 2 of 4 conditions are off the
  curve.
- **At 0.01 Hz and 1.0 s, the shipped reading is missing only because the calibration ends at
  1.0 s.** The Gaussian conversion reads 0.97.
- **Per recording, the joint fit is the better estimator from 0.5 s at 0.05 Hz.** Elsewhere the
  correlogram (pooled, or Gaussian at 0.01 Hz) is as good. The joint fit has no pooled
  counterpart here.

## Round 3 follow-ups

These answer the round-3 blind review,
[`docs/reviews/chapter-1-aim0-2026-10-29-round3-roles/`](../../../reviews/chapter-1-aim0-2026-10-29-round3-roles/)
(roles 4, 6 and 7). Written 2026-10-29. **Synthetic only.** Task 1 reads `windows.csv` for two
parameter values per stream, the baseline window length and the events per window. No recording's
onsets are analysed, and nothing here is a claim about the lab's recordings.

As before, no existing script or record was edited. The new scripts import `theory`,
`event_train`, `aim1_one_source`, `order_limit`, `membership_limit`, `kendall_w`,
`realistic_counts`, `order_rounding` and the shipped `bugarach.assess`, `bugarach.assembly`,
`bugarach.simulate` and `tools/measure_coordination_rates`. Rerun them from the repository root
with the worktree's venv python and `PYTHONPATH=src`. Wall times are on the lab workstation:

    python .../ch1_followups/window_counts.py --workers 32 > .../window_counts.txt          # task 1 (190 s)
    python .../ch1_followups/chance_bursty.py --workers 12 > .../chance_bursty.txt          # task 2 (7 s)
    python .../ch1_followups/order_rounding_cells.py --workers 14 > .../order_rounding_cells.txt  # task 3 (about 1 min)
    python .../ch1_followups/membership_repeat.py --workers 40 > .../membership_repeat.txt  # tasks 4 and 8 (127 s)
    python .../ch1_followups/dependence_null.py > .../dependence_null.txt                   # task 5 (20 s; reads records)
    python .../ch1_followups/assessor_null.py --workers 44 > .../assessor_null.txt          # task 6 (455 s)
    python .../ch1_followups/pooled_path.py > .../pooled_path.txt                           # task 7 (seconds; reads records)

| file | what |
|---|---|
| `window_counts.py` → `.txt`, `.json` | R3 task 1: 20-minute recordings with E = 1, 2, 4, 8, 16 events fixed per recording; the joint fit and the tool per recording |
| `chance_bursty.py` → `.txt`, `.json` | R3 task 2: chance clusters per hour on the bursty background, beside the flat background and the formula |
| `order_rounding_cells.py` → `.txt`, `.json` | R3 task 3: order power and null mean with frame rounding at σ 0.105/0.131 s, 7/13 cells; tie-corrected exact null mean |
| `membership_repeat.py` → `.txt`, `.json` | R3 tasks 4 and 8: the assembly test given a repeated assembly, and which statistic rejects, at 200 and the shipped 1000 surrogates |
| `dependence_null.py` → `.txt`, `.json` | R3 task 5: nulls for the condition-window counts that keep the three windows' dependence |
| `assessor_null.py` → `.txt`, `.json` | R3 task 6: the assessor's `jit_null` and `jit_excess` at the shipped 1000 surrogates, on the 240 Aim 1a recordings |
| `pooled_path.py` → `.txt`, `.json` | R3 task 7: the tool's shipped pooled reporting path beside the per-recording path |

### R3 task 1: a 20-minute window, with the count fixed per recording (role 4, blocking)

**The parameter values.** These are read from `windows.csv`, 66 windows per stream:

| stream | window length | events per window: mean | quantiles 0/10/25/50/75/90/100 % | windows with 0 events | per hour |
|---|---|---|---|---|---|
| fast | 17–20 min (median 20) | 3.21 | 0 / 0 / 0 / 1 / 4 / 9 / 23 | 28 | 9.72 |
| slow | 17–20 min (median 20) | 7.29 | 0 / 0 / 0 / 2 / 7.75 / 27.5 / 49 | 25 | 22.05 |
| combined | 17–20 min (median 20) | 8.36 | 0 / 0 / 0 / 3 / 11 / 29 / 52 | 21 | 25.30 |

These match the reviewer's figures. The per-hour rates match the 9.7 and 22.0 used in round 2.
Round 2's 45-minute recordings at 7.3 and 16.5 events were therefore realistic in rate, but not
in window length or count per window.

**How the recordings were made.**
- Length T = 1200 s, with a 5 s margin; 33 cells; b = 0.0096 Hz; 0.1 s frame.
- σ is 0.105 s for the fast list and 0.131 s for the slow list; k = 7 and 13 cells per event.
- E = 1, 2, 4, 8 or 16 events, **fixed** per recording; 40 recordings per (stream, k, E).
- The train is round 2's: a stationary renewal train of resampled list gaps, thinned with
  p_E = min(1, E ÷ the list's expected count). It is then conditioned on exactly E events by
  redrawing until the count is E (2.8–20 draws on average).
- On the fast list, E = 16 exceeds the list's own 11.8 events per window. There p = 1, and the
  conditioning alone sets the count.

**How they were fitted.** The general form is given `thinned_train(gaps, p_E)` with
`n_events = E` ("true"). The 20 s hard core is fitted in `theory.py`'s form ("page"). Conditioning
on the count beyond the fixed-count term is not modelled; that is an approximation. The tool's
estimate is `solve()` on each recording's own f2, f3 at each window.

**Joint fit, general form given the true train**, fitted ÷ planted, median [IQR]. For σ, the
bracket gives (recordings at the 0.005 s floor; recordings within 0.8–1.25 of planted, of 40).
For participants and rate it gives the number within 0.8–1.25, of 40. No σ fit reached the 5 s
bound.

| stream, k | E | σ | participants | rate |
|---|---|---|---|---|
| fast, 7 | 1 | 0.05 [0.05, 1.78] (22; 1) | 0.89 [0.66, 1.22] (13) | 1.67 [0.60, 2.89] (4) |
| fast, 7 | 2 | 0.85 [0.05, 3.30] (19; 0) | 1.14 [0.92, 1.41] (19) | 0.76 [0.36, 1.49] (7) |
| fast, 7 | 4 | 0.11 [0.05, 1.32] (19; 3) | 0.97 [0.88, 1.06] (30) | 1.07 [0.81, 1.29] (19) |
| fast, 7 | 8 | 0.79 [0.26, 2.12] (8; 4) | 1.01 [0.97, 1.09] (40) | 1.01 [0.85, 1.16] (25) |
| fast, 7 | 16 | 0.41 [0.05, 1.61] (11; 2) | 0.97 [0.92, 1.05] (40) | 1.00 [0.93, 1.09] (38) |
| fast, 13 | 1 | 0.30 [0.05, 1.84] (17; 5) | 1.00 [0.93, 1.08] (30) | 1.01 [0.66, 1.24] (16) |
| fast, 13 | 2 | 0.63 [0.05, 1.23] (14; 9) | 0.97 [0.91, 1.06] (40) | 1.09 [0.84, 1.21] (23) |
| fast, 13 | 4 | 0.84 [0.05, 1.70] (12; 7) | 0.98 [0.94, 1.03] (39) | 1.02 [0.95, 1.12] (35) |
| fast, 13 | 8 | 0.99 [0.39, 1.42] (5; 7) | 1.00 [0.97, 1.02] (39) | 0.99 [0.94, 1.05] (38) |
| fast, 13 | 16 | 0.73 [0.26, 1.66] (4; 5) | 0.98 [0.95, 1.07] (39) | 1.04 [0.95, 1.08] (39) |
| slow, 7 | 1 | 1.04 [0.04, 3.00] (11; 4) | 1.00 [0.75, 1.88] (12) | 1.27 [0.32, 2.54] (3) |
| slow, 7 | 2 | 0.87 [0.04, 2.40] (13; 3) | 1.10 [0.89, 1.30] (25) | 0.87 [0.55, 1.55] (9) |
| slow, 7 | 4 | 0.85 [0.04, 1.80] (14; 6) | 1.00 [0.89, 1.07] (36) | 1.04 [0.83, 1.22] (20) |
| slow, 7 | 8 | 0.87 [0.04, 1.36] (11; 8) | 1.02 [0.94, 1.05] (39) | 1.02 [0.86, 1.12] (31) |
| slow, 7 | 16 | 1.15 [0.62, 1.43] (5; 13) | 1.00 [0.96, 1.05] (40) | 1.02 [0.95, 1.06] (40) |
| slow, 13 | 1 | 0.77 [0.04, 1.70] (16; 3) | 1.06 [0.91, 1.23] (26) | 0.84 [0.60, 1.30] (10) |
| slow, 13 | 2 | 0.89 [0.04, 1.95] (11; 5) | 1.04 [0.98, 1.09] (40) | 0.99 [0.90, 1.14] (34) |
| slow, 13 | 4 | 1.12 [0.71, 1.73] (2; 9) | 1.00 [0.98, 1.04] (40) | 1.02 [0.91, 1.07] (37) |
| slow, 13 | 8 | 0.93 [0.57, 1.48] (2; 8) | 1.00 [0.98, 1.04] (40) | 0.98 [0.93, 1.02] (40) |
| slow, 13 | 16 | 1.04 [0.70, 1.41] (0; 12) | 1.02 [1.00, 1.05] (40) | 0.97 [0.92, 0.99] (40) |

The fit returned an answer for 799 of 800 recordings; the exception is one fast, k = 7, E = 1
recording with f2 ≤ 0 at every window. Under the true train, k reached a bound in 4 recordings
and λ in 1, all at E = 1.

**The 20 s hard core ("page")** is within 0.03 of the true train in participants and rate at
every E ≤ 8. It is also nearly the same in σ on the slow list. There is one exception: **the fast
list at E = 16, where the train is not thinned.** There the hard core reads:
- σ at 1.32 (k = 7) and 1.45 (k = 13) of planted, against 0.41 and 0.73 under the true train;
- rate at 0.92 and 0.96, against 1.00 and 1.04.

This is round 1's dense-train bias returning. All rows are in `window_counts.txt`.

**The coordination-rates tool per recording**, participants ÷ planted, median [IQR] (within
0.8–1.25, of 40). Refusals, where f2 or f3 is not positive, are shown where there are any. The
table gives the 1 s window; the 2 and 4 s windows, and the rate, are in `window_counts.txt`.

| stream, k | E = 1 | 2 | 4 | 8 | 16 |
|---|---|---|---|---|---|
| fast, 7 | 0.88 [0.78, 1.16] (18; refused 1) | 0.92 [0.85, 1.05] (34) | 0.94 [0.89, 1.00] (38) | 0.95 [0.90, 0.97] (40) | 0.92 [0.91, 0.94] (40) |
| fast, 13 | 0.92 [0.89, 0.97] (40) | 0.95 [0.91, 0.99] (40) | 0.93 [0.90, 0.95] (40) | 0.93 [0.91, 0.95] (40) | 0.92 [0.90, 0.93] (40) |
| slow, 7 | 0.98 [0.76, 1.15] (21) | 0.97 [0.90, 1.11] (37) | 0.94 [0.88, 1.00] (39) | 0.92 [0.89, 0.97] (40) | 0.90 [0.88, 0.92] (40) |
| slow, 13 | 0.97 [0.87, 1.03] (35) | 0.93 [0.90, 0.96] (40) | 0.91 [0.89, 0.94] (40) | 0.91 [0.89, 0.93] (40) | 0.90 [0.89, 0.91] (40) |

The tool refuses only at E = 1 with 7 cells:
- fast list: 1, 3 and 4 of 40 at 1, 2 and 4 s;
- slow list: 0, 0 and 5 of 40.

At E = 0, which is 28 of the 66 fast windows and 25 of the 66 slow ones in the parameter table,
there is nothing to estimate.

- **When participants become readable per recording (within 0.8–1.25 in at least 38 of 40):**
  - **With 13 cells, from E = 2** for the joint fit, on both lists (39–40 of 40).
  - **With 7 cells, from E = 8.** At E = 4 it is 30 (fast) and 36 (slow) of 40.
  - The tool's 1 s solve gets there one step earlier: from E = 1 at 13 cells on the fast list,
    E = 2 at 13 cells on the slow list, and E = 4 at 7 cells (38 and 39 of 40).
  - But the tool's participants sit at 0.90–0.95 of planted throughout, the low bias the
    hard-core form predicts. The joint fit's median is 0.97–1.02 from E = 4.
- **At a realistic median window (1 fast or 2 slow events), therefore:**
  - 7-cell events are not readable per recording: 12–25 of 40 in the band for the joint fit,
    18–37 for the tool.
  - 13-cell events are borderline to readable: the joint fit has 30 of 40 at E = 1 (fast), and
    40 of 40 at E = 2 (slow).
- **Rate needs more events than participants:** within the band in at least 35 of 40 from E = 4
  with 13 cells, and only at E = 16 with 7 cells.
- **Jitter is not recoverable per recording at any E tested.** At best, 12–13 of 40 recordings
  land within 0.8–1.25 (slow list, E = 16). At E ≤ 2, 11–22 of 40 sit at the 0.005 s floor. This
  is worse than round 2's 45-minute result.

### R3 task 2: chance clusters on an over-dispersed background (role 4)

**The bursty background.** It is invoked as
`simulate_coordination(..., bg_burst_shape=(1.547, 1.388), bg_burst_bin_sec=(300.0, 60.0))`
(`src/bugarach/simulate.py`, documented in `docs/generator.md`). Each cell's rate is multiplied,
per 300 s bin and per 60 s bin, by independent Gamma(shape, 1/shape) draws with mean 1.
**The draws are made per cell, so bursts are not shared across cells.** Note that
`bench.MEASURED_BURST_SHAPE` is (1.770, 1.439), not the (1.547, 1.388) in `generator.md`; the
documented pair was used, as asked.

An extra arm, not asked for, adds `bg_rate_shape = bench.MEASURED_RATE_SHAPE` (0.291): Gamma
heterogeneity of the cells' own rates, mean kept at b. The flat formula also assumes equal rates.

**How it was run.** Background only, 33 cells, 45 min, b = 0.0096 Hz, **400 recordings per arm**
(100 were asked for; 400 cost seconds and give K = 5 and 6 a usable count). Clusters come from
the shipped `_coact_count` and `_clusters`. The prediction is 60 q (1 − q)² per minute.

Variance ÷ mean of each cell's counts, pooled over cells with at least one onset, at
30/60/120/300 s:
- flat: 1.00 / 1.00 / 1.00 / 1.00;
- bursty: **1.50 / 2.02 / 2.29 / 3.53**;
- bursty + rate: 3.20 / 5.45 / 6.68 / 11.90.

`generator.md` gives 1.87/2.76/3.04/4.44 for the bursty mode, but on cells with 10 or more
events. At b = 0.0096 Hz the Gamma-mixed Poisson is less over-dispersed, because the extra
variance grows with the mean count.

**Chance clusters per hour.** The table gives the mean, with the exact Poisson 95 % CI of the
pooled count:

| K | flat formula | flat background | bursty | bursty + rate heterogeneity |
|---|---|---|---|---|
| 3 | 13.72 | 14.14 [13.72, 14.57] | 13.42 [13.01, 13.84] | 11.26 [10.88, 11.65] |
| 4 | 0.983 | 0.990 [0.881, 1.109] | 0.990 [0.881, 1.109] | 0.787 [0.690, 0.894] |
| 5 | 0.054 | 0.067 [0.041, 0.103] | 0.070 [0.043, 0.107] | 0.037 [0.018, 0.066] |
| 6 | 0.0024 | 0 [0, 0.012] | 0.010 [0.002, 0.029] | 0.003 [0.000, 0.019] |

**Where the smallest K under 1 per hour changes (flat formula).** K = 3 gives exactly 1 chance
cluster per hour at b = 0.00382 Hz, **K = 4 at b = 0.00964 Hz**, and K = 5 at b = 0.01793 Hz.

- **Temporal burstiness of this kind does not change the chance-cluster rate.** The bursty and
  flat backgrounds agree with each other, and with the formula, within about 5 % at K = 3 and
  within their CIs at K = 4 and 5. At K = 6 the bursty arm has 3 clusters in 300 hours against an
  expected 0.7, too few to say more.
  - The reason is that the generator draws each cell's bursts independently. Coincidences across
    cells then depend only on each cell's marginal rate per 1 s bin, which the mode leaves
    unchanged.
  - A burst shared across cells (population bursts) would raise the rate. That is a different
    model, and it was not run here.
- **Unequal cell rates lower it**, by about 20 % at K = 3–4 here. There are two reasons. A cell's
  chance of at least one onset in a bin is concave in its rate. And a count over cells with unequal
  probabilities is less variable than a binomial with the same mean, so its upper tail is thinner. So the flat formula is, if anything, conservative for this
  generator.
- **The chapter's K = 4 at b = 0.0096 Hz sits exactly on the threshold.** The flat formula gives
  0.98 per hour there, and the K = 4 threshold is crossed at 0.00964 Hz. Any background a few
  percent busier gives more than 1 chance cluster per hour at K = 4, so K = 5 becomes the smallest
  K under 1 per hour.

### R3 task 3: frame rounding at the chapter's cells (role 4)

This extends `order_rounding.py`, and imports its `draw`, `rounded`, `f_and_ties`, `run_many`
and `exact_power`. The grid is σ = 0.105 and 0.131 s; 7 and 13 of 33 cells; r = 1 and 2.5;
M = 1 and 2 templates; E = 2, 3, 5. There are 1000 recordings per point and a 2000-recording
null per (σ, k, E), rounded the same way as each test. The test is the exact-size randomized
5 % test.

**The tie-corrected exact null mean.** The `kendall_w` reduction carries over to tied onsets:
- The denominator ΣE C(k, 2) is still fixed.
- The label-swap argument still gives tied scores zero weight.
- Within a shared event, x = sign(t₂ − t₁) is still the sign of y = u₁ − u₂, and x = y = 0 on a
  tie.

So E[F] = E[x · sign(y + S)], with S the sum of the other E − 1 events' contributions. With
ties, the laws of (x, y) and of u depend on σ ÷ frame and are no longer the rank lattice. Here
they are estimated from 400 000 quantized model events per (σ, k) and then convolved exactly.
Run on untied events, the same code reproduces `F_exact` to within 0.0006.

**Null mean F** (SE about 0.002):

| σ, k | E | simulated unrounded / F_exact | simulated rounded / tie-corrected | tied pairs |
|---|---|---|---|---|
| 0.105, 7 | 2 / 3 / 5 | 0.866 / 0.865; 0.770 / 0.768; 0.637 / 0.639 | **0.689 / 0.686; 0.642 / 0.638; 0.559 / 0.559** | 26 % |
| 0.105, 13 | 2 / 3 / 5 | 0.745 / 0.743; 0.611 / 0.611; 0.479 / 0.478 | 0.625 / 0.625; 0.545 / 0.545; 0.442 / 0.442 | 26 % |
| 0.131, 7 | 2 / 3 / 5 | 0.864 / 0.865; 0.768 / 0.768; 0.635 / 0.639 | 0.721 / 0.722; 0.665 / 0.665; 0.575 / 0.577 | 21 % |
| 0.131, 13 | 2 / 3 / 5 | 0.746 / 0.743; 0.612 / 0.611; 0.478 / 0.478 | 0.651 / 0.651; 0.560 / 0.561; 0.454 / 0.452 | 21 % |

**Power (exact 5 %), unrounded → rounded, beside the mean shifts.** The table shows the
one-template case; M = 2 and r = 1 at 0.131 s are in `order_rounding_cells.txt`.

| σ, k, r | E | power | signal mean F shift | null mean F shift |
|---|---|---|---|---|
| 0.105, 7, 2.5 | 2 / 3 / 5 | 0.06→0.66 / 0.18→0.73 / 0.69→0.92 | −0.066 / −0.053 / −0.034 | −0.178 / −0.128 / −0.078 |
| 0.105, 13, 2.5 | 2 / 3 / 5 | 0.31→0.92 / 0.90→0.99 / 1.00→1.00 | −0.047 / −0.030 / −0.020 | −0.119 / −0.066 / −0.037 |
| 0.131, 7, 2.5 | 2 / 3 / 5 | 0.07→0.56 / 0.20→0.65 / 0.74→0.90 | −0.053 / −0.040 / −0.026 | −0.143 / −0.102 / −0.060 |
| 0.131, 13, 2.5 | 2 / 3 / 5 | 0.29→0.85 / 0.93→0.99 / 1.00→1.00 | −0.037 / −0.022 / −0.014 | −0.095 / −0.053 / −0.024 |
| 0.105, 7, 1 | 2 / 3 / 5 | 0.06→0.24 / 0.10→0.32 / 0.29→0.46 | −0.129 / −0.101 / −0.063 | −0.178 / −0.128 / −0.078 |
| 0.105, 13, 1 | 2 / 3 / 5 | 0.12→0.35 / 0.35→0.53 / 0.78→0.89 | −0.089 / −0.052 / −0.032 | −0.119 / −0.066 / −0.037 |
| 0.105, 13, 2.5, M = 2 | 2 / 3 / 5 | 0.17→0.63 / 0.36→0.60 / 0.69→0.87 | −0.043 / −0.025 / −0.015 | −0.119 / −0.066 / −0.037 |

- **Rounding raises power at every one of the 48 points, or leaves it saturated.** It never
  lowers it. The gain is largest at E = 2 (for example 0.06 → 0.66 with 7 cells at r = 2.5,
  σ = 0.105 s).
- **The reason is that the null falls more than the signal.** An order-free event's onsets all sit
  within about ±σ, so 21–26 % of null pairs tie, against 8–10 % of signal pairs at r = 2.5. The
  null mean drops 2–3 times as far as the signal mean. At r = 1, 15–19 % of signal pairs tie and
  the two shifts are closer, so the gain is smaller.
- **Do not use the untied exact null mean with tied onsets.** `F_exact` is off by up to 0.18
  (0.865 against 0.689 at σ = 0.105 s, 7 cells, E = 2). **The tie-corrected mean matches the
  rounded simulation in all 12 cases**: at most 0.004 apart, which is 2.1 SE at worst.
- **A test whose null is rounded the same way is still valid.** This is the generator's model of
  rounding: a uniform frame phase, and onsets i.i.d. Gaussian under the null. A null that keeps
  real event shapes would be needed before reading the power gain as real.

### R3 task 4: membership detection given a repeat (role 4)

This uses `membership_limit.py`'s model at M = 1000 (reuse E/M = 0.045): 33 cells, 10 per event,
45 events, with each event's assembly index kept. There are 1000 recordings. The p-values come
from the shipped `pvalues_margin` and `pvalues_uniform`, read by `AssemblyResult.verdict`, at 200
surrogates (as before) and at the shipped 1000, on the same membership matrices. "Both-null
rejection" is the verdict `structure-beyond-rate`.

- **Share with at least one repeated assembly:** 0.621 [0.591, 0.651]. The birthday formula
  gives 0.634.
- **Repeats per recording:** 0 in 379, 1 in 375, 2 in 163, 3 in 68, 4 in 14, 5 or more in 1.

| recordings | n | both-null rejection, 200 / 1000 surrogates | any flag, 200 / 1000 |
|---|---|---|---|
| all | 1000 | 0.094 [0.077, 0.114] / 0.092 [0.076, 0.112] | 0.211 / 0.218 |
| ≥ 1 repeat | 621 | **0.140 [0.115, 0.170] / 0.137 [0.112, 0.166]** | 0.308 / 0.319 |
| 0 repeats | 379 | **0.018 [0.009, 0.038] / 0.018 [0.009, 0.038]** | 0.053 / 0.053 |
| exactly 1 repeat | 375 | 0.061 / 0.051 | 0.179 / 0.189 |
| ≥ 2 repeats | 246 | 0.260 [0.209, 0.318] / 0.268 [0.217, 0.327] | 0.504 / 0.516 |

Random participation (task 8's size arm, 400 recordings, 1000 surrogates) gives a both-null
rejection rate of 0.015 and any flag of 0.070.

- **Without a repeat, the test is at its false-positive rate** (0.018 both-null against 0.015 for
  random participation). As expected, it sees nothing when no assembly recurs.
- **With one repeat it rejects 5–6 % of the time; with two or more, 26–27 %.** At reuse 0.045,
  detection is driven by the recordings that happen to hold several repeats.
- **The surrogate count does not matter here.** 200 and 1000 give the same rates within 0.01.

### R3 task 5: nulls that keep the windows' dependence (role 4)

The chapter reads its counts over 48 condition-windows against independent windows:
Binomial(48, 0.118) for "beyond 2 SE", and Binomial(48, ½) for "measured above predicted". Here
the null "the prediction is exact" keeps the three windows' dependence. Each null replays the
per-recording values (measured ÷ planted, all three windows of a recording kept together, from
`aim1_one_source.json` and `aim1_one_source_heldout.json`) against the matching `theory_check`
record's prediction. There are 20 000 replicate experiments, each scored exactly as the record
was. Two nulls are used:
- **MVN:** each condition's 3-window vector is drawn from a normal with the prediction as mean
  and the condition's own sample covariance; 5 recordings are drawn per condition.
- **BOOT:** each recording's vector is standardized within its condition. Each condition then
  draws 5 distinct vectors from the pool of 80, rescales them by its own SD and centres them on
  the prediction. This keeps the empirical shape as well as the covariance. Its limit is that a
  vector standardized within 5 recordings cannot exceed 1.79 SD, so the tails are lighter than
  the population's.

The mean correlation between windows within a condition is 0.49–0.77 for 1 s with 2 s, 0.24–0.57
for 1 s with 4 s, and 0.46–0.79 for 2 s with 4 s.

| count in the chapter | observed | binomial (independent): mean ± SD, P | MVN: mean ± SD, P | BOOT: mean ± SD, P |
|---|---|---|---|---|
| held-out, hard core, 0.01 Hz, participants beyond 2 SE | 17 of 48 | 5.7 ± 2.2, **< 0.0001** | 5.7 ± 2.8, **0.0005** | 6.9 ± 2.9, **0.002** |
| held-out, general, 0.01 Hz, participants beyond 2 SE | 12 of 48 | 5.7 ± 2.2, 0.009 | 5.6 ± 2.8, **0.026** | 6.9 ± 2.9, **0.070** |
| original, general, 0.01 Hz, rate above predicted | 35 of 48 | SD 3.5, two-sided 0.002 | SD 4.1, **0.011** | SD 4.1, **0.042** |
| held-out, general, 0.01 Hz, rate above predicted | 18 of 48 | SD 3.5, 0.11 | SD 4.5, **0.23** | SD 4.1, **0.64** |
| original, hard core, 0.01 Hz, rate above predicted | 43 of 48 | SD 3.5, < 0.0001 | SD 4.2, < 0.0001 | SD 4.1, < 0.0001 |
| original, hard core, 0.01 Hz, participants above | 14 of 48 | SD 3.5, 0.006 | SD 4.3, 0.024 | SD 4.5, 0.043 |

The other rows, the 0.05 Hz rows and the per-condition sign counts are in `dependence_null.txt`.

- **Dependence widens the counts' spread by about 25–30 %** (SD 2.7–2.8 against 2.2 for "beyond
  2 SE", and 4.1–4.7 against 3.5 for signs). The mean of the "beyond 2 SE" count stays at 5.7
  under MVN. Under BOOT it is 6.1–7.0, because the per-recording values are not normal.
- **The 17 of 48 holds under every null** (P ≤ 0.002). The hard-core form's participant miss on
  the held-out record is real.
- **The weaker findings soften:**
  - The general form's 12 of 48 goes from p = 0.009 to 0.026 (MVN) and 0.070 (BOOT).
  - The 35 of 48 rate sign count goes from 0.002 to 0.011 and 0.042.
  - The chapter should quote these with the dependence-aware p, or as "suggestive".
- **The per-condition sign counts (one sign per condition) need no correction.** Their p-values
  are unchanged under MVN, for example 12 of 16 at p = 0.077 against 0.074. This confirms that
  the chapter's one-sign-per-condition tests were already the right unit.

### R3 task 6: the assessor's own jitter null (roles 6 and 7)

**How it was run.** The 240 Aim 1a recordings were regenerated through `aim1_one_source`'s seed
path, as `assessor_jitter.py` does. `assess_coactivity` was then run at its **shipped settings**:
`n_surrogates` = 1000 (the signature default, and the MATLAB default), the default `rng_seed`,
the whole 45 min, K = 3, 4, 6. `jit_obs` matches the record exactly (0 difference over 708
recording-K pairs).

**The readings.** Events of 10+ cells, pooled as Figure 1.1 D/H (20 recordings per cell). Each
cell gives the median `jit_obs` / `jit_null` / `jit_excess` in seconds. `jit_defined` was True
everywhere.

| b, K | chance-cluster SD, background only (R2 task 3) | σ = 0.05 | 0.2 | 0.5 | 1.0 s |
|---|---|---|---|---|---|
| 0.01, 3 | 0.380 | 0.158 / 0.439 / −0.276 | 0.258 / 0.440 / −0.188 | 0.473 / 0.440 / +0.024 | 0.705 / 0.440 / +0.257 |
| 0.01, 4 | 0.374 | 0.068 / 0.404 / −0.330 | 0.226 / 0.406 / −0.171 | 0.486 / 0.408 / +0.082 | 0.725 / 0.408 / +0.293 |
| 0.01, 6 | 0.475 (1 cluster) | 0.068 / 0.403 / −0.339 | 0.229 / 0.388 / −0.128 | 0.485 / 0.374 / +0.112 | 0.711 / 0.367 / +0.294 |
| 0.05, 3 | 0.733 | 0.715 / 0.727 / −0.014 | 0.711 / 0.728 / −0.020 | 0.717 / 0.728 / −0.011 | 0.733 / 0.727 / +0.005 |
| 0.05, 4 | 0.680 | 0.644 / 0.671 / −0.022 | 0.646 / 0.673 / −0.025 | 0.657 / 0.672 / −0.020 | 0.692 / 0.671 / +0.016 |
| 0.05, 6 | 0.596 | 0.430 / 0.595 / −0.164 | 0.461 / 0.596 / −0.134 | 0.565 / 0.597 / −0.033 | 0.683 / 0.595 / +0.087 |

- **At 0.05 Hz, `jit_null` is the background-only chance-cluster SD.** It agrees within
  0.006–0.009 s at every K and σ, and does not depend on σ.
- **At 0.01 Hz, `jit_null` runs 0.03–0.06 s above the background-only value at K = 3–4**
  (0.40–0.44 against 0.37–0.38). The likely reason is that the shifted copies also carry the
  planted onsets, which, scattered by the shift, add to the background.
- **`jit_excess` does not rescue the flat reading at 0.05 Hz.** Because `jit_null` is constant
  in σ, `jit_excess` is just `jit_obs` minus a constant. At K = 3 and 4 it moves only 0.02–0.04 s
  as σ goes from 0.05 to 1 s, the same flat curve as `jit_obs`, shifted to about 0.
  - At K = 6 it rises from −0.16 to +0.09 s, which is as much as `jit_obs` already rises (0.43 →
    0.68).
  - At 0.01 Hz it crosses 0 near σ = 0.5 s and is negative below. It reads as "tighter or looser
    than chance", not as a jitter.
  - **The tool offers no other null-corrected jitter reading.**
- **What `adapt.generator_params` does with it** (`src/bugarach/adapt.py`, the "tightness"
  block, about lines 220–224):
  - When `jit_defined` is True and `jit_obs` is finite, it sets the generator's `jitter_sec`
    **to `jit_obs` itself**. `jit_null` and `jit_excess` appear only in the note text.
  - Otherwise it sweeps the jitter.
  - So at a busy background (0.05 Hz, K = 3–4) it would plant about 0.65–0.73 s of jitter
    whatever the true σ was. That is the chance clusters' SD, not the events'.

### R3 task 7: the tool's shipped pooled reporting path (role 6)

There is no new simulation; the readings are computed from the run records' per-recording
cumulants. Per condition-window, three readings are compared with the prediction:
- **per-rec:** `solve()` per recording, then the median of 5. This is `theory.check`'s "meas",
  the reading the chapter validates; it matches the record exactly.
- **pooled:** `solve()` on the condition's mean f2 and f3, a ratio of means. This is
  `theory.check`'s "pooled" column.
- **shipped:** `measure_coordination_rates.per_recording()` as `summarize()` calls it. k comes
  from the window-weighted pooled f3/f2, and λ from each recording's own f2 at that k, then the
  median. With equal-length recordings the pooled k equals the pooled `solve()`'s k, so the
  participant readings of pooled and shipped are identical.

Events of 10+ cells, 48 condition-windows per background. Each cell gives the median |residual|,
the median signed residual, and above of 48 (sign p).

| record, form, b, quantity | per-rec (chapter) | pooled | shipped |
|---|---|---|---|
| original, hard core, 0.01, participants | 0.0073, −0.0063, 14 (0.006) | 0.0077, −0.0065, 11 (< 0.001) | = pooled |
| original, hard core, 0.01, rate | 0.0324, +0.0298, 43 (< 0.001) | 0.0240, +0.0217, 39 (< 0.001) | 0.0219, +0.0211, 37 (< 0.001) |
| original, general, 0.01, participants | 0.0065, −0.0023, 19 (0.19) | 0.0055, −0.0027, 19 (0.19) | = pooled |
| original, general, 0.01, rate | 0.0196, +0.0129, 35 (0.002) | 0.0171, **+0.0048**, 31 (0.06) | 0.0160, +0.0048, 29 (0.19) |
| held-out, hard core, 0.01, participants | 0.0115, −0.0090, 16 (0.029) | 0.0089, −0.0066, 12 (0.001) | = pooled |
| held-out, hard core, 0.01, rate | 0.0236, +0.0165, 33 (0.013) | 0.0203, +0.0172, 30 (0.11) | 0.0233, +0.0176, 35 (0.002) |
| held-out, general, 0.01, participants | 0.0096, −0.0054, 18 (0.11) | 0.0062, −0.0034, 17 (0.06) | = pooled |
| held-out, general, 0.01, rate | 0.0141, −0.0035, 18 (0.11) | 0.0102, −0.0047, 19 (0.19) | 0.0111, −0.0026, 20 (0.31) |
| original, general, 0.05, rate | 0.0587, +0.0124, 27 (0.47) | 0.0530, −0.0008, 24 (1.0) | 0.0443, +0.0040, 26 (0.67) |
| held-out, general, 0.05, rate | 0.0504, +0.0048, 26 (0.67) | 0.0620, +0.0036, 25 (0.89) | 0.0549, +0.0018, 26 (0.67) |

The remaining 0.05 Hz rows are in `pooled_path.txt`.

**Median of ratios minus ratio of means, for rate.** This involves no prediction. The table gives
the median [IQR] over the 48 condition-windows.

| record, b | per-rec − pooled | per-rec − shipped |
|---|---|---|
| original, 0.01 | +0.0061 [−0.0010, +0.0170] | +0.0031 [−0.0075, +0.0177] |
| original, 0.05 | +0.0077 [−0.0220, +0.0193] | +0.0051 [−0.0242, +0.0391] |
| held-out, 0.01 | −0.0009 [−0.0086, +0.0089] | −0.0031 [−0.0158, +0.0084] |
| held-out, 0.05 | −0.0082 [−0.0474, +0.0375] | −0.0027 [−0.0362, +0.0341] |

For participants the gap is −0.001 (IQR within ±0.011).

- **On the shipped path the prediction does about as well or better.** Participant |residuals|
  are within 0.004 of the per-recording ones, often smaller, and of the same sign.
  - The hard-core form's low participant bias at 0.01 Hz is, if anything, more one-sided on the
    pooled path: 11 and 12 of 48 above, against 14 and 16.
  - The general form's original-record rate bias falls from +0.013 to +0.005, as `derivation.md`
    §7.2 reported (+0.005).
- **The median-of-ratio versus ratio-of-means gap is not a stable +0.008.** On the original
  record it is +0.006 (0.01 Hz) and +0.008 (0.05 Hz), consistent with §7.2. On the held-out record
  it is −0.001 and −0.008. Its IQR spans zero in every case. So it is noise at five recordings,
  not a fixed bias of the median.
- **The validation therefore transfers to the shipped reporting path** for these simulated
  conditions. The one caveat: the shipped path reports a single pooled participant count, so it
  has no per-recording spread to compare.

### R3 task 8: which assembly statistic rejects, at the shipped surrogate count (roles 6 and 7)

**How it was run.** Same model and script as task 4 (`membership_repeat.py`), at the shipped
1000 surrogates (`assess_assemblies`' default). `AssemblyResult.verdict` tests each null with two
statistics: the pair co-participation dispersion and the leading eigenvalue (`stat_eigen`), each
at α/2 = 0.025 (Bonferroni). The table gives the share of recordings in which, per null, only the
dispersion, only the eigenvalue, or both are below 0.025.

| arm (reuse E/M) | n | margin null: disp only / eig only / both / either | uniform null: disp only / eig only / both / either | verdicts: none / uniform-only / margin-only / both |
|---|---|---|---|---|
| M = 1000 (0.045) | 1000 | 0.086 / 0.021 / 0.061 / 0.168 | 0.054 / 0.078 / 0.010 / 0.142 | 782 / 50 / 76 / 92 |
| M = 150 (0.3) | 400 | 0.310 / 0.005 / 0.588 / 0.902 | 0.155 / 0.203 / 0.393 / 0.750 | 31 / 8 / 69 / 292 |
| M = 45 (1) | 400 | 0 / 0 / 1.000 / 1.000 | 0 / 0 / 1.000 / 1.000 | 0 / 0 / 0 / 400 |
| random participation | 400 | 0.022 / 0.015 / 0.010 / 0.048 | 0.020 / 0.018 / 0.000 / 0.037 | 372 / 9 / 13 / 6 |

- **Under the margin null, the dispersion statistic carries low reuse.** At reuse 0.045, the
  dispersion rejects in 0.147 of recordings (alone or with the eigenvalue), against 0.082 for the
  eigenvalue. At 0.3, the dispersion rejects in 0.90 and the eigenvalue adds almost nothing alone
  (0.005).
- **Under the uniform null, the eigenvalue carries more of it.** At 0.045 it rejects alone in
  0.078 against 0.054 for the dispersion. At 0.3, both statistics contribute (0.20 eigenvalue
  only, 0.16 dispersion only).
  - So at low reuse, the both-null verdict usually rests on the dispersion for the margin null
    and on the eigenvalue for the uniform null.
  - The two statistics rarely agree within the uniform null (0.010 both).
- **At reuse 1, both statistics reject under both nulls in every recording.**
- **Size holds.** Under random participation, each null rejects ("either") in 0.048 and 0.037 of
  recordings, and both-null in 0.015. That is consistent with the Bonferroni design.
- Detection at reuse 0.045 is 0.092 both-null (0.218 any flag) at 1000 surrogates, against
  membership_limit.json's 8 of 60 (0.13) and 16 of 60 at 200. Within noise.
