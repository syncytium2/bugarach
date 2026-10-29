GRANT 11 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred, loadable via ToolSearch), Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch/update (doc-writing tools), plus Read, Grep, Glob

*Run finding: this role was spawned through a fallback path that handed it editing and shell tools beyond its `Read, Grep, Glob` grant. I used only Read, on the role file, the context file and the artifact, and changed nothing. The run record's `roles:` line should say that the review took a fallback path.*

# Role 11 — Argument order ("Start With the Problem"), Chapter 1 (Aim 0)

Artifact: `<worktree>/docs/dissertation/chapter-1-aim0.md` (read in full, 701 lines).

## The arc I judged against, and why

The role's default arc is: problem → cost → method applied → what the method gets wrong → fix → evidence for the fix → residual risk. A dissertation chapter also has its own conventional sections: Introduction, Background, Methods, Results, Discussion, Conclusion. I accept that skeleton. Having a Background section before the work, and a Discussion and Conclusion after it, is a deviation from my default arc that the genre justifies. Inside the skeleton I map the default arc onto this chapter's own story:

- **problem**: finding which onsets belong to which coordinated event, when several sources are mixed in one recording;
- **cost**: validating detectors by brute-force simulation grids;
- **method applied**: the first brute-force experiment (Aim 1a);
- **what it gets wrong**: the two failures it found but could not explain;
- **fix**: closed-form predictions, with simulation used to check them;
- **evidence**: the residuals from those checks;
- **residual risk**: the lab's regime, two sources and human review.

I judge the order against this mapping. The chapter's own Discussion (1.10, "turns two failures that simulation found but could not explain into consequences of a formula") states this same arc. The body just does not present it in this order.

## Spine (one claim per section, in the chapter's order)

0. *(Blockquote above 1.1)* This is an exercise; every number comes from the records; no human has reviewed the work and the two-source test has not been run.
1. **1.1 Introduction:**
   - A calcium recording is a multichannel stream of event times, and the key question is which onsets form which coordinated event.
   - KNDy events are action-potential independent, so point-process statistics transfer and spike-train priors do not; the lab's parameters are b ≈ 0.0096 Hz, σ ≈ 0.1 s, k ≈ 7–13 of 33.
   - Validating by brute-force simulation is costly and answers only the conditions in its grid.
   - The question: can theory predict what each tool returns, with simulation used only to check?
   - The answer: theory aims simulation rather than replacing it.
   - The contributions list (seven formulas), followed by a summary of what is old and what is new.
2. **1.2.1:** The data are onset lists, and the generative model is a Neyman–Scott/Thomas process with a fixed event count and 20 s hard-core spacing.
3. **1.2.2:** Three population-count tools are analyzed (the coordination-rates tool, the assessor, the count detector), plus two which-cell statistics.
4. **1.2.3:** Prior work covers jitter across bin widths (uniform jitter only), minimum contrast on cluster processes, PCA assemblies, and the Synfire Indicator.
5. **1.3:** The coordination-rates tool's output follows from g_n(w, σ) and the at-most-one-event term; k̂ = 2 + (k − 2)g₃/g₂ explains why the window must exceed the jitter; there is a general event-train form; a joint fit across three windows recovers σ, k and λ.
6. **1.4:** The assessor's chance-cluster rate is 60q(1 − q)² per minute, which gives the smallest threshold safe against chance.
7. **1.5.1–1.5.2:** The testbed (48 conditions × 5 recordings, rerun after the shared-background bug) and the residual protocol.
8. **1.5.3:** Brute force alone found two failures: a fixed threshold drowns in chance clusters at 0.05 Hz (7.97 per minute against ≤ 1 planted), and the assessor's jitter reading is flat at 0.05 Hz.
9. **1.5.4:** Theory matches simulation (participants within about 0.01; chance clusters inside their 95 % intervals), explains both failures, and the joint fit reads jitter where the assessor cannot; the general form repairs the real-gap failure.
10. **1.6.1:** Assembly variance excess is 1 + (E − 1)/M, so assemblies converge to random only at fixed E, and detection outlasts the variance.
11. **1.6.2:** The order indicator has closed forms for one template, for M templates and for no order; at baseline event counts an order indicator can find one template at best; the lab's Synfire trend is consistent with bias but not tested.
12. **1.7:** The data's separation floor is 0.26–0.76 s, the tools' floor is about 2.5 and 5 s, set by bin width, and on real gaps the cost of the difference is small.
13. **1.8:** The derivations were checked by simulation (the main evidence), by two Claude rederivations (consistency only) and by Claude adversarial review; no human has reviewed them.
14. **1.9:** A table of what is old and what is new.
15. **1.10 Discussion:**
   - Theory predicts the population-count tools and explains the failures; it does not cover detection at a threshold or the rolling detectors.
   - The lab sits at the edge of the tested regime.
   - **The dissertation's premise is that two or more sources are mixed in one recording**, and pair and triple counts cannot separate them.
   - Limitations and next steps.
16. **1.11 Conclusion:** Closed forms predict, explain and estimate; at the lab's scale order is limited to one template; the tools set the separation limit; prior work sharpened the claims.

## Cold open

The reader first sees a blockquote about process and provenance that ends on what is still open: "no human has reviewed the derivations, and the two-source test has not been run". Next comes a definition of the data ("A calcium-imaging recording … is a multichannel stream"). The domain question appears in the fourth sentence. The chapter's actual problem, that brute force is costly and blind, comes in paragraph 3, and only as an assertion. The one piece of the chapter that shows what the problem looks like is §1.5.3, "What brute force found", with Figure 1.1: chance clusters at 7.97 per minute against 0.33–1 planted events, and the flat jitter readout in panel H. It sits at line 292 of 701, after both derivation sections. This is the incident pattern almost exactly: the problem is shown midway through, after the fix.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source |
|---|---|---|---|---|---|
| 1 | §1.5.3 "What brute force found" (line 290 onward, Fig 1.1), against §1.3–1.4 | **The fix comes before the problem.** The derivations in 1.3–1.4 are built to explain two failures the reader does not see until 1.5.3. Examples: 1.4's "smallest threshold that is safe against chance" answers a threshold failure not yet shown; 1.3.3's "window must be wider than the jitter" explains the "1 s window read 0.34–0.42" regularity in 1.5.3; 1.3.5's joint fit answers the assessor's flat jitter (1.5.3, Fig 1.1 H). The intro says theory "explains the two failures of the first simulation experiment" (line 47) without saying what they were. | blocking | Move the two failures, and the panels of Fig 1.1 that show them (chance clusters against background; panel H's flat jitter), into §1.1 as the motivating observation, right after "That plan is brute force". Keep the testbed details in Methods. If the full Fig 1.1 moves, drop its joint-fit trace or show it in a later version, because the caption's "introduced in 1.3.5" would then point forward. | yes (artifact lines 37–51, 251–265, 290–313) |
| 2 | §1.10 "Two sources", line 580: "The dissertation's premise is that two or more sources are mixed in one recording." | **The dissertation-level premise arrives in the Discussion.** §1.1 frames the problem as assigning onsets to events and validating detectors, never as mixed sources. Yet "for one source" already scopes the answer at line 43, "Limitation 1: one generator" depends on it, and the closing line hands Chapter 2 the two-source question. A committee member cannot judge whether a one-source chapter is the right first step without knowing the dissertation is about several sources. | blocking | State the multi-source premise in the first paragraph of §1.1, define "source" there, and say explicitly that Aim 0 handles one source on purpose, as a baseline. Then §1.10 "Two sources" becomes a payoff rather than a reveal. | yes (lines 15–35, 43, 580–588) |
| 3 | Blockquote above §1.1 ("An exercise, not a submission…") | **The cold open is provenance and limitations, not the problem.** The first thing read is how the chapter was made and what is still unreviewed. That information is legitimate, but it is front matter, and it asks the reader to hold caveats before knowing what they qualify. It also repeats §1.8 and Limitation 4. | major | Move it to an unnumbered preface or a footnote on the title. Let §1.1's first paragraph carry the problem: the mixed sources (finding 2) and the brute-force failures (finding 1). | yes (lines 3–11, 503–526, 598–602) |
| 4 | §1.1 "Contributions" (lines 55–74) and the old/new paragraph (lines 76–81) | **Claims arrive before they can be evaluated.** The list uses g_n(w, σ), k̂, "at-most-one-event term", K, M, E, c/√n̄, Kish's deft, Kruskal's τ and Durbin's covariance. All are defined only in §1.2–1.6, and Table 1.1 comes after the list. The earliest position at which these items are intelligible is after §1.2.2 (for 1–4) and after §1.6 (for 5–6). The old/new paragraph also repeats §1.9 ahead of the definitions it relies on. | major | Keep a contributions list in §1.1, as the genre expects, but write each item in plain words with no formulas (for example, "a closed form for how often one event's onsets share a window when jitter is Gaussian"). Move the formulas and the precedent comparisons to §1.9. | yes (lines 53–81, 102–118) |
| 5 | §1.3–1.5 against §1.6–1.7 | **Unstated change of arc.** For the population-count tools, the chapter puts all predictions first (1.3, 1.4), then a testbed (1.5.1–2), then all tests (1.5.4). For membership, order and separation (1.6, 1.7), each subsection derives and checks in the same place. The reader has to switch modes without being told. The split arrangement is also what separates each prediction from its evidence by about 100 lines: 1.3.4's event-train form gets its evidence in 1.5.4's sign test and "On real gaps". | major | Pick one arrangement and say which. Recommended: put the testbed and protocol (now 1.5.1–1.5.2) right after Background as Methods. Then give each tool its own predict-then-check unit: coordination-rates tool (1.3 + 1.5.4 participants, joint fit, rate and share, real gaps); assessor (1.4 + chance clusters). Membership, order and separation already follow that pattern. | yes (lines 176–357, 359–501) |
| 6 | §1.3.4 "Any stationary event train" | **A sub-fix comes before its sub-problem.** The general event-train form is introduced before the reader sees the hard-core form fail: the sign-test bias (p = 0.08) and the real-gap failure at the 4 s window, both in §1.5.4. As written, 1.3.4 is motivated by one statistic (1.7 % of gaps under 3 s) with no consequence attached. | minor (resolved by finding 5) | In the per-tool unit: hard-core prediction, then its test, then where it fails (sign test, real gaps), then the general form, then its test. | yes (lines 227–236, 325–332, 354–357) |
| 7 | §1.6.2 "The question" (line 401) against Table 1.2 and line 457 | **The opening question is not the one the subsection answers.** It opens on the lab's Synfire trend ("Is that order in the data or a property of the indicator?"). It closes by saying that question is "consistent with … but not tested". The answer it does deliver, that power at baseline event counts allows one template at best, answers a question never posed at the top. | major | Open with the question the section answers: how many events does an order indicator need, and how biased is it at few events? Use the Synfire trend as the motivating example of why bias matters. Move the four-way Kreuz comparison, which is a scope and positioning item, after Table 1.2 or into §1.9. | yes (lines 399–466) |
| 8 | §1.7 opening ("How close can two coordinated events be…") | **The problem is not motivated before the answer.** Why separation matters only appears in the third bullet (the lab's gaps; the count detector merges about 7 % of fast-stream gaps). §1.1's framing question ("what it should return") does not motivate a separation floor at all. | minor | Open §1.7 with the cost: the real fast-stream gap distribution (already partly given in 1.3.4) and the risk that tools merge real event pairs, and say why this matters for counting events. Then give the floors. Also tie it into §1.1's question. | yes (lines 468–487, 229–230) |
| 9 | §1.7 figure order | The bullets give the data's floor first and the tools' floor second, but Figure 1.5 (tools) comes before Figure 1.6 (data floor). The evidence order runs against the claim order. | minor | Swap the figures, or reorder the bullets. | yes (lines 474–501) |
| 10 | §1.9 "What is old and what is new", between §1.8 and §1.10 | **Positioning against prior work is split across five places:** §1.1 lines 76–81, §1.2.3, inline in 1.3.1, 1.3.5 and 1.6.2, then §1.9. §1.9 sits as a standalone section that breaks the move from Results to Discussion. Each novelty claim is evaluated before the result (in the intro) and again after it (1.9), but not where the result is presented. | major | Make §1.9 the single place where novelty is judged, positioned as the first part of the Discussion. Cut the §1.1 paragraph at lines 76–81 to one sentence that points to it. Keep §1.2.3 as background on what exists, with no verdicts. | yes (lines 76–81, 141–174, 528–548) |
| 11 | §1.8 "Checking the derivations" | **Placement and job.** The simulation check is the protocol already given in 1.5.2. The rederivation and agent-review checks are about process and validity, and are repeated in the opening blockquote and in Limitation 4. Placed after the separation results, the section reads as a Methods statement left at the end. | minor | Fold the simulation sentence into Methods (1.5.2), and the rederivation and adversarial-review paragraphs into a "Validity of the derivations" subsection of Limitations. Remove the blockquote copy (finding 3). | yes (lines 503–526, 598–602) |
| 12 | §1.2.3 "Order", Mariani et al. timing (9.7 s against 861.8 s) | No job in the spine. No claim later in the chapter depends on sorting speed. The score sort's "O(N²), no search" in 1.6.2 does not cite it. | minor | Either connect it explicitly to the score sort's claim of no search in 1.6.2, or cut it. | yes (lines 173–174, 411–413) |
| 13 | §1.11 Conclusion, "Reading the prior work sharpened the claims…" | Process narrative in the conclusion. It tells how the claims were reached, not what the chapter established, and it delays the handoff to Chapter 2. | minor | Replace it with the substantive point: the full count distribution is where two-source separation should start. Drop "reading … sharpened". | yes (lines 643–647) |

## Proposed order (one possible repair, for the main thread to adjudicate)

1. **Introduction:**
   - the problem (mixed sources; which onsets belong to which event);
   - the standard plan (brute force) and its cost;
   - **what brute force got wrong**: the two failures, with their Fig 1.1 panels;
   - the question (Aim 0: predict first, simulate to check), with one source taken on purpose as the baseline;
   - the answer in plain words, and the contributions in plain words.
2. **Background:** model, tools, prior work (descriptive only).
3. **Methods:** testbed and protocol (now 1.5.1–1.5.2).
4. **Coordination-rates tool:** predicted, tested, where the hard-core form fails, general form, joint fit.
5. **Assessor threshold:** predicted, tested, which explains failure 1.
6. **Membership; order:** order retargeted to the question it answers.
7. **Separation:** cost first.
8. **Discussion:**
   - old/new verdicts (now 1.9);
   - what theory replaces;
   - the lab's regime;
   - two sources;
   - limitations (absorbing 1.8 and the blockquote);
   - next steps.
9. **Conclusion.**

## What I would need before signing off

Findings 1 and 2: the chapter must open on the problem it solves, which is the brute-force failures, inside the multi-source premise of the dissertation, and not show that problem halfway through after the derivations that answer it. Findings 4, 5, 7 and 10 are needed for the case to be judgeable in sequence. The rest are polish.

Scope note: I read only the order. I did not check whether the claims are true, whether the numbers are consistent, or whether the figures are well made; other roles cover those. "Verified against source" in the table means I confirmed the location and the quoted text in the artifact. The order judgments themselves are judgments, and no source can verify them.

---
*Archivist's note (main thread, 2026-10-29): for this public repository (sapper SAP004), the review worktree's absolute path became `<worktree>/`. Nothing else in the report was changed by this pass.*
