GRANT 1 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash)

(I searched with `git grep` and `grep` through Bash instead, so no check was skipped because of the missing tools.)

# Claim and data check: slow co-modulation explainer, round 2

**Result:** almost every number on the page matches `summary.json`, which is byte-identical to `<scratchpad>/run2`. Four problems are real, though:
- Two claims are contradicted by the evidence they cite: the block-control claim that points at Figure 4, panel A, and the "5.4 s is past the dead-time floor" argument.
- One statement about the repository is false: that the group names are "not written down in this repository".
- The darkroom copy of the page is still the draft from before the first review, including a claim that review withdrew.

## What I recomputed and how
- **The numbers:** I read every quantity from `summary.json` and `results.json` myself, not from the figures.
- **Lab export (field-step-excluded folder):**
  - Opened `slices.csv`, `regions.csv`, `field_steps_excluded.tsv` and `PROVENANCE.md`.
  - Recounted the field steps that fall inside baseline windows.
  - Recomputed the shortest interval between two onsets of the same ROI, over the full baseline windows.
  - Checked that no imaging date holds more than one group.
- **Synthetic worlds:** regenerated recording 0 of the planted-event world to confirm that Figure 2, panel D is centred on a planted event.
- **Tests:** `tests/test_measure_slow_comodulation.py` gives 10 passed.
- **Other branch:** read the small-J results and the `count_excess` definition with `git show` from `origin/unsup/rigid-shift-report-residuals`.
- **Papers:** checked Perkel, Brody, Louis, Harris and Stella against the PDFs on the darkroom reading shelf.
- **Previous version:** compared against the pre-review draft in commit `8ba5f57`.

## Claim ledger (quoted · source · recomputed · verdict)

**Figure 1 and the table of numbers behind Figures 1 and 5** (`summary.json`: `var_ratio`/`var_lo`/`var_hi`, `checks`)
- Lab fast, as recorded, at 1 s / 10 s / 1-minute bins: 1.98 [1.59, 2.48] / 2.69 [2.10, 3.33] / 3.21 [2.47, 3.97]. Recomputed 1.977 / 2.685 / 3.211, intervals the same. **match**
- Lab fast, other arms (1 s / 10 s / 1-minute bins):

  | arm | page | recomputed | verdict |
  |---|---|---|---|
  | rigid shift *J* 20 s | 1.09 / 1.88 / 3.00 | 1.092 / 1.880 / 3.003 | match |
  | block control | 1.07 / 1.69 / 2.75 | 1.066 / 1.689 / 2.752 | match |
  | episodes removed, then block control | 0.96 [0.90, 1.00] / 1.41 / 2.27 [1.71, 2.87] | upper bound at 1 s is 1.0012 | match |
- Lab slow, all four rows. **match** (9.06 / 11.76 / 11.37; 1.24 / 3.88 / 9.86; 0.86 / 1.28 / 1.76; 0.59 / 0.79 / 1.48, all intervals included)
- Dard et al., three rows. **match** (9.69 / 15.54 / 15.23; 1.42 / 4.49 / 12.38; 1.17 / 2.54 / 9.33 [7.68, 11.36])
- Benchmark generator 1.67 / 4.52 / 8.94, and rigid shift 8.8 at 1 minute (1.665 / 4.520 / 8.941; 8.820). **match**
- "About a tenth of the 1-minute excess" removed by rigid shift: (3.211 − 3.003) / 2.211 = 9.4 %. **match**
- Paired differences:

  | contrast | page | recomputed | verdict |
  |---|---|---|---|
  | fast, as recorded − rigid shift | 0.21 [0.10, 0.34] | 0.209 [0.102, 0.338] | match |
  | fast, as recorded − episodes removed then block | 0.94 [0.55, 1.37] | same | match |
  | slow, as recorded − rigid shift | 1.50 [0.56, 2.41] | same | match |
  | slow, as recorded − episodes removed then block | 9.89 [6.13, 12.84] | same | match |
  | Dard, as recorded − rigid shift | 2.85 [1.77, 3.95] | same | match |
- Per-recording figures. **match**
  - Fast: 1.52 [1.11, 2.70], 83 %; after removal and block 1.28 [0.87, 1.85], 69 %.
  - Slow: 1.92 [1.09, 7.03], 80 %; after removal and block 1.065 [0.806, 1.422], 54.8 %.
  - Dard: 13.34 [8.28, 19.00], 100 %; block control 7.72 [4.72, 12.03], 100 %.
- Five heaviest recordings hold 47 % / 62 % / 28 % of pairs; dropping them leaves 2.13 on fast and 1.34 on slow (0.467 / 0.617 / 0.281; 2.131 / 1.341). **match**
- Share of onsets removed: median 2.5 % fast and 6.8 % slow; weighted 7.2 % and 61 %. **match**
- Share of time the removed episodes cover, weighted: 1.3 % fast, 4.4 % slow (1.27 %, 4.37 %). **match**

**Figure 5 bullets** (`excess`, `lo`, `hi`; lag bin edges 0, 0.3, 0.6, 1.0, 1.4, 1.96, 2.74, 3.83, 5.35, 7.49 … 300 s)
- Fast peak +1.91 [+1.17, +3.13]; gone by about 1 s (0.108 at 0.6–1.0 s, 0.043 at 1.0–1.4 s). **match**
- Fast "trough at 1–2.7 s (+0.03 to +0.04 … negative with episodes removed)". Recomputed: 0.043 and 0.031 at 1–1.96 s, but **0.073 at 1.96–2.74 s**. With episodes removed: −0.040 and −0.023 at 0.6–1.4 s, then **+0.005 and +0.057**. **mismatch (minor)**
- Fast bump +0.15 [+0.09, +0.24] near 3 s (0.147 [0.087, 0.240]). **match**
- Fast shoulder +0.06 to +0.08 from 5 s to a minute; +0.05 at 56–78 s; about +0.07 after removal and block (0.061–0.078; 0.053; 0.058–0.071). **match**
- Fast peak halved by removal, +1.91 → +0.88 (0.878). **match**
- Fast recording "slightly below its own rigid shift" at 5–20 s. Rigid shift at 20 s reads 0.101 / 0.099 / 0.095 / 0.089 against the recording's 0.078 / 0.074 / 0.061 / 0.075. **match**
- Slow peak +20.8 [+16.5, +25.8]. Dip −0.56 / −0.51, which becomes +0.03 / +0.08 after removal. Rigid shift fills it in at +0.35 to +0.57. Without the five heaviest recordings the dip is −0.39 / −0.31. **match**
- Slow "shoulder beyond 20 s +0.10 to +0.16; +0.05 to +0.09 with removal". Holds for 20–110 s. Past 110 s the recording reads 0.090 and 0.055, and removal reads 0.037, 0.029 and 0.005. **partial (minor)**
- Dard peak +0.78 [+0.64, +0.96]; dip −0.05 [−0.09, −0.01] (upper bound −0.0146). **match**
- Dard "shoulder of about +0.01 out to 5 minutes". The 7.5–56 s bins read +0.001 to +0.006; only from 56 s on is it +0.009 to +0.012. **partial (minor)**

**Figures 2 and 4 (synthetic worlds)**
- Planted-event world: 0.0097 onsets per ROI per second, 3,525 s, 32 ROIs, 15 events of 3–7 ROIs. Recomputed from `generator_spec.json` and a regenerated recording: 5 + 5 + 5 events, with 3, 4 and 7 ROIs. **match**
- Panel D is centred on a planted event: the busiest 2 s bin is centred 0.35 s from one. **match**
- 20 s world starts near +0.7; falls to about +0.5 at *J* 10 s and +0.35 at *J* 20 s; barely moves at 1.6 s (0.677 → 0.505 / 0.355 / 0.663). **match**
- 5-minute world: rigid-shift curves lie on the recorded one (0.43 vs 0.40–0.43). The block control keeps most of it (0.32). **match**
- Benchmark shoulder about +1.0 out to a minute, from a dense block at 1,200–1,500 s and 0.06 onsets per ROI per second. Recomputed 1.05 → 0.96 out to 56 s. The dense block is drawn independently for each ROI but applies to every ROI (`simulate.py`, lines 776–788). **match**
- "Generator background reads zero; it varies each ROI's rate on its own." Recomputed −0.03 to +0.01, and the burst multiplier is drawn per ROI (lines 762–765). **match** (but see finding 14)
- **"The block control makes a flat excess from events alone (Figure 4, panel A)"** (line 181), and the tool docstring's "Measured … keeps a flat residue of planted events". Panel A's block-control curve reads **−0.015 to +0.005**, flat on zero, and its 1-minute variance ratio is 0.90. **mismatch (major)**

**Other quantities and facts**
- 84 recordings from 44 mice, 17–20 minutes, 26.9 h; fast and slow cover the same recordings. Recomputed from `slices.csv` and the results rows: the recording lists are identical and the 26.88 h matches. **match**
- Dard: 59 recordings from 32 mice, 19–25 minutes, 22.4 h, median 566 ROIs (19.2–24.8 min; 22.43 h; `n_roi_recorded` median 566, which includes 1,303 silent ROIs). **match**
- CoactDetect settings: fast 2 s / 60 s / α 10⁻⁴ (`bench.py`, line 239); slow 1 s / 120 s / α 10⁻⁶ (docstring, line 87); three or more ROIs. **match**. But "an episode is a run of flagged bins" leaves out the 3 s merge across gaps (`merge_gap_sec`). **minor**
- Field-step gap: three recordings, about 12 s. Recount: 3 steps fall inside baseline windows, in 3 recordings; 3 × 4 s = 12 s. **match**
- "No imaging date holds more than one group" (0 of 42 dates; no mouse on more than one date). **match**
- Heaviest mouse holds 37–48 % of a group's pairs on fast (0.374–0.479). **match**
- Shortest same-ROI interval "2.80 s … measured by a review role and not reproduced". **Reproduced: 2.80 s slow, 0.40 s fast.** The number matches; "not reproduced" is now out of date. The attribution to the extractor is the page's own inference, which the dead-time todo warns against (finding 4).
- "The dip reaches 5.4 s, past that floor, so this cannot be the whole account." **Contradicted by the recordings** (finding 4). **mismatch (major)**
- Small-J check: 0.669 and 0.522, at `65285fa` and `ef9fdc3`, sinusoidal modulation (0.669375; 0.521875; `np.sin`, 40 s period). **match**
- `count_excess` subtracts a 30 s moving mean (branch `tools/tube_self_supervised.py`, line 514). **match**. "Its scores … come from simulated folds" is only partly true: the branch also scores it on real recordings. **minor**
- Rigid-shift report, item 2 asks about "10–45 s"; the report has not been re-reviewed (report line 395; the handoff at `57e2655` still waits on the blind round). **match**
- Test descriptions: brute force out to 300 s (L = 5,000 frames), plus the other checks listed. **match**; 10 passed.
- "About 3 minutes on 8 workers": elapsed 183 s matches. The worker count is **unverifiable**: this machine has 14 cores, so the default would be 12.
- **"Their expansions … are not written down in this repository."** They are, in `tools/build_surrogate_report.py` (lines 1357–1358) and `docs/proposals/2026-09-10-surrogate-evaluation-overnight.md` (line 88). **mismatch (major)**
- Citations:
  - Perkel p. 428 ("Linear trends result in a uniformly elevated cross correlation, which remains flat"): **match**
  - Brody, rule of thumb 3 (the integral equals count covariance): **match**
  - Louis §17.3.3 quote, which credits Pipa 2008 and Harrison & Geman 2009 and rolls the train with `% tmax`: **match**
  - Harris abstract ("circular shifting … up to 100% false positive"): **match**
  - Stella 2022 at 25 ms: **match**
  - P5–P12, CA1, CC-BY-4.0, and the authors' per-cell circular shift (PROVENANCE, GLOSSARY line 390): **match**
- **Unverifiable in the tree:** the eLife article number e78116; Dard et al. tying activity to the pups' movement; Date et al. 1998 as interval jitter; Amarasingham 2012 on "zero-lag counts".

## Record of design and unit membership
- **Where it is:** the lab export's `slices.csv` (`group_id`, `mouse_id`, `date`). No value is missing in any of the 84 rows. The group codes match `results.json` for every row, and no mouse falls in two groups.
- **Withdrawn recordings:** PROVENANCE lists one recording excluded by the lab database's exclude flag, and it is absent from the folder. The count reconciles at 84.
- **Units that share a subject:** the pooled intervals resample mice, which is correct. The "share of recordings above 1" figures count recordings as units (84 recordings from 44 mice); see finding 15.
- **Dard:** `slices.csv` has 32 subjects with nothing missing.

## Comparison with the previous version (`8ba5f57`)
- Row counts are unchanged (84/44 and 59/32).
- Dard hours fell from 22.7 to 22.4. That fits the new start at each recording's first onset (median lead-in 17.2 s × 59 ≈ 0.28 h).
- The peaks changed (fast 2.06 → 1.91, slow 21.94 → 20.8, Dard 0.83 → 0.78). The commit message attributes this to counting zero lag once and to the new bins. I did not recompute the old values.
- **Withdrawn claim:** "no benchmark in this repository contains a shoulder". Its replacement is verified: the dense-block world reads +1.35 flat, while the background and planted-event worlds read about 0.
- **Claim that survived the change of world:** the old events world (32 events of 7 ROIs in 1,200 s) kept +0.04 flat under the block control. The new world from the repository's generator keeps about 0, but the sentence citing panel A was not updated. That is finding 1.

## Findings

| # | location | issue | severity | suggested fix | verified |
|---|---|---|---|---|---|
| 1 | README lines 180–182 ("the block control makes a flat excess from events alone (Figure 4, panel A)"); lines 143–146 under "Measured"; `tools/measure_slow_comodulation.py` docstring lines 39–41 | Panel A's block-control curve is −0.015 to +0.005, and its 1-minute variance ratio is 0.90. The claim came from the retired 32×7-event world (+0.04) and outlived the switch to the generator. The lab data do give some support: on fast at 1-minute bins the block control reads 2.75 against 2.27 after removal, a paired difference of 0.46 − 0.94 ≈ 0.48. | major | Cite the lab difference between the block control with and without removal instead of panel A, or plant events large enough to show it. Fix the docstring the same way. | yes |
| 2 | `<darkroom>/bugarach/2026-09-17-slow-comodulation/README.md` | Byte-identical to the pre-review draft at `8ba5f57`. It repeats the withdrawn "no benchmark … contains a shoulder" and links to `fig1_three_kinds.png` and `fig3_recordings.png`, which the figure script has deleted. The figures and `summary.json` beside it are current, so the copy a person opens mixes the new figures with the old text. | blocking (for delivery) | Copy the reviewed README to the darkroom, or remove the stale copy. | yes |
| 3 | lines 336–338 | "Not written down in this repository" is false. `tools/build_surrogate_report.py` (lines 1357–1358) and the overnight surrogate proposal (line 88, citing `slices.csv` `group_id`) give the same expansions. The export itself carries only the codes. | major | Say the expansions are in those two files, and that they are this repository's reading, not the producer's. | yes |
| 4 | lines 201–206 | Three problems with the dead-time argument. (a) "The dip reaches 5.4 s, past that floor, so this cannot be the whole account" treats 2.80 s as a hard floor. On the slow baselines, same-ROI intervals per second of interval are 15 (2.8–3.4 s), 95 (3.4–4.0), 333 (4.0–4.6), 771 (4.6–5.4), then about 1,070 (5.4–8 s). The depletion runs to about 5.4 s, the same place the dip ends, and the per-ROI median shortest interval is 8.7 s. (b) The page says the extractor emits 2.80 s as its minimum, but that is an observed sample minimum; the dead-time todo says the true value is undeclared and must not be taken from the data. (c) "Not reproduced" is out of date: 2.80 s slow and 0.40 s fast reproduce. | major | Remove the rule-out, show the interval distribution, call 2.80 s the observed minimum, and say it is reproduced. | yes |
| 5 | lines 176–177 | The trough is at 1–1.96 s, not 1–2.7 s: 1.96–2.74 s reads +0.073. With episodes removed, the values are negative only at 0.6–1.4 s. | minor | "1–2 s (+0.03 to +0.04) … negative at 0.6–1.4 s with episodes removed" | yes |
| 6 | lines 187–188 | The slow shoulder values hold only out to 110 s. Past that the recording reads +0.09 and +0.055, and removal reads +0.04 down to +0.005. | minor | State the lag range, 20–110 s. | yes |
| 7 | line 194 | "About +0.01 out to 5 minutes": the Dard curve reads +0.001 to +0.006 at 7.5–56 s. | minor | "+0.00 to +0.01, about +0.01 beyond a minute" | yes |
| 8 | line 30 | "Back to chance (1.09)", but the interval [1.06, 1.13] excludes 1. | minor | "close to chance" | yes |
| 9 | lines 264–268 | "A 10–45 s component … not bounded here." `summary.json` holds the 10 s-bin paired difference, as recorded − rigid shift at 20 s: 0.81 [0.39, 1.35]. That bound is mixed up with the events but not absent, and the page doesn't report it. | minor | Report it, and say it is not separated from the events. | yes |
| 10 | line 169 | "An episode is a run of flagged bins", but runs separated by 3 s or less are merged (`merge_gap_sec=3.0`). | minor | Add "merged across gaps of up to 3 s". | yes |
| 11 | lines 387–388 | "The circular arm reads zero … by construction": only the variance ratio of 1 holds by construction. The excess is zero only in expectation, and the test allows up to 0.1. | minor | Separate the two. | yes |
| 12 | line 382 | "About 3 minutes on 8 workers": the 183 s is verified, but the worker count is not recorded and the default here would be 12. | minor | Record `--jobs` in `results.json`, or drop the worker count. | no |
| 13 | lines 283–284 | "Its scores … come from simulated folds": the branch also scores `count_excess` on real recordings (6.29 events per 10 minutes; 0.903 of them in 3 or more ROIs). | minor | "its planted-truth F1 scores come from simulated folds" | yes |
| 14 | lines 233 and 46–48; synthetic numbers have no interval | The background world, independent by construction, reads 0.88 at 1-minute bins (the planted-event world reads 0.90). Differences between synthetic worlds of about 10 % (for example 8.94 against 8.82) are inside that spread. | minor | Say how much synthetic ratios scatter, or add an interval over generator seeds. | yes |
| 15 | lines 33, 41, 251–253 | Per-recording shares count 84 recordings from 44 mice as units. | minor | Say they are counts of recordings, or add a per-mouse version. | yes |
| 16 | lines 342–344 (Figure 6) | "Every group's pooled curve sits in a similar low band after removal and blocking." On fast, DI reads 0.11–0.12 while the others read 0.04–0.06. On slow, MALE's pooled curve is also high (0.14–0.19 against 0.01–0.07), not only its equal-weight curve. | minor | Describe DI on fast and MALE's pooled curve on slow as higher. | yes |
| 17 | lines 294–295, 369–370 | Dard et al. tying activity to the pups' movement, and the article number e78116, have no source in the tree. | minor | Cite a page or section, or mark them unverified. | no |

## Relevant paths
- `<worktree>/docs/learned/slow_comodulation/README.md` and `summary.json`
- `<worktree>/tools/measure_slow_comodulation.py` (docstring lines 39–41)
- `<worktree>/tools/make_slow_comodulation_figure.py`
- `<worktree>/tools/build_surrogate_report.py` (lines 1357–1358)
- `<worktree>/docs/proposals/2026-09-10-surrogate-evaluation-overnight.md` (lines 79, 88)
- `<worktree>/docs/todo/2026-09-10-the-dead-time-floor-is-the-producers-number.md`
- `<worktree>/src/bugarach/detectors/coact.py` (lines 73, 245–256)
- `<darkroom>/bugarach/2026-09-17-slow-comodulation/README.md` (stale copy)
- `<scratchpad>/review2/r1/dump.txt` (full dump of the recomputed quantities)
