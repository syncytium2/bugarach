> Archived verbatim. Paths are shown as placeholders (SAP004). The reviewer quoted no recording id or single-call value.

## Murderboard follow-up (step 4, pass 2): full-panel briefing, current build

I ruled on every finding in the 22 reports against the page as built now. The page, `briefing.json`, the SVGs and PNGs were all written at about 21:28–21:29, from generator commit f69f884f, "murderboard blind round 2 applied". I read the page as text with every collapsed section opened, and rendered it with the repo `.venv` Playwright at 1200, 1920 and 390 px, light and dark. I looked at the PNGs and read the generator and its test. Scratch files are in `<scratchpad>/mbfu/` only. Nothing in the repo or the darkroom was edited. No recording id or value from a single call is quoted below.

Abbreviations: **R1** = round 1, **R2** = round 2. **F** = fixed · **NF** = not fixed · **MV** = moved (the defect now sits somewhere else, or a fix broke something it was not aimed at) · **SUP** = superseded (the surrounding content changed so the finding no longer applies).

### Round 1

| Report · id | Finding | Verdict | Evidence |
|---|---|---|---|
| 01 · 1 | Caption times rounded (a "20m60s") | F | Captions use `time_label(round(t))`; a test pins 7m59s, 20m, 1m40s and 0s |
| 01 · 2 | Examples' CoactDetect is its proposal, not stated | F | "Read this first" box, and lanes labelled "CoactDetect · proposal" |
| 01 · 3 | Median rule false for the old Figure 10 | F | The rule is stated: 10 s inside the window, preferring a recording not yet shown |
| 01 · 4 | "120 s either side" false at a recording's start | F | Captions print the actual window, with "cut at the baseline window's edge" |
| 01 · 5 | Count rows labelled "shipped" | F | Now "starting point (untuned)", with a Terms entry |
| 01 · 6 | Mean F1 does not subtract to ΔF1 | F | Tables 3–5 captions explain the two estimators |
| 01 · 7 | Table 1 top row ignores flags | F | Column is now "top unflagged row" |
| 01 · 8 | 0.10 printed against a 0.1 limit | F | Now 0.103 against 0.100 |
| 01 · 9 | SCE merge-gap reason dropped | F | "Merge gap none (no merge)" appears on the fast and combined SCE proposals |
| 01 · 10 | README's one-row budget count unexplained | F | One line in the Budgets bullet |
| 01 · 11 | Signed zero "+0.000 [-0.001, …]" | NF | Table 3 row 17 still shows it (cosmetic) |
| 01 · 12 | No pool sizes | F | Tables 6–8, plus "one of N" in each caption |
| 02 · 1 | Ruling 5 misquoted | F | Terms separate ruling 5 (off-value) from part 1 (bracketing) |
| 02 · 2 | k = 0 credited to ruling 5 | F | "at its lower limit by design … not a ruling-5 value", noted and not flagged |
| 02 · 3 | Grid edges credited to the wrong rulings | F | Marks cite ruling 7, ADR-0009 decision 5 and part 1 |
| 02 · 4 | Old bench shown against ruling 2 | F | "Tony asked … ruling 2 retired it … decides nothing" |
| 02 · 5 | Retired term "promiscuity probe" | F | Page uses elevated-rate test and no-coordination recording |
| 02 · 6 | 2.5 s tolerance hard-coded, span-to-span not said | F | Imports `TOL_SEC`; "applied here span to span" |
| 02 · 7 | locust name could leak through `--also` | F | `--also` now copies only the simulated half (SVGs and leaderboard.json) |
| 02 · 8 | Say "percentile" bootstrap | F | "95% percentile-bootstrap" |
| 02 · 9–10 | Verified items | — | Nothing to fix |
| 02 · 11 | ORX check missing | F | ORX paragraph with ρ and top rows |
| 03 · F1 | Caption times | F | As 01 · 1 |
| 03 · F2 | CoactDetect meaning changes between sections | F | Callout, lane labels, per-stream "is itself on a search limit" line |
| 03 · F3 | Budget count contradicts the README | F | Reconciling line added |
| 03 · F4 | k = 0 marked §5 | F | As 02 · 2 |
| 03 · F5 | Mean F1 vs ΔF1 | F | As 01 · 6 |
| 03 · F6 | Retired glossary terms | F on the page | Page wording fixed; the glossary itself not updated (see R2 03 · 13) |
| 03 · F7 | LoCo setting unlabelled | F | Every lane and heading carries its setting |
| 03 · F8 | Leader rule conditions unstated | F | Full rule stated; every passed-over row named with a reason |
| 03 · F9 | tube_part precision printed as 0.10 | F | 0.103 |
| 03 · F10 | Count runs undated; mixed time formats | F | Both follow-up runs dated; one 12-hour EDT format |
| 03 · F11 | "best seed" label | F | "no pick; best was training run 5 of 5", defined in Terms |
| 03 · F12 | Over-budget top row in Table 1 | F | As 01 · 7 |
| 03 · F13 | "1 rows" | F | "1 row" |
| 03 · F14 | SCE merge-gap mark missing | F | Present |
| 04 · 1 | No F1 without decoys | F | Column in every table; decoys defined; Table 2 gives decoy counts |
| 04 · 2 | No kind counts; edge calls | F | Tables 6–8; 10 s edge rule |
| 04 · 3 | Examples' reference differs from the leaderboard's | F | Callout box |
| 04 · 4 | Caption times | F | — |
| 04 · 5 | Reference moved between benches | F | Table 2 shows the reference's own change; comparison against its proposal added |
| 04 · 6 | Order read as a ranking; noise unit; multiplicity | F | "sorted by ΔF1 … level within 0.01"; "uncorrected"; level counts given |
| 04 · 7 | Old bench against ruling 2; ORX missing | F | Both addressed |
| 04 · 8 | Pooled backgrounds; merges; "background" undefined | F (partly) | Recall per background, merged calls and a background definition added; no ΔF1 per background |
| 04 · 9 | Mean F1 columns | F | — |
| 04 · 10 | Spread across training runs hidden | F | "held-out F1 of the 5 runs: a–b" |
| 04 · 11 | Agreement rule many-to-one, hides merges | F | Stated; calls that match two or more counted in the Tables 6–8 captions |
| 04 · 12 | Figures 6, 9, 10 pictures | F / SUP | Windows cut at the baseline edge and labelled; figures replaced |
| 04 · 13 | No per-group breakdown | F | Group columns and per-hour rates |
| 04 · 14 | Limits unsourced; flagged rows counted as "above" | F (partly) | Per-detector source line; "unflagged" column; no reason given for the 0.150 limit |
| 04 · 15 | Print precision | F | Three decimals |
| 04 · 16 | Rows passed over silently | F | Listed |
| 04 · 17 | Figure 5, LoCo ≈ CoactDetect | SUP | Slow leader is now line |
| 04 · 18 | One colour means over budget and no pick | NF | Orange still means both (Figure 1a caption) |
| 05 · F-1 | No sentence states the finding | F | Per-stream headline |
| 05 · F-2 | Time stamp | F | — |
| 05 · F-3 | The 47-word sentence | F | Rewritten |
| 05 · F-4 | "candidates"; seed repetition | F | — |
| 05 · F-5 | Table 1 caption does not parse | F | Rewritten |
| 05 · F-6 | Number agreement | F | — |
| 05 · F-7 | Marks printed twice; hidden excess | F | "on both benches"; three decimals |
| 05 · F-8 | Passed-over sentence garbled | F → MV | Old garble gone; the new slow runner-up note is wrong in a new way (N3) |
| 05 · F-9 | Leader used before defined; folder path | F | — |
| 05 · F-10 | Hover said ten times; floors undefined | F | — |
| 05 · F-11 | Slash-pair Terms | F | — |
| 05 · F-12 | Table 5 lead-in garbled | F | — |
| 05 · F-13 | Personal absolute path | F | 0 occurrences in index.html and briefing.json |
| 05 · F-14 | Invites copying into the export folder | F | Removed |
| 05 · F-15 | "seed" collision; abbreviations | F (partly) | Seed split into simulation seed and training run; **SCE still never expanded** |
| 05 · F-16 | Five words for one flag | F | One template |
| 05 · F-17 | Mixed time formats | F | — |
| 05 · F-18 | ADR only indexed | F (partly) | Named once; ruling and part indexes remain (see R2 05 · N1) |
| 06 · 1–5 | Time, reference, tiny pools, tolerance wording, participants label | F | — |
| 06 · 6 | Old bench against ruling 2 | F | — |
| 06 · 7 | Ruling 5 scope | F | — |
| 06 · 8 | LoCo proposal identical to CoactDetect proposal | F | "one result, shown twice, and counted once"; runner-up lane differs now |
| 06 · 9–10 | Table 1 flags; mean F1 | F | — |
| 06 · 11 | Learned models use CoactDetect's budgets | F | Stated |
| 06 · 12 | Call at a recording edge | F | 10 s rule |
| 06 · 13 | Flagged rows can lead | F | Excluded |
| 07 · 1 | Time formatter | F | — |
| 07 · 2 | `BUDGET_WORDS` copy | F | Imports `BUDGET_NAME` |
| 07 · 3 | Unmeasured budget handling | F | "not measured" path; close-events stated as retired |
| 07 · 4 | Viewer ignores `t=` | F | `t` dropped; captions give the time |
| 07 · 5 | `NAME` copy | F | Uses `display_name` |
| 07 · 6 | `CODED` copy | SUP | `ran_on_real` reads `chosen`; count rows labelled "did not run" |
| 07 · 7 | Tolerance copy | F | — |
| 07 · 8 | First-treatment rule | F | Ordered by `win_start` |
| 07 · 9 | Hover and lane re-implementation | NF (low) | Lanes still built locally |
| 07 · 10 | Dataset check; no stamp | F | `scored_on` used; `examples.dataset` stamped |
| 07 · 11 | PNG scale 2 | F | scale=3 |
| 07 · 12 | CSS hand-rolled | NF | Own palette, not `report.css` |
| 07 · 13 | Fixed EDT offset | **MV** | Code uses `ZoneInfo`; Terms still hard-code "EDT, UTC − 4 h" |
| 07 · 14 | Stem parse | F | `split` then `rsplit` |
| 08 · 1 | Detectors never described | F | "What each row is" box, before Figure 1 |
| 08 · 2 | Code identifiers as display names | NF | chorus_gain_norm_part etc. are still the names in figures, headings and lanes; only the suffix is explained |
| 08 · 3 | Raw parameter names | F | Plain words with units |
| 08 · 4 | Seed means two things | F | — |
| 08 · 5 | How-to box unreadable | F | — |
| 08 · 6 | Table 1 caption | F | — |
| 08 · 7 | Red misleading; open red missing from legend | F | Orange; both forms in the legend; legend and axis at the top |
| 08 · 8 | "best seed" | F | — |
| 08 · 9 | Caption time mismatch | F | — |
| 08 · 10 | Example call not marked | F | "this call ▼" lane |
| 08 · 11 | Lanes drawn as tick bars | NF | Lanes still spans; a ▼ lane was added above |
| 08 · 12 | Lane colours; third lane unexplained | F | Distinct colours; "the runner-up" named |
| 08 · 13 | Edge call | F | — |
| 08 · 14 | Clipped y label | F | Not clipped in the current PNGs |
| 08 · 15 | Bare "t" | F | "time in recording (min:s)" |
| 08 · 16 | Code path; baseline undefined | F | — |
| 08 · 17 | Passed-over sentence | F | — |
| 08 · 18 | Floors undefined | F | Terms: participation floor, floor variant |
| 08 · 19 | ADR, fresh seeds, adopted | F | Byline |
| 08 · 20 | Elevated-rate; 0.10 | F | — |
| 08 · 21 | Terms incomplete | F (partly) | Most added; SCE missing; no per-term links, one "defined at the end" pointer |
| 08 · 22 | Setup box after the links | F | Now at the top of §2 (but see R2 11 · 4) |
| 08 · 23 | Where the export folder lives | F | Named |
| 08 · 24 | Absolute path | F | — |
| 08 · 25 | Re-pick instruction; ▼ vs bars | F | — |
| 08 · 26 | Tone | — | — |
| 09 · 1 | No figure above the fold | **MV** | First figure now starts at y≈2309 px at 1200 px (was 940). The headline box (598 px) and Tables 1–2 sit above it |
| 09 · 2 | One long column, axis at the bottom | F (partly) | Three panels, each with top and bottom axes; still stacked, not side by side |
| 09 · 3 | Dumbbell | F | Gray join line |
| 09 · 4 | Tables 2–4 in the way | F | Collapsed `<details>` |
| 09 · 5 | Table 1 as bars | NF | Still a table |
| 09 · 6 | How-to box | F | Collapsed |
| 09 · 7 | PNG geometry | F (partly) | Right-hand blank gone; raster about 40% of height; long lane-label gutter remains |
| 09 · 8 | Caption boilerplate | F | Lanes stated once per stream |
| 09 · 9 | 3×3 structure | NF | No grid or header |
| 09 · 10 | §3 has no raster | F (partly) | 8 thumbnails of the review pages (lazy-loaded, verified); Table 9 collapsed |
| 09 · 11 | Setup box as prose | NF | — |
| 09 · 12 | Figures confined to the column at 1920 px | NF | Column still 1080 px |
| 09 · 13–14 | No flag | — | — |
| 10 · row 0 | Title vs h1 | F | Match |
| 10 · row 2 | "1 rows" | F | — |
| 10 · row 3 | Figure 1 at 390 px | F (cue) | "Scroll the figure sideways →" on all 12 figures |
| 10 · row 3a | Legend at bottom; swatches | F | — |
| 10 · row 4 | Units on marks | F | — |
| 10 · row 5 | PNG type size | F | Native 3540 px shown at 1080; about 15 px or more |
| 10 · row 6 | 16% blank; overflow | F | Plot runs to the edge |
| 10 · row 7 | Times | F | — |
| 10 · row 8 | Figure 9 label | F | — |
| 10 · row 9 | Figure 10 edge | F | — |
| 10 · row 10 | Subject call unmarked | F | ▼ lane |
| 10 · row 11 | x label; one gray for many detectors | F | — |
| 10 · row 13 | Page scrolls sideways at 390 | F | scrollWidth 390 = viewport |
| 10 · row 15 | `&t=` ignored | F | Dropped |
| 10 · row 17 | Alt text | F | Descriptive |
| 11 · 1 | Headline never stated | F | — |
| 11 · 2 | Eligible leader not in §1 | F | — |
| 11 · 3 | Encoding at the bottom of Figure 1 | F | — |
| 11 · 4 | Viewer used before explained | F | — |
| 11 · 5 | Passed-over note partial | F | — |
| 11 · 6 | Terms pointer | F | — |
| 11 · 7–8 | Sound | — | — |

### Round 2

| Report · id | Finding | Verdict | Evidence |
|---|---|---|---|
| 01 · F1 | Shipped settings on a search limit go unmarked | F | Slow LoCo, rate+context and SCE shipped, and combined LoCo shipped, now carry †; k = 0 treated alike everywhere |
| 01 · F2 | ORX check leaves out the count rows | F | Both ORX files read; "6 intervals of 59" (the duplicate is counted once) |
| 01 · F3 | tube_part description wrong | F | Separate sentence: no per-cell stage |
| 01 · F4 | Upper-middle "median" | SUP | Median column and headline figure removed |
| 01 · F5 | Outside-stretch test gated on quiet only | F | Stated |
| 01 · F6 | Merged-calls and background definitions | F | ("measured on the fast stream" still omitted, trivial) |
| 01 · F7 | Byline omits bench*.py | F | — |
| 02 · F1 | _part note | F | — |
| 02 · F2 | Merged calls: scored events | F | — |
| 02 · F3 | Close-events "not run" | F | "retired" |
| 02 · F4 | Noise-unit "level" attributed to the ADR | F | "This page treats … borrowing" |
| 02 · F5 | CICADA uncited | F (page) | "the Cossart lab's software"; the tree disagreement is outside the page |
| 02 · F6 | Why the ruling-3 fallback is in force | NF | Status not stated |
| 02 · F7 | chorus_norm wording; lineage | F | — |
| 02 · F8 | SPIKE-synch attribution | F | — |
| 02 · F9 | Floor definition | F | — |
| 02 · F10 | 120 s cap | F | — |
| 02 · F11 | Informational | — | — |
| 03 · 1 | Median | SUP | — |
| 03 · 2 | 22 vs 23 rows | F | "of the 21 other rows"; header "CoactDetect's shipped row among them" |
| 03 · 3 | "sit above" ambiguous | F | "95% interval of ΔF1 wholly above zero" |
| 03 · 4 | k = 0 inconsistent | F | — |
| 03 · 5 | Duplicate counted twice | F | Counted once |
| 03 · 6 | ORX vs the README's 17 | F | Explained |
| 03 · 7 | Runner-up parenthetical misattached | F | — |
| 03 · 8 | Counting variant unstated | F | Stated in the leader paragraph |
| 03 · 9 | Combined SCE merge-gap axis | F | Supported by the bracketing record (R1 01 · 9) |
| 03 · 10 | Fast SPIKE-synch "rescue" disagreement between companions | NF | Page silent |
| 03 · 11 | Rename of the count rows | F | "the count folder calls it 'shipped'" |
| 03 · 12 | "floor" collision | F | "participation floor" |
| 03 · 13 | Terms missing from GLOSSARY.md | NF | Outside the page; only "the glossary's distractors" added |
| 03 · 14 | Ranking used as a tiebreak | F | "chosen by the rule among rows the leaderboard cannot separate" |
| 03 · 15 | "one-off" at 3 calls | F | "one of only 3" |
| 03 · 16 | "the both benches"; "1 frames" | F | — |
| 03 · 17 | aria-label numbering | F | "Figure 1a…" |
| 03 · 18 | C_min, dt undefined | F | Plain names |
| 03 · 19 | Absolute paths in briefing.json | F | Relative |
| 04 · 1 | Fast result is mostly decoys | F | Headline plus Table 2 |
| 04 · 2 | Low-recall rows ranked high | F | Recall column; decoy caveat made general |
| 04 · 3 | Slow gap is the reference's recall and merges | F | Headline; level counts; leader chosen within noise |
| 04 · 4 | ORX check has no power | F | ρ and top rows |
| 04 · 5 | "unflagged" not one bar | F (partly) | Per-detector limits stated; no reason for the 0.150 limit |
| 04 · 6 | Agreement units | F | "(whose calls)"; matches to two or more counted |
| 04 · 7 | Combined leader under-calls | F | "the leader misses many events CoactDetect calls: 3 against 71" |
| 04 · 8 | Slow one-off | SUP | Slow figures changed |
| 04 · 9 | Examples cannot test the top rows | **MV** | Fix added a hard-coded sentence that is false tonight (N1) |
| 04 · 10 | Duplicates; median | F / SUP | — |
| 04 · 11 | Seed power differs between benches | F | Stated |
| 04 · 12 | Pooled backgrounds | F (partly) | Recall per background |
| 04 · 13 | Stale files beside the page | F | Builder clears `example_*`/`figure1_*`; `figure1_leaderboard.svg` gone |
| 05 · P1 | Runner-up modifier | F | — |
| 05 · H1 | Headline is a numeric dump | F (partly) | Verdict plus reasons per stream; still dense (see 09 · 1) |
| 05 · A5 | Interval wording | F | — |
| 05 · D2 | "unflagged" used before defined | NF | Headline uses "top unflagged row" before the Table 1 caption defines it |
| 05 · P2 | Decoy result buried | F | — |
| 05 · C1 | README reference | F | Moved into `<details>` |
| 05 · A2 | "reading of intervals" | F | — |
| 05 · A3 | "Change side" undefined | F | — |
| 05 · A1 | Pronoun | F | — |
| 05 · A4 | "reference" two senses | F | "the comparison side" |
| 05 · R1 | Name stutter | F | — |
| 05 · G1 | "the both benches" | F | — |
| 05 · N1 | Index instead of name | NF | "ADR-0010 ruling 5 / part 1" throughout |
| 05 · A6 | Zero-indexed runs | F | 1–5 |
| 05 · S1 | British spellings | F | favor/gray/center/standardizes |
| 05 · G2 | Percentile ordinal; degenerate range | F → **MV** | "0.82 in all 5 runs" and ordinals fixed, but the percentile now prints to 7 decimals (N4) |
| 05 · G3 | Missing "and" | F | — |
| 05 · G4 | Reopen sentence | F | Rewritten |
| 05 · G5 | "one of 1 call" | F | "the only call of its kind"; "80 calls away" |
| 05 · D1 | Missing terms | F (partly) | leader, unflagged and level added; SCE not |
| 05 · T1 | "At a glance." | F | — |
| 06 · 1 | No comparison against CoactDetect's proposal | F | Table 1 column and headline counts |
| 06 · 2 | Close-events | F | — |
| 06 · 3 | Strict vs looser limit reading | F (partly) | By-design limits separated; the combined CoactDetect grid edge is still flagged with no note that the looser reading is open |
| 06 · 4 | ORX coverage and wording | F | — |
| 06 · 5 | ΔF1 pooling | F | Captions |
| 06 · 6 | Hard-coded "on a search limit" | F | Per-stream sentence built from the flags. But see N1: a new hard-coded sentence appeared |
| 06 · 7 | `ran_on_real` inferred | F | Reads `chosen` |
| 06 · 8 | SCE extent vs width | NF | Latent |
| 06 · 9 | "disagrees" also requires agreement | F | "both agrees and disagrees" |
| 06 · 10 | Core-count status | NF | — |
| 06 · 11 | merged calls; floor | F | — |
| 06 · 12 | Bootstrap literal; "level" | F | `BOOTSTRAP` imported |
| 06 · 13 | Dropped seeds hidden | NF | Latent; `n_seeds` carried in the model, never marked |
| 07 · F1 | Setting names re-typed | F → **MV** | Now `PLAIN`/`_vu`; brings the 7-decimal percentile (N4) |
| 07 · F2 | Scored-dataset check fails open | F | `scored_on` |
| 07 · F3 | `ran_on_real` | F | — |
| 07 · F4 | Participants rule from current code | F | Read from results, constant as fallback |
| 07 · F5 | Case-sensitive groups | F | `in_group_order`/`group_key` |
| 07 · F6 | Treatment order | F | `win_start` |
| 07 · F7 | Stream normalisation; NaN widths | F | Stream lower-cased; widths clamped with `isfinite` |
| 07 · F8 | CSS | NF | — |
| 07 · F9 | Bootstrap literal; lane colours | F / NF | Bootstrap fixed; leader and runner-up colours still differ from the review pages, unstated |
| 07 · note | Terms hard-code EDT | NF | See R1 07 · 13 |
| 08 · F1 | Undefined terms at the top | F | — |
| 08 · F2 | Code identifiers | NF | As R1 08 · 2 |
| 08 · F3 | Run numbering | F | — |
| 08 · F4 | What-is-compared box order | F | Before Figure 1; bases before variants |
| 08 · F5 | Internal paths | F (partly) | Paths gone from visible text; "the worker's run notes" remains |
| 08 · F6 | Budget tests undescribed | F | — |
| 08 · F7 | Parameter jargon | F | Percentile precision: N4 |
| 08 · F8 | held-out; grammar | F | — |
| 08 · F9 | Reopen does not exist from file:// | F | One named viewer tab (target `bugarach-viewer`); viewer listens for `hashchange` |
| 08 · F10 | Accordion step; site | F | "expand Open a folder" |
| 08 · F11 | Python command; time | F | — |
| 08 · F12 | Reference change in §2 | F | Callout |
| 08 · F13 | Runner-up | F | — |
| 08 · F14 | "one of 1"; "/h" | F | — |
| 08 · F15 | Leader-only looks like agreement | F | Caption gives the nearest reference call's distance. But see N2 |
| 08 · F16 | Row order unstated | F | "sorted by their event count" |
| 08 · F17 | Terms incomplete | F (partly) | SCE missing |
| 08 · F18 | 22 vs 23 | F | — |
| 09 · 1 | 180-word box above Figure 1 | NF, worse | Box now about 598 px tall, and Tables 1 and 2 were added above the figure |
| 09 · 2 | Prose after Figure 1c | F | Collapsed |
| 09 · 3 | Figure share; margins | NF | — |
| 09 · 4 | Prose before Figure 2 | NF | Setup, callout and rule paragraphs still come first; no selection matrix |
| 09 · 5 | Lane-label gutter | NF | About 35% of the width |
| 09 · 6 | §3 wall of ids | F (partly) | Page thumbnails; id list collapsed |
| 09 · 7 | Stacked panels | NF | — |
| 09 · 8 | Caption bookkeeping | NF | Grew: distance sentence added |
| 10 · 1 | Figure 1b label clipped | F | Text min x 68 > SVG left 60 |
| 10 · 2 | Tables 2–4 overflow at 1200 | NF, worse | Overflow is now 1401 vs 1080 px (321 px; was 70), after the recall column was added |
| 10 · 3 | 390 px figures | F | Scroll cue |
| 10 · 4 | Leftover files | F | — |
| 10 · 5 | viewer.html is the branch copy | NF | viewer.html unchanged (17:40) |
| 10 · 6 | One fast link without calls | not checked | — |
| 10 · 7 | Unnumbered tables | F | Tables 6–8 numbered |
| 10 · 8 | x unit | F | — |
| 10 · 9 | PNG type margin | note | Still about 15 px |
| 11 · 1 | Reading key after the figures | F | Headline defines row, ΔF1, reference and old bench; Table 1 caption defines unflagged |
| 11 · 2 | Table 1 after the figures | F → **MV** | Moved up, and that pushed the first figure 2.5 screens down (see R1 09 · 1) |
| 11 · 3 | §1→§2 handoff | F (partly) | Callout added; Figure 1 does not mark which rows ran on the real recordings |
| 11 · 4 | Setup box in the wrong section | NF | Still at the top of §2; §3 back-links. (Conflicts with R1 11 · 4 and 08 · 22, which asked for it there) |
| 11 · 5 | What-is-compared box | F | Collapsed before Figure 1 |
| 11 · 6 | No "what this does not settle" place | NF | — |
| 11 · 7 | Note | — | — |

### Moved and not-fixed findings that matter, by severity

**Moderate**
- **R1 09 · 1 and R2 09 · 1 / 11 · 2 (moved, worse):** Tony asked for the leaderboard first, and the leaderboard figure is now further away. At 1200 px, Figure 1a starts at about y=2309 px, roughly 2.5 screens down (it was 940 px in round 1). The headline box (598 px), Table 1 (907 px) and Table 2 (327 px) all come first.
- **R2 10 · 2 (not fixed, worse):** Tables 3–5 are 1401 px wide in a 1080 px box at 1200 and 1920 px. The last columns sit behind a sideways scroll, and those tables have no scroll cue.
- **R2 04 · 9 (moved):** see N1 below.

**Minor**
- R1/R2 08 · 2: code identifiers are still the display names.
- R1 08 · 11: lanes are still drawn as tick bars.
- R1 04 · 18: orange still means both "over budget" and "no pick".
- SCE is never expanded (R1 05 · F-15, 08 · 21; R2 05 · D1, 08 · F17).
- R2 05 · D2: "unflagged" is used before it is defined.
- R2 05 · N1: rules are indexed by ADR number rather than named.
- R2 11 · 4: setup box placement; the two rounds asked for opposite places.
- R2 11 · 6: no "what this does not settle" place.
- R1 07 · 13: EDT is hard-coded in Terms.
- R1 07 · 12 / R2 07 · F8: CSS not the house stylesheet.
- R2 02 · F6 and 06 · 10: status of the ruling-3 core count not stated.
- R2 03 · 10: fast SPIKE-synch disagreement between companions.
- R2 03 · 13: GLOSSARY.md not updated.
- Latent code items: R2 06 · 8, 06 · 13, 07 · F9 lane colours.
- R1 01 · 11: signed zero.
- R2 10 · 5: viewer.html is the branch copy.

### New defects the fixes introduced

- **N1 (moderate): a new hard-coded sentence that is false tonight.** The "Read this first" callout says "The leaderboard's top rows mostly did not run on the real recordings at all, so these examples cannot test them." The string is fixed text in `make_briefing.py` (around lines 1372–1373), the same latent pattern R2 06 · 6 asked to remove. The page's own passed-over lists contradict it:
  - Fast: of the 8 rows above the leader, only 3 "did not run". The rest ran and were passed over for a budget or a search limit.
  - Combined: the leader is the top row of Figure 1c, so the examples do test the top row there.

  Fix: build the sentence from the passed-over reasons, per stream.
- **N2 (minor): new rounding contradiction in a Figure 3 caption.** The added sentence prints the nearest reference call's distance at 1 decimal, and it reads as equal to the 2.5 s tolerance while saying "beyond" it. This is the same class of defect as R1's "0.10 against a limit of 0.1", moved into the new caption text. Print enough digits to show the excess. Separately, the same sentence prints long gaps as raw decimal seconds rather than minutes format (Figure 4).
- **N3 (minor): wrong reason on the slow runner-up list.** Two rows are listed as "no disagreement with CoactDetect · proposal to show", but each has dozens of calls only its own. What they lack is disagreement in one direction (0 CoactDetect-only). The parentheses are also nested. Fix the template near line 798: "never misses a call CoactDetect makes".
- **N4 (minor): percentile shown to 7 decimals.** The threshold now reads "99.9921875th percentile". Adopting `_vu` (R2 07 · F1) removed a rounding R2 08 · F7 had asked to keep.
- **N5 (minor): two counts of "rows level with the top row" disagree.** Table 1 and the headline give "N other rows within 0.01". §2 says "N+1 rows sit within 0.01 F1 of the top unflagged row", which counts the top row itself (fast 7 vs 8, slow 14 vs 15, combined 1 vs 2). Use one wording.

What I checked and found clean: all 9 example PNGs and 8 thumbnails load (the thumbnails are lazy and load on scroll). No console errors. No page-level sideways scroll at 390 px. Smallest text is 15 px. Group order is DI, OVX, MALE, ORX throughout. Figures run 1a–1c and 2–10, tables 1–9. Neither index.html nor briefing.json contains a personal path, and `--also` copies only the simulated leaderboard.

Paths: artifact `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`; generator `<worktree>/tools/make_briefing.py`; renders and DOM metrics in `<scratchpad>/mbfu/` (`dom.json`, `text.txt`, `full_*.png`, `fig1*_*.png`, `rast_*.png`).
