# Chapter 1 figures: the data, the tools and the theory

The first five figures were made for the first ~3,100 words of Chapter 1, which had no figure
(committee review, `docs/reviews/chapter-1-aim0-2026-10-29-round1-roles/`, roles 8 and 9). The participant
residuals, the joint fit against the correlogram tool and the mechanisms schematic answer the
round-2 review (`docs/reviews/chapter-1-aim0-2026-10-29-round2-roles/`), and the real-intervals and
assessor-jitter figures the round-3 review. One script, `ch1_new_figures.py`, draws all ten from the
repository's own code and run records. What changed in rounds 2 and 3, figure by figure, is in
[`round2_figure_changes.md`](round2_figure_changes.md). Run it from the repository root. `--only`
redraws a subset, and `--out DIR` writes somewhere else.

| file | what it shows | command |
|---|---|---|
| `synth_raster_plot_data-and-what-each-tool-sees_20261029.png` | one minute of a simulated 33-cell recording (one-ink raster), two coordinated events enlarged with their onset spread and σ, and what each tool counts | `PYTHONPATH=src python docs/dissertation/figures/ch1_new_figures.py --only data` |
| `synth_recovery_plot_window-sharing-and-participant-bias_20261029.png` | g₂ and g₃ for Gaussian and uniform jitter; participants reported ÷ planted against σ/w, with measured medians | `... ch1_new_figures.py --only sharing` |
| `synth_recovery_plot_chance-clusters-against-threshold_20261029.png` | predicted and measured chance clusters per minute against the assessor's threshold K | `... ch1_new_figures.py --only chance` |
| `synth_recovery_plot_order-power-against-event-count_20261029.png` | power to detect order against events per recording, for one or two latency templates and r = 1, 2.5, 5 (exact-size 5 % test) | `... ch1_new_figures.py --only order` |
| `synth_recovery_plot_realistic-values-against-tested-grid_20261029.png` | the tested jitter × participants grid, resolved or not by the joint fit on each of the two records, with realistic parameter values (fast stream and slow stream) | `... ch1_new_figures.py --only regime` |
| `synth_recovery_plot_participant-residuals-two-records_20261029.png` | participants (measured − predicted) ÷ planted per condition-window, ordered by σ/w, first experiment and held-out record, ±2 SE | `... ch1_new_figures.py --only residuals` |
| `synth_recovery_plot_joint-fit-against-correlogram_20261029.png` | recovered ÷ planted jitter, joint fit against the correlogram tool, both backgrounds; per-recording joint-fit jitter at realistic values | `... ch1_new_figures.py --only jointfit` |
| `synth_recovery_plot_surrogate-nulls-and-order-schematic_20261029.png` | schematic on toy values: the time-shift surrogate, the assembly test's two nulls, and the score sort and F | `... ch1_new_figures.py --only schematic` |
| `synth_recovery_plot_coordination-rates-on-real-intervals_20261029.png` | measured against predicted rate and participants on trains from the measured interval lists, hard-core and general form, at one event per mean interval and at the tabulated counts | `... ch1_new_figures.py --only intervals` |
| `synth_recovery_plot_assessor-jitter-reading-as-mixture_20261029.png` | the assessor's jitter reading against planted σ, measured and as a mixture of chance and event clusters | `... ch1_new_figures.py --only assessor` |

The power figure reads `docs/learned/synthetic_validation/ch1_followups/order_power.json` (its
randomized, exact 5 % rows). The figure that plotted the older power estimates against the number
of templates has been withdrawn.

File names come from `tools/naming/artifact_name.py build`, the copy of armory's naming tool
vendored into this repository, and pass `check`.

## Draft captions

Numbered as in the chapter after round 3 (1.2 data, 1.3 schematic, 1.4 parameter map, 1.5 window
sharing, 1.7 participant residuals, 1.8 joint fit, 1.9 chance clusters, 1.14 order power). The two
round-3 figures have no number yet and are headed by the section they were made for (§1.4.5 and
§1.5.2). The captions of the figures drawn elsewhere (1.1, 1.6, 1.10–1.13) live in the chapter.

**Figure 1.2. What one recording looks like, and what each tool counts.** A: one minute of a
simulated 45-minute recording of 33 cells, one mark per onset. The background is 0.0096 onsets per
second per cell, and there are two coordinated events of 10 cells each with onset jitter σ = 0.2 s.
Triangles above the raster mark the planted event times. B, C: each event enlarged. Each shows its
10 cells' onsets, then those onsets per 0.1 s frame against the Gaussian they were drawn from (σ is
its SD), then the coordination-rates tool's 1, 2 and 4 s windows with the number of the event's
onsets in each; a window's shade deepens with its share of the event's onsets, so event 1's 1 s
windows holding 4 and 6 onsets are a lighter and a darker orange. A 1 s window border splits event
1 into 4 and 6, while event 2 falls inside one window at every width. D–F: what each tool counts in
the same minute, colored by event, with alternate windows or bins shaded so their edges can be
seen. The coordination-rates tool counts onsets per window, the assessor counts distinct cells per
1 s bin, and the count detector counts distinct cells per 2 s bin; the threshold of 5 cells is set
for illustration. D shows the windows starting on whole multiples of the width; the tool also
counts on a grid offset by half a window and averages the two, which is not drawn. This minute was
picked from the recording because it shows one split event and one whole one. The onsets in it are
exactly as simulated.

**Figure 1.3. Three mechanisms the tests rest on, drawn on toy values.** All values are small,
synthetic and chosen for illustration; none comes from a run. A: the coordination-rates tool's
time-shift surrogate. "Recording": 60 s of four cells' onsets (one mark per onset), with background
onsets and two coordinated events of all four cells, whose planted times are marked in the lane
above. "Surrogate": each cell's train is shifted circularly by its own offset, drawn by the tool's
own function (`measure_coordination_rates.shifted`); offsets are distinct multiples of two windows,
so they span only about N·2w (here −6, −2, +2 and +6 s for a 2 s window, listed beside each cell).
Each cell keeps its own onsets and spacing, but the events no longer line up across cells. The 2 s
window marked in each lane holds 4 onsets in the recording and 1 in the surrogate. B: the assembly
test's two nulls, on a membership matrix of 6 cells by 4 events (filled tile = the cell joined the
event; row sums at right are each cell's event count, column sums below are each event's size). The
margin-preserving null swaps a checkerboard pair of tiles (orange), which keeps every row and column
sum. The uniform null draws each event's participants at random, which keeps the column sums only;
the row sums it changed are in orange. C: the score sort and F for 4 cells and 3 events (onset
orders 1, 2, 3, 4; 2, 1, 4; and 2, 4, 3). For each pair, the table gives who leads in each shared
event and the net, the first cell's leads minus the second's. A cell's net lead count, wins minus
losses over all its pairs, is +3, +5, −3 and −5, so the score sort orders the cells 2, 1, 3, 4. Of
the 6 + 3 + 3 = 12 pair co-participations, 10 agree with that order and 2 disagree, so
F = (10 − 2) ÷ 12 = 0.67. The numbers in C are computed with `order_limit.py`'s own functions.

**Figure 1.4. Realistic parameter values sit between the points the joint fit resolves.** Each circle
is a combination of planted jitter and cells per event, judged on two records: the first simulation
experiment and the held-out rerun on fresh seeds. On each record the point counts as resolved when
the joint fit's recovered ÷ planted jitter is within 0.8–1.25 in all four conditions (15 or 45
events, background 0.01 or 0.05 Hz), each the median of 5 recordings. A filled circle is resolved
on both records, an open one on neither, and a circle with its left half filled on the first
experiment only; no point is resolved on the held-out record only. The two lines of numbers under
each circle give the range of the four ratios, first experiment above and held-out record below.
Two points are resolved on the first experiment only: 10 cells at 0.2 s (held-out 0.98–1.36) and 5
cells at 0.5 s (held-out 0.66–1.55). On both records only the 20-cell row is resolved from 0.2 s
up. The orange and violet boxes mark realistic parameter values for the fast stream and the slow
stream: jitter 0.105 s with 7 cells per event (0.20 of 33), and 0.131 s with 13 cells (0.38 of 33).
The box sizes are nominal. Beside each box is the share of 40 recordings simulated at those values,
with the tabulated event counts, whose per-recording jitter falls within 0.8–1.25 under the general
form (Figure 1.8 C): 2 of 40 for the fast stream and 16 of 40 for the slow stream.

**Figure 1.5. Window sharing, and the undercount of participants it causes.** A: the chance that
one window holds all the onsets of an event, for two onsets (g₂) and three (g₃), against window
width over jitter standard deviation (SD). Solid lines are Gaussian jitter; dashed lines are uniform
jitter of the same SD, computed by numerical integration and checked by simulation. B: participants
reported over planted (k̂/k) against jitter over window, from k̂ = 2 + (k − 2) g₃/g₂, for 5, 10 and
20 cells per event (light to dark blue). Points are medians from the first simulation experiment
(10 recordings each, background 0.01 Hz). Yellow dashes are the full prediction, which adds the
term for at most one event per window and accounts for the points that sit below the lines at the
4 s window. The dotted line at k̂/k = 1 marks no bias. With 10-cell events, the reported count falls
below 0.9 of planted once the jitter passes about a sixth of the window, and to 0.45 when the
jitter equals the window.

**Figure 1.7. The participant prediction is close, with a small excess on both records.** Each point
is one condition-window with events of 10 or 20 cells (15 or 45 events; 1, 2 or 4 s window): the
coordination-rates tool's reported participants minus the full prediction, divided by planted
participants. The x-axis is categorical: condition-windows are grouped by jitter SD over window
(σ/w), in increasing order, and gray vertical lines divide the groups; the tick under each group
gives its σ/w. Within a group, points are dodged by record: blue for the first simulation
experiment, orange for the held-out rerun on fresh seeds. Circles are 10-cell and squares 20-cell
events; filled markers are 45 events and open markers 15. Whiskers are ±2 standard errors (SE) of
the median of 5 recordings, 1.2533 × SD ÷ √5, the convention `theory.py` uses. A: background
0.01 Hz per cell; B: 0.05 Hz. The y-axes differ between panels. Above each panel are the counts
beyond 2 SE (about 5.7 of 48 are expected if the prediction is exact) and the median signed
residual. They also give the number of conditions, of 16, in which measured lies below predicted,
with a two-sided sign test, counting one sign per condition because the three windows reuse the
same recordings. At 0.01 Hz, measured lies below predicted in 24 of 32 conditions across the two
records (p = 0.007), a median shortfall of about 0.01 of planted. On the held-out record, 17 of 48
condition-windows lie beyond 2 SE.

**Figure 1.8. The joint fit against the correlogram tool, and at realistic values.** A, B:
recovered ÷ planted jitter against planted jitter, for events of 10 or 20 cells on the 240
first-experiment recordings (20 recordings per point), at backgrounds of 0.01 Hz (A) and 0.05 Hz
(B) per cell. Gray squares are the correlogram tool as shipped (its own calibration) and violet
circles the joint fit (hard-core form). Markers are medians and bars interquartile ranges. Gray
text counts recordings whose correlogram width fell above or below the calibration curve; these
have no estimate and are left out of the median and range, which are therefore censored where the
count is large. Violet text counts joint fits at the jitter bound (within 2 % of 0.005 or 5 s).
The shaded band is 0.8–1.25 of planted and the dotted line equality. C: the joint fit per
recording at the realistic values, background 0.0096 Hz per cell, 40 recordings per strip, for
the fast stream (σ 0.105 s) and slow stream (σ 0.131 s), with 7 or 13 cells per event. Events
follow the measured interval lists, thinned to the tabulated counts of 9.7 and 22.0 per hour (7.3
and 16.5 per recording on average; `ch1_followups/realistic_counts.json`). Violet is the hard-core
form and green the general form given the true train. Bars are medians, and fits at the lower
bound sit at 0.005 s ÷ σ. Above each strip: recordings in band (within 0.8–1.25) · at the bound.
In band: fast stream, 4 and 2 of 40 for 7 cells and 8 and 8 for 13 cells (hard-core, general);
slow stream, 17 and 18 for 7 cells and 16 and 16 for 13 cells.

**Figure 1.9. How many clusters chance alone gives the assessor at each threshold.** Lines show the
predicted rate of chance clusters per minute against the threshold K, for 33 cells at three
background rates. Each line is labeled at its end with the first K whose predicted rate is at most
one chance cluster per hour (dashed), found by `bugarach.event_floor.floor_of` at the estate's
`FA_PER_HOUR` (1), and the rate at that K. Filled points were measured on 100 background-only
recordings of 45 minutes per background, with exact Poisson 95 % intervals, which are smaller than
the markers. At K = 6 and 0.01 Hz no cluster occurred, so the triangle marks the 95 % upper bound.
Only K = 3, 4 and 6 were simulated; the shaded thresholds are predictions only. The 0.01 and
0.0096 Hz lines stop at K = 8, where they leave the axis. They lie on top of each other at this
scale, yet their first K under one per hour differs: 0.0096 Hz sits on the budget line at K = 4
(0.98 chance clusters per hour) and 0.01 Hz just above it, so K = 5 is the safe choice at both. At
0.05 Hz the first K under one per hour is 8, so one fixed threshold cannot serve both
backgrounds.

**Figure 1.14. An order test needs several events, and two templates need more than five.** The
y-axis is power to detect order: the share of 300 simulated recordings in which the order indicator
rejects an exact-size 5 % test. The test is calibrated on 3,000 order-free recordings of the same
size and randomized at its threshold. Power is plotted against events per recording (1, 2, 3, 5),
for 7 (A) and 13 (B) of 33 cells per event, with onset jitter σ = 0.2 s. Lines are for a template's
latency spread δ of 1, 2.5 or 5 times the onset jitter (r = δ/σ); solid lines with filled circles
are one template and dashed lines with open squares are two. The dash-dot line is power 0.8 and the
dotted line the test size, both labeled in B. With one event no test has power, because the
indicator is 1 with or without order. One template reaches power 0.8 at 3 events of 13 cells when
r is 2.5 or more, but at 5 events of 7 cells only when r = 5. Two templates stay below 0.8
everywhere up to 5 events.

**Figure for §1.4.5. The coordination-rates tool on event trains built from measured intervals.**
Measured against predicted event rate (A, C) and participants (B, D), as ratios to planted, on
event trains whose intervals are resampled from the measured interval lists of the fast stream
(σ 0.105 s, circles) and the slow stream (σ 0.131 s, squares), with 7 (small) or 13 (large) of 33
cells per event, background 0.0096 Hz per cell, 45-minute recordings, 40 recordings per stream and
cell count. Color is the window (1, 2, 4 s). Each measurement (solve() on the pooled f₂, f₃) is
drawn twice at the same height: open at its hard-core-form prediction and filled at its
general-form prediction, joined by a thin line; the vertical bar is ±1 bootstrap SE of the
measurement. A, B: one event per mean interval (25.5 and 53.6 events per recording;
`separation/real_intervals/intervals_results.json`). C, D: thinned to the tabulated counts, 7.3 and
16.5 events per recording (`ch1_followups/realistic_counts.json`). The count under each x-axis is
how many of the six slow-stream measurements lie on one side of the general form. At the tabulated
counts, all six slow-stream rates lie above it and all six participant counts below it. At the 4 s window the
hard-core form misses the fast-stream rate by up to 0.17 of planted, and the general form brings
it close to the identity line.

**Figure for §1.5.2. The assessor's jitter reading is a mixture of chance and event clusters.**
The assessor's jitter reading (the median, over all its clusters, of each cluster's onset SD)
against planted jitter, at background 0.01 Hz per cell with K = 4 cells (A) and 0.05 Hz with K = 3
(B), 4 (C) and 6 (D). Orange points: measured, the median over the 20 first-experiment recordings
with events of 10 or 20 cells (bars: quartiles). Violet line: the mixture prediction, in which a
share c/(c + e) of clusters are chance clusters (c chance clusters per minute from the predicted
rate, e = E/45 events per minute) with the spread of chance clusters measured on background-only
recordings, and the rest are event clusters. Blue dotted line: event clusters only, the SD of an
event's onsets under a Gaussian truncated at the ±1.5 s gather, plus background onsets the gather
catches; it levels off near 0.74 s. Dashed line: chance clusters only, the reading on
background-only recordings. Dotted gray line: reading = planted. The chance share printed in each
panel is the range over 45 and 15 events per recording. Where chance clusters are few (A), the
reading follows the event-only curve up to its ceiling; where they are most clusters (B, C), it
sits on the chance-only level whatever was planted; at K = 6 (D) it lies between. The curves are
computed with `ch1_followups/assessor_jitter.py`'s own functions on a fine jitter grid, from the
record `assessor_jitter.json`.
