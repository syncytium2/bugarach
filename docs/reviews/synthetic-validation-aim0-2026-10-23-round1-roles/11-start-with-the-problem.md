GRANT 11 MISMATCH — missing none; holds forbidden tools: Edit, Write, NotebookEdit (plus Bash, PowerShell, Agent, Artifact, Skill, MCP tools). I was spawned through the general-purpose fallback. I used only Read and Grep and changed no files. Note this in the run record's `roles:` line as a fallback path.

**Arcs used.** (1) The stated arc for a goal page in `docs/goals/README.md:117-119`: goal → where it stands → settled → tried and dropped → waiting on Tony → open work → where the work lives → how the page stays true. (2) My default arc, applied to the Aim 0 block: problem → cost → method → what it gets wrong → fix → evidence → residual risk.

## Spine (one claim per section, in page order)

1. **Goal paragraph (L7-14).** Test the measure → simulate → tune → characterise loop on synthetic data with two or more sources, against known truth.
2. **Where it stands (L16-23).** Aim 1a ran (one source, 240 recordings). Aim 0 later predicted it from the planted parameters and gave a jitter estimate that works.
3. **Aim 0, first result (L25-53).** For this generator, the excess cumulants of the coordination-rates tool are exact closed forms. They predict participants, jitter (from how the pair count changes with window) and the chance-cluster rate. After reseeding they match within about 0.01-0.02.
4. **Aim 0, replicated blind (L55-104).** Two blind agents reached the same cumulant answer, so it is "not the only solution, but one answer reached three ways". They also found a seed-sharing flaw in Aim 1a (now fixed), plus a noise model, the closed-form floor and a better joint fit.
5. **Aim 0, membership and order (L106-162).** Membership excess decays as 1 + (E−1)/M. The order indicator has closed forms, including a null bias of 0.375/√n̄ that explains the August spike-count anticorrelation. A score sort replaces annealing. So the generator needs a membership rule and a latency template.
6. **Aim 1a, first result (L164-188).** By brute force: the coordinated share is robust, participants are recovered within about 30 %, K must rise with the background, and jitter is the weak parameter. This section is flagged as rerun after the seed fix.
7. **Settled (L190-200).** Seven decisions by Tony or the ADRs.
8. **What the tree has (L202-230).** The generator plants one source with random membership. It has no assembly mode, no order and no shared slow comodulation. Several tools are folder-bound, and the negatives tool is unbuilt.
9. **The plan, Aim 0 bullet (L234-254).** Predict first, simulate to check. A list of next steps follows "in order".
10. **Aims 1-3, Waiting, Open work, Not here, Where the work lives.**

**Cold open.** The page opens on the goal paragraph, which is mandated and fine, then on dated status bullets. The first result the reader meets is Aim 0, the prediction, not the problem it answers. The problem is that brute force left jitter as the weak parameter and the first run had correlated errors. That problem appears only in section 6, after all three Aim 0 sections.

## Findings

Each finding gives location · issue · severity · suggested fix · whether I could verify it against a source.

1. **Aim 0 sections (L25-162) come before Aim 1a (L164-188), which they predict and are scored against.**
   - Issue: Section 3 says "it predicts Aim 1a", "Figure 1 now carries the predictions" and "turns jitter from Aim 1a's weakest parameter into one of its best". Section 4 says "the 0.05 Hz rows now sit on the prediction". None of this can be judged until the reader has seen what Aim 1a measured and what Figure 1 is, and those arrive afterwards. The fix is shown before the problem, which is the core "start with the problem" failure. It is also anti-chronological, an unstated deviation (Aim 1a ran first; Where it stands L18-23 says so). It comes from appending new sections at the top in conversation order.
   - Severity: **high**.
   - Fix: move "Aim 1a, first result" in front of the three Aim 0 sections. Aim 1a then states the problem and its cost (brute force; jitter unusable; K does not transfer), and Aim 0 follows as the method, fix and evidence.
   - Verifiable: yes, from L18-23, L42, L50, L78, L164-188.

2. **The result sections that fix Aim 1a's numbers are reached only through forward references.**
   - Issue: L51 says "After the reseeding below". L166 says "Rerun … (see *Aim 0, replicated blind*)". The seed flaw that invalidated Aim 1a's first run is bullet 1 of "What only the blind passes found" (L74-78), below a six-row agreement table. The most consequential correction on the page sits in the middle of the third section, and two other sections point forward to it.
   - Severity: **high**.
   - Fix: state the seed flaw and the rerun at the top of the Aim 1a section, as a correction it owns (with the "found by blind pass" attribution). Have Aim 0 cite the rerun numbers, not "the reseeding below".
   - Verifiable: yes, L51, L74-78, L166-168.

3. **"Aim 0, first result" (L25-53): the pre-fix claim is listed first and the post-fix correction appended after it.**
   - Issue: Bullet L36-37 says "within about 0.03 in every cell". The appended paragraph L50-53 gives median 0.011, worst 0.06, and at 0.05 Hz only for events of 10 or more cells. The current number arrives last, after one it partly supersedes (worst 0.06 is above "about 0.03 in every cell"). Whether the numbers conflict belongs to Reviewer 2. That the newer state sits below the older one is an order defect.
   - Severity: medium.
   - Fix: put the rerun figures in the bullet and drop the appended paragraph, or fold it in.
   - Verifiable: yes, L36-37 against L50-53.

4. **"Aim 0, replicated blind" (L55-104): the answer to Tony's question comes last.**
   - Issue: He asked "to see if this is the only solution". The verdict, "not the only solution, but one answer reached three ways", is at L101, after the table, the new findings and the disagreements.
   - Severity: medium.
   - Fix: open the section with the L101-104 verdict (just after the quoted question), then the agreement table as evidence, then the new findings, then the open residuals as residual risk.
   - Verifiable: yes, L57-58 and L101.

5. **"Aim 0, membership and order" (L106-162) answers two questions, and the second answer is split.**
   - Issue: The section opens on "It does", answering the convergence question. It then quotes a second question, the Kreuz synfire comparison. That answer is split between the "two changes from the published method" sentence inside **Order** (L132-135) and the "Against the brute force" paragraph (L151-156). Its residual risk (⚠ not compared with PySpike) is buried in that last paragraph. Its conclusion, "What it changes for the generator", refers to Aim 1b/1c, which are defined only in the plan (L259-262).
   - Severity: medium.
   - Fix: split the section by question, or put the brute-force comparison in one place right after **Order**. Lift the PySpike caveat next to the table whose constants it qualifies (L137-141).
   - Verifiable: yes.

6. **Terms are used before they are defined.**
   - Issue: The Aim 0 sections use terms that "What the tree has" (L202-230) and "The plan" (L234, L256-265) define later: "Aim 0" itself (its definition, "predict first, simulate to check", is at L234), "the assessment", "the coordination-rates tool", "the chance floor", "Aim 1b and 1c", and "the generator plants no order" (the generator survey is at L204). Agent 8 owns legibility. My point is position: the reference material comes after the claims that depend on it.
   - Severity: medium.
   - Fix: either move "What the tree has" and a one-line definition of each Aim above the results, or give each Aim 0 section a one-clause gloss at first use.
   - Verifiable: yes.

7. **The page as a whole departs from the README's arc without saying so.**
   - Issue: The README order has no slots for results, "What the tree has", "The plan" or "Not here", and has slots the page lacks: "what was tried and dropped" and "how the page stays true". Four result subsections, about 165 lines, are nested under "Where it stands", which makes "where it stands" the bulk of the page. The page also has a "tried and dropped" story it does not tell in that slot: the Poisson treatment (5-15 % residual), the shared-seed design, and the one-parameter jitter fit superseded by blind A's joint fit ("Adopt it", L92).
   - Severity: medium. It is a page-level deviation, and the Aim 0 additions deepen it.
   - Fix: either state the deviation (for example, a line saying results sit under Where it stands until moved to `learned/`), or move the derivation-level detail to `learned/synthetic_validation/` and keep a short headline per Aim here. Add a "Tried and dropped" section with those three items.
   - Verifiable: yes, README L117-119 against the page headings.

8. **"Where it stands" bullets (L18-23) do not carry the replication's headline.**
   - Issue: The second bullet summarises only section 3. It does not mention the blind replication, the seed flaw that forced a rerun of Aim 1a, or the membership and order results. A reader who stops at the summary misses that Aim 1a's first numbers were superseded.
   - Severity: medium.
   - Fix: add a bullet saying the blind replication agreed, found the seed flaw and forced the Aim 1a rerun, and add one for membership and order.
   - Verifiable: yes.

9. **The Aim 0 plan bullet (L234-254) orders "Next, in order" without a rationale, and repeats finished work.**
   - Issue: The PySpike comparison is second (L240), yet it gates whether the order claims of section 5 stand (L154-156). It reads like validation owed before the order result is built on, and should go before the new random-matrix threshold work, which includes "its counterpart for order". Two items present as future results that section 4 already marks as "stated" or derived: the two-sources item (L245-247) and the shared-slow-rate item (L248-249). The count/SCE recall item (L250-252) repeats what blind B already derived (L88-89).
   - Severity: low to medium.
   - Fix: state the ordering rule, and put the PySpike check first. Reword the derived items as "check by simulation", or move them to the result.
   - Verifiable: yes.

10. **Do the slots earn their positions?** Every Aim 0 section has a job: method and fix, evidence and correction, extension to Aims 1b/1c. None belongs in an appendix. The derivation detail inside them (Charlier polynomials, the arcsin formula, the ±1.5 s truncation SD) is appendix-grade for a goal page, but that is density (agent 9) more than order. **No finding beyond #7.**

**Suggested order for the Aim 0 block:** Aim 1a result, with the seed-flaw correction at its head → Aim 0 first result (rerun numbers only) → replicated blind (verdict first) → membership and order → plan. This also restores the chronological order, which the current page reverses.
