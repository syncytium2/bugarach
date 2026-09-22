GRANT 3 ok — Read, Grep, Glob

# Cross-Examiner review: `docs/learned/slow_comodulation/README.md` (branch unsup/slow-comodulation, 2f77de1)

The numbers mostly check out. Every value on the page that should be in `summary.json` matches it after rounding. The problems are about what the page says those numbers mean: two claims contradict the page's own data or figures, three cited figures don't show the arm they're cited for, and several companion docs now disagree with the page.

**What I checked (all passed unless listed below):**
- **Main table:** all 39 cells of the count-variance table (every arm × bin width × raw/detrended).
- **Checks block:** all 10 paired differences with their intervals; all per-recording rows (median, quartiles, share above 1, detrended median, circular-shift reference share); the per-pair values 0.019, 0.034 and 0.021; the leave-five-out results; how much CoactDetect removed (2.5/8.8 % median, 7.2/64 % weighted, 1.3/7.5 % of time); effective mice (12.7/7.7/17.5, 23–25).
- **Groups:** recording and mouse counts (17+22+25+20 = 84, 10+12+12+10 = 44); pooled ratios and medians by group; heaviest-mouse shares (37–48 % fast, 52–64 % slow, and the legend in Figure 6).
- **Correlogram values:** fast +1.91 [1.17, 3.13], +0.88, the shoulder, and +0.07 to +0.04 after removal; slow +20.8, the dip at −0.56/−0.51, +0.05 after removal, and +0.35 to +0.57 under rigid shift at 10–20 s; Dard +0.78 and the −0.05 dip.
- **Synthetic worlds:** 5.25 of 5.53, 6.93 of 6.95, 1.71 of 1.79, 8.9, 0.88; 20 s world at +0.68 → +0.51 → +0.36; 1.7–5.0 % removed.
- **Run details:** window lengths 17–20 and 19–25 minutes; 566 median ROIs; 27 h analysed; 2 m 15 s run time; 3–7 ROIs per event, 0.0097 onsets per ROI per second, and the 0.06 onsets per second, 1,200–1,500 s promiscuity probe (against `simulate.py`); CoactDetect settings (`bench.py`, `coact.py`); the step exclusion at ±2 s (MILESTONES).
- **Figures:** all six opened and compared with their captions. In Figure 2, every block-control row keeps its per-block count.
- **Group order:** DI, MALE, ORX, OVX everywhere.
- **Test list:** the Reproduce section's description matches `tests/test_measure_slow_comodulation.py`.

## Findings

1. **README l.195–196 and l.303**
   - **Issue:** "Rigid shift fills in the dip" is only true at *J* = 10 s and 20 s. At 1.6 s, lags 2.7–5.4 s on the slow stream still read −0.18 and −0.38 (`summary.json` `rigid_1.6`). Figure 5E draws that light-blue curve dipping to about −0.38. The page uses 1.6–20 s as the thread's range everywhere else.
   - **Severity:** major.
   - **Fix:** Write "rigid shift at 10–20 s fills in the dip; at 1.6 s it does not."
   - **Verified:** yes.

2. **README l.25 (short answer), repeated at `docs/goals/unsupervised-learning.md` l.58**
   - **Issue:** "One group of mice carries most of it" contradicts the page's own heading at l.267 ("The pooled result is not one group's"). It also doesn't fit the data.
     - After removal and the block control, the pooled 1-minute ratios are DI 2.74, OVX 2.62, MALE 2.03, ORX 1.71.
     - As recorded, they are DI 3.71 and OVX 3.30.
     - DI is 17 of 84 recordings.
   - **Severity:** major.
   - **Fix:** Match the By group section, e.g. "higher in DI than in the other groups, and not evenly spread". Update the goal-page pointer in the same change.
   - **Verified:** yes.

3. **README l.267–270**
   - **Issue:** Two measurement bases are mixed in one sentence.
     - The curve claim (DI +0.11, others +0.05) is after removal and the block control.
     - The ratios quoted beside it (3.71 vs 2.83/1.96/3.30; medians 2.94 vs 1.81/1.20/1.32) are as recorded.
     - The same-basis ratios are in `checks_by_group`/`by_group`: pooled 2.74/2.03/1.71/2.62, medians 1.76/1.21/1.09/1.31.
   - **Severity:** minor.
   - **Fix:** Quote both measurements on one basis, or label each one.
   - **Verified:** yes.

4. **README l.68–70**
   - **Issue:** "Each of these is drawn in Figure 2" follows the definitions of CoactDetect and an episode. Figure 2 draws only the three surrogates; the tool's own docstring says "a schematic of the three surrogates".
   - **Severity:** major.
   - **Fix:** Say "The three surrogates are drawn in Figure 2", or add an episode to the figure.
   - **Verified:** yes.

5. **README l.32 and l.297–298**
   - **Issue:** The claim "rigid shift at 1.6–20 s leaves it in every dataset" cites Figure 4 and Figure 3 panel F. Both plot only *J* = 20 s. The claim holds in `summary.json` (1-minute ratio at *J* = 1.6/10/20: fast 3.20/3.12/3.00 of 3.21; slow 11.24/10.62/9.86 of 11.37; Dard 15.08/13.69/12.38 of 15.23), but no figure shows it.
   - **Severity:** minor.
   - **Fix:** Cite `summary.json` for the 1.6 s and 10 s values, or add those arms to Figure 4.
   - **Verified:** yes.

6. **README l.149–150**
   - **Issue:** "Removing CoactDetect's episodes spares drift (C, D, F) … within 0.3 of the recorded value" has three problems.
     - The episodes-removed arm is in no panel of Figure 3. The tool draws only `minus_coact_block_120` (the removal followed by the block control).
     - In panel F, the 5-minute world after removal and the block control reads 6.10 against 6.95, which is 0.85 apart.
     - The top of the 1.7–5.0 % range is the 20 s world (panel B), not C or D.
     - The "within 0.3" is true only in `summary.json` (5.35/6.73/2.05 against 5.53/6.95/1.79).
   - **Severity:** major.
   - **Fix:** Cite `summary.json` for this arm, or plot it. Change the panel list to B–D.
   - **Verified:** yes.

7. **README l.131–135 (Figure 3 caption) and `tools/make_slow_comodulation_figure.py` l.14–15**
   - **Issue:** "Each against every arm" and "F: … every world and arm" overstate what's drawn.
     - Panels A–E draw 7 arms, without the episodes-removed arm.
     - Panel F draws 4 arms: as recorded, *J* = 20 s, block control, and removal then block control.
     - The docstring's "under each arm" for Figure 4 is also wrong: Figure 4 draws 4 arms.
   - **Severity:** minor.
   - **Fix:** List the arms each panel draws.
   - **Verified:** yes.

8. **README l.143, l.301–302; `tools/measure_slow_comodulation.py` l.49–50**
   - **Issue:** Three different cutoffs are given for what rigid shift removes:
     - "only faster than about *J*" (l.143, and the tool docstring);
     - "faster than about 40 s" at *J* = 20 s, which is 2*J* (l.301);
     - "between 10 and 45 s" (l.302).
   - **Severity:** minor.
   - **Fix:** Pick one (about *J*, or about 2*J*, which matches the "plateau reaching about 2*J*" at l.142) and use it in all three places.
   - **Verified:** yes.

9. **`docs/MILESTONES.md` l.99 and l.60; `docs/learned/tube_self_supervised/README.md` l.74–76 and l.395–397**
   - **Issue:** These say shared modulation is "absent on the lab fast stream (flat at 0.50)" and still frame the decision as "10–45 s". This page measures a fast-stream shoulder of +0.06 to +0.08, and a paired rigid-shift (*J* = 20 s) removal of 0.81 [0.39, 1.35] at 10 s bins. Neither the page nor the milestones row mentions the disagreement.
   - **Severity:** major.
   - **Fix:** Say on the page that the classifier result and the variance result differ on the fast stream, and why. Annotate the MILESTONES row and open item in the same change.
   - **Verified:** yes.

10. **README l.368–369, against `tube_self_supervised/README.md` l.415–416 and `GLOSSARY.md` l.379–380**
    - **Issue:** The page says "Harrison & Geman trace it to Pipa, Riehle & Grün 2007". The tube report says "no source reached attributes train shifting to it". The glossary credits Pipa 2007 outright.
    - **Severity:** major.
    - **Fix:** Settle it against the Harrison & Geman text, then fix whichever documents are wrong.
    - **Verified:** yes for the disagreement; the paper itself not checked.

11. **README l.86–89 (the note on the darkroom-only one-recording figure) and `FOUNDATIONS.md` §5 l.127–130**
    - **Issue:** §5 says "anything derived from real data" stays machine-local. The page cites §5 only to keep out the single-recording figure, while committing `summary.json` and Figures 4–6, which are pooled summaries of real recordings. §5 doesn't make that distinction.
    - **Severity:** major.
    - **Fix:** Cite the ruling that allows pooled summaries in the repo, or amend §5 in the same change.
    - **Verified:** yes.

12. **README l.192–198, Figure 4, and the detail table rows for the slow stream; against `FOUNDATIONS.md` §9 l.382–384 and the overnight proposal l.88**
    - **Issue:** §9 admits no number pooled across groups unless the per-group numbers sit beside it. The slow stream's pooled 11.4, 2.59 and 2.17 have no per-group numbers anywhere on the page. `checks_by_group` has them:
      - as recorded: DI 13.01, MALE 13.44, ORX 5.81, OVX 5.69;
      - after removal and the block control: 2.04, 2.95, 1.84, 1.47.
    - **Severity:** major.
    - **Fix:** Add the per-group slow-stream ratios to the By group section.
    - **Verified:** yes.

13. **README l.280–283**
    - **Issue:** The interval histogram (2.80 s floor; 15/95/333/771 per second of interval; about 1,050 beyond) is labelled "measured". It is in neither `summary.json` nor `measure_slow_comodulation.py`, so the Reproduce table can't regenerate it.
    - **Severity:** minor.
    - **Fix:** Name the tool and output these numbers came from, or add them to the run.
    - **Verified:** no.

14. **README l.183–184 against Figure 5, panel D**
    - **Issue:** The text says the fast event peak is "gone by about 1 s" and the shoulder starts "from about 5 s". Between them is a bump at 2.7–3.8 s of +0.15 [+0.09, +0.24]. Its interval clears the shoulder level, it is visible in panel D, and the text never mentions it. It sits at the same lags as the slow-stream dip.
    - **Severity:** minor.
    - **Fix:** Mention the bump, or say why it's left out.
    - **Verified:** yes.

15. **`summary.json` `leave_heaviest_out_note` (from the measurement tool l.536); the tool's `checks` docstring l.480–481**
    - **Issue:**
      - The note says "Figure 1's weight", but the count-variance figure is Figure 4.
      - The docstring says leave-five-out drops the five recordings with the most onset pairs. For the variance ratio, the code drops the five with the largest circular-shift variance. The page (l.249) describes it correctly.
    - **Severity:** minor.
    - **Fix:** Fix the figure number and the docstring.
    - **Verified:** yes.

16. **README l.156–157**
    - **Issue:** "Varies each ROI's rate on a fixed 60 s grid". `generator_spec` has `bg_burst_bin_sec` = [300, 60], so there are two grids.
    - **Severity:** minor.
    - **Fix:** Write "on 300 s and 60 s grids".
    - **Verified:** yes.

17. **Figure 3 panel D label and README l.130**
    - **Issue:** The panel says "shallow shared modulation, 1 minute", while panel C says "shared drift, 5 minutes". The page defines "drift" as shared modulation over a minute or more (l.59), so the 1-minute world counts as drift.
    - **Severity:** minor.
    - **Fix:** Call it "shallow drift, 1 minute", or explain why this one isn't drift.
    - **Verified:** yes.

18. **README l.53, l.133, l.205; `GLOSSARY.md` shared-activity vocabulary**
    - **Issue:** New terms defined on the page are missing from the glossary: **arm**, **lit**, and **effective mice**. The rule is that new terms go into the glossary in the same change.
    - **Severity:** minor.
    - **Fix:** Add all three.
    - **Verified:** yes.

19. **README throughout, against `summary.json` (`cossart/events`), the measurement tool's docstring l.73, MILESTONES l.99, the goal page l.54, and the tube report l.397**
    - **Issue:** This page calls the dataset "the Dard et al. 2022 dataset". Every companion doc calls it "Cossart". The page never says the two names mean the same folder.
    - **Severity:** minor.
    - **Fix:** At first use, say it's the folder named `cossart` elsewhere.
    - **Verified:** yes.

20. **Figure 3 legend**
    - **Issue:** The legend lists "curve above the view ▼", but no Figure 3 panel shows that mark. In panel F, ▼ also means rigid shift at *J* = 20 s, so one glyph has two meanings.
    - **Severity:** minor.
    - **Fix:** Drop the unused legend entry.
    - **Verified:** yes.

21. **README l.80 ("D is centered on a planted event")**
    - **Issue:** The figure tool's `_busiest` centres panel D on the 2 s bin with the most distinct ROIs lit, rounded down to 5 s. It never reads a planted-event time.
    - **Severity:** minor.
    - **Fix:** Write "centered on its busiest 2 s", or centre on a planted-event time.
    - **Verified:** partly (the code, not the draw).

22. **`GLOSSARY.md` l.411–413 against README l.199 and l.277–291**
    - **Issue:** The glossary defines the dip as "on the lab slow stream, after events". The page leaves the cause open with three readings, and reports a dip on the Dard dataset too.
    - **Severity:** minor.
    - **Fix:** Make the glossary definition describe the dip without assuming its cause.
    - **Verified:** yes.

23. **`docs/goals/unsupervised-learning.md` l.20**
    - **Issue:** It says "Twenty-two hours of baseline recordings". This run analysed 26.9 h of lab baseline after trimming, and 22.4 h of Dard data. The new pointer sits on a page stating a number the page it points to doesn't support.
    - **Severity:** minor.
    - **Fix:** Reconcile the number or say where it comes from.
    - **Verified:** partly.

24. **README l.306–313**
    - **Issue:** The small-*J* check (95.8–100 %, 52.4–54.1 %, 54.9–62.4 %) and `count_excess` both live on another branch. Neither `tools/check_small_j_mixes_events.py` nor `count_excess` exists in this worktree, so none of those numbers can be checked here.
    - **Severity:** minor.
    - **Fix:** Name the branch explicitly (l.306 says only "the unmerged branch"), or mark the numbers as not reproducible from this tree.
    - **Verified:** no.

**Files:**
- `docs/learned/slow_comodulation/README.md`
- `docs/learned/slow_comodulation/summary.json`
- `docs/learned/slow_comodulation/fig1_two_kinds.png` through `fig6_by_group.png`
- `tools/measure_slow_comodulation.py`
- `tools/make_slow_comodulation_figure.py`
- `tests/test_measure_slow_comodulation.py`
- `docs/MILESTONES.md`
- `docs/goals/unsupervised-learning.md`
- `docs/learned/tube_self_supervised/README.md`
- `docs/GLOSSARY.md`
- `docs/FOUNDATIONS.md`
- `docs/INDEX.md`
- `docs/learned/recording_identity.md`
- `docs/proposals/2026-09-10-surrogate-evaluation-overnight.md`
- `src/bugarach/simulate.py`
- `src/bugarach/bench.py`
