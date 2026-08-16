# Murderboard run — `roi_rate_distribution`

- upstream:  syncytium2/murderboard @ b2b2ba2
- vendored:  b2b2ba2 (`murderboard_freshness.sh --refresh --verbose` → `current (@ b2b2ba2, via remote)`, exit 0)
- freshness: current
- artifact:  `<darkroom>/bugarach/roi_rate_distribution.png` (`47e19fb`) + `.html` (`339565e`);
  generator `tools/make_roi_rate_distribution.py` (`3363c01`)
- roles:     11 of 11 run, as parallel subagents
- rounds:    **0 blind verify rounds — FIXES NOT YET APPLIED.** This record is the
  synthesis only. The artifact is **do-not-ship** and has not been rebuilt.

The artifact is a figure + caption + numeric table on one page, produced by new
analysis code, so roles 6–7 reviewed `make_roi_rate_distribution.py` and the
`bugarach.bench` path it calls as well as the render.

---

## Role ledger

| # | role | findings | outcome |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 20-row claim ledger, **all 20 match**; 1 blocking, 2 major, 6 minor | every number recomputed independently from the archive; the defects are what the numbers *mean* |
| 2 | Citation & reference validator — "DOI or Die." | **8 findings** (1 high, 4 medium, 3 low); 6 verified clean | the cited definition is not the computed one |
| 3 | Consistency auditor — "Cross-Examiner." | **20 findings** (3 blocking, 2 high, 12 medium, 5 low) | one population, four bases, no reconciliation on the page |
| 4 | Adversarial reviewer — "Reviewer 2." | **12 findings** (3 blocking, 6 major); verdict **do not ship** | built and ran every attack; the finding survived, the artifact did not |
| 5 | Line editor — "Kill Your Darlings." | **15 findings** (3 blocking, 7 major, 5 minor) | named the root pattern (below) |
| 6 | Methods / domain expert — "RTFM." | **13 findings** (2 blocking, 2 major, 2 moderate) | the mechanism named is not the mechanism that produced the gap |
| 7 | Reuse auditor — "Reinventing the Wheel." | **14 findings** (1 blocking, 5 major, 8 minor) | the one-line fix exists in `bench` and was not called |
| 8 | Naive-reader accessibility — "You Lost Me." | per-element table; **6 of 7 elements blocking**; 12 findings | written entirely for someone who already knows the answer |
| 9 | Density & figure-first — "Show, Don't Tell." | count table; **1 blocking, 5 major, 2 minor** | figure is 39.3% of canvas; named the replacement figure |
| 10 | Build & craft gate — "Ship It." | 31-row table; **4 FAIL, 7 FLAG** | the two things the reader must separate are 3.5 px apart |
| 11 | Argument order — "Start With the Problem." | spine + **9 findings** (2 blocking) + 4 on the docstring | no element states the conclusion |

No role returned "nothing to check."

---

## The root pattern

Role 5 named it and roles 8, 9 and 11 hit it independently:

> **The figure explains itself by naming its own source code.**

Once `roiRate` is the subject, the caption cannot say what the line *is* — it says
"the mean roiRate the calibration was taken from", four abstractions with no
agent. Once `MEAN` and `MEDIAN` are adjacent row labels differing by one
lowercase word, the author reaches for capitals to separate them. Once
`baseline_quiet` is a row label, the caption half-translates it to "quiet" and
the two surfaces disagree.

This is `docs/writing_conventions.md`'s own rule — *name things; don't index
them* — and it is the **opposite error** from the one that prompted this figure's
rewrite. Told that invented vocabulary was wrong, the fix reached for the
project's identifiers and put them on the reader's page.

---

## The defect that four roles found independently

Roles **1**, **5**, **6** and **7** converged, from four different directions, on
the same thing:

> **The curves labelled "generator" are realized total rates, not the background
> model the figure exists to indict.**

`generator_rates()` calls `bench.make_recording()`, which returns the background
**plus** 15 planted coordinated events, 6 distractors, and a 300 s promiscuity
probe running at 16× the quiet background. Measured (3 seeds, mHz per ROI):

| what is counted | quiet | busy |
|---|---|---|
| **as plotted** | **11.1** | **25.2** |
| probe removed | 5.4 | 19.6 |
| background only (`make_null_recording`) | **3.70** | **17.78** |
| `bg_rate_hz`, the parameter being indicted | 3.8 | 17.5 |

**51–67% of the plotted quiet-regime rate is structure that is not background.**
`bugarach.bench` itself scopes the probe out of every headline number — `n_scored`
and the `precision` docstring exist for exactly this reason — and the figure folds
it back in, against real data containing no analogue, then reads the result as a
calibration defect. The gap drawn (1.7 → 11.1, 6.5×) is ~3× the gap the parameter
creates (1.7 → 3.8, 2.2×), inflated in the direction that flatters the thesis.

Role 7 supplied the fix in one line, using an API that already exists:
`bench.make_null_recording(seed, **bench.REGIMES[regime])`.

Two consequences ride on this. The purple calibration line at 10.1 mHz lands
within 1 mHz of the quiet curve at 11.1, so the panel *visually asserts* that the
generator's quiet regime sits on the calibration point — a coincidence
manufactured entirely by the inflation (role 1 M3, role 10 F1). And the flatness
claim is overstated too: the probe adds the same block to every ROI, halving
apparent spread (CV 0.15 plotted vs 0.29 background-only).

---

## The mechanism named is not the mechanism

Role 6 F2, corroborated by role 1's ledger row 20. The artifact and the todo both
say `bg_rate_hz` was *"calibrated to the mean roiRate of a right-skewed
distribution."* `bench.REGIMES`' endpoints are **derived, not read**:

```
p25: 7.55 events/min ÷ 60 ÷ 33.16 = 0.00379 Hz  → baseline_quiet 0.0038
p75: 34.88 events/min ÷ 60 ÷ 33.16 = 0.01753 Hz → baseline_busy  0.0175
```

`rate_p25`/`rate_p75` are percentiles of the **population** rate; the mean-over-ROIs
statistic enters only through the derived ROI count 33.16. **No regime is set at
the mean**, and the figure indicting `bg_rate_hz` never plots `bg_rate_hz`.

The true statement is cleaner and still damning: **`baseline_quiet` sits at the
60th percentile of real per-ROI rates and `baseline_busy` at the 83rd** — and
neither can produce a field whose busiest ROI holds 30% of the events.

---

## What survived attack

Role 4 built every attack it could and role 6 built the control the process
demands. The **conclusion holds**; only the instrument was wrong.

| attack | result |
|---|---|
| duration confound (flagged potentially fatal) | **dead** — windows run 1020–1860 s, rate quantum 0.56–0.88 mHz, below the 1.7 median; 0 of 81 could be manufactured |
| restrict to long windows | skew **increases** (20× at ≥1500 s) |
| "486 mHz is one extreme" | not load-bearing — drop the top 20 ROIs, median unchanged |
| seeds | inert across 4 seed sets |
| **matched homogeneous-Poisson null** (role 6 F4) | real **35%** silent ROIs / CV **2.00** against the null's **2%** / **0.26** |

The alarm can ring. It rings loudly. That null belongs on the figure — it
separates "wrong *shape*" from "wrong *level*", which is exactly what the current
version blurs.

---

## Findings the human must rule on

1. **⚠ The claim is false on the slow stream.** Role 4 B2b: SLOW gives mean/median
   1.4× with **7 of 77 windows below the line**. The artifact says "a right-skewed
   field" and names its stream only in a monospace footer. FOUNDATIONS §9 requires
   a claim to name its stream. Either scope the claim to FAST or explain SLOW.
2. **⚠ Group pooling cannot be resolved from this source.** Role 4 M3: 81 windows
   are pooled across every group, and the archive carries **no group labels** — so
   §9's mandated breakdown is not producible here. This is a permanent `⚠`, not a
   fixable one, though §9's prohibition targets treatment effects and this figure
   draws none.
3. **⚠ The comparison is circular and should say so.** `bg_rate_hz` was calibrated
   from this archive; comparing the generator against it is a consistency check on
   the calibration's own source, not independent validation. It is the *right*
   design for this claim — saying so costs nothing.
4. **Real slice ids in a public repo.** Role 3 C20: `20240813_39` is hardcoded at
   `tools/make_reality_check.py:33` and named in the todo, against FOUNDATIONS §5.
   Pre-existing, not caused here, and sapper does not catch it.

---

## Corrections this run made to its own earlier findings

Recorded because the disagreement is the evidence the roles were independent.

- **Roles 2 and 3 called the raw-vs-trimmed `win_dur` blocking; roles 1 and 6
  measured it and it is numerically nil.** Recomputed under interface2's 1200 s
  backward cap: pooled median 1.67 → 1.67, slice-mean 10.09 → 10.09, zeros
  35.1% → 36.1%, max 486 → 481. **Real attribution defect, null numeric effect** —
  one clause and one function call, not a rebuild.
- **Role 3's "37% p25 gap" is an artifact of this survey's own filter.** Role 1 M2:
  only 4 slices are dropped (the archive holds **85** `.mat` files, not the 88 in
  `SESSIONS.md` — the rest are a CSV and two `.bak`), all four to `MIN_EVENTS`.
  Include them and the real slice-mean IQR is **3.70–18.47 mHz** against the
  calibration's 3.8–17.5. The calibration is fine; the gate made it look off.

---

## Fix list, ranked — NOT YET APPLIED

**Blocking**
1. Plot the background, not the benched field — `make_null_recording` (roles 1, 5, 6, 7).
2. Restate the mechanism as percentile-of-real-ROIs; draw `bg_rate_hz` itself (role 6).
3. Report `0%` and `81/81` as arithmetic, not observation; quote 52/52 and n on the 2.6× (roles 1, 4).
4. Name the stream in the claim; state what SLOW does (role 4).
5. Add the matched-Poisson null and/or the mean-normalised overlay (roles 4, 6).
6. State the conclusion somewhere in the artifact (role 11).

**Major**
7. Left panel: add slice-mean and slice-median ECDFs (role 9 — makes the table readable off the picture and the purple line self-explaining).
8. Right panel: log–log with a labelled 2.6× ray; mark the 29 median-zero windows (roles 4, 9, 10).
9. Letter the panels A/B; kill "Left"/"Right" (roles 5, 8, 10).
10. Rebuild the key as a key, reusing `ui.diagnostic._key()` (roles 7, 8, 10).
11. Print the skip tally by reason; say "81 of 85" (roles 1, 3, 4, 6, 7).
12. Relabel the purple line; cite 9.6 mHz with n=84 (roles 1, 2, 3, 4, 6, 7).
13. Plain language for `roiRate`/`win_dur`/`bg_rate_hz`/`baseline_quiet` (roles 5, 8).
14. Call `region_windows()` for `win_dur`, or restate the attribution (roles 1, 2, 3, 6).

**Minor** — ECDF `steps-post` (6); stamp figure id/script/sha in HTML title and PNG
tEXt (10); page padding (10); `MIN_ROIS` → `MIN_ROIS_PER_SLICE` (3); integer-count
guard (7); one `_render_png` helper across four copies (7); `roiRate` into GLOSSARY (3).

**Housekeeping, caused by this branch**
- `docs/todo/2026-08-14-generator-background-model-is-flat.md` and `docs/SESSIONS.md`
  still name the deleted `make_roi_concentration.py`; the todo's four headline
  statistics are reproducible by nothing in the tree (roles 2, 3, 7).
- `docs/generator.md:359`'s "0–99 mHz" is one slice presented as the population;
  pooled max is 486 mHz (role 3).
- `docs/generator.md:286`'s ⚠ that `n_roi ≈ 33` is unmeasurable is **answered** by
  this survey: 2643 ROIs / 81 windows = 32.6, measured directly (role 3).
