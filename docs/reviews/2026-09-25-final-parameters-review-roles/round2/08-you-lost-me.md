GRANT 8 ok — Read, Grep, Glob (also holds SubagentHandback, the report channel only; no editing tool)

# Role 8 — "You Lost Me": naive-reader review
Artifact: `docs/learned/runs/2026-09-25-final-parameters/README.md` + its four PNGs (all four opened). Each section was read cold and checked against `docs/GLOSSARY.md`.

**Scoring note:** the page defines some terms only in the Definitions list at the end, and says so at the top. A term defined in its section, or in that list, counts as defined; a term defined nowhere on the page counts as undefined, and the ≥3 rule is applied to those.

## Per-section verdict

| section | terms/identifiers first used here | defined on page? | cold reader follows? |
|---|---|---|---|
| Intro (L1–13) | event floor, budget, chorus models, operating point, `bench*.py`, runbook, ADR-0008/0009 | floor and budget: at the end (the intro points there). Operating point: no | yes |
| Decision 1 | strict rule, held-out gain, 95% interval, selection/held-out/fresh seeds, **quiet/busy background**, **call**, **PR A**, `score_bench_candidates.proposal()`, `bin_width_sec`, `merge_gap_sec`, `threshold_pctile`, `excess_threshold_hz`, `merge_gap_s`, `C_threshold`, **`tau_mode` isi_adaptive → fixed**, precision swing, close-events test, elevated-rate stretch | strict rule: here. Seeds, swing, close-events: at the end. **Undefined anywhere: quiet/busy background, call, PR A (only a label in the What ran table), what `tau_mode`/isi_adaptive mean. The parameter identifiers get no plain-language gloss here, although the Decision 2 table gives one.** | **BLOCKING** (≥4 undefined) |
| Figure 1 | shipped point, proposal, strict rule, picked chorus fit | yes | yes, apart from the unexplained connector line (F2) |
| Decision 2 | **bracketed**, hard limit, locust, `n_synchronous_frames`, `guard_sec`, `C_min` | limit: at the end. **"Bracketed" is never defined as a word** (Decision 1 gives the meaning without the word) | yes |
| Decision 3 | precision swing, **inadmissible**, **neighbor tried**, **"the gate"**, middle-level events, darkroom path | swing: at the end. Middle level: later (Table 3). **Inadmissible, neighbor and "the gate" undefined** | **BLOCKING** (3 undefined) |
| Decision 4 | **`alpha` (what it is)**, extension cap, **context (window)**, **"the bracketing record"**, **sliding vs binned form** | extension cap: at the end. **alpha, context window, bracketing record and sliding/binned all undefined** | **BLOCKING** (4 undefined) |
| Decision 5 | context grid, extended, first-round move, two-setting grid, "cap", "94 to 1" | rounds/pair/cap: at the end; "94 to 1" unexplained | yes, with friction |
| Decision 6 | **guard**, quarter-of-context cap, **"LoCo's own validity branch returned"**, **"walk the 8 s guard"**, `bench.settings_are_valid` | **guard never defined on the page**; the other two are code-internal | **BLOCKING** (3 undefined) |
| Decision 7 | planted levels, floors range, don't care, **no-coordination recording**, "event set partly defines itself" | don't care: at the end; the no-coordination recording is only listed as a budget | no — the "last three rows" sentence points at the wrong rows (F9) |
| Decision 8 | version, "tuned on", the 3 × 3 | yes (via Figure 2) | yes, apart from a misplaced sentence (F11) |
| Smaller items | chorus_norm, "picked fit", allowance | partly (chorus_norm vs chorus_gain_norm never explained) | yes |
| Full tables / How to read | sliding/binned, cap/edge/limit, decoy | mostly yes | yes |
| Figure 2 | tuned on / scored on bench | yes | yes from the printed numbers; the colour adds almost nothing (F12) |
| Figure 3 | elevated-rate recording, symmetric log scale, WSMIP065 | WSMIP065: no | partly — markers sit above bars without failing (F13) |
| Figure 4 | floor, no-coordination recording, ADR-0009 expected range | partly | partly — the triangle-and-dotted-stem marker is unclear (F14) |
| Real data | **senktide_ttx / senktide**, **treatment window**, baseline window, **"cells"**, **OVX**, **ORX** | **none defined; "cells" means table cells, in a neuroscience document** | **BLOCKING** (5 undefined) |
| Definitions | stream, SCE, ROI, floor, decoy | the SCE/ROI/stream entry runs into one sentence (F17) | yes |
| What ran | PR A/B, WSMIP064/065, `Evaluator`, `make_admissible` | PR labels yes; machines no | yes (identifiers are acceptable in a provenance section) |

## What a cold reader sees in each figure
- **Figure 1:** three panels, one per stream; each detector is a row with an open circle (shipped) and a coloured diamond (proposal), each with a horizontal interval; blue diamonds adoptable, orange not. It reads as a dot plot, not a false friend (the x axis is labelled F1, with no implied zero-effect line).
- **Figure 2:** eight small 3 × 3 heatmaps, one per detector; rows are the tuned-on stream, columns the scored-on stream, diagonal numbers bold. It resembles a confusion matrix, and the diagonal = "own stream" fits that idiom well enough, so it is not a false friend; the one idiom risk (confusion-matrix readers compare along rows) is corrected by the caption.
- **Figure 3:** six panels, three streams across, "inside the stretch, calls per minute" on top and "outside, calls per hour" below; each detector has a marker cluster against a black budget bar; filled/open = quiet/busy, circle/triangle = shipped/proposal.
- **Figure 4:** left, short coloured bars (floor ranges) in grey bands (the ADR-0009 expected range), with grey ticks below and down-pointing triangles on dotted stems far above; right, grouped bars of the percent of planted events under the floor at each participant count, with n/40 printed on each bar.

## Findings (location · issue · severity · suggested fix · verified against a source)

F1 · **Decision 1** · Three things block a cold reader: (a) "quiet" and "busy" background are used throughout and defined nowhere on the page (the glossary calls them regimes `baseline_quiet` / `baseline_busy`, the 25th/75th percentile of baseline rate); (b) "PR A's choice" (L45) is resolved only in the What ran table; (c) the settings column is bare code identifiers (`C_threshold`, `tau_mode` isi_adaptive → fixed, `excess_threshold_hz`), while Decision 2's table shows the better pattern (plain concept + identifier). · **blocking** · Add quiet/busy (with their rates) and "call" to Definitions; replace "PR A's choice" with what PR A was ("the bench PR, #809"); give each Decision 1 setting a plain name ("coincidence threshold (`C_threshold`)", "coincidence window: adaptive to each pair's inter-event interval → fixed"). · yes (glossary L355–360; README L23–26, 45, 422–423)

F2 · **Figure 1** · Each circle–diamond pair is joined by a thin light-grey line, and the caption says "Each line is a 95% bootstrap interval", so a reader takes the connector for a very wide interval (most visibly slow locust, spanning 0.74 to 0.85). · major · Caption line "a light grey line joins each shipped point to its proposal", or drop the connector, or add it to the legend. · yes (image)

F3 · **Decision 2 heading** · "Bracketed" first appears in a heading as a term of art. Its meaning ("no setting at an end of its searched grid") is in Decision 1, but the word is never tied to it or put in Definitions. · minor · Definitions: "**Bracketed** — every setting of the proposal lies strictly inside its searched grid"; use the word in Decision 1's third criterion. · yes

F4 · **Decision 3** · "Inadmissible", "every neighbor tried" and "the gate working as written" are undefined. Also, the heading says "the floor may be why", but the floor argument covers only the precision-swing rows; slow locust's elevated-rate failure gets no explanation, so the reader must work out which failures "why" refers to. · **blocking** · "Inadmissible (failing a budget)", "every adjacent grid value the search tried", "the budget check"; retitle "…and for three of them the floor may be why". · yes

F5 · **Decision 4** · The page never says what CoactDetect's `alpha` is (presumably the coincidence test's false-alarm level); without it, "is 1e-9 a setting you would ship?" cannot be judged by a later reader. "Context" (window), "the bracketing record" and "sliding form" vs binned are also undefined here. · **blocking** · One clause: "`alpha`, the per-bin false-alarm probability of CoactDetect's coincidence test"; define "context window" and "sliding vs binned window" in Definitions; name the file the bracketing record is. · no (the CoactDetect source was not opened to confirm alpha's meaning)

F6 · **Decision 5** · "all six extensions went downward (94 to 1)" does not say what 94 and 1 are (the percentile values of `threshold_pctile`, the grid's lower end before and after). The threshold_pctile cap bullet is also unrelated to the decision asked, which makes the question harder to find. · minor · "the grid's lower end was extended six times, from the 94th percentile down to the 1st"; move the cap note to Table 1's How to read (where it is already repeated). · yes

F7 · **Decision 6** · "Guard" is never defined on the page (Decision 2 introduced it only as "guard (`guard_sec`)"). "Its check sat after LoCo's own validity branch returned" and "walk the 8 s guard" describe code internals. · **blocking** · Define it: "guard — a stretch around the tested window left out of the background estimate"; in plain words, "the cap was never applied to LoCo, so LoCo's searches tried an 8 s guard at 20 s and 30 s contexts". · yes (glossary L279–293 describe guard_sec)

F8 · **Decision 7 table** · The "floors" column gives "5–6 ROIs" without saying what it ranges over, and leaves "(3 ROIs)" for the reader to decode as participants at that level (Table 3 gives a percentage too). · minor · Header "floors (range over the 24 recordings)"; level header "lowest level (participants)". · yes

F9 · **Decision 7, L182** · "25 of 40, 20 of 40 and 15 of 40 for the last three rows" points at the wrong rows. The table's last three rows are combined quiet, combined busy and slow busy, and Figure 4 gives combined quiet's lowest level as 40/40. The three numbers actually match fast busy middle (25/40), combined busy middle (20/40) and slow busy lowest (15/40), so a reader checking against the figure is lost. · major · Name the cells: "fast busy middle 25 of 40, combined busy middle 20 of 40, slow busy lowest 15 of 40". · yes (README table vs Figure 4 right panel)

F10 · **Decision 7, last bullet** · "The event set partly defines itself" is cryptic, and the "no-coordination recording" is used here but only listed under budgets, never described. · minor · "Planting events raises the recording's own null, so the floor that decides which planted events count depends on those events"; Definitions: "no-coordination recording — a bench recording with background activity and nothing planted". · yes

F11 · **Decision 8, the sentence after the table** · "Compare down a column, not across a row" sits under a table whose columns are version / scored on / score; it actually refers to Figure 2. The lead-in also promises 95% intervals, and row 3 has none. · minor · "In Figure 2, compare down a column"; add row 3's intervals or note that they are in `adoption.json`. · yes

F12 · **Figure 2** · Cell values span ~0.67–0.87 on a 0.4–0.9 colour scale, so nearly every cell is the same mid-blue; the comparisons the page asks for (0.82 vs 0.79) cannot be seen in colour, and the reader falls back on the printed numbers. (Checking the scale itself is agent 10's; this is the readability consequence.) · minor · Narrow the scale to the data range, or colour each cell by its difference from the column's diagonal cell. · yes (image)

F13 · **Figure 3, bottom row** · Several busy-background (open) markers sit above their budget bar (fast rate+context shipped ~3/h, combined rate+context shipped ~10/h, combined SPIKE-synch). They are not failures, because the bottom row is gated on quiet only, but a cold reader sees a marker over a bar and reads a failure before reaching that legend clause. The legend also uses a filled circle both for "shipped point" and for "quiet background (filled)". · major · Grey out or thin the open markers in the bottom row, or draw the busy markers without a bar comparison; split the legend into a shape key (circle/triangle) and a fill key (filled/open), each in neutral grey. · yes (image)

F14 · **Figure 4, left panel** · The elevated-rate recording is drawn as a down-pointing triangle on a dotted stem. It is unclear whether the triangle marks the top of a range, a single value, or points at something below; in this repo a down triangle means "look below" (CLAUDE.md plot conventions), so it reads as an annotation pointing at the planted bars. · major · Draw the elevated-rate floor range like the others (a hatched or outlined bar), or use a neutral marker (e.g. a diamond) with an ordinary range bar. · yes (image; CLAUDE.md raster/lane convention)

F15 · **Real data** · "In 2,696 cells the two floors differ": in a calcium-imaging document "cells" reads as neurons, but here it means detector × stream × window combinations. senktide / `senktide_ttx`, "treatment window", OVX and ORX are all undefined (CLAUDE.md requires every abbreviation defined at first use). · **blocking** · "window–stream–detector combinations" instead of "cells"; say what senktide_ttx is (the default export: senktide and TTX treatments); expand OVX/ORX; define treatment vs baseline window. · yes (README L370–383)

F16 · **Illustrate, don't name-drop — event floor / rigid-shift null** · The night's central new mechanism (each window's floor from its own rigid-shift null) is introduced only in text, in the Definitions list, with no picture of a shifted event train or of where the floor falls. · minor · Reuse an illustration of the floor/null if ADR-0008 or its explainer has one; otherwise link one. · no (no search for an existing illustration)

F17 · **Definitions, SCE/ROI/stream entry** · "**SCE** (…), **ROI** (…), **stream**. The event trace analysed…" runs three definitions into one sentence, so the "event trace" gloss seems to apply to all three. Chorus is defined as "the learned detector", but there are two (chorus_norm, chorus_gain_norm) and the difference is never given. · minor · One bullet per term, plus one line on what "gain" adds in chorus_gain_norm. · yes

F18 · **Decoy vs distractor** · The page says "Decoy (ADR-0006)", but the glossary's term for the same object is **distractor**, so a reader looking it up will not find "decoy". (Borders agent 3's consistency role; filed here because it strands the reader.) · minor · Use "distractor", or note "decoy (glossary: distractor)". · yes (glossary L379)

F19 · **WSMIP064 / WSMIP065** (Figure 3/4 captions, What ran) · Machine names used as if the reader knows them. · minor · At first use: "WSMIP065 (the second overnight workstation)". · yes

F20 · **Table 2, fast CoactDetect proposal, held-out** · The row shows a bold **fail: close-events test**, while Decision 4 says the proposal does not fail against the point fast actually ships; a reader of the table alone sees a failure. · minor · Append to the cell "passes against the binned point that ships — see Decision 4". · yes

Tone: sentence case consistent; no ALL-CAPS prose; lists formatted as lists. No findings.

Summary: five sections are blocking under the ≥3-undefined rule (Decisions 1, 3, 4, 6 and Real data). The most concrete errors are F9 (a sentence pointing at the wrong table rows) and F15 ("cells" meaning table cells). The figure defects are F2, F13 and F14.
