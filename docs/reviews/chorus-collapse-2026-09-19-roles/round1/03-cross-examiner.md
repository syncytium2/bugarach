GRANT 3 ok — Read, Grep, Glob (plus SubagentHandback for delivery; no Edit, Write or NotebookEdit)

# Role 3 (Cross-Examiner), round 1: `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`

**What I checked:**
- Every count on the page (answer box, sections 1–7, Table 1, Table 2, and the captions and `<title>` tooltips of Figures 1–4) against:
  - the builder `tools/diagnose_chorus_collapse.py`;
  - `collapse_table.json`, `census.json` and `replays/`;
  - the replicate report's Table 2, § 8 and † definition;
  - the new todo, INDEX row 108, `GLOSSARY.md`, and the weekend-runs worktree's `why_chorus.txt`.

**Counts I re-derived from the data, and they match:**
- **Figure 1, panel A:** the tooltips for lr 0.03 add up to 292 of 396 fits (11 configurations × 36). Below 0.03 they add up to 1 + 6 = 7 of 468 fits (13 configurations). Every dot's x position matches its count out of 36.
- **Table 1:** 146 / 153 / 111 fits and 75 / 75 / 38 fits, identical to the replicate report's Table 2. The per-learning-rate columns sum to the per-draw columns.
- **Section 2, from `collapse_table.json`:**
  - seed shares: 97, 93 and 109 of 288 fits (34%, 32%, 38%);
  - width 4: 172 of 216 fits; depth 4: 108 of 180 fits.
- **Census, from `census.json`:** 152 of the 153 second-draw collapsed chorus_norm inner fits have a layer with minimum live share 0. The exception is d9b39874, seed 2, lr 0.003 (live share 0.875).
- **Table 2:** all 8 fits are collapsed second-draw inner fits in the census.
- **Replay:** the as-run replay's first dead layer is at step 30, and its first-batch spread is 0.0008.
- **F1:** 0.125 follows arithmetically from 1 of 15 events matched.
- **Refits:** the 4 collapsed refits match the replicate report § 8 (2 of chorus_gain_norm, 2 of chorus_norm in the second draw's fold 1).

**Findings**

| # | Location | Issue | Severity | Suggested fix | Verified against a source |
|---|---|---|---|---|---|
| 1 | Section 5, bullet 1 ("its 95 refits … (the chosen configurations …) are 35 at lr 0.003, 60 at lr 0.01") | 40 of the 95 chorus_norm refits are the **untuned** configuration (9c65e498, `untuned: true`, lr 0.01), which tuning did not choose. The chosen refits number 55: 35 at lr 0.003 and 20 at lr 0.01. "60 at lr 0.01" includes the 40 untuned ones, and the parenthetical definition is wrong for those 40. The builder's `refits = [r for r in table if r["role"] != "inner"]` does not filter `untuned`. | major | Filter `untuned` out for the "tuning chose" sentence: "its 55 tuned refits … 35 at lr 0.003, 20 at lr 0.01, 0 at lr 0.03". Report the 40 untuned refits separately, or drop them. | yes (`collapse_table.json`: 95 chorus_norm outer rows, 40 with `untuned: true`) |
| 2 | Section 5, bullet 3 ("200 steps rescued 7 of 8 fits tried"); Section 6 ("Warm-up was tried on 9 collapsed fits"); Section 4; todo option 2 ("rescued 7 of 8 collapsed fits in replay") | Two counting bases for one quantity. The 200-step warm-up was run on 9 collapsed fits: Figure 3's fit plus the 8 in Table 2. 8 of those 9 trained. "7 of 8 tried" leaves out the Figure 3 fit, while Section 6 counts it. | major | Pick one basis everywhere: "8 of the 9 collapsed fits it was tried on" (page and todo). Or keep Table 2's 7 of 8 and write "7 of 8 more, besides the fit of Figure 3". | yes (replays folder: 9 fits with a lr0.03-warmup200 or matching file; builder `wu` excludes `ref_id`) |
| 3 | Answer box, bullet 2 ("152 of 153 collapsed chorus_norm fits … 1 of the 279 working fits") next to bullet 1 ("292 of its 396 inner fits") | Bullet 1 pools both draws (inner fits, 864 in all). Bullet 2 is second-draw inner fits only (432) and does not say so. A reader adding 292 + 7 = 299 cannot reconcile that with 153. | major | Write "In the second draw, 152 of the 153 collapsed chorus_norm inner fits … 1 of the 279 working ones". | yes |
| 4 | Todo, "What was found" bullet 5 and option 1; page Section 5 bullet 3 ("drop lr 0.03 from the chorus grids, which accepts the smaller grid tuning already used in effect") | "Tuning never chose a lr-0.03 configuration" is true only for chorus_norm. The page's own Section 5 lists two chorus_gain_norm refits **at lr 0.03**, so tuning did choose lr 0.03 for chorus_gain_norm. The todo states the claim without naming the net, then cites those same refits in the next sentence. "Chorus grids" (plural) + "the grid tuning already used" is false for chorus_gain_norm. | major | Scope both to chorus_norm: "drop lr 0.03 from chorus_norm's grid …". State separately that for chorus_gain_norm, dropping lr 0.03 removes configurations that tuning did choose. | yes (page Section 5 bullet 2; builder asserts `ref_lr` only for chorus_norm) |
| 5 | Todo title "The chorus grids put a third of their fits where they cannot train" | Mixes bases and nets. "A third" is chorus_norm's collapse share (299 of 864 inner fits). Only chorus_norm's lr-0.03 fits "cannot train", and those are 396 of 864 fits, not a third. chorus_gain_norm collapses in about a sixth (150 of 864 fits; the replicate report says "a sixth"). The page title is scoped correctly to chorus_norm. | major | Retitle, e.g. "chorus_norm's lr-0.03 configurations do not train: pick a repair". The todo filename is referenced from INDEX, so rename both in the same change. | yes |
| 6 | Todo bullet 2 ("A dead head layer makes the output a constant") | Contradicts the page. Section 3 says the output "hardly moves" (median spread 0.0055), and the one working fit with a dead layer still varies (spread 3.1). | major | "A dead head layer leaves the output nearly flat …" | yes |
| 7 | INDEX row 108 ("Its `replay` subcommand re-runs any inner fit bit-exactly against its checkpoint") | Overstates the tool and the page. `replay` reads only the second draw (`_results("second")`). It builds only chorus_norm (the `net` default has no CLI flag). It needs CUDA. "Bit-exact" was checked for the 2 as-run replays, and the page claims no more than that. | major | "re-runs a second-draw chorus_norm inner fit on the GPU, checked bit-exact against its checkpoint for the fits replayed here …" | yes (builder lines 170–201, 715–718) |
| 8 | Section 3 ("Every second-draw chorus inner fit was reloaded") vs Section 5 bullet 2 ("The second draw's 3 were in the census") and builder `census()` ("inner fits and refits") | The census also covers refits, but Section 3 describes it as inner fits only. Figure 2 plots inner fits only. The separation claim in Section 5 bullet 4 (at most 0.13 against at least 0.80) uses inner fits plus refits (`census_all`), so it is not fully visible in Figure 2. | minor | Section 3: "Every second-draw chorus fit (inner fits and refits) was reloaded …; Figure 2 shows the inner fits". Section 5 bullet 4: say the bounds include the refits. | yes |
| 9 | Section 2, "chorus_gain_norm shows the same pattern, milder" vs Figure 1 panel B | Panel B does not show the same pattern. At lr 0.03, 7 of 12 configurations collapse in 3 or fewer of 36 fits (0, 0, 1, 2, 2, 3, 3). Two lr-0.01 configurations (95a649dd at 12 of 36 fits, c5fcce77 at 11) exceed 9 of the 12 lr-0.03 configurations. Learning rate does not "separate them almost completely" here, and Section 3 itself describes a second route not concentrated at lr 0.03. | minor | "In chorus_gain_norm the share rises with the learning rate (3 of 144, 37 of 288, 110 of 432 fits) but does not separate configurations: see Section 3." | yes (Figure 1 tooltips, Table 1) |
| 10 | Prose counts not in any figure or table | Section 2's width/depth breakdown (172 of 216 fits, etc.) and the seed/fold-pair shares; Section 5's refit counts (95 / 35 / 60 / 0 refits, 4 collapsed refits, 3 refits in the census); the 0.13 / 0.80 bounds. None appears in a figure or table. Figure 1 tooltips omit width and depth, so the breakdown cannot be traced to the figure. | minor | Add width and depth to Figure 1's tooltips, and add a small refit table (net × draw × lr, collapsed of total). Or state that these come from `collapse_table.json`. | yes |
| 11 | Learning-rate order: answer box bullet 3, Section 4 ("lr 0.01 or 0.003"), Figure 3 legend (0.01 row before 0.003) | Table 1, Figure 1 rows, and the Section 3 and Section 5 lists all use ascending order (0.003, 0.01, 0.03). These three places use descending. | minor | Use ascending order everywhere: "0.003 or 0.01". Reorder the `curves` dict so the Figure 3 legend lists 0.003 before 0.01. | yes |
| 12 | Section 5 bullet 2 ("each puts a † beside its net in the replicate report") | The † definition in the replicate report is "made one call per recording **or called nothing**". Tube's † is a refit that called nothing, not a collapse. chorus_norm's second-draw † in the budget column comes from the same two refits calling nothing under that selection's threshold. The mapping from 4 refits to 4 † marks holds only loosely. | minor | "These account for the † on chorus_norm and chorus_gain_norm in the replicate report's Table 1; tube's † is a refit that called nothing." | yes (replicate report line 276 tnote, § 8) |
| 13 | Terminology: "collapsed" / "still collapses" in Figure 3's legend and Table 2 | The page defines "collapsed" by scoring (exactly one call on every recording scored). Table 2's "still collapses" and Figure 3's "collapsed fit at lr 0.01" (a curve that trains) use a training-loss test instead (loss 0.5 or higher), and Section 6 says replays were never re-scored. Same word, two definitions. | minor | Figure 3 legend: "the collapsed fit, replayed at lr 0.01". Table 2 outcome: "trains" / "does not train (loss 0.5 or higher)". | yes |
| 14 | Terminology: "training seed" (this page) vs "training repeat" (replicate report § 8, Figure 7) | Companion documents use two words for one index. The replicate report also mixes them itself (its tnote says "training seed"). | minor | Pick one. Since both docs are new, align the replicate report or add a glossary entry naming both. | yes |
| 15 | GLOSSARY.md | New load-bearing terms appear on the page, todo and INDEX with no glossary entry: collapse / collapsed fit, dead head layer, inner fit, refit, draw, configuration, warm-up, call. "Dead" already means something else in the glossary ("dead time, τ") and in CLAUDE.md ("dead-ROI filter"). "Cell" is a radar term in the glossary ("cell under test"), while the page uses "per-cell encoder" for what the code calls `roi_width` / `roi_depth` and the glossary calls ROI. | minor | Add entries for collapse, dead head layer, inner fit, refit and draw in the same change. Consider "per-ROI encoder" to match the code and glossary. | yes (glossary has no match for these terms) |
| 16 | Section 4 ("the one working fit of the same configuration") | The basis is second draw only (1 of 18 fits). Pooled over both draws, the configuration has 3 working fits (33 of 36 collapsed, per Figure 1). | minor | "the one working second-draw fit of the same configuration". | yes |
| 17 | Todo, last bullet ("15 of its 75 collapsed fits") | Unstated basis. 75 is the count in each draw, so the reader cannot tell this is the second draw. | minor | "In the second draw, 15 of chorus_gain_norm's 75 collapsed inner fits …" | yes |
| 18 | Todo option 2 ("and 50 steps did not") | Reads as if a 50-step warm-up was tried on all 8 fits. It was tried on one fit, Figure 3's. | minor | "a 50-step warm-up, tried on one fit, did not". | yes |
| 19 | Answer box, bullet 4 ("plain chorus's per-cell encoder starting deaf at every learning rate") | `why_chorus.txt` tests plain chorus at lr 0.01 and 0.001 only. 0.001 is not in goal 2's grid, and 0.003 and 0.03 were not tested. | minor | "at both learning rates tried (0.01, 0.001)". | yes |
| 20 | Section 7 ("`why_chorus.txt` (branch `replicate-run`)") | The file's own header says it was produced on branch `eval-field-size-candidates`. I found it in the weekend-runs worktree and could not check which branch now carries it. | minor | Confirm the branch and cite the one that holds the file. | no |
| 21 | Units (house rule) | Bare numbers where the unit or noun is missing: "in 7 of 468 below it" (answer box, no "fits"); "The second draw's 3" (Section 5, no "refits"); "4 of its 8 at the end" (Section 4, no "layers"). The spreads 0.0008, 0.0011, 0.0055, 5.20, 0.13 and 0.80 carry no unit: they are in logit units and the page never says so. Figure 1's axis uses a 0–1 share while the prose uses percentages. | minor | Add the nouns. State once that the spread is the standard deviation in logit units. Use percentages on Figure 1's axis or fractions in the prose. | yes |
| 22 | Figure and table references (house rule) | Bare references without the name: "the configuration of Figure 3" (Section 4), "The two as-run replays of Figure 3" (Figure 4 caption), "(Table 2)" (Section 4). "lr" is used from Table 1 and Figure 1 onward but never defined as the learning rate. | minor | "Figure 3, the replays"; "Table 2, the warm-up on other fits"; define "learning rate (lr)" at first use. | yes |
| 23 | `<title>` "Why chorus_norm collapses" vs h1 "Why a third of chorus_norm's fits do not train" | The two titles disagree on what collapses: the net, or a third of its fits. | minor | Make the `<title>` match the h1. | yes |
| 24 | Figure 2 tooltips | Tooltips identify a fit by configuration and seed only, so 6 dots share each label. The page defines a fit as configuration, training seed and pair of folds. Table 2 rows have the same gap. | minor | Add the fold pair (or recs hash) to Figure 2's tooltips and Table 2's rows. | yes |

**Checked and clean:**
- **Net order:** chorus_norm before chorus_gain_norm in Figure 1, Figure 2 and Table 1.
- **Draw order:** first before second.
- **Figure colors:** working is c1 and collapsed is c2 in Figures 2, 3 and 4.
- **Figure numbering:** Figures 1–4 are numbered, and each first reference carries its number and name.
- **"11 of 24 configurations":** matches the 11 lr-0.03 dots in Figure 1, panel A.
- **"e86433df … 31 of its 36 fits":** matches Figure 1's tooltip.
- **Banned and British words:** no "modality", no British spellings, and no singular "data" on the page or in the todo.

The heaviest items are 1–7:
- **1:** the untuned refits are counted as tuning's choices.
- **2:** the warm-up rescue is 7 of 8 in one place and tried on 9 fits in another.
- **3:** the answer box mixes both draws with the second draw alone.
- **4–7:** the todo and the INDEX row say more than the page supports.

Paths referenced, relative to `<worktrees>/chorus-collapse/`:
- `docs/learned/chorus_collapse/index.html`, `collapse_table.json`, `census.json`, `replays/`
- `tools/diagnose_chorus_collapse.py`
- `docs/learned/tuned_vs_coact/replicate1/report.html`
- `docs/todo/2026-09-19-chorus-grids-put-a-third-of-their-fits-where-they-cannot-train.md`
- `docs/INDEX.md` (row 108)
- `docs/GLOSSARY.md`

Also `<worktrees>/weekend-runs/docs/learned/field_size_candidates/why_chorus.txt`.
