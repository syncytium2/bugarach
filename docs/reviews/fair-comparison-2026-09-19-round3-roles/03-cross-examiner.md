<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round3/. -->

GRANT 3 ok — Read, Grep, Glob

**Role 3 (Cross-Examiner), round 3, blind pass: 14 findings (0 high, 6 medium, 8 low). I edited nothing.**

Artifact reviewed: `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html`. I read its prose and tables directly. The inline figure lines are too long for my tools, so I checked those through the round-3 renders (fig1–fig12.png) and the generator's caption source.

I did not open `docs/reviews/fair-comparison-2026-09-19*` or any run record. As a result I have not checked whether the §12 and Provenance reference to that review record resolves.

Format: location · issue · severity · suggested fix · verified against a source.

### Findings

**1. Figure 1 caption, panel A** ("at about 12 times the quiet background's rate and 3 times the busy one's")
- **Issue:** this contradicts §1, which says every ROI fires "an extra 0.06 times a second". §1 is correct: `src/bugarach/simulate.py` lines 776–783 add the probe's firings on top of the background. The caption's 12 and 3 are 0.06/0.0052 and 0.06/0.019, the extra rate alone. The probe's actual rate is 0.0652 on the quiet background (about 13 times it) and 0.079 on the busy one (about 4 times it). The built HTML contains the caption string once.
- The companion `docs/goals/learned-model-family.md` decision 3 ("the 5-minute stretch at 0.06 Hz") makes the same mistake.
- **Severity:** medium.
- **Fix:** either say "adds about 12 and 3 times the background's rate", or compute (0.06 + background) / background, giving about 13 and 4.
- **Verified:** yes.

**2. Figure 5 caption** ("six ROIs fire within half a second")
- **Issue:** the figure's own firings run from 9.55 s to 10.40 s (`MODE_TICKS`, generator line 505), a span of 0.85 s. The rendered panel A shows them spread over nearly a second.
- **Severity:** medium.
- **Fix:** say "within a second", or tighten the ticks so they still split 3 and 3 across the 10 s bin edge.
- **Verified:** yes.

**3. §9, bullet 2** ("Under the budget, 4 coded detectors have no admissible result… the starting points of binned SCE, LoCo, SPIKE-synch and rate+context were themselves over it")
- **Issue:** two different sets of four sit side by side.
  - The four with no admissible result are LoCo, SPIKE-synch, rate+context and locust (Table 2, Figure 7B).
  - binned SCE does have an admissible result: fold 4, which bullet 1 and Table 3 both report.
  - locust's starting point was also over the budget. `selections/gated/outer0/cicada.json` shows 16 of 16 settings refused and an inner probe rate of 503 per hour at the quiet background, against a budget of 16 per hour. So five starting points were over the budget, not four.
- **Severity:** medium.
- **Fix:** name the four detectors with no admissible result. Say that every coded starting point except CoactDetect's was over the budget.
- **Verified:** yes (locust checked on fold 0; Table 3 says 4 of 4 folds).

**4. §10, "False alarms on held-out recordings"**
- **Issue:** two figures in one paragraph count different populations.
  - "0 to 17 false alarms per hour… median 1" covers the chorus nets under the budget, as a mean of the two backgrounds.
  - "Across the five refits of one choice, the probe rate at one background differs by up to 106 per hour" is computed over all four nets, both selections and each background (generator lines 1583–1585).
  - Read in context it seems to describe the chorus nets under the budget, where it is impossible: a two-background mean of at most 17 caps any single background at 34 per hour.
- **Severity:** medium.
- **Fix:** name the population ("across any net's five refits, in either selection"), or compute the spread over the chorus nets under the budget.
- **Verified:** yes.

**5. §9, bullet 3** ("The crowded numbers differ from goal 1's published ones… because those come from goal 1's held-out crowded recordings, seeds 49 to 60, while this check… uses seeds 1 to 12")
- **Issue:** the shipped-setting crowded F1 values match goal 1's published values exactly:
  - CoactDetect: 0.808 here and 0.808 there.
  - LoCo: 0.816 here and 0.816 there.
  - Sources: `crowded_check.json`; `HANDOFF-coded-detectors.md` lines 323–325; `docs/goals/coded-detector-optimization.md` line 78.
  - Only the sliding starting values differ: 0.826 against 0.818, and 0.834 against 0.827.
  - If the recordings were different, the shipped values would differ too. So either the seed explanation is wrong, or the gap has another cause, such as the starting parameters not being exactly goal 1's chosen point.
  - Neither companion document states "seeds 49 to 60" for the crowded recordings. The handoff's line 200 gives 1–48 and 49–96 for the bench recordings.
- **Severity:** medium.
- **Fix:** re-derive the explanation, or cite where goal 1's crowded seeds are recorded.
- **Verified:** partly. The numbers are checked; I could not find a source for the seed claim.

**6. Terminology: "setting(s)" throughout**
- **Issue:** `docs/GLOSSARY.md` lines 151–154 retire bare "settings". The report uses the word in two senses:
  - one parameter: "5 settings", "10 settings, 49 grid values", "searched one setting at a time";
  - a whole parameter set: "a setting is chosen on three", "its untuned setting", "each candidate setting", "the setting its search started from".
  - For the nets, the "settings" (learning rate, steps, architecture) are what the glossary calls a training spec.
- **Severity:** medium.
- **Fix:** use "parameter" for one parameter and "configuration" or "operating point" for a full set, or add a glossary entry that fixes the word's meaning.
- **Verified:** yes.

**7. Table 1, column "what was tuned"** (CoactDetect "49 grid values", LoCo "46", rate+context "47")
- **Issue:** these are the declared grid sizes (`bench.FULL_GRIDS`, `meta.json` `hand_axes`; generator line 936 sums the declared axes). They include the context values that §4.1 says the context rule removed: 240 s for CoactDetect, 240 s and 480 s for LoCo, 240 s for rate+context. The values actually searchable were 48, 44 and 46. The same population is counted on two bases.
- **Severity:** low–medium.
- **Fix:** give the searchable counts, or add "(N refused by the context rule)".
- **Verified:** yes.

**8. §12, "1,728 inner fits of nets", against §4.1's description**
- **Issue:**
  - §4.1 describes, for each outer fold, 3 rotations × 3 training seeds per configuration. Over 24 configurations, 4 nets and 4 outer folds that makes 3,456 fits.
  - `ran.json` has 1,728 `inner:` stages. That equals 6 distinct training-fold pairs × 24 configurations × 3 seeds × 4 nets. So each inner fit is shared by the two outer folds whose training sets contain that pair.
  - The page never says this. It also bears on the independence discussion: the §4.2 fix made the outer refits distinct, while the inner fits are shared by construction.
- **Severity:** low–medium.
- **Fix:** add one clause in §4.1 or §12 saying inner fits are shared between outer folds.
- **Verified:** the count, yes. The sharing mechanism is inferred, not read from code.

**9. New terms missing from the glossary**
- **Issue:** the rule is that a new term enters the glossary in the same change. Missing:
  - "call"
  - "firing(s)". The page also uses "onsets" for the same thing: §2 "Each event's onsets" and Figure 1 "6 ROIs whose onsets", beside "2,595 firings".
  - "background". The glossary's word is "regime" (lines 319–324), while `meta.json` now says "backgrounds".
  - "empty recordings"
  - "the probe" (the glossary says "promiscuity probe")
  - "refit"
  - "failed-training signature"
  - "local-gap window" (the glossary says "ISI-adaptive")
  - the contestant names `chorus_norm`, `chorus_gain_norm` and `tube`. The glossary lists `line`, `line_bound` and `line_length` as detector-axis names but none of these three.
- **Severity:** low–medium.
- **Fix:** add the entries, or map each to the existing glossary term. Use one word for per-ROI events.
- **Verified:** yes.

**10. Figure 6 caption and the glossary's "shared false-alarm budget" entry**
- **Issue:** both say the budget is measured "on the empty recordings" (the glossary: "on recordings with nothing planted"). §4.4 and `meta.json` (`gate_empty_recording: null_quiet`) say only the quiet-background empty recordings gate; the busy ones are only reported.
- **Severity:** low.
- **Fix:** say "on the empty recordings at the quiet background" in the caption, and update the glossary.
- **Verified:** yes.

**11. Figure 10 against §7's "at every gap tried… at any matched gap"**
- **Issue:** the nets were re-scored at 2, 4, 8 and 16 s (`merge_gap.json` `net_gaps_sec`; Figure 9 plots 4 s). Figure 10 shows only 2, 8 and 16 s, so the 4 s part of the claim is not visible in it.
- **Severity:** low.
- **Fix:** add the 4 s rows, or say "at 2, 8 and 16 s".
- **Verified:** yes.

**12. Lede** ("the nets find more of the faintest events against a busy background")
- **Issue:** §8 and Figure 11 compare only the two chorus nets. `line_length` and `tube` are not shown.
- **Severity:** low.
- **Fix:** say "the chorus nets".
- **Verified:** yes.

**13. Figure 1 panel B heading and caption**
- **Issue:** the heading says "Ten minutes of it"; the caption says "15m40s to 26m", which is 10 min 20 s (`FIG1_WINDOW` is 940 to 1560 s).
- **Severity:** low.
- **Fix:** make the window exactly 10 minutes, or say "About ten minutes".
- **Verified:** yes.

**14. Category order, Figure 7 against Table 2, and §11**
- **Figure 11 row order:** CoactDetect is listed above the chorus nets. Table 1, Table 2 and Figures 7, 8, 10 and 12 all put the nets first.
- **locust in Figure 7B against Table 2:** the figure plots a value of about 0.55 as an ×. Table 2 gives no number ("the budget refused every setting"). The legend explains it, but the figure and table disagree on whether a number exists.
- **§11 participation:** "18% of the ROIs (6 of 33)" is placed beside "lower end is 18.18%, which is 6 of 33". Read that way, the bench sits at the interval's edge, not outside it. Only the rounded 0.18 label is outside.
- **Contamination policy:** `CLAUDE.md` says a known contamination "does not become a caveat". §11 lists it as a limit because "the project lead asked for exactly that in the brief". The brief as relayed to me says "limits stated plainly" and does not name the contamination.
- **Severity:** low for each.
- **Fix:** keep one row order throughout. Say the 0.18 label, not the planted count, is outside the interval. Quote or cite the brief's actual words on the contamination.
- **Verified:** yes for the first three; no for the contamination, since I have not seen the full brief.

### What I checked and found clean
- **Table 2:** all 13 differences from CoactDetect and all 12 corrected *t* values (×0.655, which is √(3/7)).
- **Basic counts:** 15/(15 + 6) = 0.71; 48 seeds, 12 per fold, 72 training recordings.
- **Figure 4:** four distinct fitting sets, each sharing 2–3 of its 5 recording seeds with the others.
- **Job counts against `ran.json`:** 1,963 = 1 + 24 + 1,728 + 210.
- **Budget overruns:** 4 + 7 + 3 + 11 refits of 80 exceeded the budget, per-fold sums correct. Refit counts of 210 distinct and 240 scored. A failure rate of about 1%.
- **Tuned minus untuned:** checked against `results.json` and Figure 12.
- **§7 against `merge_gap.json`:**
  - +0.010 with the net ahead in 4 of 4 folds;
  - +0.009 with the net ahead in 3 of 4 folds;
  - CoactDetect 0.731, 0.748 and 0.803;
  - `chorus_norm` from 0.741 to 0.775;
  - binned SCE 0.587 at 8 s;
  - CPU re-scoring within 0.0015 per refit.
- **Figure 8:** the right-of-zero marks (0.0001 and 0.0004) and the replicate's per-fold values (+0.003, −0.243, +0.003, +0.007; mean −0.057) match `results.json` and `replicate_summary.json`.
- **Table 3 against `crowded_check.json`:** every range and pass count, including binned SCE passing only in fold 4.
- **Cross-references:** every "section N", "Figure N" and "Table N" link resolves to what it claims.
- **Reserved words:** "modality", bare "adaptive" and "detection" do not appear.
- **Companion documents:** these facts agree:
  - the earlier +0.103 lead and `tube`'s tie with CoactDetect;
  - goal 2 decisions 2–8;
  - the launch at 16:14 on 2026-09-18 from commit e8764aa;
  - the grids and reference values in `bench.py` and `meta.json`;
  - the 2.5 s tolerance in `score.py`;
  - decision 3 and the 0.03% contamination figure in `HANDOFF-slow-comodulation-on-the-de-pinned-export.md`.
