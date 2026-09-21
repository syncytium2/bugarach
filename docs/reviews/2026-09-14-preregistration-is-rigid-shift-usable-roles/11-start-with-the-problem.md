GRANT 11 ok — Read, Grep, Glob

# Argument order review: "Pre-registration — is rigid shift a usable surrogate on these data?"

**Verdict:** the sections are in a sound order and none should move; the ordering problems are inside sections. Three are medium:
- The value that defines "coordinated" (1.0 s) appears only in the last gate, after the claims that depend on it.
- "Why rigid shift" uses words the page defines later, or never.
- The warning about how VIABLE may be reported sits far above the outcome table.

The medium problem most likely to change what someone writes is the VIABLE warning.

## The spine (one claim per section)

For each section: its claim, and the earliest point at which a reader can judge it.

0. **Banner, and why this page exists.** The page is signed and frozen. The last surrogate screen went in circles because its verdict rules were written after the data, so this page fixes the rule first. *Judgeable where it sits.*
1. **The question.** Rigid shift is usable only if a classifier that cannot see coordination fails to tell it from real data, and it also removes planted coordination at this project's timescale. Yes sends the goal to the model; no stops the goal. *Only in outline where it sits.* "Coordination-blind classifier", "planted coordination" and the timescale are defined later, in the Leak gate and the Destruction gate.
2. **Why rigid shift, and why only rigid shift.** In the exploratory run, rigid shift was the only candidate the leak test could not detect at a displacement big enough to matter. So if rigid shift stops, the goal stops. *Judgeable only after the gates.* That needs the fast/slow streams, Cossart, the 0.55 accuracy margin, uniform dither as the known leaker, and the seed-0 defect, which the page explains only at line 97.
3. **What this run cannot claim.** The data were already used. A VIABLE result means it held up under a rule set in advance, not that it was replicated. *Judgeable only after Data and the outcome table.* It uses "both folders", "mouse folds" and "VIABLE" before any of them is defined.
4. **Data.** Lab-folder baselines, with fast and slow judged separately; Cossart for the leak test only; zero-event ROIs and the motion-pinned recordings stay in. *Judgeable where it sits.*
5. **The displacements.** Three values of *J* per stream, fixed now, with bounds widened to a 98.3 % interval (Bonferroni). *Only partly judgeable where it sits.* Whether 1.6 s is big enough depends on the 1.0 s timescale, which first appears at line 119.
6. **The gates.** Every gate can fail, and each has a control that shows it can. *Judgeable where it sits.*
   - **Leak:** passes if the upper bound on accuracy is below 0.55, with a uniform-dither positive control and a 4-of-20-seeds negative control.
   - **Count preservation:** passes if the count change stays within ±2 %; the `edge_thinning` control must fail.
   - **Destruction:** passes if at most 25 % of planted coordination survives, scored at 1.0 s, with controls, a saturation void, and no destruction scoring on Cossart.
7. **The outcome.** Each stream gets PASS, VOID or FAIL; the streams combine into VIABLE, NARROWED or STOPPED, and each outcome commits to a next step. *Judgeable where it sits.*
8. **Not in this run.** Band statistics, other candidates, the ROI swap, MAHICE, and model training are excluded. *Mostly judgeable.* The band-statistics item makes sense only if you have read the overnight page.
9. **What has to be built, and its cost.** A runner, a bin parameter, two rules with tests, and a run of a few hours priced by a smoke run first. *Judgeable where it sits.*
10. **Review, once.** The murderboard runs before signing. *Judgeable where it sits, but the Amendments section contradicts it.*
11. **Sign-off.** Accepted as written. *Judgeable where it sits.*
12. **Amendments.** The page was signed before its review ran. *Judgeable where it sits, but nothing above points the reader here.*

## The arc I judged it against

For a pre-registration: question → why this candidate → what the run cannot claim → data → parameters → gates with controls → decision rule → what each outcome commits to → exclusions → build and cost → review → sign-off.

The page follows that arc section for section, with no unstated departures. Every section has a job in the argument, and none belongs in an appendix. The one-candidate paragraph in "Why rigid shift" belongs there because it justifies testing only one candidate.

**Cold open.** A reader first sees the signed-and-frozen banner and a short account of the process failure, then the question at line 15. For a frozen pre-registration it is reasonable to open on the freeze, since that changes how every line below is read. But the scientific problem only appears as a clause at line 21: the self-supervised objective needs a negative class, and the surrogate is meant to be it.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source |
|---|---|---|---|---|---|
| 1 | The Destruction gate, line 119 (the 1.0 s timescale); depended on at lines 19, 29, 33, 69 | The value that defines "coordinated" is the one everything else rests on. The question points to it, "Why rigid shift" leans on it ("seconds-scale coordination"), and the displacement table can only be judged against it: is 1.6 s big enough against a 1.0 s window? It first appears as a sub-bullet of the last gate, about 50 lines after the displacements. The person running the tests won't get them wrong because of this, but anyone reviewing the choice of *J* can't judge it when they reach it. | Medium | The sections can't move. Record a residual ⚠: the 1.0 s timescale in the Destruction gate governs the displacement choice. Optionally add a one-line dated amendment saying so. | yes |
| 2 | "Why rigid shift", lines 27–36 | The case for the only candidate uses words defined later or nowhere: fast/slow (first at line 53, never defined), Cossart (line 55), "per-ROI leak test" (line 84), accuracy 0.495–0.524 with no chance level or 0.55 margin (line 90), "the seed-0 defect" (explained only at line 97, "that was the defect"), "the other survivors", "uniform dither" (line 93), "Joint-ISI" (never), and "STOP" (outcomes use "STOPPED", line 146). The predecessor, `2026-09-10-surrogate-evaluation-overnight.md`, put a Terms table (lines 67–97) before first use; this page dropped it, so its case for the candidate can't be judged by someone who hasn't read that page. | Medium for outside reviewers, low for whoever runs it | Add a dated amendment naming the overnight page's Terms section as this page's vocabulary, with one sentence on what the seed-0 defect was and that the 4-of-20 rule is its fix. Otherwise record a residual ⚠. | yes |
| 3 | "What this run cannot claim", line 45, versus the outcome table, line 143 | The reporting rule ("held up under a rule declared in advance, not replicated … It must be reported that way") sits about 100 lines above the table. The table's VIABLE row says only "the goal moves to the model tier", and the section also uses "both folders", "mouse folds" and "VIABLE" before they are defined. Whoever writes up the result will work from the outcome table and "What each outcome commits to next", and neither carries the rule. So a VIABLE report could fairly be written as a replication. | Medium; worth an amendment, because the report's wording could come out wrong | Add a dated amendment saying the VIABLE and NARROWED rows carry the "held up under a rule declared in advance" wording from "What this run cannot claim", and that the write-up uses it. | yes |
| 4 | The question, lines 17–23, versus the gates and outcome, lines 99–146 | The question sets out two conditions (no leak, removes coordination) and a yes/no answer. The rule has three gates and five results: PASS/VOID/FAIL per stream, and VIABLE/NARROWED/STOPPED overall. Count preservation arrives at line 99 without the question having mentioned it, and NARROWED has no place in "If yes / If no". A reader checking the gates against the question expects two gates and meets three. | Low | Record a residual ⚠: the question states two of the three gates, and the outcome is not binary. | yes |
| 5 | Banner and why this page exists, lines 3–13 | The page opens on how it was signed and on process history, not on the scientific problem. Why a surrogate is needed at all first appears as a consequence clause at line 21. Opening on the freeze is defensible here, but the page never says it is making that choice. | Low | No amendment needed. The goal page (`docs/goals/unsupervised-learning.md`) is outside the frozen region and can supply the motivation. Note it in the ledger. | yes |
| 6 | Amendments, lines 192–196, versus the banner (lines 3–6) and "Review, once" (line 177) | Reading top-down, you meet "every value accepted as proposed" and "`/murderboard` runs … before signing", and only in the last lines learn that the review had not run and values may still be amended. The banner says amendments go below but not that they must be read before running anything. Someone who stops at the gates could run with values an amendment has since changed. | Low | Outside the frozen region: change the goal page's pointer (`docs/goals/unsupervised-learning.md` lines 35–36) to say "read its Amendments section before executing". | yes |
| 7 | "Not in this run", line 158 | "The band statistics and their family size" refers to something this page never introduces, so a reader who has only this page can't tell what is being excluded or why it matters. | Low | Record a residual ⚠, or cover it in the vocabulary amendment from finding 2. | yes |

**Checked and fine:**
- Data comes before displacements, which come before the gates.
- Data's "Cossart … leak test only (see *Destruction*)" gives a forward pointer, so it isn't a defect.
- The displacement section says explicitly that its 98.3 % interval applies to bounds "below".
- The count-preservation gate explains its own purpose (the `tube` foot gun) before its pass rule.
- The outcome table comes right after the last gate, and each outcome's commitments follow it directly.
- Build and cost comes after the rules that need building.
- The sign-before-review reversal is already recorded honestly under Amendments, so it is not a new finding.

**Files:**
- Artifact: `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md`
- Compared against: `docs/proposals/2026-09-10-surrogate-evaluation-overnight.md` (its Terms section) and `docs/goals/unsupervised-learning.md`
