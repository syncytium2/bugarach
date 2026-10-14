GRANT 9 ok — Read, Grep, Glob, Bash (also holds SubagentHandback; no Edit/Write/NotebookEdit)

Role 9: Density and figure-first. Artifact: `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md` and its six PNGs, checked against ADR-0014 in the same worktree.

**Bottom line:** the six figures fill their own canvases, so no reflow is needed. The density problem is in the text: about 3,660 words, all below the figures as ADR-0014 requires. Several mechanisms, and the design of the simulated sets, are described in words but drawn nowhere.

**Thresholds I used.** These are conventions, not optima. The checklist's 40-words-per-slide rule does not fit a scrolling page, so I used:
- a single block over 60 words is flagged;
- a section is judged on whether its claim has a picture somewhere on the page;
- figure share is the ink bounding box as a percentage of the rendered PNG.

GitHub scales each image to the full column width. I did not render the GitHub page itself.

## Table (one row per section or figure)

| Section / figure | words | largest block | carries a figure | figure share of canvas |
|---|---|---|---|---|
| Fig 1 caption + PNG | 73 | 73 | y | 95% (1471×1401); no side margins |
| Fig 2 caption + PNG | 59 | 59 | y | 92% (1369×724) |
| Fig 3 caption + PNG | 71 | 71 | y | 91% (1473×732) |
| Fig 4 caption + PNG | 73 | 73 | y | 92% (1430×745) |
| Fig 5 caption + PNG | 89 | 89 | y | 92% (1484×810) |
| Fig 6 caption + PNG | 51 | 51 | y | 92% (1365×714) |
| The question | 273 | 119 | n | – |
| Terms | 255 | 47 | n | – (prose is right: glossary) |
| Step 1, count in windows | 201 | 69 | n (points to 1C, 2A, 2B) | – |
| Step 2, chance is measured | 189 | 147 | n (points to 1B, 1D, 2B) | – |
| Step 3, two numbers to three answers | 149 | 102 | n (points to 2B, 6) | – (prose is right: arithmetic) |
| Does it get the right answer? (intro) | 70 | 70 | n | – |
| The check, and the two models | 487 | 137 | n (points to 3, 4) | – |
| Window size, moments close together | 343 | 135 | n (points to 4) | – |
| What else it counts | 520 | 169 (largest on the page) | n (points to 5) | – |
| How far one recording strays | 260 | 67 | n (points to 6) | – |
| The simulated recordings | 171 | 136 | n | – |
| Where the method comes from | 295 | 176 | n | – |
| What waits | 165 | 114 | n | – (prose is right: status) |
| For developers | 188 | 73 | n | – (prose is right: pointers and formulas) |

- **Text sections:** all 14 are prose-only. That is mandated by ADR-0014 points 1–4, so I have not flagged the run of consecutive prose sections by itself.
- **Blocks over 60 words:** 13 text blocks and 4 captions.
- **Page total:** 4,079 words.
- **Figures as a share of the whole page:** about 30% of scroll height. This is an estimate (about 3,100 px of figure at column width against about 7,000+ px of text) and was not measured on a render.

## Findings

Each finding gives location · issue · severity · fix · whether I could verify it.

**F1 · Sets described in prose.** Location: lines 126–130, 174–181 and 257–269 (three sections).
- **Issue:** the design of the simulated sets (moment sizes, interval schedules, backgrounds, recording counts, durations) is spread over about 380 words. The interval schedules ("2 close pairs + 2 medium pairs, each ≥120 s from the next") describe an arrangement in time, in words.
- **Severity:** medium.
- **Fix:** a new figure, "the simulated sets": one 45-minute timeline strip per set (mixed, 120 s only, medium, close, very close, bench at about 7 moments), ▼ per moment coloured as in Fig 1 and sized by cells. Add a parameter table (background · moments · sizes · recordings · duration · used in figure). The three passages shrink to pointers. Keep the "bench merged intervals under 2 s" caveat as one sentence.
- **Verified:** yes.

**F2 · The slide ladder has no picture.** Location: Step 2, lines 98–105 (147-word block).
- **Issue:** the slide ladder (each cell slid by its own amount, at least 2 windows apart, about −32 to +32 s, wrapping) is the mechanism Fig 5's whole argument rests on ("about half a minute"). No figure shows it.
- **Severity:** medium.
- **Fix:** add panel E to Figure 1, beside D: one dot per cell, x = its slide in seconds, y = cell. It shows the spacing and the reach at a glance. The paragraph drops to one sentence plus the pointer.
- **Verified:** yes.

**F3 · Half of the busy-stretch argument has no picture.** Location: "What else it counts", first bullet, lines 203–212 (169 words, the largest block).
- **Issue:** the argument has two steps. (1) Only the stretch's first and last half minute survive the slides, so the false excess is about constant (350–380 pairs) beyond 1 minute. (2) A longer stretch adds more onsets, so the share falls. Fig 5A shows only the share, so step (1) is prose only.
- **Severity:** medium.
- **Fix:** add a panel above 5A on the same x axis: false excess pairs per recording against stretch length, flat from 1 m. Alternatively, a schematic of one stretch in the recording and in a shifted copy, with the ±half-minute edge zones shaded. The bullet then becomes two sentences.
- **Verified:** yes for the figure lacking it. I did not check the 350–380 values in numbers.json.

**F4 · The removal percentages cannot be read off Fig 5C.** Location: lines 218–223.
- **Issue:** the claims are percentages ("removes 98%", "99%"). Fig 5C plots raw *f*₂ on a symlog axis, where the removed fraction cannot be read.
- **Severity:** low.
- **Fix:** add bars to 5C: % of the *f*₂ excess removed by subtraction, one bar per row. Axis legibility as such belongs to agent 10; my finding is only that the claim has no picture.
- **Verified:** yes.

**F5 · Prose repeats Fig 4.** Location: "Window size" bullets, lines 183–193 (343 words).
- **Issue:** the bullets read about 20 values off Fig 4. One claim, the binomial model's "3% to 17% low", is plotted nowhere, because Fig 4 shows the fixed model only.
- **Severity:** low.
- **Fix:** label the points the text names directly on Fig 4 (4 s close pairs at −21%, +56%, −49%; the very-close range). Add the binomial model as hollow markers in 4A. Cut each bullet to its assertion plus a pointer. Move the range values to numbers.json, which already holds them. Relocate them; do not delete them.
- **Verified:** yes.

**F6 · Mechanism stated without pointing at its evidence.** Location: "Why the fixed model reads low", lines 157–164 (137 words).
- **Issue:** the claim that *k* reads high and λ reads low has no figure pointer. Fig 4B and 4C already show it (120 s only: *k* +26–33%, λ about −35%).
- **Severity:** low.
- **Fix:** cite Figure 4B and 4C in that paragraph. No new figure is needed.
- **Verified:** yes.

**F7 · Captions duplicate in-image legends.** Location: captions of Figs 1, 3, 4 and 5 (71–89 words each).
- **Issue:** they repeat the legends already drawn inside the PNGs; Figs 2–6 carry full symbol keys. Two captions also carry content that is not legend:
  - Fig 5: "each worked out as one recording in a run with 24…" is method, repeated at lines 197–200.
  - Fig 1: "drawn one above the other" is reading guidance.
- **Severity:** low.
- **Fix:** ADR-0014 point 2 puts the key in the heading line. So either keep the caption key and drop the duplicate drawn in the image, or keep the in-image key and cut the caption to number + name + panel map. Move the Fig 5 pooling sentence and the Fig 1 reading note into the text.
- **Verified:** yes.

**F8 · Citation-dense prose.** Location: "Where the method comes from", lines 273–295 (176-word block).
- **Severity:** low.
- **Fix:** a lineage table. Columns: source · what this tool does differently · correction tried here (y/n). Rows:
  - population-count estimate (Ehm 2007)
  - CuBIC (Staude 2010)
  - multiple-interaction process, the binomial model (Kuhn 2003)
  - fixed model
  - shift surrogate (Pipa 2008)
  - rate-change corrections (Staude 2008/2010)
  - non-Poisson correction (Reimer 2012)

  The "What is this project's" paragraph becomes the "differently" column. Keep the ⚠ sentence as prose.
- **Verified:** yes.

**F9 · Each figure is discussed far from where it is drawn.** Location: whole page.
- **Issue:** about 3,660 words of argument sit below all six figures, and each figure is discussed 100–250 lines below it. That is report-length text.
- **Severity:** low; this is a question for the main thread, not a fix.
- **Fix:** ADR-0014 points 1–4 mandate this layout for explainers. Point 5 (a report leads with its main figure and keeps the others in place) would put figures beside their text. Whether this page is an explainer or a report is the main thread's call, or Tony's. F1–F5 shrink the text either way.
- **Verified:** partly; the share is an estimate.

**F10 · Provenance inside the key caveat.** Location: "The question", lines 39–46 (119 words).
- **Issue:** the ADR-0017 parenthetical is provenance sitting in the page's most important paragraph.
- **Severity:** low.
- **Fix:** move the parenthetical to "For developers" and keep the treatment caveat on the face. Prose is right for the caveat.
- **Verified:** yes.

**F11 · Fig 6 does not show where real recordings sit.** Location: "How far one recording strays", bullet 2, lines 243–245.
- **Issue:** the link to real recordings (about 7 moments per 45 min, 2–3 per 15 min) is not on Fig 6.
- **Severity:** low.
- **Fix:** on Fig 6, add a bracket under the 6-moment and 3-moment groups: "where real baselines sit".
- **Verified:** yes.

## Checked and passed
- **Figure share:** all six PNGs carry ink across 91–95% of their area, with no side margins. No reflow is needed.
- **Prose is the right form** for Terms, the Step 3 arithmetic, What waits and For developers.
