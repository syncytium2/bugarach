GRANT 11 MISMATCH — missing none; holds Edit, Write, Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch/update/guide

This is a finding about the run, not about the artifact. The harness gave this reviewer editing and execution tools that role 11 is not granted. I used only Read (on the artifact and on two figure PNGs). I edited, wrote and ran nothing, and I did not open docs/reviews/. The run record's `roles:` line should say this review took a fallback path.

# Role 11: Argument order ("Start With the Problem")

Artifact: <repo>/docs/dissertation/chapter-1-aim0.md (blob 0acfccbb), read in full, 1745 lines. Figures 1.1 and 1.2 were opened as images to check the cold open. The rest were judged only from their captions and where they sit, because placement is what this role reviews.

## 1. The spine (one claim per section)

0. Front matter (L3–6): an AI wrote this chapter as an exercise, no human has reviewed the derivations, and ⚠ marks sources that were not read.
1. 1.1 "The problem" (L10–17): a recording reduced to onset times mixes coordinated onsets with background, and all later analysis depends on telling them apart.
2. 1.1 definitions (L19–26): recording, frame, calcium event, onset and channel mean specific things here; nothing else about the cells is used.
3. Figure 1.1 (L28): the analyst receives panel C, where coordination is not visible by eye and no onset is labeled.
4. Cost (L40–45): getting the counts wrong plants errors into Chapter 2's simulations and Chapter 4's comparisons (example: the assessor reports about 0.7 s as jitter).
5. Premise (L47–54): recordings mix two or more sources, each with its own participation, jitter, timing and membership; the goal is to measure these properties, simulate from them and test detectors.
6. Dissertation map (L56–63): the four chapters and what each does.
7. Scope (L65–66): this chapter takes one source on purpose.
8. Roadmap (L68–84): detectors, then tools, then the question, then the answers.
9. 1.2 / 1.2.1–1.2.2: fixed bins fail at bin borders; a sliding window removes borders but calls more chance groupings.
10. 1.2.3: the right threshold depends on the background (chance floor of 6 cells at 0.0096 Hz, 12 at 0.05 Hz); CFAR follows the background, at the cost of masking and clutter edges.
11. 1.2.4 + Figure 1.2 + Table 1.1: each of the five situations shows one way a detector setting mismatches a property of coordination.
12. End of 1.2 (L233–241): every setting depends on jitter, participation or event spacing, none of which is known in advance, so they must be measured without a detector.
13. 1.3.1: the input, the "realistic" values from the lab, and the Neyman–Scott/Thomas generative model with a hard-core event train.
14. Figures 1.3 and 1.4 (L281–321): what each tool counts, on a sharp set and a jittered set.
15. 1.3.2: the correlogram's width depends on jitter alone and its area counts coordinated pairs; prediction matches measurement.
16. 1.3.3: excess pair and triple counts (factorial cumulants) give participants as 2 + f₃/f₂; jitter breaks this through window sharing g₂; surrogates supply chance.
17. 1.3.4: counting cells in bins (the assessor and the count detector); a high threshold misses jittered events.
18. 1.4 "What brute force found": a 48-condition grid found three failures it could not explain.
19. Table 1.2: the symbols.
20. Figure 1.6: undercount at wide jitter, and a flat jitter reading at the busier background.
21. 1.4 "The question": can each tool's output be derived in advance, with simulation only checking? (Aim 0)
22. 1.4 "Answer in brief": mostly yes, with numbers, known gaps and the realistic-segment verdict.
23. 1.4 "How tested": the residual definition, the held-out rerun and the realistic-value runs.
24. 1.4 "Prior work": detectors, bin-width coincidences, cumulants, cluster processes, assemblies, order.
25. 1.4 "Contributions": seven results, each with its standing against prior work.
26. 1.5.1–1.5.2: the undercount is k̂ = 2 + (k−2)g₃/g₂, and g_n has a closed or tabulated form.
27. 1.5.3: the expected excess counts with the at-most-one-event term; two same-jitter sources look like one.
28. 1.5.4: the hard-core form predicts participants to about 1 %, but residuals exceed noise on the held-out run.
29. 1.5.5: the general form (any stationary train) fixes the denser trains; the slow-stream residual is unexplained.
30. 1.5.6: the joint fit recovers σ, k and λ in part of the grid; against the correlogram tool.
31. 1.5.7: at realistic values, participants can be read from one segment when events are large or many, jitter never.
32. 1.6.1: the chance-cluster rate ν_c = 60q(1−q)² predicts the threshold failure, so the threshold must be set per recording.
33. 1.6.2: the assessor's jitter reading is a mixture of chance and event clusters; its own null does not rescue it.
34. 1.7: the tools merge event pairs at about (m+½) bin widths, while likelihood tests separate them at 0.3–0.8 s; this rarely binds at realistic intervals.
35. 1.8 / 1.8.1: membership reuse is detectable before its variance converges (Kish design effect).
36. 1.8.2: an order indicator has a large, exactly derivable no-order bias at few events; power needs at least 3–5 events.
37. 1.9.1: what the theory replaces and what stays with simulation.
38. 1.9.2: old versus new (Table 1.9).
39. 1.9.3: two sources are predicted, not tested; the test goes to Chapter 2.
40. 1.9.4–1.9.5: limitations and next steps by chapter.
41. 1.10: what one realistic segment can support.
42. About / Reproducing / References.

## 2. The arc used, and the cold open

**Arc.** Default arc: problem → cost → method → what it gets wrong → fix → evidence → residual risk. The chapter departs from it in two ways, and both are stated. The roadmap at L68–84 says the order is detectors, then tools, then question; the revision note at L1641ff records the owner's order (problem, detectors, tools with their math, then onward). Mapped onto the default:

- problem: items 1–3
- cost: item 4
- method and what it gets wrong: items 9–12 for the detectors, and items 15–20 for the tools
- question: item 21
- fix and evidence: items 26–36
- residual risk: items 39–40

The order holds overall. Positions 1–12 follow the owner's requested order faithfully.

**Cold open.** The first thing the reader sees is the title, then an italic provenance and disclaimer note (L3–6: who wrote it, that no human reviewed it, what ⚠ means). Only then comes "The problem". The problem paragraph itself is good, and Figure 1.1 arrives early (L28) and shows exactly what the problem looks like. Panel C as "all an analyst receives" is a strong first image.

But a block of definitions (L19–26) sits between the problem statement and the figure. And the disclaimer is the very first text, so the chapter opens on scope and provenance before motivation. Both are small, and both can be fixed without losing anything.

## 3. Findings

Columns: location · issue · severity · suggested fix · verifiable against a source. In the last column, "yes (artifact)" means checkable against the artifact's own lines.

1. **1.3 → 1.4 (items 15–18, L323–502).** The mystery arrives after its solution.
   - Issue: 1.4 presents the grid's three failures as things "nothing explained" (L500–502), and the chapter's question grows out of that puzzle. But by then the reader has already been given each mechanism:
     - g₂ and the f₃/f₂ undercount (1.3.3, L423–426);
     - the chance floor and the threshold failure (1.2.3, situation 4);
     - the assessor's 0.7 s jitter artifact (L43–45).
   - L501 admits it ("Section 1.3 has sketched their mechanisms"). So the motivating evidence follows the explanation it is supposed to motivate, and the question "can we derive it in advance?" reads as already answered.
   - Severity: major.
   - Fix (either works):
     - (a) Recast 1.4's opening honestly: the grid confirmed at scale what 1.2–1.3 sketched, but sketches are not predictions, so the question is whether they can be made exact and tested.
     - (b) Strip the mechanism sentences from 1.3 (keep the definitions, drop "That is not the jitter…", the hard-core explanation and the k̂-undercount preview) so that 1.4's failures arrive unexplained.
     - (a) is cheaper and keeps the owner's order.
   - Verifiable: yes (artifact).

2. **1.4, between the question (L567) and the first derivation (1.5, L744).** About 175 lines separate them: the answer in brief, how predictions are tested, prior work and contributions.
   - Issue: the "Contributions" list asserts seven results the reader cannot yet evaluate (g_n closed form, Kish design effect, arcsine relation, Borda score) before any of them is derived. "Answer in brief" (L572–591) likewise cites numbers that depend on terms first defined later (general form, slow-stream residual, the joint fit, "held-out rerun", which is only defined at L607).
   - The owner placed the prior work in 1.4 deliberately (L1644), so moving it is not this role's call. The contributions list, however, duplicates Table 1.9 (1.9.2), which sits where the claims can be judged.
   - Severity: moderate.
   - Fix:
     - Merge "Contributions" into 1.9.2 beside Table 1.9, leaving one sentence in 1.4 that points forward.
     - Trim "Answer in brief" to qualitative statements, or move "How the predictions are tested" in front of it so "held-out rerun" is defined before use.
   - Verifiable: yes (artifact).

3. **Figure 1.5 panels B and C (in 1.3.3, L442–461).** These panels belong to 1.8.1 and 1.8.2, about 870 lines later.
   - Issue: they show the assembly-test nulls and a fully worked score-sort/F example. A reader in 1.3 meets "the score sort", "net lead count" and "F = 0.67" with no motivation. The caption itself says "Panels B and C belong to 1.8.1 and 1.8.2". When 1.8 cites "Figure 1.5 B" and "Figure 1.5 C", the reader has to scroll back across the whole chapter.
   - Severity: moderate.
   - Fix: split the figure. Keep A (surrogate shift) in 1.3.3 and make B and C a new figure placed in 1.8.1 and 1.8.2.
   - Verifiable: yes (artifact).

4. **Figures 1.3 and 1.4 (in 1.3.1, L281–321).** Both are placed before the tools they depict are introduced.
   - Issue: Figure 1.3's caption explains "the coordination-rates tool's 1, 2 and 4 s windows" and "the assessor counts distinct cells per 1 s bin". Figure 1.4's caption uses HWHM, "excess pair count … as a share", g₂ and the K-cell tail. All of these are defined only in 1.3.2–1.3.4. The figures arrive before the reader can evaluate them.
   - Severity: moderate.
   - Fix: place Figure 1.3 at the end of 1.3.4 as the summary of "what each tool sees", or keep it but cut its tool-specific caption text to forward references. Either split Figure 1.4 so that C sits in 1.3.2, D in 1.3.3 and E in 1.3.4, or move the whole figure to the end of 1.3.
   - Verifiable: yes (artifact).

5. **Table 1.2 (Symbols), placed in 1.4 at L514.** The symbol table arrives after its symbols have been used for 300 lines.
   - Issue: N, b, K, w, σ, k, λ, E, h and B are used from 1.2.3 and through all of 1.3. The text at L278 even points forward to it ("Table 1.2 (1.4) collects the symbols"). Its "values in the first experiment" column ties it to 1.4, but its job is reference.
   - Severity: low–moderate.
   - Fix: move the table to the end of 1.3.1, right after the generative model, and keep the first-experiment values column there. 1.4 then refers back to it.
   - Verifiable: yes (artifact).

6. **Figure 1.6 (in 1.4, L535–545).** The motivating figure includes a result from later in the chapter.
   - Issue: the figure that shows "what brute force found" also draws the joint fit (violet), which is built from theory derived in 1.5.6. The caption admits it is "not part of the first experiment". Showing the fix inside the picture of the failure weakens the "failure, then question" beat.
   - Severity: low.
   - Fix: drop the violet series here (Figure 1.11 already compares the joint fit with the correlogram tool), or keep it but state in the 1.4 text that it is a forward reference.
   - Verifiable: yes (artifact).

7. **The two-source result buried in 1.5.3 (L835–839).** The result most consequential to the dissertation's premise sits in a technical subsection.
   - Issue: "pair and triple counts cannot tell two same-jitter sources from one" bears directly on the premise (L47). It sits as a bold paragraph inside the hard-core derivation, and only 1.9.3 picks it up. It has no job in 1.5.3's argument, which is about predicting one source.
   - Severity: low.
   - Fix: keep the derivation in 1.5.3, but give the claim its own short subsection or state it as the opening claim of 1.8 (which already restates it at L1304). Either way it arrives where its consequence is argued.
   - Verifiable: yes (artifact).

8. **Cold open (L3–6, L19–26).** The chapter opens on provenance before motivation, and definitions sit between the problem and its picture.
   - Severity: low.
   - Fix:
     - Move the italic disclaimer under the title into "About this chapter", or reduce it to one line after 1.1.
     - Move the definitions paragraph after Figure 1.1 and its caption, so the problem, its picture and then the vocabulary arrive in that order. The caption already defines raster, background and coordinated events.
   - Verifiable: yes (artifact).

9. **Cost paragraph (L40–45).** The concrete cost is stated in terms the reader does not have yet.
   - Issue: "one of the repository's tools reports the spread of chance groupings, about 0.7 s, as the jitter" uses the assessor and chance clusters before either is introduced. The reader cannot judge it at position 4.
   - Severity: low.
   - Fix: phrase the cost in Figure 1.1 terms (for example: if chance groupings are mistaken for events, the measured jitter is that of chance, not of the cells), with the forward pointer kept.
   - Verifiable: yes (artifact).

10. **1.3.1 realistic-value list (L248–266).** Material arrives before its use.
    - Issue: per-segment event counts, medians, ranges and interval-list provenance arrive before any tool. They have no job until 1.4 ("How tested"), 1.5.7 and 1.8.2. The generative model in the same subsection is needed here; the segment statistics are not.
    - Severity: low.
    - Fix: keep the four parameter values (b, σ, k, segment length) in 1.3.1, and move the segment-count distribution and interval-list details to "How the predictions are tested" under "Realistic values".
    - Verifiable: yes (artifact).

11. **Back-pointers from the answers to 1.4's failures are swapped.** This is a sequence-pointer error. Factual consistency is other roles' ground, but these pointers are how the reader matches each answer to its question.
    - L1125 (1.6.1, chance-cluster rate) says "This explains the third failure of 1.4", but in 1.4 the threshold failure is failure 2 (L550).
    - L1209 (1.6.2, jitter reading) says "This is the second failure of 1.4", but the jitter reading is failure 3 (L555).
    - Severity: low (but misleading).
    - Fix: swap "third" and "second".
    - Verifiable: yes (artifact).

12. **1.7 back-pointer to situation 3 (L1233).** It says "two events 3 s apart", while 1.2 (L176, L205) and Table 1.1 say 4 s apart. This is a cross-reference inconsistency, and number-checking is outside this role.
    - Severity: low.
    - Fix: change to "4 s apart".
    - Verifiable: yes (artifact).

## 4. Does each position earn its place?

**Positions that earn their place:** 1, 3, 4, 5, 7, 8, 9–12 (the detector section is well ordered: three detectors of rising sophistication, then one figure and table, then the synthesis that motivates measurement), 13 (model only), 15–17, 18, 21, 26–36, 37, 39–41.

**Positions that should move or be trimmed:**
- 0 and 2 (finding 8)
- 14 (finding 4)
- 19 (finding 5)
- 22 and 25 (finding 2)
- Figure 1.5 B–C (finding 3)
- the two-source paragraph inside 27 (finding 7)

**Positions that are appendix-like but sit at the end:** 38 is fine where it is; 42 is correctly last.

## 5. Bottom line

The large-scale order is defensible: problem with picture, cost, detectors, tools, failures, question, answers per tool, residual risk. It matches the owner's request, and the deviation from the default arc is stated in the roadmap.

The main defect is finding 1. Because the mechanisms are taught in 1.2–1.3, the 1.4 "unexplained failures" beat that motivates Aim 0 arrives after its own explanation. The next three in importance are the long gap between question and first answer (finding 2) and two figures placed far from what they illustrate (findings 3 and 4).
