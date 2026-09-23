# De-pinning the export barely moved shared co-modulation; the surrogate arms still remove most of it

Run 2026-09-23 on WSMIP064. Shared co-modulation re-measured on all three lab streams —
**fast**, **slow** and **combined** — over the current default export, the one whose pinned
regions of interest (ROIs) were removed.

**Working material, not murderboarded** — same standing as the other run records here.

**Dataset:** `steps_and_pins_excluded`, 84 recordings, 44 mice, **confirmed by Tony in this
session** in his own words before anything read it.
**Tool:** `tools/measure_slow_comodulation.py`, unchanged by this run.
**Figures:** `tools/make_slow_comodulation_figure.py` → `fig1`–`fig6` here and in the darkroom
folder `bugarach/2026-09-23-comodulation-three-streams/`, claimed on `docs/SESSIONS.md` before
any write.
**Record:** `summary.json` — every stream, every arm, per recording and per group.
Wall clock 587 s; 8 surrogate draws per recording, 12 jobs.

**Adopts nothing.** No operating point, no bench constant, no model. This measures, and the
one comparison it is for — against the 2026-09-17 page — is reported below without a ruling.

> **`results.json` carries `tag = "slow-comodulation-2026-09-17"`.** That is the tool's default
> tag constant, not a claim about when this ran; it was not updated when the third stream was
> added. Read the run date from this record, not from that field.

## What the measure is

Each ROI's onset times are binned; the **variance of the population onset count** is compared
with the variance the same ROIs would give if they were independent of one another. A ratio of
1.0 means independent. Everything below is at **1-minute bins** unless another bin is named,
and every interval is the **bootstrap over mice** (44 mice for the lab streams, 32 for Dard),
because recordings from one mouse are not independent draws.

Three abbreviations used throughout. **ROI** is a region of interest — one traced cell.
**CoactDetect** is the project's calibrated coincident-event detector, run here at
`detect_folder.detector_params('coact', …)`, the same settings on all three streams so the
removal arm is comparable across them. ***J*** is the width of the **rigid shift**, this
project's surrogate: every cell's whole train of events slid by **its own** random offset, at
most *J* seconds. Each cell keeps its own internal timing, and the alignment between cells is
destroyed below roughly *J* — which is why the arm removes coincident events and leaves
minute-scale shared change in place. `tools/tube_self_supervised.py`'s `rigid_frames` draws
`size=1 if shared else len(trains)` offsets; `measure_slow_comodulation` leaves `shared` at its
default `False`, so it is one offset **per ROI**, not one for the recording.

## The three streams, side by side

Pooled over recordings, 1-minute bins, mouse bootstrap in brackets. All values are ratios
(dimensionless: variance ÷ variance).

| stream | as recorded | CoactDetect episodes removed | removed + 120 s block control | removed + rigid shift *J* = 20 s |
|---|---|---|---|---|
| lab fast | 3.20 [2.46, 4.11] | 2.54 [1.96, 3.21] | 2.36 [1.83, 2.97] | 2.48 [1.94, 3.11] |
| lab slow | 12.00 [7.95, 15.39] | 2.61 [1.85, 3.35] | 2.17 [1.59, 2.78] | 2.45 [1.82, 3.10] |
| lab combined | 5.54 [3.88, 7.31] | 2.77 [2.14, 3.38] | 2.51 [1.96, 3.06] | 2.68 [2.07, 3.25] |
| Dard et al. 2022 | 15.23 [12.50, 18.28] | — | — | — |

The Dard comparison recordings have no CoactDetect arm here — the removal is defined on the lab
streams' detector output, and running it on a foreign preparation would not mean the same thing.

**The three streams converge once the episodes are removed.** As recorded they span 3.20 to
12.00, a factor of 3.8; after removal and the block control they span 2.17 to 2.51, a factor of
1.15, and all three intervals overlap. Nearly all of the difference between the streams is in
the coincident episodes, not in what is left over.

**Figure 4, how much the count varies**, is this table across all three bin widths (1 s, 10 s
and 1 minute) with Dard beside it. **Figure 5, recordings**, gives the full and zoomed excess
coincidence against lag for each stream, and **Figure 6, by group**, splits it by treatment
group. **Figures 1–3** are the synthetic worlds and what each surrogate removes; they never
read the export folder and are unchanged from the 17 September run.

> **The minute-scale residual is not interpreted here.** Something at ~2.2–2.5× survives every
> surrogate on every stream. Whether that is background drift or coordination is an open question
> with Tony, and this record deliberately does not answer it.

## Against 2026-09-17: the contamination was not driving the result

The 17 September page read the export before the pinned ROIs were removed, and its numbers are
under a STOP banner for exactly that reason. This run is the re-measurement. That page is
**not edited by this change** — Tony reads these numbers first.

| | 17 Sept (contaminated) | 23 Sept (de-pinned) | change |
|---|---|---|---|
| fast, as recorded | 3.21 [2.47, 3.97] | 3.20 [2.46, 4.11] | −0.01 |
| fast, episodes removed | 2.56 [1.92, 3.21] | 2.54 [1.96, 3.21] | −0.02 |
| fast, removed + block | 2.37 [1.79, 2.95] | 2.36 [1.83, 2.97] | −0.01 |
| slow, as recorded | 11.37 [7.50, 14.57] | 12.00 [7.95, 15.39] | +0.63 |
| slow, episodes removed | 2.55 [1.80, 3.41] | 2.61 [1.85, 3.35] | +0.06 |
| slow, removed + block | 2.13 [1.54, 2.83] | 2.17 [1.59, 2.78] | +0.04 |
| Dard et al. 2022, as recorded | 15.23 [12.50, 18.28] | 15.23 [12.50, 18.28] | 0.00 |

**Every lab change is far inside its own bootstrap interval**, and Dard — which the de-pinning
could not touch — reproduces to the digit, which is the control that says the pipeline itself
did not move. The combined stream has no 17 September row: this run is the first time it was
measured.

**This is a result worth stating plainly and it is not the result the STOP banner anticipated.**
The banner's worry was that frame-floor-pinned ROIs are a cross-cell artifact and therefore
imitate the very signal this page measures. Measured, they do not carry it: removing them
changes the pooled answer by less than a hundredth on the fast stream and by about six
hundredths on the slow one. The stop was still right to happen — the question had to go to the
producer rather than be estimated by a session — but the answer is that the numbers stand.

**The four recordings are still over-represented, and that part has not gone away.** With their
pinned ROIs removed they still hold 9.4 % of the slow stream's pooled excess variance as
recorded and 13.4 % of it after removal and the block control, against the 19 % the contaminated
page reported. Dropping all four moves slow from 12.00 to 11.92 as recorded and from 2.17 to
2.11 after removal. All four are **DI**, the group that reads highest, so the by-group reading
below is still the part to lean on least.

## By group, with leave-one-out

Four treatment groups: **DI** (diestrus), **MALE**, **ORX** (orchiectomised) and **OVX**
(ovariectomised). For each group and stream the table gives the pooled 1-minute ratio, then the
range it takes when each recording in turn is dropped and the group repooled, then the single
most influential recording.

This leave-one-out is not part of the co-modulation tool. It was added because
[#765](https://github.com/syncytium2/bugarach/pull/765) found one dense recording carrying a
group's slow jitter result, and the same question is worth asking of this measure. It calls
`measure_slow_comodulation.pooled` rather than repooling by hand, so it cannot disagree with the
run it is checking.

**As recorded:**

| stream | group | recordings | pooled | leave-one-out range | most influential |
|---|---|---|---|---|---|
| fast | DI | 17 | 3.60 | [3.32, 3.83] | `20250925_231` → 3.32 |
| fast | MALE | 22 | 3.05 | [2.53, 3.20] | `20241120_96` → 2.53 |
| fast | ORX | 25 | 1.86 | [1.49, 1.92] | `20260115_243` → 1.49 |
| fast | OVX | 20 | 3.26 | [1.64, 3.62] | `20260702_334` → **1.64** |
| slow | DI | 17 | 12.93 | [10.10, 14.03] | `20260303_296` → 10.10 |
| slow | MALE | 22 | 16.37 | [13.59, 18.25] | `20250827_199` → 13.59 |
| slow | ORX | 25 | 5.82 | [2.35, 6.49] | `20250806_174` → **2.35** |
| slow | OVX | 20 | 5.24 | [3.04, 5.59] | `20250829_204` → 3.04 |
| combined | DI | 17 | 5.57 | [4.65, 6.06] | `20260303_296` → 4.65 |
| combined | MALE | 22 | 7.35 | [5.64, 8.42] | `20241120_96` → 5.64 |
| combined | ORX | 25 | 3.19 | [2.23, 3.38] | `20250806_174` → 2.23 |
| combined | OVX | 20 | 4.20 | [2.86, 4.42] | `20260702_334` → 2.86 |

**Episodes removed + 120 s block control:**

| stream | group | pooled | leave-one-out range | most influential |
|---|---|---|---|---|
| fast | DI | 2.64 | [2.34, 2.82] | `20250731_151` → 2.34 |
| fast | MALE | 1.94 | [1.70, 2.01] | `20260706_343` → 1.70 |
| fast | ORX | 1.64 | [1.20, 1.77] | `20260115_243` → 1.20 |
| fast | OVX | 2.72 | [1.52, 2.98] | `20260702_334` → **1.52** |
| slow | DI | 1.96 | [1.66, 2.07] | `20260630_316` → 1.66 |
| slow | MALE | 3.06 | [2.40, 3.61] | `20241120_96` → 2.40 |
| slow | ORX | 1.89 | [1.30, 2.03] | `20260115_243` → 1.30 |
| slow | OVX | 1.43 | [1.35, 1.51] | `20260702_334` → 1.35 |
| combined | DI | 2.76 | [2.47, 2.94] | `20250925_231` → 2.47 |
| combined | MALE | 2.37 | [2.10, 2.50] | `20241120_96` → 2.10 |
| combined | ORX | 1.84 | [1.24, 1.96] | `20260115_243` → 1.24 |
| combined | OVX | 2.67 | [1.57, 2.88] | `20260702_334` → **1.57** |

### ⚠ Three recordings carry more than a group should let one recording carry

- **`20250806_174` is the same recording [#765](https://github.com/syncytium2/bugarach/pull/765)
  named for slow jitter.** Dropping it takes slow ORX from 5.82 to 2.35 — it more than halves
  the group, and the group goes from the second-highest as-recorded slow reading to the lowest.
  Two independent measures of coordinated activity now point at one recording; that is worth a
  look at the recording itself rather than at either measure.
- **`20260702_334` carries OVX on two streams.** Fast as recorded 3.26 → 1.64, and combined
  after removal and the block control 2.67 → 1.57. In both, dropping one recording of 20 halves
  the group.
- **`20260115_243` is the most influential ORX recording on all three streams** after removal
  and the block control (fast 1.64 → 1.20, slow 1.89 → 1.30, combined 1.84 → 1.24). It is the
  only recording that tops the list in every stream.

**No group difference here is safe to read.** In six of the twelve group-by-stream cells the
leave-one-out range is wider than the gap between the groups being compared. The group
comparison needs either a per-mouse weighting throughout or an explicit influence check before
anything is concluded from it, and neither is done in this run.

## What was fixed while making this

The figure tool crowded once the third lab stream added a column. Three defects, all in
`tools/make_slow_comodulation_figure.py` and all fixed in the same change:

- **The lag axis label was drawn once per column.** Three or four copies of a sentence that long
  overlap each other and the last one clips at the figure's right edge. `lag_axis` now separates
  the tick labels from the axis-label text, and `lag_caption` writes the label **once**, centred
  under the whole bottom row, which is also what the plot conventions ask for.
- **Y-axis labels landed on the previous panel's frame.** Figure 5's column gap was not wide
  enough for a column's tick labels plus its two-line y-label; Figure 6's labels were two lines
  where the longest line was taller than the panel. Wider gaps in both, and three lines in
  Figure 6 so the arm's name sits on its own line.
- **Narrower panels ran `0.3s` into `1s`** on Figure 5's lag ticks. Its lag ticks are a size
  smaller; Figure 6, with three columns rather than four, keeps the default.

Figure 6's off-scale legend entry also said "curve above the view (▲ below it)" while showing a
▼ marker. It now reads the same as Figure 5's.

## Reproduce

```
python tools/measure_slow_comodulation.py --out <run>
python tools/make_slow_comodulation_figure.py --run <run> --out <figures>
```

The default export must be confirmed first (`python -m bugarach.dataset confirm`, by Tony, never
on his behalf). The combined stream reaches the export folder, so this run was the first real
exercise of that loading path outside CI — CI cannot reach the folder at all.
