GRANT 5 ok — Read, Grep, Glob

# Line edit of the slow co-modulation explainer, first round

**Artifact:** `<worktree>/docs/learned/slow_comodulation/README.md`
**Rules applied:** the banned-construction list from the role-5 checklist, `CLAUDE.md` (names instead of numbered labels, plural "data", a unit on every number, abbreviations and symbols defined at first use, figures cited by number and name) and `docs/writing_conventions.md` (American spelling, units in table columns, bold in tables).

## The search, run by hand

`murderboard_prose.sh` is not in this repository and I have no shell, so this is **not the tool's output**. These are Grep searches against the file. Constructions searched:

| construction | pattern | hits (line · kind) |
|---|---|---|
| *delve, leverage, robust, seamless, crucial, landscape, tapestry* (any ending) | `(?i)\b(delve\|…\|tapestry)\w*` | none |
| *not just X, but Y* / *not only* | `not just\|not only` | none |
| *it's not about A, it's about B* | `it'?s not about` | none |
| *it's worth noting* | `worth noting` | none |
| *In today's ___* | `in today's` | none |
| em-dash pivot into an uplifting close | ` — ` and `—$` | 11 lines (22, 23, 48, 54, 97, 135, 150, 151, 159, 160, 179). All are asides or definitions. None pivots into an uplifting close. |
| three-item list built for rhythm | read by hand, no pattern | title (line 1) is a possible hit. Lines 72, 163 and 182–184 list three things that really are three. |
| singular "data" | `\bdata\b` | none (the word never appears) |
| bare numbered label (`panel A`, `step 4`, …) | `(panel\|step\|option\|set\|phase\|case\|arm) [A-Z0-9]` | none. Read by hand for "the first / the second", "Figure N" without a name, and "§N": lines 23–24, 33–34, 124, 182 |
| British spelling | `centre\|labelled\|analysed\|analyse\|colour\|modelling\|favour` | 69 "analysed", 94 "analysed", 101 "labelled" |
| the retired word "modality" | `modalit` | none |

## Block table

Word and sentence counts are **my estimates from reading**, not counted by a tool.

| block (lines) | words · sentences | payload sentence | where it sits | what the other words buy |
|---|---|---|---|---|
| Header note, 3–7 | ~70 · 4 | Exploratory, one run, baseline only, not a milestone. | first | Needed labels (what "measured" and "argued" mean) and why the page exists. Earns its place. |
| The two things, 11–18 | ~75 · 6 | Events align onsets; shared modulation raises rates together. | spread over the two bullets | "The onsets themselves are aligned" repeats the sentence before it. |
| Why it matters, 20–25 | ~95 · 4 | Whether rigid shift also removes shared modulation, and how much of it the recordings hold, decides what a label-free detector learns. | **last**, split over two sentences | The definition of rigid shift and the "paid" framing: needed evidence. Promote the payload. |
| How to read the measurement, 29–38 | ~135 · 5 | A narrow peak in the cross-correlogram means events; a broad shoulder means shared modulation. | last (the bullets) | The method: needed, but its order is misstated (see findings). |
| Figure 1 caption, 42–51 | ~150 · 8 | Sizes, planted parameters, controls, axis scale. | n/a (a caption) | The simulator quotation repeats itself at 55–57 and 175–176. |
| Two easy-to-miss points, 53–57 | ~60 · 3 | Shared modulation also makes sub-second coincidences. | second | The opening sentence previews what follows (throat-clearing). The simulator point is the second of three copies. |
| Figure 2 caption, 63–70 | ~125 · 3 | Defines the three kinds of surrogate. | n/a | Needed. |
| Three facts, 72–83 | ~165 · 8 | Rigid shift spreads events and removes only modulation faster than *J*. | first two bullets | The third bullet restates the second in reverse. Only its block-control half is new. |
| ⚠ block control, 85–87 | ~50 · 2 | The block control tells a curve that falls over tens of seconds from one that stays flat for a minute. | **last** | Repeated at 198–199. |
| Figure 3 caption, 93–99 | ~110 · 6 | Which recordings were used, and what the shading means. | n/a | "Eight surrogate draws" is repeated at 202. |
| Recordings results, 115–130 | ~230 · 10 | On lab fast, most shared excess is a flat shoulder that CoactDetect removal, rigid shift and the block control all leave alone: drift over minutes. | **the end of the second bullet**, line 124 | The peak numbers are needed evidence. The Cossart bullet repeats 188–189. |
| The dip, 132–138 | ~120 · 5 | On the slow stream, a real-against-shifted contrast is also paid for what follows an event, not only the event. | **last** | The refractory reading and the numbers: needed. Promote the payload. |
| Figure 4 and group, 144–152 | ~125 · 7 | The pooled curve is not one group's; this does not show a group difference. | **last** | The OVX observation sets up the disclaimer. Earns it, but the long sentence needs splitting. |
| Label-free implications, 156–176 | ~330 · 17 | On lab fast, the shared structure outside the peak is drift over minutes, which rigid shift does not remove. | first bullet, mid-bullet | The provenance sentence (168–170) buys nothing for a public reader. The last bullet is the third copy of the simulator point. |
| Open question, 178–184 | ~95 · 4 | Does shared drift over minutes belong to coordination, to background, or to the producer? | **last** (the bold question) | The candidate causes: needed. Earns its place. |
| Does not settle, 188–204 | ~260 · 14 | Seven limits. | n/a (a list) | "Pairs, not counts", "keeps some faster structure" and "Eight surrogate draws" each repeat an earlier passage. |
| Reproduce, 208–218 | ~110 · 4 | The commands. | n/a | Needed. |

## Findings

| # | location | issue | severity | suggested fix | verified |
|---|---|---|---|---|---|
| 1 | 29–31 | **The method is stated in the wrong order.** "Divide by the count expected … Pool that over all pairs and all recordings" reads as: take a ratio per pair, then average the ratios. The code does the reverse. `pooled()` in `tools/measure_slow_comodulation.py` (lines 303–307) sums observed counts and expected counts across recordings, then divides once. That changes the weighting: busy recordings count for more. | major | "Sum the observed onset pairs at lag *τ* over all ROI pairs and recordings, sum the counts expected if each pair fired independently at its own observed totals, and divide." | yes |
| 2 | 81, 83, 87, 124, 160 | **"Drift" carries the headline but is never defined.** It first appears in a bullet heading (81) as if already known. The page uses six names for overlapping ideas: *co-modulation* (title only), *shared slow modulation*, *shared modulation*, *drift*, *shoulder*, *shared structure*. | major | Define it once, near line 37: "shared modulation slower than a few minutes — call it **drift**". Then use *shared modulation* for the general thing and *drift* for the slow case only. Drop "co-modulation" from the title or define it. | yes |
| 3 | 54, 63, 76, 78, 81, 124, 198, 218 | **The synthetic "worlds" are used before they are named, and under shifting names.** "The 20 s world" first appears at 54; the Figure 1 caption says "columns" and "kinds". The 5-minute case is "the 5-minute world" at 81 and "the drift world" at 124. "Drift world" is never defined, yet line 124 cites it as "Figure 2's terms". | major | Name the three in the Figure 1 caption: "the **planted-event world**, the **20 s world**, the **5-minute world**". Use exactly those names afterwards. At 124: "…the 5-minute world of Figure 2, what each surrogate removes, not its 20 s world." | yes |
| 4 | 144 | **Undefined abbreviations DI, MALE, ORX and OVX.** `CLAUDE.md` requires every abbreviation to be defined at first use. | major | Spell each group out at first use. I cannot confirm what DI stands for. | no |
| 5 | 101–113 | **The table's value column has no unit.** `writing_conventions.md` says every column carries a unit and "dimensionless is a unit". The headers give only lag ranges. | major | Lead line: "Excess coincidence (dimensionless; 0 = independent) by lag bin; brackets are the 95 % interval over mice." | yes |
| 6 | 93–98, 117, 132 | **Undefined jargon at first use for a public reader:** "fast and slow streams" (the whole results section depends on the difference); "CoactDetect" (first use at 97 says only "the CoactDetect detector"; what it detects appears 95 lines later, at 192); `steps_excluded`; "declares no regions". | major | Line 93: one clause on what the fast and slow streams are. Line 97: "CoactDetect, the repository's detector for coincident onsets across three or more ROIs". Replace `steps_excluded` with what it means (the windows it keeps). | partly (the `GLOSSARY.md` entries for stream and CoactDetect) |
| 7 | 128–130 | **States as fact what the page does not measure, then walks it back in brackets.** "Looks negligible and is not … (argued; this page measures pairs, not the count's variance)." The house voice names the unknown instead of hedging around a flat claim. The limits list repeats the point at 188–189. | major | "Cossart's shoulder is +0.01 to +0.02 per pair. Every ROI pairs with 565 other ROIs, so it could still move the count of lit ROIs visibly; this page does not measure that." Then cut 188–189 or point to it. | yes (the page's own text) |
| 8 | 23–24, 33–34 | **Refers back by position** ("destroy the first", "also destroys the second", "the two things above"), which makes the reader scroll back to the bullets. | minor | "…was chosen to destroy coordinated events. Whether it also destroys shared modulation, and how much shared modulation the recordings hold…". At 33–34: "separates coordinated events from shared modulation". | yes |
| 9 | 33–38 | "Separates the **two** things above:" introduces **three** bullets. | minor | "…separates them, and a control:", or move the per-ROI bullet after the list as a control. | yes |
| 10 | 124 | "In Figure 2's terms" is a figure number without its name (`CLAUDE.md`). | minor | "In the terms of Figure 2, what each surrogate removes, …" | yes |
| 11 | 69, 94, 101 | British spelling "analysed" (twice) and "labelled", against the American-English rule in `writing_conventions.md`. | minor | "analyzed", "labeled". | yes |
| 12 | 53 | Throat-clearing: "Two things in Figure 1, the three kinds, are easy to miss." | minor | Cut it. Open with the bold claim. | yes |
| 13 | 72 | Throat-clearing: "Read Figure 2, what each surrogate removes, for three facts:" | minor | Cut it. The bullets stand alone. | yes |
| 14 | 78–83 | **One fact stated twice.** "Removes modulation only on timescales shorter than about *J*" and "Drift slower than *J* passes through untouched" say the same thing from opposite ends. Only the block-control sentence in the third bullet is new. | minor | Merge the 5-minute evidence into the second bullet. Make the third bullet: "**The 2-minute block control keeps most of a 5-minute drift**, because a 2-minute count still carries it." | yes |
| 15 | 74–77 | "A low plateau reaching to about 2*J*", then "near +0.1 out to about 30 s" at *J* = 20 s (2*J* = 40 s). This reads as a contradiction. "Where it was zero" has no clear subject. | minor | "…a low plateau that tapers to zero at 2*J*. At *J* = 20 s the planted-event curve sits near +0.1 out to about 30 s, where the recorded curve was zero." | yes (text only) |
| 16 | 48–50, 55–57, 175–176 | **The same point three times:** the simulator's background has no shared modulation. | minor | Keep it in the implications section (175–176), which adds "or a dip". Keep the code citation in the Figure 1 caption. Cut 55–57. | yes |
| 17 | 85–87 vs 198–199 | The block-control caveat is stated twice. | minor | Keep the ⚠ block. In the limits list, point to it in one line or cut. | yes |
| 18 | 99 vs 202–203 | "Eight surrogate draws per recording per arm" is stated twice. | minor | Keep the limits bullet (it adds that intervals include draw noise). Cut it from the caption. | yes |
| 19 | 20–25 | The payload comes last, and the 21–23 sentence carries two definitions (rigid shift, *J*) nested inside a dash pair inside a claim. | minor | Give the definition its own sentence: "A **rigid shift** slides each ROI's whole onset train by its own random offset within ±*J* seconds, the displacement radius." | yes |
| 20 | 132–138 | The payload ("a real-against-shifted contrast on the slow stream is paid for the event's aftermath as well as the event") is the last sentence. "+0.36 to +0.57 at *J* of 10 and 20 s" does not say which number goes with which *J* and lag bin, and neither number is in the table. | minor | Open the paragraph with the payload. Add a "lab slow, rigid shift *J* 20 s" row to the table, as lab fast has, or give the pairs explicitly. | no (`summary.json` not opened) |
| 21 | 115–124 | The payload sits in the second bullet's final clause. "Every folder has both" is imprecise: the claim covers three stream curves from two folders. | minor | Lead: "**On every stream, most shared excess is a shoulder, and on lab fast it is drift over minutes.**" Or: "Every stream in both folders has…". | yes |
| 22 | 119 | "Cuts it by six-sevenths" is hard to parse. | minor | "cuts it to about a seventh on slow (+21.94 to +3.20)". | yes (3.20 / 21.94 = 0.146) |
| 23 | 144 | Four parallel lists ("DI, MALE, ORX and OVX: 17, 22, 25 and 20 recordings from 10, 12, 12 and 10 mice") make the reader match items by position. | minor | "DI, 17 recordings from 10 mice; MALE, 22 from 12; ORX, 25 from 12; OVX, 20 from 10." | yes (the sums, 84 recordings and 44 mice, match line 94) |
| 24 | 149–152 | One sentence carries the confound, two links, the overlapping intervals and the conclusion. | minor | Split it: "⚠ Group cannot be separated from imaging day here: no imaging date holds more than one group ([links]). The intervals also overlap. So this figure shows the pooled curve is not one group's, and does not show a group difference." | yes |
| 25 | 161 | "So on that stream **it** is not what those objectives were paid for": "it" could be the drift or the shared modulation. | minor | "…so on that stream, drift is not what those objectives were paid for." | yes |
| 26 | 158 | "The decision is narrower than it was framed" never says how. | minor | "**On lab fast, the 10–45 s question has little to act on.**" Then the evidence. | yes |
| 27 | 168–170 | Unlinked provenance: "the rigid-shift report" is never linked or named as a file, and the sentence spends about 20 words on a session and a date a public reader cannot follow. | minor | Link the report and cut the session and date, or cut the sentence. | no |
| 28 | 171–172 | "Zero-parameter baseline" is followed in the same sentence by a 30 s window, which is a parameter. | minor | "no-training baseline" or "a baseline with no fitted parameters". | yes (text only) |
| 29 | 192–197 | The bullet is headed "partial", but half of it describes over-removal ("every onset inside an episode goes, member or not"). The slow-settings sentence is a separate point folded in. α and "explore_sce viewer" are used without definition. | minor | Head it "**CoactDetect removal both misses and over-removes.**" Move the slow settings into their own bullet. Define α ("α, the per-bin false-alarm level", if that is what it is). | no (α's meaning not checked) |
| 30 | 3 | "**Numbers** carry a 95 % interval from resampling mice", but the synthetic results and the 0.91 / 0.71 / 0.86 shares have none. "It was written because…": "It" could mean the interval rather than the page. | minor | "Numbers from the recordings carry…". "This page exists because…". | yes |
| 31 | 20, 129, 172 | "Lit ROIs" is used three times and never defined. The Figure 1 caption's "ROIs with an onset in each 10 s bin" is the definition. | minor | At 20: "counts lit ROIs (ROIs with an onset in the same bin)". | yes |
| 32 | 1 | The title may be a three-part list built for rhythm. "Where it sits in time" is vague, and the title states no finding. | minor | Something like "Slow co-modulation: most shared activity is drift over minutes, and rigid shift leaves it". | yes |
| 33 | 182 | "FOUNDATIONS §9" is a section label, which `writing_conventions.md` discourages. The sentence does state the consequence ("sends such questions to the lab"). | minor (arguably fine as written) | Leave it, or "FOUNDATIONS' rule that questions about the preparation go to the lab". | yes |
| 34 | 216–218 | "The nulls keeping what they claim" is vague. | minor | "the circular shift keeping each ROI's total and the block control keeping each ROI's count per 2-minute block". | yes (claims from lines 66–68) |

**No problems found here:**
- **"Data":** the word never appears, so there is nothing to make plural.
- **Banned words and phrases:** no hits.
- **Em-dash pivots:** none of the 11 lines with an em-dash pivots into an uplifting close.
- **Bold in the table:** only row labels are bold. The rules allow bolding the rows a passage is about.
- **Units:** every count and duration outside the table has one. The closest miss is "565 others", which could say "565 other ROIs".
