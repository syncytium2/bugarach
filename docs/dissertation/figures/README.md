# Chapter 1 figures: the data, the tools and the theory

These five figures were made for the first ~3,100 words of Chapter 1, which had no figure
(committee review, `docs/reviews/chapter-1-aim0_2026-10-29-roles/`, roles 8 and 9). One script,
`ch1_new_figures.py`, draws all five from the repository's own code and run records. Run it from
the repository root. `--only` redraws a subset, and `--out DIR` writes somewhere else.

| file | what it shows | command |
|---|---|---|
| `synth_raster_plot_data-and-what-each-tool-sees_20261029.png` | one minute of a simulated 33-cell recording (one-ink raster), two coordinated events enlarged with their onset spread and σ, and what each tool counts | `PYTHONPATH=src python docs/dissertation/figures/ch1_new_figures.py --only data` |
| `synth_recovery_plot_window-sharing-and-participant-bias_20261029.png` | g₂ and g₃ for Gaussian and uniform jitter; participants reported ÷ planted against σ/w, with measured medians | `... ch1_new_figures.py --only sharing` |
| `synth_recovery_plot_chance-clusters-against-threshold_20261029.png` | predicted and measured chance clusters per minute against the assessor's threshold K | `... ch1_new_figures.py --only chance` |
| `synth_recovery_plot_order-power-against-event-count_20261029.png` | power to detect order against events per recording, for one or two latency templates and r = 1, 2.5, 5 (exact-size 5 % test) | `... ch1_new_figures.py --only order` |
| `synth_recovery_plot_realistic-values-against-tested-grid_20261029.png` | the tested jitter × participants grid, resolved or not by the joint fit, with realistic parameter values (the fast and slow bench levels) | `... ch1_new_figures.py --only regime` |

The power figure reads `docs/learned/synthetic_validation/ch1_followups/order_power.json` (its
randomized, exact 5 % rows). The figure that plotted the older power estimates against the number
of templates has been withdrawn.

File names come from `tools/naming/artifact_name.py build`, the copy of armory's naming tool
vendored into this repository, and pass `check`.

## Draft captions

The numbers below assume the figures go in where their sections are: the data figure in 1.2,
window sharing in 1.3, chance clusters in 1.4, order power in 1.6.2 and the parameter map in 1.10.
The six existing figures are renumbered around them. Change the numbers if the placement changes.

**Figure 1.1. What one recording looks like, and what each tool counts.** A: one minute of a
simulated 45-minute recording of 33 cells, one mark per onset. The background is 0.0096 onsets per
second per cell, and there are two coordinated events of 10 cells each with onset jitter σ = 0.2 s.
Triangles above the raster mark the planted event times. B, C: each event enlarged. Each shows its
10 cells' onsets, then those onsets per 0.1 s frame against the Gaussian they were drawn from (σ is
its SD), then the coordination-rates tool's 1, 2 and 4 s windows with the number of the event's
onsets in each. A 1 s window border splits event 1 into 4 and 6, while event 2 falls inside one
window at every width. D–F: what each tool counts in the same minute, colored by event. The
coordination-rates tool counts onsets per window, the assessor counts distinct cells per 1 s bin,
and the count detector counts distinct cells per 2 s bin; the threshold of 5 cells is set for
illustration. This minute was picked from the recording because it shows one split event and one
whole one. The onsets in it are exactly as simulated.

**Figure 1.2. Window sharing, and the undercount of participants it causes.** A: the chance that
one window holds all the onsets of an event, for two onsets (g₂) and three (g₃), against window
width over jitter standard deviation (SD). Solid lines are Gaussian jitter; dashed lines are uniform
jitter of the same SD, computed by numerical integration and checked by simulation. B: participants
reported over planted (k̂/k) against jitter over window, from k̂ = 2 + (k − 2) g₃/g₂, for 5, 10 and
20 cells per event. Points are medians from the first simulation experiment (10 recordings each,
background 0.01 Hz). Yellow dashes are the full prediction, which adds the term for at most one
event per window and accounts for the points that sit below the lines at the 4 s window. With
10-cell events, the reported count falls below 0.9 of planted once the jitter passes about a sixth
of the window, and to 0.45 when the jitter equals the window.

**Figure 1.3. How many clusters chance alone gives the assessor at each threshold.** Lines show the
predicted rate of chance clusters against the threshold K, for 33 cells at three background rates.
Points were measured on 100 background-only recordings of 45 minutes per background, with exact
Poisson 95 % intervals. At K = 6 and 0.01 Hz no cluster occurred, so the triangle marks the upper
bound. Only K = 3, 4 and 6 were simulated, and the shaded thresholds are predictions only. The
budget is one chance cluster per hour (dashed). The smallest threshold that stays under it is 5
cells at 0.01 Hz and 8 at 0.05 Hz, so one fixed threshold cannot serve both backgrounds. At the
realistic background of 0.0096 Hz, 4 cells comes in just under the budget, at 0.98 chance clusters
per hour.

**Figure 1.8. An order test needs several events, and two templates need more than five.** The
y-axis is power to detect order: the share of 300 simulated recordings in which the order indicator
rejects an exact-size 5 % test. The test is calibrated on 3,000 order-free recordings of the same
size and randomized at its threshold. Power is plotted against events per recording (1, 2, 3, 5),
for 7 (A) and 13 (B) of 33 cells per event. Lines are for a template's latency spread of 1, 2.5 or
5 times the onset jitter (r); solid lines are one template and dashed lines are two. With one event
no test has power, because the indicator is 1 with or without order. One template reaches power 0.8
at 3 events of 13 cells when r is 2.5 or more, but at 5 events of 7 cells only when r = 5. Two
templates stay below 0.8 everywhere up to 5 events.

**Figure 1.11. Realistic parameter values sit between the tested points.** Each circle is a
combination of planted jitter and cells per event from the first simulation experiment. A filled
circle means the joint fit recovered jitter within 0.8–1.25 of planted in all four conditions (15 or
45 events, background 0.01 or 0.05 Hz, each the median of 5 recordings). The numbers give the range
of the four ratios. Boxes mark realistic parameter values at the fast and slow bench levels: jitter
0.105 s with 7 cells per event (0.20 of 33), and 0.131 s with 13 cells (0.38 of 33). The box sizes
are nominal. Both boxes lie between the unresolved 0.05 s column and the resolved 0.2 s column. The
fast level also lies between the unreliable 5-cell row and the 10-cell row, so neither has been
tested where it sits.
