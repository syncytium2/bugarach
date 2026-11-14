GRANT 11 MISMATCH: missing none; holds forbidden tools Edit, Write, Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch, mcp__claude_ai_Claude_Docs__update (plus deferred Docs/Dropbox and Gmail write tools reachable via ToolSearch). I used only Read and Grep. No file was edited, written or deleted.

**Note for the run record:** this reviewer was spawned through a fallback path, not as a named agent with its own grant. The run record's `roles:` line must say so.

# Role 11: Argument order ("Start With the Problem")

**Artifact:** `<repo>\docs\dissertation\chapter-1-aim0.md` (blob 14d63527), 1669 lines.

**What I read:**
- the whole body through 1.10, plus the headings of the end matter;
- Figures 1.1 and 1.2 opened as images;
- the other figures judged only from their captions and where they sit, since my unit is the sequence.

## Spine (one claim per section)

0. **Title and italic note:** "Predict first, simulate to check." This is the method's slogan. Then comes a note on who wrote the chapter, that no human has reviewed it, and what the ⚠ mark means.
1. **1.1 The problem + Fig 1.1:** A recording becomes unlabeled onset times per cell. Some onsets are coordinated events hidden in independent background, and the analyst cannot tell which.
2. **1.1 premise and plan:** Recordings mix two or more sources, each with its own participation, jitter, intervals, membership rule and template. The dissertation builds tools to measure them over four chapters, and this chapter takes one source on purpose.
3. **1.1 How the chapter proceeds:** A roadmap: detectors, then tools, then the Aim 0 question, then answers.
4. **1.2.1–1.2.3:** Fixed bins, a sliding window and CFAR each count active cells against a threshold. Each has a built-in weakness (bin borders, chance groupings, masking).
5. **1.2.4 + Fig 1.2 + Table 1.1:** Each detector succeeds or fails depending on whether its settings match unmeasured properties (jitter, participation, interval, background). So those properties must be measured without a detector first.
6. **1.3.1 + Table 1.2 + Fig 1.3:** The data, the realistic values, the cluster-process model, the symbols, and two demonstration sets (sharp and jittered).
7. **1.3.2:** The correlogram's width reads jitter, its area reads coordinated pairs, and its height reads visibility. The prediction matches the two sets.
8. **1.3.3 + Fig 1.4:** Excess pair and triple counts (factorial cumulants) give participation, provided the window holds the whole event. Window sharing g₂ breaks that; the tool takes its chance level from surrogates.
9. **1.3.4 + Fig 1.5:** Counting active cells per bin separates coordination from chance in the tail. Jitter spreads events across bins. Defines the assessor and the count detector.
10. **1.3.5:** A placeholder saying membership and order statistics exist and are introduced in 1.8.
11. **1.3.6:** Prior work, about 75 lines, ending with "What is missing."
12. **1.4 What brute force found + Fig 1.6:** A simulation grid found three failures it could not explain: participant undercount, a flat jitter reading, and a threshold that does not transfer across backgrounds.
13. **1.4 The question:** Aim 0 asks whether each tool's output can be derived and checked by simulation. Brief answer: mostly yes for one source, with listed limits.
14. **1.4 How the predictions are tested:** Residual definition, held-out record, realistic-value simulations.
15. **1.4 Contributions:** Seven results, each with its standing against prior work.
16. **1.5.1–1.5.2 + Fig 1.7:** The undercount follows from window sharing g_n.
17. **1.5.3:** The hard-core form of the excess counts. A side result: two sources with the same jitter look like one.
18. **1.5.4 + Figs 1.8, 1.9:** The hard-core form predicts participants to about 1 %, with residuals beyond sampling noise.
19. **1.5.5 + Fig 1.10:** The general form (pair correlation of the event train) fixes dense trains. A slow-stream residual is still unexplained.
20. **1.5.6 + Fig 1.11:** The joint fit recovers jitter, participation and rate for k ≥ 10 and σ ≥ 0.2 s, and beats the correlogram at the busier background.
21. **1.5.7 + Fig 1.12, Tables 1.4, 1.5:** At realistic values one 20-minute window reads participants only when events are large or many, and never reads jitter.
22. **1.6.1 + Fig 1.13:** The chance-cluster rate explains the threshold failure. The threshold must be set per recording.
23. **1.6.2 + Fig 1.14:** The assessor's jitter reading is a mixture of chance and event clusters, which explains the flat reading. Its own null does not fix it.
24. **1.7 + Figs 1.15, 1.16:** Likelihood tests separate events about 0.5 s apart, but the tools merge events within about 2.5–5 s because of their bins. This rarely binds at realistic intervals.
25. **1.8.1 + Fig 1.17:** Membership reuse is detectable before its variance excess is visible (Kish design effect).
26. **1.8.2 + Figs 1.18, 1.19:** The order indicator has an exact no-order mean. An order test needs about 3–5 events, and frame rounding changes the null.
27. **1.9.1–1.9.5:** What theory replaces, a table of old vs new, the two-source question deferred to Chapter 2, limitations, next steps.
28. **1.10:** Conclusion: what one realistic window can support.

## Arc used

The owner's stated order: problem → simplest detectors, with successes and failures → tools that characterize coordination, with their mathematics → onward.

Mapped onto the default arc: problem (1.1) → what it costs (1.2) → method (1.3) → what the method gets wrong (1.4) → fix (1.5–1.6) → evidence (1.5.4–1.6.2, 1.7, 1.8) → residual risk (1.9.4).

The chapter follows this arc, and the roadmap in 1.1 states the order out loud. One deviation: the Aim 0 question arrives only in 1.4, after about 540 lines. That is the owner's requested placement, and the roadmap announces it, so it is not a defect in itself.

## Cold open

**What the reader sees first:**
1. the title, which is the method's slogan (the fix), not the problem;
2. an italic note about who wrote it, who reviewed it, and what ⚠ means;
3. the problem in prose (lines 12–17);
4. a definitions paragraph;
5. Figure 1.1, at line 27.

Figure 1.1 shows the problem well. Its three panels (background, events, the analyst's view) make it clear the analyst cannot see the labels. So the problem does arrive first among the content. The material in front of it is small, but it is not the problem.

## Findings

Each row: location · issue · severity · suggested fix · could I verify against a source.

| # | Location | Issue | Severity | Suggested fix | Verified? |
|---|---|---|---|---|---|
| 1 | Fig 1.5 (l. 439–456), in 1.3.4 | Figure 1.5 ("One recording, and what each tool counts in it") is never cited anywhere in the text (the only match for "Figure 1.5" is its own caption). It has no job in the spine where it sits. It is the intuitive picture of what each tool counts. It arrives after Fig 1.3 has already shown every tool's *output* on two sets, so the reader sees results before the picture that explains what is being counted. | High | Move Fig 1.5 to the start of 1.3, before Fig 1.3, or right after 1.3.1. Cite it where each tool is introduced (1.3.3 windows, 1.3.4 bins). If it cannot earn a citation, move it to an appendix. | yes (Grep) |
| 2 | 1.3.3 (l. 370–378) vs 1.4 failure 1 (l. 572–574) | 1.3 already explains the undercount ("g₃ falls faster than g₂ … k̂ falls below the true participation"). It also shows the "full prediction (solid lines, derived in *1.5.3*)" matching within 0.02, including the hard-core correction. Then 1.4 presents the undercount as a failure "it could not explain," and Aim 0 as the response. The reader meets explanation → mystery → explanation. This undercuts the motivation of the chapter's central question: the answer arrives before the question. | Medium-High | In 1.3, keep the tools' ideal-case math (g₂ and the k̂ = k − 2 logic, as the owner asked). Remove the "full prediction" lines and the "within 0.02" claim from Fig 1.3 D and the 1.3.3 text, and delete the sentence that predicts k̂ falls. Let 1.4 raise the undercount as the unexplained observation and 1.5 resolve it. Or, if 1.3 keeps the predictions, reword 1.4 so it doesn't claim the failures were unexplained. | yes |
| 3 | Fig 1.6 caption (l. 569–570) | The figure that presents the brute-force failures (the problem in 1.4) also plots the violet joint fit, "an estimator built from the theory in *1.5.6*." The fix appears inside the figure meant to show the failure, two sections before the fix is built. | Medium | Remove the violet series from the 1.4 version of Fig 1.6. Show the joint fit against the grid first in 1.5.6 (Fig 1.11 already does this). If one figure must serve both places, say in the 1.4 caption to ignore the violet series until 1.5.6. | yes (caption; I did not open the image) |
| 4 | Fig 1.4 (l. 392–411), placed in 1.3.3 | Fig 1.4 bundles three mechanisms. Only panel A (surrogate) is used where it sits. Panels B (assembly nulls) and C (order indicator worked example) are first used in 1.8.1 and 1.8.2, about 850 lines later. When the reader meets them they cannot evaluate them: assemblies, nulls, the score sort and F are not yet defined. | Medium | Split it. Put panel A in 1.3.3. Move B to 1.8.1 and C to 1.8.2, where they are cited. | yes |
| 5 | 1.3.6 Prior work (l. 467–540) | About 75 lines of prior work sit between the tools (1.3.1–1.3.5) and the question (1.4). That puts the motivation off further, which is the failure the cold-open rule targets. Its "What is missing" paragraph names results the reader has not met (the assessor's cluster-start factor, its jitter reading as a mixture, an analytical no-order mean). It also overlaps the Contributions list (1.4) and Table 1.9 (1.9.2): the same material is placed three times. | Medium | Move 1.3.6 to just after the question in 1.4, as the context for the Contributions. Or fold it into 1.9.2 beside Table 1.9. Keep in 1.3 only the one-line source for each tool where it is introduced (most already have one inline). | yes |
| 6 | Table 1.2 (l. 247–265), in 1.3.1 | The symbols table has a column "values in the first experiment," but that experiment is introduced only in 1.4. Most rows (g_n, K/q, ν_c/ν_e, π_K, Δ/τ_min, M, δ/r, F/n̄) belong to 1.5–1.8. A reader outside the subfield gets a glossary of things not yet motivated. | Low-Medium | Keep the table where it is but limit it to the symbols used in 1.2–1.3 (N, k, σ, b, E/λ, w/p, f₂/f₃). Move the grid values and the later symbols to the start of 1.4 (the first experiment) or to an appendix glossary. | yes |
| 7 | 1.3.5 (l. 458–465) | This subsection only points forward to 1.8. It makes no claim and does no job at this position. | Low | Delete it. 1.8's opening already motivates membership and order from the two-sources result. Optionally keep one sentence at the end of 1.3.4. | yes |
| 8 | 1.5.3 "Two sources look like one" (l. 776–780) | The chapter's result most relevant to the dissertation's premise (pair and triple counts cannot tell two same-jitter sources from one) is a bolded aside inside the derivation of the hard-core form. It falls between that form and its test (1.5.4), interrupting derivation → test. 1.8 and 1.9.3 both depend on it. | Low-Medium | Move it to its own short subsection at the end of 1.5 (after 1.5.7), or make it the opening claim of 1.8. Keep 1.5.3 → 1.5.4 contiguous. | yes |
| 9 | 1.4 failure list (l. 572–583) vs 1.6 order | Failures are numbered 2 = jitter reading and 3 = threshold. 1.6 resolves them in the opposite order, 1.6.1 threshold then 1.6.2 jitter, and correctly so, since the jitter mixture depends on the chance-cluster rate. The brief answer (l. 596–599) also lists jitter before threshold. The reader's index of the problems runs against the order of the answers. | Low | Swap failures 2 and 3 in 1.4, and in the brief answer, so the list follows the order of the derivations. | yes |
| 10 | 1.1 (l. 39–56) | Between the problem figure and the detectors, 1.1 gives the multi-source premise, the four-chapter plan, the repository's name, and then "this chapter takes one source." The reader carries dissertation-level scope through 1.2–1.8, while this chapter's problem is the one-source picture in Fig 1.1. The cold-open rule warns against scope ahead of motivation. Here it comes after the cold open, so the cost is suspense rather than a missing problem. | Low | Keep one sentence of the premise in 1.1. Move the four-chapter plan to just before 1.9.5 or to the dissertation's front matter. | yes |
| 11 | Missing arc step: "what it costs" | 1.1 gives the cost of the problem in one sentence ("Downstream analysis rests on knowing which onsets…"). Section 1.2 shows detector failures, which is the cost to the *method*. But a reader outside the subfield is never told what goes wrong *scientifically* if events are miscounted or jitter is misread. The one concrete downstream cost is in 1.6.2 (l. 1164–1166): the repository plants the chance-cluster spread as simulated jitter. It sits at the end of a technical subsection. The deviation from the default arc is not stated. | Medium | After Fig 1.1, add two or three sentences naming the stakes: wrong event counts, participation or jitter flow into the simulated sets of Chapter 2, and into the treatment comparison of Chapter 4. Pull the 1.6.2 "plants `jit_obs`" consequence forward as the example. | partly. The stakes are a content question; whether they are absent from the spine is verified |
| 12 | Title and italic note (l. 1–6) | The first things the reader sees are the method's slogan and a provenance/review/⚠ note, before the problem. The note duplicates "About this chapter" (l. 1549ff.) and Limitation 6. | Low | Move the italic note to "About this chapter," keeping only the ⚠ legend, or put the ⚠ legend at the References. Optionally reorder the title so the problem comes first ("Finding coordinated events in multichannel event times: predict first, simulate to check"). | yes |
| 13 | 1.1 (l. 19–26) | A definitions paragraph (recording, frame, onsets, what is not used) sits between the prose statement of the problem and Figure 1.1, which delays the picture. | Low | Put Figure 1.1 right after the first paragraph and move the definitions below it. The figure's caption already defines raster, background and coordinated event. | yes |
| 14 | 1.4 "How the predictions are tested" (l. 635–650) | The realistic-value simulation designs (renewal trains, 45-minute vs 20-minute windows, the denser earlier run) are set out in 1.4. The reader can evaluate them only at 1.5.5 and 1.5.7, where they are used. | Low | Move the realistic-value design paragraph to the start of 1.5.7 (or 1.5.5 for the denser-train check). Keep the residual and held-out definitions in 1.4. | yes |

## Each section's job, and whether it earns its position

- **Earn their positions:** 1.1 problem + Fig 1.1; 1.2 as a whole (motivates measuring before detecting, with each detector succeeding and failing as the owner asked); 1.3.1–1.3.4 (tools with their mathematics); 1.4 failures → question → contributions; 1.5 → 1.6 → 1.7 → 1.8 (each answers a named failure or limit, with back-links to Fig 1.2 situations 3 and 4 that tie the sequence together); 1.9; 1.10.
- **Placed out of order:** Fig 1.5 (finding 1), Fig 1.4 B/C (finding 4), 1.3.6 (finding 5), the explanatory content of 1.3.3 (finding 2), the joint-fit series in Fig 1.6 (finding 3).
- **No job where it sits:** 1.3.5 (finding 7).

## Overall

At the level of sections the order is sound, and it is the order the owner asked for. The problem is drawn first, the detectors succeed and fail visibly in Fig 1.2 / Table 1.1, the tools follow with their mathematics, and the failures → question → derivation → evidence → limitations sequence holds from 1.4 on.

The defects are local placements that put the answer ahead of the question:
- 1.3 explains a failure that 1.4 then calls unexplained;
- the 1.4 problem figure carries the 1.5.6 fix;
- two figure panels and a prior-work section arrive long before the reader can judge them;
- one figure (1.5) has no citation and lands after the results it should introduce.
