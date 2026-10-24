GRANT 11 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), plus Bash, PowerShell, Agent, Artifact, Skill, ToolSearch and MCP write tools (Claude Docs, Dropbox, Gmail). I was spawned as general-purpose through the inline fallback, so the run record's `roles:` line has to say this review took a fallback path. I used only Read and Grep, and edited nothing.

**What I read:** `_scratch/r2_common.txt`, `_scratch/r2_extract.md` (in full), the page `docs/goals/synthetic-validation.md` (lines 1–16 and 240–364 for context), the goal-page order in `docs/goals/README.md:117-119`, the section headings of the sibling pages `unsupervised-learning.md` and `coded-detector-optimization.md`, and the two new GLOSSARY blocks (GLOSSARY.md:473-476 and 656-672). I opened nothing under the blindness list.

## Spine (one claim per section or block)
1. **Goal (l.1–14):** validate the toolset on synthetic data with two or more sources, condition by condition.
2. **Where it stands, bullet 1:** Aim 1a showed that a fixed K does not transfer across backgrounds and that the assessor cannot measure jitter. It was reseeded.
3. **Where it stands, bullet 2:** the tool's output can be predicted from the planted parameters, and a fit across windows recovers jitter for k ≥ 10. Two sessions agree, and membership and order have closed forms.
4. **Where it stands, bullet 3:** a murderboard found overclaims and two analysis faults, and both faults are fixed.
5. **Symbols:** notation and the two tools (definitions; the heading says they are "used below").
6. **Aim 1a, Figure 1 and caption:** recovery against planted jitter across 240 recordings. The caption already shows Aim 0's joint fit in violet.
7. **⚠ shared seeds:** the first run's conditions shared five background draws, "found by both blind passes below".
8. **Aim 1a bullets:** the share moves least; participants need a window wider than the jitter; a fixed K fails across backgrounds; the assessor reads about 0.7 s whatever is planted, "Aim 0's joint fit does measure it".
9. **Aim 0 opening:** Tony asked whether an analytical prediction could replace brute force; for this generator, mostly yes.
10. **What it rests on:** a Neyman–Scott process, CuBIC cumulants and Grün's fission probability. What is added: g_n, the at-most-one-event term, and the fit across windows.
11. **Figure 2:** predicted against measured, with and without the at-most-one-event term.
12. **Prediction bullets:** participants within noise; rate and share less well; 5-cell events at 0.05 Hz not predicted; joint fit recovers σ ("blind pass A's route"); chance clusters predicted.
13. **Blind sessions:** one answer reached three ways, but only a consistency check. The table holds k̂ = 2 + (k−2) g3/g2 and 60 q(1−q)².
14. **What only the blind passes found:** the seed flaw, estimator noise, the event floor (6 cells at 0.01 Hz, 12 at 0.05 Hz), detector recall, the joint fit.
15. **Open residuals:** the triple count low and the rate high, possibly from surrogate correlation.
16. **Membership and order opening:** both converge to the exchangeable limit, and population-count tools are blind to both.
17. **Figure 3 and membership:** the ratio is 1 + (E−1)/M, assuming perfect readout.
18. **Figure 4 and order:** F = (2/π) arctan τ under one template, and the signal falls as 1/√M.
19. **Against Kreuz:** not yet compared. The no-order constant is fitted, the August link is untested, and the fast sort has prior art.
20. **What it changes for the generator:** a source should carry k, σ, a membership rule and a template, as in PP-Seq.
21. **Tried and dropped:** four dropped approaches.
22. **Plan, Aim 0 items 1–7:** stated rule, "validation owed by results already stated first, then derivations".

**Arcs used:**
- **Page level:** the README arc: goal → where it stands → settled → tried and dropped → waiting on Tony → open work → where the work lives → how the page stays true.
- **Aim 0 body:** the default arc: problem → cost → method → what the method gets wrong → fix → evidence → residual risk.

**Cold open:** the reader first sees the goal paragraph, then a dated log whose first bullet does state the problem (K does not transfer; jitter cannot be measured). Within the results, Aim 1a (the problem) comes before Aim 0 (the method), which is the right order.

## Findings
*location · issue · severity · suggested fix · verifiable against a source*

1. **Page structure: "Tried and dropped" (l.230) is an H3 inside "Where it stands", placed before "## Settled" (l.242).**
   - Issue: README:117-119 puts settled before tried-and-dropped, as top-level sections. Both siblings follow that order, and this deviation is not stated.
   - Severity: medium.
   - Fix: promote it to `## Tried and dropped` and move it after Settled.
   - Verifiable: yes (README:117-119; sibling headings).
2. **Page structure: the page has no "how the page stays true" section and ends at "Where the work lives" (l.358-364).**
   - Issue: the README arc requires it, and both siblings have "## Keeping this page true".
   - Severity: medium.
   - Fix: add the section at the end.
   - Verifiable: yes.
3. **Page structure: "## Settled" (l.242-252) holds only Tony's decisions.**
   - Issue: every measured or derived result sits under "Where it stands" with its strength in the H3 heading. Examples: "fixed K does not transfer"; "participants predicted to within noise"; 1 + (E−1)/M; F = (2/π) arctan τ. The README defines Settled as "what is settled, with strength and source". A session that reads Settled first finds no results.
   - Severity: medium.
   - Fix: add Settled rows for the load-bearing results, each with its strength (measured, derived and checked, consistency-checked) and a link to the section, or say in Settled that results are kept above.
   - Verifiable: yes (README).
4. **Figure 1 caption (l.45) and the last Aim 1a bullet (l.63): the fix arrives before its method.**
   - Issue: Figure 1 plots the "joint fit (violet, Aim 0)", and the bullet says the joint fit "does measure it". The fit is not defined until the fourth prediction bullet, about 40 lines later. The reader cannot judge the violet points where they first appear.
   - Severity: medium.
   - Fix: either drop the violet series from Figure 1 and show the joint fit's recovery next to its bullet in Aim 0, or add a one-clause definition and an explicit forward pointer ("fitted across the three windows; see Aim 0 below").
   - Verifiable: yes.
5. **Aim 0 predictions, "What it rests on" to Figure 2 (l.72-86): the mechanism is buried in the blind-sessions table (l.127-129).**
   - Issue: two formulas the predictions depend on appear only in that table, after the results built on them:
     - k̂ = 2 + (k − 2) g3/g2, "the window must exceed the jitter". This explains Aim 1a's "participants need a window wider than the jitter".
     - 60 q(1−q)² per min. The chance-cluster bullet (l.105) cites only "the binomial tail".
   - Severity: medium.
   - Fix: give the core prediction in one or two lines right after "What it rests on" and before Figure 2. The table then confirms it rather than introducing it.
   - Verifiable: yes.
6. **Prediction bullets (l.90-104): results are credited to the blind passes before the blind passes are introduced (l.111).**
   - Issue: "blind pass B named it a hard-core bias" and the joint fit as "blind pass A's route" both come before the section that introduces the passes. The joint fit, which Where it stands bullet 2 makes the headline, is fourth of five bullets, after "Not predicted".
   - Severity: low-medium.
   - Fix: put the joint-fit bullet right after the participants bullet, since it answers Aim 1a's sharpest failure. Either move "checked by two more sessions" ahead of the predictions or add one line at the top of Aim 0 introducing the two blind sessions.
   - Verifiable: yes.
7. **"What only the blind passes found" (l.135-140): the event floor arrives after the claims that need it.**
   - Issue: the floor is 6 cells at 0.01 Hz and 12 at 0.05 Hz, so 5- and 10-cell events cannot pass it at 0.05 Hz. Two earlier claims are what this explains:
     - Aim 1a's "K = 6 misses most 5-cell events" and "the case for setting K per recording" (l.58-60).
     - "Not predicted: 5-cell events at 0.05 Hz" (l.96).

     Here it reads as an aside in a list of credits.
   - Severity: low-medium.
   - Fix: state the floor where Aim 1a makes the K argument, and keep the attribution here.
   - Verifiable: yes.
8. **Figure 4 caption (l.173-176): the caption comes before its definitions.**
   - Issue: the caption uses "order indicator", "signal term", "no-order bias" and "1/√n̄, constant for each way of choosing the order", but F and the score sort are defined only in the paragraph after it (l.178-182). Figure 3 avoids this because its caption defines its own statistic.
   - Severity: low.
   - Fix: put a one-line definition of F in the caption, or put the "Order" paragraph before the figure.
   - Verifiable: yes.
9. **Plan, item 6 (l.304-306): the plan breaks its own stated order.**
   - Issue: the rule (l.288) is that validation owed by results already stated comes first. Item 6 checks the two-source non-separability already stated as a result in the blind table (l.130), yet it sits after the new derivations in items 4 and 5.
   - Severity: low.
   - Fix: move item 6, or at least its two-source half, ahead of item 4, or state why it waits.
   - Verifiable: yes.
10. **Aim 1a placed before Aim 0 (l.36 against l.65): the order is right but unstated.**
    - Issue: the plan lists Aim 0 first, while the results run 1a then 0. Bullet 2 of Where it stands implies the reason (Aim 0 was added later), but the body never says that Aim 1a comes first because its failures are what Aim 0 answers.
    - Severity: low.
    - Fix: add one clause at the head of Aim 0 linking it to Aim 1a's two failures.
    - Verifiable: yes.
11. **Where it stands, bullet 3 (l.13-18): this bullet is about process, not results.**
    - Issue: it is a review history in the page's opening log. It can stay, because it records that numbers were recomputed.
    - Severity: low, advisory.
    - Fix: none required. Optionally fold it into one clause of bullet 2.
    - Verifiable: yes.

**Checked with no finding:**
- **Symbols block before the results:** a definitions-first block, but its heading announces it, and Figure 1 needs K and σ.
- **⚠ seed warning before the Aim 1a bullets:** the caveat correctly comes before the numbers it qualifies.
- **Membership and order:** opens claim-first.
- **Kreuz subsection:** residual risk correctly follows the evidence.
- **"What it changes for the generator":** correctly closes the section.
- **"Tried and dropped" items:** each follows the result that replaced it.
- **GLOSSARY blocks:** reference lists with no argument order to judge. The vocabulary block is appended at the end of the file. That fits the glossary's sectioned layout, and it is not an argument-order matter.
