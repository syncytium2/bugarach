> **Public copy.** Lines that concern real treatment recordings are removed (21 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1 (Prove It): claim and data verification, round 3, blind pass

**Artifact:** `detector_review.html` (sha256 5495e51e…, checked). I read it through `detector_review_plain.txt` and the PNGs in `review\_work\`.

**Sources checked against:**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- The generator at commit 699de8e (`git show`). The worktree copy of `tools/make_detector_review.py` has been edited since the build: blockrecall spacing and a new fig19. I reviewed the committed version the page was built from.
- Detector and scoring code: `src/bugarach/{bench,score,simulate,detect_folder,io}.py`, `detectors/*.py`, `learn/{train,encode}.py`, `learn/nets/*.py`
- The bake-off tool: `tools/fair_bakeoff.py`
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**Recomputed independently:**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Figure 2D, per bar
- The composition of the Figure 4A bin
- Decoy positions on the bench recording (seed 3)

---

## Findings, ranked

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Where:**
  - §7, "So no design here both ignores busy cells and keeps finding events among them. That is the central difficulty…"
  - §10, "every design either calls through busy stretches or goes partly blind in them"
  - In short, "Detectors that judge chance from the nearby seconds make few false calls… They also miss most real events there"
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - **rate+context:**
    - Its bar comes from the nearby 60 s (`settings.rate.context_win`, `rate.py`).
    - It makes 0.60 calls/min in the busy block (`shipped_baseline_quiet_rate.probe_per_min`), under its limit of 2.
    - Mid-sized recall inside the block is 75%, against 71% outside, with a chance line of 5% (`blockrecall…rate.p18`).
  - **SPIKE-synch:**
    - It makes 0.29 calls/min, under its limit of 1.
    - Large-event recall inside is 92% against 72% outside, with chance at 3%. Mid-sized: 38% inside against 13% outside.
  - The document's own bullets ("rate+context held up"; Table 4, "Keeps finding large events inside a busy stretch") say the same thing.
- **Fix:** Narrow the generalization to what the rows show. Name rate+context and SPIKE-synch as the exceptions, and give their costs: rate+context finds 2% of small events at its shipped setting; SPIKE-synch cannot call 10% events. Or drop "no design".
- **Verified against source:** yes.

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - At 699de8e, `_block_events` puts both events in 1240–1460 s and requires only 30 s between them.
  - I re-ran the draw for all 72 cases (24 seeds × 3 sizes):
    - 46% of pairs are less than 60 s apart, so they share CoactDetect's ±30 s context and LoCo's 60 s half-windows.
    - 83% are less than 120 s apart. Median gap: 64.5 s.
  - Outside the block, planted events are kept 120 s apart. The inside-vs-outside contrast behind "a bar that follows the nearby background also hides real events" (CoactDetect 8% against 97%; LoCo 15% against 94%) therefore mixes the busy block with exactly the crowding weakness §3.3 says is unmeasured.
  - It is also 72 recordings, not 24. 24 of the 72 were redrawn at seed + 100000·attempt, which is outside 2000–2023.
- **Fix:**
  - Re-run with the two inside events at least 120 s apart. The worktree edit appears to do this, but the built page does not reflect it.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Correct the count and seed wording either way.
- **Verified against source:** yes (recomputed).

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Where:** §8, "Coordination… falls to about half of baseline in the fast stream and rises in the slow stream (typical values; unpublished lab data)."
- **Evidence:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - The measurement also came from the MATLAB campaign at its own settings. FOUNDATIONS says magnitudes differ from the ports, so "these same six detectors" overstates the match.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verified against source:** yes.

### MAJOR 4: one of locust's "four differences from CICADA" is not a difference
- **Where:** §3.5, "It differs from CICADA in four ways: … and it uses one bar for the whole recording."
- **Evidence:** `docs/detector_history.md` (Tier 1 locust entry): "A regional-scope option was added; the original thresholds over the whole recording." `cicada.py` describes the global threshold as CICADA's rule. The project record documents two deviations from upstream: events are fed in, and the duration is supplied rather than measured.
- **Fix:** Drop the fourth item, giving "three ways". This is an attribution about another lab's software, so it should be exact.
- **Verified against source:** yes.

### MINOR 5: "Most false alarms outside the busy block are decoys" is a generalization that fails for three detectors
- **Where:** §7 lead sentence; §10 "makes most false alarms decoy calls".
- **Evidence:** From `precision` and `precision_no_decoys`, the decoy share of non-block false alarms (approximate) is:

| detector | decoy share of false alarms |
|---|---|
| CoactDetect | ≈84% |
| LoCo | ≈91% |
| tube | ≈68% |
| rate+context | ≈56% |
| binned SCE | ≈41% |
| locust | ≈30% |
| tube-ratio-guard | ≈47% |

- **Fix:** Say "for CoactDetect and LoCo".
- **Verified against source:** yes (derived from tokens).

### MINOR 6: the In short describes decoys as chance lineups
- **Where:** In short, "because some chance lineups look exactly like real events".
- **Evidence:** Decoys are deliberately planted correlated bursts (`simulate.py`, lines 734–753). They are not chance lineups, and §5 says so correctly.
- **Fix:** "because decoys, built like real events but left out of the answer key, cannot be told apart from them".

### MINOR 7: the provenance of the 80 baselines and the "matching the two levels" claim
- **Where:** §5, "Recomputed on the 80 baselines the simulator was fitted to (…) matching the two levels"; Figure 10 caption.
- **Evidence:**
  - `bench.py` records the rate shape as fitted on 81 windows / 2,643 ROIs and the burst shape on 85 windows. The recomputation uses the later `steps_excluded` folder: 80 windows, 2,557 ROIs. So it is not the set the simulator was fitted on.
  - The recomputed 25th percentile is 5.0 mHz against the bench's 5.2 mHz.
  - The generator's own comment calls the realized rates "the like-for-like number": 6.1 and 17.2 mHz. Against real 5.0 and 19.0, the quiet level is 22% busier and the busy level 9.5% quieter.
  - §2 uses 84 baselines and never explains why §5 has 80.
- **Fix:** Say "80 baselines from the current export that pass the fitter's floors (the shapes were fitted on an earlier export)". Say that realized rates run 6.1 and 17.2 mHz against real 5.0 and 19.0.

### MINOR 8: SPIKE-synch's frame score is described inaccurately
- **Where:** §3.6, "takes the average score of the events in each 0.1-second frame" and "A call must include at least 3 events"; Figure 8B.
- **Evidence:** `sync.binned_synchrony`:
  - The mean is taken only over events at the same time.
  - Each distinct event time overwrites the bin, and can write into the neighbouring bin within ±0.1 s.
  - `Cn` is the group size of the last writer, not the number of events in the frame.
- **Fix:** "the score of the latest event in each frame". Or add a footnote.

### MINOR 9: SPIKE-synch "cannot call such an event at all" and "at most 6 minus 1"
- **Evidence:**
  - Measured 10% recall at the shipped setting is 1/120, not 0 (`shipped_*_sync.by_frac.p10`). Background cells can join an event.
  - The Figure 4A bin holds a seventh, non-planted ROI (recomputed: ROI 29 alongside the six planted). SPIKE-synch's "at most 5/32" bound for Figure 8A therefore assumes no background coincidence.
- **Fix:** "cannot call such an event unless background events happen to join it".

### MINOR 10: "Tube filter widths" are Gaussian standard deviations
- **Where:** §4.1, "center filters are about 0.19 to 0.63 seconds wide…"
- **Evidence:** `tube_sigma` holds the σ of each Gaussian (`tube.py` `_kernels`). The widest surround (σ 16.3 s, cut at ±12.8 s) still falls to about 73% of its peak at the cut, so "nearly flat" is generous.
- **Fix:** "spread (standard deviation) of about…".

### MINOR 11: two words understate their numbers
- **Evidence:**
  - "tube-guard (65%) and tube (46%) lost part of their recall": tube lost 54% of it.
  - "CoactDetect … Almost never calls in the busy block" (0.17/min tuned) uses the same words as the ratio models (0.01–0.02/min), which call about twenty times less.
- **Fix:** Use the numbers. Say "about half" for tube.

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:** The shipped-setting columns and diamonds come from `bench.evaluate` over all 24 recordings (`stage_shipped`).
- **Fix:** Add "except the shipped-setting columns".

### MINOR 13: attribution for SPIKE-synch's calling rule and the PySpike cap
- **Evidence:**
  - §11 says "The rule that turns scores into calls is ours". `detector_history.md` says "Not novel either: Kreuz's own lab has published the same two-knob detector on this profile (… Kreuz et al. 2022, J Neurosci Methods 381:109703)".
  - "PySpike … has had no effect since its version 0.8.0": the project's own note limits this to spikes with neighbours on both sides.
- **Fix:** Reconcile with detector_history, or cite Kreuz et al. 2022. Qualify the PySpike sentence.

### MINOR 14: small rounding and wording points
- **Rounding:**
  - 0.525 appears as "52%"; half-up gives 53%.
  - Doubles of 24.5 per 1,000 appear as "about 24".
  - tiny's 0.125 appears as "0.12".
- **"Across the list, F1 runs only from 0.48 to 0.53":** these are the quiet-level values (busy is 0.47–0.51), but the sentence sits right after a busy-level sentence.
- **"CoactDetect's and SPIKE-synch's came from the project's viewer":** the source is interface2's explore_sce viewer (`bench.py`).
- **"Where many cells start events within a few frames of each other, most detectors do call"** (In short and §8) is an eyeballed agreement claim in a document that says agreement was not measured.

### Flag for adjudication (not a factual error)
- `MILESTONES.md` row 63 holds "promoting any new bake-off number" for Tony's decision. The page publishes fresh bake-off numbers to outside readers. It labels them provisional, which is accurate.

---

## Claim ledger (recomputed or looked up; "ok" means it matches)

| claim (location) | cited value | source | recomputed | status |
|---|---|---|---|---|
| Top-five quiet F1 (§7) | .74/.73/.73/.71/.71 | `perf_baseline_quiet_*.f1` | .736/.732/.725/.713/.711 | ok |
| Lower three quiet (§7) | locust .57, SPIKE .53, SCE .45 | perf | .567/.529/.446 | ok |
| Busy F1 (§7) | .66/.65/.64/.64/.63/.63 | perf busy | .661/.649/.641/.636/.626/.625 | ok |
| F1 ceiling / precision | 0.83 / 0.71 | 15/21 | .833/.714 | ok (expected-value ceiling) |
| Decoys reached: CoactDetect / SPIKE (§7) | 99% / 31% | `decoys_share` | .986/.3125 | ok |
| Precision → decoys set aside (§7) | .65→.92, .66→.96 | perf | .646→.919, .657→.958 | ok |
| Round ranges: tube / TRG / Coact | .63–.76 / .49–.70 / .71–.76 | `f1_min/max` | same | ok |
| Shipped F1 (§7) | Coact .74, LoCo .72, rate .63, SCE .37 | `shipped_*` | .741/.719/.633/.370 | ok |
| Small-event recall, shipped Coact / tuned tube (§7) | 52→24% / 64→12% | `by_frac.p10` | .525→.242 / .636→.117 | ok (rounding, item 14) |
| Tuned rate block calls, 4/4 rounds; shipped 0.6 | 5.3 | perf | 5.32, 4, 0.60 | ok |
| locust over limit 2/4, worst 35; SPIKE 3 | — | perf | 2, 34.7, 3 | ok |
| Table 3, every numeric cell | — | `table_performance.html` vs perf/shipped | cell-by-cell | ok |
| Loosest pick 3/4 (SCE, LoCo quiet); SPIKE busy 0.005 ×4; 3 tied | — | `opt_*` / `sweeps.json` | 3, 3, 4, 3 (grid .005/.01/.02 < 1/32) | ok |
| LoCo list "nearly flat", SCE "climb slightly" | — | `sweeps.json` | .737/.738; .440→.452 | ok |
| Setting picks breaking limits: rate, locust, SPIKE | — | `picks_over_limit` | 4, 2, 4 | ok |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| rate 75/71/5; SPIKE 92/72; SCE 100%; locust 51% | — | blockrecall | .75/.708/.051; .917/.725; .996; .514 | ok |
| Ratio models find nothing inside | 0 | blockrecall | 0 at all sizes | ok |
| "24 recordings, seeds 2000–2023, 2 per recording" | 24 | `_block_events` | 72 recordings, 24 redrawn outside that range | **mismatch** |
| Speed: slowest / fastest | 9,660 / 534,310 | perf | 9,659.7 / 534,309.9 | ok |
| Doubles per 1,000: real / shift / shuffle; slow | 24/26/108; 0/33 | `sur_*_doubles` | 24.5/25.6/107.9; 0/33 | ok |
| n ≥ 6: shuffle / shift | .35% / .58% | `sur_fast_n6` | .351/.575 | ok |
| Real over shift at n8 / n10; groups | 16× / 153×; 4/4 | `sur_fast_real_over_shift` | 16.4, 153; 4 | ok |
| Simulated below real at n ≥ 8 | — | `sur_sim_n8` | .0035 < .0058 | ok |
| Figure 2D: bar 4; 46 vs 0 in block; 3 calls each (1 planted, 2 decoys); missed events 3 ROIs each | — | recomputed (RandomState 7) | both bars identical outside: 926.5, 1084.5, 1664.5; decoys 927.2, 1085.2; planted 1664.7; missed 983.6 and 1792.0, 3 ROIs each | ok |
| Figure 2A: busiest of 84, 15 ROIs | — | `sur_a` | 84, 15 | ok |
| Bench recipe: 33 ROIs, 45 min, 15 events (5/level), 30/18/10%, 0.36 s, 120 s, block 20–25 min, 60 mHz, 30 s ease-in, 6 decoys at 18% in min 2–18 | — | `BENCH_RECORDING` | same (decoy window ends at 18.3 min) | ok |
| Decoys built exactly like planted events | — | `simulate.py` 740 | same jitter, ROI draw and fraction | ok |
| Levels 5.2 / 19 mHz; realized 6.1 / 17.2; real p25/p75 5.0 / 19.0 | — | REGIMES / generator | same | ok, but see MINOR 7 |
| Bunching 1.73 vs 1.79; 1.17 vs 9.81 | — | `gen_*_fano_by_rate` | same | ok |
| 0.42 s null; 0.64 s round trip | — | `docs/generator.md` | 0.42, ~0.64 | ok (older run, not re-measured) |
| Window A event: 6/33, 0.8 s | — | recomputed | onsets 491.7–492.5 | ok |
| Figure 4A count 7 = 6 planted + 1 background | 7 | recomputed | obs 7 (ROI 29 is the extra) | ok |
| Figure 4B surrogate average ≈4, bar ≈10 | — | figure | ≈4 / ≈10–11 | ok |
| Figure 6: count 7 equals bar 7 | — | `sce_winA_bin` | 7 / 7 | ok |
| Window call counts in Figures 3, 5–9 | — | `*_winA/B` | rate 1/2, LoCo 1/0, SCE 0/18, locust 2/15, SPIKE 0/0, tube 3, tube-guard 7, ratio models 0 | ok |
| z 3.72 ↔ 1 in 10,000 | — | `coact_bar` | 3.719 | ok |
| Limits 1/1/1/2/9/25, each set above an earlier measured rate | — | `MAX_PROBE_PER_MIN` | measured 0/.1/.2/.6/5.6/17.3 | ok |
| Tie goes to the looser value | — | `fair_bakeoff.py` 230 (strict >, loosest first) | all six grids list loosest first | ok |
| Learned: 10 fit + 2 threshold; one run in three uses a different training set | — | `fold_maker` / `train` | seed1 → offset 8 of 16; seeds 0 and 2 identical | ok |
| trace/tiny at 1/10 learning rate; parameter counts | 1,149 / 2,065 / 2,393 | `LR`, `learned_meta` | 1e-2 vs 1e-3 | ok |
| tiny: 1 call covering all; trace: 3 calls covering 97% | — | `*_bench_seed_score` | same | ok |
| Call level 0.972; widen to 0.3 s; guard 0.8 s; cutoff 12.8 s | — | `learned_meta`, `tube.py` | 0.9716; 3 frames; 8 frames; k = 128 | ok |
| Busy block and decoys labelled 0 in training | — | `encode.frame_targets` | yes | ok |
| All six anchor on half-rise | — | `io._as_stream` (locs = t50rise), export spec | yes on folder input | ok (the `ONSET_FIELD` comment in code is stale) |
| Windowing per detector (§8, Table 1) | — | `detect_folder.py` | flat and learned per window; SCE regional; LoCo and locust whole recording | ok |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| Middle-ROI pick per group | — | `_real_members` | upper-middle for even group sizes | ok |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| Brightness-jump events removed | — | `current_export.toml` (steps_excluded) | ±2 s of 9 steps | ok |
| 2.5 s tolerance chosen at the LoCo/Coact plateau | — | `score.TOL_SEC` doc | yes | ok |
| Earlier run: one detector ahead at every rate | — | MILESTONES row 85 | yes | ok |
| Bake-off held pending data revision | — | MILESTONES row 63/96 | yes | ok |
| Python matched MATLAB to 1e-9 | — | README, detector docstrings | yes | ok |
| CICADA: "one bar for whole recording" is a difference | — | `detector_history.md` | the original also thresholds over the whole recording | **mismatch** (MAJOR 4) |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |

---

## Sources outside the document's citations
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Producer's contamination caveat.** None of the eight shown recordings is on the producer's list of recordings with motion-pinned ROIs.
- **Recordings from the same animal.** Several recordings can come from one animal, and the §2 surrogate curves pool recordings as if independent. No inferential claim rests on that pooling, so it is not listed as a finding.

## Files
- Artifact: `<scratchpad>\review\detector_review.html`
- Committed generator used for this review (extracted): `<scratchpad>\mdr_699de8e.py`
- Evidence files cited above:
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - `<worktree>\docs\detector_history.md`
  - `<worktree>\src\bugarach\bench.py`
  - `<worktree>\src\bugarach\detectors\sync.py`
  - `<worktree>\current_export.toml`
