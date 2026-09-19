GRANT 11 ok — Read, Grep, Glob

Role 11, argument order ("Start With the Problem"). Blind verify, round 3 of 3.
Artifact: %USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html (hash-object 9a99a7a4…). I read the headings and paragraph openings with Grep, read the full text of the paragraphs where order depends on them (lines 112–124, 165–169, 227–236, 279–285, 355–359), and looked at all 14 rendered slices, light_1100_00 to light_1100_13. I did not open any earlier review report.

## 1. The spine: one claim per unit

- **0a. Subtitle.** The question: can a lead of about 0.01 in F1 between a learned and a coded detector be told apart from the luck of which recordings were drawn? A second draw on unseen recordings answers it, within stated limits.
- **0b. "Why this report exists."** A rehearsal put two nets slightly ahead. One run cannot measure how much a result moves when only the recordings change, and a keep/drop decision depends on it, so the comparison was run twice. It gives a roadmap: sections 1–5 explain the comparison, section 6 onward is what the second draw adds.
- **0c. Answer box.**
  - Changing only the recordings moves a score by about 0.01.
  - Under the budget, every net trailed CoactDetect by 2–3 times that move.
  - Part of the shortfall is the merge setting.
  - Training failures pull two nets down.
  - Limits: no drugs, no slow stream, no real recordings, and a simulator fitted to a folder with a known defect.
- **§1.** Finding coordinated events is hard because events recruit few cells, independent firing makes chance coincidences common, and dense stretches mimic events (Figure 1).
- **§2.** Truth is unknown on real recordings, so the comparison uses a simulator that keeps an answer key. The section defines the bench, call, match, merge and F1, and gives the practical ceiling of 0.83.
- **§3.** The contestants: six coded detectors with CoactDetect as the reference, and four nets, with tube as the control for tuning inflation.
- **§4.** Nested cross-validation keeps the held-out scores honest. The fold defect was fixed before either run.
- **§5.** Each entry is chosen two ways: on F1 alone, and under a false-alarm budget anchored to CoactDetect. The section also says what the budget does not police.
- **§6.** The rehearsal's lead (+0.011 and +0.016) came from a flawed setup. The corrected comparison was run twice on disjoint seeds, and nothing else changed.
- **§7.** The per-draw results: CoactDetect scores 0.748 in both draws, and binned SCE leads on F1 alone in the first draw.
- **§8.** The runs carry things besides skill: failed training, searches that found no admissible setting, held-out breaches of the budget, and merge settings pinned at the top of their grid.
- **§9a.** The unflagged entries move a median of 0.010 (nets) and 0.006 (coded) between draws. That is the scale any lead must beat, and the rehearsal's lead was within it.
- **§9b.** Under the budget, every net is below CoactDetect in every fold. chorus_gain_norm trails by 0.030 and 0.025, which is 2–3 times the typical move.
- **§9c.** Matching the merge closes 28–57% of that gap under the budget, and the rest survives. On F1 alone, the chorus models lead.
- **§9d.** The as-run gap is in precision: more false alarms outside the dense stretch.
- **§9e.** Tuning's gain for line_length is real but small. For chorus_norm it cannot be separated from failed training.
- **§10.** The limits, with the two commissioned ones first. Table 7 lists where the two sides were not treated alike.
- **§11 and References.** Provenance and sources. This is appendix material and sits at the end, where it belongs.

## 2. The arc I used, and how the report maps to it

I used the default analysis arc: problem → what it costs → method → what the method gets wrong → fix → evidence → residual risk. The report maps onto it as follows:
- **Problem:** the subtitle's question and §1.
- **Cost:** 0b, because a keep/drop decision depends on the answer.
- **Method:** §2–5.
- **What the method gets wrong:** §6, since one run cannot measure between-draw variance and the rehearsal was flawed.
- **Fix:** the second draw (§6, Figure 5).
- **Evidence:** §7–9.
- **Residual risk:** §10.

There is one deviation: the answer box comes before the method (bottom line up front). The report states it, through the label "The answer, in plain words" and the roadmap sentence in 0b, so it is not a defect in itself (but see finding 5).

## 3. The cold open

The first thing the reader sees is the subtitle, and it is the report's problem stated as a question. Then comes the reason the question matters, then the answer. The first figure (Figure 1, the raster) is on the first screen after the answer box, and it shows what the domain problem looks like. That suits a reader new to the project, which is who the commission names.

The picture of the report's own statistical problem is Figure 8, the between-draw moves. It sits in §9, and I judged that placement correct: Figure 8 cannot be read before entries, selections and flags have been introduced (§5 and §8). The cold open is clean.

## 4. Findings

Each finding is given as location, issue, severity, fix, and whether I checked it against the source.

**1. §7 (line ~245) and §8 "Settings at the top of their grid" (line 280), against §9c "At a matched merge" (lines 319–321).**
- **Issue:** Two sections claim "Binned SCE's first-draw lead may be the bench rewarding a long merge", and neither can support it where it is made. The only evidence that a longer merge scores better on this bench is CoactDetect's own F1 rising from 0.733 at 2 s to 0.748 at 8 s and 0.797 at 30 s. That appears only in §9c, one to two sections after the claim. At the point of the claim, the reader has only the §2 argument that a long merge hides distractors, with no size attached.
- **Severity:** minor.
- **Fix:** Move the sentence with 0.733 → 0.748 → 0.797 into §8's grid-top subsection, beside binned SCE's 30 s grid top. §9c can then point back to it.
- **Checked against source:** yes (lines 280–285, 319–321).

**2. §3, the tube bullet (lines 168–169), against §9e "Tuning" (lines 356–359).**
- **Issue:** §3 sets tube up as "the project's control for tuning inflation … if tuning lifts it clear too, the gains are about the tuning budget". §9e, the section that judges tuning's effect, discusses line_length and chorus_norm and never mentions tube. The setup has no payoff, so the reader carries the question to the end unanswered. Table 1 holds the numbers: tube goes from 0.629 untuned to 0.631 on F1 alone in the first draw, and from 0.651 to 0.646 in the second.
- **Severity:** minor.
- **Fix:** Add one sentence to §9e giving tube's untuned-to-tuned change and what it says about tuning inflation. Otherwise, drop the "control" framing from §3.
- **Checked against source:** yes (grep for "control for tuning" finds only line 168; §9e text read in full).

**3. §9c "At a matched merge" placed before §9d "Where the as-run gap is".**
- **Issue:** The two subsections run cause before symptom. §9d finds that the gap is in precision, from extra false alarms outside the dense stretch, and that the score files cannot say whether those fell on distractors. That is exactly the question the matched-merge test answers, because a short merge leaves distractors unhidden. In the current order, the decomposition (9c) comes before the localization that motivates it (9d), and 9d never links back to the merge.
- **Severity:** minor.
- **Fix:** Swap 9c and 9d, so the order is gap → where it is (precision, outside the dense stretch) → how much of it is the merge. Or keep the order and add a bridging sentence at the end of 9d.
- **Checked against source:** yes (rendered slices 09–11).

**4. Table 7, first cited in §3 (line 165, "each coded detector instead tunes its own merge (Table 7)") but placed in §10 (line 391).**
- **Issue:** A reader in §3 is sent forward seven sections. The table is mostly method facts (recordings behind a choice, one threshold carried across refits, a budget anchored to CoactDetect, tuning before this comparison). A reader needs those facts to weigh §9's net-versus-CoactDetect comparisons, and the table becomes readable at the end of §5, but it only arrives after §9.
- **Severity:** minor.
- **Fix:** Place Table 7 at the end of §5 and keep the §10 bullet as a back-reference ("Table 7, section 5"). If it stays in §10, drop the forward pointer from §3.
- **Checked against source:** yes (lines 165, 375, 391).

**5. Answer box, bullet 2: "in every fold of both draws".**
- **Issue:** The box comes before §1–5, and it glosses F1, the reference detector and the false-alarm cap inline. "Fold" is the one load-bearing term it does not gloss, and it is not defined until §4. The commission asks for concepts before numbers. The box is a stated exception to that, but this term arrives before the reader can evaluate it.
- **Severity:** minor.
- **Fix:** Replace it with "in every held-out quarter of the recordings, in both draws", or drop the phrase from the box and leave it to §9b.
- **Checked against source:** yes (slice 00; §4 at line 187 is where "outer folds" is defined).

**6. §7 opening prose (line 239 onward).**
- **Issue:** The section holding the main evidence (Figure 6, Table 1) opens with side points: CoactDetect's stability, then binned SCE's lead. It does not say where the report's question is visible, which is the nets against CoactDetect in Panel C. §7 earns its position as the evidence container, but its prose points the reader away from the claim the evidence supports.
- **Severity:** minor.
- **Fix:** Open §7 with one sentence that sends the reader to Panel C, where the nets against CoactDetect under the budget carry the headline that §9b quantifies. Then give the CoactDetect and binned SCE observations.
- **Checked against source:** yes (slice 05).

## 5. Checked and found clean

- **Motivation before what it motivates.** Section 6 ("Why two draws") needs §4, because it cites the fold defect, and §5, because it cites the older budget. It sits right after §5, which is the earliest point it can be read. Its gist is also given in 0b, so the motivation is never missing up front.
- **§8 before §9.** §9a's medians exclude flagged entries ("Among entries with no flagged fold"), so the flags in §8 have to come first, and they do. This is "what the method gets wrong" coming before the claims, and it is justified.
- **Order inside §9.** The between-draw scale (9a) comes before the headline gap judged against it (9b). The gap comes before its decomposition (9c). The evidence in every subsection follows its claim.
- **Answer box order.** It matches the body order, except that it puts training failures after the gap (the body puts them before, in §8). That difference is harmless.
- **The commissioned limits.** They are stated three times, in the right places: the subtitle ("simulated recordings only, untreated activity only, one of the lab's two event streams"), bullet 5 of the answer box (which names the defect), and the first two bullets of §10.
- **The commissioned "what the pair can claim".** It has its own section, and that section comes after everything it depends on.
- **Every unit has a job in the spine.** §11 and References are appendix material at the end. No mid-argument unit lacks a job.
- **The §2 ceiling.** The practical ceiling of 0.83 is defined in §2, before Figure 6 draws it as a dotted line.

**Outside my role (noted only for the boundary):** the Figure 2 placeholder in §3 ("Architecture drawings: to come") is a craft and mechanical question for roles 9 and 10. I also noticed that tube, described in §3 as having "tied CoactDetect in an earlier comparison", is far below CoactDetect here. Whether that claim is supported is for role 4.

## 6. Verdict

The order argues the case, and I found no blocking or major defect. The report opens on its question, gives the answer, builds the method in the order each piece is needed, and motivates the second draw at the earliest point it can be read. It isolates the confounds before the pair claims that exclude them, and ends with the commissioned limits. The six findings are minor. Three are local re-sequencings (1, 3, 4); one is a setup with no payoff (2); two are small fixes to what the reader is told before they can use it (5, 6).
