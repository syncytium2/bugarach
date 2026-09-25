# Floor + 1: what raising the event floor by one ROI does to the calls

**Evidence for a decision Tony has not made.** Tony is weighing raising the event floor by one
co-active ROI, because people struggle to call events near the floor. Nothing here is adopted, and
ADR-0008 is unchanged. This page and the raster pages are descriptive only (FOUNDATIONS §9). They
count calls; they state no treatment effect.

**Where it is.** Every path below is inside the darkroom folder
`<darkroom>/bugarach/2026-09-25-floor-plus-one-review/`. The repo copy of this page is
`docs/learned/runs/2026-09-25-floor-plus-one-review/README.md`.

**What was run.**
- **Tool:** `tools/detect_with_floors.py --floor-offset 1`, from `c30d88c6` (branch
  `floor-plus-one-variant`).
- **Data:** every recording of the default dataset,
  `2026-09-23_revised_2v_long_senktide_ttx_STEPS_AND_PINS_EXCLUDED`: 66 recordings, of which none
  failed. The dataset stamp is in `run/results.json`.
- **Two floors per window.** Each analysis window is scored at its own floor (ADR-0008) and at its
  own floor + 1. A floor is the fewest co-active ROIs a call must reach, and each window's floor is
  computed from that window's own null.
- **CoactDetect** runs at its shipped setting on every stream (not a proposal), with its minimum
  number of ROIs set to the floor.
- **chorus_norm and chorus_gain_norm** run at the checkpoint each training run picked on
  2026-09-25. They have no minimum-ROI setting, so at a floor they keep the calls whose
  participants reach it.
- Every detector that draws random numbers is seeded.

**The raster pages**, one folder per stream, one page per group × treatment:
- `pages/fast/`
- `pages/slow/`
- `pages/combined/`

**How to read the pages.**
- **Rows:** each recording is a row, aligned at the end of its baseline.
- **Lanes:** above each raster sit six lanes: CoactDetect, chorus_norm and chorus_gain_norm, each at
  its floor and then at floor + 1. The floor + 1 lane is the lighter colour of the pair.
- **Floors:** each recording's own floor per window, in co-active ROIs, is listed in the page
  header. Floor + 1 is one more.
- **Nothing is drawn on the raster.**
- **Which pages exist:** the tool's default treatments, TTX and senktide. So there is no page per
  high K⁺ or wash, although those windows appear on the pages where their recordings do, and are
  counted in the tables below.

**Calls at the own floor, then at own floor + 1**, summed over each group's windows. "Treatment
windows" means every non-baseline window: senktide, TTX, high K⁺ and wash. Groups are in DI, OVX,
MALE, ORX order. Generated from `run/windows.csv` by `floor_plus_one_summary.py`, beside this
page.

**Fast stream**: calls at own floor → at own floor + 1, summed over windows

| Detector | Group | Recordings | Baseline windows | Treatment windows |
|---|---|---|---|---|
| CoactDetect | DI | 17 | 82 calls → 58 (29% lost) | 88 calls → 62 (30% lost) |
| CoactDetect | OVX | 17 | 11 calls → 8 (27% lost) | 22 calls → 17 (23% lost) |
| CoactDetect | MALE | 13 | 44 calls → 30 (32% lost) | 58 calls → 43 (26% lost) |
| CoactDetect | ORX | 19 | 11 calls → 7 (36% lost) | 40 calls → 28 (30% lost) |
| **CoactDetect** | **all** | | **148 calls → 103 (30% lost)** | **208 calls → 150 (28% lost)** |
| chorus_norm | DI | 17 | 28 calls → 26 (7% lost) | 29 calls → 26 (10% lost) |
| chorus_norm | OVX | 17 | 1 call → 0 (100% lost) | 3 calls → 3 (0% lost) |
| chorus_norm | MALE | 13 | 11 calls → 9 (18% lost) | 14 calls → 13 (7% lost) |
| chorus_norm | ORX | 19 | 5 calls → 5 (0% lost) | 6 calls → 5 (17% lost) |
| **chorus_norm** | **all** | | **45 calls → 40 (11% lost)** | **52 calls → 47 (10% lost)** |
| chorus_gain_norm | DI | 17 | 19 calls → 17 (11% lost) | 24 calls → 21 (12% lost) |
| chorus_gain_norm | OVX | 17 | 1 call → 1 (0% lost) | 1 call → 1 (0% lost) |
| chorus_gain_norm | MALE | 13 | 11 calls → 8 (27% lost) | 9 calls → 7 (22% lost) |
| chorus_gain_norm | ORX | 19 | 2 calls → 2 (0% lost) | 3 calls → 3 (0% lost) |
| **chorus_gain_norm** | **all** | | **33 calls → 28 (15% lost)** | **37 calls → 32 (14% lost)** |

**Slow stream**: calls at own floor → at own floor + 1, summed over windows

| Detector | Group | Recordings | Baseline windows | Treatment windows |
|---|---|---|---|---|
| CoactDetect | DI | 17 | 243 calls → 232 (5% lost) | 397 calls → 361 (9% lost) |
| CoactDetect | OVX | 17 | 41 calls → 33 (20% lost) | 66 calls → 51 (23% lost) |
| CoactDetect | MALE | 13 | 116 calls → 112 (3% lost) | 233 calls → 206 (12% lost) |
| CoactDetect | ORX | 19 | 23 calls → 19 (17% lost) | 218 calls → 184 (16% lost) |
| **CoactDetect** | **all** | | **423 calls → 396 (6% lost)** | **914 calls → 802 (12% lost)** |
| chorus_norm | DI | 17 | 234 calls → 222 (5% lost) | 383 calls → 346 (10% lost) |
| chorus_norm | OVX | 17 | 30 calls → 30 (0% lost) | 46 calls → 36 (22% lost) |
| chorus_norm | MALE | 13 | 109 calls → 105 (4% lost) | 198 calls → 181 (9% lost) |
| chorus_norm | ORX | 19 | 20 calls → 16 (20% lost) | 195 calls → 176 (10% lost) |
| **chorus_norm** | **all** | | **393 calls → 373 (5% lost)** | **822 calls → 739 (10% lost)** |
| chorus_gain_norm | DI | 17 | 225 calls → 206 (8% lost) | 324 calls → 297 (8% lost) |
| chorus_gain_norm | OVX | 17 | 29 calls → 28 (3% lost) | 29 calls → 25 (14% lost) |
| chorus_gain_norm | MALE | 13 | 96 calls → 95 (1% lost) | 171 calls → 153 (11% lost) |
| chorus_gain_norm | ORX | 19 | 16 calls → 13 (19% lost) | 159 calls → 147 (8% lost) |
| **chorus_gain_norm** | **all** | | **366 calls → 342 (7% lost)** | **683 calls → 622 (9% lost)** |

**Combined stream**: calls at own floor → at own floor + 1, summed over windows

| Detector | Group | Recordings | Baseline windows | Treatment windows |
|---|---|---|---|---|
| CoactDetect | DI | 17 | 273 calls → 244 (11% lost) | 400 calls → 361 (10% lost) |
| CoactDetect | OVX | 17 | 41 calls → 35 (15% lost) | 46 calls → 36 (22% lost) |
| CoactDetect | MALE | 13 | 131 calls → 127 (3% lost) | 230 calls → 207 (10% lost) |
| CoactDetect | ORX | 19 | 26 calls → 21 (19% lost) | 193 calls → 172 (11% lost) |
| **CoactDetect** | **all** | | **471 calls → 427 (9% lost)** | **869 calls → 776 (11% lost)** |
| chorus_norm | DI | 17 | 139 calls → 130 (6% lost) | 197 calls → 181 (8% lost) |
| chorus_norm | OVX | 17 | 19 calls → 19 (0% lost) | 9 calls → 9 (0% lost) |
| chorus_norm | MALE | 13 | 74 calls → 71 (4% lost) | 101 calls → 96 (5% lost) |
| chorus_norm | ORX | 19 | 16 calls → 14 (12% lost) | 90 calls → 83 (8% lost) |
| **chorus_norm** | **all** | | **248 calls → 234 (6% lost)** | **397 calls → 369 (7% lost)** |
| chorus_gain_norm | DI | 17 | 146 calls → 138 (5% lost) | 219 calls → 211 (4% lost) |
| chorus_gain_norm | OVX | 17 | 26 calls → 26 (0% lost) | 13 calls → 13 (0% lost) |
| chorus_gain_norm | MALE | 13 | 91 calls → 91 (0% lost) | 124 calls → 120 (3% lost) |
| chorus_gain_norm | ORX | 19 | 15 calls → 14 (7% lost) | 86 calls → 83 (3% lost) |
| **chorus_gain_norm** | **all** | | **278 calls → 269 (3% lost)** | **442 calls → 427 (3% lost)** |


**What the tables show, as counts:**
- **Where floor + 1 costs most.** It removes the most calls from CoactDetect on the fast stream:
  30% at baseline and 28% in treatment windows, of 148 and 208 calls. On the slow and combined
  streams CoactDetect loses 3% to 23% per group.
- **The chorus models.** Floor + 1 removes 0% to 27% of their calls per group and window kind. The
  one exception is a single call: fast OVX chorus_norm at baseline, 1 call → 0. The lowest shares
  are on the combined stream, at 0% to 12%.
- **Small counts.** On the fast stream, OVX and ORX have few calls at the floor: 1 to 11 per cell
  for chorus, 11 to 40 for CoactDetect. Their shares move a lot on one call. For example, fast
  OVX chorus_norm at baseline is 1 call → 0.
