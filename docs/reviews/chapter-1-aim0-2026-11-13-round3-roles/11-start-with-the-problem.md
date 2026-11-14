GRANT 11 MISMATCH — missing none; holds Edit, Write, Bash, PowerShell, Agent, Artifact, Skill, Claude Docs batch/update (NotebookEdit and others deferred)

This mismatch is a finding about the run, not about the artifact. The role was reached through a fallback path that handed it editing tools. I used only Read and Grep-free Read calls on the artifact and the role file, edited nothing, and did not open docs/reviews/.

Artifact: `<repo>/docs/dissertation/chapter-1-aim0.md` (1794 lines), read in full. My unit is the order of sections, not the content of any one section.

## Spine: one claim per section

0. Title and provenance note: the chapter is an exercise, no human has reviewed it, and ⚠ marks sources that were not opened.
1. **1.1 The problem.** An onset stream mixes coordinated events with background, and nothing labels which is which (Fig 1.1). Getting this wrong carries into Chapters 2 and 4: for example, a tool reads about 0.7 s of jitter whatever the truth. The dissertation's premise is two or more sources; this chapter takes one on purpose. A roadmap follows.
2. **1.2 Simple detectors.** Counting active cells with fixed bins, a sliding window or CFAR succeeds or fails depending on whether its window, threshold and merge gap match properties of coordination. Those properties are unknown, so they must be measured first, without a detector.
3. **1.3.1 Data and model.** The input is onset lists. The model is a hard-core Neyman–Scott/Thomas process. Realistic parameter values are taken from the lab's data.
4. **1.3.2 Correlogram.** The width of the correlogram peak is set by jitter alone (HWHM ≈ 1.67σ), and the predicted width matches simulation.
5. **1.3.3 Coordination-rates tool.** Factorial cumulants f₂ and f₃ cancel the background, and k̂ = 2 + f₃/f₂. Jitter breaks this through g₂, and the prediction matches simulation to within 0.02. Surrogates supply the chance level.
6. **1.3.4 Assessor and count detector.** Counts of distinct cells in bins. A high threshold loses jittered events first.
7. **1.4 First simulation.** A brute-force grid found three failures it could not explain. The question (Aim 0): can each tool's output be derived in advance? The answer, in brief, is mostly yes. This section also holds how predictions are tested, the prior work and the contributions.
8. **1.5 Coordination-rates tool.** Window sharing g_n predicts the participant undercount. The hard-core form and then the general form predict the tool to a median of 1–2 %. The joint fit recovers jitter. At realistic values, one segment reads participants only when events are large or many, and never reads jitter.
9. **1.6 Assessor.** The chance-cluster rate predicts the threshold failure. The jitter reading is a mixture of chance clusters and event clusters.
10. **1.7 Separation.** The tools merge events closer than (m + ½) bins (2.5 s / 5 s). Likelihood tests separate them at 0.3–0.8 s. At realistic intervals the limit rarely binds.
11. **1.8 Membership and order.** How much assembly reuse, and how many events, a test needs. With few events, F is heavily biased.
12. **1.9 Discussion.** What theory replaces; old versus new (Table 1.9); two sources (predicted, untested); limitations; next steps.
13. **1.10 Conclusion.** What one 20-minute segment supports.

## Arc used

I checked against the default arc: problem → cost → method → what the method gets wrong → fix → evidence → residual risk. The chapter runs that arc twice, and says so in "How the chapter proceeds":
- **Outer loop:** the detection problem (1.1) → its cost (1.1) → simple detectors (1.2) → their failure, because settings need unmeasured properties (end of 1.2) → measuring tools (1.3).
- **Inner loop:** the tools' behavior is unknown and a grid finds failures (1.4) → predict-first theory (1.5–1.8, fix and evidence together) → residual risk (1.9.4).

Because it is stated, the double arc is a legitimate deviation. The defects are where the inner loop's fix arrives before its problem.

## Cold open

After the provenance note, the reader's first sight is "The problem", and Figure 1.1 is captioned "The problem". The cold open is the problem: this passes. The one wrinkle is at paragraph level. The first problem paragraph uses "calcium-imaging recording", "onset times", "calcium events" and "multichannel stream", and the paragraph that defines them comes second (see finding 8).

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source |
|---|---|---|---|---|---|
| 1 | 1.3.2–1.3.4 against 1.4 "What brute force found" | **The fix arrives before the problem that motivates it.** 1.4 presents the grid's failures as things "nothing explained" and states Aim 0 only at line ~599. By then 1.3 has already done predict-and-check successfully: correlogram predicted 0.174 s vs measured 0.177 s; g₂ predictions within 0.02, with "the full prediction (solid lines, derived in 1.5.3)"; "k̂ falls below the true number of participants" in 1.3.3; jittered events lost at a high threshold in 1.3.4. Each of the three failures 1.4 lists has already been explained earlier: the undercount in 1.3.3, the fixed threshold in situation 4 of 1.2.4 plus 1.3.4, the flat jitter reading in 1.1 para 3. 1.4's own disclaimer, "A sketch is not a prediction", is contradicted by 1.3 giving quantitative predictions to three digits. The chapter's titular question therefore lands as a question already answered. | High | Either (a) keep 1.3 to definitions and what each tool counts: move the predicted curves in Fig 1.4 C/D and the predicted-vs-measured numbers in 1.3.2/1.3.3 into 1.5, and let Fig 1.4 show measurements only. Or (b) move "What brute force found" with Fig 1.6 to the end of 1.3, before any prediction, and reframe 1.3's numbers as the first instance of the answer. Option (a) keeps the owner's requested sequence (problem → detectors → tools with their mathematics) and preserves 1.4's surprise. | yes (artifact text, lines 384–451, 493–500, 525–531) |
| 2 | Fig 1.6 (1.4), violet series | The problem figure carries the fix. The joint fit, built "afterwards from the theory of 1.5.6", is drawn on the figure meant to show the unexplained failures. A reader sees the solution track planted jitter before the joint fit is defined or motivated. | Medium | Drop the violet series from Fig 1.6 and show it where the joint fit is evaluated (Fig 1.11 already does this). | yes (caption, lines 569–577) |
| 3 | 1.4 "How the predictions are tested" (lines 626–663) | **Evidence machinery arrives before any prediction exists.** It defines residuals, the pooled path ("residuals change by at most 0.008"), refusals ("17 of 720"), the held-out rerun and the realistic runs (citing Fig 1.12 from 1.5.7). None of it can be evaluated until 1.5.4. The earliest point where it makes sense is the opening of 1.5.4. | Medium | Keep one sentence in 1.4 ("predictions are checked on a held-out rerun and at realistic values; see 1.5.4"). Move the rest to the head of 1.5.4, or to a short 1.5.0 "How the predictions are tested". | yes |
| 4 | Fig 1.5, placed in 1.3.3 | Panels B and C (the assembly test's nulls; the score sort and F) "belong to 1.8.1 and 1.8.2" by the caption's own admission. They arrive about 900 lines before F, the score sort or the assembly nulls are defined. | Medium-low | Split Fig 1.5: keep A (surrogates) in 1.3.3 and move B and C to 1.8 as their own figure. | yes (lines 467–486) |
| 5 | 1.3.1 realistic-values block (lines 260–287) | The lab's realistic values (segments, event counts per segment, interval lists, k = 7/13) sit inside the tools introduction. Their only job is to set the stakes for 1.5.7, 1.7 and 1.8, and 1.4 restates them. Meanwhile 1.2.3 already relies on "0.0096 Hz, typical of the lab's recordings" before this block sources it. | Low | Move the block to 1.4 next to "Realistic values ... were simulated directly", leaving one line in 1.3.1. Alternatively, cite the source for 0.0096 Hz at first use in 1.2. | yes |
| 6 | 1.4 "Contributions" → Table 1.9 in 1.9.2 | The contributions are tagged with their standing against prior work, and "Table 1.9 gives the full comparison", but the table arrives about 830 lines later. The claim and its supporting comparison are split across the chapter. The deviation is conventional for a dissertation but unstated. | Low | Either move Table 1.9 into 1.4 under Contributions, or state at the top of Contributions that the evidence for each tag is in 1.9.2. | yes |
| 7 | 1.2.3 lines 136–146 | The chance-floor reconciliation with the repository's simulated event floor ("agreement at two points, not a test of the formula's shape") is evidence for a result that 1.6.1 develops. It sits inside the beginner's tour of detectors and interrupts the tour's single job, which is to show that the threshold must follow the background. | Low | Cut to the floor values (6 and 12 cells). Move the comparison with the repository's floor to 1.6.1, which already discusses the event floor. | yes |
| 8 | 1.1, paragraphs 1 and 2 | Paragraph 1 uses "calcium-imaging recording", "onset times", "calcium events" and "multichannel stream". Paragraph 2 defines recording, frame, calcium event, onset and channel. The definitions follow their first use. (Boundary: role 8 owns whether a stranger can read each term. I flag only that the defining paragraph comes after the one it serves.) | Low | Merge so that each term is defined in the sentence that first uses it, or open with the concrete paragraph 2 and follow with the abstract problem statement. | yes |
| 9 | 1.5.2 opening, "Section 1.3.3 introduced g₂", and 1.5.1 restating k̂ | This duplication follows from finding 1: g₂ and k̂ are derived twice, informally in 1.3.3 and formally in 1.5. | Low (resolved by fixing 1) | If 1.3 is cut back under option (a), 1.5.1–1.5.2 become the single first statement. | yes |

## Does each section earn its position?

- **1.1:** problem, cost and scope. It earns its position.
- **1.2:** shows the problem is non-trivial and motivates measurement before detection. It earns its position, apart from finding 7.
- **1.3:** introduces the instruments. Its job should be "what each tool counts", but it currently also does 1.5's job (finding 1).
- **1.4:** states the inner problem and the question. It is overloaded with test methodology (finding 3), prior work and contributions. Prior work and contributions are placed defensibly; the test methodology is not.
- **1.5, 1.6:** the fix and its evidence, one tool each. They earn their positions, and each correctly ends on realistic values or the shipped null.
- **1.7:** motivated by situation 3 and by 1.4's "fourth limit". It earns its position.
- **1.8:** motivated by "two sources look like one" in 1.5.3. It earns its position, and its opening restates the motivation, which is needed after a 470-line gap.
- **1.9 / 1.10:** discussion, residual risk (1.9.4) and next steps. They earn their positions.
- **"About this chapter" and "Reproducing":** appendix material, correctly placed at the end.

No section lacks a job in the spine. The main defect is finding 1: the tool-mathematics section presents successful predictions before 1.4 sets up the question those predictions answer.
