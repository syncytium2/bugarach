GRANT 5 ok — Read, Grep, Glob (SubagentHandback is also present; it only delivers this report and edits nothing. No Edit, Write, NotebookEdit or shell.)

# Role 5, line editor: round 1

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html` (built file, 234 lines; line numbers below are the HTML's). Where a fix belongs in the generator, the source line in `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\tools\make_replicate_report.py` is given as `gen:NNN`.

## Finding about the run: the prose tool was not run
- `murderboard_prose.sh` **is not in either repo.** Glob `**/murderboard_prose*` returned nothing under `...\bugarach-worktrees\replicate-report\` or `...\bugarach\bugarach\`. I also hold no shell. **The tool was not run.** That is a failure of the run, not a clean result. Record it in the ledger: the checklist names a tool that does not exist in this tree.
- **What I did instead:** I ran the banned-construction search with Grep over the built HTML. Hits are pasted below. I counted words per block by reading, not by script, so treat each count as ±5%.
- **Which list I ran:** the house list from this role's checklist:
  - *not just X, but Y*
  - *it's not about A, it's about B*
  - *it's worth noting*
  - delve, leverage, robust, seamless, crucial, landscape, tapestry
  - *In today's ___*
  - a three-item list built for rhythm
  - an em-dash pivot into an uplifting close
  - I added: very, really, simply, clearly, essentially, basically, notably, importantly
  - House rules checked as well: singular "data", and British spellings.

## Banned-construction search: Grep output as returned
```
pattern (?i)\bnot just\b|\bnot only\b|it'?s not about|is not about|worth noting|\bdelve|\bleverag|\brobust|\bseamless|\bcrucial|\blandscape|\btapestry|in today'?s|\bvery\b|\breally\b|\bsimply\b|\bclearly\b|\bessentially\b|\bbasically\b|\bnotably\b|\bimportantly\b
53:simply

pattern \b[Dd]ata (is|was|has|does|itself|shows)\b|\bthis data\b
No matches found

pattern (?i)\b(centre|labelled|standardise|analyse|colour|behaviour|modelling)\w*
89:standardise

pattern "X, not Y" / "not X, but Y" / "rather than" (near-miss family)
58:  ...that measures agreement, not truth
128: ...rather than for the values'
146: ...The lone low dots are defects named in section 8, not draws
178: ...rewarding a long merge, not better detection
191: ...so the gap is a property of both draws, not of one
```
**How I judged each hit:**
- **53, `simply`:** a defect. It is filler ("some stretches are simply busy"). Cut the word (gen:792).
- **89, `standardise`:** a defect under the American-English house rule (Figure 2, the four learned architectures). Change it to "standardize" at gen:331. Re-render; do not patch the HTML.
- **58, 178, 191:** real contrasts. They are not the banned *not just X, but Y* form, so they stay.
- **146, "not draws":** see finding F4 (the pun on "draw").
- **128:** see finding P4 (the browser-viewer clause).
- **Em-dashes:** 26 of them. None is a pivot into an uplifting close. Every one sets off a definition or an aside.
- **Three-item lists:**
  - The heading at line 113, "Two selections, one shared budget, and a sliding coded side", looks built for rhythm. "A sliding coded side" means nothing until the reader has finished the section (finding F12).
  - The others are real triples: the subtitle's "Simulation only, fast stream, baseline only", the three reasons at lines 50–54, and "code, configurations and most of their training data" at line 134.

## Passage test: each block, its word count and its payload

**Where the payload sits:** first, middle or last.

**What the other words buy:**
- **E:** evidence a sceptic would ask for.
- **S:** the author's satisfaction at having been thorough.
- **R:** repetition of something stated elsewhere.

| block (line) | words | sentences | the one sentence it exists to deliver | payload sits | the other words buy |
|---|---|---|---|---|---|
| subtitle (25–27) | ~36 | 3 | One comparison, run twice on disjoint simulated recordings. | first | E, but WSMIP ids are unexplained (F2) |
| answer box, bullet 1 (31–34) | ~50 | 2 | Under the budget no net reached CoactDetect in either draw. | first | E |
| answer box, bullet 2 (35–37) | ~45 | 3 | On F1 alone the leading net and CoactDetect cannot be separated. | first | E; "at this size" is ambiguous (F9) |
| answer box, bullet 3 (38–41) | ~47 | 2 | An entry moves ~0.008 F1 between draws, so +0.011 was noise. | split | E; "entry" and "rehearsal" undefined (F3) |
| §1 ¶1 (45–49) | ~73 | 3 | A coordinated event is ROIs' events rising together more often than chance. | middle | E |
| §1 ¶2 (50–54) | ~79 | 4 | It is hard: few cells per event, chance coincidences, busy stretches. | first | E |
| §2 ¶1 (57–62) | ~78 | 3 | A simulator keeps the answer key; this one is fitted to real baseline recordings. | middle | E; last sentence broken (F7) |
| §2 ¶2 (63–73) | ~130 | 4 | What a bench recording contains, and how F1 is scored. | none (two payloads) | E; split it (F8) |
| §3 ¶1 (76–81) | ~70 | 1 | The six coded detectors, one clause each. | n/a | E; one sentence joined by semicolons, better as a list |
| §3 ¶2 (82–88) | ~100 | 4 | tube is the control that cannot count cells. | middle | E |
| Fig 2 caption | ~95 | 6 | tube averages before learning; the others keep one vote per cell. | middle | E; "the shaded box" is ambiguous (F15) |
| §4 ¶1 (91–96) | ~80 | 3 | Nested CV: everything is chosen on 3 folds, scored once on the 4th. | last | E |
| §4 ¶2 (97–104) | ~100 | 4 | Inner fits choose the configuration; the refit is scored once. | first | E; the arithmetic "6 distinct fold pairs" is left open (F16) |
| §4 warning (105–111) | ~115 | 6 | A shared-training defect was fixed and a check proves it; both runs passed. | first + last | E/S; mixed fold indexing (F5) |
| §5 ¶1 (114–120) | ~105 | 6 | Under the budget, every entry is held to 1.6× CoactDetect's false alarms. | middle | E; "one ceiling" contradicts the "three ceilings" of Figure 4 (F6) |
| §5 ¶2 (121–129) | ~120 | 5 | The reference is the sliding CoactDetect, because the binned one is known worse. | **last** | S (P4) |
| Fig 4 caption | ~75 | 4 | Three ceilings, each 1.6× CoactDetect's rate on training recordings. | last | E; hard to parse (F17) |
| §6 (132–139) | ~115 | 6 | One run cannot measure its own noise, so it was run twice on disjoint seeds. | middle | **S**: last 2 sentences (P1) |
| Fig 5 caption + SVG text | ~90 | 5 | The two runs differ only in recordings. | last (SVG) | **R**: third time said (P2) |
| §7 ¶1 (142–145) | ~55 | 2 | CoactDetect is steadiest: 0.748 in both draws. | middle | E; "two columns identical in both" is ambiguous (F14) |
| §7 ¶2 (147–149) | ~30 | 2 | The median entry moved 0.008 F1; none moved more than 0.027. | last | "The joins are short" is figurative (F13) |
| Fig 7 caption | ~50 | 2 | Bold marks the defects; nothing else moved more than 0.027. | last | the definition is circular (F18) |
| §8, collapse (153–162) | ~125 | 7 | Inner selection at 3 seeds can pick a configuration that fails at refit. | **last** | **S**: sha, `tiny` digression (P3) |
| Fig 8 caption | ~50 | 3 | 2 of 5 refit seeds fail, in both selections. | last | ambiguous grammar (F19) |
| §8, no admissible (165–170) | ~75 | 3 | locust and one binned SCE fold are not results. | last | E; the "quiet busy" collision (F1) |
| §8, grid edge (172–178) | ~100 | 3 | SCE's F1-alone lead may be the merge gap exploiting wide spacing. | **last** | E; the lead is asserted without its number (F10) |
| Table 2 + caption (179) | ~40 + table | 2 | All six sat at the top in 8 of 8 folds. | n/a | **R**: every row is "8 of 8" and the prose already says "every fold for all six" (P6) |
| §9, bullet 1 (182–185) | ~55 | 2 | Median move 0.008, max 0.027. | first | **R**: fourth statement of these two numbers (P2) |
| §9, bullet 2 (186–193) | ~100 | 4 | The budgeted gap holds in both draws, and both entries are steady. | middle | E; one false clause (F0), "share nothing" (F11) |
| §9, bullet 3 (194–196) | ~40 | 2 | The F1-alone difference flips sign within the noise. | first | **R**: near-verbatim answer box, bullet 2 (P2) |
| §9, bullet 4 (197–200) | ~50 | 2 | Tuning helped line_length beyond noise in both draws. | first | E |
| §10, bullet 1 (204–207) | ~55 | 3 | Nothing here covers drugs or the slow stream. | middle | the date is a lookup key (F20) |
| §10, bullet 2 (208–217) | ~140 | 5 | The bench was fitted on a flawed export; re-fitting on the corrected one gives the same constants. | **middle** | **S**: HANDOFF filename, "item 3", "Tony", closing line (P5) |
| §10, bullets 3–4 (218–220) | ~35 | 3 | Simulation only; no crowded check. | first | E |
| §11 (224–232) | ~120 | 5 | Where the results and the builder live. | n/a | E |

About 2,900 words of prose in all. The recap load is the biggest single cost. Four numbers each appear in 3 to 5 places:

| number | places it appears |
|---|---|
| median move 0.008 | answer box, bullet 3; §7 ¶2; §9, bullet 1 |
| max move 0.027 | answer box, bullet 3; §7 ¶2; Fig 7; §9, bullets 1 and 3 |
| F1-alone −0.012 / +0.006 | answer box, bullet 2; §9, bullet 3 |
| rehearsal +0.011 | answer box, bullet 3; §6; §9, bullet 1 |

## Findings

**Columns:**
- **Sev:** H is high, M is medium, L is low.
- **Verifiable:** can the finding be checked against a source? Most answers are "yes (text)", meaning the artifact's own text proves it.

| # | location | issue | sev | suggested fix | verifiable |
|---|---|---|---|---|---|
| F0 | §9, bullet 2, lines 187–189 (gen:1009–1010, hard-coded prose) | **False sentence.** "trails by 0.030 and 0.025 F1: about 3 times the median move, though not beyond the largest." But 0.030 > 0.027, so the first draw's gap *is* beyond the largest move. The clause is literal text while the numbers are computed, so it cannot follow the data. | H | Compute the clause, for example: "0.030 exceeds the largest move of any entry (0.027); 0.025 does not." | yes (text: 0.030 vs 0.027, same page) |
| F1 | §8, line 167: "the quiet busy stretch". Also §2 line 68–70, Fig 1, Fig 4 SVG "quiet 10.3 / busy 8.0 / hour" | **"Busy" names two different things.** It names a background level (the 75th percentile rate) and a 5-minute stretch inside every recording. "Quiet busy stretch" and a Figure 4 box reading "busy 8.0 / hour" (busy-stretch calls at the busy background) make the reader stop and decode. | H | Rename one of them. The backgrounds could become "low-rate / high-rate", keeping "busy stretch" for the stretch. Or rename the stretch ("the decoy-rate stretch"). Apply it in the generator and the SVG labels. | yes (text) |
| F2 | subtitle (26–27); used 15 times | **WSMIP064 / WSMIP065 are indexed, not named.** The reader first learns they are workstations in §10 ("Both workstations"). The house rule is: name things; don't index them. | H | At first use: "run on two workstations, WSMIP064 (seeds 1000–1047) and WSMIP065 (seeds 2000–2047)". Then say "the first draw" and "the second draw" in running prose, and keep the ids for the legend and §11. | yes (text) |
| F3 | answer box, bullet 3 (38, 40); §5 (114) | **Two terms are used before they are defined.** "Entry" appears at line 38 but is defined only by use at §5 ("Every entry is chosen twice"). "The rehearsal run" is never defined: what it was, and on which seeds. | M | Define "entry" once: a detector or net under one selection rule, which is one row of Table 1. Add one clause to §6: "the rehearsal run, an earlier single run of this comparison on seeds …". | yes (text) |
| F4 | "draw" across the page, especially §9 line 189 "more than a draw", Fig 6 line 146 "not draws" | **"Draw" is a pun here.** It means both a replicate and a tie. "What makes it more than a draw" reads as "more than a tie". "Draw", "run" and "replicate" name the same thing, and "draw" is never defined. | M | Define it once: "each run is one draw of 48 recording seeds". Then use "draw" only in that sense. Rewrite line 189 as "What makes the gap more than draw-to-draw noise …" and line 146 as "…not movement between draws". | yes (text) |
| F5 | §4 warning, lines 107–108 (gen:872–873) | **Mixed fold numbering.** "held-out folds 3 and 4 (counting from 1)". Every figure and §8 count folds from 0 (Fig 3 "fold 0", §8 "fold 1", "fold 2"). "Four folds were then three fits" is too terse to parse. | M | "held-out folds 2 and 3 both trained on recordings 1000–1009, so the four folds held only three distinct trained nets and were not four independent looks." | yes (text) |
| F6 | §5 ¶1, line 117 (gen:891) vs Fig 4 | "false alarms stay within **one ceiling**" contradicts Figure 4's "the **three** ceilings" and "all three ceilings". | M | "within one shared budget of three ceilings (Figure 4)". | yes (text) |
| F7 | §2 ¶1, lines 59–62 (gen:816) | **A broken sentence and an undefined term.** "…before any drug), fast stream: the lab's two event streams…". The ", fast stream:" attaches to nothing. "Stream" is jargon a new reader has not met. | M | "…before any drug). The lab records two event streams, fast and slow [one clause saying what distinguishes them]; the bench and this work use only the fast one." | yes (text) |
| F8 | §2 ¶2, lines 63–73 (gen:822) | **A misplaced modifier and a 48-word sentence.** "each cell's onset scattered by 0.36 s…, spaced at least 120 s apart" reads as the onsets being 120 s apart, but the events are. The F1 sentence packs a definition, a match tolerance, pooling and averaging into one. | M | "It carries 15 planted events, at least 120 s apart: 5 each recruiting…". Give F1 its own paragraph: define it, then "A call matches an event within 2.5 s. Scores are pooled over a fold's recordings at each background, then averaged over the two." | yes (text) |
| F9 | answer box, bullet 2, line 37 (gen:775) | "the question is not settled **at this size**": the size of what? Recordings, folds or effect? | L | "is not settled by 48 recordings per draw" (or whatever is meant). | no (intent unknown) |
| F10 | §8, grid edge, line 177 | "SCE's lead on F1 alone" is the first mention of any SCE lead. Neither the answer box nor §7 says binned SCE leads anything. The block's payload rests on a claim the page never states. | M | State the number where the claim is made: "binned SCE's F1-alone score (x.xxx, the highest on the page)". Check with role 4 that the lead is real. | no (would need Table 1 values; the table sits on one over-long line I read only in part) |
| F11 | §9, bullet 2, line 193 (gen:1014) | "two draws that **share nothing**" overstates. Figure 5 and §6 say they share everything except the recordings. | M | "two draws that share no recordings". | yes (text) |
| F12 | §5 heading, line 113 | A three-item heading built for rhythm, with an opaque third item ("a sliding coded side"). | L | "Two ways to choose, and the false-alarm budget both are held to". | yes |
| F13 | §7 ¶2, line 147 (gen:947) | "The joins are short": figurative, and "joins" is never introduced. The Figure 7 caption does not mention them. | L | "The two draws agree closely:" | yes |
| F14 | §7 ¶1, lines 143–145 | "0.748 and 0.748 in the two draws, and its two columns are identical in both" leaves "which two columns" to the reader. | L | "CoactDetect scores 0.748 in both draws, and the same whether chosen on F1 alone or under the budget, because the budget is built from its own settings." | yes |
| F15 | Fig 2 caption (89) | "The shaded box in tube's row": every stage box is shaded, and tube's differs only by tint. | L | Name the tint, or say "the average-over-ROIs box". Role 10 owns whether the tint is legible. | yes |
| F16 | §4 ¶2, lines 98–100 | The sum "(24 configurations × 3 seeds × 6 distinct fold pairs)" invites the reader to ask why not 4 × 3 = 12 pairs. The text never says fits are shared between outer folds. | L | Add one clause: "each pair of training folds recurs in two outer folds and is fitted once." | no (needs code) |
| F17 | Fig 4 caption (130) | One 45-word sentence with a nested "per hour of that stretch at each background" and a parenthetical. | L | Split it: "Three rates are measured: CoactDetect's calls per hour in the busy stretch at each background, and on the empty recording. Each is multiplied by 1.6." | yes |
| F18 | Fig 7 caption (150) | Circular. The bold threshold (0.027) is defined by the non-defect rows, and then "those bold rows are the defects". "Section 8" is an index, not a name. | L | "Bold rows are the entries with a named defect (the three things that are not the models); every other entry moved at most 0.027." | yes |
| F19 | Fig 8 caption (163) | "the hatched bars are the 2 that failed, at F1 0.125 chosen on F1 alone and at 0 under the budget": are these the same two seeds? The grammar does not say. The §8 prose mentions only the F1-alone selection. | L | "The same 2 seeds fail under both selections: F1 0.125 with the threshold chosen on F1 alone, and 0 under the budget, whose threshold calls nothing." | yes (SVG labels name seeds 1 and 2 in both) |
| F20 | §10, bullet 1 (204), bullet 2 (214); subtitle (27) | Dates used as content: "By decision of 2026-09-17", "on 2026-09-17". "This training run" is singular in a two-run report. | L | "By a project decision, these runs use…". Drop the date or move it to §11. | yes |
| F21 | §10, bullet 2, line 215–216 | Ambiguous antecedent: "Both workstations re-measured the … eight fitted constants … **one of them**, the share of ROIs…". "One of them" could mean a workstation or a constant. | L | "One constant, the share of ROIs an event recruits, …". | yes |
| F22 | §3 ¶2, lines 86–88 | "24 configurations drawn at random … one of them the untuned default": is the default drawn at random, or added? | L | "23 drawn at random plus the untuned default" (if true). | no (needs the tuner) |
| F23 | §5 ¶2, line 126 | "a 1 s guard": "guard" is undefined. | L | Add a gloss, or drop the setting from the list. | yes |
| F24 | subtitle (25); §4 (104); §5 (125); §8 (175, 177) | "goal-2", "goal 1" are internal project labels, undefined for a new reader. | L | Name them once: "goal 1, the earlier tuning of the coded detectors against crowded recordings" and so on. | yes (text) |

### Passage-test cuts (the words buy S or R)

| # | block | cut or move | what the reader keeps |
|---|---|---|---|
| P1 | §6, lines 136–139 | Cut "the two declarations differ in exactly 2 entries, `recording_seeds` and `replicate`. `--replicate 0` declares, byte for byte, …resumable while this option was added." This is engineering provenance, and it also brings in a second meaning of "entries" (see F3). Move it to §11 beside the `--replicate` pointer. | "They share no recording, and nothing else differs." |
| P2 | the noise numbers ×4, Fig 5 ×3 | Recap. §9's bullets 1 and 3 restate the answer box almost word for word. "Nothing else differs" is said in §6, the Fig 5 caption and the Fig 5 SVG. | Keep the numbers in the answer box and §7. In §9, keep only what the answer box lacks: bullet 2's steadiness argument and bullet 4. Give the "only recordings differ" line once, in §6. |
| P3 | §8, collapse (153–162) | Cut the config hash `75d4474550026cfa` (a lookup key; it can go in Fig 8 or §11). Cut the `tiny` digression, which relies on "published run", undefined. **Promote** the last-but-one sentence, which is the payload. | Lead with: "Inner selection scores each configuration at only 3 training seeds, so it can choose one that fails to train at refit. In the second draw's fold 1 it did: chorus_norm's chosen configuration failed at 2 of 5 refit seeds and the fold's score fell from 0.745 untuned to 0.501." |
| P4 | §5 ¶2 (121–129) | The payload is at the end and the clause before it is inside baseball ("held back for the browser viewer's sake rather than for the values'"). | "The reference is the sliding CoactDetect, not the binned version the code still ships. The binned versions lose 30–36% of their calls when a recording shifts by a fraction of a second, and comparing against a detector known to be worse would not be fair." Then the settings. Also replace "That fixed detector runs sliding" with "is the sliding version". |
| P5 | §10, bullet 2 (208–217) | The `HANDOFF-…md` filename, "item 3 of the decisions waiting on Tony", "at the root of `main`" and "untouched" mean nothing to a new reader (and "Tony" is never introduced). "None of this makes the results wrong; it is a thing a reader must be told" echoes the heading and makes a claim the bullet does not support. **Promote** the re-measurement, which answers the worry. | "The bench was fitted on an export with a known motion-correction defect (12 ROIs pinned to the floor in 4 recordings, about 0.03% of events). Re-measured on the corrected export, all eight constants came out the same, within their bootstrap intervals. Switching the bench to the corrected export is still an open decision." |
| P6 | Table 2 | Every row reads "8 of 8"; the table asserts one fact, which the prose already states. Its only extra content is the name of each detector's setting. The caption also brings in a third name for the merge gap ("call-fusing setting"). | Either fold the setting names into the §8 sentence and drop the table, or keep it and say "merge gap" throughout. (Role 9 or 10 may weigh in on the table's form.) |

## What I checked
- **All body prose**, lines 24–233.
- **Every figure caption** (Figures 1–8), read in full through anchored Grep.
- **The explanatory text inside the Figure 2, 4 and 5 SVGs.**
- **The header notes of Tables 1 and 2.**
- **Not read:** the cell values of Table 1 (on the over-long line 146) and the image payload of line 55.
- **Also read:** `%USERPROFILE%\bugarach\bugarach\docs\writing_conventions.md`, and the generator at the lines cited.

Relevant paths:
- `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`
- `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\tools\make_replicate_report.py`
- `%USERPROFILE%\bugarach\bugarach\docs\writing_conventions.md`
