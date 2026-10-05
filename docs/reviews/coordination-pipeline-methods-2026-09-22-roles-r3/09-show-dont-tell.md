# Role 9 — Show, Don't Tell (round 3, blind pass, verbatim as returned)

GRANT 9 ok — Read, Grep, Glob, Bash

(I also hold SubagentHandback, which is only the reporting channel. I hold no editing tool, and I made no edits.)

## Role 9: density and figure-first review. Round 3, blind pass, commit ee7bd62

**What I checked:** the source `docs\methods\coordination_pipeline_methods.md` read top to bottom; all 15 rendered Word pages (`...\scratchpad\methods_build_r2\coordination_pipeline_methods_docx_page01..15.png`); `docs\methods\figures\fig1_benchmark_recording.png` (1324×794 px); and `tools\make_methods_bench_figure.py`, for the figure's font sizes and plot conventions.

### Thresholds used
These are adapted to a manuscript methods section. They are my conventions, not researched optima.
- The slide limits (40 words per page, 60 words per block) do not apply to a methods section, so I did not use them.
- **Table candidate:** four or more parallel items that share four or more attributes and are written as prose.
- **Schematic candidate:** a structure or data flow scattered across three or more sections.
- **Block size:** a block over 150 words is looked at for structure. It is not flagged just for being prose.
- **Figure share:** measured on the rendered page against the text block, not a 50%-of-canvas rule. The target for a single-column manuscript figure is full text width.
- **Blank space:** more than 15% of a page's text block left empty.
- **Constant columns:** a table column or row that holds the same value everywhere.

### Count table
Words per page are estimated from source line ranges matched to the rendered page breaks. Tables inflate the counts, so take them as about ±15%. Page area is 8.5×11 in; the text block ends at about y = 1075 px of 1210.

| page | words | largest single block (words) | figure | figure share | blank text block |
|---|---|---|---|---|---|
| 1 | ~320 | dataset paragraph (~75); Table 1 | n | – | 0% |
| 2 | ~310 | floor-pinning bullet (~75) | n | – | **~22%** (Figure 1 pushed to p3) |
| 3 | ~310 | Planted events (124); Figure 1 caption (86) | **y** | 24% of page area; 685 of 720 px text width (95%), about 6.2 in | 0% |
| 4 | ~440 | Origin of the constants (171) | n | – | 0% |
| 5 | ~470 | rate+context bullet (134) | n | – | 0% |
| 6 | ~560 | SPIKE-synch bullet (176) | n | – | 0% |
| 7 | ~390 | default-setting paragraph (~75) | n | – | **~17%** (Table 3 kept with its caption) |
| 8 | ~400 | Table 3; coordinate-search step (~95) | n | – | 0% |
| 9 | ~250 | Table 4, part 1 | n | – | 0% |
| 10 | ~260 | Table 4, part 2 | n | – | 0% |
| 11 | ~450 | Training (113) | n | – | 0% |
| 12 | ~520 | Separability (147) | n | – | 0% |
| 13 | ~470 | width/amplitude and Limitations (~85 each) | n | – | 0% |
| 14–15 | ~475 | references | n | – | p15 is the end of the document |

The body is about 5,100 words before references. There is one figure and there are four tables. None of the six "methods" pages that describe the detectors (p5–7, p11) has a figure. For a methods section that is normal, so I do not flag it on its own.

### Findings
Columns: location · issue · severity · suggested fix · verifiable (yes/no).

1. **p5–7, the six coded-detector bullets (~800 words; the largest blocks are 176, 136, 134 and 117 words).**
   - **Issue:** six parallel descriptions share the same attributes: what is counted, window, null (form and surrogate count), threshold rule, merge, and whether the detector runs per window or on the whole recording. A reader comparing detectors has to rebuild that grid from prose. The "run on" attribute is stated separately on p12–13 ("rate+context, CoactDetect, SPIKE-synch … run separately inside each analysis window …").
   - **Severity:** moderate.
   - **Fix:** add a compact table, "Table: Coded detectors at a glance", with columns detector · statistic counted · window · null · threshold rule · run on. Fold the p12–13 run-scope sentences into its last column. Shrink each bullet to what the table cannot hold: provenance (Cossart/Mao lineage, the partial CICADA port, the Finn–Johnson resemblance, the Kreuz/Cecchini note) and the caveats (α is not a false-alarm rate; the pooled percentile is lenient). Those move within the section; none are cut. This should also shorten the section net, which fits the "as brief as possible" request.
   - **Verifiable:** yes.

2. **p5, p8, p11–12, seed and recording allocation scattered across four sections.**
   - **Issue:** the evaluation design is spread out:
     - selection on seeds 1–48 and held-out testing on 49–96, both at both backgrounds;
     - the no-coordination test on the shared seed, or the seed plus 100,000;
     - the close-events test on 12 seeds per background;
     - nested cross-validation on 1000–1047: 4 outer folds of 12 seeds, 72 tuning recordings, 10 training recordings plus 2 threshold recordings, and a refit on 5 seeds;
     - the replication on 2000–2047.

     This is a structure written as a sequence, and it is the part a reviewer will most want to audit.
   - **Severity:** moderate.
   - **Fix:** the cheaper option is a seed-allocation table: purpose · seeds · backgrounds · recordings · which detectors. The richer option is a small schematic (a Figure 2 panel) of the nested cross-validation: 4 outer folds, 3 tuning folds rotated for configuration choice, and the refit, with the 10 training and 2 threshold recordings drawn inside one fold. Either lets the prose on p11–12 lose its counts.
   - **Verifiable:** yes.

3. **p8, Table 3, the "close-events F1 fall" column.**
   - **Issue:** the column is 0.02 in all six rows. A constant column is not a table column. "Precision change" is 0.10 in four of six rows, which is fine to keep.
   - **Severity:** minor.
   - **Fix:** drop the column and state it in the caption: "The close-events limit is a fall of at most 0.02 in mean F1 for every detector …".
   - **Verifiable:** yes.

4. **p9–10, Table 4, the "detection mode" row.**
   - **Issue:** it repeats "threshold, peak | threshold" for five detectors, which is six rows carrying one fact.
   - **Severity:** minor.
   - **Fix:** remove the row and put it in the caption: "Detection mode (threshold or peak) was searched for every detector except locust; all use threshold." The caption already explains what "peak" adds.
   - **Verifiable:** yes.

5. **p9–10, Table 4, the detector column.**
   - **Issue:** the names break mid-word: "rate+contex/t", "CoactDetec/t", "SPIKE-/synch". Grid cells also wrap ("0–4 s; compact,/exposure", "whole recording, per/period"). The cause is the relative column widths that pandoc takes from the separator dashes (detector 15, parameter 35, grid 29, value 21).
   - **Severity:** minor. This overlaps role 10's geometry check; I file it here because it makes the table fail as a table.
   - **Fix:** widen the detector separator to about 20 dashes and shorten parameter to about 30.
   - **Verifiable:** yes.

6. **p4, Table 2, column widths.**
   - **Issue:** the header "benchmark" breaks as "benchm/ark", and two 95% intervals wrap ("0.0028–/0.0066", "0.0162–/0.0233"). The benchmark column's separator is 11 dashes against 27 for "constant".
   - **Severity:** minor.
   - **Fix:** widen the benchmark and 95%-interval separators, or shorten the constant column.
   - **Verifiable:** yes.

7. **p2 (~22% blank) and p7 (~17% blank).**
   - **Issue:** Figure 1 would not fit under the Synthetic recordings intro, and Table 3 is held with its caption. Each leaves a large empty band.
   - **Severity:** minor. In a submission manuscript the figures usually go after the references anyway.
   - **Fix:** for the submission build, place Figure 1 after the references with a call-out in the text. For this review build, let the Background paragraph flow ahead of the figure.
   - **Verifiable:** yes.

8. **Figure 1, what the figure can show.**
   - **Issue:** the figure earns its space. It carries the benchmark's structure (three levels, distractors, the elevated-rate block, near-regular spacing) that about 600 words of prose describe. It is sized correctly: 95% of text width, with ticks at about 8.6 pt per the tool's sizing note. But at a 45 min scale, the defining property (cells within about 1 s of one another) and the central design claim (distractors cannot be told from 6-cell planted events) cannot be seen. The caption itself says the 3-cell events are "barely visible".
   - **Severity:** minor. It is optional given the brevity request.
   - **Fix:** add a panel C with two narrow zooms (about ±5 s): one 10-cell planted event and one distractor, on the same raster style. The 0.36 s jitter and the indistinguishability would then be seen rather than asserted. Keep the lane-above and down-triangle conventions.
   - **Verifiable:** yes.

9. **Figure 1, panel letters.**
   - **Issue:** "A" and "B" are drawn as rotated y-axis labels, and B is fused into "B   cell (33 cells)" (`make_methods_bench_figure.py`, lines 72 and 79). Journal convention is upright bold panel letters at each panel's top-left, and a rotated "A" reads as an axis name.
   - **Severity:** minor.
   - **Fix:** set the y label of A to empty and the y label of B to "cell (33 cells)". Add upright bold letters at the top-left of each panel, as a Bokeh `Title` placed above or left, or as a `pn.pane.Markdown` label in the layout. This is not a plot title, so the no-titles-above-plots rule still holds.
   - **Verifiable:** yes.

10. **Figure 1, house conventions.**
    - **Checked against:**
      - down-pointing ▼ in a lane above the raster;
      - nothing drawn on the raster (the block is shaded in the lane only);
      - no titles above plots;
      - one x-axis on the bottom row;
      - 60-base ticks (0s/10m/…/40m) through `_time_axis_hook`;
      - counts carry units ("10 cells", "33 cells");
      - numbered caption.
    - **Result:** all conform. Distractors are separated by hollow fill plus grey, not by shape, so "shape is spoken for" is not breached.
    - **Severity:** no finding.
    - **Verifiable:** yes.

11. **p6–7, the implementation-verification paragraph (115 words) and p11, "In the code these are tube, line_length …".**
    - **Issue:** software-provenance detail (the MATLAB parity, cSPIKE agreement to 10⁻⁹, PySpike pull request 89, code identifiers) sits in the manuscript body even though the PI asked for maximal brevity.
    - **Severity:** minor.
    - **Fix:** relocate these, without deleting anything, to a "Code availability and software validation" subsection or a supplement, leaving one sentence in the body ("Ports were checked against the laboratory's MATLAB output and against cSPIKE; see Supplementary").
    - **Verifiable:** yes.

### Prose judged right as written (no figure or table owed)
- The exclusions list and the periods/windows list (p2).
- The Background, Planted events, Distractors and Elevated-rate block paragraphs. Their constants are already in Table 2 and their structure is in Figure 1.
- Scoring formulas (p7).
- Coordinate search (p8): a numbered procedure is the right form.
- Separability (p12): it is an argument with caveats.
- The width/amplitude rule (p13): three numbered steps are enough. A toy schematic would help only if the results depend on it.
- The learned-detector architectures: a schematic is warranted only if the Results compare architectures.
- Limitations.

**Files:**
- `docs\methods\coordination_pipeline_methods.md`
- `docs\methods\figures\fig1_benchmark_recording.png`
- `tools\make_methods_bench_figure.py`

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
