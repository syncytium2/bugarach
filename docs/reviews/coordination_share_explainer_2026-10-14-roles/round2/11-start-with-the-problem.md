GRANT 11 ok — Read, Grep, Glob

(SubagentHandback is the hand-off channel. I hold no Edit, Write or NotebookEdit.)

**What I reviewed.** I read only the order. Artifact: `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md`. I opened Figures 1 and 5 to state their claims correctly. ADR-0014 points 1–4 govern this page, which is an explainer, so the figures-first layout is taken as given and was not reviewed.

## Spine: one claim per figure

- **F1. The count.** In the window count, a shared moment shows as a column of ticks and a tall bar. A shifted copy removes the columns but keeps each cell's ticks.
- **F2. Same mean, wider spread.** The recording and its shifted copy have the same mean count. Only the recording has a wide tail, and the excess *f*₂/*f*₃ is what the measure keeps.
- **F3. Planted vs recovered.** The medians pass ±25% on all three sets. The fixed model reads 5–18% low.
- **F4. Window and intervals.** The share barely moves with window size, except for moments closer together than a window. Participants per moment and moments per minute move a great deal.
- **F5. What else it counts.** With nothing planted, a sharp field-wide rate change is counted as coordination, most when the stretch is short. Slow drift and each cell's own clumping are removed.
- **F6. One recording.** A single recording strays widely, more so with few moments. Pooling does not steady it.

## Spine: one claim per text section

1. **The question.** The measure never defines a coordinated event. Implicitly it counts onsets in several cells in one window, beyond chance, arriving faster than the field's rate changes, and the last condition is where it is fooled. It is fireflies' measure. Everything shown is simulated, and the real numbers are withheld.
2. **Terms.** Vocabulary only, no claim.
3. **Step 1.** Coordination shows in the spread of the window counts, not their mean, and *f*₂/*f*₃ measure the excess spread.
4. **Step 2.** Chance is measured with per-cell shifted copies. These keep each cell's rate and rhythm and destroy co-timing.
5. **Step 3.** *f*₃/*f*₂ gives *k*, *f*₂ gives λ, and together with the event rate they give the share. The ratio is pooled across recordings.
6. **Does it get the right answer? (check and models).** The medians pass. The fixed model reads low by an amount that depends on how much moment sizes vary, which is unknown in real data. It was adopted to match the bench, not for accuracy.
7. **Window size.** Same claim as F4. In addition, participants per moment and moments per minute fall outside ±25% on every set.
8. **What else it counts.** Same claim as F5.
9. **How far one recording strays.** Same claim as F6, plus the tool's limits on which recordings it uses.
10. **The simulated recordings.** How the sets were built: quiet and busy backgrounds, the mixed set, the bench set.
11. **Where the method comes from.** CuBIC, the multiple-interaction process (MIP) model and shift surrogates come from the literature; the listed parts are this project's own.
12. **What waits.** The real numbers are withheld under the contamination stop, and the bench is to be revised.
13. **For developers.** Code pointers and formulas.

## Arc used

For a measure explainer there is no "fix", so I adapted the default arc to: question → its answer → mechanism → evidence it works → what it gets wrong → per-recording risk → provenance → what waits. This is a stated deviation from the default. The figure order (1–6) and the text order follow this arc, and the figures are numbered in the order the text first discusses them. **The overall spine is sound.**

## What the reader sees first

The title, which already poses the problem ("…counted without defining a coordinated event"), and then Figure 1, a raster in which co-timed columns and the tall window-count bars are visible. The planted lane is the thing "the measure never sees". This is a good cold open for this question: it shows what the measure looks at instead of a definition. The first text section opens on the question and states the weakness and the "all simulated" caveat up front. I have no cold-open finding.

## Findings

Each finding gives: location · issue · severity · suggested fix · could I verify it against a source.

1. **Section 10, "The simulated recordings" (after all results) vs Figures 2–6 and text sections 6–9** · Terms the results depend on arrive only after those results:
   - "quiet" and "busy" background (used in the F2 legend, §8 "13 times quiet", §9 "¼ quiet")
   - the "mixed" set and "120 s only" (F4 legend, §7)
   - "15 moments of 10/6/3 cells" (needed to read F6 "15 / 6 / 3 moments")

   A reader cannot evaluate §§6–9 until §10, which is unstated forward dependency.
   · **Medium-high** · Open "Does it get the right answer?" with a 3–4 sentence summary of the sets (32 cells, 45 min; quiet = 0.0049 and busy = 0.0169 onsets/s/cell; 15 moments of 10/6/3 cells; mixed = 2 close + 2 medium pairs + 7 singles). Keep the full detail where it is.
   · Verify: yes, against the README text.

2. **Step 3 (line 100–102) vs §9 (lines 204–207)** · Step 3 says *f*₃ is noisy "so the tool pools… Figure 6 shows what that does". This leaves the impression that pooling fixes per-recording noise. The result that contradicts it ("pooling steadies the median, not the single recording") arrives about 100 lines later, so the reader carries a wrong belief through three sections.
   · **Medium** · State the outcome where pooling is introduced, e.g. "…which steadies the median across recordings but not any single recording (Figure 6)".
   · Verify: yes.

3. **§6, "The check, and the two models" (line 116 vs lines 137–140)** · "The tool adopts the fixed model" comes before the bullets in which the binomial model is closer on 2 of 3 sets. The reason for adopting it ("matches the bench, not accuracy") and the cancellation explanation come two paragraphs later. The reader meets the decision before they can judge it, and meets the numbers that seem to argue against it before the explanation.
   · **Medium** · Move the adoption rationale up next to the adoption sentence, or lead the section with its conclusion: "medians pass; the fixed model reads 5–18% low, by an amount set by size variance; read it as an underestimate." Then give the bullets as the evidence.
   · Verify: yes.

4. **§7, closing paragraph (lines 165–167)** · Participants per moment and moments per minute fall outside ±25% "on every set here". That is an accuracy claim about two of the three answers step 3 promised, and it sits at the end of the window-size section. It belongs where the pass band is introduced (§6, line 109); there the reader learns that the check covers only the share.
   · **Medium** · Move the paragraph to §6, directly after "It passes when the median error of the share is within ±25%", and leave a back-reference in §7.
   · Verify: yes.

5. **Step 1 (lines 69–70) and the F1/F2 legends vs step 2 (lines 81–86)** · "a shifted copy" is used to make step 1's claim (same mean, wider spread) before step 2 says what a shifted copy is. The term is also missing from Terms.
   · **Low-medium** · Add a "Shifted copy" entry to Terms, one line pointing at step 2. Alternatively, in step 1, gloss it in one clause ("a copy with each cell's onsets slid in time, see step 2").
   · Verify: yes.

6. **§7, opening (lines 144–149)** · The section opens on bench history ("since 2026-10-07…") and only reaches its claim in the first bullet. The motivating context does precede what it motivates, which is correct. But the reader holds a dated history before learning what the section concludes.
   · **Low** · Lead with a one-sentence claim ("The share holds up across window sizes unless two moments fall closer than a window; the other two answers do not"), then explain why these sets were built.
   · Verify: yes.

7. **§8 placement (What else it counts / Figure 5)** · This is a judgment call, not a defect. The page's own question ("how can you count without defining?") is most directly answered by what the measure counts that is not coordination. The opening flags Figure 5 as that answer, but Figure 5 sits third of four results. Placing §8 and Figure 5 immediately after step 2, as the limit of "chance is measured", would put the false-positive answer next to the mechanism it qualifies, ahead of the bias numbers. The current order (evidence before failures) is defensible; it is just unstated.
   · **Low** · Either move §8 and Figure 5 up to become Figure 3, renumbering after it, or add one sentence at the head of "Does it get the right answer?" saying that accuracy on planted moments comes first and what it miscounts follows.
   · Verify: yes.

8. **§9, closing paragraph (lines 212–214)** and **§11, closing sentence (lines 250–252)** · The limits on which recordings the tool uses are operating rules, not part of the "how far one recording strays" claim. The untried time-varying-rate extension is a residual or forward item that addresses the Figure 5 weakness. Neither paragraph does a job in its current section.
   · **Low** · Move the recording limits to §10 or "For developers". Move the untried extension to "What waits", or cross-reference it from §8.
   · Verify: yes.

**Checked and found clean:**
- The title poses the problem.
- The "all simulated, real numbers withheld" caveat comes early (line 42), with its reason last in "What waits".
- Figure numbers follow the order of first discussion in the text. The early forward reference to Figure 5 is deliberate and serves the opening.
- Provenance, What waits and For developers sit at the end, which suits their jobs.
- Every figure and section has a job in the spine; nothing needs to move to an appendix.
