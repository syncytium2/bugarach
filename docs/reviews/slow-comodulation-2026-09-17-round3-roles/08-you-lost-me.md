GRANT 8 ok — Read, Grep, Glob

# Role 8, naive-reader accessibility: `docs/learned/slow_comodulation/README.md` and its six figures

**Summary:** 5 locations are blocking, 10 findings are major and 13 are minor. The definitions section and all three figure-schematic captions work well. The problems are concentrated in the parts a reader meets **first** (the "why this page exists" box, the short answer, the Figure 1 caption) and in the **late** sections (the effective-mice bullets, the label-free thread section). Illustrations are missing for episode removal and for the count-variance ratio. Two things are easy to misread: "heaviest mouse" and the correlogram layout.

All paths are relative to `bugarach-worktrees/unsup-slow-comodulation/`. The artifact is `docs/learned/slow_comodulation/README.md`, and the figures sit beside it.

## Per-location verdict

| location | terms / identifiers / symbols first used here | defined here | cold reader follows? |
|---|---|---|---|
| Title | co-modulation, onset rate, ROIs, rigid shift | co-modulation (glossed) | yes (defined about 40 lines later) |
| "Why this page exists" box | rigid shift, detector trained without labels, label-free detector thread, coordination, `main`, branch `unsup/rigid-shift-report-residuals`, baseline windows, milestone, measured/argued, 95 % interval from resampling mice | measured, argued | **blocking** (5 undefined: rigid shift, label-free thread, baseline windows, milestone, `main`/branch name) |
| The short answer | lab fast stream, lab slow stream, population onset count, 1-minute bins, independent ROIs, CoactDetect, "events removed", straight-line trend, group of mice, Dard et al. 2022 dataset, benchmark generator, promiscuity probe, label-free models, training contrast, "rigid shift at 1.6–20 s" | Dard dataset (in vivo pups); the 2-minute block scramble, roughly | **blocking** (at least 6 undefined: fast/slow stream, CoactDetect, benchmark generator, promiscuity probe, training contrast, the shift radius) |
| Two ways ROIs are active together | ROI, onset, producer, stream, fast/slow, lit, coordinated event, shared modulation, drift, label-free detector, surrogate, rigid shift, *J*, circular shift, block control, CoactDetect, episode, CA1, "local circular shift" | all but CA1 and "local circular shift" | yes |
| Figure 1 caption | planted-event world, generator (`generator_spec.json`), promiscuity probe, distractors, 20 s world, 5-minute world, shared multiplier, depth, share of ROIs lit, raster, cross-correlogram, generator's background | the worlds, share lit | **blocking** (promiscuity probe, distractors, depth, generator's background; excess coincidence is only defined in the *next* section, but G–H plot it) |
| Paragraph pointing to `one_recording.png` | `<darkroom>`, FOUNDATIONS §5 | none | no (a public reader cannot open it, and the reason given is an internal reference) |
| Two measurements | excess coincidence, *ℓ*, independence level, shoulder, *T*, count-variance ratio, bin width *w*, Schluter's variance ratio, window, detrending | all except whether *ℓ* is signed | yes |
| Figure 2 caption | lane, block edge | yes | yes |
| Figure 3 caption and bullets | shallow 1-minute world, arm, "whole spec", "y to 0.9", "the null" (legend), promiscuity probe (finally defined here), fixed 60 s grid | arm, episodes removed then block control, promiscuity probe | yes, with friction (2 new undefined: whole spec, the null) |
| Figure 4 caption | raw, detrended (hollow), whiskers | yes | yes |
| Figure 5 caption | calibrated operating point, context window, *α*, episodes merged across gaps | *α* | yes (2 jargon terms) |
| Bullets under Figures 4 and 5 | "a single circular shift scored against the reference", expected onset pairs, effective mice, "weighted as the correlograms weight recordings / as the count variance weights them", `summary.json` | per-pair ratio (inline formula) | **blocking** (the reference, effective mice, the two weightings, expected onset pairs) |
| Collapsed numbers block | 8-draw mean, "circular 1-minute variance", paired differences | 8-draw mean | yes, for a reference block |
| By group / Figure 6 | DI, MALE, ORX, OVX, "heaviest mouse", pooled vs equal-weight, imaging day | the group labels are glossed but the abbreviations are not expanded | yes, but contains a misreading trap ("heaviest mouse") |
| Aside on the slow-stream dip | extractor dead time, "per second of interval" counts, quiet interval | dead time, implicitly | yes, but misplaced (it is about Figure 5, not groups) |
| What this changes for the label-free thread | training contrast, paired crops, fits, "the unmerged branch", `tools/check_small_j_mixes_events.py`, commits `f55db21`/`4518d21`, `count_excess`, "baseline" in a new sense | none | **blocking** (training contrast, crops, fits, `count_excess`; "baseline" clashes with its earlier meaning) |
| The decision this sets up | focus/slice-position change, bleaching, FOUNDATIONS | mostly | yes |
| What this does not settle | carrier, field-step exclusion (renamed from the earlier "brightness step" removal), effective number of mice | partly | yes |
| Published lineage / Reproduce | citations, tool paths, `checks`, `checks_by_group` | n/a | yes (identifiers belong in Reproduce) |

## Per-panel: what a cold reader sees, and the false-friend check

| panel | what a cold reader sees | looks like · axes in that idiom · same here? |
|---|---|---|
| Fig 1 A | A noisy step trace near 0.05–0.1 with a few tall spikes (about 0.28–0.38) across 20 minutes | population rate / PSTH · time, rate · yes |
| Fig 1 B | Almost the same noisy trace, also with tall isolated spikes (0.37 at ~6m, 0.35 at ~14m). **It looks like A, i.e. like events** | PSTH · yes, but the spikes are phantom events (see finding 4) |
| Fig 1 C | A noisy trace, slightly flatter, with a weak rise after 15m; the 5-minute drift is not visibly there | PSTH · yes |
| Fig 1 D | A 1-minute raster: a vertical column of ticks at ~33 s, plus one row with ~15 ticks running across the whole minute | spike raster · time, one row per cell · yes |
| Fig 1 E | A raster where ticks cluster between ~35 and 50 s | raster · yes |
| Fig 1 F | A raster of evenly scattered ticks with nothing to see (drift cannot show in one minute) | raster · yes |
| Fig 1 G | Log-lag lines: pink high then falling by 1m, brown flat to ~1m then falling, orange dropping to zero by 1 s, gray dotted at zero | cross-correlogram · signed lag centred on 0, linear, symmetric peak · **no**: unsigned lag, log axis, peak pinned at the left edge |
| Fig 1 H | The same curves on a linear lag axis to 2m: orange is a spike at 0, pink decays by ~50 s, brown stays at 0.2–0.4 to 2m | correlogram · one-sided, otherwise yes |
| Fig 2 A | Four rows of ticks over 4 minutes; one aligned column at 1m40s | raster · yes |
| Fig 2 B | The same rows shifted a little; the column spreads over ~1m28s–1m55s; a note says one onset was dropped | raster · yes |
| Fig 2 C | Rows scattered with no alignment | raster · yes |
| Fig 2 D | Rows scattered, with a purple ▼ "2-minute block edge" floating in a gap above the panel | raster · yes (the edge has to be projected down across white space) |
| Fig 3 A | A black line from 0.53 at the shortest lag to 0 by 1 s; a light-blue low plateau to ~3 s; everything else flat | correlogram · same false friend as Fig 1 G |
| Fig 3 B | Black and light blue high (~0.65) to ~10 s then falling; the other blues lower; purple and green at ~0.18 | correlogram · as Fig 1 G |
| Fig 3 C | All lines form a broad plateau at 0.3–0.45 falling to 0 at 5m | correlogram · as Fig 1 G |
| Fig 3 D | A tangle of noisy lines near 0.05 on a magnified y axis, all dropping to 0 after a minute; the three blues are hard to tell apart | correlogram · as Fig 1 G |
| Fig 3 E | Black starts at 1.6, and all lines sit on a plateau near 1.0 that falls at minutes | correlogram · as Fig 1 G |
| Fig 3 F | Coloured markers per world on a log y axis: events and background just under 1; 20 s, 5 min and benchmark at 4–9; shallow at ~1.7 | categorical dot plot · yes; but the rigid-shift ▼ is the same shape as the legend's "curve above the view" ▼ |
| Fig 4 A | Black dots at 2–3 rising with bin width; the other markers near 1 at 1 s, climbing to 2–3 at 1 minute | grouped dot plot · categories on a log-looking x axis, so the spread-out markers can read as different bin widths (minor) |
| Fig 4 B | Black at 9–12 at every width; at 1 minute rigid shift and block control stay near 9, while green drops to ~2 | as above |
| Fig 4 C | Black at 10–15; shifted markers near 1 at 1 s, climbing to 9–12 at 1 minute | as above |
| Fig 5 A–C | A tall black spike at the left with a gray band, dropping to ~0 by 1 s; everything else flattened | correlogram · as Fig 1 G, with no linear-lag view anywhere for real data |
| Fig 5 D | A tangle: black runs off the top, dips to ~0.03 near 1 s, spikes to 0.15 at ~3 s, then slides from 0.08 to 0 with most coloured lines inside wide gray and green-hatched bands | correlogram · as above; hard to read |
| Fig 5 E | Black dives to −0.56 at 3–5 s then recovers; **light blue (J = 1.6 s) also dives**; the darker blues and purple stay positive | correlogram · as above |
| Fig 5 F | Black dives to −0.05 near 5 s; the blues sit at 0.03–0.06 | correlogram · as above; x label clipped |
| Fig 6 A | Four coloured solid lines falling from off the top to ~0.05 by 1 s, with noisy thin dashed twins; the lower half of the axis is empty | correlogram · as above |
| Fig 6 B | All groups dive to −0.4…−0.65 near 3 s, then jagged positive values | correlogram · as above |
| Fig 6 C | Teal (DI) near 0.11 out to a minute, about double three lines near 0.05; dashed lines scatter widely | correlogram · as above |
| Fig 6 D | Olive and teal near 0.12–0.15 above brown and pink; the olive dashed line runs off the top with no mark | correlogram · as above |

## Findings

All were checked against the page text and the rendered PNGs (verified = yes) unless marked otherwise.

| # | location | issue | severity | suggested fix | verified |
|---|---|---|---|---|---|
| 1 | The short answer | At least 6 undefined terms come before the definitions section: lab fast/slow stream, CoactDetect, benchmark generator, promiscuity probe, training contrast, rigid shift and its 1.6–20 s radius. A reader who stops after the summary is lost. | blocking | Move a 5-line glossary above the short answer, or gloss inline ("CoactDetect, the repository's event detector"; "a 5-minute rise in every ROI's rate that the generator plants"). | yes |
| 2 | "Why this page exists" box | Rigid shift, the label-free detector thread, baseline windows and milestone are undefined. A git branch name and `main` appear in reader-facing prose. | blocking | Gloss rigid shift in one clause. Move the branch provenance to Reproduce or a footnote. | yes |
| 3 | Figure 1 caption | Promiscuity probe, distractors, "depth" (depth of what?) and "generator's background" are undefined. G–H plot excess coincidence, which is only defined in the next section. | blocking | Define depth as the multiplier's swing (with a value) and background as "per-ROI rates with nothing shared"; drop or gloss distractors. Either move Figure 1 after "Two measurements" or add a one-line definition of excess coincidence to the caption. | yes |
| 4 | Fig 1 A–C | B (no events) shows tall isolated spikes that look like A's planted events. C shows no visible 5-minute drift. The panels don't show the difference they exist to show. | major | Bin at 1 minute, or plot the true shared multiplier in a lane above each trace. | yes |
| 5 | Fig 1 D | One row carries ~15 ticks across the minute. This horizontal line of marks reads as a second kind of structure. | minor | Say in the caption that it is one high-rate ROI, or choose another window. | yes |
| 6 | Fig 1 / Fig 3 labels vs prose | The figures say "shared drift, 5 minutes", "shared modulation, 20 s" and "benchmark generator, whole spec"; the prose says "5-minute world", "20 s world" and "whole spec". | minor | Use one name for each world in both places; replace "whole spec" with plain words. | yes |
| 7 | Every correlogram (Fig 1 G–H, 3 A–E, 5, 6) | **False friend.** A correlogram reader expects signed lag centred on 0 on a linear axis. Here the lag is unsigned and log-scaled, with the peak pinned at the left edge, so the event peak reads as a decay. The text never says the lag is unsigned, and only the synthetic Figure 1 has a linear view. The lab shoulder claims rest on Figure 5, which has none. | major | Define *ℓ* as unsigned (both orders of a pair pooled) and say so in the axis label. Add a linear-lag panel for the lab fast stream to Figure 5, as Figure 1 H does. | yes |
| 8 | Two ways ROIs are active together: "Each of these is drawn in Figure 2" | CoactDetect episodes and episode removal are not drawn anywhere, yet the lab claims rest on the arm that removes episodes. | major | Add a panel to Figure 2: a flagged episode in a lane above, with every onset inside it deleted, members and non-members alike. | yes |
| 9 | Two measurements | The count-variance ratio is described only in words. Its one picture (`one_recording.png`) is darkroom-only. | major | Add a synthetic panel: the 5-minute world's population count per minute beside one circular shift, with the two variances noted. | yes |
| 10 | Paragraph pointing to `one_recording.png` | `<darkroom>` and "FOUNDATIONS §5" are internal references that a public reader cannot use. | minor | Say "not published because it shows a single real recording" and move the path to Reproduce. | yes |
| 11 | Fig 3 F (and Fig 4) | Rigid shift at *J* = 20 s is drawn as a ▼, the shape the Figure 3 legend also uses for "curve above the view". No out-of-view marks exist in Figure 3, so that legend entry is unused and invites the misreading. | minor | Use another shape for rigid shift; drop the unused legend entry. | yes |
| 12 | Fig 3 and Fig 5 legends, y labels | "Circular shift (the null)": "the null" is never defined. "y to 0.9" is an awkward label idiom. | minor | Write "circular shift (independent ROIs)", matching Figure 4's axis; drop "y to" since the ticks already show the range. | yes |
| 13 | Bullets under Figures 4 and 5, fast-stream bullet | "A single circular shift scored against the reference is above 1 in 55 %": "the reference" is defined only in the collapsed block. That comparison is what makes the 67 % interpretable. | major | "A circular shift scored against the mean of 8 circular shifts exceeds 1 in 55 % of recordings, so 67 % is only modestly above chance." | yes |
| 14 | Bullets under Figures 4 and 5, effective-mice bullet | Effective mice, the two weightings and "expected onset pairs" are undefined. Together with row 13 this location is blocking. | blocking | One sentence: recordings with more onsets contribute more pairs, and the effective number is computed as (give the formula). | text yes; formula no (the code was not read) |
| 15 | Fig 6 legend and By group text | "Heaviest mouse" reads as body weight. | major | "The mouse contributing the most onset pairs." | yes |
| 16 | By group | DI, ORX and OVX are not expanded; all-caps MALE runs through the prose. | minor | Expand the abbreviations (diestrus, orchidectomized, ovariectomized) and say they are the export's labels verbatim. | yes |
| 17 | Short answer vs By group | The summary says "one group of mice carries most of it" without naming the group. The By group section opens "The pooled result is not one group's", which reads as a contradiction. | major | Name DI and use the same wording in both places ("largest in DI, about twice the other three, present in all"). | yes |
| 18 | What this changes, `count_excess` bullet | A code identifier appears in prose. "Baseline" here means a comparison detector, but earlier it was defined as the pre-treatment stretch. | major | "A simple comparison detector with no fitted parameters, which counts lit ROIs and subtracts their 30 s moving mean." | yes |
| 19 | What this changes | Training contrast, paired crops, fits and "the unmerged branch" (which one?) are undefined; tool path and commit hashes sit inline. | blocking | Define training contrast ("the recording-versus-surrogate pair a model learns to rank") and crop once. Move the tool and commit references to a footnote or Reproduce. | yes |
| 20 | What this changes, first bullet | "Excess" now means ratio − 1, not excess coincidence. "Faster than about 40 s" is unexplained (it is 2*J*). | minor | "The ratio's amount above 1"; add "(2*J* at *J* = 20 s)". | yes |
| 21 | Dip aside, dead-time bullet | "Per second of interval there are 15 …" gives no unit noun or pooling (intervals? per ROI?). A histogram is described in prose instead of shown. | minor | "15 intervals per second of interval width, pooled over ROIs", or draw a small histogram. | yes |
| 22 | Dip aside placement | The aside sits under By group, but it concerns Figure 5 panel E. | minor | Give it its own heading after the Figure 5 bullets. | yes |
| 23 | Slow-stream bullet: "rigid shift fills in" the dip | *J* is not named, and in Figure 5 E the *J* = 1.6 s curve dips to about −0.38. | minor | "Rigid shift at *J* = 10 and 20 s fills it in; at 1.6 s the dip remains." | yes (read from the render) |
| 24 | Short answer | "CoactDetect's events removed" vs "episodes" everywhere else. | minor | Use "episodes". | yes |
| 25 | Figure 5 caption | "Calibrated operating point" and "context window" are jargon. | minor | Gloss each in a few words. | yes |
| 26 | Fig 2 D | The block-edge ▼ floats in white space above the panel, so the reader has to carry 2m down across a gap. | minor | Tighten the gap. The no-drawing-on-the-raster rule rightly forbids a line. | yes |
| 27 | Fig 4 x axis | Categorical bin widths sit at log-spaced positions with markers spread sideways, so the offsets can read as different bin widths. | minor | Add group separators, or note "markers offset for legibility" in the caption. | yes |
| 28 | Two ways ROIs are active together | CA1 is undefined, and so is "local circular shift" in CoactDetect's definition. | minor | "Hippocampal area CA1"; "a circular shift inside a rolling window". | yes |

**Mechanical problems I saw but did not score (agent 10's job):**
- **Figure 1:** the A–C y labels print over the neighbouring panel's "20m" tick label.
- **Figure 5:** panel F's x label is cut off ("log sca").
- **Figure 6:** in panel D the MALE dashed curve leaves the top with no "curve above the view" mark, and in panel C the OVX dashed curve leaves the bottom unmarked.
- **Figure 5:** the legend doesn't say the green episode-removal arms are lab-only.

**Checked and clean:**
- No bare enumerated labels.
- Every symbol (*J*, *ℓ*, *T*, *w*, *α*) is defined before use, except *ℓ*'s sign (finding 7).
- Headings are in sentence case and there are no titles over the plots.
- Rigid shift, circular shift and the block control are illustrated rather than just named (Figure 2).
- "Data" is used as a plural throughout.
