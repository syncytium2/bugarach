GRANT 3 ok — Read, Grep, Glob

(I also hold SubagentHandback, the channel for this report. I hold no Edit, Write or NotebookEdit.)

**Scope.** I read the built artifact `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`: all prose, the answer box, 7 figure captions, all SVG `<text>` labels and `<title>` tooltips, and Tables 1–3. I cross-checked it against:
- `collapse_table.json` and `trace.json`, with spot checks of `census.json` and `replays/`
- `tools/diagnose_chorus_collapse.py`
- the replicate report, §4 and the collapse table
- the todo
- the INDEX row
- GLOSSARY "Tuning the learned nets"
- `weekend-runs/.../field_size_candidates/why_chorus.txt` and its README

**What reconciles (checked, no finding):**
- **chorus_norm, both draws:** 146 + 153 = 299 of 864 fits; 292 of 396 at lr 0.03 plus 7 of 468 below it = 299. Figure 2's row labels read 1/216, 6/252 and 292/396.
- **chorus_gain_norm, both draws:** 3/144, 37/288 and 110/432 = 150, which is 75 per draw, matching the replicate report.
- **Table 1** cells equal the per-configuration sums from the Figure 2 tooltips, all 16 checked.
- **Table 3** configuration counts are 6/7/11 and 4/8/12.
- **Step-length split:** 141/216, 59/72 and 92/108 sum to 292/396.
- **Range and left-outs:** the 42%–92% range is 15/36 to 33/36. The 3 left-out configurations are aace23d7, 9987efaa and a04f8e10.
- **"5 twin pairs" is correct once vote_gain is counted,** and "8 early / 0 late / 3 recovered" matches the pair c5fcce77/a6d1c9b2.
- **Chance prediction:** 1.4 of 7 = 52/36.
- **Figure 1:** 15 planted events and 23 working calls; the collapsed fit has 1 call of 2,693.8 s.
- **Figure 5:** the 158 logged steps are steps 230–1,800 at every 10 steps, and the curve ends at 2 silent layers.
- **Thresholds:** 0.95 is logit 2.9, and 0.0001 is logit −9.2.
- **Consistent everywhere:** net order (chorus_norm, then chorus_gain_norm) and learning-rate order (0.003, 0.01, 0.03) are the same in every figure and table.
- **House rules:** no "modality", no singular "data", no British spellings.
- **PR #596 claims** (lr 0.01 and 0.001 tested, encoder "starts deaf") match `why_chorus.txt` and the README.

## Findings
Format: location · issue · severity · suggested fix · verified against a source

1. **§1 ¶1 ("Both fits come from the same configuration and differ only in their training seed").**
   - **Issue:** False. `trace.json` and `collapse_table.json` show the collapsed fit is seed 0, recs `3a17721a7a`, pair [1, 3]. The working fit is seed 2, recs `ecf4b9b71a`, pair [0, 3]. They differ in fold pair too. This is the page's main exhibit, and §2 leans on it to argue that the seed matters.
   - **Severity:** blocking.
   - **Fix:** Reword to "differ in training seed and in the pair of inner folds they trained on". Or use the same-pair contrast the data hold: seed 0 on `ecf4b9b71a` collapsed, seed 2 on `ecf4b9b71a` worked. That second option needs a new replay.
   - **Verified:** yes.

2. **§4 ¶3 ("one collapsed fit … from each of 7 other lr-0.03 configurations"); Figure 7 caption ("each of the other lr-0.03 configurations tried").**
   - **Issue:** Table 2 and Figure 7 show 8 fits from 8 configurations. One of them is 2736f584 seed 1, which is Figure 1's own configuration, so it is not "other". The paragraph's arithmetic breaks: 7 configurations with one pair merged would give 6 distinct runs, but the text says "6 of 7 distinct runs". The "3 left out" count only works with 8 tried (8 + 3 = 11).
   - **Cause:** the builder computes `len(tried_cfgs) - 1` with `tried_cfgs = {warm-up cfgs} | {ref cfg}`, and the reference configuration is already among the warm-up configurations.
   - **Severity:** major.
   - **Fix:** "from each of 8 lr-0.03 configurations: Figure 1's own at another seed, and 7 others". Fix the builder's count and the Figure 7 caption the same way.
   - **Verified:** yes (builder lines 869 and 1144; Table 2; Figure 7 tooltips).

3. **§1 "How the fits are organized" ("Inside each outer fold, every configuration is trained … on each of the 6 pairs of 4 inner folds … 432 per net per run"); also GLOSSARY "inner fit" ("one pair of inner folds").**
   - **Issue:** Contradicts the replicate report §4. There, the 4 folds are the outer folds, each inner fit trains on two of them, and one held-out fold leaves only 3 pairs; the 6 pairs are counted across the whole draw. As worded, "inside each outer fold … 6 pairs" implies 4 × 432 inner fits per draw.
   - **Severity:** major.
   - **Fix:** Follow the replicate report: "each inner fit trains on 2 of the 4 outer folds and is scored on the other 2; across the draw that is 6 pairs, so 24 × 3 × 6 = 432 inner fits per net per draw." Correct the glossary entry in the same change.
   - **Verified:** yes.

4. **§1 definition of "configuration"; Figure 2 tooltips; §2 "5 pairs … differ only in step count".**
   - **Issue:** chorus_gain_norm configurations also differ in `vote_gain`. The builder's `_identity` uses it, but the page never names it. Two consequences:
     - Figure 2 shows 95a649dd and c5fcce77 with identical descriptions ("4 wide × 6 deep, top 8, 900 steps, lr 0.01").
     - A reader who applies the page's own definition to the tooltips finds 11 or more step-only pairs, not 5. The "8 early / 3 recovered" chorus_gain_norm figures cannot be traced.
   - **Severity:** major.
   - **Fix:** Add the vote gain to the definition, and to chorus_gain_norm's tooltips and Table 2. The GLOSSARY "configuration" entry could also list it.
   - **Verified:** yes (`collapse_table.json` `vote_gain`; builder line 377).

5. **Answer box, bullet 2 ("292 of 396 fits collapse at lr 0.03; 7 of 468 fits below it"); same numbers in the todo ("What was found", bullet 1).**
   - **Issue:** The counting basis changes without notice. Bullet 1 is per draw (of 432), bullet 2 pools both draws (of 864), and bullet 3 is second draw only. A reader can take 396 as part of the 432.
   - **Severity:** major.
   - **Fix:** "Across both draws, 292 of 396 inner fits collapse at lr 0.03 …". Do the same in the todo.
   - **Verified:** yes.

6. **Subtitle, answer box bullets 1, 3 and 4, §7: the word "run".**
   - **Issue:** §1 says the replicate report "calls the two runs draws, and so does this page", but the answer box uses "runs" for draws ("In both runs of goal 2", "In the second run"). The same box then uses "runs" for training runs ("6 of 7 other collapsed runs"), and the subtitle uses both senses in one sentence. The glossary term is **draw**.
   - **Severity:** major.
   - **Fix:** Use "draw" for the goal-2 repeats everywhere. Keep "run" only for a training run.
   - **Verified:** yes.

7. **Todo, "Why the output stays flat" ("Every fit starts with a nearly flat output").**
   - **Issue:** The page shows this for exactly two replayed fits (§4: "Both start with an output that barely varies"). The todo turns it into a claim about every fit.
   - **Severity:** major.
   - **Fix:** "Both replayed fits start with a nearly flat output."
   - **Verified:** yes.

8. **Todo, "Effect on goal 2".**
   - **Issue:** It drops the page's qualifier "2 of its refits collapsed anyway". Without it, "rather than putting dead models into its held-out scores" reads as absolute, which contradicts the replicate report's † on chorus_norm, second draw.
   - **Severity:** minor.
   - **Fix:** Carry the qualifier over.
   - **Verified:** yes.

9. **Todo, option 1 vs page §5.**
   - **Issue:** The todo says dropping lr 0.03 "says nothing about chorus_gain_norm". The page's parenthetical says that for chorus_gain_norm "it would change what tuning chose". The two describe the option differently.
   - **Severity:** minor.
   - **Fix:** State whether the option is chorus_norm-only and use the same wording in both places.
   - **Verified:** yes.

10. **Answer box, bullet 3 (the 142 of 153 and 0 of 279 counts cite "Figure 4, where the signal stops").**
    - **Issue:** The silent-layer counts are in Figure 3. Figure 4 shows only the separation (d).
    - **Severity:** minor.
    - **Fix:** Cite "Figure 3, silent layers and flat outputs" for the counts and Figure 4 for the separation.
    - **Verified:** yes.

11. **§3 ("lowest value on the threshold grid (0.0001)") vs Figure 1 ("threshold, −9.2").**
    - **Issue:** The same threshold is given on two scales, and neither place says so. The 0.0001 has no unit (it is a probability).
    - **Severity:** minor.
    - **Fix:** "(probability 0.0001, logit −9.2)".
    - **Verified:** yes (`trace.json` `threshold_logit`).

12. **§3 closing and §6 bullet 5 ("24 collapsed chorus_gain_norm fits").**
    - **Issue:** The basis is the second-draw census, but neither place says so. The rest of the Limits list mixes the census with both-draw counts. The todo does state it ("In the second draw, 24 of its 75").
    - **Severity:** minor.
    - **Fix:** "24 of the second draw's 75 collapsed chorus_gain_norm inner fits".
    - **Verified:** yes.

13. **Subtitle ("14 training runs were replayed").**
    - **Issue:** There are 14 replay files, but they cover 10 fits, and by the page's own §4 rule the `2736f584` seed-1 and `9ad792aa` replays are one training run.
    - **Severity:** minor.
    - **Fix:** "14 replays of 10 fits", or similar.
    - **Verified:** yes (`replays/`).

14. **§5, collapsed-refits list ("chorus_norm, second draw, lr 0.01; chorus_norm, second draw, lr 0.01").**
    - **Issue:** The duplicated item reads as a typo.
    - **Severity:** minor.
    - **Fix:** "two chorus_norm refits, second draw, lr 0.01".
    - **Verified:** yes (Table 3).

15. **§4 ¶2, figure order.**
    - **Issue:** Figure 6 is cited ("the replays") before Figure 5 is first cited, while the figures are numbered and placed 5 then 6.
    - **Severity:** minor.
    - **Fix:** Swap the numbers or the order of the citations.
    - **Verified:** yes.

16. **§4 ¶2 ("the replay with a 50-step warm-up stays flat without a silent layer on any of its training batches").**
    - **Issue:** No figure shows this. Figure 5 plots only the two as-run replays. The data are in the 50-step replay JSON under `head_varying`, which I did not re-count.
    - **Severity:** minor.
    - **Fix:** Add the 50-step trace to Figure 5, or point to the data file.
    - **Verified:** no (not re-counted).

17. **Answer box ("leaves it within 220 steps"), §4 ("loss falls below 1.0"), Table 2 note ("trains when … below 0.5").**
    - **Issue:** Two loss cutoffs are used for leaving the flat start and training, and the page never says how they relate.
    - **Severity:** minor.
    - **Fix:** Say that 1.0 marks leaving the start and 0.5 marks trained, or use one cutoff.
    - **Verified:** yes.

18. **Order and color of the collapsed/working categories across figures.**
    - **Issue:**
      - Figures 1, 5 and 6 list working before collapsed; the Figure 3 and 4 legends list collapsed before working.
      - Figure 2 colors every configuration dot `--c1`, the color Figures 1, 3 and 4 use for "working", including configurations with 33 of 36 fits collapsed.
    - **Severity:** minor.
    - **Fix:** Pick one order. Use a neutral ink in Figure 2.
    - **Verified:** yes (SVG fill attributes).

19. **Numbers without units.**
    - **Issue:** "would be 111.5", "38 observed, 39.6 expected", "60 of 62", "predicts 1.4 of 7", "4 × 6: 23, 8 × 4: 1". Table 2's "configuration's collapse share" column also does not say it pools both draws.
    - **Severity:** minor.
    - **Fix:** Add the unit, e.g. "111.5 fits", "60 of 62 collapses", "1.4 of 7 runs", "23 fits". Add "(both draws)" to Table 2's column heading.
    - **Verified:** yes.

20. **Glossary coverage.**
    - **Issue:** The page coins "census", "working fit", "twin"/"shorter twin" and "warm-up" without glossary entries, although the glossary's rule is that new terms are added in the same change. It also says "dead models" (answer box, §5), while the glossary's silent-layer entry warns against "dead". The INDEX row lists "dead layer", "dead head" and "dying GELU" as search keywords, which is fine for an index.
    - **Severity:** minor.
    - **Fix:** Add census and twin to the "Tuning the learned nets" section. Say "collapsed models" instead of "dead models".
    - **Verified:** yes.

21. **Figure 3 caption ("59 chorus_norm and 26 chorus_gain_norm fits have an output SD below 10⁻³").**
    - **Issue:** Not checked. `census.json` is a single line and too large to count with my tools.
    - **Severity:** minor (flag only).
    - **Fix:** Have a role that can run code count `logit_sd < 1e-3` by net in `census.json`.
    - **Verified:** no.

## Files
- `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`
- `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/collapse_table.json`
- `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/trace.json`
- `<worktrees>/chorus-collapse/tools/diagnose_chorus_collapse.py` (lines 377, 864–877, 1143–1156)
- `<worktrees>/chorus-collapse/docs/learned/tuned_vs_coact/replicate1/report.html` (lines 213–232)
- `<worktrees>/chorus-collapse/docs/todo/2026-09-19-chorus-norm-does-not-train-at-lr-0.03.md`
- `<worktrees>/chorus-collapse/docs/GLOSSARY.md` (lines 313–332)
- `<worktrees>/chorus-collapse/docs/INDEX.md` (line 108)
