GRANT 3 ok — Read, Grep, Glob

# Consistency auditor ("Cross-Examiner"): blind verify, round 3

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`

I read it as built, all 443 lines. For the lines that hold the SVGs and tables I pulled every `<text>`, `<title>`, `<tr>`, caption and table note. I checked the page against:
- its own generator;
- the second draw's `meta.json`, `replicate_summary.json` (per-fold copy) and `merge_gap.json`;
- the first draw's `results.json`;
- the rehearsal's `results.json`;
- the first draw's companion report (`bugarach-worktrees\merge-gap-second-draw\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html`);
- on main: `docs\GLOSSARY.md`, `FOUNDATIONS.md` §9, `goals\README.md`, `goals\coded-detector-optimization.md`, `goals\learned-model-family.md`, `HANDOFF-coded-detectors.md`, `HANDOFF-slow-comodulation-on-the-de-pinned-export.md`, `detector_history.md`.

I have no git or shell tool, so I could not open branch-only files through `git show`. Those sources are marked unverified below.

## Findings

Format: location · issue · severity · suggested fix · verified against a source

1. **Figure 9 caption vs its own marks** · The caption says "A triangle at the left edge is a fold below −0.15, where a net's training failed." The figure also draws a triangle for *tube under the budget, second draw, fold 0: −0.164* (SVG `<title>`; replicate_summary per_fold −0.1637). That entry is not flagged anywhere: Table 1 shows tube budget second draw as 0.616 with no †, Table 5 leaves no fold out, and Figure 10 plots it. So one of the five triangles is not a training failure. · **major** · Drop "where a net's training failed", or say "four of the five are folds where training failed; tube's second-draw fold 0 under the budget is a genuine low fold". · yes

2. **"The closest learned model" uses two counting bases** · The build picks chorus_gain_norm as closest from all-fold means (generator `best()` on `mean[k]`, which includes flagged folds). Table 5 and Figure 10 use means with flagged folds left out. On that basis chorus_norm is closer in the second draw under the budget: −0.021 as run against chorus_gain_norm's −0.025, and −0.004/−0.006/−0.010/−0.013 at matched merges against −0.011 to −0.018. The summary box says "the closest learned model still trailed under the cap, by half to three-quarters as much" and section 9 says "chorus_gain_norm, the closest". Both are true only on the all-folds basis, while the matched-merge numbers beside them are on the other basis. · **major** · Pin one basis. Either say "closest on the mean over all four folds, failed folds included", or state that on the folds where it trained, chorus_norm's budgeted second-draw gap is smaller still (−0.021 as run, −0.004 at 2 s). · yes (replicate_summary and Table 5)

3. **Disagreement with the companion report on the first draw** · WSMIP064's report on the same first draw applies goal 1's crowded-recording veto after the fact (`tools/crowded_check_fair_comparison.py`, `crowded_check.json`). It concludes that binned SCE's 0.771/0.770 "does not stand": its choices fail the veto in 7 of 8 cases. It also marks LoCo, rate+context, SPIKE-synch and locust under the budget as "not admissible". This page:
   - shows all of those entries unflagged in Table 1;
   - counts SCE on F1 alone, and LoCo, rate+context and SPIKE-synch under the budget, as "unflagged" in the between-draw spread (SCE's 0.023 is the coded maximum);
   - says only that SCE's lead "may belong to the bench's spacing";
   - lists "No check on crowded events" as a limit, without mentioning that a crowded check exists for the first draw.

   A reader of both reports gets opposite verdicts on the same first-draw entries. · **major** · Cite the companion's crowded check in section 8 and section 10, and say whether this page's flags deliberately exclude it and why. Ideally, show the veto outcome for the first draw beside Table 1. · yes

4. **Fold numbering vs the companion** · This page numbers outer folds 0–3 (Figures 3, 5, 7, 10 and the text: "tube's in the first draw, fold 0", "CoactDetect in the first draw, fold 2"). The companion numbers them 1–4 ("folds 1 to 4; the run's files number them 0 to 3") and calls the same tube fold "tube's fold 1 under the budget". Section 11 points the reader to that report ("WSMIP064 writes its own report on it"), so every fold this page names will mismatch there. · **major** · Add one line: "folds are numbered 0–3 as in the run's files; WSMIP064's report numbers them 1–4." · yes

5. **Section 11: the first draw's matched-merge file** · The page gives `docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/merge_gap.json` with no branch. It is not on main, and it is not in any local worktree: the `merge-gap-second-draw` worktree has that folder without `merge_gap.json`. The build read a scratchpad file (`merge_gap_first.json`). Every other branch-only source in section 11 names its branch; this one names none, so the reader has no way to find the file. · **major** · Name the branch it is committed on (e.g. `nets/fair-comparison-report`), or ship the file beside this report and cite that path. · partly (not on main or in local worktrees; origin branches not checked, no git tool)

6. **Section 9 vs section 6: how many things changed** · Section 9 says "four things changed at once (simulator, coded tuning, budget and the fold defect)". Section 6 lists five: the four named plus "no limit on CoactDetect's context window, which reached 240 s". · minor · Make it five and add the context limit. · yes (internal)

7. **Section 3 and Table 7: "chose these values on 96 other bench recordings (seeds 1–96)"** · HANDOFF-coded-detectors.md (on main, line 200) says goal 1 chose on recordings 1–48 and scored on 49–96. Line 321 says the values were "held out on 48 recordings the search never saw". "Chose on 96" overstates the selection set. · minor · "chose these values on bench recordings 1–48 and confirmed them on 49–96". · yes

8. **Summary box: "by half to three-quarters as much"** · Section 9 gives 28%–57% of the gap closing, so 43%–72% remains. "Half" is above the low end. · minor · "by roughly 45–70% as much", or quote section 9's range. · yes (internal arithmetic)

9. **Section 8, Table 3 prose** · The prose says "some refits of every net went over, as did CoactDetect in the first draw, fold 2". Table 3 also shows binned SCE (second draw, 1 of 4 folds) and locust (4 of 4 in both draws) over. Those are the ‡ folds, but the prose reads as if CoactDetect were the only coded detector over. · minor · Add "and the ‡ entries (locust everywhere, binned SCE's second-draw fold 2), whose searches returned an over-budget starting point". · yes

10. **Glossary reserved word: bare "settings"** · GLOSSARY.md retires bare "settings" ("name which"). The page uses it throughout: "each a rule with its own settings", "the settings of section 3", "reference settings", "Settings fixed before the runs and never varied" (a list that mixes budget, scoring, training spec and search parameters), and "every threshold and setting". It also writes "matching tolerance", although the glossary says "tolerance" "should not acquire" a qualifier. · minor · Use "detector settings" or "operating point" (the reference is CoactDetect's operating point), "training spec", and plain "tolerance". · yes

11. **Terms missing from the glossary** · chorus_norm, chorus_gain_norm and tube are detector-axis proper names. `line_length` has a glossary entry; these three have none, on main or on the report branch. "Dense stretch" is a new second name for the glossary's "promiscuity probe"; the page states the mapping, but the glossary does not. "draw", "entry", "call" and "matched merge" are page-local. · minor · Add the three net names, and "dense stretch" as an alias under promiscuity probe, in the same change. · yes

12. **Table 2 caption: "held-out recording"** · The caption says "every held-out recording of both folds they were scored on", but these are inner scoring folds. Section 4 defines "held out" as the outer fold, scored once at the end. · minor · "every recording of both folds it was scored on". · yes (internal)

13. **Section 9, where the false alarms fall** · "chorus_gain_norm, line_length show that pattern" repeats the subject, has no "and", and silently omits chorus_norm. Figure 11 shows chorus_norm with the pattern in the first draw (0.21 < 0.88 dense; 7.42 > 6.42 outside) but not the second (5.61 < 6.03 outside). · minor · "line_length shows the same pattern in both draws, chorus_norm in the first only; tube instead…". · yes

14. **Table numbering order** · Table 7 is first cited in section 3, before Tables 1–6 are cited. · minor · Renumber by first citation, or drop the early citation. · yes

15. **Section 2 and section 10: participation** · Section 2 gives "recruiting 30%, 18% and 10% (10, 6 and 3 cells)", but 3 of 33 is 9%. Section 10 then speaks of "the share of ROIs an event recruits … 0.18" as if there were one level. · minor · Say "3 cells (the 10% level)", and in section 10 name it as the bench's measured participation constant, 0.18, the middle level. · yes (meta.json `participation` [0.3, 0.18, 0.1]; `measured_outside_interval`)

16. **Table 1 note: "its search starts from fixed settings (section 3)"** · Section 3 gives only CoactDetect's starting values. meta.json's `coded_base` covers CoactDetect and LoCo; the others start from `OPERATING_POINTS`. · minor · Point to where the other starting points are stated, or say "from the bench's stored operating points". · yes

17. **Order of the nets** · Every table and figure lists chorus_norm, chorus_gain_norm, line_length, tube. Section 3's descriptions run in reverse (tube, line_length, chorus_norm, chorus_gain_norm). · minor · Use the table order in section 3. · yes (internal)

18. **Figure 10 caption** · The figure draws left-edge triangles (line_length on F1 alone, first draw, fold 2 at 8 s −0.161; tube on F1 alone, first draw, fold 1 at 8 s −0.205; tube under the budget, second draw, fold 0), but its caption never says what a triangle means. Figure 9's caption does. · minor · Add the edge-triangle sentence. · yes

19. **Section 4: "(24 recordings, one per background)"** · This reads as one recording per background. The real count is 12 seeds × 2 backgrounds. · minor · "(24 recordings: each seed at both backgrounds)". · yes

20. **Section 7: CoactDetect "met the budget in every fold"** · Section 7 says CoactDetect's F1-alone choice "already met the budget in every fold", while Table 3 shows CoactDetect over the budget in 1 of 4 first-draw held-out folds. Both are true on different recordings, but the page does not say which. · minor · "met the budget on its training recordings in every fold". · yes

21. **Section 2: "differ in how an event's duration is measured"** · FOUNDATIONS §9 says "Fast/slow duration: an export step, not two measurements." The page's description of what distinguishes the fast and slow streams may disagree with it. · minor · Check the wording against FOUNDATIONS §9 and export_folder_spec §width. · no (reading is ambiguous)

## Checked and clean

- **Numbering and links:** Figures 1–11 are numbered in order, each cited before it appears, and all 11 `#fig-*` anchors resolve. Section cross-references all point at the right sections (2, 3, 4, 5, 8, 9, 10, 11).
- **Category order:** the order of coded detectors matches the glossary everywhere (rate+context, CoactDetect, LoCo, binned SCE, locust, SPIKE-synch). Draw order (first, second), selection order (untuned, F1 alone, budget) and background order (quiet, busy) are the same in every table and figure.
- **Figure 1:** 20 calls = 14 matched + 6 not; 4 on distractors + 2 inside hits = 6 distractors. 0.75 dense-stretch calls per recording matches Figure 11. The 15/21 ceiling gives F1 0.83, matching the Figure 6 caption.
- **Section 2 and Figure 3:** the bench constants agree with meta.json and the glossary (33 ROIs, 2700 s, 0.0052/0.019, 120 s spacing, jitter 0.36, 6 distractors at 0.18, dense stretch 1200–1500 s, twins at seed + 100,000). Figure 3's counts agree (48 seeds, 12 per fold, 72 coded training recordings, 24 × 3 × 6 = 432 inner fits, minimum gain 0.002).
- **Figure 4:** agrees with the second draw's fold-0 budget (10.3/8.0/5.41 × 1.6 = 16.5/12.8/8.65). The quiet ceilings of 15–18 cover every second-draw fold.
- **Figure 5:** the seed blocks match the two budgets' held-out seeds.
- **Table 1 against source:** SCE vs CoactDetect +0.000 in the second draw; t = −13.0 (sd 0.005) and −2.8 (sd 0.018); ungated gaps −0.007 and −0.029; "within 0.029"; untuned −0.012 and +0.006; line_length tuning +0.032/+0.029; chorus_norm +0.005/−0.063; fold mean 0.501 against 0.745 untuned.
- **Between-draw spread:** 8 unflagged net entries (7 rose) and 9 unflagged coded entries (7 did not rise); coded median 0.006, maximum 0.023; net maximum 0.027; drift 0.018.
- **Rehearsal:** +0.011 and +0.016 match the rehearsal's `results.json`.
- **Collapse and flags:** Table 2's shares ("a third", "a sixth") hold. The † marks agree with Table 5's "left out" counts and Figure 10's labels (1/2/0/0 and 1/0/0/1).
- **Table 5 and matched merge:** as-run budget gaps agree with Table 1; 11 of 13 folds; 0.005–0.022. CoactDetect's F1 at 2/8/30 s (0.733/0.748/0.797) matches merge_gap.json.
- **Table 6 and Figure 11:** pooled recall is 0.90/0.85 against 0.86/0.84. The counts behind 9.1/7.6 against 6.4/6.0 match Figure 11's titles.
- **Section 11:** 1,938 fits and 12.7 hours for the first draw match the companion. HANDOFF-slow-comodulation item 3 and "0.03%" match.
- **Goal pages:** section 10's "seven of eight constants" and "0.18 = 6 of 33" match the coded-detector-optimization goal page and meta.json. The goals-page decisions (margin 1.6, one threshold pair of mixed backgrounds, busy empty recording reported only, 12 seeds per fold) all agree.
- **Reference and stream wording:** the reference's parameters (2 s, 120 s, α 10⁻⁵, guard 1 s, merge 8 s) match meta.json and HANDOFF-coded-detectors. "Modality" and bare "adaptive" are absent, and "stream" is used as the glossary requires.

## Not verifiable

- **Branch-only sources:** `docs/forks.md` §14 (30–36%), `HANDOFF-workstation-tuning.md` (the 1.6 margin), the rehearsal README, and `HANDOFF-coded-detectors.md` on `opt-every-knob-run` (the main copy was checked).
- **Sources I did not open:** the first-draw matched-merge values behind Table 5 (the scratchpad file), and the per-fold "below zero in all 8 folds" at 8 s.
