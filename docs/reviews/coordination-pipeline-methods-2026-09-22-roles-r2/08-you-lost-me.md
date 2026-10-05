# Role 8 — You Lost Me (round 2, blind pass, verbatim as returned)

GRANT 8 ok — Read, Grep, Glob

(SubagentHandback is the report channel, not an editing tool. I hold no Edit, Write or NotebookEdit.)

Role 8, "You Lost Me", blind pass on round 2.

**What I read:** the source at `docs\methods\coordination_pipeline_methods.md` (all 442 lines); the rendered pages 01, 02, 03 (the page with Figure 1), 04, 05, 07 and 09 from `...\scratchpad\methods_build_r1\`; and `docs\methods\figures\fig1_benchmark_recording.png` at full resolution. I did not open pages 06, 08, 10, 11 or 12, so I read that text from the source only.

**Reader:** a neuroscientist who knows calcium imaging and nothing about this project.

**Overall:** two blocking problems.
1. The binned and sliding modes of CoactDetect and LoCo are used throughout the paper and never defined.
2. Treatments and several exclusion terms are used about 8 pages before they are defined.

The rest is fixable locally, mostly with forward pointers and a few definitions.

## Per-section verdict

| # | Section | Terms and identifiers first used here | Defined where first used? | Cold reader follows? |
|---|---|---|---|---|
| 0 | Title, subtitle, opening paragraph | coordinated event, detector, call, coded or learned detector; "fast event stream" in the subtitle | All defined except "fast event stream" (defined one section later) | yes |
| 1 | Detected calcium events (including Table 1, exclusions, periods) | ROI, t50rise, export folder, imaging pipeline, fast and slow stream, half prominence, `findpeaks`, DI/MALE/ORX/OVX, **TTX, senktide, "first treatment"** (Table 1 caption), **confirmed steps, inspected windows, screening cut, "judged dead"**, trailing treatment periods, periods, analysis window | ROI, t50rise, streams, groups, periods and windows: yes. TTX, senktide and first treatment: no, they are defined 8 pages later. Screening cut, dead, inspected windows, confirmed and export folder: never defined | **blocking** (6 or more undefined) |
| 2 | Synthetic recordings (Figure 1, background, planted events, distractors, block, widths, constants, Table 2, test recordings) | benchmark recording or seed, background rate, quiet or busy, **participation level** (in the caption, before its paragraph), gamma shape, **"burst shape"** (Table 2 only), jitter, nominal spacing, distractor, **"negatives", precision, F1** (defined in Scoring), elevated-rate block, coincidence cluster, **"earlier data" or "earlier export"**, **CoactDetect** (defined in the next section), crowding, **"merges calls"**, false alarm | Most are defined. Forward references without a pointer: participation level (in the caption), precision, F1, CoactDetect, merge. Never defined: "earlier export" (earlier than what?) and "burst shape" | **blocking** (5 or more undefined at first use; the fix is cheap) |
| 3 | Coded detectors | merge gap, surrogate null, population event rate, context, guard, α and z, percentile, SCE, surrogate, synchronous frames (implied), minimum distance, coincidence threshold, sustain level, maximum gap, window cap, **binned mode and sliding mode**, **minimum cells**, **cSPIKE** | Mostly yes. **Binned and sliding modes: never defined anywhere.** Minimum cells: never defined. cSPIKE: no definition and no reference. LoCo and CoactDetect: names never expanded | **blocking** (modes, minimum cells, cSPIKE) |
| 4 | Scoring (including Table 3) | interval, nominal time, one-to-one matching, **"planted spacing"**, **"evaluation"**, recall, precision, F1, objective, setting, admissible, default setting, **"published with each implementation"**, a dated retune | Mostly yes. "Planted spacing" is ambiguous (120 s minimum or 133 s mean). "Evaluation" and "published" are undefined | yes, with fixes |
| 5 | Optimization of coded detectors (including Table 4) | coordinate search, grid, rounds, context rule, two-parameter grid, **synchronous frames**, **"declares"**, held out, bracketed optimum, **"sliding mode at the default values" and "binned defaults"** | Synchronous frames and the modes are undefined. "Declares" is software vocabulary. The parameter grids are never given | no, while the modes stay undefined |
| 6 | Learned detectors | binary raster, positive or negative frame, difference of Gaussians, Deep Sets, standardised, **`tube`, `line_length`, `chorus_norm`, `chorus_gain_norm`**, Adam, weighted binary cross-entropy (BCE), crop, fit, **"fitting pool"**, training seed, threshold recordings | Yes, except "fitting pool" (which seeds?). There are **four code identifiers in the prose** | yes, with fixes |
| 7 | Comparison of coded and learned detectors | nested cross-validation, outer, inner and tuning folds, **"the context rule"**, **"detection mode"**, configuration, refit, **two selection rules**, **"the replication" and "both draws"** (used before the Replication paragraph), "32 cases", separable, Nadeau–Bengio correction | Mostly yes. The context rule is a back-reference with no name. Detection mode inherits the mode gap. The replication is a forward reference. "32" is never broken down | yes, with fixes |
| 8 | Analysis of recorded data | surrogate seed, "shared by both streams", "for its fold", TTX and senktide (defined here, too late), **SB222200** | SB222200: never defined. "Both streams" points to a slow stream the paper excludes | yes, with fixes |
| 9 | Width and amplitude of coordinated events | call centre, group, width, **amplitude (cells s⁻¹)**, **"window"** (meaning the 1 s window) | Yes. But "amplitude" and "window" both collide with terms already defined for something else | yes, with fixes |
| — | References | — | — | n/a |

## Figure 1, read cold

**What it resembles:** a spike raster (time on x, one row per cell) with an event-marker lane above it. **It is a real raster**, and the axes mean what the idiom says. There is no false friend.

What a cold reader sees in each part:
- **Top lane:** coloured down-triangles in three rows labelled 30%, 18% and 10%, one row of open triangles labelled "distractor", and a tan block at about 20–25 min.
- **Bottom panel:** sparse black ticks for 33 cells. A dense vertical band sits under the tan block. Faint vertical columns of ticks line up under some triangles. Cells 30–32 are very busy in the first 7 min.

Caption against figure:
- Agrees on levels, distractors and the shaded block.
- Five triangles per level; 6 distractors between 2 and 17 min, inside the 120–1,100 s the text gives.
- Block at 20–25 min = 1,200–1,500 s, as the text says.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source? |
|---|---|---|---|---|---|
| 1 | Coded detectors: the paragraph after the list; Optimization; Table 3 caption; Table 4; Comparison ("detection mode") | "Binned mode" and "sliding mode" of CoactDetect and LoCo are **never defined**. The detector bullets describe "a 2 s window" and "a 1 s window" without saying which mode. The optimization result ("gains over sliding mode at the default values", "gained over the binned defaults") cannot be read without the definition | **blocking** | Add one sentence to each of the CoactDetect and LoCo bullets: binned = non-overlapping windows; sliding = a window stepped every frame (or whatever the implementation does) | yes |
| 2 | Section 1: Table 1 caption and column heads | TTX, senktide and "first treatment" are used here and defined only in *Analysis of recorded data*. At this point the reader does not know that recordings contain a sequence of treatments | **blocking** (part of the section 1 row) | Define TTX and senktide at first use. Add one sentence in *Periods and analysis windows*: "each recording has a baseline followed by one or more drug treatments" | yes |
| 3 | Section 1, exclusions | "confirmed steps" (confirmed by whom, and how?), "8 inspected windows" (collides with *analysis window*, defined 10 lines later), "screening cut" (a cut on what quantity?), "judged dead" (criterion?), "export folder" (project-internal term) | **blocking** (with finding 2, this section introduces 3 or more undefined terms) | Give the criterion in a clause for each. Rename "windows" to "intervals". Replace "export folder" with "exported event tables" | yes |
| 4 | Section 1, floor pinning | "8 ROIs in 4 recordings … 56 fast events … in 3 recordings": a cold reader cannot tell why 4 became 3 | major | Add the reason, for example "(the fourth recording's windows held no fast events)", if that is the reason | yes (the text); the cause is not verifiable |
| 5 | Figure 1 caption | "participation level" is used before its defining paragraph, which comes after the figure | minor | "one row per participation level (the fraction of the 33 cells in the event; see *Planted events*)" | yes |
| 6 | Figure 1 caption | "nothing is drawn on it" reads as an internal house rule, not a description. A stranger asks "why say that?" | minor | "no detections are overlaid on the raster" | yes |
| 7 | Figure 1 caption | The caption never says that a triangle marks the time of a planted event, or that the event shows in the raster as a vertical column of ticks under the triangle. The reader has to discover the correspondence. 10% events (3 cells) are nearly invisible in the raster, and the caption does not say that this is expected | major | Add: "Each triangle marks the time of a planted event; its cells appear below as a vertical column of ticks. 10% events (3 cells) are barely visible against the background." | yes (render) |
| 8 | Figure 1 against the text | The figure's time axis is in minutes (0s … 40m) while every time in the text is in seconds (2,700 s; 1,200–1,500 s; 120–1,100 s). The reader must convert to check the figure against the text | minor | Add "(45 min)" after "2,700 s" and give the block as "1,200–1,500 s (20–25 min)". The minutes axis follows house style, so leave it | yes |
| 9 | Figure 1 raster y-axis | "cells · 33" is a separator construction; the rows are numbered 0–32. The strip across the top of the figure also smuggles a list into a title with "·" separators | minor | Label the y-axis "cell (33 cells)". The figure's colour key already exists, so drop the list from the caption strip or format it as a key | yes (render) |
| 10 | Synthetic recordings, *Distractors* | "labelled as negatives", "precision 15/21" and "F1 0.83" are used before *Scoring* defines them | minor | Add "(see *Scoring*)", or state here that precision = matched calls / calls | yes |
| 11 | Synthetic recordings, *Origin of the constants* and Table 2 | "earlier data" and "earlier export" are relative words with no referent. Earlier than what, and which recordings? Table 2's "81 baseline windows" and "85 baseline windows" sit beside a dataset of 84 recordings with no explanation | major | Name the earlier export (its date or size) once, and say that 81 and 85 are its window counts | yes |
| 12 | Table 2 | "burst shape" appears only in the table. The text calls these "gamma-distributed multipliers … (shape …)" | minor | Use one name in both places, for example "rate-modulation shape, 300 s bins" | yes |
| 13 | Test recordings, *Close-events test* | "CoactDetect" and "merges calls" are used before *Coded detectors* | minor | Add "(a coded detector, described below)" | yes |
| 14 | Coded detectors | "minimum cells" is a parameter in Table 4 and in the searches, but no detector description mentions it | major | Add to the section intro: "Every count-based detector also requires at least a minimum number of cells per call (minimum cells)" | yes |
| 15 | Coded detectors, last paragraph | "cSPIKE" has no definition and no reference, although PySpike has both | minor | Say it is the MATLAB/C++ SPIKE toolbox by Kreuz and colleagues and cite it | yes |
| 16 | Coded detectors | The names "LoCo" and "CoactDetect" are never expanded. "synchronous frames" (the locust parameter in Optimization and Table 4) is never tied to the description "a window of consecutive frames" | minor | Expand the names if they are acronyms. In the locust bullet, write "a window of consecutive frames (synchronous frames)" | yes |
| 17 | Coded detectors, sentences opening "rate+context, binned SCE …" and Scoring's "binned SCE's interval" | Lowercase detector names at sentence start read as typos | minor | Rephrase so a sentence does not open with a lowercase name ("The rate+context, …") | yes |
| 18 | Coded detectors (mechanism) | The circular-shift null (shift each cell's events within a context, with a guard removed) is the core mechanism of three detectors and is only named, not illustrated | minor | Optional: a small schematic panel (Figure 2) showing the window, the context, the guard and one shifted train | yes |
| 19 | Scoring | "planted spacing" is ambiguous: 120 s is the minimum and 133 s the mean. "evaluation" is undefined. "published with each implementation, after a 2026-09-16 retune" gives an internal date as content, and "published" has no referent | minor | "wider than the 120 s minimum planted spacing"; "the recordings of an evaluation (for example, seeds 49–96)"; "the default setting distributed with the software, retuned once on this benchmark" | yes |
| 20 | Optimization | "Only the parameters each detector declares were searched" uses software vocabulary. The parameter grids are never stated, so "an edge" and "extended" have no referent | minor | "Only each detector's tunable parameters were searched". List the grids in a supplementary table, or say where they are | yes |
| 21 | Learned detectors, *Architectures* | Internal code identifiers leak into the prose: `tube`, `line_length`, `chorus_norm`, `chorus_gain_norm` (visible on rendered page 9) | major | Remove them from the prose. If a mapping is needed for code availability, put it in a data/code availability note | yes |
| 22 | Learned detectors, *Training* | "a fitting pool" has no referent: which seeds, and how many? | minor | Name the pool (for example, "seeds 1–48", or "the tuning folds" in the comparison) | yes |
| 23 | Comparison, *Coded detectors* bullet | "the context rule was kept" points back to a sentence three sections up that has no name | minor | "and contexts longer than 120 s were still refused" | yes |
| 24 | Comparison, *Merge gap* | "16 of 48 in the replication" and "both draws" come before the *Replication* paragraph. "26 of 32 cases" is never broken down | minor | Move *Replication* above *Merge gap*, and write "32 cases (4 learned detectors × 4 folds × 2 rules)" | yes |
| 25 | Analysis of recorded data | "SB222200" is never defined. "one sequence shared by both streams" refers to the slow stream, which the paper excludes, so the reader wonders whether it matters. "For its fold" names no fold | minor | "SB222200 (a neurokinin-3 receptor antagonist)", if that is its role. Drop "shared by both streams" or add "so results do not depend on which stream is run first". Name the fold | yes (text); SB222200's pharmacology not checked against the lab's usage |
| 26 | Width and amplitude | "amplitude" is redefined as cells s⁻¹ after the paper has used fluorescence amplitude. The disclaimer helps, but the word will be misread in the Results. "the window holds no events" means the 1 s window around the call centre, which collides with *analysis window* | major | Rename it: "recruitment rate" or "cell rate". Write "the 1 s neighbourhood holds no events" | yes |
| 27 | Subtitle | Draft marker: "Draft for review, 2026-09-22". Also "fast event stream" appears before its definition | minor (a draft marker must go before submission) | Remove it before submission. Keep "fast event stream only" in the first paragraph of Methods, where it is defined | yes |

**Not found:** TODO or XXX markers, bracketed placeholders, ALL-CAPS emphasis, inconsistent heading case, bare units (calls min⁻¹, calls h⁻¹ and events s⁻¹ per cell are all stated), or a false-friend chart.

**Boundaries:** mechanical figure legibility belongs to agent 10. On the rendered page, Figure 1's tick labels look about 6 pt at 6.5 in wide, which is worth their check. The title strip above the plot, which house style disallows, is also agent 10's. Whether the missing parameter grids or a parameter count are adequate for reproducibility is agent 4's. I did not check them.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
