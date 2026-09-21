GRANT 1 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash only)

That mismatch is a finding about the run, not the page. I did the Grep and Glob searches with `grep` and `find` through Bash, so no check was skipped. The run record's `roles:` line should still say this role ran on a fallback grant.

**Contamination disclosure.**
- **Leak-test rows at three declared displacements were exposed.** To check the page's claim that rigid shift was "not detected to 1.6 s fast, 1.4 s slow, four frames on Cossart", I had to read the rigid-shift rows at those three displacements. All three are declared. I do not report their accuracies or P values.
- **Status only at the other declared displacements.** For 2.5 s fast, 2.8 and 5.6 s slow, and 8 and 16 frames on Cossart I read only whether the row returned a number, and the fast void flag. No accuracies.
- **The page's own quoted range points at a declared row.** The rows from 0.1 to 1.6 s do not reach the upper end of the page's "0.495–0.524". So that upper end belongs to a row at a displacement the page declares. The page already prints that value, so I repeat nothing new.
- **Nothing computed for destruction or count.** No destruction retained share and no count outcome for rigid shift at any displacement.

## Claim ledger

| # | Quoted claim | Cited source | Recomputed | Verdict |
|---|---|---|---|---|
| 1 | Rigid shift: each ROI's whole train moved by one offset in ±*J*, nothing wrapped | `surrogates.rigid_shift` | Elephant `dither_spike_train(shift=J, edges=True)`, one offset per ROI, onsets outside the window dropped | match |
| 2 | Not detected out to 1.6 s fast, 1.4 s slow, 4 frames Cossart | the join todo | Not significant at those three. **But slow 0.7 s was detected**: accuracy 0.5167, P = 0.005. So "to 1.4 s" is not a contiguous range | partial mismatch |
| 3 | 1.6 s is "the largest leak-free value" | join todo | Needs the 2.5 s row, which is off-limits | unverifiable (contamination rule) |
| 4 | Fast accuracies "there" were 0.495–0.524 | join todo | The five rows from 0.1 to 1.6 s span 0.4952–0.5137. The page's range comes from the voiding todo's "all six *J* values", which includes 2.5 s | mismatch in scope |
| 5 | Every fast row voided by the seed-0 defect | voiding todo | All 6 fast rigid-shift rows void. 126 of 248 fast candidates void, 122 intractable, one void reason | match |
| 6 | Seed-0 negative control: 0.539, P = 0.035, 830 pairs; 20 seeds flag at 0.05, mean 0.4948 | `negative.json`, `negative_seeds.json` | 0.5386, 0.035, 830; flag rate 0.05, mean 0.4948; slow and Cossart 0.0 | match |
| 7 | The other survivors moved onsets by one frame | join todo | Interval and pattern jitter at 0.1 s or 1 frame. Do-nothing moves nothing at all | match (minor wording) |
| 8 | Uniform dither is known to leak | discriminator CSV | 12 of 12 cells significant on every stream. Cossart at 1 frame: 0.742, P = 0.005 | match |
| 9 | **Joint-ISI was never measured** | goal page, joint-ISI todo | **Leak test returned numbers at 36 joint-ISI cells**: fast 2.5 s (12, voided), slow 5.6 and 11.2 s (24). All significant, accuracy 0.60–0.73. ISI dither: 34 cells, all significant. Only Cossart is fully intractable | **mismatch** |
| 10 | 84 recordings, 44 mice, four groups, frame interval 0.1 s | `dataset.current("steps_excluded")` | 84; 44 mice (35 with more than one recording); MALE 22, ORX 25, OVX 20, DI 17; frame interval 0.1 s for all 84 | match |
| 11 | Cossart median 566 ROIs | cossart folder | 566.0; 59 recordings, 32 mice; frame interval 0.0926–0.1190 s | match |
| 12 | No unused baseline recordings | `current_export.toml` | Every lab folder is a view of the same 84 recordings; Cossart was used | match |
| 13 | Four motion-pinned recordings, which the report can name | `current_export.toml` | Named there: 20260629_312, 20260629_309, 20260630_316, 20250926_235 | match |
| 14 | Baseline only; zero-event ROIs stay in (FOUNDATIONS §9) | §9 | Both rules are in §9 | match |
| 15 | 98.3 % = Bonferroni over three | arithmetic | 1 − 0.05/3 = 0.98333. Whether it is one-sided or two-sided is not stated (z = 2.128 or 2.394) | ambiguous |
| 16 | 0.55 is "the screen's own smallest effect worth detecting" | `MIN_EFFECT`, plan Table 4 | 0.55 in both | match |
| 17 | 60 s windows, mouse-grouped folds, 199 within-pair permutations | discriminator, `ss.ANALYSIS_WINDOW_SEC` | 60.0 s; 5 folds grouped by mouse; `n_permutations=199` | match |
| 18 | "Coordination-blind": per-ROI features, pooled only by symmetric statistics | `ROI_FEATURES`, `pool_symmetric` | Count, interval quantiles, shortest interval, edge bands; mean, sd, min, median, max, plus two shares | match |
| 19 | Bootstrap over mice, 2,000 resamples, using `mouse_bootstrap` | `measure_recording_identity.py` | `N_BOOT = 2000`, but **percentiles are hard-coded at [2.5, 97.5]**. The function cannot produce a 98.3 % interval, and it lives in a tool, not the library | **mismatch** |
| 20 | "Three or more happens 7.5 %, four or more 1.6 %" | binomial | At a per-seed rate of 0.05: 7.55 % and 1.59 %. The code flags on `p < alpha`, and with 199 permutations the exact size is 9/200 = 0.045: 5.9 % and 1.1 % | minor mismatch |
| 21 | `edge_thinning` deletes onsets near the window edges | `surrogates.edge_thinning` | Uniform dither within each 60 s window, dropping what leaves it. Expected loss is *J*/120 of onsets. A 2M-draw Monte Carlo gives 1.337 % at 1.6 s, 1.173 % at 1.4 s, 2.087 % at 2.5 s, 2.326 % at 2.8 s | match; consequence in the first blocking finding |
| 22 | Destruction bin was ±2 frames (0.5 s) | `DESTRUCTION_HALF_WINDOW_FRAMES` | 5-frame bin = 0.5 s | match |
| 23 | "The assessor uses **1.0 s**", "the assessor's own definition" | `assess.py` | 1.0 s default, documented as "the MATLAB default for the **faster** stream". LoCo's per-stream bin defaults are **(1.0, 2.0) s** | true for fast; unsupported for slow |
| 24 | Twins "with the stream's own per-ROI counts and floor" | screen tool, lines 550–560 | One twin at the median ROI count and length. Counts are a Poisson resample of per-ROI rates pooled across all recordings and groups; floor is 1× the observed floor | loosely true |
| 25 | Retained = what the planted twin keeps, as a share of before | `destruction` | Actually (planted − unplanted) after ÷ (planted − unplanted) before | description incomplete |
| 26 | Participation 0.2 and 0.5; the assessor's K scan | constants | (0.20, 0.50); K = (3, 4, 6, 8) | match |
| 27 | Do-nothing ≥ 0.9 shows "the measure sees coordination that survives" | code, exploratory destruction.csv | Identical trains plus the fixed assessor seed (20260722) give **1.0 by construction**. Observed 0.99999–1.0 at every visible K, on both streams and Cossart | **self-description false**: the control cannot fail |
| 28 | Circular shift is the assessor's own null | assess.py, review record | `assess_coactivity` draws its null from `circular_shift_trains` | match |
| 29 | Cossart: "the measure registered no removal at any setting" | review record | The source says every Cossart radius is **saturated**. Homogeneous resample on Cossart retained −0.0007 to 0.013, which is removal registered | overstated |
| 30 | "The discriminator has no command-line entry point today" | tree | `tools/probe_discriminator.py` has argparse and `__main__` and runs the discriminator's two controls | mismatch (minor) |
| 31 | "Rigid shift is one of the cheapest generators" | `run_notes.json` cost probe | 2.8 s per draw, 12th of 16 generators excluding joint-ISI. Cheap only next to joint-ISI (73–159 s) | mismatch (minor) |
| 32 | Slow *J* follows "the same logic on the slow grid" | `J_SEC["slow"]` | Grid is 0.7, 1.4, **2.5**, 2.8, 5.6, 11.2. The next step after 1.4 is 2.5, not 2.8 | **mismatch** |
| 33 | Fast 5.0 s is "double that" | grid | Correct, but 5.0 s was never measured, and it is past the 2.5 s point where 50.4 % of fast intervals already sit inside 2*J* | match; undisclosed |
| 34 | Stopped because "it felt like going in circles" | handoff | The handoff records "Stop here for now" and that family size needs discussion. The phrase appears nowhere in docs | unverifiable |
| 35 | "Fresh randomness — new surrogate seeds, new mouse folds" | code | Surrogate keys are crc32 of (recording, stream, cell id, draw). Twin seeds are keyed on (role, stream, participation). Assessor seed is fixed. `forced_choice` seed defaults to 0. The exploratory keys lived in scratch scripts outside git | not guaranteed; unverifiable |
| 36 | Declared *J* were chosen from exploratory evidence | discriminator CSV (status only) | **Every declared *J* except 5.0 s fast already has a leak row that returned a number**, and destruction rows too | undisclosed |

**Sources the page did not consult.**
- **Group membership.** `slices.csv` has `group_id` and `mouse_id`. FOUNDATIONS §9 says "a pooled across-group number … is not admissible on its own". Every gate on the page is pooled.
- **Field steps inside baseline.** `field_steps_excluded.tsv` has three removals inside baseline analysis windows: 20240708_17 (45 events), 20250826_192 (55), 20260122_259 (62). Each leaves an all-ROI gap of about 4 s that a shift of a few seconds would partly fill.
- **Recording identity measurements.** `recording_identity.md` measured real-vs-real intervals over mice: fast 0.523 [0.491, 0.556]. The page takes its bootstrap from this run but never uses the measured width.
- **Saturation arithmetic, checked.** With the review's formula (co-active in bin = recruited × bin / (2*J*+1)), a 1.0 s bin does not saturate at any declared *J*. No finding.

## Findings

| Location | Issue | Severity | Suggested fix | Verified |
|---|---|---|---|---|
| Count preservation, Control | **`edge_thinning` cannot fail the ±2 % gate at the smallest declared *J*.** It drops *J*/120 of onsets per 60 s window: 1.33 % at 1.6 s fast, 1.17 % at 1.4 s slow, both inside ±2 %. So the control passes and the count gate is void at exactly the displacements with exploratory evidence. At 2.5 s the expected loss is 2.08 %, a coin flip. The page also never says which *J* `edge_thinning` runs at | **blocking** | Amendment: a control whose expected loss is clearly outside ±2 % (e.g. `edge_thinning` at a fixed large *J*, or a declared thinning share), with its *J* stated | yes (analytic + Monte Carlo) |
| Leak, Pass / Intervals | **The declared interval cannot be computed as stated, and its width is uncertain.** `mouse_bootstrap` is hard-coded at 95 %. "Upper 98.3 % bound" does not say one-sided or two-sided. It bootstraps a fixed cross-validated correctness vector, which ignores refitting. On fast, the 20-seed spread of accuracy is **1.44× binomial** (95 % CI 1.10–2.10), so the interval is too narrow and passing is too easy. With intra-mouse correlation near 0 at 1,669 pairs, the gate passes any accuracy below about **0.521** (two-sided) or **0.524** (one-sided); with the seed-derived spread, below about 0.508 | **blocking** | Amendment: fix the sidedness; give `mouse_bootstrap` a level parameter with a test; decide whether the interval refits folds or is calibrated against the negative-control seed spread | yes |
| Leak, "the bound has to exclude one" | **The gate passes leaks the screen detected.** Slow rigid shift at 0.7 s was detected (0.5167, P = 0.005) and still falls inside the pass region above. A PASS means "no leak of 0.55 or more", not "no leak". Given the tube foot gun, a small count-driven leak is the one that matters | major | Report a PASS as "leak below 0.55 excluded", and put the permutation P beside every bound | yes |
| Outcome table, "Cossart leak at the passing *J*" | **Not defined.** Lab *J* is in seconds, Cossart *J* is in frames (4/8/16 frames ≈ 0.37–1.9 s over its 0.093–0.119 s intervals), and fast and slow may pass at different *J*. VIABLE and NARROWED cannot be told apart | **blocking** | Amendment: a declared mapping (e.g. Cossart passes at any declared frame *J*, or at a named one), plus a row for a void Cossart result | yes |
| Destruction, timescale | **"1.0 s, the assessor's own definition" does not carry to slow.** `assess.py` calls 1.0 s the default for the faster stream; the project's LoCo per-stream bins are 1.0 s fast and 2.0 s slow. A slow PASS at 1.0 s could leave 2 s coincidences in place | major | Amendment for slow: score at 2.0 s as well, and state which bin gates | yes |
| Destruction, Controls, do-nothing | **The control cannot fail.** Identical trains plus a fixed assessor seed give retained = 1.0 by construction (exploratory 0.99999–1.0 everywhere). It is the same circularity the page rejects for circular shift, and it breaks "each has a control that shows it can [fail]". The screen's existing graded control, freeze-half (0.29–0.47 in the withdrawn re-evaluation), is unused | major | Add freeze-half with a declared band; keep do-nothing only as a code check | yes |
| What protects this run | **"Fresh randomness" is not delivered by instruments run unchanged.** Surrogate keys, twin seeds, the assessor seed and the `forced_choice` default seed are all deterministic, and the exploratory discriminator's keys are not in git. A runner reusing cell ids would redraw the exploratory data exactly | major | Declare a salt or seed set and a test that the confirmatory draws differ from the exploratory ones | yes (code); exploratory keys unverifiable |
| Why rigid shift | **Undisclosed: every declared *J* except fast 5.0 s already has exploratory leak and destruction results**, and the page's quoted fast range includes one. The slow choice of 2.8 over the grid's next step, 2.5, is unexplained | major | Disclosure amendment: list which declared *J* were seen in the exploratory run and whether 2.5 s slow was skipped knowingly | yes (status only) |
| Why rigid shift, "Joint-ISI was never measured" | **False for the leak test.** 36 joint-ISI and 34 ISI-dither cells returned numbers on the lab folder, all detected. The conclusion (nothing else survived) holds; the stated reason is wrong, and so are the goal page and the joint-ISI todo | major | Correct to "intractable at small *J* and on Cossart; detected at every cell measured (lab folder, 2.5 s fast; 5.6 and 11.2 s slow)" | yes |
| Why rigid shift, "to 1.4 s slow" | Reads as a range. 0.7 s was detected, so slow evidence is one non-detection, not a run of them | major | Say "at 1.4 s only; 0.7 s was detected" | yes |
| Whole page vs FOUNDATIONS §9 | Every gate is pooled across the four groups; only the unchanged share is reported per group. Recording identity found DI slow baselines least stationary | major | Report every gate per group, descriptively, beside the pooled verdict | yes |
| Displacements, "same logic on the slow grid" | Next step after 1.4 s on the slow grid is 2.5 s, not 2.8 s | minor | Correct the why-column; the values stay signed | yes |
| Displacements, fast 5.0 s | Off the exploratory grid; past the 2.5 s ceiling reasoning (50.4 % of fast intervals within 2*J*) | minor | Say so beside the row | yes |
| Negative control, 7.5 % / 1.6 % | Assumes a per-seed rate of 0.05; the code's size is 0.045 (5.9 % / 1.1 %) | minor | Correct the rates or flag on `p <= alpha` | yes |
| Destruction, Cossart | "No removal at any setting" overstates it. Homogeneous resample registered removal; the source reason is saturation at every radius | minor | "saturated at every displacement" | yes |
| Destruction, Retained | The definition omits the unplanted-twin subtraction | minor | Quote the code's formula | yes |
| Count statistic | Counted on onset trains; the linked todo asks for counts after encoding (tube's input) | minor | Say which, or add the encoded count | yes |
| What has to be built | "No CLI entry point" is wrong (`probe_discriminator.py`). "One of the cheapest generators" is wrong (12th of 16). Elephant is needed for rigid shift, uniform dither, homogeneous resample and edge thinning, and it is not in the main venv | minor | Correct both; add the environment to the build list | yes |
| Data | Three field-step removals sit inside baseline windows: 20240708_17, 20250826_192, 20260122_259 | minor | Name them beside the motion-pinned four | yes |
| Why this page exists | "Felt like going in circles" is not in the recorded stop | minor | Cite the handoff's recorded words | no |

Files:
- `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md`
- `tools/measure_recording_identity.py`
- `src/bugarach/surrogates.py`
- `src/bugarach/surrogate_stats.py`
- `tools/probe_discriminator.py`
- `<darkroom>/bugarach/2026-09-11-surrogate-screen/discriminator/steps_excluded/discriminator.csv`
