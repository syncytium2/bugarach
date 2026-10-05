# Role 8 — You Lost Me (round 3, blind pass, verbatim as returned)

GRANT 8 ok — Read, Grep, Glob

Role 8, "You Lost Me" (naive-reader accessibility). Round 3, final blind pass.

**What I checked:** the source `docs\methods\coordination_pipeline_methods.md` (549 lines, every line), all 15 rendered pages in `<scratchpad>\methods_build_r2\` (`coordination_pipeline_methods_docx_page01.png` to `_page15.png`), and `docs\methods\figures\fig1_benchmark_recording.png`. I read as a calcium-imaging neuroscientist who knows nothing about this project. Read-only; nothing was edited.

**Overall:** most of the document can be read cold. Almost every project term is bolded and defined where it first appears, and units are nearly complete. Two sections are blocking under the three-undefined-terms rule: Coded detectors (grid point, interior events, summed-coincidence identity) and the Table 4 half of Optimization (greatest-of, guard normalisation compact/exposure, threshold update step). One code-identifier violation is left in Learned detectors. Figure 1 can be read and agrees with its caption; the one problem is that it uses words the text defines only after it.

---

## Per-section verdicts

| # | Section (pages) | Terms / identifiers first used here | Defined on first use? | Cold reader follows? |
|---|---|---|---|---|
| 0 | Opening paragraph (p1) | coordinated event, detector, call, coded detectors, learned detectors | all defined | **yes** |
| 1 | Detected calcium events (p1–2) | imaging pipeline, ROI, t50rise, fast stream, slow stream, half prominence, TTX, senktide, SB222200, diestrus/orchidectomized/ovariectomized, whole-field brightness steps, floor pinning, NoRMCorre, pinned intervals, **screening cut**, "judged dead", periods, analysis windows, **High-K⁺ periods** | defined: ROI, t50rise, fast and slow stream, the drugs, NoRMCorre (cited), periods, windows. **Not defined:** screening cut; High-K⁺ (never introduced as a treatment); "the imaging pipeline" (definite article, never named or cited). Domain terms are fine for this reader. | **yes, with fixes** (2 undefined plus 1 dangling referent; one garden-path sentence; one internal contradiction) |
| 2 | Synthetic recordings (p2–5) | benchmark recording, benchmark seed, background rate, quiet, busy, participation level, nominal time, planted spacing, **margins**, distractors, elevated-rate block, coincidence clusters, **earlier archive / earlier export / earlier data**, **rate shape / burst shape** (Table 2), elevated-rate / no-coordination / close-events tests, **settings search**, crowding | most defined. Not defined: "margins" (made explicit only 2 paragraphs later), what distinguishes "archive" from "export" from "data", "burst shape" (the text calls these "multipliers"), "settings search" (forward reference to a later section). The baseline and senktide rates behind "6 times" and "1.6 times" are never stated. | **yes, with fixes** |
| 3 | Coded detectors (p5–7) | merge gap, binned mode, sliding mode, null, surrogates, context window, **tested window**, **grid point**, **guard** (used in the rate+context bullet, defined one bullet later), CFAR, z, α, LoCo, SCE, synchronous frames, CICADA, SPIKE-synchronization, coincidence profile, hysteresis, sustain level, maximum gap, cSPIKE, PySpike, **interior events**, **summed-coincidence identity**, "a recursion" | Not defined: grid point, interior events, summed-coincidence identity (3). "Tested window" is the same thing Table 4 calls "rate window". Guard is used before it is defined. CICADA is expanded only in the references. | **BLOCKING** (3 or more undefined) |
| 4 | Scoring (p7–8), Table 3 | call interval, match, false alarm, recall, precision, F1, objective, setting, default setting, admissible, precision change, close-events F1 fall, "evaluation" | all defined ("evaluation" is loose but survivable) | **yes** |
| 5 | Optimization of coded detectors (p8–10), including Table 4 | coordinate search, two-parameter grids, held out, gain, extension limit, bracketed optimum, **greatest-of**, **guard normalisation: compact, exposure**, **threshold update step**, threshold form, threshold scope, detection mode "peak", `recorded_data_detector_settings.csv` | prose is defined (the "gain" referent arrives one paragraph late). **Table 4 values that are never explained anywhere:** greatest-of, compact/exposure, threshold update step (3). LoCo's prose ("exact null percentile") never mentions an update step. | **BLOCKING** (Table 4 rows) |
| 6 | Learned detectors (p10–11) | configuration (used before it is defined in Training), binary raster, dilated convolutional head, difference-of-Gaussians, max-pooling, Deep Sets (cited), encoder channel, channel gain, crop, training seed, tuning recordings (forward), threshold recordings, **`tube`, `line_length`, `chorus_norm`, `chorus_gain_norm`** | mostly defined or cited. Standard ML terms are not glossed (dilated convolution, max-pooling). **Internal code identifiers appear in the prose.** No architecture illustration. | **yes, with fixes** (the code-identifier row must be fixed) |
| 7 | Comparison of coded and learned detectors (p11–12) | nested cross-validation, outer fold, tuning folds, **inner fits**, selection rules, false-alarm rule, **"its budget"**, replication, first/second draw, separable, corrected paired t, Nadeau–Bengio, **contrast** | Not defined: inner fits, contrast. The "its budget replaced them" referent is unclear. The ratio direction flips mid-paragraph (test-to-training 1/3, then "3" and "below 1" as training-to-test). | **yes, with fixes** |
| 8 | Analysis of recorded data (p12–13) | surrogate seed, upper-median, joint selection, rate (calls min⁻¹) | all defined; units given | **yes** |
| 9 | Width and amplitude (p13) | search span, centre, core group, width, amplitude (cells s⁻¹) | all defined, with units; says it is not the fluorescence amplitude | **yes** ("308 calls had zero width" has no denominator) |
| 10 | Limitations (p13) | none new | fine; "absolute in cells" is loose phrasing for a threshold in events s⁻¹ | **yes** |
| F1 | Figure 1 (p3) | participation level, distractor, elevated-rate block, quiet background, benchmark seed | used in the caption **before** the text defines them (except benchmark seed) | **yes** (see below) |

---

## Figure 1

**What it resembles:** a spike raster (panel B: time on x, one row per cell) under an event lane (panel A). **Is it a true raster?** Yes. Time is on x and cells are the rows, so it is not a false friend. The down-pointing triangles in the lane above follow the house convention.

**What a cold reader sees:**
- **Panel A:** four labelled rows of coloured down-triangles (green 30% / 10 cells, blue 18% / 6 cells, pink 10% / 3 cells, open grey distractors / 6 cells), with a tan shaded band from 20 to 25 min.
- **Panel B:** a black-tick raster of 33 cells over 45 min, with a dense band from 20 to 25 min. Faint vertical columns of ticks sit under the green and blue triangles, and the top few rows are much denser than the rest.

**Caption and figure agree.** Five triangles per level (30%: about 8.5, 13.3, 17.8, 31.5, 39.5 min; 18%: 2.3, 6.4, 15.7, 35.5, 42.7; 10%: 4.4, 11.3, 28.9, 33.5, 37.5). Six distractors, all between 2 and 16.6 min, which fits the 120–1,100 s rule. The shaded span is 20–25 min, matching the 1,200–1,500 s block. No planted triangle falls within 2 min of the band. The caption's claim that "the 3-cell events are barely visible" is true.

**Cold-reader snags:**
1. The caption uses "participation level", "distractors", "elevated-rate block" and "quiet background" before the text defines them. The figure sits between the one-line introduction and the paragraphs that explain it.
2. The rows in B are visibly sorted by rate (cells 30–32 are very busy), but nothing says so. A cold reader may think those cells are special or contaminated.

---

## Findings

Columns: location · issue · severity · suggested fix · verified against source (yes/no)

1. **Learned detectors, p11: "In the code these are `tube`, `line_length`, `chorus_norm` and `chorus_gain_norm`."** Internal code identifiers in audience-facing prose. They mean nothing to the reader, and the names suggest meanings they do not have. · **should-fix** · Move the mapping to a code-availability statement or supplementary table, or drop it. · yes

2. **Coded detectors, p5–7: blocking, three undefined terms.**
   - "A call must span more than one grid point after merging": the grid is never named (the rate's sampling grid? the frame?).
   - "no effect on interior events": interior of what?
   - "summed-coincidence identity": which identity?

   Also: "a recursion" in the Poisson-binomial check is unnamed. · **blocking** · Say "more than one frame (0.1 s)" if that is what grid point means. Gloss interior events ("events not at a train's first or last spike"). State the identity in a clause. · yes

3. **Table 4, p9–10: blocking, three undefined parameter values.** "null context: greatest-of, symmetric", "guard normalisation: compact, exposure", "threshold update step 15 s" appear nowhere in the prose. The LoCo bullet describes an exact null percentile with no update step. · **blocking** · Add one clause per term to the CoactDetect and LoCo bullets or to the Table 4 caption, e.g. "greatest-of: the larger of the two one-sided contexts", "threshold update step: the threshold is recomputed every 15 s". · yes

4. **Coded detectors, rate+context bullet, p5: two term problems.** "no guard" is used one bullet before the guard is defined in the CoactDetect bullet. "tested window" is the parameter Table 4 calls "rate window". · minor · Define the guard at first use, or move the definition up to the paragraph introducing the detectors. Use "rate window" in both places. · yes

5. **Detected calcium events, p1: "Rows without a time mark ROIs that had no events".** Garden-path sentence: "a time mark" parses as a noun. · minor · "Rows with no event time stand for ROIs that had no events (87 rows)." · yes

6. **Detected calcium events, p2: "Two recordings with pinning below the screening cut were kept."** "Screening cut" is undefined. · minor · Give the criterion (e.g. "below the screening threshold of N pinned frames"), or drop the term. · yes

7. **Detected calcium events, p2: "High-K⁺ periods, not analysed here".** High-K⁺ was never introduced among the treatments (only TTX, senktide and SB222200 are). · minor · Introduce it in the treatments paragraph, e.g. "some recordings end with a high-K⁺ period". · yes

8. **Detected calcium events, p1: an internal contradiction.** "Each recording has a baseline followed by one or more drug treatments" is contradicted six lines later by "5 had no treatment". · minor · "Each recording has a baseline, usually followed by one or more drug treatments." · yes

9. **Detected calcium events, p1: "the imaging pipeline" / "detected by the same method".** Definite reference to a pipeline and an event-detection method that are never named, cited or described. The reader cannot tell what produced the events. · minor · Name or cite the pipeline and say it is described elsewhere. · no (I have no source for which pipeline this is)

10. **Synthetic recordings, "Elevated-rate block", p4: "about 6 times the measured baseline rate and 1.6 times the senktide rate".** Neither rate is stated. 0.06 is about 12 times the quiet rate and about 3 times the busy rate, so the reader cannot recover which baseline is meant. · minor · Give both rates in events s⁻¹ per cell. · yes (the arithmetic against 0.0052 and 0.0190)

11. **Synthetic recordings, "Origin of the constants", Table 2 and the Close-events test, p4–5: "earlier data", "earlier archive", "earlier export", "the laboratory's archive" (p2).** Relative word with no referent: earlier than what, and is an archive the same thing as an export? "Export" is never defined as a noun. · minor · Define once: "an earlier export of the same pipeline (N recordings, date)" and "the laboratory's archive (85 recordings)", then use those names. · yes

12. **Table 2, p4: "rate shape" and "burst shape" rows.** The prose calls these the gamma shape of the mean rate and of the "multipliers"; the word "burst" never appears in the prose. The "cells 33 / 31.5" row says the cell count came from coincidence clusters, and it is not clear what cell count a cluster summary measures. · minor · Use the prose terms in the table ("rate shape", "300 s multiplier shape"). Say what the cells row measures (e.g. "median cells per recording"). · yes

13. **Synthetic recordings, "Planted events", p3: "fill the recording outside the elevated-rate block and its margins" and "Draws that overrun are rescaled".** "Margins" is quantified only two paragraphs later (120 s). "Overrun" has no stated referent. · minor · "…and a 120 s margin either side" and "draws that would overrun the recording end are rescaled". · yes

14. **Coded detectors, binned SCE bullet, p6: "is more lenient".** A comparative with no stated referent. · minor · "more lenient than Cossart et al.'s per-frame 5% criterion". · yes

15. **Coded detectors, p5: "Each also requires a minimum number of cells".** "Also" has no antecedent. · trivial · Drop "also". · yes

16. **Comparison, "Close-events test", p12: "on the inner fits".** Undefined. The nested cross-validation text never uses "inner". · minor · "on the fits to two of the three tuning folds (the inner fits)". · yes

17. **Comparison, coded-detectors bullet, p11: "No Table 3 limit was applied; under the false-alarm rule below, its budget replaced them."** The referent of "its" is unclear, and so is whether the F1-alone rule had any limit at all. · minor · "No Table 3 limit was applied. Under the second selection rule, its false-alarm budget took their place; under F1 alone there was no limit." · yes

18. **Comparison, "Separability", p12: the ratio direction flips.** "a test-to-training ratio of 1/3" is followed by "neither ratio here: 3 for the coded detectors … below 1 for a learned refit", which are training-to-test ratios. A cold reader loses which way the ratio runs. "Contrast" is also undefined. · minor · Say "training-to-test ratio" explicitly for both numbers. Define contrast as "each learned-versus-coded pair". · yes

19. **Learned detectors, p10–11: machine-learning jargon without gloss, and no picture.** "Dilated convolutional head", "max-pooling" and "encoder channel" are not glossed, and the four architectures are named-and-described with no illustration. · minor · Add a one-clause gloss for each term. Ideally add a small architecture schematic (Figure 2) under the illustrate-don't-name-drop rule. · yes

20. **Learned detectors, first sentence, p10: "configuration".** Used before the Training paragraph says what a configuration varies. · trivial · Add "(learning rate, training length and size; see Training)". · yes

21. **Figure 1 caption, p3: terms used before they are defined.** The caption uses participation level, distractors, elevated-rate block and "quiet" before the text defines them. · minor · Place the figure after the "Elevated-rate block" paragraph, or give each term a four-word gloss in the caption. · yes

22. **Figure 1, panel B, p3: row order not stated.** The rows appear sorted by event rate (cells 30–32 dense), and nothing says so. · minor · Add "rows ordered by event count" (or whatever the true order is) to the caption. · no (inferred from the render; I did not check the generator)

23. **Tone, throughout: detector names begin sentences in lowercase.** "binned SCE's interval is its bin" (p7), "binned SCE did not move" (p9), "locust is a partial…" (p6), "rate+context, CoactDetect…" (p12). This reads as typos to a cold reader. "LoCo" is never expanded or explained as a name. · minor · Rephrase so the name does not open a sentence ("The binned SCE detector…"). Expand LoCo if it is an acronym. · yes

24. **Table 4 caption, p9: `recorded_data_detector_settings.csv`.** An internal filename in the caption. · trivial · "(supplied as Supplementary File N)", or remove it. · yes

25. **Draft marker, title block, p1: "Draft for review, 2026-09-22. Fast event stream only."** A draft marker is present. Acceptable at review stage; it must come out of a submission copy. · minor, pre-submission · Remove it, or move "fast event stream only" into the first paragraph. · yes

26. **Width and amplitude, p13: "308 calls had zero width and 185 had a single cell".** No denominator, so a cold reader cannot tell whether this is rare or common. · minor · "308 of N calls". · yes (the number is absent from the source)

---

## Other checks
- **Rendering defects seen in passing (agent 10's area, noted only):**
  - Table 2 header wraps as "benchm / ark" (p4).
  - Table 4 detector column wraps as "rate+contex / t" and "CoactDetec / t" (p9).
- **Units:** complete for every rate, duration and count I checked (events s⁻¹ per cell, calls min⁻¹, calls h⁻¹, cells s⁻¹, frames with their 0.1 s conversion). No bare-count violations found.
- **Code identifiers in prose:** `findpeaks` is a public MATLAB function and acceptable. "t50rise" is a column name used as a term; it is defined and acceptable, though "half-rise time" would be plainer. The only real violations are findings 1 and 24.
- **Draft markers:** only the subtitle (finding 25). No TODO, TBD or ⚠ markers in the source.
- **Sentence case:** headings are consistent; no ALL-CAPS emphasis; lists are formatted as lists.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
