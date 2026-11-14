GRANT 5 MISMATCH — missing none; holds Edit, Write, Bash, PowerShell, Agent, Artifact, Skill, ToolSearch (NotebookEdit loadable through it), mcp__claude_ai_Claude_Docs__batch/update/guide, SubagentHandback

This was a fallback-path spawn: the harness gave me editing and shell tools that role 5 must not hold. I used only Read, Grep and Glob, and I edited nothing. Record it in the run's `roles:` line.

# Role 5, line editor ("Kill Your Darlings"): chapter-1-aim0.md (blob faa8e320)

## Run finding (about the review, not the artifact)
- **R1. The prose tool was not run.** `murderboard_prose.sh` is missing from the worktree. Glob over the whole repository and over `.claude/` found no file. Only references to it exist: `docs/doc_review_process.md`, `tools/murderboard_revendor.py`, `tools/murderboard_freshness.sh`, one handoff file, and the role file. My grant has no Bash in any case. Under the role's rule, "not run" is a failure, not a clean result. What I did instead:
  - I ran the banned-construction and *data is* searches as Grep regexes. Their output is pasted below.
  - I could not count words per block mechanically. The block sizes in the passage table are estimates from line counts (about 14 words per line) and are marked "~".
  - Severity: high for the run, none for the artifact. The fix is to vendor the script or point the role at its real path.

## Mechanical searches (Grep, house list as written in 05-kill-your-darlings.md)
| search | hits (line · text · kind) |
|---|---|
| `delve\|leverage\|robust\|seamless\|crucial\|landscape\|tapestry`, `worth noting`, `not just`, `not only`, `it's not about`, `In today's` | 1780 · "Simple, robust and optimal ranking…" · inside a cited paper title, so a quotation and not a finding |
| em-dash pivot (` — `) | 0 |
| *the/this/these… data is/was/has/does/shows/itself*, `this data` | 0 |
| writing_conventions extras: `fire/fires/fired/firing`, `centre`, `labelled`, `modelling`, `toy` | 0 |
| a hyphen at the end of a line (it renders as "word- word") | 733 · "net downstream-minus-" / "upstream" · **render defect, see F1** |

No *In today's* opener and no *not just X but Y*. The "X, not Y" contrasts at lines 140, 981, 1170 and 1681 are precise rather than rhetorical, except 1170 (F17).

## Findings
Columns: location · issue · severity · fix · verifiable against a source?

- **F1.** Lines 733–734 · "downstream-minus-⏎upstream". Pandoc turns the line break into a space, so the .docx reads "downstream-minus- upstream". · med · join it into one word on one line. · yes (the source line)
- **F2.** Lines 1602–1603 · Limitation 2 ends a clause with "…error in the theory ⚠". ⚠ is defined (lines 4 and 1737) as a citation marker meaning "not opened or from earlier reading". Using it as a free-standing doubt flag gives a defined symbol a second meaning. · med · drop the ⚠, or write "(not tested)". · yes
- **F3.** Line 946 · Figure 1.10 caption: "A, B: one event per mean interval (25.5 and 53.6 events per recording;" never closes its parenthesis. · low · "(25.5 and 53.6 events per recording). C, D: …" · yes
- **F4.** Lines 1066, 1079–1081 and the Fig. 1.12 caption · "within 0.8–1.25, a ±25 % convention". 0.8–1.25 is −20 %/+25 %, a symmetric band only on a log scale, so "±25 %" asserts something false. · med · "within a factor of 1.25 of planted (0.8–1.25)". · yes
- **F5.** Lines 1097–1104 and the Table 1.5 title · "readable", "borderline to readable" and "not readable" are used as a criterion that is never defined. The table gives counts out of 40, and the reader cannot tell where "readable" begins (35? 38?). · med · define it once, e.g. "readable = at least 35 of 40 recordings in band", or report counts only. · yes (Table 1.5)
- **F6.** Lines 538–542 · Naming collision: "A first run of this grid … that repetition is what this chapter calls **the first experiment**". The second run is named "first", directly after a sentence that calls the discarded run "a first run". · med · call the discarded run "the shared-seed run" and do not use "first" for it. · no (judgment)
- **F7.** Lines 889, 956 and 1155, plus the Fig. 1.9 filename · Term drift. The chapter fixes "runs" (lines 542–544), then switches to "2 records" (889) and "pooled records" (956). "Record" already means a documentation record ("run record", "separation record"). · med · use "runs" throughout. · yes
- **F8.** Lines 227, 1168, 1170, 1159–1160, 1175 · One idea goes by five names: "one-per-hour allowance", "budget", "budget line", "chance floor", "event floor", and "safe threshold" on top. "Chance floor" (1.2.3) and "event floor" (1.6.1) are near-synonyms that differ only by the max(3, ·) and the null. · med · keep "allowance" or "budget" (one of them), "chance floor" for the formula and "event floor" only where the max-3 rule matters, with that difference stated once. · yes
- **F9.** Lines 148–166 · "Cell" is overloaded. The CFAR paragraph imports radar's "cell", "reference cells", "cell under test" and "guard cells" into a chapter where "cell" means neuron. Line 163 ("a second target in the reference cells") reads as neurons. The text itself switches to "reference stretches" at line 210. · med · keep the radar words in the history sentence only, and use "test instant", "reference stretch" and "guard stretch" when applying them. · no
- **F10.** Line 153 · Misplaced purpose clause: "…and Finn & Johnson (1968) analyzed the method in full, so that the rate of false alarms stays fixed while the background changes." The "so that" describes the method, not the analysis. · low · move the clause after "set it instead from an estimate of the background". · yes (Finn 1967 in <01-lit>; not reopened by me)
- **F11.** Lines 246–247 · "The window must be wide compared with the jitter, or it splits events, and narrow, or it gathers background." The ellipsis leaves "narrow" with no comparator, so it reads as "wide and narrow". · med · "wide enough to hold an event's jitter, and narrow enough to keep background out". · no
- **F12.** Lines 136–146 · The paragraph does five jobs: the floor values, the bias direction, the simulation agreement, the fixed-bin floor and the window dependence. Its "therefore" (line 141, "A threshold of 6 cells is therefore right…") follows the simulation-agreement sentence, but the conclusion rests on the floor computation two sentences earlier. Stray hard breaks at 141–142 and 145–146 are edit remnants. · med · move "A threshold of 6 cells is right for the lower background and far too low for the busier one" directly after line 136. · no
- **F13.** Lines 264–266 and 286–287 · "They serve only to choose where to simulate": the grammatical antecedent of "They" is "the fast stream and the slow stream", but the intended one is the realistic values. The same sentence then comes back 20 lines later ("the values only choose where to simulate"). · low · keep one occurrence, subject "These values". · no
- **F14.** Lines 631–636 · "The two can differ even under an exact theory": "the two" sits right after a sentence about the shipped pooled path against the per-recording path, but it refers to prediction against measurement (line 629). · med · move the sentence directly after line 631. · no
- **F15.** Lines 609–614 · "The theory predicts … though not exactly: … the tool misses the prediction … It yields an estimator…". After a sentence whose subject is "the tool", "It" can be read as the tool. · low · "The theory also yields…". · no
- **F16.** Line 1165 · "This explains why a fixed threshold does not carry across backgrounds" follows "measuring none tests nothing", so "This" points at the non-test. · low · "The formula's steepness in b explains…", placed before the K = 6 caveat. · no
- **F17.** Line 1170 · "a loose budget, not a strict one". "Not a strict one" repeats "loose". · low · cut "not a strict one". · no
- **F18.** Lines 1660–1662 (Conclusion) · "For 10-cell events, a window shorter than … undercounts participants, a fixed threshold drowns in chance clusters at a busier background, and those chance clusters then set the assessor's jitter reading." The 10-cell scope attaches to all three clauses, but only the first depends on k. · med · split it: "For 10-cell events, a window shorter than about six times the jitter undercounts participants. Whatever the event size, a fixed threshold…". · yes (1.5.2, 1.6)
- **F19.** Line 1016, topic sentence of the 1.5.6 comparison · "elsewhere the correlogram tool does as well". Table 1.3 contradicts it at 0.01 Hz/1.0 s (no pooled estimate, per-recording 0.86 with n = 5 against 1.01) and at 0.05 s (many recordings off the curve). The sentence asserts more than the table shows. · med · "elsewhere the correlogram tool does about as well where its calibration curve reaches". · yes (Table 1.3)
- **F20.** Line 220 · "about (m + ½) bin widths": m is used here but defined only in 1.7 (line 1317). · low · "about 2.5 bin widths (*1.7*)", or define m inline. · yes
- **F21.** Lines 458–459, 474 and 868 · The offset span is given three ways: "(N − 1) × 2w", "N·2w" and "N × 2w". · low · use one form, with "about". · yes (src tool)
- **F22.** Line 340 · "0.2, 0.5 and 8 s are run off its settings". "Run off" is an idiom an outside reader will misread. · low · "are run outside its shipped settings". · no
- **F23.** Line 382–383 · "The width is read above that level". The nearest level is the unexplained 0.859 at 2–3 s, but the tool reads above the 5–10 s level (line 396). · low · "above the 5–10 s level". · yes (tools/measure_jitter_correlogram.py)
- **F24.** Line 260 · "region of interest" is bolded as a defined term and never used again. · low · cut the parenthesis or the bold. · yes (Grep: 1 hit)
- **F25.** Lines 273 and 270 · "the goal page's working values" and "the simulator's generator notes" are repository-internal labels presented to an outside reader as sources. · low · "(working values from the project record)", with the link. · yes
- **F26.** Lines 12–26 · Order of definitions. Paragraph 1 uses "calcium events", "onset times" and "multichannel" before paragraph 2 defines them; the owner asked for every term at first use. · low · open with the paragraph-2 definitions, or define "onset" inline in paragraph 1. · no
- **F27.** Lines 1222–1224 (adjacent) and 860 · "the terms beyond the first are the at-most-one-event term" has a number disagreement. · low · "together form the at-most-one-event term". · no
- **F28.** Lines 1285–1287 · "The two sides are not given the same information": "sides" comes before either side is named. · low · "The likelihood-ratio tests and the tools are not given the same information." · no
- **F29.** Lines 1277–1278 · "Three analyses answer it": the three bullets that follow are two analyses and a conclusion. · low · "Two analyses, each checked by simulation, answer it." · no
- **F30.** Lines 1487–1490 · This paragraph restates the last three sentences of the Fig. 1.19 caption, and "at one event no test has power" appears twice within 20 lines. · low · cut the paragraph's first sentence and keep only the 0.80 ± 0.02 detail. · no
- **F31.** Lines 1176–1178 · Stray hard breaks ("is a related⏎statistic and⏎gives"), and a third statement of the 6/12 agreement after 1.2.3 and before 1.9.1. · low · reduce it to one clause pointing to 1.2.3. · no
- **F32.** Line 507 · "each cell's nearest onset … from every cell" is redundant. · low · "the nearest onset of every cell within ±1.5 s". · no
- **F33.** Lines 495–497 · Three prepositional phrases stack before the main clause ("Counting every active cell … in the 1 s bins within 1.5 s of each event, at 5 cells, about the safe threshold…, the two sets are close"). · low · "At a threshold of 5 cells (about the safe value for 1 s bins here), 450 of 450 sharp events and 442 of 450 jittered reach it." · no
- **F34.** Line 1471 area / Fig. 1.3 caption, line 319 · "In this figure cell 1 is at the top of the raster" implies other figures differ, and the reader wonders why. · low · cut it, or say what is different elsewhere. · yes (figure scripts)
- **F35.** Line 225 · "and so many that a call lands near event 4" has a stray "and". · low · "so many that…". · no

## Passage test (block words are estimates; the tool was not run)
| block | ~words | the one sentence it exists to deliver | where it sits | what the rest buys | verdict |
|---|---|---|---|---|---|
| 1.1 "How the chapter proceeds" (71–85) | ~230 | "Can what each tool returns be derived in advance, with simulation used only to check?" | last paragraph | a section-by-section preview that the headings already give. The house voice bans previews. | **cut to the question plus one sentence of order; promote the question** |
| 1.2.3 floor paragraph (123–146) | ~330 | "A threshold of 6 cells is right at 0.0096 Hz and far too low at 0.05 Hz." | line 141, near the end | the derivation (needed), plus the simulation agreement, the fixed-bin floor and the window dependence (three asides) | promote the payload; move the asides to a footnote-length sentence (F12) |
| 1.2.4 item 4 (221–231) | ~200 | "A fixed threshold drowns in a busier background; CFAR rises with it." | header | the clutter-edge detail and the 1.5/h interval: evidence a skeptic would want | keep, trim the cross-reference tail |
| 1.2.4 closing (245–254) | ~170 | "None of these properties is known before the analysis; they must be measured first." | middle | the setting-to-property mapping, which is needed | fine; fix F11 |
| 1.3.1 data and model (260–300) | ~500 | "Realistic values only choose where to simulate; the model is a hard-core Thomas process." | split across both ends | segment statistics a methods reviewer wants | cut the duplicate "only choose where to simulate" (F13) |
| Fig. 1.3 caption (304–319) | ~330 | "A window border can split an event; each tool counts something different." | middle (311–313) | the shading rule is said twice; three closing sentences are provenance | cut "A 1 s window border splits event 1 into 4 and 6" (a duplicate) and the last two sentences |
| 1.4 "The question, and the answer in brief" (599–624) | ~380 | "For one source, mostly yes, and it is wrong in specific, measurable places." | 604 and 619 | a preview of 1.5–1.8 that 1.9.1 and 1.10 repeat (the answer appears four times: here, the 1.5 opening, 1.9.1 and 1.10) | **keep this one; cut the 1.5 "In short:" preview (784–790) and shorten 1.9.1's first paragraph** |
| 1.4 "How the predictions are tested" (628–639) | ~200 | "The residual is the median ratio minus the predicted ratio; refusals bias the 5-cell, 0.05 Hz medians." | ends | the pooled-path digression | fix F14; the digression can go to 1.5.5 |
| 1.4 Prior work, cluster processes (706–719) | ~210 | "Cluster-process moments are textbook, and minimum-contrast fits across scales exist." | first two sentences | the Thomas-1949 provenance sentence and the Diggle & Gratton "not a cluster process" sentence: thoroughness, not evidence the reader needs | **cut both sentences (711–715)** |
| 1.5.6 joint-fit paragraph (986–998) | ~260 | "σ is identifiable only through how g₂ and g₃ change with w; the fit's weighting and uncertainty are ad hoc." | middle | honest caveats (keep) | fine; "below" at 995 is ambiguous, so write "in 1.5.7" |
| Fig. 1.11 caption (1020–1035) | ~290 | "The joint fit beats the correlogram per recording at 0.05 Hz from 0.5 s, and fails at realistic jitter." | absent | in-band counts that repeat Table 1.4 and Fig. 1.12 | cut the in-band counts from the caption |
| Fig. 1.12 caption (1063–1077) | ~300 | "Realistic values lie below the resolved region." | title | the per-point ranges are evidence; "box sizes are nominal" is fine | fix F4 only |
| 1.6.1 threshold paragraph (1167–1178) | ~210 | "A threshold must be set per recording from its own background." | first sentence (good) | the 0.0096-against-0.00964 detail is needed once; this is its third appearance (Fig. 1.13 caption, here, Fig. 1.16 caption) | keep it here; cut it from the Fig. 1.13 caption |
| 1.8.2 power closing (1487–1490) | ~70 | duplicate of the caption | — | nothing new except 0.80 ± 0.02 | F30 |
| 1.10 Conclusion (1652–1665) | ~210 | "Chapter 2's two-source sets test 1.5.3's prediction first." | last sentence | a recap, which the house voice bans; a dissertation convention may override that, and the author should say so | promote the forward pointer; fix F18 |

## What I checked
- The whole artifact, lines 1–1794, including captions, tables, About and References.
- The house rules in `docs/writing_conventions.md`: data plural, no "fire", American English, units.
- The banned list exactly as written in the role file.

I did not open the PNGs; rendered-figure checks belong to role 10. Table header units ("(ratio)" missing on Tables 1.3–1.5) fall under writing_conventions but are a mechanical check, so they are left to role 10. Nothing under `docs/reviews/` was read.
