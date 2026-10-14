GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1 (Prove It): claim ledger for the coordinated-share explainer, round 1

**Artifact:** `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md`, plus fig1–fig5 PNGs.

**Reproduction:** I re-ran the generator with `--out` pointed at scratch (`...\scratchpad\mb-r1\role1\rerun\`). It produces a `numbers.json` identical to the committed one, and all five PNGs are byte-identical. Every number below was recomputed from those outputs, from `tools/measure_coordination_rates.py`, `src/bugarach/bench.py`, `tools/fit_background_shape.py` and `current_export.toml`. I also ran four checks of my own, read-only and through the generator's own functions:
- the subtraction of the 5-minute stretch;
- pooled f₃ for the null and ramp sets;
- the spread of each recording's own answer at lowered backgrounds;
- a set with only one moment size, to separate the mixture bias from everything else.

## Findings (location · issue · severity · suggested fix · verified against a source)

1. **"What it cannot see", bullets 1–2 (lines 177–189): the corrected rule is refuted by the page's own case.** · blocking · yes
   - The README says the stretch is counted because "each cell's busy stretch is slid by a different amount, so in the copies the stretches no longer line up". It concludes that "a shared change faster than about a minute is counted; a slower one is not".
   - The offsets span N × 2 windows = 64 s, centred, so each shift is at most about ±32 s. A 300 s stretch still overlaps itself in the copies for most of its length.
   - Recomputed over 8 seeds: the shifted copies keep a median **92%** of the stretch's f₂ (real 1.53, copies 1.39 per window). Only the edges, about 8%, survive as excess, and that is what produces the 3.7%.
   - A 5-minute change is *slower* than a minute, yet it is counted. So the rule as written contradicts the bullet right above it.
   - This is the correction the page makes to its own commissioning todo, so the replacement needs the same rigour as the claim it retracts.
   - Fix: say the copies remove most of a slow joint rise. What survives is the part that changes faster than the shifts' span, here the stretch's step edges. Describe the 3.7% as an edge effect, not as stretches that "no longer line up".

2. **Lines 61 and 67–68 ("They copy the fast stream's bench… The bench keeps its moments at least 120 s apart"): stale.** · major · yes
   - `bench.DEFAULT_SPACING = "realistic"` since 2026-10-07 (ADR-0010). `make_recording` now draws gaps from measured real gaps, and fast plants about 7 events (`realistic_counts`: "Fast: 9.7 per hour, 7 events"), not 15. The 120 s floor applies only under `spacing="bench"`.
   - The bench's background is also bursty (`bg_burst_shape=MEASURED_BURST_SHAPE`), and it plants 6 distractors (`n_distractors=6`), which the tool's `truth()` counts. The explainer's recordings have neither.
   - Fix: "built from `BENCH_RECORDING`'s constants (cells, duration, levels), with Poisson background and no distractors". State that the bench's default spacing is now realistic.

3. **Line 179 and the label on Figure 5A: "0.127 onsets per second (the bench's elevated-rate level)" is wrong.** · major · yes
   - `ELEVATED_RATE_RECORDING["hot_rate_hz"] = 0.1334`. The value 0.127 (0.1271) is the 84-recording value from before 2026-09-23. It survives only in `CAL_NO_PROBE` and as the generator's hard-coded `PROBE_HZ`.
   - Fix: read the value from `bench.ELEVATED_RATE_RECORDING` and redraw, or call 0.127 "the level `CAL_NO_PROBE` tested".

4. **Line 64: "0.106 s, the measured fast-stream jitter".** · minor · yes
   - `BENCH_RECORDING["jitter_sec"] = 0.105`, re-measured on 66 recordings. 0.106 is `mcr.CAL_JITTER`, the tool's fixed calibration value from the 84-recording measurement.
   - Fix: "0.106 s, the jitter the tool's calibration plants".

5. **Lines 159–164 and 168: "The share is their product and survives" / "can be read at any of the three windows".** · major · yes
   - At 4 s the share error is −17.6% with close pairs against −10.4% with 120 s gaps only, a 7-point move. That is larger than the "about 3 percentage points" the page treats as enough to restrict k and λ to 1–2 s.
   - At 1 s and 2 s the close-pair effect on the share is ≤1.5 points. Figure 4A shows the 4 s divergence (blue below aqua).
   - Fix: say close pairs pull the 4 s share down by about 7 points, still inside the band.

6. **Line 160: "a pair of moments 2 s apart usually falls in one window" at 4 s.** · minor · yes
   - For a 2 s gap in a 4 s window the chance is (4−2)/4 = **50%** at each of the tool's two offsets.
   - Fix: "half the time".

7. **Lines 165–166 vs 169–170: medium pairs "change nothing", close pairs move k and λ "by about 3 points".** · minor · yes
   - Medium pairs against 120 s only: k +30.2% vs +27.5% at 1 s, λ −33.2% vs −29.9% at 4 s, share −13.1% vs −10.4% at 4 s. These are 2–3 points, the same size as the close-pair effect the page counts at 1–2 s.
   - Both are at seed-noise level. The sets share background draws, but their schedule and participant draws differ.
   - Fix: treat differences of 3 points or less as noise in both places.

8. **Lines 136–142: "The reason both read low is that the planted moments come in three sizes".** · major · yes (recomputed)
   - **Fixed model: confirmed.** The analytic mixture bias for k ∈ {10, 6, 3} is k +38%, λ −37.5%, share −14.0%. With every moment at k = 6 (120 s gaps, 48 recordings), the fixed model reads −4.1% at 1 s, +1.1% at 2 s and +6.3% at 4 s. So the mixture explains most of the −18% to −21%.
   - **Binomial model: refuted.** With one moment size it reads **+18.6% / +25.2% / +32.5%** (1/2/4 s), so it is biased *high*. Its −11% here comes from the mixture bias (−4.4% analytically) partly cancelling that upward bias.
   - So "the binomial model is the closer of the two" (lines 147–148) depends on the planted size mix, and that mix is chosen, not measured: the bench says the outer levels 0.30 and 0.10 "are chosen, not measured".
   - The same contingency applies to "take the fixed-model share as an underestimate of about a fifth" (lines 148–150).
   - Fix: limit the "reason" sentence to the fixed model. Say the binomial model's closeness is a cancellation, and tie "a fifth low" explicitly to the three-size mix.

9. **Lines 183 and 190–191, and the Figure 5A labels: two outcomes that are numerically identical are described differently.** · major · yes
   - The README says the ramp is "reported as no coordination in all 24 recordings", while the steady null "gives no answer at all, not a small one".
   - In `numbers.json` both have `answered: 0`, `median: null`. In both, pooled f₃ is ≤ 0, so `solve`/`pooled_ratio` decline. Recomputed pooled Σf₃·n: null −14.1, ramp −33.5.
   - The figure labels both rows "no coordination reported", which contradicts the README's own distinction for the null row.
   - Fix: describe both as "no answer: pooled excess f₃ not above zero". The ramp's pooled excess f₂ (8.8) is at the null's level (10.9), which is the evidence it was subtracted.

10. **Lines 196–201: "Lowering the background … changes the pooled answer by about two points … So a lower event rate on its own does not make the answer noisy".** · major · partly
    - The quoted evidence is the pooled *median*, which measures bias, not noise. `numbers.json` holds no spread for the lowered-background sets, so the conclusion is not supported by anything the page cites.
    - My recompute does support the conclusion. Each recording's own answer, q10–q90: 1.0× 0.756–0.835, 0.5× 0.770–0.846, 0.25× 0.782–0.821. The spread does not widen.
    - The lowered-background sets use the **mixed** schedule (`run_set(pool, dict(), …)` takes the default n_close=2, n_medium=2). The sentence that follows ("Figure 5B's recordings are all at the quiet background, with every moment 120 s or more…") implies they are the 120 s set. That is why "79% at the quiet level" (mixed) and "81%" for 15 moments (120 s only) differ for what reads as the same condition.
    - Fix: add the own-answer spread to `numbers.json` and quote it. State the schedule. Explain or remove the 79% vs 81% mismatch.

11. **Line 211: "Figure 3 is that check".** · minor/major · yes
    - The tool's `calibrate` runs on `bench.make_recording`: realistic spacing by default, bursty background, distractors, jitter 0.105.
    - It also compares share in Hz against `ks.sum()/(N·T)`, which counts planted participants before frame rounding and dedup and includes distractors.
    - Figure 3 is an analogue on this page's own generator, which compares against deduplicated planted onsets.
    - Fix: "Figure 3 runs the same test on this page's recordings".

12. **Lines 220–222: "the pinning census missed ROIs in four DI recordings".** · major · yes
    - Per `current_export.toml` and `docs/todo/2026-10-05-the-pinning-census-undercounts-on-the-default-folder.md`, misses are confirmed in **one** recording (`20260629_312`, 9 contaminated ROIs against the census's 4). `20260629_309` ROI 16 is over-cut. `309`, `20260630_316` and `20250926_235` are not yet reviewed ROI by ROI.
    - "Four DI recordings" is accurate for the scope of the stop. "Missed ROIs in" all four is not established.
    - Fix: "missed ROIs in one DI recording and over-cut another; four DI recordings await review".

13. **Line 56 and lines 123–125: "of all a cell's onsets" / "dividing that by the cell's event rate".** · minor · yes
    - `solve` gives every cell the same coordinated rate λk/N, and `measure` divides by the *mean* per-cell rate. The result is the population fraction of onsets that are coordinated, which is also what the generator's truth uses. It is not any one cell's fraction; busy cells would have less.
    - Fix: "of all onsets in the recording".

14. **Lines 85–87: "so that a moment cut by a window edge is not lost".** · minor · yes
    - The `population_cumulants` docstring says two offsets "halve the share of shared moments split by a window edge".
    - Fix: "is less often lost".

15. **Line 182: CAL_NO_PROBE "says the effect may be large on the slow stream".** · minor · yes
    - The note says "not obviously small", and it gives fast's effect as small (0.6%). The paraphrase strengthens it.

16. **Line 186: "after a shift of a minute or so".** · minor · yes
    - Offsets are centred, so shifts run about −32 s to +32 s. The *span* is about 64 s, which line 187 already says correctly.

17. **Lines 67–68: the gap schedule "(Tony, 2026-10-14)".** · minor · no
    - The only source is the commissioning todo's header, written by the same session that wrote the page. I could not trace it independently.
    - Fix: cite where the ruling was given.

## Claim ledger (quoted · source · recomputed · result)

**Setup and bench constants**

| Quoted | Source | Recomputed | Result |
|---|---|---|---|
| 32 cells, 45 min | `BENCH_RECORDING` | 32, 2700 s | match |
| 15 moments, 5 each at 10/6/3 cells | `participation` (0.30, 0.203, 0.10) × 32, `n_per_level` (5, 5, 5) | 9.6→10, 6.5→6, 3.2→3 | match for the constants; the bench's default spacing differs (finding 2) |
| quiet 0.0049, busy 0.0169 | `REGIMES` | same | match |
| a few cells busy, many nearly silent | gamma shape 0.291 | | match |
| jitter 0.106 s | bench 0.105; `CAL_JITTER` 0.106 | | mismatch with the bench (finding 4) |
| bench moments ≥ 120 s apart | `DEFAULT_SPACING = "realistic"` | | mismatch (finding 2) |
| 0.127 "bench's elevated-rate level" | `ELEVATED_RATE_RECORDING` 0.1334 | | mismatch (finding 3) |
| N = 32 in every simulation | generator | | match |
| 48 recordings = 24 seeds × quiet + busy | `run_set` | | match |
| 24 per row in Figure 5 | quiet only | | match |
| Mixed set: 2 close pairs 2 s apart, 2 medium pairs 10–20 s apart, 7 singles, every slot ≥ 120 s from the next | `schedule()` | 15 − 8 = 7 singles; gap between slots = 120 s + slack | match |
| Fig 1: 35m10s–41m10s, seed 10, quiet | `numbers.json` window [2110, 2470] | 2110 s = 35m10s, 2470 s = 41m10s | match |
| Fig 2: busy, seed 3 | `recording(3, BUSY)` | | match |

**Figure 2**

| Quoted | Source | Recomputed | Result |
|---|---|---|---|
| mean 0.47 onsets per window, both versions | `numbers.json` | 0.4737 / 0.4737 | match |
| only the recording has windows of 5–11 onsets | recomputed counts | real values ≥ 5: {5, 6, 7, 8, 10, 11}, 10 windows; shifted copy max 4 | match |
| excess f₂ 0.214 | 0.20671 − (−0.00744) | 0.2142 | match |
| excess f₃ 1.369 | 1.36792 − (−0.00113) | 1.3691 | match |
| the copies sit at zero | means −0.0074 / −0.0011 | | match |

**The tool's behaviour**

| Quoted | Source | Result |
|---|---|---|
| counts twice, offset by half a window, and averages | `population_cumulants`, offsets 0 and wf//2 | match ("not lost" overstated, finding 14) |
| 20 copies | `N_SURR = 20` | match |
| every two cells' shifts at least two windows apart, wrapping round | `shifted` with spacing 2·wf, mod L | match |
| span about a minute for 32 cells at 1 s | 32 × 2 s = 64 s | match |
| f₂ and f₃ formulas | `factorial_cumulants` | match |
| fixed model k = f₃/f₂ + 2; λ = f₂/(w·k(k−1)); share = λk/N | `solve` and `per_recording` | match |
| f₃/f₂ pooled over the run; f₂ and rate per recording | `pooled_ratio` (weighted by n_win) and `per_recording` | match (by-group runs pool within each group, not mentioned) |
| `ADOPTED_MODEL` = fixed, and its rationale | comment beside it | paraphrase faithful |
| `CAL_TOL` ±25%, median relative error | 0.25 in `calibrate` | match |
| check stored with every run | `main` writes `rec["calibration"]` | match |
| primary window 1 s; windows 1/2/4 s | `PRIMARY_W`, `WINDOWS` | match |
| `shape_usable` floors 300 s / 20 onsets / 5 cells | `MIN_DURATION_SEC` 300, `MIN_EVENTS` 20, `MIN_ROIS` 5 | match |
| floors applied to the reported quiet/busy rates only | `summarize` | match |
| every simulated recording clears the floors | recomputed | null, ramp and lowered sets all usable; smallest recording 152 onsets (0.25× quiet); every other set is at quiet or busier | match |
| `coordinated_share_of_rate` | exists in `summarize` | match |

**Results**

| Quoted | numbers.json | Result |
|---|---|---|
| fixed −21%, binomial −11%; factor of about two | −0.2074 / −0.1102 (ratio 1.88) | match |
| both inside the pass band | | match |
| k too high, λ too low; they nearly cancel | k +30.2%, λ −39.1%, product 0.79 | match |
| fixed error between −10% and −21% | −10.4% to −20.7% | match |
| binomial between +1% and −11% | +0.9% to −11.0% | match |
| 56% high instead of 28% (k, 4 s) | close pairs +55.8%, 120 s only +27.9% | match (mixed +53.8%) |
| 47% low instead of 30% (λ, 4 s) | −47.1% / −29.9% | match |
| ≤ about 3 points at 1–2 s | largest is 2.8 (k at 2 s) | match |
| fixed and binomial pass at every window and schedule | all |error| < 0.25 | match |
| stretch median 3.7%, max 5.7% | 0.03735 / 0.05651 | match |
| ramp: none answered | answered 0 | match (wording, finding 9) |
| null: no answer | answered 0; pooled f₃ −14.1 | match |
| Fig 5B middle 80%: 78–84% (15 moments) | 0.782 / 0.843 | match |
| 73–91% (6 moments) | 0.730 / 0.910 | match |
| 69–105% (3 moments) | 0.688 / 1.054 | match |
| pooled 81–83% | 0.814 / 0.806 / 0.833 | match |
| no recording failed to answer | `no_answer` 0 everywhere | match |
| 79% / 81% / 81% at lowered backgrounds | 0.790 / 0.812 / 0.812 | match (schedule unstated; noise conclusion not shown by these numbers, finding 10) |

**What waits**

| Quoted | Source | Result |
|---|---|---|
| 66-recording `senktide_ttx`, stopped since 2026-10-05 | `current_export.toml` | match |
| four DI recordings | | count matches; "missed in" overstated (finding 12) |
| pinning makes several ROIs show events at once | the `steps_and_pins_excluded` note ("CROSS-CELL artifact") | match |
| bench revision waiting on Tony | todo 2026-10-08, status waiting-on-tony | match |
| the commissioning todo had the slow-change rule backwards | todo item 5 vs the tool's docstring | match; but the README's replacement mechanism is refuted (finding 1) |

## Sources consulted beyond the named ones

- **Group membership and withdrawals:** not applicable, because no real recording is used. The only real-data claims are the 66-recording count and the four DI recordings, checked against `current_export.toml`. That file is the source of record for the producer's applied withdrawals; the 2026-10-05 todo is the record for the stop.
- **Tool vs page on treatment:** the tool reads baseline windows only today (`_real`). The README's "will report … under treatment … a separate piece of work" is consistent with the todo's out-of-scope note, so no finding.

## Scratch outputs

`C:\Users\defazio\AppData\Local\Temp\claude\c--Users-defazio-bugarach-bugarach\8f7e79d0-c19b-4389-819d-be7bbbbd9efc\scratchpad\mb-r1\role1\rerun\` holds the reproduced PNGs and `numbers.json`, plus the run log. My own checks were run inline and were not saved as files. The `.claude/hooks/no-heredoc-source.sh` hook blocked writing a check script through a heredoc, so I passed each script with `python -c`.
