GRANT 11 ok — Read, Grep, Glob

# Role 11: argument order ("Start With the Problem")

**Artifact:** `<worktree>/docs/learned/rigid_shift_look/README.md`, read against `<worktree>/docs/goals/unsupervised-learning.md`.

The note opens on how it was run, not on why the question matters. For the lab folder, its order mostly works: the headline comes first, then the planned displacements fall short, then the follow-up fixes that, then the limits. The Cossart section was added later and is the real problem. It sits between the evidence and the limits, but neither the answer nor the decisions ever mention it. On Cossart the displacements the answer recommends leak, and the caveat that weakens Cossart's removal result is left inside its figures rather than in the limits.

## The spine (one claim per section)

0. **Header block:** this is an exploratory look, the dashed thresholds are for reference only, it has not been murderboarded, it covers baseline windows of the lab folder only, and here are the paths.
1. **The answer, short:**
   - Fast stream: rigid shift at 10–20 s is usable, because it hides, keeps counts and removes 84–99 %. The planned 1.6–5 s hides but removes too little.
   - Slow stream: shifts up to about 11 s hide but leave 29 % of large events. From 22 s it leaks, mostly in the DI group, probably from slow drift.
2. **What was measured:** three tests (leak, destruction, count) over 1,501 window pairs per stream from 44 mice, with synthetic twins, retained share and K defined.
3. **Figure 1, leak and count at the planned displacements:** rigid shift reads at chance (0.49–0.52) while dither leaks (0.63–0.77), and counts move 0.14 % at most.
4. **Figure 2, destruction at the planned displacements:** large events survive. At K = 3 with 50 % participation, 1.6 s keeps 0.87 and 5 s keeps 0.41–0.60.
5. **Figure 3, leak at larger displacements:** fast stays at chance out to 40 s. Slow rises to 0.55–0.56 from 22 s, driven by DI.
6. **Figure 4, destruction at larger displacements:** retained share falls steadily with displacement, to 0.04–0.07 at 40 s.
7. **Figures 5 and 6, the Cossart folder, with its "Reading":** rigid shift hides only up to 5 s and leaks from 10 s. From 5 s it removes everything at a scaled K, so the only candidate is near 5 s.
8. **"The K scaling makes removal easy":** Cossart's complete removal is an artefact of K ≥ 55. Small K is not measured, and removal at small K would need exactly the shifts that leak.
9. **What this cannot say:**
   - Removal is a best case, because the synthetic events have tight jitter.
   - A linear classifier is a weak learner.
   - A 10–20 s shift destroys all structure faster than *J*, not only coordination.
   - The same recordings were used, and the follow-up was chosen after seeing the first run.
10. **Decisions for Tony:** is fast at 10–20 s worth training against? On slow, accept about 11 s or look for a slow-specific surrogate?

## The arc I judged it against

I used the default analysis arc: **problem → what it costs → method applied → what the method gets wrong → fix → evidence for the fix → residual risk**. For a note that ends on decisions, I allowed one change: the answer lifted to the front and the decisions at the end. The heading "The answer, short" states that change well enough.

How the spine maps onto that arc:
- **Problem and cost:** missing. The title poses a question but never says why both hiding and removing are required.
- **Method applied:** "What was measured" plus Figure 1, the planned-displacement leak.
- **What the method gets wrong:** Figure 2, the planned-displacement destruction.
- **Fix and its evidence:** Figures 3 and 4, the larger displacements.
- **Second folder:** Figures 5 and 6, Cossart. The arc has no slot for it, and it is not tied back into the answer or the decisions.
- **Residual risk:** "What this cannot say", which is missing the K-scaling limit.
- **Decisions:** present.

Credit where it is due: for the lab folder, the order of the figures tracks the argument. The planned range falls short, which motivates the larger range, which is the fix.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified |
|---|---|---|---|---|---|
| 1 | "The answer, short" (lines 10–22) and "The decision this sets up for Tony" (147–152) versus the Cossart section (93–131) | The Cossart result never reaches the two places a decision-maker reads. The answer still says "fast stream, 10–20 s looks usable". The Cossart section shows that same range leaks (0.58 at 10 s, 0.59 at 20 s, lower bounds 0.53–0.56), and its own Reading says "unlike the lab's fast stream, larger shifts leak". Decision 1 asks whether to train at 10–20 s without mentioning that. The goal page's outcome table counts a result as *viable* only if it holds on **both folders**, so Cossart decides between *viable* and *narrowed*. A reader who reads the answer and the decisions gets a recommendation the body contradicts. | blocking | Add a third paragraph to the answer on the Cossart folder: the window is near 5 s at best, it leaks from 10 s, and removal is shown only at K ≥ 55. Make decision 1 state the conflict: on Cossart, 10–20 s leaks. Add a third decision: does one surrogate have to serve both folders (the *viable* outcome), or can each folder get its own displacement (the *narrowed* outcome)? | yes (README lines 12–16, 107–109, 122, 149–150; goal page lines 51 and 136) |
| 2 | Header block, line 6 | The opening scope line says "Baseline windows of the lab folder only." That stopped being true when the Cossart section was added. Cossart recordings were read whole, with no baseline region (line 96). The first thing the reader is told about scope is contradicted halfway down. | major | Change the scope line to cover both folders: lab baselines, and whole Cossart recordings because that folder declares no baseline region. Also bring "Not murderboarded" up to date after this review. | yes (lines 6, 96–97) |
| 3 | "The K scaling makes removal easy" (lines 126–131), placed after the Cossart "Reading" (121–124) | A limit on a result arrives *after* the result has been read, inside the figures section. The Reading says "it removes large events", and the next paragraph explains that this is so only because K was scaled to 55 or more, with small K unmeasured. Separately, the sentence saying the controls now read 0 and 1 is what licenses reading Figure 6, the Cossart destruction, at all. It appears only after that figure. | major | Split the paragraph. Move the control-validity sentence ("the screen's review found… with K scaled, the controls read 0 and 1") up into the Cossart setup (lines 98–100), before Figure 6. Move the argument that the scaling makes removal easy and small K is unmeasured into "What this cannot say", beside the one-frame-jitter point. Qualify the Reading in the same sentence: "removes large events at K ≥ 55". | yes |
| 4 | "The answer, short" versus the first bullet of "What this cannot say" (135–137) | The headline "removes 84–99 %" is stated four sections before the reader learns that these retained shares are a best case (synthetic events with one frame of jitter, when real fast jitter is about 1 s). The limit bounds the headline but never meets it, so a reader who stops after the answer takes 84–99 % at face value. | major | Put the qualifier in the answer itself: "removes 84–99 % of tightly timed planted coordination, a best case (see What this cannot say)". | yes |
| 5 | Cold open: header block (lines 3–8), then the title question | What the reader sees first is how the run was done: exploratory status, threshold disclaimer, not murderboarded, file paths. The problem never appears: the label-free detector needs a negative class that both hides from a coordination-blind classifier and destroys coordination. A negative that leaks teaches the leak, and one that does not destroy coordination teaches nothing. Also missing is why rigid shift is the candidate (the screen cleared it only up to 1.6 s, dither leaks, joint-ISI leaked) and why the planned range was 1.6–5 s. Tony can rebuild this from memory. A portfolio reader cannot, and without it "hides" and "removes" read as two arbitrary metrics. | major (portfolio reader); minor (Tony) | Open with a two- or three-sentence "Why this look": the goal, the two conditions a negative class must meet, and where rigid shift came from, linking the goal page. Cut the header to one line (exploratory, thresholds drawn for reference). Move the results, code and branch paths to the foot of the note. | yes (goal page lines 20–26, 81, 124–126) |
| 6 | Transition into the larger displacements (line 74) | The stated reason for the follow-up is "the first run showed no leak rising with displacement". That is only half the reason the argument needs. The other half, the one that makes larger shifts a fix, is Figure 2: the planned displacements leave up to 0.87 of large events. As written, the step from what the planned range gets wrong to the fix is not connected. | minor | Give both reasons: "The planned displacements hid but left large events intact (Figure 2, destruction at the planned displacements), and the leak did not rise with displacement (Figure 1), so larger shifts were run the same night." | yes |
| 7 | "The answer, short", slow paragraph (lines 20–22) | The mechanism sentence relies on context the reader has not been given: "the DI group" (the group names DI, MALE, ORX and OVX first appear at line 82) and "the recording-identity run" (never introduced or linked). It arrives before the reader can judge it. This is about order; whether the sentence is readable at all belongs to the You Lost Me reviewer. | minor | Either give the answer only the result ("from 22 s it leaks, mostly in one hormonal group") and move the drift explanation to the Reading under Figure 3, the larger-displacement leak, or link the recording-identity note inline. | yes |
| 8 | "What was measured" (lines 26–45) | The section mixes what a reader needs before the figures with implementation detail that does no job in the argument. Needed: what the leak, destruction and count tests are, retained share, and K. Not needed in that position: dropping edge windows, excluding edge-band features "because the second review showed…", resampling over both mice and slices, the 1.67–98.33 % range, how the twins are built, and the controls. The detail pushes the first figure further from the answer. | minor | Keep one definition sentence each for leak, destruction, count, retained share and K ahead of the figures. Move the rest to a closing "Method details" appendix, together with the provenance paths from the header. | yes |
| 9 | Heading structure: "## Figures" contains "### The Cossart folder" together with its "Reading" and the K-scaling paragraph | Findings and caveats about a second folder sit under a heading that promises only figures, and the sections follow the order the work was done (planned, then follow-up, then "2026-09-15"), not the argument. For the lab folder the two orders happen to agree. For Cossart they do not, which is how its conclusions ended up outside the answer and the decisions. | minor | Organise by folder: a "Lab folder" section (Figures 1–4, with the planned-to-larger step from finding 6) and a "Cossart folder" section (setup and control validity, Figures 5–6, Reading), both before "What this cannot say". | yes |
| 10 | "The decision this sets up for Tony" | The decisions do not say what either answer unlocks: training, reopening the pre-registration, or Tony's still-pending choice between writing the rule as tested code and stopping the goal (goal page line 42). Without that, the arc stops at a question rather than at what happens next. | minor | Add one clause per decision on what it releases, for example "yes: train against rigid shift at J on fast; no: the fast stream has no viable surrogate candidate left". | yes (goal page line 42) |

## Proposed order

1. **Why this look:** the problem and the two conditions a negative class must meet.
2. **The answer:** lab fast stream, lab slow stream and Cossart, with the best-case qualifier.
3. **What was measured:** definitions only.
4. **Lab folder:** Figures 1–2, then the step to larger shifts, then Figures 3–4.
5. **Cossart folder:** setup and control validity, then Figures 5–6, then the Reading.
6. **What this cannot say:** adds the K-scaling limit and the whole-recording scope.
7. **Decisions:** fast (with Cossart's leak at 10 s), slow, and whether one surrogate must serve both folders.
8. **Appendix:** method details and provenance paths.
