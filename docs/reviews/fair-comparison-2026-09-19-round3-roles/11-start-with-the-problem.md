<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round3/. -->

GRANT 11 ok — Read, Grep, Glob

(SubagentHandback is only the channel for returning this report. I hold no Edit, Write or NotebookEdit tool.)

Role 11, argument order ("Start With the Problem"), round 3, blind pass.
Artifact: %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html (the built HTML). I read the headings, all the prose and the captions with Grep and Read. I also looked at the full-page render, %USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\renders_round3\page_full_1100px.png, but it only displays at 121x2000, so I used it for rough layout only. I did not open any review record or run record.

## Spine: one claim per section

0a. Title line (H1): the question is whether the learned detectors beat the hand-written ones once both are tuned fairly.
0b. Dim line and "Terms" block: a glossary of 13 terms (ROI, firing, coordinated event, call, F1, recall, precision, outer fold, held-out, the two streams, baseline periods, goal 1, project lead). It makes no claim.
0c. "The question": an earlier comparison put the best net 0.103 F1 ahead of CoactDetect, but on a retired simulator and with the nets untuned, so this run tunes both sides and asks again.
0d. "The answer": under a shared false-alarm budget CoactDetect leads every net. On F1 alone the two sides are within 0.01 F1, and which one leads depends on the merge gap and on the draw of recordings. The 0.103 lead is gone, but the report cannot say which of three changes removed it. The two sides win in different places.
1. The problem: a coordinated event is hard to find because busy cells and field-wide busy spells produce chance coincidences. Distractors cap precision at about 0.71.
2. The bench: F1 needs known events, so a simulator fitted to real baseline recordings plants them. This section also gives the scoring rules.
3. The contestants: ten detectors, four nets and six coded. The nets differ in where they pool ROIs. `tube` is a control that no longer ties CoactDetect.
4.1 Nested cross-validation: settings are chosen without seeing the recordings they are scored on. Four folds give only 3 degrees of freedom, so the t values rank consistency and are not tests.
4.2 A pre-run defect, where outer folds could train the identical model, was fixed and checked before launch.
4.3 The coded side runs in sliding mode at goal 1's settings.
4.4 Every contestant is chosen twice: on F1 alone, and on F1 within a false-alarm budget of 1.6 times the reference CoactDetect.
4.5 A coded result counts only if it passes the crowded-recording check. The nets were not checked.
5. A second, disjoint draw of recording seeds replicates the whole run.
6. Results: in this run no net is ahead of CoactDetect. In the replicate the best net is ahead on F1 alone once failed refits are set aside. Under the budget both draws agree that CoactDetect leads.
7. The merge gap was tuned for the coded side only. Matching it puts `chorus_norm` ahead on F1 alone in point estimate but not under the budget.
8. The two sides differ only on the faintest events: the nets find more of them against a busy background, CoactDetect more against a quiet one.
9. Binned SCE's first place comes from its merge gap. Four coded detectors have no admissible result under the budget. Choosing a different reference for the crowded check changes no verdict.
10. Tuning moved the nets very little. About 1% of net refits failed to train. Many net refits went over the budget on held-out recordings.
11. Limits (twelve items).
12. Where everything is. Provenance follows.

## The arc I judged against

I used the default analysis arc, adapted to a comparison report:
- problem: the detection task, plus an earlier comparison that was not fair
- what it costs: a 0.103 lead that may be an artifact
- method: fair nested tuning with a shared budget
- what the method gets wrong: the merge gap is not shared, the two sides train on different amounts of data, and there are only 4 folds
- fix: re-scoring at matched gaps, and the replicate
- evidence
- residual risk

The report's one deviation is putting the answer before the problem. That deviation is stated ("The sections below explain every term in this paragraph, and sections 6 to 8 give the numbers"), so it is allowed. The body order 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 11 fits the arc well. The defects are in where individual concepts and claims land, not in the overall order of sections.

## Cold open

The reader first sees the H1 question. Next come a dim scope line and then a 13-term glossary paragraph, which is a "definitions" opening. Only after that do the question and a number-dense answer arrive. Figure 1, the one picture of what the problem looks like, comes after all of that and after section 1's first paragraph. Judging from the downscaled render, Figure 1 starts somewhere near the bottom of the first screen at 1100 px, but I could not verify this at that resolution.

The owner's brief asked for "concepts before numbers". The cold open gives definitions first and numbers second (+0.103, "within 0.01 F1"). The first concept figure comes third.

## Findings

Each finding gives: location · issue · severity · suggested fix · verified against a source (yes/no).

1. **The merge gap concept arrives in section 7 but is load-bearing from the lede on.**
   - Location: the lede answer; Table 1's caption; Figure 2's third row; §4.3 ("merge gap of 8 s (section 7)"); §4.4 ("counts calls after merging… (section 7)"); §4.5 ("a search free to widen the merge gap (section 7)"); §7 with Figure 9 panel A.
   - Issue: the reader is sent forward to section 7 five times before the concept is explained. The only concept schematic for it, Figure 9 panel A, is numbered 9 and sits after all the results figures. The crowded-recording check (§4.5), and so admissibility in Table 2, cannot be understood without it. All other concept figures come first (Figures 1–6).
   - Severity: high.
   - Fix: move the concept, §7's first paragraph and Figure 9 panel A, up to §2 next to Figure 2's scoring rules (or make it its own §4 subsection) and renumber the figure. Keep the asymmetry analysis (panel B and Figure 10) in §7, where it correctly follows the results.
   - Verified: yes.

2. **Section 4 is titled "How the comparison was kept fair" and lists only what was made fair. The asymmetries come after the results.**
   - Location: §4 compared with §7 and §11.
   - Issue: several asymmetries bear directly on the H1 question ("tuned fairly?"):
     - The nets' merge gap was fixed at 2 s.
     - A net fits 10 of the 72 training recordings and picks its threshold on 2, which §11 calls a handicap to the nets.
     - The nets' threshold is picked on pooled F1.
     - Only the coded side had the crowded-recording check.

   The reader first learns them in §7 and §11, after judging Table 2 and Figure 7. §4.1 and §4.5 each mention one of these only in passing. This is the "what the method gets wrong" step of the arc, split and put after the evidence.
   - Severity: medium-high.
   - Fix: end §4 with a short "4.6 What was not equalized" list (one line each, pointing to §7 and §11), so the reader reads the results already knowing about them.
   - Verified: yes.

3. **The cold open is definitions, then numbers, then the problem picture.**
   - Location: from the H1 down to §1 and Figure 1.
   - Issue: a glossary paragraph comes before the question. The answer paragraph uses concepts the reader does not yet have (budget, merge gap, refits, draws, busy and quiet background), and the report admits this ("The sections below explain every term"). The owner asked for concepts before numbers. Figure 1, the picture of the problem, comes after the answer.
   - Severity: medium.
   - Fix: open on the question, then Figure 1 with section 1's first paragraph (what a coordinated event looks like and why chance coincidence makes it hard). Then give a plain-language answer with no numbers and no undefined terms, e.g. "tied on accuracy alone; the coded detector ahead once false alarms are capped; they win on different events". Move the numeric answer to the top of §6. Define terms at first use, or move the glossary below the answer.
   - Verified: yes for the order; no for exactly where Figure 1 falls on the first screen.

4. **Binned SCE's apparent top score is explained three sections after the reader sees it.**
   - Location: §6 (Figure 7, Table 2) compared with §9's first bullet.
   - Issue: §9 says binned SCE "finishes first on paper, at 0.771" on F1 alone, above CoactDetect's 0.748. §6's text never mentions it. A reader looking at Figure 7 and Table 2 sees a coded detector ahead of the reference and gets no explanation until §9. The claim is intelligible at §6, where it belongs.
   - Severity: medium.
   - Fix: add one sentence to §6 saying that binned SCE's top place comes from its 30 s merge gap and that it fails the crowded check in 7 of 8 cases (§9). Alternatively, move §9's first bullet into §6.
   - Verified: yes.

5. **§6 relies on "refits that failed to train", but that concept is explained in §10.**
   - Location: the lede answer ("once refits that failed to train are set aside"); §6 bullets 2 and 3; §10, "Refits below 0.2 F1".
   - Issue: the replicate's disagreement on F1 alone rests on setting failed refits aside. What a failed refit is (the signature of one long call per recording), how often it happens (about 1%) and why excluding them is defensible all come four sections later. So §6's key sentence arrives before the reader can judge it.
   - Severity: medium.
   - Fix: move the failed-refit paragraph and its list from §10 into §6, just before the replicate bullet, or put a two-sentence definition at the point of first use.
   - Verified: yes.

6. **The lede sends the reader to sections 6–8 for the numbers, but the evidence for "the 0.103 lead is gone and three changes are confounded" is in §10.**
   - Location: the lede answer compared with §10, "Tuning moved the nets by little" (Figure 12).
   - Issue: the claim that answers the report's own "The question" paragraph sits under a heading about checks ("Tuning, failed refits and budget overruns"). The lede's pointer ("sections 6 to 8 give the numbers") sends the reader past it.
   - Severity: medium.
   - Fix: move the tuned-versus-untuned paragraph and Figure 12 into §6, as the direct test of the earlier +0.103 comparison. Alternatively, change the lede's pointer to include §10.
   - Verified: yes.

7. **§1's distractor paragraph arrives before the bench it depends on.**
   - Location: §1, second paragraph.
   - Issue: the claim that distractors cap precision at 0.71 (15 planted events against 6 distractors, the 18% participation level, the probe) uses parameters first given in §2 (participation levels and the count of 15 events). Its earliest intelligible position is after §2's second paragraph. §1's own job is "why this is hard", and the first paragraph already does it.
   - Severity: low-medium.
   - Fix: keep §1 to the conceptual problem and Figure 1. Move the distractor definition and the precision-cap arithmetic into §2 after the bench parameters, or into §8, where "both sides call 84% to 100% of distractors" pays it off.
   - Verified: yes.

8. **§4.2, a pre-run defect, is process history placed in the middle of the method.**
   - Location: §4.2 and Figure 4.
   - Issue: its job in the argument is to assure that the outer folds are independent fits. That fits in one sentence of §4.1. The full account (runs of 10 consecutive recordings, dealing order, a replay check, shared seeds) and a concept figure spend the newcomer's attention between the fairness design and the coded-side settings. For a newcomer, the claim has no downstream job beyond that one assurance.
   - Severity: low-medium.
   - Fix: reduce it to one sentence in §4.1 ("each outer fold trains a different model; see §10"). Move the details and Figure 4 into §10 or an appendix.
   - Verified: yes.

9. **The statistical caveat comes before any comparison exists.**
   - Location: §4.1, "What four folds can and cannot show".
   - Issue: the correction factor, three citations and the 3.18 threshold arrive two sections before the first t value (Table 2, §6). The reader holds them without a number to apply them to.
   - Severity: low.
   - Fix: keep one sentence in §4.1 ("4 folds, 3 degrees of freedom; t values rank, they do not test"). Move the correction paragraph next to Table 2 in §6.
   - Verified: yes.

10. **§3 has a result before the method, and one claim nothing later uses.**
    - Location: §3.
    - Issue:
      - "untuned, it scores 0.629 against the tuned CoactDetect's 0.748" is a held-out result given before tuning and scoring are explained.
      - "The difference between the nets that matters most is where each stops treating ROIs separately" is presented as the key distinction, but no later section uses it. §8's result is not tied back to pooling, and the drawings are elsewhere (on an unmerged pull request, per §12).
    - Severity: low.
    - Fix: move the 0.629 figure to §6 or §10. Either connect the pooling distinction to a later result, for example in §8, or cut it to a description.
    - Verified: yes.

11. **What passes.**
    - Location: overall order of §5, §7, §8, §11 and §12.
    - Assessment:
      - §5, the replicate, correctly comes before the results that use it.
      - §6 → §7 follows the arc correctly: evidence, then the method's flaw, then the fix and its evidence. Only the merge gap concept is late (finding 1).
      - §8 correctly carries the lede's "win in different places" claim right after the main results.
      - §11 limits and §12 pointers are correctly last, as residual risk and appendix.
      - The stated answer-first deviation is acceptable.
    - Severity: none.
    - Fix: none.
    - Verified: yes.

## Boundary notes

- Whether each claim is supported (role 4) and whether each slide or section reads for a stranger (role 8) I left to those roles.
- Whether the contestants or the merge gap should be figures is role 9's call. I only note that the one merge gap concept figure is mispositioned (finding 1).
