GRANT 11 ok — Read, Grep, Glob

# Argument order review: `docs/learned/slow_comodulation/README.md`, round 1

I held only the three tools my role is granted, and I edited nothing. I read the whole page, opened all four figures and checked one cross-reference against its source.

## Spine (one claim per section, in page order)

1. **Status banner (lines 3–7).** This is one exploratory run on baseline windows. The page exists because the label-free thread cannot decide whether shared modulation counts as coordination until someone shows what that modulation is.
2. **The problem.** Two things put many ROIs in the same window: onsets that line up, and firing rates that rise and fall together. Rigid shift was chosen to destroy the first. Whether it also destroys the second, and how much of the second the recordings hold, decides what a label-free detector learns.
3. **How to read the measurement (Figure 1, three kinds of activity).** Plotted against lag, the population cross-correlogram tells the two apart: events make a narrow peak and shared modulation makes a broad shoulder. Shared modulation also adds sub-second coincidences, and the simulator's background has no shoulder at all.
4. **What the surrogates remove (Figure 2).** Rigid shift spreads an event peak into a plateau about 2*J* wide. It removes only modulation faster than about *J*, and slower drift passes through untouched. The 2-minute block control can tell a curve that falls from one that stays flat.
5. **What the recordings hold (Figure 3 and the table).** Every folder has both a peak and a shoulder. On the lab fast stream the shoulder is flat drift over minutes: rigid shift and CoactDetect removal leave it unchanged, and it holds 91 % of the excess. The lab slow stream also has a dip after events, which rigid shift fills in.
6. **By group (Figure 4).** The pooled curve does not come from one group alone. No group difference can be claimed, because group is confounded with imaging day.
7. **What this changes for the label-free thread.** On the fast stream the models were not paid for the drift, so the decision is narrower than first framed. On the slow stream the real-versus-shifted contrast rewards three things at once. A small *J* is not a modulation control, and `count_excess` removes drift by construction. The page then says the drift's source is unknown, and the decision Tony owes is whether it belongs to coordination, to background, or to the producer.
8. **What this does not settle.** A list of technical limits: pairs not counts, the 1 s cut, partial CoactDetect removal, how clean the block control is, the 20-minute window, 8 draws, baseline only.
9. **Reproduce.** Commands and tests.

## Arc used

I judged the page against a teaching arc, adapted from the default analysis arc:

**problem → instrument → how the method behaves where the answer is known → what the recordings hold → what it changes → decision owed → residual risk.**

This order departs from the default in a defensible way. The instrument and the synthetic surrogate results have to come before the recordings, because Figure 3's legend (block control, three rigid-shift *J* values, CoactDetect removal) and the phrase "the drift world" can't be read without Figures 1 and 2. So Figure 3 should not simply move to the front. The problem is that the page never states this order, and it holds back both the answer and the decision until the reader has gone through all of it.

## Cold open

**What the reader sees first:** a 5-line status blockquote (interval convention, the measured/argued legend, why the page was written). Then "The problem": an abstract contrast between two kinds of co-activity and a question about rigid shift.

**Is that the problem?** Partly. It poses the question, and it doesn't open on history or scope. But it gives the problem only in the abstract:
- It never says the recordings actually have this drift.
- It never shows what the drift looks like in a real recording.
- It never names the decision the page leads to.

The first real data appear in Figure 3, after two synthetic figures and about 90 lines. The headline is the second bullet under "What the recordings hold" (line 121). The three-way decision is the last paragraph of "What this changes" (lines 183–184), about 30 lines from the end.

## Verdict

The section order is mostly right and should largely stay. The page needs:
- a claim-first lead that states the headline finding and the decision;
- a real-data view of the problem, or at least a sentence of real finding, before the instrument;
- "By group" moved out of the path between evidence and decision;
- the decision under its own heading.

The headline should lead **as a claim**, not as evidence. Its proof can't be judged before Figures 1 and 2, but a reader who knows the conclusion reads those figures looking for it.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified |
|---|---|---|---|---|---|
| 1 | Top of page (banner, then "The problem") | The answer and the decision both come last. The fast-stream drift that rigid shift leaves untouched (line 121) and the coordination/background/producer decision (lines 183–184) sit at the bottom. The reader holds two synthetic figures and a 9-row table in suspense without knowing what they are building toward. Tony asked to have slow co-modulation explained because he "cannot ignore it"; the page should tell him in its first screen that the recordings have it and what he will have to decide. | high | Right after "The problem" (or folded into its last paragraph), add 3–4 sentences stating what the page finds and what he must decide. **What it finds:** on the lab fast stream, 91 % of the excess coincidence sits beyond 1 s. That excess is drift over minutes, and rigid shift at every *J* tried leaves it in place. Its source is unknown. **What he must decide:** whether shared drift counts as coordination, as background to subtract, or as a question for the producer. Then one sentence stating the order: measurement, then surrogates on synthetic worlds where the answer is known, then the recordings. | yes |
| 2 | "The problem" and Figure 1 | The problem is never shown as it looks in the recordings. The first figure is synthetic. Real data appear only in Figure 3, and only as correlograms, which already need the instrument to read. The one concrete picture of a busy stretch (Figure 1's lit-share row and raster) is of simulated worlds. | medium | Before the measurement section, show one real lab fast-stream recording: lit-ROI share over the 20-minute baseline plus its raster, where the drift is visible. Label it as what the rest of the page measures. At minimum, point in prose to where the drift can be seen. Whether this should be a new figure is agent 9's call; this row is only about where the first contact with real data happens. | yes |
| 3 | "What this changes", first bullet (lines 158–159) | The old framing (shared modulation on 10–45 s) first appears while it is being corrected. The reader can't see the question narrow because they were never told what it was. | medium | In "The problem", state the question as the thread framed it: "does shared modulation on timescales of 10–45 s count as coordination?" Link its source. The correction in "What this changes" then lands on something the reader already has. | yes |
| 4 | "By group" section and Figure 4 | This section sits between the evidence and its consequences, and its own conclusion is a null ("does not show a group difference"). It delays the handoff from "What the recordings hold" to "What this changes" with a full figure. Its one job, showing the pooled curve isn't one group's, is a robustness check. | medium | Move it after "What this does not settle", as an appendix-style section. Leave a one-sentence pointer at the end of "What the recordings hold": "the shoulder is present in all four groups (Figure 4, by group); group is confounded with imaging day." | yes |
| 5 | Last paragraph of "What this changes" (lines 178–184) | The decision the page exists to set up has no heading of its own. It is the unlabeled closing paragraph of a bulleted section, and it opens with an unsettled point ("cannot say where the drift comes from") that belongs with "does not settle". The page's destination is easy to miss when skimming. | medium | Give it its own heading, for example "The decision this sets up", between "What this changes" and "What this does not settle". Lead with the three-way question, then the possible sources of drift that make it a real choice. | yes |
| 6 | "What the recordings hold", lines 101–115 | The evidence comes before the claim. A 9-row, 5-column table appears before the section's first claim ("Every folder has both a peak and a shoulder"). Inside the bullets the peak comes first, although the shoulder is the page's subject and the peak is already known. | medium | Order the section as: claim sentence, then shoulder bullet, then share-of-excess bullet, then peak bullet, then Cossart. Put the table after the bullets as the numbers behind them, or trim it to the rows the bullets cite. | yes |
| 7 | "What the surrogates remove" (line 61) and "What the recordings hold" (line 91) | Both sections open straight on the figure and caption, with no sentence saying what the figure shows. The reader decodes Figure 2's 15 curves before reaching the three facts at line 72. | low | Open each section with its claim in one sentence. For Figure 2: "Rigid shift spreads events and removes only modulation faster than *J*; drift slower than *J* passes through." Then the figure. | yes |
| 8 | Measurement section, lines 55–57 | "No benchmark in this repository contains a shoulder" is a consequence that arrives before the reader knows the recordings have one, so it can't yet be weighed. It is stated again, in its proper place, in the last bullet of "What this changes" (line 175). | low | In the measurement section, keep only what the reader needs to read Figure 1: the orange control is how the simulator draws background. Leave the benchmark consequence to "What this changes". | yes |
| 9 | Status banner (lines 3–7) | The reader's first lines are conventions (interval over mice, the measured/argued legend) before the motivation, which comes in the banner's last sentence. It is short, so the cost is small. | low | Put the motivation sentence first in the banner, or move the notation legend just above the table, where it is first used. | yes |
| 10 | Measurement section (Figure 1) through "What the recordings hold" | Placement check, no defect. Excess coincidence is defined immediately before Figure 1 uses it. *J* is defined in "The problem" before Figure 2 uses it. The ⚠ on how clean the block control is sits before Figure 3, which needs it. The slow-stream dip paragraph comes before the "What this changes" bullet that relies on it. | none | Keep. | yes |

**Noticed in passing, outside my role (for agents 1 or 3 to adjudicate):** line 158 says "The goal page asks whether *shared modulation on timescales of 10–45 s* counts as coordination." That phrasing isn't in `docs/goals/unsupervised-learning.md`. It is in `docs/learned/tube_self_supervised/README.md` at line 395 ("Does shared modulation on timescales of 10–45 s count as coordination?"). The attribution, or the link added under finding 3, should point there. Verified: yes.

Files examined:
- <worktree>/docs/learned/slow_comodulation/README.md
- <worktree>/docs/learned/slow_comodulation/fig1_three_kinds.png
- <worktree>/docs/learned/slow_comodulation/fig2_what_the_surrogates_remove.png
- <worktree>/docs/learned/slow_comodulation/fig3_recordings.png
- <worktree>/docs/learned/slow_comodulation/fig4_by_group.png
- <worktree>/docs/goals/unsupervised-learning.md (searched, not read in full)
- <worktree>/docs/learned/tube_self_supervised/README.md (line 395 only)
