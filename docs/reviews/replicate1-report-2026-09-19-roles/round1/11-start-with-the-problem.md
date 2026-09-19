GRANT 11 ok — Read, Grep, Glob
(I also hold SubagentHandback, which is the delivery channel for this report and not an editing tool. I hold no Edit, Write, NotebookEdit or Bash.)

# Role 11: argument order ("Start With the Problem"), round 1

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`. I read all of its prose, all 8 figure captions and both table captions. I looked at the rendered screenshots `light_1100_00.png`, `_04.png` and `_05.png` in `...\scratchpad\shots\` to see the cold open and the positions of the results figures.

**Arc used:** the default analysis arc, adapted to what this report is commissioned to do.
- Default arc: the problem → what it costs → the method → what the method gets wrong → the fix → the evidence → the residual risk.
- This report has two layered problems:
  - the goal-2 problem: finding coordinated events, and comparing the detectors fairly;
  - the replicate's own problem: a +0.011 margin that one run could not separate from the noise in the draw.
- Target arc: answer → the replicate's question, stated in plain words → coordinated events and why they are hard → simulation → contestants → nested cross-validation and the fold defect → the two selections and the sliding coded side → why two draws, and the design → per-run results → defects that are not the models → the draw-against-draw evidence and what the pair claims → limits → locations.
- The commission itself asks for "conceptually before any number". That justifies sections 1–5 coming before section 6, and I do not count it as a defect.

## 1. The spine (one claim per section)

0. **Answer box:** under the shared budget CoactDetect beats every net in both draws (by 0.030 and 0.025). On F1 alone the leading net and CoactDetect cannot be told apart. An entry moves about 0.008 (at most 0.027) between draws, and the rehearsal's +0.011 falls inside that.
1. A coordinated event is several ROIs rising together more often than chance. Finding one is hard because events recruit few cells, cells fire on their own, and busy stretches imitate events (Figure 1).
2. Real data have no answer key, so a simulated bench plants events. It is scored by F1, averaged over a quiet and a busy background.
3. Six coded detectors are compared with four nets. tube is the control, because it cannot count distinct cells. Each net has the same 24 configurations in both runs.
4. Nested cross-validation makes a score honest. A fold defect that made two held-out folds share one fit was fixed and checked before either run started.
5. Every entry is chosen twice, on F1 alone and under a false-alarm ceiling of 1.6 × CoactDetect. CoactDetect and LoCo run in their sliding form with goal 1's values, because the binned forms are known to be worse.
6. The rehearsal's +0.011 lead cannot be judged from one run. So the comparison was run twice on disjoint recordings with everything else held fixed (Figure 5).
7. Per-run results: CoactDetect is the steadiest entry (0.748 in both draws; Figure 6, Table 1). Between draws the median entry moved 0.008 and the largest non-defect move was 0.027 (Figure 7).
8. Three effects in the results are not the models: a tuned configuration that collapses in training, coded detectors with no admissible setting, and settings stopped at the edge of their grid (Figure 8, Table 2).
9. What the pair can claim: the noise yardstick; CoactDetect leading under the budget in both draws; the F1-alone question left open; tuning helping line_length in both draws.
10. Limits: baseline and fast stream only; bench constants measured on the folder with floor-pinned ROIs; simulation only; no crowded check inside the search.
11. Where the run folders and the build tool are.

**Coverage of the commission.** Every commissioned item is present, and each sits at or after the earliest point where it can be understood:
- coordinated events and why they are hard: §1
- why a simulation: §2
- nested cross-validation and the fold defect: §4
- the sliding coded side and the two selections: §5
- why a second draw, disjoint recordings, everything else fixed: §6
- what the pair can claim: §9
- the two required limits: §10

The broad order is defensible. The defects below concern **where the replicate's own argument sits inside that order**.

## 2. Cold open

**What the reader sees first:**
1. The title, "what a second set of recordings adds".
2. A subtitle made mostly of lookup keys: WSMIP064, WSMIP065, seed ranges.
3. The answer box: seven numbers, two net names (chorus_gain_norm, chorus_norm) and "the rehearsal run". None of these is defined until §3, §5 or §6.
4. §1 and Figure 1, the problem figure, which is still on the first screen (shot `_00`).

**Verdict:**
- For the goal-2 problem, the cold open is good: the picture of the problem is on screen one.
- For **this report's own problem** it is not. The question the replicate exists to answer is never stated as a question anywhere before §6. The box gives it only as a conclusion ("the +0.011 … sits inside it"), about a run the reader has not been told exists.

## 3. Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source? |
|---|---|---|---|---|---|
| 11-1 | §7, second half (Figure 7 and the "joins are short" paragraph), relative to §8 | **The noise yardstick is shown before the defects it excludes.** §7 defines the replicate's central number as "none of the 20 entries **without a named defect** moved more than 0.027". The Figure 6 caption ("defects named in section 8") and the Figure 7 caption ("Those bold rows are the defects of section 8") both point forward to defects the reader has not met. At its current position the reader cannot evaluate the report's most important measurement, and it sits in a generic "Results" section rather than beside the claims it supports. | Medium | Move Figure 7 and its paragraph out of §7 to the **opening of §9**, after §8. Order becomes: §7 per-run results (Figure 6, Table 1) → §8 defects → §9 "draw against draw" (Figure 7) → the claims read against it. The yardstick then arrives after its exclusions are known and directly before the claims it supports. | yes (artifact text: §7 para 2, Figure 6 and 7 captions, §9 bullet 1) |
| 11-2 | Answer box, and §1 before §6 | **The replicate's own question arrives at position 6 of 11.** The title promises "what a second set of recordings adds". But the reason a second draw exists (a +0.011 margin one run cannot separate from redrawing the recordings) is first stated as a question in §6, after five sections of shared background. §6 cannot move up whole, because it needs F1 (§2), folds (§4) and the budget (§5). A plain-language version needs none of those. As it stands the reader holds the report's purpose in suspense through §1–5. | Medium | Add two or three sentences between the answer box and §1, with no jargon. For example: "A rehearsal of this comparison put the best learned model slightly ahead of the best coded detector. Whether a lead that small is real depends on how much a result moves when you only swap the recordings, and one run cannot measure that. This report is the second run, and it measures exactly that." §6 keeps the full, jargon-dependent version. | yes |
| 11-3 | Answer box, bullet order | **The box's first two conclusions depend on the third.** "The same sign and size twice" (bullet 1) and "cannot be told apart" (bullet 2) are both judged against the 0.008 / 0.027 yardstick, which appears only in bullet 3. §9 has the correct order: yardstick first, then the margins read against it. The box reverses it, and the yardstick is also the replicate's distinct contribution. | Low–medium | Reorder the box to match §9: (1) how far an entry moves between draws, and that the rehearsal's +0.011 is inside it; (2) the budgeted result; (3) the F1-alone result. | yes |
| 11-4 | Answer box bullet 3; §4 warning paragraph; §6 | **"The rehearsal run" is used three times before anything says what it was, and the fact needed to weigh its +0.011 sits in the wrong section.** The box cites "the rehearsal run before these two". §4 says "The rehearsal run found that two outer folds trained the same net". §6 then uses its +0.011 as the motivation. Nothing at §6 or §9 connects these: the rehearsal ran **with** the fold defect, and it had the opposite sign (net ahead by +0.011 under the budget, against net behind by 0.030 and 0.025 here). The swing from +0.011 to −0.030 is 0.041, which is larger than the 0.027 maximum move. A reader cannot tell whether the rehearsal counts as a third draw. (Boundary: whether the claim that "+0.011 sits inside it" is supported belongs to agent 4. Here the problem is that the fact needed to judge it is in §4 and never brought to §6 or §9, where the judgment happens.) | Medium | Define the rehearsal in one clause at first use: an earlier full run of the same comparison, before the fold fix. In §6, state that the rehearsal ran with the defective folds, so it is not a clean third draw, and say how the reader should treat its sign. Repeat that in §9 bullet 1, where the +0.011 is placed inside the range. | yes (box bullet 3, §4 warning paragraph, §6 para 1, §9 bullet 2) |
| 11-5 | §6, "what it costs" slot | **Nothing states what decision the comparison informs, or what taking +0.011 at face value would have cost.** The arc has the problem (§1) and the replicate's question (§6), but never the stake. It is never said what would follow from "a net beats CoactDetect" (for example, adopting a net as the lab's detector). Without that, the reader cannot tell why a 0.01-sized question deserved a second 13-hour run. | Medium | In §6, one sentence after the +0.011: the conclusion that margin would have licensed, and why being wrong about it matters. The same sentence can go in the new framing paragraph proposed in 11-2. | yes (absence confirmed across the full prose) |
| 11-6 | §8, "Settings at the edge of their grid", and Table 2 | **A caveat arrives for a claim the spine never makes.** The subsection ends: "SCE's lead on F1 alone may be the bench's wide event spacing rewarding a long merge". But no section says that binned SCE leads on F1 alone. It does, in Table 1 (0.771 and 0.748). The answer box and §9 frame the F1-alone question as leading net against CoactDetect only. So the qualification comes before, and in place of, the claim it qualifies. (Boundary: whether SCE's lead should change the headline belongs to agent 4. Here the caveat's claim is simply missing from the order.) | Low–medium | Either state SCE's F1-alone lead in §7, where Table 1 is read, and keep the §8 caveat after it; or, if SCE's lead has no job in the replicate's argument, move the grid-edge subsection and Table 2 to an appendix after §10. The §10 "no crowded check" bullet then points there. | yes (Table 1 in shot `_05`; §8 third subsection) |
| 11-7 | §2 against §10, bullet 2 | **The floor-pinning limit appears only at §10, though it could be understood at §2.** That is where the bench's fitted background is introduced. The reader meets the bench's constants in §2 and relies on them through §9 before learning, at position 10, that they were measured on a folder with a known defect. Putting residual risk last is the stated arc, so moving the limit is not required. A pointer is, given this repository's rule that a known contamination is not a footnote. (The fast-stream and baseline-only limit is already seeded at §2 and in the subtitle, so it is fine.) | Low | Add one clause to §2 where the fitted background is introduced: "…fitted on an export with a known motion-correction defect; see section 10." | yes |
| 11-8 | §6, last sentence ("`--replicate 0` declares, byte for byte, … which is what let that run stay resumable while this option was added") | **An implementation detail with no job in the argument, placed at the pivot of the replicate's case.** The resumability of WSMIP064's run while the option was added does nothing for "the two draws share everything but the recordings". The preceding sentence (two declarations differing in exactly 2 entries) already does that job. | Low | Move the sentence to §11, next to the `--replicate` option. | yes |
| 11-9 | Answer box: an unstated deviation from the commission | **The commission says "conceptually before any number". The box opens with seven numbers before any concept.** Answer-first is a defensible deviation, but the page never says so, and most of the box cannot be read until §3, §5 and §6. | Low | Keep the box. Add a closing line such as "Sections 1–5 explain the terms; section 6 says why there are two runs; section 9 reads these numbers." That states the deviation and gives the reader the route. | yes |

## 4. Earliest intelligible position, and each section's job

| Section | Job in the argument | Earliest intelligible after | Position OK? |
|---|---|---|---|
| Answer box | Headline | After §2, §3, §5, §6 (terms), so it needs pointers (11-3, 11-4, 11-9) | Allowed deviation, currently unstated |
| §1 | The problem, and why it is hard | Nothing | Yes |
| §2 | Why a simulation; the scoring measure | §1 | Yes (pointer needed, 11-7) |
| §3 | Who competes; tube as the control | §1–2 | Yes |
| §4 | Honest scoring; the fold defect fixed before launch | §2–3 | Yes |
| §5 | The two selections; the sliding reference detector | §2–4 | Yes |
| §6 | Why a replicate; the disjoint-draw design | §2, §4, §5 | Yes as written. A plain version belongs before §1 (11-2) |
| §7 | Per-run results | §5–6 | Yes for Figure 6 and Table 1; **no for Figure 7** (11-1) |
| §8 | What the results show that is not the models | §7 | Yes for the first two items; the third qualifies an unstated claim (11-6) |
| §9 | What the pair claims | §6–8 | Yes. It should also carry Figure 7 (11-1) |
| §10 | Residual risk | §2 | Yes (end of arc) |
| §11 | Locations | — | Yes (appendix-like, at the end) |

## 5. Proposed order

Answer box (yardstick first, rehearsal defined, pointer line) → **new two-to-three-sentence "why this report exists" framing** → §1 → §2 (limit pointer) → §3 → §4 → §5 → §6 (rehearsal ran with the fold defect; what the margin would have licensed; no resumability sentence) → §7 (Figure 6, Table 1; SCE's lead stated if kept) → §8 → §9 **opening with Figure 7, draw against draw**, then the claims → §10 → §11 (plus the `--replicate 0` sentence; plus the grid-edge subsection if demoted).

No slide-level moves beyond Figure 7 are needed. The main sequence already follows the commission. The defects are that the replicate's own question and its yardstick arrive later than the reader can use them, and that one fact needed to weigh the rehearsal sits in the wrong section.
