GRANT 11 ok — Read, Grep, Glob (SubagentHandback is present only as the delivery channel; I hold no editing tools)

# Role 11: argument order ("Start With the Problem")

**What I read:** the built `report.html`, using its heading and paragraph-opening lines (grep). The file is 654 KB because of embedded images, so I could not read it whole. I also read all 11 rendered screenshots (`light_1100_00.png` to `_10.png`). I edited nothing.

## The spine: one claim per unit

- **0a. Heading paragraph:** The same learned-versus-coded comparison was run twice, on seeds 1000–1047 and 2000–2047, on two named workstations. This report covers the second run. It is simulation only, fast stream only, baseline only.
- **0b. Answer box:**
  - When only the recordings change, a result moves by a median 0.010 F1 for nets and 0.006 for coded detectors.
  - Under the shared budget, every net trailed CoactDetect in both draws. The best trailed by 0.030 and 0.025, and that gap moved by 0.005 between draws.
  - Chosen on F1 alone, the best net also trailed in both draws.
  - The gap is in precision, possibly from the asymmetric merge, and that was not tested.
- **0c. "Why this report exists":** the rehearsal's small net lead cannot be judged from one run. The comparison decides which detectors the project keeps, so it was rerun on recordings the first run never saw.
- **1.** A coordinated event is several ROIs rising together beyond chance. It is hard to find because events are small, chance coincidences are common, and busy stretches look like events (Figure 1).
- **2.** Only a simulation has an answer key. The bench plants events, distractors and a dense stretch, scores with F1, and caps the ceiling at 0.83.
- **3.** There are ten contestants: six coded rules and four nets with 24 configurations each, the same in both draws.
- **4.** An honest score needs nested cross-validation (CV). Nets train on 10 recordings; coded detectors tune on 72. A fold defect that let two folds train the same model was fixed and gated before both runs.
- **5.** Every entry is chosen twice: on F1 alone, and under a budget of 1.6× sliding CoactDetect's false-alarm rates. Sliding CoactDetect at goal 1's values is the reference. The budget does not police the busy empty recording or time spent calling in the dense stretch.
- **6.** The rehearsal's +0.011/+0.016 lead could not be judged from one run, because its folds share data. So the comparison was run twice on disjoint seeds with everything else held fixed (Figure 5).
- **7.** Each draw's results: CoactDetect scores 0.748 under both selections. Binned SCE leads on F1 alone in draw 1 and ties in draw 2 (Figure 6, Tables 1–2).
- **8.** Some results reflect failures rather than skill: collapsed nets, searches with no admissible setting, held-out budget breaches, and merge settings at the edge of their grids. These entries are flagged † or ‡.
- **9a.** Under the budget, every net sits below CoactDetect in every fold of both draws, and the best gap agrees to within 0.005 across draws.
- **9b.** The gap is in precision, in the pattern a short fixed merge would produce. This was not tested.
- **9c.** Unflagged entries move a median 0.010 (nets) and 0.006 (coded) between draws. This is a lower bound.
- **9d.** Tuning on F1 alone lifted line_length by more than any unflagged net moved between draws.
- **10.** Limits: baseline and fast stream only; bench constants measured on the floor-pinned folder; the two sides were treated differently; no crowded check; event sizes pooled; simulation only.
- **11.** Where the files and code are.

## Arc used, and verdict

I used the default arc, adapted to a replicate report:
- **Problem:** can a lead of about 0.01 F1 be told from the noise of which recordings were drawn? (plus the domain problem in section 1)
- **Cost:** the comparison decides which detectors are kept.
- **Method:** sections 2–5.
- **What the method gets wrong:** one run cannot measure draw noise (section 6); the fold defect (section 4).
- **Fix:** a second, disjoint draw (section 6).
- **Evidence:** sections 7–9.
- **Residual risk:** section 10.

The overall order is defensible and follows the commission's own sequence. Every section has a job; section 11 is an appendix and is correctly placed last. The two required limits are mentioned early (heading paragraph, section 2) and stated in full at the top of section 10.

**What the reader sees first:** a provenance paragraph (seed ranges, workstation hostnames, date, scope), then a box full of numbers. The problem ("Why this report exists") is the third thing they see. The domain problem (section 1, Figure 1) follows immediately after.

The main defects:
1. The answer box arrives before anything in it can be understood.
2. The question the replicate exists to answer is posed but never explicitly answered.
3. Inside section 9, the noise scale arrives after the claim that depends on it.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verifiable against source? |
|---|---|---|---|---|---|
| 1 | Answer box (position 0b) | **Nothing in it can be judged at position 0, and it breaks the commission's "conceptually before any number".** It holds about 12 numbers and relies on terms defined only later: F1 (section 2), CoactDetect / chorus_norm / chorus_gain_norm (section 3), outer folds and 10-vs-72 recordings (section 4), shared false-alarm budget (section 5), "flagged fold" (section 8), merge at 2 s (first defined in section 9). Most of it becomes readable only after section 5, and "flagged fold" only after section 8. The box's label ("Each point is explained in the section named") states the deviation, but the commission's constraint is explicit. | Major | Keep an answer-first box but make it concept-first: no model names and at most one number, each with its meaning. Example: "When only the recordings change, a score moves by about a hundredth. Under one shared false-alarm budget, the learned models' shortfall against the reference hand-written detector was about three times that and held in both draws. It lies in false alarms and may come from how differently the two sides merge calls, which was not tested." Move the numeric bullets to the head of section 9. | Yes (commission text, render 00) |
| 2 | Box, section 6 → section 9 | **The question the report exists to answer is posed but never answered.** Section 0c and section 6 motivate the replicate with the rehearsal's +0.011/+0.016 lead, which could not be separated from draw noise. Section 9 measures draw noise (median 0.010) but never goes back to the rehearsal: "rehearsal" does not occur anywhere in section 9 (grep hits are at lines 58, 149, 184 and 321 only; 321 is in section 11). The box gives the noise (bullet 1) and the gap (bullet 2) separately and never compares them. So "what the pair can claim that either alone cannot" (the commission's distinct job) is left for the reader to assemble. | Major | Add one sentence at the head of section 9, and mirror it in the box: the rehearsal's leads (+0.011, +0.016) are about the size of the median between-draw move (0.010); the present gaps (0.025–0.030) are about 2.5–3× that, and the gap itself moved 0.005. Reviewer 2 should check that this comparison is legitimate; my finding is only that the arc needs it. | Yes (grep "rehearsal") |
| 3 | Section 9 internal order (lines 249 → 257 → 267) | **The noise scale arrives after the claim that depends on it.** Section 9a asserts "Two draws that share no recording, agreeing to within 0.005, are the stronger evidence." But the reader cannot judge 0.005 until "How far results move between draws" (9c), two subsections later. The box orders these the other way (movement first), so the box and section 9 disagree. | Major | Reorder section 9: between-draw moves (currently Figure 10) → headline gap against that scale (Figure 8) → where the gap is (Figure 9) → tuning. Renumber the figures to match. | Yes (render 07–09) |
| 4 | Sections 3–4 vs section 9b and section 10 | **The main alternative explanation of the headline arrives only after the results.** The nets' fixed 2 s merge, set against coded merges that tune up to 8–30 s, first appears in the body in section 9 "Where the gap is" (line 263) and section 10 (line 295). Section 3 describes the nets without their merge. Section 4 gives only the 10-vs-72 asymmetry, and section 8 only the coded side's grid-top merges. So the reader weighs sections 7–9a without knowing that one side's merge is fixed at 2 s. It should be introduced in section 3 or section 4. | Moderate | Add one sentence in section 3 or 4, next to the 10-vs-72 sentence: nets merge calls closer than 2 s, fixed; each coded detector tunes its own merge. Then have sections 9b and 10 refer back to it. | Yes (grep "fixed 2 s", "merge at") |
| 5 | Section 5, line 167 (sliding paragraph) | Commission item "why the coded side runs sliding LoCo/CoactDetect from goal 1's values" sits inside "Two selections and one shared budget", as an aside on the budget's reference. Section 3 introduces CoactDetect and LoCo without the sliding/binned distinction, yet names "binned SCE". The reader meets "binned" as a contrast before "sliding" exists, and would not look for the reason under the budget heading. | Minor | Move the sliding paragraph into section 3, after the coded-detector list. Section 5 then says "the reference is sliding CoactDetect (section 3)". | Yes |
| 6 | Heading paragraph (0a), what the reader sees first | The report opens on provenance and scope: seed ranges, hostnames WSMIP064/065, date, "simulation only". Seeds and hostnames mean nothing at position 0, and Figure 5 (section 6) and section 11 already carry them. The motivation paragraph comes third, after the numeric box. | Minor | Make the heading paragraph state the question (can a lead this small be told from which recordings were drawn?). Move seeds and hosts to section 6 / section 11. Put "Why this report exists" directly under it, before the answer box. | Yes (render 00) |
| 7 | Section 7 → section 8 | Section 7's evidence needs section 8 to be read. Tables 1–2 carry †/‡ flags and Figure 6's "isolated low dots", which are explained only in section 8. Section 7 also defers the binned SCE lead to section 8. Section 8 does not depend on section 7's tables. | Minor | Either swap them (section 8, framed as "what to discount before reading the results", then section 7), or accept the forward references knowingly. The section 8 → section 9 order is correct either way, because section 9's headline excludes flagged entries. | Yes |
| 8 | Section 5 "What the budget does not police" vs section 10 | A residual risk (busy empty recording not gated; dense-stretch ceiling counts calls, not time spent calling) sits in the method section and is missing from the limits list, so the residual-risk step of the arc is incomplete. | Minor | Add a one-line bullet in section 10 pointing back to section 5. | Yes (render 04, 09–10) |
| 9 | Between 0c and section 1 | An unstated deviation: about 40% of the page (sections 1–5, the comparison in general) separates the replicate's motivation from its method (section 6). This is defensible because the commission orders concepts first, but the report never says so. | Minor | After "Why this report exists", add one line: "Sections 1–5 explain the comparison itself; section 6 onward is what the second draw adds." | Yes |

## Checked with no finding

- **Sections 1 → 2:** they motivate before they define. Figure 1 (what the problem looks like) is the first figure and sits in section 1. That is correct.
- **Section 4's fold-defect box:** it comes before either run is described, and before section 6 cites it. That is correct.
- **Section 8 before section 9:** needed, because section 9 excludes flagged entries.
- **Section 10's order:** the commission's two named limits come first.
- **Section 11:** it is an appendix and sits last.

## Files

- Artifact: `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`
- Renders read: `<session-scratch>\scratchpad\shots\light_1100_00.png` … `_10.png`
