GRANT 11 ok — Read, Grep, Glob

# Argument-order review: `docs/learned/slow_comodulation/README.md`

The middle of the page is in the right order: definitions, then the method, then the method tested where the answer is known, then the recordings. The page stated that order itself, though only after its findings. Four problems break the case:
- **The opening shows a results chart, not the problem.** Figure 1 uses terms that aren't defined until much later.
- **The page never states its answer near the top.** The question that prompted it (were rigid-shift-trained models learning slow drift?) is answered plainly only in "What this changes for the label-free thread".
- **The main measurement is never explained in the method sections.** That measurement is the count-variance ratio.
- **The group check comes after the conclusions.** Pooled numbers are not admissible without it (FOUNDATIONS §9), yet the conclusions are drawn from them first.

This needs moving and a few added sentences, not a rewrite.

## Spine: one claim per section

| # | Section | Claim | Job in the argument | Earliest point it makes sense |
|---|---|---|---|---|
| 0 | "Why this page exists" box | A detector trained against rigid shift is paid for whatever the shift destroys. Whether that includes slow shared rate change is an open decision, and this page measures it. | The problem | First. **In place.** |
| 1 | What the page finds, with Figure 1 | On the lab fast stream the onset count swings about 3× chance at 1 minute. Rigid shift leaves almost all of it, and it is not CoactDetect's events. Slow-stream swings are mostly events. Dard et al. and the generator swing more. So where does minute-scale shared rate change belong? | Bottom line | Only after the surrogates section: it needs block control, circular shift, CoactDetect and the count-variance ratio. **Too early as written.** |
| 2 | Two ways ROIs are active together | Coordinated events and shared modulation both light more ROIs than chance. A detector that counts lit ROIs responds to both, so what rigid shift does to modulation decides whether the detector is paid for it. | Defines the problem and its terms | Needs nothing earlier. **Should come before Figure 1.** |
| 3 | Telling them apart: the cross-correlogram, with Figure 2 | Events make a narrow peak. Shared modulation makes a broad shoulder, plus some sub-second excess. The measure cannot see change spanning the whole window. | Method | After "Two ways". In place. |
| 4 | What the surrogates remove, with Figures 3 and 4 | Rigid shift spreads events out and removes only modulation faster than about *J*. The block control keeps any shared change in 2-minute counts, events included. The generator has a minute-long shoulder that no rigid shift touches. | The method tested where the answer is known | After the correlogram section. In place. |
| 5 | What the recordings hold, with Figure 5, the dip readings and the numbers table | Every dataset has a sub-second peak. Lab fast and Dard et al. keep minute-scale excess that rigid shift leaves. The slow-stream shoulder mostly goes with the events, which are followed by a dip of unknown cause. | Evidence | After the surrogates section. In place, but uses CoactDetect, which is defined only here. |
| 6 | What this changes for the label-free thread | On lab fast, the rigid-shift contrast was mostly not paid for minute-scale drift (a 10–45 s part is not bounded). On slow it is paid for events and what follows them. The simulated training data hold a block that rigid shift also keeps. A small *J* is not a modulation control. `count_excess` removes drift by construction. | Consequence (the cost) | After the recordings and the group split. Recordings: yes. Group split: no. |
| 7 | The decision this sets up | Whether minute-scale shared rate change is coordination, background, or the producer's to explain can't be settled from these data: its source is unknown, and nobody has asked the producer. | Decision | After the consequences. In place, but it **repeats** the end of the findings section. |
| 8 | What this does not settle | Caveats: whole-window baseline, how removal misses or over-removes, synthetic depth, the two folders differ, baseline only. It also says pooled numbers are inadmissible until Figure 6 "below". | Residual risk | End. In place. |
| 9 | By group, with Figure 6 | The pooled result is not one group's, and group can't be separated from imaging day. | Makes the pooled numbers admissible | Straight after the recordings section. **Misplaced: it comes after the conclusions.** |
| 10 | Published lineage | Shared rate change posing as synchrony is a known problem (Perkel 1967, Brody 1999). The surrogates correspond to dithering and interval jitter. | Background and sources | Appendix. In place. |
| 11 | Reproduce | Commands and what the tests cover | Appendix | End. In place. |

## Arc used

For an explainer that ends in a decision rather than a fix, I adapted the default arc to: **problem → what it looks like and what to call it → a method that can see it → the method tested where the answer is known → evidence from the recordings → the check that makes that evidence admissible (by group) → what it costs the thread → the decision → what is left unsettled → appendices.**

The page runs a bottom-line-first version of this. That is a defensible choice, but it is only half stated: the roadmap sentence (lines 55–57) comes after the dense findings and names only four of the later sections.

## The opening

**What the reader sees first:** the title, then the "Why this page exists" box, which states the problem correctly but in abstract terms. The first visual is **Figure 1**: four panels of bars with four surrogate types, on a log scale. Its caption says those surrogates are "each defined below".
- Block control and circular shift are defined in Figure 3's caption.
- CoactDetect is defined in Figure 5's caption.

**Is that the problem?** No. It is the result. What slow co-modulation looks like is shown first in Figure 2 (panels B, C, E, F) and Figure 3, and only on synthetic recordings. No lab recording's population count over time appears anywhere. Whether one should is a figure question for role 9, but it bears directly on what this page should open with.

## Findings

**1. The page opens on a results chart the reader can't yet read**
- **Where:** "What the page finds": Figure 1, its caption and the four bullets (lines 15–48).
- **Issue:**
  - Figure 1's legend and caption use rigid shift *J*, block control, circular shift and "CoactDetect episodes removed". Only rigid shift is even named before this point.
  - The lab-fast bullet quotes a paired difference, a per-recording median, the share of recordings above 1, and a figure with the top five recordings dropped. These robustness checks can't be judged before the reader knows what the arms are.
  - The problem itself (what shared modulation looks like, and why rigid shift keeps it) arrives only with Figures 2 and 3.
- **Severity:** High.
- **Fix:**
  - Move "Two ways ROIs are active together" ahead of the findings.
  - Open on the phenomenon: Figure 2's top two rows, or a lab fast recording's onset count over its baseline next to its rigid shift. The second doesn't exist yet; raise it with role 9.
  - Replace the findings with a 3–4 sentence answer in plain terms.
  - Make Figure 1 the headline of "What the recordings hold". If it has to stay first, cut it to "as recorded" and "rigid shift" and move the robustness numbers down.
- **Verified:** yes.

**2. The answer to the question that prompted the page isn't at the top**
- **Where:** the findings section (lines 27–54) compared with "What this changes for the label-free thread" (lines 264–270).
- **Issue:** The worry was that rigid-shift-trained models may be learning slow shared modulation rather than coordination. The plain answer only appears in the implications section:
  - On lab fast, change at a minute or more "was at most a small part of the contrast", and a 10–45 s component is not bounded.
  - On slow, the contrast rewards events and what follows them.

  The opening goes from measurements straight to the decision and never says what they mean for the trained models.
- **Severity:** High.
- **Fix:** Add one bullet to the opening that states the consequence for the models on each stream, including the part that is not bounded.
- **Verified:** yes.

**3. The main measurement has no place in the method sections**
- **Where:** Figure 1's caption (line 20), "Telling them apart" (lines 81–114), Figure 4 (line 129), Published lineage (lines 355–356), and the lab fast bullet in "What the recordings hold" (lines 183–185).
- **Issue:**
  - The count-variance ratio drives the title claim, the table and the "a tenth of the 1-minute excess" consequence, but it is defined only in Figure 1's caption.
  - The method section introduces only the correlogram. The roadmap promises "a measurement" (singular).
  - Figure 4 tests only correlograms on the synthetic recordings, so the reader never sees how the count variance behaves where the answer is known.
  - The link between the two measures (the correlogram integrates to count covariance) appears only in the lineage appendix.
  - The recordings section then calls the Figure 1 count variance "the evidence that can fail". So the deciding measure is the one the method never introduced.
- **Severity:** Medium-high.
- **Fix:**
  - In "Telling them apart", add a paragraph saying that count variance at bin width *T* is roughly the population correlogram summed out to lags near *T*: one number per timescale for the same shoulder.
  - Add count-variance values for the three synthetic recording types to Figure 4, or give them as a short table.
- **Verified:** yes (the text, and Figure 4 opened).

**4. The group check comes after the conclusions drawn from pooled numbers**
- **Where:** "By group" (lines 330–346), and its pointer at line 327.
- **Issue:** "By group" comes after "What this changes", "The decision this sets up" and "What this does not settle". The caveats themselves say pooled numbers are "not admissible on their own" (FOUNDATIONS §9, `docs/FOUNDATIONS.md` lines 382–384). So the consequences and the decision are argued from pooled numbers before the reader sees the check that makes them admissible.
- **Severity:** Medium-high.
- **Fix:** Move "By group" to straight after the recordings section's numbers table, before "What this changes". Change the caveat's "below" to point back up.
- **Verified:** yes.

**5. The decision is stated twice, and the part that makes it actionable is in the later copy**
- **Where:** lines 50–54 and the section at lines 286–298.
- **Issue:** The second copy adds what Tony needs in order to act:
  - the source is unknown (network state, or focus, bleaching, or baseline estimation);
  - the Dard et al. authors tie activity to movement;
  - nobody has asked the producer (flagged ⚠).

  The first copy is what a reader who stops early takes away.
- **Severity:** Medium.
- **Fix:** State the decision once. Either put the "source unknown; producer not asked" ⚠ in the opening and turn the later section into a pointer, or cut the opening copy to a one-line pointer to the full section.
- **Verified:** yes.

**6. The Dard et al. dataset is compared at the top before the reader knows it's a different preparation**
- **Where:** line 43 ("swings most"). Its preparation is described only at line 61, lines 164–165, line 212, lines 320–323 and line 369.
- **Issue:**
  - Line 43 ranks it against the lab slices.
  - The one place terms are defined ("The recordings are calcium imaging of hippocampal slices", line 61) describes only the lab folder.
  - That the dataset is in vivo imaging of mouse pups, with a different extractor and a different definition of onset, comes out only in Figure 5's caption and the caveats.

  So the reader can't judge the ranking where it is made.
- **Severity:** Medium.
- **Fix:** Introduce both folders in "Two ways ROIs are active together". At the first mention, add "in vivo imaging of CA1 in mouse pups, a different extractor".
- **Verified:** yes.

**7. The removal arm that the lab claims rest on is introduced in the evidence and never tested where the answer is known**
- **Where:** CoactDetect is first used at line 23, defined in Figure 5's caption (lines 165–170) and relied on at lines 315–316.
- **Issue:** The caveats say "the lab claims rest on the arm that removes episodes first". That arm:
  - is defined inside a figure caption in the recordings section;
  - is absent from Figure 3, the surrogate schematic;
  - is absent from Figure 4, the tests on synthetic recordings.

  So the deciding control shows up for the first time on real recordings.
- **Severity:** Medium.
- **Fix:** Define "CoactDetect episodes removed, then block control" in "What the surrogates remove", alongside the other arms. Show it on the planted-event and 5-minute synthetic recordings in Figure 4, and leave only the parameters in Figure 5's caption.
- **Verified:** yes (the text, and Figures 4 and 5 opened).

**8. The slow-stream dip digression sits in the middle of the evidence**
- **Where:** "Why the slow stream dips — three readings, none tested" (lines 198–213).
- **Issue:** The digression is about extractor dead time or quiet periods after events, not slow co-modulation. Its only job in the argument is to support the implications bullet that the slow-stream contrast "rewards the events and their aftermath". Where it sits, it breaks up the recordings evidence before the numbers table.
- **Severity:** Low.
- **Fix:** Give it its own heading, marked as an aside, after the numbers table (or after "By group, once that section has moved"). Link it from the implications bullet.
- **Verified:** yes.

**9. The roadmap comes after the dense findings and leaves out sections**
- **Where:** lines 55–57.
- **Issue:** The findings-first structure isn't announced until the reader has already got through it. The sentence also omits the consequences, the decision and the group check.
- **Severity:** Low.
- **Fix:** Move the order statement into the "Why this page exists" box or to the start of the findings, and name every section it leads through.
- **Verified:** yes.

**10. *J* = 1.6 s appears with no reason for choosing it**
- **Where:** line 141 and the Figure 4 and 5 legends. The reason comes at line 273.
- **Issue:** The 1.6 s arm first appears in the synthetic tests. Why it is there (a small displacement is not a modulation control, and it is the low end of the window where rigid shift hides on Dard et al.) arrives only in the implications section.
- **Severity:** Low.
- **Fix:** In "What the surrogates remove", add one clause saying why 1.6, 10 and 20 s were chosen.
- **Verified:** yes.

**11. The fact that this is a known problem is held back until the appendix**
- **Where:** Published lineage (line 350).
- **Issue:** "The phenomenon is old" frames the problem: shared rate change looking like synchrony is a documented confound (Brody 1999). It would help the opening persuade, and at the end it does nothing for the argument.
- **Severity:** Low.
- **Fix:** Add one sentence with the citation to the "Why this page exists" box, and keep the full lineage where it is.
- **Verified:** yes.

## Checked and left alone
- Figure 2 comes before Figures 3 and 4, and the correlogram is explained before any surrogate is applied to it. Correct.
- Tests on synthetic recordings come before the recordings. Correct.
- The caveats come after the decision.
- The lineage and reproduction sections are appendices at the end.
- The whole-window caveat appears twice (lines 112–114 and 302–303). The first sits where the method needs it, and repeating it in the caveat list does no harm to the order.

## Files
- <worktree>/docs/learned/slow_comodulation/README.md (reviewed; Figures 1, 2, 4 and 5 opened)
- <worktree>/docs/goals/unsupervised-learning.md (line 58)
- <worktree>/docs/learned/tube_self_supervised/README.md (lines 387–398)
- <worktree>/docs/FOUNDATIONS.md (lines 382–384)
