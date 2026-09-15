> **Public copy.** Lines that concern real treatment recordings are removed (8 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 10 ok — Read, Grep, Glob, Bash

# Role 10: Ship It (build & craft gate) — report

**Verdict: not shippable yet.** The build is current and complete, but three figures have clipped or hidden content, a real phone never gets the mobile layout, and the keys for most markers and colors are in prose or plain caption text instead of in the figures.

## Build currency
| check | result | source |
|---|---|---|
| artifact hash | `af9c8ded2073038c0774b27cd2982bb2d5e94f42`, same as the brief | `git hash-object` on the artifact |
| HTML newer than template, generator and every PNG | **yes, current.** HTML 11:09:50.92; template 11:09:48.89; generator 11:06:53; newest PNG is fig02 at 11:09:18.66 | file timestamps |
| unfilled `{{` tokens | 0 | grep on the built HTML |
| figures present | 16 of 16; all loaded (`complete`, natural 2360 px wide); all have alt text | DOM at 1280 |
| tables | **3, not 2**: the §4 detector table, Table 1 (performance), the §10 strengths table | DOM |
| figure numbering | Figure 1–16 all captioned and all referenced in the text; no dead `#` anchors, no duplicate ids | DOM |

Renders are in `...\scratchpad\mb_scratch\role10\`:
- `full_1280.png`: 1280 × 31218
- `full_400.png`: 400 × 35070
- `mobile_emulated.png`: 400 px with `is_mobile`
- zoom bands `b00`–`b09` (1280) and `m01`, `m03` (400)
- PNG zoom crops `z02b`, `z12bc`, `z11c`, `z07edge`, `z10c`

Effective text size is worked out like this: figures were rendered at scale=2, so each 2360 px PNG is 1180 CSS px, placed at **1142 px** (not ~1108), a factor of 0.968. At 400 px the figure is 370 px wide, a factor of 0.314. Smallest stated font per figure comes from the embedded Bokeh JSON in `_work/figNN.html`.

## Per-figure table
All boxes are x=70, w=1142 (89% of the 1280 viewport); at 400 px, w=370. Heights are given as 1280 / 400 px.

| Fig | checked against | box h (1280 / 400) | smallest text (1280 / 400) | overlap / clipping | axis names + units | shared y | letters | every mark identified? | conventions |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `fig01_problem.png`, band `b01` | 458 / 149 | 8pt → 7.7pt / 2.5pt | none; about 9% blank on the right inside the frame | x is just "t" (units only in ticks); B lane has no row label | n/a | A, B ✓ | ▼ named in B's heading ✓ | nothing on raster ✓; ▼ points down ✓; minutes axis ✓ |
| 2 | `fig02_surrogates.png`, `z02b` | 1300 / 421 | 8pt → 7.7 / 2.5 | **both B y-labels clipped at the top** ("…at least K ROIs" loses its end); right B label sits close to the left panel's "16" tick | A and C have no x name; B x ✓ | B 1e-6–1 on both ✓ | A1–A3, B, C ✓ | peach band, grey step, orange dashed and blue lines keyed only in plain caption text; **blue/orange mean shift/shuffle in B but nearby/whole-recording bar in C**; **▼ marks calls in C** but planted events everywhere else; caption says 3 calls outside the block are planted events, but C has no planted row | ✓ |
| 3 | `fig03_rate.png`, `b04` | 452 / 147 | 8pt → 7.7 / 2.5 | none | **no x-axis name** | 0–14 on both ✓ | A, B ✓ | ✕, green/red ▼ and the peach band are keyed only in a prose paragraph before the figure; blue/grey/dotted keyed in plain caption | ✓ |
| 4 | `fig04_coact.png` | 452 / 147 | 8pt → 7.7 / 2.5 | none | no x name | 0–14 ✓ | ✓ | teal, grey dots, black dashes keyed in plain caption only; band keyed in prose | ✓ |
| 5 | `fig05_loco.png` | 452 / 147 | 8pt → 7.7 / 2.5 | none | no x name | 0–14 ✓ | ✓ | purple and dotted keyed in caption; band in prose | ✓ |
| 6 | `fig06_sce.png` | 452 / 147 | 8pt → 7.7 / 2.5 | none | no x name | 0–~24 on both ✓ | ✓ | red ▼ (missed) and ✕ keyed only in the prose before Fig 3 | ✓ |
| 7 | `fig07_cicada.png`, `z07edge` | 452 / 147 | 8pt → 7.7 / 2.5 | **right-most ✕ in the B lane is cut by the frame** | no x name | 0–14 ✓ | ✓ | ○ named in caption ✓; ✕ and band in prose only | ✓ |
| 8 | `fig08_sync.png` | 607 / 197 | 8pt → 7.7 / 2.5 | none | no x name; y "(0–1)" ✓ | 0–1 ✓ | ✓ | red ▼ in prose only | ✓ |
| 9 | `fig09_learned.png`, `b05` | 1086 / 352 | 8pt → 7.7 / 2.5 | none | A x ✓ (lag in raw seconds); B/C have no x name | **A: four panels of the same quantity (weight) have four y ranges (≈0.2 / 0.2 / 0.45 / 0.6), unmarked**; B/C 0–30 and 0–1 ✓ | A, B, C ✓ | the four shades per model in A are not identified; **one ▼ serves six detectors, so green ("this detector found it") is ambiguous: trace and tiny missed**; ✕ in prose only | ✓ |
| 10 | `fig10_generator.png`, `z10c` | 1036 / 336 | 8pt → 7.7 / 2.5 | none; legends clear of data | A2 and B x is just "t"; C and D ✓ | n/a | A1, A2, B, C, D ✓ | ▼ / ▽ / band keyed in caption only, no lane labels; C/D legends ✓ | ✓; ▽ and ▼ both point down |
| 11 | `fig11_optimization.png`, `z11c` | 837 / 271 | **7pt → 6.8pt / 2.2pt** (rotated ticks) | **markers at the left plot edge are half-clipped** (✕ at 0.5, 0.1, 0.005 and 90; ○ at 99 and 75); C x-labels sit at three different heights; right ~13% blank | A x "seconds"; **C x-axes are raw knob names** (`excess_threshold_hz`, `alpha`, `threshold_pctile`, `sce_percentile`, `C_threshold`); C y "score" is generic but three different measures are drawn | C 0–1 on all ✓ | A, B, C ✓ | ○ ✕ ■, dashed blue-grey and dashed tan keyed only in plain caption text; **the two dashed lines are low-contrast and thin** | **A is a timeline in raw seconds (0–60)**, against the minutes-friendly axis rule |
| 12 | `fig12_performance.png`, `z12bc`, `b07` | 636 / 207 | 8pt → 7.7 / 2.5 | **B y-label cut off: "…where nothing was plant"**; **C legend hides the LoCo 10% dot (~0.48)**; B dots on the 10⁻² floor are half-clipped; right ~13% blank | x categorical, no name; A y ✓, C y ✓ | A 0–1 on both ✓ | A, B, C ✓ (letters only in y-labels) | blue/dark red and red dash keyed only in caption; **caption says C is "one line per detector", but C draws only dots**; the "no calls" floor is not marked, so floor dots and real 0.01 values look the same; light-grey 10% dots have low contrast | n/a |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |

## Page-level table
| check | checked against | result |
|---|---|---|
| overlap and running off the page, 1280 | `full_1280.png`, bands `b00`–`b09` | no element wider than the viewport; no shape-on-shape overlap seen |
| no horizontal page scroll, 400 | DOM at 400 | ✓ scrollWidth 400; Table 1 (788 px) sits inside `.scroll{overflow-x:auto}` |
| Table 1 at 400 | `m03` | columns cut at the right edge with no cue that the table scrolls; reads as if it ends there |
| figures at 400 | `m01`, `m03` | unreadable (~2.5pt text); images are not links, so there is no tap-to-open at full size |
| **real phone** | `mobile_emulated.png` | **no `<meta name=viewport>`**, so the page lays out at 980 px and shrinks to fit; the `@media (max-width:640px)` rules never apply; body text is ~7 px on screen |
| HTML basics | head of file; `document.compatMode` | **no DOCTYPE, so the page renders in quirks mode (BackCompat)**; no `<html>`/`<head>`/`<body>`, no `lang`, no `<meta charset>`; the file starts at `<title>`. Chromium guessed UTF-8 when opening the local file; served over HTTP without a charset header, ▼ ✕ ○ – could turn into garbage characters |
| `<title>` | DOM | "Coordinated-Event Detectors" ✓ |
| stamp for this build | grep | no date, commit, version or author anywhere; the footer says only "Built from the project's own tools…", so a reader cannot tell which build they have |
| tables numbered | DOM | only Table 1 is numbered; the §4 and §10 tables have no number or caption |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| "no titles above plots" (CLAUDE.md) | renders | every panel has a heading above the plot ("A · …"). It carries the panel letter, so this conflicts with the lettering rule; your call |

## Findings
Columns: location · issue · severity · fix · verifiable against the render or source (yes/no)

1. **Page head** · no DOCTYPE (quirks mode), no `<meta charset>`, no `<meta viewport>`; a real phone gets a shrunk 980 px desktop layout · **high** · template: add `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">` · yes
2. **Fig 12 B** · y-label clipped ("…nothing was plant") · **high** · shorten the label or give the plot more height · yes (`z12bc`)
3. **Fig 2 B** (both panels) · y-labels clipped at the top · **medium** · shorten, e.g. "share of bins with ≥K ROIs", or add height · yes (`z02b`)
4. **Fig 12 C** · legend hides the LoCo 10% dot · **medium** · move the legend outside the plot or to an empty corner · yes
5. **Fig 12 caption** · says "one line per detector"; C shows only dots · **medium** · change the caption to dots, or draw the lines · yes
6. **Figs 3–9** · ✕, ○, green/red ▼ and the peach busy-block band are keyed only in one black prose paragraph before Fig 3; by Fig 9 that key is ~9,000 px up · **medium** · put an in-figure key in colors (e.g. a legend strip on the B lane) or at least a colored key in each caption · yes
7. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
8. **Fig 9 A** · same quantity (weight) on four different y ranges, unmarked · **medium** · share y-limits, or mark the difference; also identify the four center filters · yes
9. **Fig 9 B** · one ▼ colored green for all six detectors, but trace and tiny missed · **medium** · give each lane its own verdict mark, or use a neutral ▼ in multi-detector lanes · yes
10. **Fig 2 C** · ▼ used for calls (planted events elsewhere); blue/orange change meaning between B and C · **medium** · use bars for calls as in Figs 3–9; pick colors for C that are not shift/shuffle · yes
11. **Fig 11 C** · x-axes are raw parameter names; y "score" covers F1, recall and precision; marker key is plain caption text; edge markers half-clipped; smallest text in the document (6.8pt effective) · **medium** · reader-facing axis names with units ("threshold (events/s)", "percentile (%)"), pad the x-range, larger ticks, legend in the figure · yes
12. **Fig 11 A** · timeline axis in raw seconds 0–60 · low · minutes-friendly ticks via `_time_axis_hook` · yes
13. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
14. **Fig 7 B** · right-most ✕ clipped by the frame · low · pad xlim or allow the glyph to overflow the frame · yes (`z07edge`)
15. **All figures** · 10–13% of each canvas is blank on the right, so the plots are narrower than the 1142 px box they get · low · widen the plots to the full canvas width · yes
16. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
17. **Fig 2 C caption** · says 3 calls outside the block are planted events, but no planted row is drawn · low · add a planted row or drop the sentence · yes
18. **Tables** · §4 and §10 tables unnumbered, uncaptioned; Table 1 has no scroll cue at 400 px · low · number as Tables 1–3 (renumber references); add a fade or "scroll →" hint · yes
19. **Document** · no build date or commit stamp · low · stamp date and commit in the footer · yes
20. **Mobile figures** · ~2.5pt text at 400 px and no way to open full size · low (desktop document) · wrap each `<img>` in a link to itself · yes
21. **Axis-label wording** · "32 ROI" / "33 ROI" in raster labels vs "15 ROIs" elsewhere · low · pluralize consistently · yes
22. **Rows named by position** · "Bottom row", "Third row", "Top lane" in captions and prose · low · adjudicate against the "never spatial words" rule, or name rows by content · yes

Corrections to the brief: the image column is 1142 px, not ~1108, and the page has 3 tables, not 2.
