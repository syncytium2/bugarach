GRANT 5 ok — Read, Grep, Glob

(I also hold SubagentHandback, which is only the hand-off channel. I hold no Edit, Write or NotebookEdit.)

# Role 5, line editor: report.html (second draw, the "replicate1" report)

**Artifact:** %USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html (654 KB). I read the prose at lines 1–74, 76–154, 156–324. Lines 75, 155, 182, 193, 202, 219, 256, 266 and 275 hold embedded images or SVG. I took their captions out with Grep. I checked the Figure 1 caption and Tables 1–2 against %USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\tools\make_replicate_report.py (lines 1005–1021 and 1185–1192) and against the screenshots light_1100_01.png and light_1100_05.png.

## The prose tool: not run
`murderboard_prose.sh` is **not run**. It does not exist in this repository and I hold no shell. That is a failure, not a clean result. Below is the search I ran with Grep instead, with its raw output. The block counts were done by reading, so they are approximate to about ±5 words.

**List searched:** the house list from my role file in doc_review_process.md, role 5: not just X but Y · it's not about A it's about B · it's worth noting · delve, leverage, robust, seamless, crucial, landscape, tapestry · rhythm triads · em-dash pivot into an uplifting close · "In today's ___".

| pattern (Grep, case-insensitive) | raw hits | verdict |
|---|---|---|
| `not just\|not only\|it's not about\|worth noting\|delve\|leverag\|robust\|seamless\|crucial\|landscape\|tapestry\|in today's` | `75:DeLvE` | False positive: base64 image data on line 75. **0 real hits.** |
| ` — ` (spaced em dash) | 73, 136, 137, 157 ×2, 193 ×2, 219 ×4, 309 | None is a pivot into an uplifting close. 73, 136–137, 157 and 193 are paired parentheticals. 219 is inside the Figure 7 SVG. 309 introduces a list. The unspaced dash at line 80 is a definition. **0 defects.** |
| `not … , but \|, not [word]\|rather than` | 51 ", not a verdict", 52 ", not recall", 78 ", not truth", 176 ", not for the values", 180 ", not time", 264 ", not a finding", 271 "rather than" | These are "X, not Y" contrasts. They are not on the banned list, and each one carries a real contrast. Lines 51–52 put two of them in consecutive sentences, which reads as rhythm (see finding F4). |
| 3-item lists `A, B and C` | 54, 116, 118, 126, 189 | All are real enumerations (section numbers, authors, detectors, shared resources). The subtitle's "Simulation only, fast stream only, baseline only" names three real limits. **0 rhythm triads.** |
| `\bdata\b` (plural-data rule) | 5, 9 (CSS), 75 (base64), 170, 189, 253 | Lines 170 and 253 have no verb that agrees with "data", and line 189 has only a noun phrase. **0 violations.** |
| British spelling | 130 "draughtsman" ×2, 224 "neighbour", 301 "favours" | **4 hits.** The house rule is American English (writing_conventions.md). See F20. |

## Passage test, one row per block
Columns: block · words · sentences · the payload sentence · where the payload sits · what the other words buy.

| block | words | sents | payload | at | the other words buy |
|---|---|---|---|---|---|
| Subtitle (31–36) | ~72 | 5 | "The same comparison was run twice …" | 2nd | Workstation names and the report date are lookup keys. Keep the seeds. |
| Answer box (38–56) | ~210 | 11 | four bold claims | bullet leads | Mostly evidence. Its opening sentence and bullet 1's label-style lead buy nothing (F1, F2). |
| Why this report exists (58–62) | ~85 | 4 | "so it was run a second time on recordings the first never saw" | end | Motivation. Its content is repeated by section 6 (F6). |
| §1 ¶1 (65–69) | ~65 | 4 | definition of a coordinated event | 3rd | Needed definitions. Keep. |
| §1 ¶2 (70–74) | ~65 | 4 | three reasons it is hard | 1st | Evidence. Keep. |
| Fig 1 caption | ~140 | 6 | how to read the raster | 2nd | Fine, apart from one number with no unit (F11). |
| §2 ¶1 (77–83) | ~115 | 5 | "A simulation plants the events and keeps the answer key." | 2nd | Definitions (bench, baseline, stream). Keep. |
| §2 ¶2 (84–93) | ~110 | 4 | bench composition | 1st | Needed numbers. One sentence parses badly (F9). |
| §2 ¶3 (94–101) | ~95 | 6 | F1 definition, ceiling 0.83 | 1st and end | Keep. Uses "fold" before it is defined (F10). |
| §3 provenance (115–119) | ~65 | 1 | where each detector comes from | — | Attribution a sceptic wants. One awkward clause (F21). |
| §3 nets (120–129) | ~140 | 7 | four nets, 24 configurations | spread | "pool the cells' votes three ways" names no ways (F22). |
| Fig 2 caption | ~70 | 4 | (describes a picture that is absent) | — | Asserts something false (F12). |
| §4 ¶1 | ~75 | 4 | "A score is honest only if …" | 1st | Good. Keep. |
| §4 ¶2 (138–146) | ~140 | 5 | how inner fits are compared | 1st | The deduplication parenthetical creates a 432 vs 864 puzzle (F13). The closing pointer sentence repeats the asymmetry (F7). |
| §4 defect note (147–154) | ~115 | 5 | "A defect was fixed before either run started." | 1st (good) | The mechanism sentence is the author's thoroughness, and it uses "run" in two senses (F14). |
| §5 ¶1 (157–166) | ~150 | 6 | the budget is 1.6 × the reference detector's false-alarm rates | 4th | The 1.6 provenance chain (binned, sliding, HANDOFF, branch) is heavier than a new reader needs. It withholds the reference's name, and "entry" and "empty recording" are defined badly (F15, F16, F17). |
| §5 ¶2 (167–176) | ~150 | 5 | the reference is sliding CoactDetect at goal 1's settings | 1st | The last sentence, about the code's settings table, is repository housekeeping (F18). |
| §5 ¶3 (177–181) | ~60 | 3 | what the budget does not police | 1st | Concrete. Keep. |
| §6 (184–192) | ~125 | 6 | the rehearsal's lead (+0.011, +0.016) is too small to judge from one run | 4th | Half of it restates "Why this report exists" (F6). "entries" collides with a defined term (F19). |
| §7 (195–201) | ~75 | 5 | CoactDetect 0.748 in both draws; SCE leads in draw 1 | 2nd | "0.748 and 0.748" reads like a typo. "leads" does not say over whom (F23). |
| §8 training failed (205–218) | ~150 | 7 | a configuration that fails some repeats can still win | 1st (good) | A sentence carrying eight numbers belongs in a table (F24). |
| §8 no admissible setting (221–226) | ~65 | 3 | locust never found an admissible setting | 1st | Evidence. "cells" collides with biological cells (F25). |
| §8 held-out budget (228–232) | ~70 | 3 | some net refits broke the budget on held-out data | 2nd | Keep. |
| §8 grid edge (236–242) | ~120 | 5 | SCE's first-draw lead may come from the bench's wide spacing rewarding a long merge | **last** | Promote the payload to the top (F26). |
| §9 headline gap (249–255) | ~105 | 5 | two disjoint draws agree to within 0.005 | **last** | Promote it. One sentence is imprecise (F27). |
| §9 where the gap is (257–265) | ~135 | 6 | gap is in false alarms "anywhere else"; merge suspicion untested | 2nd | Evidence. One sentence claims more than its own figure shows (F28). |
| §9 moves (267–274) | ~110 | 4 | for a gap, what matters is how far the gap moved: 0.005 | **last** | Promote it. One interpretation is stated as fact (F29). |
| §9 tuning (276–278) | ~40 | 2 | (implicit) | none | The paragraph gives numbers but never says what they mean (F30). |
| §10 bench defect bullet (285–294) | ~135 | 6 | the simulator was fitted to a defective folder, and refitting moved one of eight constants | spread | Who decides, "item 3", the branch: provenance. The closing sentence asserts something the document does not know (F31). |
| §10 other bullets | 25–55 each | — | the limits | 1st | Keep. The asymmetry bullet is the third statement of the same point (F7). |
| §11 | ~165 total | — | where the files are | — | Pointers. Keep. |

## Findings
Format: location · issue · severity · suggested fix · could I verify it against a source.

1. **Answer box, line 38.** "Each point is explained in the section named." is throat-clearing: every bullet already names its section. · low · Cut it. · yes
2. **Answer box, bullet 1, line 40.** The bold lead is a label ("How much a result moves…"). The other three bold leads are claims. · low · Make it a claim, e.g. "Changing only the recordings moved a result by about 0.01 F1." · yes
3. **Answer box, bullet 2, lines 45–46.** "trailed by 0.030 and 0.025 F1, below zero in all 8 outer folds": "below zero" has no subject, since the gap is never named. "Outer folds" and "flagged fold" (bullet 1) come before any definition. · medium · Use "…and trailed in all 8 outer folds". Gloss "fold" once, or point to section 4. · yes
4. **Answer box, bullets 3–4, lines 48–52.** "the best learned model also trailed in both (−0.007 and −0.029)" hides that the best model is a different net in each draw. Table 1 shows chorus_norm at 0.741 in draw 1 and chorus_gain_norm at 0.719 in draw 2. "Only the untuned chorus_norm reached CoactDetect, in one draw (−0.012 and +0.006)" makes the reader work out which draw. "reached" is vague, and the sign shows it came out ahead. Bullet 4 then puts two "X, not Y" sentences back to back. · medium · Name the model per draw. Write: "Only untuned chorus_norm came out ahead, in the second draw (+0.006; −0.012 in the first)." Split bullet 4's precision point into its own sentence. · yes (Table 1 screenshot)
5. **Subtitle, lines 33–35.** WSMIP064/WSMIP065 and "2026-09-19" are lookup keys in the opening paragraph for a new reader (writing_conventions: "Shas and dates are lookup keys"). · low · Move the machine names to section 11. The date is already in `<meta name='date'>`. · yes
6. **Section 6 against "Why this report exists" (lines 58–62 and 184–192).** Both say the rehearsal put nets slightly ahead, that a margin that small cannot be judged from one run, and that the comparison was therefore run twice. · medium · Cut section 6's restatement. Keep only what is new: the rehearsal's defects, its numbers (+0.011 and +0.016), and the fact that the two runs differ only in seeds and the replicate option. The boundary with role 11: I am not moving the section, only removing repeated sentences inside it. · yes
7. **The asymmetry is stated three times** (answer box bullet 4, section 4 lines 144–146, section 10 lines 295–298), and section 10's "The headline is a result about the comparison as run" repeats bullet 4. · low · Keep the answer box and section 10. In section 4, cut "That difference is one of the asymmetries of section 10." · yes
8. **Lines 61, 171 and 281.** "goal 2 of the program", "Goal 1 of the program" and "item 3 of the decisions" index things instead of naming them. "the program" and "the project" are used interchangeably. · low · Name the goals, e.g. "the goal of choosing which detectors to keep" and "the goal that tuned the sliding detectors". Pick one of "project" or "program". · yes
9. **Lines 85–87.** "15 planted events at least 120 s apart, 5 each recruiting 30%, 18% and 10% of the ROIs" reads first as "five each". · low · Write "five at each of three sizes: 30%, 18% and 10% of the ROIs (10, 6 and 3 cells)". · yes
10. **Line 97 (§2) and line 142 (§4).** "a fold's recordings" appears before section 4 defines a fold. "the budget's winner" appears before section 5 introduces the budget. · low · In §2 write "pooled over the recordings scored together". In §4 write "the winner under the false-alarm budget (section 5)". · yes
11. **Figure 1 caption, last sentence.** "CoactDetect averages 0.75 there": 0.75 of what? CLAUDE.md requires a unit on every number. · low · Write "0.75 calls per recording". This overlaps with role 10's mechanical unit check, and I file it once, here. · yes
12. **Figure 2 caption, line 130.** "This slot holds the project's draughtsman drawings…" is false: the slot holds a placeholder. The section 3 link "Figure 2, the four architectures" promises a picture that is not there. · medium · Say "will hold", or say plainly that the drawings are not in this build, and drop the promise from the §3 link text. · yes
13. **Section 4 ¶2 (lines 138–141) against section 8 (line 213).** "432 inner fits per net … fitted once" sits beside "292 of 864 scored inner fits". The reader gets two counts and no bridge between them. The first sentence also carries three claims. · medium · Split the sentence. Write "432 inner fits per net, each scored in both outer folds that share its pair: 864 scores". · yes (24 configurations × 6 pairs × 3 repeats = 432; × 2 = 864)
14. **Defect note, lines 147–153.** "training reads a contiguous run of its recording list, so … that run sat inside …" uses "run" in the paragraph that ends "Both runs passed it", where it means the comparison run. The mechanism is thoroughness a sceptic does not need. · medium · Cut to: "In the rehearsal, two held-out folds trained on the same ten recordings. Recordings are now dealt round-robin across the training folds, and a check refuses to start a run unless every outer fold fits its own. Both runs passed it." If the mechanism stays, write "contiguous block". · yes
15. **Section 5, line 157.** "Every entry — one detector or net under one way of choosing it — is chosen twice" is circular. If an entry is already detector plus selection, it cannot be chosen twice. · medium · Write "Each detector and net is chosen two ways, and each pairing is an entry." · yes
16. **Section 5, lines 159 and 177.** "a recording with nothing in it" and later "the quiet empty recording" rely on a recording that section 2's bench description never mentions. Figure 4's "three ceilings" are never named in the prose. · medium · Name the empty recordings in §2. List the three ceilings in §5 (for example: dense stretch at each background, plus the quiet empty recording, if that is what they are). · no (which three ceilings they are is inferred from Figure 4 and line 177)
17. **Section 5, lines 161–167.** "one fixed detector's own false-alarm rates … That fixed detector is sliding CoactDetect" withholds a name for one sentence. The 1.6 rationale uses "binned CoactDetect" and "the sliding reference" a paragraph before they are defined. · medium · Name sliding CoactDetect in the first sentence. Reduce the 1.6 sentence to "a margin carried over from the bench's calibration" plus the source pointer. · yes
18. **Section 5, lines 175–176.** "The code's table of shipped settings still names the binned versions, held back for the browser viewer and for an analysis tied to the binned calls, not for the values." This is repository housekeeping that changes nothing a reader concludes. · low · Cut it, or move it to section 11. · yes
19. **Section 6, line 190.** "declarations differ in exactly two entries" collides with "entry" as defined in section 5. · low · Write "two fields". · yes
20. **British spellings at lines 130 ("draughtsman" ×2), 224 ("neighbour") and 301 ("favours").** · low · Change to draftsman, neighbor, favors. Change them in the generator, not the HTML. · yes (writing_conventions.md, "American English")
21. **Line 115.** "Where each comes from, and what is this project's, is recorded in…" is awkward. "independently resemble radar…" does not say independent of what. · low · Write "docs/detector_history.md records each detector's origin and what this project added: …" and "resemble, without having been derived from, radar constant-false-alarm-rate detection". · yes
22. **Line 125.** "pool the cells' votes three ways" names no ways. "tube is the control" does not say a control for what. · low · Name the three pools, or cut "three ways". Say what tube controls for. · no
23. **Section 7, lines 196–200.** "CoactDetect scores 0.748 and 0.748" reads like a typo. "Binned SCE leads on F1 alone … (+0.023)" does not say over whom. · low · Write "0.748 in both draws" and "leads CoactDetect by 0.023". · yes (Table 1: 0.771 − 0.748)
24. **Section 8, lines 211–218.** One sentence carries eight numbers for four nets and two draws, with the draws only implied. The next sentence opens with a numeral ("2 refits…"). · medium · Put it in a small table, or summarise: "about a third of chorus_norm's inner fits (292 and 306 of 864), a sixth of chorus_gain_norm's (150 of 864 in each draw), under 3% of line_length's and tube's". Write "Two refits…". · yes
25. **Line 226.** "Those cells carry ‡" means table cells in a document where "cell" means a neuron throughout. · low · Write "Those table entries carry ‡". · yes
26. **§8 "Settings at the edge of their grid" (lines 236–242).** The payload (SCE's lead may be the wide spacing rewarding a long merge) is the last clause of a 120-word block. The goal 1 history sentence is long. · medium · Open with the payload. Shorten the goal 1 sentence to: "CoactDetect and LoCo start at goal 1's 8 s, which goal 1 checked on events 6 s apart." · yes
27. **§9 headline gap (lines 253–255).** "a statistic over them overstates their independence" is imprecise, since a statistic assumes independence and so overstates precision. "would not settle it" has a vague "it". The payload is the last sentence. · medium · Write: "Two draws that share no recording agree to within 0.005 F1. Within a draw the four folds share training data, so a spread over them would overstate its own precision." · yes
28. **§9 "Where the gap is", line 261.** "the nets … far more often anywhere else" is not true of tube. The Figure 9 SVG tooltips give tube 0.57 and 0.43 per recording against CoactDetect's 0.57 and 0.24. · medium · Write "three of the four nets call far more often anywhere else" and name tube. · yes (SVG `<title>` text, line 266)
29. **§9 "moves", lines 270–274.** "which is a shift of the whole draw rather than independent noise" states an interpretation as fact. The payload (use how far the gap moved, 0.005) comes last. · low · Write "which looks like a shift of the whole draw". Open the paragraph with the gap figure. · no
30. **§9 "Tuning", lines 276–278.** The paragraph gives numbers and never says what they mean. · low · Add the claim: "so tuning's gain for line_length is larger than rerun noise; for chorus_norm it is not separable from the collapse." · yes
31. **§10 bench-defect bullet, lines 285–294.** "It does not make the results wrong" asserts something the document does not know: one of eight constants moved outside its interval, and nothing reran the comparison. "both workstations … in both folders" leaves unclear what "both" counts. "item 3 of the decisions" is an index. · medium · Write: "Refitting on the corrected folder moved one of eight constants, the share of ROIs an event recruits, just outside its interval. Whether that changes any result here is untested." Keep the file pointer. · yes (the prose shows no rerun on the corrected export)
32. **§10, line 281.** "By the program's decision of 2026-09-17" treats the date as content. "under TTX" is used without saying what TTX is. · low · Cut the date. Gloss TTX as "a sodium-channel blocker applied during the recording", or cut the clause. · yes
33. **Figure 1 key (inside the raster PNG, drawn by `bugarach.ui.diagnostic`).** Some phrases are decoration: "hairlines by honesty rather than by style", "this figure's inference wearing the detector's authority", "fragmentation, not hallucination". "SCE bins at ten seconds" refers to a detector this figure does not draw. · low · Fix it in the shared legend text, not in this report. This is outside the HTML prose; I am flagging it for the owner. · yes (screenshot light_1100_01.png)

## Outside my scope, passed on and not adjudicated
- **Figure 9, line 266.** The SVG tooltips give LoCo **−0.70** and **−0.67** false alarms per recording "anywhere else". A negative count, drawn as a zero-width bar, points to a bookkeeping error in the split (for roles 10 and 4).
- **Answer box.** Untuned chorus_norm is given as "+0.006". Table 1 gives 0.753 − 0.748 = 0.005. This is probably rounding of unrounded means (for role 4).

**What I checked:** every prose block, caption, table caption and footnote in the rendered HTML body, the §10 and §11 lists, and the Figure 1 legend via its screenshot. I did not read the SVG axis labels or the table cell values beyond the checks cited above; those belong to role 10.
