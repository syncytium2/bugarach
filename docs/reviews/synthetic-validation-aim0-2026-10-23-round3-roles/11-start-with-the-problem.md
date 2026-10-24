GRANT 11 MISMATCH — missing none; holds Edit, Write, Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch/update/guide (NotebookEdit and others available as deferred). Spawned via the inline general-purpose fallback, so the run record's `roles:` line must say the review took a fallback path. I used only Read and Grep. I did not edit, create or run anything.

**Surface checked:** the page's section order (lines 1–464) against the `docs/goals/README.md` order and the sibling goal pages. In detail: the extract (page lines 16–329 and 362–397) and the glossary's new section (order only).

**Arcs used.**
- (a) README: goal → where it stands → settled → tried and dropped → waiting on Tony → open work → where the work lives → keeping true.
- (b) Default, applied inside each result block: problem → cost → method → what it gets wrong → fix → evidence → residual risk.

## Spine (one claim per section)

0. Goal paragraph: the toolset must be validated on synthetic streams that mix two or more sources.
1. Where it stands, dated bullets: Aim 1a showed a fixed K fails and the assessor can't measure jitter. Aim 0 predicts the tool and a joint fit recovers jitter. Membership converges to random as 1/M. Order has closed forms. The page was murderboarded.
2. Symbols table: definitions, which make no claim.
3. Aim 1a: on one generator, a fixed K fails across backgrounds, the assessor's jitter is flat, participants need a window wider than the jitter, and the share moves least.
4. Aim 0 predictions: a window-sharing model (g_n plus the at-most-one-event term) predicts the tool's participants closely and rate/share less well. A joint fit recovers σ ≥ 0.2 s. Chance clusters follow 60q(1−q)².
5. Two more sessions: the same core derivation three times, a consistency check only, plus some results only the blind passes found.
6. Membership: the excess falls as 1 + (E−1)/M, and population-count tools can't see membership.
7. Order: a template reads as jitter. F = (2/π)arctan r. The no-order bias c/√n̄ is fitted and may exceed the lab-scale signal. Kreuz comparison not made. The August result is untested.
8. Generator implications: a source = (k, σ) + membership rule + template, which is close to PP-Seq.
9. Settled: Tony's rulings, then the results rows above.
10. Tried and dropped: the superseded approaches.
11. (Context) What the tree has. 12. Plan, Aim 0: nine next steps, "owed checks first, then derivations".
13–16. (Context) Aim 1–3; Waiting on Tony; Open work; Not here; Where; Keeping true.

**Cold open.** The reader first sees the goal (two or more sources), then a dated log whose first substantive line is Aim 1a's two failures. That is the problem, so the cold open passes.

## Findings

Columns: # · location · issue · severity · suggested fix · verifiable against a source

1. **Goal-page order, page lines 330–419 and 441.**
   - **Issue:** "What the tree has" and "The plan" sit between *Tried and dropped* and *Waiting on Tony*, and "Not here" sits before *Where the work lives*. None of the three has a slot in the README's stated order, no sibling goal page has a Plan section, and nothing on the page says why it deviates.
   - **Also:** plan item 2 and *Open work* item 1 point forward into sections the README order puts later or overlapping. Plan Aim 0 is in effect "open work", and *Open work* item 1 just says "see *The plan*".
   - **Severity:** minor (the deviation is unstated).
   - **Fix:** either state the deviation in one line under "## The plan" (the plan is a goal-specific section between dropped and waiting), or fold the Aim 0 next steps into *Open work* and keep "The plan" as Aim 1–3 only.
   - **Verifiable:** yes (README line 117; sibling pages' headings).

2. **Figure 1 caption, extract lines 48–50.**
   - **Issue:** The problem section shows the fix first. The violet joint fit (Aim 0) is drawn, and the caption's conclusion is "only the joint fit tracks jitter". The reader can't evaluate that until extract line 119, two subsections later.
   - **Severity:** moderate.
   - **Fix:** end the caption on Aim 1a's own finding ("…the assessor's jitter is flat"). Mark the violet series "(explained in *Aim 0, the predictions*)", or move that sentence to the Figure 2 discussion.
   - **Verifiable:** yes.

3. **Aim 0 predictions, extract lines 90–100 ("What it rests on").**
   - **Issue:** The prior-art paragraph sits between the core claim (83–88) and its evidence (Figure 2, residuals 102–137). The reader has to hold the claim through a literature survey before seeing whether it holds.
   - **Severity:** minor.
   - **Fix:** move "What it rests on" after the residual bullets, just before the "checked by two more sessions" section.
   - **Verifiable:** yes.

4. **Aim 0 predictions bullets, extract lines 115–137.**
   - **Issue:** The section says "Aim 1a's two failures are what it answers" (line 78), but the bullets don't follow those failures. The answer to failure 1 (fixed K: chance clusters at K) comes **last**, after rate/share and the "not predicted" bullet. Failure 2 (jitter) is answered second, by the joint fit. The reader is never told which bullet answers which failure.
   - **Severity:** moderate.
   - **Fix:** after the core prediction, order as: participants (the base) → joint fit, labelled "answers failure 2" → chance clusters at K, labelled "answers failure 1" → rate/share residuals → not predicted.
   - **Verifiable:** yes.

5. **Two-source claim, extract line 157; plan item 3 (line 325).**
   - **Issue:** The one result that bears on the goal's premise ("two or more sources") is "two equal-jitter sources are inseparable from pair and triple counts — stated, untested". It first appears as a row in the consistency table and is never stated as a claim. *Where it stands* never tells the reader that nothing yet addresses two sources, so the cold open implies more progress on the goal than exists.
   - **Severity:** moderate.
   - **Fix:** add a line to the Aim 0 predictions (or the 10-23 status bullet): "Two sources: predicted inseparable at equal jitter from pair/triple counts; untested (plan item 3)". Let the table then confirm it.
   - **Verifiable:** yes.

6. **Event-floor paragraph, extract lines 169–171.**
   - **Issue:** The evidence for Aim 1a's first bullet (lines 56–61, the event floor) arrives two sections later, inside the blind-sessions section. It is labelled "*Aim 1a*", but the reader of Aim 1a never gets it.
   - **Severity:** minor.
   - **Fix:** move the two sentences into Aim 1a's fixed-K bullet as its support, credited "(blind B)". Leave a pointer in the blind section.
   - **Verifiable:** yes.

7. **Shared-seed warning, extract lines 52–54.**
   - **Issue:** Fix history sits between Figure 1 and the findings. It repeats *Tried and dropped* (line 301), and it makes the reader process a corrected flaw before the result.
   - **Severity:** minor.
   - **Fix:** shorten it to a clause in the heading or caption ("each recording has its own seed; the shared-seed run is in *Tried and dropped*"), or put it after the findings.
   - **Verifiable:** yes.

8. **Membership, extract lines 183–197.**
   - **Issue:** The figure and caption ("The excess falls as 1/M, and reuse E/M sets it") come before the model and assumptions that make them intelligible: M assemblies, equal use, perfect readout, and the ratio 1 + (E−1)/M (lines 192–196). The evidence leads the claim.
   - **Severity:** minor.
   - **Fix:** put the assumptions-and-formula paragraph before Figure 3.
   - **Verifiable:** yes.

9. **Order section, extract lines 202–268.**
   - **Issue:** The section opens on a claim, the template-as-jitter confound, without its motivating problem. Its problem (the August synfire anti-correlation with spike count, and whether Kreuz's indicator measures finite-size bias) arrives last, at lines 240–260. The most consequential claim, "at the lab's scale the signal may sit below the bias" (235–238), comes after three technical bullets. Plan item 1, the page's top-priority next step, is rooted in that final paragraph. Membership got a problem-first opening (Tony's question); order did not.
   - **Also:** the opening confound belongs with the joint fit, which already says "see *Order*".
   - **Severity:** moderate.
   - **Fix:** open with the problem: the August result plus the question "does an order indicator have a no-order floor?". Then the lab-scale consequence, then the closed forms, then the Kreuz comparison table. Move or duplicate the template-as-jitter sentence into the joint-fit bullet.
   - **Verifiable:** yes.

10. **Figure 4, extract lines 208–221.**
    - **Issue:** The caption uses "score sort and a local search" before either is defined (lines 218–221).
    - **Severity:** minor.
    - **Fix:** put the `order_limit.py` method paragraph before the figure (the same move as #8).
    - **Verifiable:** yes.

11. **Plan Aim 0 order, extract lines 316–347.**
    - **Issue:** The stated rule ("owed checks first, then derivations later aims will use") is sound, but three things break it:
      - The boundary between the two groups is never marked.
      - Item 2 ("Ask Tony") is not a session step. It duplicates *Waiting on Tony*, and *Open work* already excludes it.
      - Within the "owed" group, the August/Kreuz side question (item 1) ranks above the two-source check (item 3), which is the goal's premise, and no reason is given.
    - **Also:** item 8 (joint fit against the correlogram) is a check owed by a *Settled* row but sits among the later derivations, gated on `--folder` without saying so. Item 9 is a presentation task, not a derivation.
    - **Severity:** moderate.
    - **Fix:** split the list into "Owed by this page" (current items 1, 3, 4, plus 8, marked "once `--folder` lands") and "For later aims" (5, 6, 7, 9). Drop item 2 into a pointer to *Waiting on Tony*. State why item 1 precedes item 3, or swap them.
    - **Verifiable:** yes.

12. **Settled, extract lines 280–295.**
    - **Issue:** None. Rulings come before results, and the results rows follow page order. The order passes.
    - **Verifiable:** yes.

13. **Glossary "Synthetic-validation vocabulary".**
    - **Issue:** None. It is a reference list, not an argued sequence. Terms are defined before they are used within the list ("membership" before "exchangeable limit").
    - **Verifiable:** yes.

Files: `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\docs\goals\synthetic-validation.md`, `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\docs\goals\README.md` (line 117), `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\_scratch\r3_extract.md`, `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\docs\GLOSSARY.md` (lines 659–691).
