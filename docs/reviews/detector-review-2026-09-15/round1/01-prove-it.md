> **Public copy.** Lines that concern real treatment recordings are removed (13 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 1 ok — Read, Grep, Glob, Bash

(No editing tool was held and nothing was written. A repository hook blocked one attempt to write a scratch script through a shell heredoc, so every recomputation below ran inline with `python -c`. The only write was an empty `mb_scratch/role01/` directory.)

# Role 1 (Prove It): claim ledger and findings for `detector_review.html`

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**What I checked:**
- All 16 captions, the prose, Tables 1 and 10, and the Section 12 citations (against README "Licensing & citations").
- Every "X does Y" statement against the six detector modules, `simulate.py`, `score.py`, `bench.py`, `fair_bakeoff.py`, `learn/train.py`, `learn/nets/*` and `detect_folder.py`.
- Table 1, recomputed from the 6 bake-off JSONs.
- Figure 2C, re-run. The 25th/75th percentile rates, recomputed from the `default` and `steps_excluded` exports.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- The Figure 10 statistics, from `generator_stats.json`.
- Figures 4 and 11, opened as images.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## Claim ledger

| Quoted value | Source cited or used | Recomputed | Verdict |
|---|---|---|---|
| Quiet 5.2 mHz / busy 19 mHz = 25th/75th percentile of real baselines | `bench.REGIMES`; typed into the generator as `quiet_mhz=5.2, busy_mhz=19.0` | Slice-mean per-ROI fast rate, 84 baselines: p25 **3.6 mHz**, p75 18.6–19.0 mHz. Same in both exports, analysis window or whole region. The 2026-09-12 review row 16 already recorded that the range does not reproduce | **mismatch (p25)** |
| Learned detectors trained on 18 recordings | typed in template | `fold_maker` gives 16 fit + 2 validation. `train(n_train=min(10,16))` fits on **10**; threshold chosen on 2; 6 unused | **mismatch** |
| Figure 2C: "three calls outside the block … are planted events" | re-run of the generator code, seed 3 | Calls at 926.5, 1084.5, 1664.5 s. Decoys at **927.2 and 1085.2**; planted event at 1664.7. Only 1 of 3 is planted | **mismatch** |
| Figure 2C: whole-recording bar 4 ROIs; 46 vs 0 passes in block | same | 4.0; 46; 0 | match |
| Figure 2B fast K≥6: shuffle 0.35%, shift 0.58%; slow 0.35% vs 0.40%; 84 recordings, 50 draws | `surrogate_survival.json` | 0.351 / 0.575; 0.353 / 0.395; 84; 50 | match |
| Quiet F1 means: CoactDetect 0.74, LoCo 0.73, tube_guard 0.73, tube 0.71, rate+context 0.71, locust 0.57, SPIKE-synch 0.53, binned SCE 0.45 | bake-off JSONs | 0.736, 0.732, 0.725, 0.713, 0.711, 0.567, 0.529, 0.446 | match |
| Busy F1: LoCo 0.66, CoactDetect 0.65, tube 0.64; binned SCE 0.45→0.63 | same | 0.661, 0.649, 0.641; 0.446→0.625 | match |
| 10% events: CoactDetect 57%→19%, tube 64%→12%; SPIKE-synch 2% | same | 0.567→0.192; 0.636→0.117; 0.017 | match |
| Busy-block calls/min: rate+context 5.3, SPIKE-synch 1.05, CoactDetect 0.17, LoCo 0.31, tube 1.40, tube_guard 1.01, ratio models 0.01/0.02 | same (mean hot-window false alarms ÷ 30 min) | 5.317, 1.050, 0.167, 0.308, 1.400, 1.014, 0.008, 0.019 | match (Table 1 shows CoactDetect 0.2 and SPIKE-synch 1.1: rounding only) |
| locust 19.4/min "allowed 25", no red cell | same | Per round **33.7, 34.7**, 4.5, 4.5. Two of four rounds broke the limit | **misleading** |
| tube range 0.63–0.76; tube_ratio_guard 0.49–0.70; trace 0.23, tiny 0.12 | same | 0.629–0.756; 0.494–0.704; 0.228, 0.124 | match |
| Slowest ≈9,786× real time; rate+context ≈536,163× | same (quiet) | 9,786 / 536,163 at quiet. At busy, **LoCo 8,143** is slowest | match (quiet only) |
| Limits 1/1/1/2/9/25 calls/min | `MAX_PROBE_PER_MIN` | same | match |
| Tuning edge cases: SCE and LoCo lowest value 3 of 4 rounds; SPIKE-synch F1 0.48–0.53; busy SPIKE-synch picks 0.005 ×4; rate+context picks 2 ×4 and breaks its limit | `numbers.json`, `sweeps.json` | same. But 0.005, 0.01, 0.02 **tie exactly**, so "chose 0.005" is tie-breaking | match (see findings) |
| "binned SCE … still rising" past the list end | `sweeps.json` quiet | 0.440 / 0.444 / 0.447 / 0.452 going to 75; not monotone, +0.008 | overstated |
| 1,149 parameters; call level 0.972; centre widths 0.19–0.63 s; surround widths 2.6–16.3 s; widening 0.3 s | models / `numbers.json` | same | match |
| Figure 9C busy-block calls: tube 3, tube_guard 7, ratio models 0, 0; Figure 9B four tube models find the event | `numbers.json` | same | match |
| Window calls in Figures 3–8 (2, 0, 0, 19, 15, 0; locust A 2 calls, 1 hit) | `numbers.json` | same | match |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| Figure 10: silent 38/37/4%; 2,630 ROIs; burstiness 1.39/3.55, 1.86/5.22, 0.97/0.79; event B 10 ROIs, span 1.2 s | `generator_stats.json` | 37.9/37.0/3.5%; 2,630; **medians** match exactly (means: 1.82/6.95, 3.07/12.30, 1.00/1.01) | match (median, not stated) |
| Bench: 33 ROIs, 45 min, 15 events, 5 at each of 30/18/10%, jitter 0.36 s, spacing 120 s, busy block minutes 20–25 at 60 mHz, 6 decoys at 18% | `BENCH_RECORDING`; bake-off spec | same | match (see decoy and busy-block findings) |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| Python matches MATLAB "within one part in a billion" | README; tests | 1e-9 tolerance tests (rate, SPIKE-synch; exact for CoactDetect, LoCo, locust signals) | match (loose: absolute tolerance, not relative) |
| Section 12 citations | README | Authors, venues, volumes and pages agree | match |
| Footer: "every number in the text [was] produced by the same run that drew the figures" | generator | Many numbers are typed into the template (detector settings, "18 recordings", "5 of the other 32", "about 4/10", "minute 21"). The quiet/busy rates are typed into the generator. Rounds come from a separate `fair_bakeoff.py` run | **mismatch** |

## Findings

**Location · issue · severity · suggested fix · verified against a source**

1. **Figure 2C caption** · "The three calls outside the block that both bars make are planted events." Two of the three are decoys (927.2 s and 1085.2 s), which the document itself defines as false alarms. · **blocking** · Say "one is a planted event and two are decoys", or pick a window without decoys. · yes (re-ran)

2. **§5, first paragraph ("trained each one on 18 simulated recordings")**, also §7.2 and the Figure 11B heading · Each learned model is fitted on 10 recordings, and its threshold is picked on 2 more. The other 6 of the 18 are never used. · **blocking** · "fitted on 10 and set its call level on 2 more, all from the three training groups." · yes (`train.py`, `fair_bakeoff.py`)

3. **§4.5 and its weakness; §10 locust row** · Two claims are wrong:
   - "gets each event's length from the lab's data file" and "takes [event length] from the data file". The shipped mode is `active_duration_mode="fixed"`, 1 s for every event; `detect_folder` never switches it on.
   - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
   
   [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

4. **§6 and Figure 12 ("25th and 75th percentiles of real baselines")** · The 75th percentile reproduces (19 mHz). The 25th gives 3.6 mHz, not 5.2, from both the current and the default export. The values are hardcoded in `stage_generator`, so no measurement stands behind the sentence. An earlier review already flagged this. · **blocking** · Settle the derivation, or drop "25th percentile" and state the value as the bench setting. · yes

5. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
   - binned SCE runs `analysis_mode="regional"`: it detects only inside each window, with its own bar per window.
   - locust runs `threshold_scope="global"`: one surrogate bar for the whole recording that ignores the windows.
   
   Only LoCo matches the sentence. · **major** · Describe each of the three separately. · yes

6. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

   | detector | calls |
   |---|---|
   | locust | 168 |
   | **SPIKE-synch** | **119** |
   | rate+context | 24 |
   | binned SCE | 23 |
   | LoCo | 16 |
   | CoactDetect | 11 |

   [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

7. **§6 "Decoys … outside any planted event"; §7.1 "a call on [a decoy] counts as a false alarm"** · The simulator places decoys uniformly in 120–1100 s with no exclusion around planted events. In the bench recording used for every mechanism figure (seed 3), a decoy sits 1.9 s from a 30% planted event (861.5 vs 863.4 s). In 5 of the 24 bake-off recordings a decoy lies within the 2.5 s matching tolerance of a planted event, so a call on it scores as a hit. · **major** · Say decoys are placed at random in the first ~18 minutes and can land next to planted events. · yes

8. **§6 "Planted events are at least 120 seconds apart, so that no detector's chance estimate contains a second planted event"** · False for binned SCE and locust: both build their surrogates from the whole recording, which holds all 15 planted events. · **major** · Limit the claim to the detectors that judge chance locally. · yes

9. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

10. **§5 strengths: "The fastest detectors here once trained"** · Table 1 contradicts it. tube models run 9,786–17,999× real time; rate+context 536,163×, binned SCE 166,570×, trace 148,799×. tube_ratio and tube_ratio_guard are the two slowest of all twelve. · **major** · Delete the sentence. · yes

11. **Table 1 locust row, and §8 "three flaws"** · The mean of 19.4 calls/min hides two rounds at 33.7 and 34.7/min, both over the 25 limit; Figure 11C itself shows a red ✕ inside a green ring at 99.9. SPIKE-synch's chosen value (0.04) also breaks its limit in every round. The third flaw names only rate+context. · **major** · Add locust (2 of 4 rounds) and SPIKE-synch to that flaw, and mark per-round violations in the table. · yes

12. **§6 "rises and falls over minutes and over seconds"** · The two burst scales are 300 s and 60 s (`MEASURED_BURST_BINS`), so both are minutes. · **major** · "over 5-minute and 1-minute stretches." · yes

13. **§3, the paragraph after Figure 2 ("real cells are not random. Busy cells fire at fairly steady intervals")** · This is true of the Figure 2A recording, whose busy ROIs have gaps-between-events CV 0.2–0.9. But generator code picked that recording as the one with the most baseline events, and the caption does not say so. Across all 84 baselines, ROIs with ≥50 events have median CV **1.08** (only 41% below 1) and burstiness 1.43 at 30 s. That is bunchier than random, which is what Figure 10D reports. The two sections contradict each other. · **major** · Say Figure 2A shows the busiest recording, and limit the "steady intervals" claim to it. · yes

14. **§8 "binned SCE is the one exception" and "every detector less sensitive"** · trace also rose (0.23→0.25) and tiny did not fall. binned SCE's recall rose (0.48→0.60), so "every detector less sensitive" is false for it. · **major** · Name the exceptions. · yes

15. **Footer provenance sentence** · See the ledger: typed numbers, including the wrong "18"; rates hardcoded in the generator; rounds from a separate `fair_bakeoff.py` run. · **major** · Reword it, or turn the typed numbers into tokens. · yes

16. **Figure 11 caption "Blue square: the value the detector ships with"** · SPIKE-synch ships at 0.1, which is not on its list (0.005–0.12), so its panel has no square. · **minor** · Say so in the caption. · yes (image)

17. **§8 SPIKE-synch "every round chose the lowest value, 0.005"** · 0.005, 0.01 and 0.02 give identical scores, so the pick is tie-breaking, not a choice. · **minor** · State the tie. · yes

18. **§4.1 "how many arrived in the last second"** · The 1-second window is centered on each moment, not trailing (`train_rate`). · **minor** · "in the 1-second window around each moment." · yes

19. **§6 busy block "every ROI fires at 60 mHz"** · 60 mHz is added on top of each ROI's own background, and ramps in over the first 30 s. · **minor** · Reword. · yes

20. **Table 1, tiny (and trace) rows** · Precision 0.92 and 0.0 busy-block calls/min are artifacts. tiny makes one call spanning the whole recording, which one-to-one matching scores as one hit (recall 1/15 = 0.067). · **minor** · Footnote it. · yes

21. **Figure 10D caption** · The values are medians across ROIs of variance ÷ mean, which the caption does not say. "Closer to real than flat" holds only on a ratio scale: in absolute terms flat is closer at 30 s and 60 s. Also, the document's finding that the simulator over-bunches reverses `bench.py`'s `MEASURED_BURST_SHAPE` docstring ("coarse end is still short"). That table appears to put real *means* beside fitted *medians*; the document's like-for-like comparison looks right, so the docstring is what needs correcting. · **minor** · Say "median", and reconcile with `bench.py`. · yes

22. **§8 speed "the slowest … 9,786×"** · This is the quiet background only; at busy, LoCo is slowest at 8,143×. · **minor** · Add "at the quiet background". · yes

23. **§12 "All six … first written in MATLAB in the same lab"** · locust derives from CICADA (Cossart lab) and SPIKE-synch from Kreuz's measure, through MATLAB ports in the lab's own interface2 MATLAB code. The 1e-9 figure is an absolute tolerance, not "one part in a billion". · **minor** · "Python versions match the lab's MATLAB versions to 1e-9 on test fixtures." · yes

24. **Figure 8 caption "score cannot exceed about 0.16"** · A participant's event can also coincide with a background event in a non-participating ROI, so 5/32 is not a hard ceiling. · **minor** · "rarely exceeds". · yes (`adaptive_profile`)

25. **Figure 12 caption "C: … one line per detector"** · The code draws one set of points per event size, not a line per detector. · **minor** · Match the caption to the plot. · yes (code)

26. **Unit membership** · The 84 pooled baselines in Figures 2B and 10C/D include the four recordings the producer flags for pinned ROIs. The document does not say so. · **minor** · Note it, or exclude them as a sensitivity check. · yes (`current_export.toml`)

## Relevant files
- `<worktree>\tools\detector_review_template.html`
- `<worktree>\tools\make_detector_review.py`
- `<worktree>\src\bugarach\detect_folder.py`
- `<worktree>\src\bugarach\detectors\cicada.py`
- `<worktree>\src\bugarach\detectors\sce.py`
- `<worktree>\src\bugarach\simulate.py`
- `<worktree>\src\bugarach\learn\train.py`
- `<worktree>\src\bugarach\bench.py`
- `<worktree>\tools\fair_bakeoff.py`
- `<scratchpad>\review\_work\numbers.json`
- `<scratchpad>\run\baseline_quiet\` and `...\run\baseline_busy\`
