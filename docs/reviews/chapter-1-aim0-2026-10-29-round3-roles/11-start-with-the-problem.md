GRANT 11 MISMATCH — missing none; holds Edit, Write, Bash, PowerShell, Agent, Artifact, Skill, ToolSearch (which can load NotebookEdit and others), and the Claude Docs MCP write tools (batch, update)

This is a finding about the run, not the artifact. The session handed this role the full harness instead of `Read, Grep, Glob`. I used only Read and Grep, and edited or created nothing.

**Blindness disclosure.** One Grep over `docs/` used a glob exclusion for `reviews/**` that did not take effect. Its output showed five lines from `docs/reviews/chapter-1-aim0_2026-10-29-round2-roles/`: four from `11-start-with-the-problem.md` (three printed, one omitted as too long) and one from `09-show-dont-tell.md`. Those lines refer to an earlier draft's section numbers (1.9.2, 1.6.2), which do not match this draft. One of them mentions the two-source claim being placed late. I had already written finding F1 below in my notes before that grep ran, but the adjudicator should know about the overlap. I opened nothing else under `docs/reviews/`.

## Spine (one claim per section)

1. **1.1 The problem.** Recordings mix two or more sources of coordinated events. This chapter deliberately takes one source first.
2. **1.1 What brute force found.** A 240-recording grid found three failures it could not explain: the participant undercount, the flat jitter reading, and a threshold that does not transfer (Fig 1.1).
3. **1.1 Question and answer.** The tools' output can mostly be derived from the planted parameters. At realistic values, participants can be read and fast-stream jitter cannot.
4. **1.1 Contributions.** Seven results, each tagged with its standing against prior work. Section 1.6 is explicitly not claimed.
5. **1.2.1** The data are multichannel onset times. The model is a hard-core Neyman–Scott/Thomas process, and the realistic values are listed.
6. **1.2.2** Four population-count tools and two cell-identity statistics are defined (Figs 1.2, 1.3).
7. **1.2.3** Prior work covers the neighbors. Gaussian g_n, the event-train term, the assessor's behavior and the analytical no-order mean were not found.
8. **1.3** The testbed: the grid, the residual definition, a held-out rerun, realistic-value simulations and the rederivation check. Fig 1.4 also appears here and states a joint-fit result.
9. **1.4.1** The undercount reduces to the window-sharing ratio g₃/g₂.
10. **1.4.2** g_n has a closed form, close to the uniform-jitter value, and k̂ falls toward 2 as σ approaches w.
11. **1.4.3** The full expected excess counts are factorial cumulants with an at-most-one-event term.
12. **1.4.4** The prediction matches to about 1 % of k, with a small systematic excess.
13. **1.4.5** The general event-train form removes that bias, matters on dense trains, and leaves a slow-stream residual unexplained.
14. **1.4.6** The joint fit recovers (σ, k, λ). Per recording it beats the correlogram at the busier background. At realistic values it reads participants but not fast-stream jitter.
15. **1.5.1** The chance-cluster rate explains the threshold failure and sets a safe threshold per background.
16. **1.5.2** The assessor's jitter reading is a chance/event mixture, which explains the flat reading.
17. **1.6** The tools merge events closer than about 2.5 bins. Likelihood tests separate events at about 0.5 s. Rarely binding at realistic intervals.
18. **1.7 intro** Two sources look like one to pair and triple counts, so separating them needs membership or order.
19. **1.7.1** Membership excess has Kish's design-effect form. The test detects reuse long after the variance has converged.
20. **1.7.2** The no-order mean of F is exact and its bias is large with few events. Order needs at least 5 events (or 3 events of 13 cells).
21. **1.8.1–1.8.5** What the theory replaces; old versus new; two sources (a prediction, no test); limitations; next steps.
22. **1.9** Closed forms explain the three failures. Chapter 2 starts from the two-source prediction.

## Arc and cold open

**Arc used:** the default analysis arc. Problem → what it costs → method → what the method gets wrong → fix → evidence → residual risk.

At chapter level the draft follows it:
- **Problem and cost:** 1.1 and Fig 1.1.
- **Method:** 1.4.1–1.4.3 and 1.5.
- **What the method gets wrong:** 1.4.4.
- **Fix and evidence:** 1.4.5 and 1.4.6.
- **Residual risk:** the end of 1.4.5 and 1.8.4.

Sections 1.6 and 1.7 extend past the three failures. For 1.7 the extension is announced in the 1.1 answer ("For cell-by-cell structure…"). For 1.6 it is not (see F2).

**Cold open:** good. Apart from the italic authorship note, the first thing the reader meets is the problem. Within a page they see Figure 1.1, which shows the failures, so the reader sees the problem before any method. That is the strongest ordering feature of the draft.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against a source |
|---|---|---|---|---|---|
| F1 | 1.7 opening, "derived, not simulated; *1.8.3*"; 1.8.3, "two sources with the same jitter look … like one source" | The two-source claim motivates all of 1.7 and the hand-off to Chapter 2. 1.7 points forward to 1.8.3 for its derivation, but 1.8.3 only restates the claim. The goal page (line 196) also gives only the statement and points to "blind B". So the claim that motivates a section arrives first as a pointer and never as an argument the reader can judge. Motivation trails what it motivates. | major | Derive the claim where it first becomes intelligible: at the end of 1.4.3 (or as a short 1.4.7). It follows from the f₂/f₃ forms, because a mixture's f₃/f₂ matches some single k̄. Then 1.7 opens by citing that, and 1.8.3 points back to it. | yes (chapter lines 753–754 and 977–984; goal page line 196) |
| F2 | 1.6 as a whole; 1.1 "Each is taken up in a section of its own"; Contributions, "not claimed as a contribution" | 1.6 has no stated job in the spine. It is not one of the three failures, it is disclaimed as a contribution, and no sentence says why it sits between the assessor (1.5) and the structure the population count cannot see (1.7). It breaks the 1.5 → 1.7 link, which runs from what the count tools see to what they cannot. 1.5.1 also forward-references its π_K ("derived exactly in *1.6*"). This deviation from the arc is unstated. | major | Either (a) state its job in 1.1. One sentence such as "The first experiment's 20 s hard core hid a fourth limit, merging of close events (*1.6*)" would do, and 1.6 could then move after 1.4.5, next to the dense-train result it belongs with. Or (b) move it to an appendix or the end of Discussion as a supplementary limit. Either way, π_K should come before 1.5.1's recall paragraph or that paragraph should move. | yes (lines 40, 114–115, 633, 687–749) |
| F3 | 1.3, Figure 1.4 and its caption ("the joint fit (*1.4.6*) recovers jitter within 0.8–1.25 … (Figure 1.8 C)") | This is a results figure placed in Methods. To evaluate it the reader needs the joint fit (1.4.6), the resolution band and Figure 1.8 C, none of which they have seen yet. Its claim ("realistic values sit between the points the joint fit resolves") reaches the reader before the estimator it judges. Evidence arrives before the claim and the method. | major | Move Figure 1.4 into 1.4.6, after the realistic-values table, or into 1.8.1, which already cites it. In 1.3, keep one sentence saying realistic values fall between grid points and were simulated directly. | yes (lines 317–338, 938) |
| F4 | Figure 1.1 caption, "The violet series is an estimator built from the theory in *1.4.6* and can be ignored until then" | The opening figure carries a result from the middle of the chapter and asks the reader to hold it in suspense. Minor, but it is the one blemish on an otherwise clean cold open. | minor | Drop the violet series from Figure 1.1 and show it in Figure 1.8, or re-show it in 1.4.6 as "Figure 1.1, revisited". | yes (lines 50–51) |
| F5 | 1.4.6, final third ("**At realistic values and realistic event counts**" through "A fit to a train built from *detected* events was not run") | This is the chapter's practical headline, stated in the 1.1 answer: participants can be read at realistic values, fast-stream jitter cannot. It is buried without its own heading at the end of a subsection titled for the joint fit and the correlogram. The 1.1 answer gives no section pointer for it. | minor | Split it into its own subsection, "1.4.7 At realistic values", and add "(*1.4.7*)" to the 1.1 answer sentence. | yes (lines 82–84, 567–591) |
| F6 | 1.7.1, "The variance is not what a test detects, though" | The section derives the variance ratio and its convergence first, then pivots to say the test detects something else. Reuse (E/M) and the two nulls are only defined after that pivot, although "reuse" is the axis of Fig 1.12 and of the conclusion. The order follows how the work was done, not how the argument runs. | minor | Open 1.7.1 with the question (how much reuse does a test need?), define reuse and the nulls, give the detection result, then present the variance ratio (Kish) as the reason the variance is the wrong statistic. | yes (lines 759–800) |
| F7 | 1.4.1, "dropping small terms derived in *1.4.3*"; Fig 1.5 B caption, "Yellow dashes are the full prediction of *1.4.3*" | Forward references inside 1.4. They are tolerable because they come in simplest-first order, but the figure in 1.4.2 depends on a term not yet introduced. | minor | Either move the yellow dashes to Figure 1.6, or add one clause to 1.4.2 saying the remaining gap is closed in 1.4.3. | yes (lines 355–357, 398–400) |
| F8 | Italic preface under the title | A process disclaimer comes before the problem. In this exercise's setting it is defensible, so I note it rather than ask for a move. | minor | Optional: shorten it to one sentence and leave the rest to *About this chapter*. | yes (lines 3–7) |

## What I checked and found sound

**Intro and background:**
- The cold open shows the problem, and Figure 1.1 is the first figure.
- The three failures are numbered in 1.1, and each is resolved in a section named there (1.4 / 1.5.2 / 1.5.1).
- The Contributions list states its own deviation, placing precedents in 1.2.3 and the full comparison in 1.8.2.

**Coordination-rates tool (1.4):**
- 1.4.4 → 1.4.5 → 1.4.6 follows the order "where the method gets wrong → fix → evidence → residual", and 1.4.5 ends on an explicitly unexplained residual.

**Order section (1.7.2):**
- 1.7.2 opens on its motivating observation before the indicator.
- The power section states why it uses 1–5 events, before the table.

**End of the chapter:**
- The Discussion's limitations follow the order of the results.
- The Conclusion closes on the Chapter 2 hand-off.

## Verdict for sign-off

The chapter-level order is sound and the cold open is right. Before I would sign:
- **F1:** derive the two-source claim before 1.7 relies on it.
- **F2:** give 1.6 a stated job and a position next to the dense-train result, or move it out of the main line.
- **F3:** move Figure 1.4 out of Methods to after the joint fit.

F4–F8 are polish.
