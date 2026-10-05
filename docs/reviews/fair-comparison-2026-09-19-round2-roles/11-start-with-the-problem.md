<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round2/. -->

GRANT 11 ok — Read, Grep, Glob
(I also hold SubagentHandback, which only delivers this report. I hold no Edit, Write or NotebookEdit, and I did not edit any file.)

# Role 11: argument order ("Start With the Problem")

**Artifact:** %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html (hash 16ac704)
**What I read:** the built HTML, prose, headings and captions, using Read and Grep. I also opened the full-page render at 1100px, but at display scale it only confirms the layout. I judged every order question from the text.

## The spine (one claim per section)

- **H1 + "The question":** An earlier comparison put the best net +0.103 F1 ahead of CoactDetect, but on a retired simulator with untuned nets. This run re-asks the question with both sides tuned and selection kept apart from scoring.
- **"The answer":** Once both sides are tuned they finish within 0.010 F1, and the sign turns on the merge gap, which only one side tuned. So the run does not settle which side is better. The replicate agrees no net is ahead as chosen. Binned SCE leads only by merging calls up to 30 s apart.
- **Terms paragraph:** Defines ROI, F1, GPU, *t*, Goal 1 and "project lead".
- **§1 The problem:** A coordinated event is several ROIs firing together more often than chance. Detection is hard because firing rates differ and the whole field has busy stretches. Figure 1 shows a planted event, distractors and the probe.
- **§2 Why a simulation:** Real recordings have no answer key, so the run uses a simulator fitted to real baselines. It covers two backgrounds and a 2.5 s hit rule, under which a long call hits any event inside it ("matters later").
- **§3 Contestants:** Ten detectors: four nets and six coded. `tube` is a control. The nets differ in where they stop treating ROIs separately. The architecture drawings are not on the page yet.
- **§4.1 Nested cross-validation (CV):** Settings are chosen on three outer folds and scored once on the fourth. Nets add an inner fit-and-score rotation.
- **§4.2 Fold defect:** Fold-ordered training lists made outer folds fit the same model. Dealing the recordings across folds fixed it, and this was checked before launch.
- **§4.3 Sliding mode:** Coded detectors start from Goal 1's sliding-mode values, because the project defaults (binned) would tune them in their weaker mode.
- **§4.4 Two selections:** Choosing on F1 alone rewards calling more. So every contestant is also chosen under a false-alarm budget of 1.6 times CoactDetect's rate.
- **§4.5 Merge gap:** One setting was not shared. Coded detectors tuned their merge gap; the nets' stayed at 2 s. On this bench a wide gap is free, but on real recordings it fuses events. Figure 5B gives held-out F1 against gap, and a crowded-recording check was applied after the run.
- **§5 Replicate:** Four folds give only 3 degrees of freedom, so a second workstation ran the same comparison on disjoint seeds.
- **§6 Results:**
  - The *t* values overstate the evidence, and the corrected ones rank consistency rather than test it.
  - At the chosen settings, no net beats CoactDetect.
  - With the merge gap matched, the order reverses.
  - Tuning moved some nets and not others. The earlier lead is gone, but three changes are confounded.
  - Binned SCE's first place comes from its merge gap.
  - Under the budget, four coded detectors have no admissible result.
  - Two refits failed to train, and some choices exceeded the budget on new data.
- **§7 Limits:** Baseline and fast stream only; contamination; one bench value outside its interval; simulation only; merge gap tuned on one side; nets not crowd-checked; unequal data; four folds; one-at-a-time search; choices at the top of the grid; `min_rois`; one GPU.
- **§8 Where everything is, and Provenance:** Locations of files and code.

## Arc I judged against

The default analysis arc (problem → cost → method → what the method gets wrong → fix → evidence → residual risk) holds up here, with the owner's brief as the ordering constraint: concepts first, "before showing a number". Mapped onto the report:

- **Problem and cost:** the earlier +0.103 claim rested on an unfair comparison (lede).
- **Method:** §1–§4.4.
- **What it gets wrong:** the fold defect (§4.2) and the unshared merge gap (§4.5).
- **Fix:** the dealing fix; re-scoring at matched gaps.
- **Evidence:** §6 and the replicate.
- **Residual risk:** §7.

The body follows this arc well. The brief's six concepts arrive in the order asked, each after what it depends on:

- coordinated events: §1
- the simulator: §2
- nested CV and the fold defect: §4.1–4.2
- sliding mode: §4.3
- the two selections: §4.4
- the replicate: §5

**Cold open.** The reader first sees the title question, then "The question" paragraph. The problem it opens on is that the earlier comparison may have been unfair, and that is the right problem. The first figure (Figure 1) comes in §1 and shows what the detection problem looks like, which is also right. The defects are in where specific claims land, not in the overall shape.

## Findings

1. **The lede, "The answer" paragraph.**
   - **Issue:** The answer puts numbers and undefined concepts in front of the reader before the report has explained anything. Its intelligible position is after §4.5 (or at least after the Terms paragraph).
     - Numbers: 0.010, 0.007, +0.010 with 4 of 4 folds, +0.009, 30 s.
     - Concepts: F1 (defined in the *next* paragraph), folds, merge gap, binned SCE, chorus_norm, "a second draw".
     - This is a bottom-line-up-front (BLUF) deviation. It is defensible, but the page never states it, and it contradicts the brief's "conceptually ... before showing a number".
   - **Severity:** medium.
   - **Fix, one of two:**
     - (a) Reduce the answer to one or two plain-language sentences with at most one number: "tuned fairly, the two sides finish in a near-tie, and which is ahead depends on a setting only one side was allowed to tune". Move the per-gap figures to §6.
     - (b) Keep it, but put the Terms paragraph *above* it and add a line: "The answer comes first; sections 1–5 explain every term in it."
   - **Verified:** yes (lines 39–57: the answer precedes the Terms paragraph).

2. **§4.5 sits inside "4. How the comparison was kept fair".**
   - **Issue:** §4.5 is the one place the comparison was *not* fair, and it is the pivot of the whole answer. Yet it is filed as the fifth fairness device, and it reports results before the results section:
     - CoactDetect 0.731 / 0.748 / 0.803 at 2, 8 and 30 s;
     - chorus_norm 0.741 / 0.775;
     - Figure 5B, held-out F1;
     - a check applied after the run.
     These results come before §6 has told the reader how to read them, before the headline (Table 2), and before the replicate is introduced. §6 then points back to Figure 5 panel B for binned SCE's 0.587, so the reader has to scroll back. In the default arc, this is "what the method gets wrong" plus its evidence, crammed into the method slot.
   - **Severity:** high. It is the claim the lede says the answer turns on.
   - **Fix:** Pull 4.5 out of §4 into its own section, placed after §6's headline bullet ("At the settings chosen, no net is ahead"). Title it for what it is, for example "Where the two sides were not treated alike: the merge gap". The order becomes headline → the unequal setting → matched-gap reversal → binned SCE. Keep the merge-gap *concept* (the Figure 5A schematic, the hit-rule consequence) early if wanted, as one paragraph in §2 next to the hit rule, which already foreshadows it with "matters later". The Figure 5B data and all F1 numbers belong after the headline.
   - **Verified:** yes (lines 192–223, 276–278).

3. **§6, the replicate's verdict.**
   - **Issue:** The report calls the replicate "the stronger check" (line 247), but §6 never states its outcome in prose. It appears only as orange diamonds in Figure 8 and a caption reference.
   - A second problem: the lede says the replicate "was not re-scored at matched gaps (section 5)". Neither §5 nor §6 says that. The only place the claim appears is the lede, and its section pointer goes to text that does not contain it.
   - So the report's strongest evidence has no claim of its own in the spine.
   - **Severity:** medium.
   - **Fix:** Add a §6 bullet directly after the matched-gap bullet: "On the second draw, [verdict at chosen settings]; it was not re-scored at matched gaps, so the reversal above is unreplicated." Point the lede's reference at that bullet rather than at §5.
   - **Verified:** yes (grep: "matched" occurs only at lines 44, 48 and 263; "re-scored" only at line 48; the replicate's prose mentions are lines 116, 226–234, 247 and 262).

4. **§6 bullet 3 and §7: the report never directly answers its own opening question.**
   - **Issue:** The opening question is whether the earlier +0.103 lead survives fair tuning. The direct answer is that the lead is gone, but three changes are confounded: the new simulator, CoactDetect's sliding values, and the tuning. That answer arrives only as the tail of the *third* results bullet. It is absent from the lede and absent from §7 Limits.
   - As ordered, the lede reads as though fair tuning closed the gap. The residual-risk slot of the arc is missing its most relevant entry.
   - **Severity:** medium to high. Boundary: whether the claim is *supported* belongs to agent 4; I am flagging that it arrives in the wrong place and not at all where the reader judges the answer.
   - **Fix:**
     - Add one sentence to the lede's answer: "The earlier lead is gone, but three things changed at once and this run cannot say which removed it."
     - Add a §7 Limits item for the confound.
     - Promote the bullet within §6, or split it: the "which of three changes" point first, the per-net tuning deltas after.
   - **Verified:** yes (lines 274–275; the Limits list at lines 307–342 has no such item).

5. **§6 opens with two paragraphs on the *t* correction.**
   - **Issue:** §6 begins with two paragraphs on the Nadeau–Bengio correction, Bouckaert & Frank, and Bengio & Grandvalet, before any result is shown. The caveat arrives before the numbers it qualifies, so the reader has to hold it in suspense. Its content is methods: it follows from the fold sharing set up in §4.1.
   - **Severity:** low.
   - **Fix:** Move the derivation and citations to the end of §4.1 or into a note under Table 2. Keep one sentence at the head of §6: "the *t* values rank consistency; they are not tests; see §4.1".
   - **Verified:** yes (lines 239–248).

6. **§1 → §2: a small inversion.**
   - **Issue:** §1 uses simulator vocabulary through Figure 1 before §2 says why a simulation is used at all: "one *simulated* recording", "planted event", distractors, the probe, and "labeled a negative".
   - **Severity:** low.
   - **Fix:** Move §2's first sentence ("A real recording has no answer key ... every planted event is known") to the start of Figure 1's introduction in §1, or state in §1 that the example is simulated because only simulation gives an answer key.
   - **Verified:** yes (lines 67–82).

7. **§3, the architecture-drawings warning box.**
   - **Issue:** A "not on this page yet" status notice sits in the middle of the case, in the contestants section. It has no job in the argument.
   - **Severity:** low.
   - **Fix:** Move it to §8 Where everything is, or to §7 Limits. Leave one line in §3 pointing there.
   - **Verified:** yes (lines 114–117).

8. **§6, the subsections "Refits below 0.2 F1" and "Choices that exceeded the budget on new data".**
   - **Issue:** These are audit detail placed after the results argument and before Limits. They support the robustness of the means but do not advance the case. Acceptable where they are, but they read as an appendix.
   - **Severity:** low (optional).
   - **Fix:** Move them under a "Checks on the results" heading after §7, or keep them and label them as checks.
   - **Verified:** yes (lines 291–303).

## Positions checked and passing

- §4.2 (fold defect) follows §4.1, which defines the folds and training seeds it depends on.
- §4.3 and §4.4 each state their "why" before their "what".
- §5 (replicate design) precedes the results that use it.
- §2 foreshadows the hit-rule consequence that the merge-gap argument needs.
- §7 and §8 are correctly last.
- Every section's job: problem (1), answer key (2), who competes (3), fairness devices (4.1–4.4), replication design (5), evidence (6), residual risk (7), locations (8). Only the items in findings 2, 5, 7 and 8 are mispositioned.
