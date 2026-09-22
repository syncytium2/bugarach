GRANT 4 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash)

# Reviewer 2: slow co-modulation explainer at ab736cd

Two of the page's claims break when rerun. The count-variance numbers for the arms that remove CoactDetect's episodes are computed against the wrong reference. And about a third of the fast stream's minute-scale excess is a steady rise or fall in rate across each window, which the page says it cannot see. Four major findings and six minor ones follow.

I reran the committed tool's functions on the export folders and on synthetic worlds. My scripts and outputs are in `<scratchpad>/review2/r4/` (`recheck.py`, `recheck.json`, `syn_removal.py`, `syn_removal.json`). Before correcting anything, I reproduced the page's own numbers from its code exactly.

## Findings

**1. BLOCKING — wrong reference for every episodes-removed count-variance number.**
- **Location:** `<worktree>/tools/measure_slow_comodulation.py`, the `pooled()` function and the per-recording part of `checks()`.
- **What goes wrong:** the ratio is meant to compare the recording with a copy in which ROIs are independent. For the two removal arms, that reference is the circular shift of the *original* recording, not of the recording with episodes removed:
  ```python
  C = [unpack(r["arms"]["circular"]) for r in rows]
  ```
  That reference still holds the deleted onsets, so it is too large. Weighted as Figure 1 weights recordings, the deletion took 10.5 % of onsets on fast and 42 % on slow.
- **What I measured:** I recomputed with a circular shift of the removed trains, 8 draws per recording. At 1 s / 10 s / 1-minute bins:

  | stream, arm | page | corrected |
  |---|---|---|
  | fast, episodes removed | 1.25 / 1.62 / 2.45 | 1.38 / 1.80 / 2.61 |
  | fast, removed then block control | 0.96 / 1.41 / 2.27 | 1.06 / 1.57 / 2.42 |
  | slow, episodes removed | 0.86 / 1.28 / 1.76 | 1.48 / 2.16 / 2.72 |
  | slow, removed then block control | 0.59 / 0.79 / 1.48 | 1.02 / 1.33 / 2.28 |

  Per recording, the slow median after removal and block control goes from 1.06 (55 % of recordings above 1) to 1.24 (69 %).
- **The page explains the defect instead of catching it.** It says removal "can take a variance below 1: it empties the busiest bins". With the right reference, slow at 1 s reads 1.02. The values below 1 in Figure 1 panel B come from the reference, not from the data.
- **What else is wrong because of it:**
  - the slow bullet (1.76×, 1.48×, median 1.06×);
  - four table rows;
  - the paired differences 0.94 and 9.89;
  - the per-recording table;
  - the leave-five-out values 2.13 and 1.34;
  - the green bars in Figure 1;
  - the by-group count-variance ratios in `summary.json`.
- **The fast/slow contrast goes away:** once episodes are removed and the block control applied, both streams sit at about 2.3–2.4× at 1 minute.
- **Fix:** add a circular arm computed on the removed trains and divide by it. Delete the "empties the busiest bins" sentence. Add a test that removal on independent trains gives about 1 at 1 s bins.
- **Verified:** yes.

**2. MAJOR — at 1-minute bins, surviving rigid shift cannot tell drift from events.**
- **Location:** the first bullet under "What the page finds", and the first bullet under "What this changes for the label-free thread".
- **Why:** offsets of up to ±20 s leave most same-bin coincidences inside a 60 s bin, whatever produced them. The page's own table shows it:
  - the slow stream, which the page calls mostly events, keeps 87 % of its 1-minute excess under rigid shift (11.37 → 9.86);
  - Dard et al. keeps 80 %;
  - lab fast keeps 90 %.

  So "rigid shift leaves almost all of it" is no evidence that the structure is "not CoactDetect's events". The bullet presents the two as if one supported the other.
- **"Not bounded here" is not quite true.** The page says a 10–45 s component is "not bounded here". Its own 10 s row says rigid shift at 20 s removes 48 % of the fast excess (2.69 → 1.88). That figure also contains event spread, so it is an upper bound, but it is a bound.
- **Fix:** say that retention at 1-minute bins is expected from any source when *J* ≤ 20 s. By my own reasoning, not measured, pure events at *J* = 20 s would keep roughly 78 %. Quote the 10 s row as the bound.
- **Verified:** partly. The table numbers are checked; the 78 % is argued.

**3. MAJOR — a whole-window trend is visible, and it is about a third of the fast excess.**
- **Location:** the ⚠ note under the correlogram section ("cannot see a change in rate that spans the whole window"), and the first two bullets of "What this does not settle".
- **What the page gets wrong:** only a constant level across the window is invisible. A steady rise or fall inflates both the count variance and the short-lag excess; the Perkel page the page cites says a linear trend elevates the correlogram flat.
- **What I measured:**
  - I removed each recording's own straight-line trend from its 1-minute population count, and did the same to the circular copies. Fast drops from 3.21 to 2.46: the excess goes from 2.21 to 1.46. Slow drops from 11.37 to 7.12.
  - Onsets in the last third of the window ÷ onsets in the first third: median 1.18 on fast and 1.41 on slow. Rate rises in 58 % and 71 % of recordings.
  - Rate changes by more than a factor of 1.5, either way, in 57 % and 62 % of recordings.
- **What that means:** a large, mostly rising part of the "drift" is a trend inside the baseline window. The page's "timescale not resolved" is partly answerable with a test it did not run.
- **Fix:** add a detrended arm and report which way the trend goes. Put the rising rate to the producer, or check syncytium2 FOUNDATIONS §15; this repository should not guess its cause.
- **Verified:** yes.

**4. MAJOR — the headline was never split by group, and Figure 6 is misread (FOUNDATIONS §9).**
- **Location:** Figure 1, and the reading of Figure 6.
- **Count variance by group** (fast stream, 1-minute bins, per-recording median):

  | group | as recorded | removed then block control |
  |---|---|---|
  | DI | 2.94 | 1.79 |
  | MALE | 1.81 | 1.15 |
  | ORX | 1.20 | 1.09 |
  | OVX | 1.32 | 1.30 |

- **Correlogram, fast:** mean excess at 5–60 s after removal and block control is DI +0.103 [0.066, 0.225], against MALE +0.052, ORX +0.053 and OVX +0.038. In Figure 6 panel C, DI's pooled curve sits at about twice the others. The text calls this a "similar low band".
- **Correlogram, slow:** MALE's equal-weight curve is +0.28, against ≤ +0.08 for every other group.
- **Consequence:** the pooled "3×" rests disproportionately on DI. The ORX medians are close to the null (finding 5). Group is confounded with imaging day, so none of this is a group difference, but the page should describe what the figure shows.
- **Fix:** add a group-split version of Figure 1 using the corrected reference, and rewrite the Figure 6 reading.
- **Verified:** yes.

**5. MAJOR — ranking datasets by the ratio mostly ranks their ROI counts.**
- **Location:** the Dard et al. headline bullet, and the matching sentence on the goal page.
- **Why:** the ratio grows roughly as 1 + (*N* − 1) × the average correlation between pairs of ROIs, where *N* is the ROI count. Per pair, as (ratio − 1) ÷ (*N* − 1), median recording, 1-minute bins, as recorded:
  - lab fast 0.019;
  - lab slow 0.034;
  - Dard et al. 0.021.

  "Swings most" therefore reflects 566 ROIs against 31.5. Per pair, Dard et al. matches lab fast and is below lab slow. The page mentions this mechanism in one clause but still presents the ranking as a finding.
- **The Dard et al. block-control figure is not evidence of drift either.** "Still 9.3× under the block control" comes with no episode-removal arm, and the page itself says the block control keeps events.
- **Fix:** report the per-pair figure beside the ratio. Restate or drop "swings most", and caveat the 9.3×.
- **Verified:** yes.

**6. MINOR — "above 1 in 69 %" has no stated null.**
- **Location:** the fast bullet and the per-recording table.
- **What I measured:** I built a null that keeps each lab ROI's own timing: one circular copy scored against eight others. Median 0.92 with 42 % of recordings above 1 on fast; median 0.97 with 46 % above 1 on slow.
- **Consequence:** the fast 69 % is informative. The slow 55 % (before correction) was at the null.
- **Fix:** print the null beside the share.
- **Verified:** yes.

**7. MINOR — the pooled headline number and its robustness check use different weightings.**
- **Location:** "about 3× at 1 minute", and "dropping the five recordings with the most onset pairs".
- **What's off:**
  - "3×" is a ratio of summed variances; the median recording is 1.52×.
  - The leave-five-out check drops the top five recordings by onset pairs (47 % of pairs). Figure 1 weights by circular variance, where the top five hold only 25 %.
- **Fix:** put the median in the headline, and pick the five to drop by the same weight Figure 1 uses.
- **Verified:** yes.

**8. MINOR — the generator's ratios carry an artefact of how bins line up.**
- **Location:** Figure 1 panel D; no independent-world reference is shown.
- **Why:** the generator varies each ROI's rate on a fixed 60 s / 300 s grid. The circular reference scatters that grid against the 60 s count bins; the recording as analysed keeps it at a 20 s offset.
- **What I measured:** with truly independent ROIs, the 1-minute ratio is 0.88 in the run (24 recordings) and 0.877 over 300 lab-length recordings. With bins offset 0 s, 20 s and 30 s from the grid it reads 1.28, 0.92 and 0.86.
- **Consequence:** the benchmark's 8.94 moves with the trim chosen. The lab data have no such grid, so their numbers are unaffected.
- **Fix:** add a bar for independent generator background, and randomise the bin phase.
- **Verified:** yes.

**9. MINOR — "the generator's own background reads zero", and the test behind it cannot fail at the size that matters.**
- **Location:** Figure 2 panel G, and `test_the_worlds_have_the_shapes_the_page_teaches`.
- **The picture:** the dotted curve sits at −0.02 to −0.03 from about 1 s to 1 minute. That is a third of the lab shoulder the page reads as signal, and synthetic curves carry no interval.
- **The test:** it accepts a background mean within 0.2 at short lags and 0.15 at 5–30 s, twice the lab effect, so it cannot fail at that size.
- **Fix:** tighten the tolerance to the lab scale with more recordings, or show intervals.
- **Verified:** yes; the test tolerance is read from the file, and −0.02 is read off the figure.

**10. MINOR — nobody showed that CoactDetect removal spares drift, and the slow-stream claim sits outside anything tested.**
- **Location:** the slow bullet.
- **What I ran:** removal on the 20 s and 5-minute worlds, which have no events. It took 2–5 % of onsets and barely moved the 1-minute ratio (5.46 → 5.31 and 6.79 → 6.70 on fast settings). At synthetic rates, removal is specific, which supports the page.
- **What that does not cover:** on slow, removal took 42 % of onsets by variance weight (61 % by pair weight), at a slow setting nobody has retuned. The synthetic check does not reach that regime.
- **Fix:** show this removal check, and state the slow claim as "inside the episodes of an untuned CoactDetect".
- **Verified:** yes.

**11. MINOR — "rigid shift removes modulation only faster than about *J*" rests on two worlds.**
- **Location:** Figure 4, second bullet.
- **Why:** it is generalised from two timescales, both at a depth (σ 0.8) five to ten times the lab's. There is no world at lab depth, and none at 1–2 minutes.
- **Fix:** soften the wording, or add worlds at lab depth and at 1–2 minutes.
- **Verified:** yes.

**12. MINOR — the test suite cannot catch finding 1.**
- **Location:** `<worktree>/tests/test_measure_slow_comodulation.py`.
- **What's missing:** no test covers the removal arms. The one count-variance check on the reference, `assert_allclose(vr, 1.0)`, divides the circular arm by itself, so it cannot fail; the page admits this.
- **Record:** no existing assertion encodes the defect, so none needs to flip. The fix is a new assertion, as in finding 1.
- **Verified:** yes.

## Checked and holding
- The benchmark generator's slow swing comes from its 5-minute dense block (hot window alone 9.59, background alone 0.88).
- Rigid shift at 1.6 s and 10 s gives 3.20 and 3.12 at 1 minute.
- The simulated training recordings come from the full spec, dense block included (`tools/tube_self_supervised.py`, via `fair_bakeoff._make_recording`).
- Figure 3 is geometrically consistent: the block-control shifts are circular within each block.

## Scope and grant
- **Grant:** the declared grant covers Read, Grep, Glob and Bash. This run held only Read and Bash, so it took a fallback path. The run record should note that.
- **What I read:** the README, all six figures, the measurement tool, the tests, `results.json`, `summary.json`, the generator's background code, and the relevant lines of the goal page and the rigid-shift training tool.
- **Not checked:** whether the published citations are accurate.
