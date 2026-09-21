GRANT 3 ok — Read, Grep, Glob

# Cross-Examiner findings: `docs/learned/slow_comodulation/README.md` (branch `unsup/slow-comodulation`, commit ab736cd)

I found 17 problems. Three stand out:
- **Row 1:** the page cites Figure 4, panel A for a result the run's own numbers contradict.
- **Row 2:** the page's reading of the slow stream conflicts with two companion documents, and it doesn't say so.
- **Row 3:** the event-free synthetic part of the benchmark goes by four different names across the page, its figures, the glossary and the goal page.

The large majority of numbers match `summary.json`; the list of what I confirmed is at the end.

**What I checked:**
- **The page against `summary.json`:** every number in the prose, the three tables in the "Numbers behind Figures 1 and 5" section, and the lag-bin edges. I checked the lab fast and slow streams, the Dard et al. dataset, the four groups, the synthetic worlds and the checks block.
- **The figures:** all six PNGs, against their captions, the prose and `tools/make_slow_comodulation_figure.py`.
- **The measurement tool and its tests:** the docstrings of `tools/measure_slow_comodulation.py`, and `tests/test_measure_slow_comodulation.py` against the Reproduce section.
- **Companion docs:**
  - `docs/GLOSSARY.md` (including its new shared-activity block)
  - `docs/INDEX.md`, the new slow shared modulation row
  - `docs/MILESTONES.md`
  - `docs/goals/unsupervised-learning.md`
  - `docs/learned/tube_self_supervised/README.md`
  - `docs/learned/recording_identity.md`
  - `docs/FOUNDATIONS.md` §5 and §9
  - `docs/export_folder_spec.md`
  - `docs/learned/generator_spec.json`
  - `src/bugarach/bench.py` operating points
  - the `coact_detect` docstring
- **Conventions:** figure numbers with names, "data" plural, bare enumerated labels, units, symbols, group order.

## Findings

| # | location | issue | severity | suggested fix | verified |
|---|---|---|---|---|---|
| 1 | README line 181 (*"the block control makes a flat excess from events alone (Figure 4, panel A)"*); lines 143–146, under "Measured, from Figure 4"; `tools/measure_slow_comodulation.py` docstring lines 39–40 (*"Measured on synthetic recordings it keeps a flat residue of planted events"*) | **The cited panel shows the opposite.** In the planted-event world the block control reads −0.015 to +0.005 in every lag bin, with intervals that include 0; Figure 4, panel A draws it on the zero line. The only measured sign that the block control keeps events is on the lab slow stream: +0.24 under the block control, falling to +0.10 once episodes are removed. So the "Two of the arms cannot rule drift in or out" caveat rests on a citation that does not support it, and the docstring states a measurement the run did not produce. | high | Drop the Figure 4, panel A citation. Either cite the lab slow drop (block control +0.24 → +0.10 after removal, Figure 5, panel E), or mark "keeps events" as argued and say that at the generator's event density the retention is not visible. Fix the docstring to match. | yes |
| 2 | README lines 50–55 and 186–192, against `docs/learned/tube_self_supervised/README.md` line 395–398 and `docs/MILESTONES.md` line 99 | **Two companions disagree with this page and it doesn't say so.** They read the rigid-shift contrast at 22–45 s as shared modulation that is present on lab slow and the Dard et al. dataset and absent on lab fast (flat at 0.50). This page finds instead: <br>• On lab slow, rigid shift at *J* = 10–20 s fills the event-aftermath dip at 2.7–5.4 s (−0.56 becomes +0.35 to +0.57), and the swings are mostly events. <br>• On lab fast, slow shared structure exists, but at a minute or more. <br>It also calls a 10–45 s component on fast "not excluded", without citing the companion's "absent". A reader holding both documents gets two readings of the same contrast. | medium | Add one sentence saying the slow-stream signal those two documents read as 10–45 s modulation may be partly the post-event dip. Cite the fast "flat at 0.50" result next to "not excluded". Flag the MILESTONES row as affected. | yes |
| 3 | README lines 47, 98, 148 ("dense block"); Figure 2 and Figure 4 labels ("no hot window"); `docs/goals/unsupervised-learning.md` line 58 and `docs/INDEX.md` line 145 (`hot_window`); `docs/GLOSSARY.md` line 330 ("promiscuity probe"); `generator_spec.json` line 83 | **Four names for one thing.** The page's prose never uses the glossary term "promiscuity probe", and "dense block" appears in no glossary. A reader can't tie the prose's "dense block switched off" to the figures' "no hot window". | medium | Use "promiscuity probe" in prose and figure labels, and gloss it once as `hot_window`, 1,200–1,500 s. Or add "dense block" to the glossary as a synonym in the same change. | yes |
| 4 | README lines 83–87 (*τ* for the lag); `docs/GLOSSARY.md` line 360; goal page line 30 | **The symbol τ is already taken.** In the glossary and on the goal page, τ is the dead time. This page uses *τ* for the lag between onsets, then discusses extractor dead time at line 201. | medium | Rename the lag (for example *ℓ* or *Δt*), or cite the glossary and say τ here is not dead time. | yes |
| 5 | Numbers-behind-the-figures table (README lines 220–233) against Figure 1 | **The table is titled "Numbers behind Figures 1 and 5" but doesn't match Figure 1.** <br>• Plotted but missing from the table: lab slow block control (1.16, 2.94, 9.14); benchmark generator rigid shift at *J* = 20 s (1.47, 4.24, 8.82) and block control (1.43, 3.94, 8.40). <br>• In the table but not plotted: "lab slow, episodes removed". <br>• Line 27 says "read off Figure 1", but the 1.76× on line 40 is not in Figure 1, and the 8.8× on line 48 is not in the table. | medium | Add the three missing rows. Either plot the episodes-removed arm or label its row "not in Figure 1". Say where 1.76× comes from. | yes |
| 6 | Figure 6 legend (`make_slow_comodulation_figure.py` lines 385–389) | **The legend's percentages are fast-stream only, but the slow panels share the legend.** "Heaviest mouse 43/48/46/37 % of pairs" comes from the fast stream (`G0 = names[0]`). Panels B and D are slow, where the heaviest mouse holds 52 %, 56 %, 64 % and 64 %. The text (line 340) correctly says "on the fast stream"; the legend doesn't. | medium | Label the shares "fast stream", add the slow shares, or give each column its own legend. | yes |
| 7 | README lines 29–48 and 327–328, against FOUNDATIONS §9 | **The headline pooled numbers have no per-group numbers beside them.** Every headline is a pooled count-variance ratio. Figure 6 splits only the correlogram, so no per-group count-variance ratio appears anywhere, though `summary.json` holds them. For example, fast at 1 minute after removal and block control: DI 2.54, MALE 1.90, ORX 1.64, OVX 2.52. FOUNDATIONS §9 admits no pooled number without per-group numbers beside it. | medium | Add a per-group count-variance row, or a Figure 6 panel, for the numbers the headline rests on. | yes |
| 8 | README lines 337–338 (*"not written down in this repository"*) | **The group expansions are already in the repository.** `docs/proposals/2026-09-10-surrogate-evaluation-overnight.md` line 88 spells them out ("ORX and OVX are gonadectomized males and females, DI intact females in diestrus, MALE intact males"). FOUNDATIONS line 383 and `bench.py` line 317 use "diestrus". The page's wording also differs: "orchidectomised males" against "gonadectomized". | medium | Cite that file and use its wording, or say which source is authoritative. | yes |
| 9 | `make_slow_comodulation_figure.py` line 20 (*"None holds a real raster (FOUNDATIONS §5)"*); `measure_slow_comodulation.py` line 453 | **The citation reads §5 as a raster rule, which it isn't.** §5 says "anything derived from real data" stays machine-local, and allows one exception by name. The committed `summary.json` and Figures 1, 5 and 6 are derived from real data. Other learned pages commit real-derived figures too, so the conflict is project-wide, but these docstrings name §5 as the authority for something it doesn't say. | medium | Cite the ruling that actually permits committing pooled real-derived summaries, or raise the gap with §5 as a separate item. | yes |
| 10 | README lines 175–176 (*"A trough follows at 1–2.7 s (+0.03 to +0.04 … negative with episodes removed)"*) | **The 1.96–2.74 s bin doesn't fit the description.** As recorded it reads +0.073, not +0.03–0.04. With episodes removed, the curve is negative only at 0.6–1.4 s (−0.04, −0.02); it reads +0.005 at 1.4–1.96 s and +0.057 at 1.96–2.74 s. | low | Say "at 1–2 s (+0.03 to +0.04), below the block control; negative at 0.6–1.4 s with episodes removed". | yes |
| 11 | README lines 193–196 (Dard et al. "shoulder of about +0.01 … out to 5 minutes"; "the 9× count swing of Figure 1") | **The Dard et al. curve is described as flat, but it rises.** It reads +0.001 to +0.006 at 10–56 s (lower bounds below 0) and climbs to +0.009–0.012 at 56–300 s. Also, "9×" is the block-control ratio (9.3×); as recorded, line 43 gives about 15×. | low | Describe it as near zero out to about a minute, then +0.01 out to 5 minutes. Say the 9.3× is under the block control. | yes |
| 12 | README line 13 (*"Numbers from recordings carry a 95 % interval"*) | **Many recording numbers carry no interval.** Examples: the per-recording medians, the leave-five-out values, "+0.06 to +0.08", "−0.56 and −0.51", "+0.35 to +0.57", "+0.10 to +0.16", and the Dard et al. "+0.01". | low | Change it to "headline pooled numbers carry…", or add the intervals. | yes |
| 13 | README lines 41, 88, 255, 340 ("onset pairs") | **The weighting basis is never named.** Every weight — heaviest mouse, the five heaviest recordings, the pooled removal share — uses *expected* pairs at lags of 0.3–300 s (`exp[1:]`), not observed pairs. Also, "weighted that way" on line 42 reads as if it meant the five heaviest recordings, but the weighting covers all recordings. | low | State the basis once ("expected onset pairs at lags of 0.3–300 s") and use it in all four places. | yes |
| 14 | Figure 3, panel D; generator lines 272–300 | **The 2-minute block edge is drawn on the raster and hides an onset.** ROI 4's second-block onset lands at exactly 120 s (190 − 120 + 50 = 120), under the dashed edge. The caption's "every ROI keeps its onset count in every block" can't be checked by eye for ROI 4. This also breaks the CLAUDE.md "nothing drawn on the raster" rule. | low | Change ROI 4's block offset so the onset clears the edge, and move the edge marker into a lane above the raster. | yes |
| 15 | Generator docstring lines 20–21 (*"not in titles over the plots"*) against Figure 2, panels D–F and Figure 3, panels A–D | **Both figures put text titles above their panels**, which the docstring says they don't do. Figure 3's titles describe each surrogate. | low | Move the titles into y-axis labels or the caption, or correct the docstring. | yes |
| 16 | README lines 6, 17–19, 22, 27, 107, 134, 173, 181, 184, 196, 272, 327, 345 | **Convention breaks:** <br>• "item 2 of *What waits on Tony*" is a bare enumerated label; the goal page's "decision 2" is the same. <br>• Figure references in the prose give the number without the name. <br>• Each figure's alt text title differs from its caption title (Figure 1: "How much the population count swings…" against "How much more the number of onsets swings…"), so each figure has two names. <br>• Figure 1's caption uses *J*, CoactDetect and ROI before the page defines them (lines 61, 78, 166). | low | Name the question ("the shared-modulation question"). Write "Figure 4, what the surrogates remove". Make alt text and caption titles match. Define *J*, ROI and CoactDetect before Figure 1, or in its caption. | yes |
| 17 | Figure 6 against Figures 2, 1 and 5 (colour) | **Group colours reuse meanings from other figures.** OVX pink (`#e7298a`) is the 20 s world's colour in Figure 2. ORX brown is close to the 5-minute drift's brown. DI green is close to the CoactDetect green in Figures 1 and 5. | low | Choose group colours that no other figure uses. | yes |

**Minor, not given rows:**
- The glossary's "oracle threshold" entry (line 419) now sits under the new shared-activity header. It looks like the new block was inserted above it (I did not check the cause).
- The page says "trough" for the lab fast stream and "dip" elsewhere; the glossary only defines "dip".
- The goal page (line 20) says "twenty-two hours of baseline" while this page says 26.9 hours per lab stream.
- Line 276 gives 0.669 and 0.522 without naming the metric.
- I could not check the lines that point at other branches (`65285fa`, `ef9fdc3`, `count_excess`) or the "three recordings, about 12 s" field-step gap.

**Confirmed against `summary.json` and the other sources:**
- **Count-variance ratios:** every cell in the count-variance table except the two cases in row 5, plus the paired-difference and per-recording tables.
- **Removal and weight shares:** 2.5 % / 6.8 % (median), 7.2 % / 61 % (weighted), 1.3 % / 4.4 % of time, and the heaviest-five shares of 47 %, 62 % and 28 %.
- **Leave-five-out values:** 2.13, 1.34, −0.39 and −0.31.
- **Peaks, bumps and dips:** +1.91, +0.15, +20.8 (dip −0.56 / −0.51), +0.78, and −0.05 [−0.09, −0.01].
- **Synthetic worlds:** +0.7 → +0.5 → +0.35, the 5-minute world unmoved by rigid shift, the benchmark generator's 8.94 / 8.82 and its +1.0 shoulder.
- **Recording counts:** 84 recordings from 44 mice and the group splits (17/10, 22/12, 25/12, 20/10). The Dard et al. dataset: 59 recordings from 32 mice, 566 ROIs (median), 22.4 hours, 19–25 minutes. The lab streams: 26.9 hours, 17–20 minutes.
- **Detector settings:** CoactDetect's fast and slow operating points.
- **Generator spec values:** 0.0097, 3,525 s, 15 events of 3–7 ROIs, `hot_window` 1,200–1,500 s at 0.06.
- **Peak delays:** 0.3 s and 2 s (export spec).
- **Groups and dates:** no imaging date holds more than one group.
- **Links and tests:** the report anchor exists, and the test descriptions in the Reproduce section match `tests/test_measure_slow_comodulation.py`.
- **Group order:** DI, MALE, ORX, OVX is the same everywhere it appears.
- **"Data" plural:** no violations.
