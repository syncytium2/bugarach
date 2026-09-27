> Archived verbatim except machine-local paths (shown as `<darkroom>`, `<worktree>`, `<scratchpad>`, `<repo>`, SAP004) and redactions: in finding F1, times of calls on real recordings are replaced by `[t]`,
> because nothing derived from real data goes into this public repo (FOUNDATIONS §5). The finding's arithmetic
> stands: each caption is one minute later than the call.

GRANT 3 ok — Read, Grep, Glob

Role 3 (Cross-Examiner), round 1. Artifact: `<darkroom>\bugarach\2026-09-26-full-panel\briefing\index.html` (the built page), checked against `briefing.json`, the generator `<worktree>\tools\make_briefing.py`, the four companion READMEs (065/README.md, 065/RUN_C.md, 064/README.md, 064/count/README.md), `docs/GLOSSARY.md` and the CLAUDE.md plot conventions. No recording or slice ids are quoted below.

**Summary:** 1 blocking, 5 major, 8 minor. The blocking one: four example-figure captions give the wrong call time, and one of them reads "20m60s". The generator line that causes it is F1.

## What I checked and found consistent
- **Row counts.** Figure 1's panels (23, 19 and 21 rows) match Tables 2–4.
- **Table 1 tallies.** Each stream's three columns (above, includes zero, below) plus the reference row add up to the stream's total. I re-derived every above/includes/below count from Figure 1's SVG coordinates (zero line at x=696, about 2,608 px per unit of ΔF1) and all six rows match. The six "top row" ΔF1 values match the figure and Tables 2–4.
- **Row order.** Figure 1 lists the rows in the same order as Tables 2–4 on every stream.
- **Red marks.** Figure 1's red marks match the over-budget flags in Tables 2–4, row by row and bench by bench.
- **Seed counts.** The byline's seed counts (new bench: 48 fast, 24 slow, 24 combined; old bench: 24 each) match `briefing.json` n_seeds and RUN_C.md. RUN_C.md confirms that fast seeds are not doubled on the old bench.
- **Timestamps.** "1:33 AM" (05:33Z) and "8:03 PM" (00:03Z) match RUN_C.md.
- **ΔF1 range.** −0.086 to +0.063 matches 065 README finding 4. SPIKE-synch combined at +0.039 [+0.012, +0.065] matches.
- **Ruling-5 marks on coded proposals.** They match 065 README's axis table. The 12 proposals, and the searches that proposed nothing, match the rows present.
- **Review pages and recordings.** Table 5 has 8 × 3 = 24 pages, matching README step D. Table 6 has 17 + 17 + 13 + 19 = 66 recordings, matching "66 recordings".
- **Group order.** DI, OVX, MALE, ORX is kept in Tables 5 and 6.
- **Numbering.** Figures run 1–10 and Tables 1–6, both in sequence.
- **Slow no-pick row.** Slow chorus_gain_norm_part at 2.44 calls/h against a limit of 1 matches both READMEs.
- **Banned words.** No "modality", no "fire", no singular "data".

## Findings
(location · issue · severity · suggested fix · verified)

**F1**
- **Location:** Figures 2, 3, 6 and 9, the captions' "the call at …".
- **Issue:** The caption time disagrees with the viewer link's `t=` and with the figure itself. Examples:
  - Figure 2: the link's t=[t] and the PNG agree; the caption is one minute later.
  - Figure 3: printed one minute late.
  - Figure 9: printed one minute late.
  - Figure 6: printed as "20m60s".
- **Cause:** `make_briefing.py` line 769 is `f"{t / 60:.0f}m{t % 60:02.0f}s"`. It rounds the minutes instead of flooring them, so the minute runs one high whenever the seconds are 30 or more.
- **Severity:** blocking. The page sends Tony to the wrong minute in 4 of 9 examples.
- **Fix:** floor the minutes (`int(t // 60)`), round the seconds, and carry 60 s into the next minute. Better, reuse the minutes-friendly formatter the CLAUDE.md plot conventions name.
- **Verified:** yes (link `t=`, the Figure 2 PNG, the generator line).

**F2**
- **Location:** Section 2 intro, the headings "X against CoactDetect", and the captions of Figures 2–10.
- **Issue:** "CoactDetect" changes meaning between sections.
  - In Section 1, Figure 1 and Tables 1–4 it is CoactDetect at its **shipped** setting.
  - On the real recordings, 065/README step D says detection ran "CoactDetect at its proposal on every stream". Those proposals carry ruling-5 marks on all three streams.
  - The page says only "CoactDetect as it ran there". A reader will take the Section 2 reference to be the leaderboard's reference.
  - It matters. On fast, the chosen leader chorus_gain_norm_part has new-bench mean F1 0.641 against 0.651 for CoactDetect's proposal, so it sits below the setting it is shown against.
- **Severity:** major.
- **Fix:** name the setting everywhere in Section 2 ("CoactDetect · proposal"). State that it is not the leaderboard's reference and that it is itself §5.
- **Verified:** yes (065/README step D, Table 2).

**F3**
- **Location:** Tables 2–4, the red "over budget" marks, against 065/README finding 2.
- **Issue:**
  - 065/README says slow chorus_gain_norm_part is "the only row over budget" and that every other coded setting and pick is within budget on both spacings.
  - The page flags roughly 20 rows as over budget.
  - 064/README ("Two shipped points are out of budget on the realistic fast bench") agrees with the page, not with 065.
  - The generator's docstring (lines 119–120) knows the reason: the worker README counts only the no-coordination budget. It says the page "names each failure so the difference is visible", but the page never says so.
- **Severity:** major. The companion contradiction is unreconciled on the page.
- **Fix:** add one sentence to "How to read it" or to the budget entry in Terms. It should say that the pick and the 065 README use only the no-coordination budget, and that the page applies all four budgets the search's admissibility rule holds.
- **Verified:** yes.

**F4**
- **Location:** Tables 2 and 4 (count (binned) proposal on fast, count (sliding) proposal on combined): the mark "ruling 5: k_offset at its limit (0)" and the Figure 1 label "proposal §5".
- **Issue:**
  - 064/count/README says k=0 "is a hard lower limit by design … it reads as bracketing reason `limit` and not as a ruling-5 off-limit".
  - The page brands both rows §5, and Figure 1's caption defines §5 as "not adoptable".
  - Cause: `_unbracketed()` (lines 135–144) turns every unbracketed axis into a ruling-5 mark, whatever the reason.
- **Severity:** major. The page contradicts the companion's ruling and its adoptability.
- **Fix:** mark §5 only for bracketing findings of kind `off_limit` or `cap`. Show `reason: limit` as "at its design floor (not ruling 5)", or resolve the disagreement with the count README's author before shipping.
- **Verified:** yes.

**F5**
- **Location:** Tables 2–4, the "new mean F1" / "old mean F1" columns against the ΔF1 columns and the Terms definition of ΔF1.
- **Issue:**
  - Terms and "How to read it" define ΔF1 as the mean over the same seeds of (row F1 − CoactDetect F1). If that held, and mean F1 were the mean of the same per-seed F1s, the ΔF1 column would equal the difference of the mean F1 columns.
  - It often does not:
    - Fast SPIKE-synch shipped: 0.686 − 0.608 = 0.078, printed +0.063.
    - Fast count (sliding) proposal: 0.075 vs +0.060.
    - Combined chorus_gain_norm_part: 0.062 vs +0.057.
    - Fast old-bench LoCo proposal: 0.036 vs +0.031.
  - Others match (slow LoCo: 0.037 vs 0.038).
  - `briefing.json` gives the same n_seeds for each pair, so seed count does not explain it. The two columns sit on different counting bases, and the page does not say which.
- **Severity:** major. A reader who subtracts gets a different number.
- **Fix:** define "mean F1" in Terms (pooled over backgrounds? pooled events rather than per-seed F1?) and say why it does not difference to ΔF1. Or drop the column.
- **Verified:** the arithmetic, yes. The cause, no.

**F6**
- **Location:** Terms "budget" and "pick"; the marks in Tables 3–4.
- **Issue:** Retired glossary terms are used:
  - "(the promiscuity probe)" and "calls in the dense block with nothing planted (the probe)". The glossary retired both *promiscuity probe* and *probe* on 2026-09-21 in favour of **elevated-rate test**.
  - "no seed within the empty-recording budget" and "recording with nothing planted". The glossary retired *empty recording* in favour of **no-coordination test**, and says explicitly "Not 'empty'".
  - The budget set itself (precision change between backgrounds; calls per hour outside the elevated-rate window) is not in the glossary. The glossary's only "fourth budget" is the close-events test, which is a different set.
  - Also, 064/count/README says "all three budgets" where the page says four.
- **Severity:** major, under the reserved-word and glossary rule. The page's four-budget set contradicts the glossary's and the count README's.
- **Fix:**
  - Rename to "elevated-rate test" and "no-coordination test" in `BUDGET_WORDS` (lines 106–109), in the mark text and in Terms.
  - Add the page's four budgets to `GLOSSARY.md` in the same change, or reconcile them with the close-events-test definition.
- **Verified:** yes.

**F7**
- **Location:** Section 2 (fast), "Lanes: chorus_gain_norm_part, LoCo, CoactDetect", and the slow heading "LoCo against CoactDetect".
- **Issue:** "LoCo" is LoCo · proposal on fast (the only LoCo detection ran there) but LoCo · shipped on slow. The label changes meaning between streams, and Section 1 always carries the setting.
- **Severity:** minor.
- **Fix:** label lanes and headings with the setting ("LoCo · proposal", "LoCo · shipped").
- **Verified:** yes (065/README step D: proposal where one exists).

**F8**
- **Location:** Section 2 selection rule against its "Passed over" note.
- **Issue:**
  - The intro gives the rule as the top row that ran on real recordings, minus CoactDetect and minus over-budget rows. The fast note then adds an unstated second rule: skip a row with no disagreement to show.
  - The intro also does not say that count rows, and shipped rows that have a proposal, never ran on real recordings. That is why fast rows 7 and 8 (count (binned) proposal; LoCo shipped, which carries no flags) are silently skipped.
  - The slow third lane "line" skips rank 2, count (sliding) shipped, for the same unstated reason.
- **Severity:** minor.
- **Fix:** state both conditions in the intro, and name which rows ran on real recordings (six coded detectors at proposal-else-shipped, plus eight picks).
- **Verified:** yes (065/README step D).

**F9**
- **Location:** Table 4, row 6 (tube_part): "precision change … 0.10 against a limit of 0.1".
- **Issue:** The flagged value prints equal to the limit (the true value is 0.1035). `budget_words` formats the value with `:.2f` and the limit with `:g`.
- **Severity:** minor.
- **Fix:** print three decimals (0.104 against 0.100), matching the count README's style.
- **Verified:** yes (`briefing.json`).

**F10**
- **Location:** Byline, "new bench … scored 2026-09-26 1:33 AM EDT" / "old bench … 8:03 PM EDT".
- **Issue:** The count rows come from different runs: `064/count/fresh-realistic`, scored about 6:33 PM, and `065/fresh-bench-count`, finished 8:07 PM (RUN_C.md). `briefing.json` lists them under `sources.extra`, but the byline dates every row by the main files only. The byline also mixes 12-hour times ("8:03 PM") with 24-hour times ("20:29 EDT").
- **Severity:** minor.
- **Fix:** name both source runs per bench, and use one time format.
- **Verified:** yes.

**F11**
- **Location:** Figure 1 and Table 3 label "best seed, seed 4" (slow chorus_gain_norm_part), against "pick, seed N" everywhere else.
- **Issue:** "best seed" is not in Terms, and the Figure 1 legend calls the case "no pick".
- **Severity:** minor.
- **Fix:** add "best seed (no pick): comparator only" to Terms, or label it "no pick · best seed 4".
- **Verified:** yes.

**F12**
- **Location:** Table 1, "top row (ΔF1)" for fast / new.
- **Issue:** It names SPIKE-synch · shipped with no mark, although Table 2 and Figure 1 flag it over budget on both benches, and Section 2 excludes over-budget rows as leaders. The at-a-glance table reads as a headline winner that the rest of the page disqualifies.
- **Severity:** minor.
- **Fix:** mark flagged top rows in Table 1, or add a "top row within budget" column.
- **Verified:** yes.

**F13**
- **Location:** Table 1 cells "1 rows".
- **Issue:** Singular/plural.
- **Severity:** minor.
- **Fix:** "1 row".
- **Verified:** yes.

**F14**
- **Location:** Table 2 row 11, binned SCE proposal (fast), ruling-5 marks.
- **Issue:** The page shows only "threshold_pctile at its cap". 064/README also lists "no merge" (off-limit) for this proposal, flagged ⚠ because its step-off check compared two off-limits. 065/README's axis table omits it too, so the companions disagree with each other and the page follows 065.
- **Severity:** minor.
- **Fix:** add the merge-gap off-limit mark with 064's ⚠ caveat, or note why it was dropped.
- **Verified:** yes.

## Could not verify
- The old-bench budget values equal the new-bench values in several rows (for example precision change 0.15 on both). That is plausible if the no-coordination recording and the precision swing do not depend on spacing, and the count README shows the same pattern. I did not trace it in the scorer.
- The "2.5 s scoring tolerance" in Section 2 and the old bench's "at least 120 s apart" in Terms.

A note for the run record: this report quotes no recording ids.
