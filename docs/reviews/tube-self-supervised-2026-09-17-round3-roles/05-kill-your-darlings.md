GRANT 5 ok — Read, Grep, Glob

# Line editor review of the rigid-shift report (`docs/learned/tube_self_supervised/README.md`)

**Artifact:** `<worktree>/docs/learned/tube_self_supervised/README.md` (481 lines)

**What I checked:** every line of the artifact. I also checked it against `docs/writing_conventions.md`, the glossary (`docs/GLOSSARY.md`), and the writing and plot sections of the project's `CLAUDE.md`. I made two lookups in the code: one to learn what the leak-test score is, and one to learn what "untrained" means. I opened no review records, handoffs or todos, and followed none of the artifact's links to them.

**The search tool was not run.** `murderboard_prose.sh` is not in this repo, and my grant has no Bash. I did the construction search by hand and with Grep. I counted words per block by eye, so the counts below are close but not exact. I ran the banned list exactly as it appears in the role 5 instructions of the vendored review process, and I added the house rules named in the task.

## Count table (done by hand)

### Constructions

| line | construction | kind |
|---|---|---|
| 1 | "what it hides, what it destroys, and what training on it alone buys" | a three-item title built for rhythm; it leaves out the bake-off (Figure 2) |
| 356 | "rank whole-train shifting most **robust**" | banned word, used to report Stella 2022 |
| 411 | "ranked most **robust** by Stella et al. 2022" | banned word, used to report Stella 2022 |
| 85 | "on **today's** `main`" | the "In today's" pattern; not an opener, but it goes stale |
| — | *not just X, but Y* / *it's not about A* / *it's worth noting* / delve, leverage, seamless, crucial, landscape, tapestry / em-dash pivot into an uplifting close | none found |
| 16, 398 | initialisation | British spelling (house rule is American English) |
| 59, 427 | centre, centre-surround | British spelling; "centre-surround" is the exact case `writing_conventions.md` cites |
| 224 | unlabelled | British spelling |
| 380 | behaviour, behavioural | British spelling |
| 402, 404 | localise, realise | British spelling |
| — | singular "data" | none found |

### Blocks over about 80 words

| block | words (approx.) | sentences |
|---|---|---|
| Summary bullets, lines 5–21 | 180 | 10 |
| Blockquote, lines 23–34 | 110 | 7 |
| What changed, lines 67–89 | 290 | 8 |
| Figure 1 caption, lines 95–104 | 150 | 4 |
| Aggregate gate, lines 125–130 | 90 | 1 |
| Aggregate ⚠ paragraph, lines 132–136 | 75 | 3 |
| Coverage ⚠ paragraph, lines 273–282 | 180 | 6 |
| Edge-enrichment ⚠ paragraph, lines 336–343 | 150 | 6 |
| Lanes-over-raster note, lines 345–349 | 90 | 4 |
| Lineage, lines 409–414 | 95 | 3 |
| CFAR paragraph, lines 423–431 | 130 | 5 |

## Findings

| # | location | issue | severity | suggested fix | verified against a source |
|---|---|---|---|---|---|
| 1 | 6, 11–12, 107–111, 116, 120–130, 133–134, 396 | **The Figure 1 score is never named.** Every number (0.49, 0.74, 0.558, 0.664…) is a quantity with no name. `tools/look_rigid_shift_controls.py` shows it is held-out classification accuracy, where 0.5 is chance. | high | Say once, in the summary and the Figure 1 caption: "held-out accuracy, 0.5 = chance". Put "(accuracy)" in the table header. | yes (`tools/look_rigid_shift_controls.py`, lines 90–159) |
| 2 | 284–290 | **The paired-check score is also unnamed** (0.720–0.774, etc.). "Ties … counted as half" suggests a share of crop pairs where the real crop scores higher, but the page never says so. | high | Name the quantity and say what 0.5 means. | no (source not opened) |
| 3 | 439 | **"Two more names in Figure 2" is followed by three names:** SPIKE-synch, locust and binned SCE. | high | "Three more names…" | yes (in the text) |
| 4 | 313–315 | **The comparison mixes quantities.** "median 0–1 within ±2 frames, against 0.07–0.13 for random times" sets a median ROI count beside what looks like a share with at least three ROIs. The random row in the table (line 307) gives medians of 0–1 and shares of 0.06–0.18, and 0.07–0.13 matches neither. | high | Compare median with median and share with share, and quote the same subset the table shows. | yes (in the text) |
| 5 | 5–21 | **The summary uses terms before the page defines them:** ROI and F1 (defined at line 36), per-onset dither, shared offset, aggregate-channel gate, counting builds, second sensor, truth-reading, label-free thresholds, arm, trained cells. A cold reader cannot parse the first bullets. | medium-high | Either move the terms paragraph above the summary, or rewrite each bullet in plain words ("the model that counts lit ROIs", "the threshold chosen by looking at the planted events"). | yes |
| 6 | 17, 19, 265–269; 36; 423–429 | **"Cell" has three meanings.** It means an imaged cell (line 36: ROI = "one imaged cell"; line 429: "capping each cell at one vote"), a table cell or condition ("every trained cell is ahead"), and the radar "cell under test" (line 427, never defined on the page). | medium-high | Call conditions "rows" or "model × arm × displacement", and define or gloss "cell under test". | yes |
| 7 | 138, 155, 173, 390, 469 | **"Probe" has two meanings on one figure.** "Probe firings" are calls in the promiscuity-probe stretch of the benchmark. "The plant probe" is Panel B. The table sits under a heading that names the plant probe, so "probe firings" reads as firings on the plants. | medium | Rename the column "promiscuity-probe firings (calls per fold)". | yes (glossary: promiscuity probe) |
| 8 | 9, 76, 125, 132, 359, 476 | **One test has four names:** aggregate-channel gate, aggregate gate, aggregate test, aggregate leak. It is also called a "gate" and a "test", which suggests two different things. | medium | Pick one name, for example "the aggregate leak test", and use it everywhere. | yes |
| 9 | 9–12 | The bullet says the gate "gives the same answer" but never says what the answer means: real recordings *do* separate from rigid shift at 0.65–0.68. "Read off what a fitted `tube` or `line` actually receives, real recordings separate…" reads as an order to the reader, and the grammar breaks. | medium | "On the channels a fitted `tube` or `line` receives, real recordings separate from their rigid shift at 0.65–0.68 accuracy, as they did from the initial parameters, while the shared offset stays at chance (0.48–0.53)." | yes |
| 10 | 57 | "Does rigid shift hide from a detector of everything except alignment" is very hard to parse, and it is the question Figure 1 exists to answer. | medium | "Can a classifier that cannot see alignment tell rigid shift from a real recording, and does rigid shift remove alignment?" | yes |
| 11 | 59, 150–153, 252, 279 | **Undefined jargon.** "counting architecture" and "counting builds" (the page never lists them: `line`, `line_bound`, `line_length`), "the centre-surround one" (= `tube`, not named), "tube family", "smear", "ink" / "plant of equal ink" (146, 198), "head" (103, 215), "initial bank" / "fitted banks" (126, 133–134, 476), "cells-mean trace" (133), "twin" / "unplanted twins" (128, 287), "thin event" (309), "bench" (216, 363–365), "empty-field floor" (74), "edge-of-grid guard" (82, which also collides with `tube_guard`), `fold_maker` (83), "the earlier look" (122), "the Elephant virtual environment" (453). | medium | Define each at first use in a clause, or replace it with the plain thing. | yes |
| 12 | 169, 445; 411; 384 | **Abbreviations never spelled out:** SCE (in "binned SCE"), SPADE, EEG. | low-medium | Spell each out at first use. | yes |
| 13 | 7, 12, 15, 21, 58, 60, 61, 358, 360, 377, 420, 439 | **Figure references carry the number but not the name**, which the plot conventions require: "Figure 3, the candidate field". Line 358's "(Figure 1, panel B)" also depends on the reader working out that panel B is the slow stream. The caption (95) never says which of Panels A and B is fast and which is slow. | medium | Add the name ("Figure 1, the leak tests"), and say "Panel A lab fast, Panel B lab slow" in the caption. | yes |
| 14 | 15, 193, 389; 152; 331 | **Bare positional labels.** "The second sensor" (use "the concentration channels"), "keeps only the first" (use "keeps only relative length"), "the first column … the second column" (name the column). | medium | Use the names. | yes (CLAUDE.md, writing conventions) |
| 15 | 329–331 | "so the first column rewards firing more, and the second column is the one that bounds it": "bounds it" has no clear subject or object. | medium | "…so overlap with the references rises with firing rate. The share of the model's own events near a reference is the fairer column." | yes |
| 16 | 81–84 | **Broken parallel structure.** "picked by … with its edge-of-grid guard, over a grid that…; with the validation recordings…; and, for the arm…, not on recordings that arm was trained on." The three fixes do not read as three fixes. | medium | Split into three sub-bullets: grid reaches the lowest score; two validation recordings, not four; the arm trained on simulated recordings is not thresholded on its own training recordings. | yes |
| 17 | 67–89 | **Passage test.** The payload is "six fixes since the reviewed version, each of which moved a number". The remaining ~250 words mostly repeat material placed later: `line_bound` is described again at 152–153, 367–368 and 430–431; the positive controls in the Figure 1 and Panel C text; the grid at 280–282; the seeds in the Figure 2 caption. The detail serves a reader of the old version, not a sceptic of this one. | medium | Cut to one line per fix, each pointing to where the fix shows. Keep the `line` docstring correction here only. | yes |
| 18 | 125–130 | **Passage test.** One 90-word sentence holds eight ranges in four parallel pairs, which makes it a table set as prose. The payload ("fitted channels agree with the initial bank on all four comparisons") is only in the bold lead. | medium | Use a 4 × 2 table: rows are the comparisons, columns are initial bank and fitted heads. | yes |
| 19 | 336–341 | **Passage test.** The same table-as-prose problem: six pairs of percentages in one sentence. "Window edge" is also ambiguous: the glossary's analysis window is the 60 s cut, but a 0.84 % expectation within 5 s implies a window of about 20 minutes. "is involved" is a hedge. | medium | Use a table with rows for detector and rule and columns for within 5 s and within 12.8 s. Name which window. Replace "is involved" with "moves the enrichment". | yes (arithmetic) |
| 20 | 132–136 | "So the test rules out a leak on these channels that the shared offset would also carry, and nothing about co-activity itself." The verb does double duty and the sentence reads wrongly. | medium | "So the test can rule out only a leak that the shared offset would also carry. It says nothing about co-activity." | yes |
| 21 | 273–276 | Paired ranges with no "respectively": "reach 0.50–0.56 and 0.50–0.58", "cover 0.962–0.984 and 0.954–0.985". The widths (23–128 s) do not say whose they are. | low-medium | Give each arm its own clause. | yes |
| 22 | 268–269 | "no architecture approaches **its own** supervised score", but the evidence is the best trained row overall (0.322) against the range across all supervised models (0.519–0.674). | low-medium | Either compare each model with itself, or say "no trained row approaches any supervised model". | yes |
| 23 | 270–271 | "Between 0 and 4 fits of each cell of twelve ended at or above chance loss" is garbled. | low | "In each row, 0 to 4 of the 12 fits ended at or above chance loss (ln 2 = 0.693)." | yes |
| 24 | 16 vs 223, 398, 368 | **"Random initialisation" (16)** against "untrained" (223), "initialisation" (398) and "hand-set widths" (368). The tool describes the untrained arm as "the architecture at initialisation", and the page itself says some initial parameters are hand-set. "Random" may be wrong. | low-medium | Say "untrained (at registered initial parameters)" throughout. | partly (tool docstring, line 32; whether it is random is not verified) |
| 25 | 198–200 | "fuzz (the same ROIs spread over 2.9 s)" and "wave (the same ROIs one frame apart)": the same as which, the line plant's ROIs or the burst's quarter? How many onsets each? | medium | Say which ROIs, and how many onsets each. | yes |
| 26 | 204 | Header "plant 4 / 8 / 16" has no unit. Line 199 implies ROIs. | low | "plant size 4 / 8 / 16 ROIs"; state that the ratios are dimensionless. | yes |
| 27 | 181, 243, 257, 301 | **Missing units in headers:** the paired-difference table needs ΔF1; the threshold tables never say their cells are F1; the ≤ 0.5 and ≤ 1 columns lack SD while ≤ 2 has it; line 301 puts ±2 frames beside ±1 s with the conversion (0.1 s per frame) 70 lines earlier. | low-medium | Add "(ΔF1)" and "(F1)" to headers, and "(±0.2 s)" beside ±2 frames. | yes (writing conventions, units section) |
| 28 | 155, 390 | "probe firings" 3.25 / 4.42: a count with no unit. | low | "calls per fold". | yes |
| 29 | 181 | "without the largest fold" is ambiguous: largest by what? It is the largest difference. | low | "without the fold with the largest difference". | yes |
| 30 | 185 | "−0.000" | low | Print "0.000" or add a digit. | yes |
| 31 | 116–117 | "Its lowest interval bound on this stream is 0.70": whose bound, and which end? | low | "Dither's lowest lower 95 % bound on the fast stream is 0.70." | yes |
| 32 | 122–123 | "the shared offset, which moves each ROI identically": identically to what? The argument needs "exactly as rigid shift moves it". | low | Reuse the wording from line 113. | yes |
| 33 | 120–121 | The slow-stream displacements (11.2, 22.4, 44.8 s) differ from the fast stream's (10, 20, 40 s), and the page never says why. | low | One clause giving the matching rule. | no |
| 34 | 309–311 | "The random rows … which is why their range spans the detectors": the table has one random row, and the "which is why" clause does not follow. | low-medium | Say what the random row is matched to per detector and what its range covers. | yes |
| 35 | 345–349 | **Passage test.** The payload is "no raster view accompanies this run". The rebuild command, the darkroom claim and the FOUNDATIONS §5 release rule are work notes for the author, not evidence for a reader. "§5" is a bare index, and "releases by name only" is opaque. | medium | Cut to one sentence here; move the command to the provenance section. | yes |
| 36 | 355 | "three orders of magnitude": 25 ms to 10–20 s is 400–800 times, about 2.6–2.9 orders. | low | "400 to 800 times its published regime". | yes (arithmetic) |
| 37 | 409–412 | One 55-word sentence with a chain of "which" clauses. "and ranked most robust by Stella" attaches as if to Louis 2010. This is also the second "robust" hit. | medium | Split: "Whole-train shifting is Pipa et al. 2008. Louis, Borgelt &amp; Grün 2010 recommend it and credit it jointly to Pipa and Harrison &amp; Geman 2009. Stella et al. 2022 found it the least distorting for SPADE (…) at a 25 ms dither." Use Stella's own criterion instead of "robust". | yes |
| 38 | 428 | "The label-free threshold rule is better described as a surrogate threshold." Better than what? The sentence stands alone. | low | "…is closer to Dard's surrogate threshold than to CFAR." | yes |
| 39 | 85 | "on today's `main`" will be wrong within a day. | low | "on `main` as of 70201e7". | yes |
| 40 | 1 | The title is a three-part list built for rhythm. "Hides" and "destroys" are both Figure 1, and the bake-off, a whole figure, is missing. | low | Name the three findings the page actually delivers, or drop the list. | yes |
| 41 | 63, 294 | "what these models call on real tissue": "call" is ambiguous (call a detection, or call it something?), and "tissue" does not match the section title, "On real recordings". "nothing in this folder is annotated": which folder? | low | "A fourth, how these models behave on real recordings, follows the figures." Name the export folder. | yes |
| 42 | 391 | "bounding the vote in time adds −0.004 F1" | low | "changes F1 by −0.004". | yes |
| 43 | 17 | "nowhere near supervised training" is vague when the number exists. | low | "…its best row reaches 0.322 F1 against 0.519–0.674 supervised." | yes |
| 44 | 238, 150–151 vs glossary | **The page and the glossary use different names.** The page says "truth-reading threshold"; the glossary says "oracle threshold". The page says "concentration channels"; the glossary says "orientation channels". The page also calls relative length "that count", but the glossary defines it as a mean over ROIs, not a tally. | low | Align one side (the page's names are clearer), and say "share", not "count". | yes (`docs/GLOSSARY.md`, lines 390, 400–410) |
| 45 | 224 | "with no labels on unlabelled simulated recordings" says the same thing twice. | low | Drop "with no labels". | yes |
| 46 | 16, 59, 224, 380, 398, 402, 404, 427 | British spellings (see the count table). | low | Change to initialization, center, unlabeled, behavior, localize, realize. | yes (writing conventions, American English section) |

## Blocks that passed the passage test

- **Lines 113–118:** the payload is at the end ("a leak confined to single ROIs … would have been caught"). It earns its length.
- **Lines 192–196:** the payload comes first. Good.
- **Lines 211–217:** the three reasons are three real reasons, not a rhythm list.
- **The "What this does not settle" section, lines 353–385:** each bullet states one thing the page does not know. This is the voice the house style asks for.
- **Line 362:** "a two-ROI coincidence earns as much as a crowd" is the kind of concrete example the house style wants.

## Outside my role (not verified)

The docstring at `tools/look_rigid_shift_controls.py` line 90 reads "fixed fits, no refit". The Figure 1 caption (line 100) says "refitting bootstrap". The page may be describing a different code path in the same file.
