# The correlogram's width by group on the 66-recording export: still no group difference, and still one recording at a time

Written 2026-09-23 on the orchestrator's brief, at Tony's request. Working material, not
murderboarded.

**Tool:** `tools/measure_jitter_correlogram.py --by-group` (tests:
`tests/test_measure_jitter_correlogram.py`), same settings as the
[2026-09-22 run on 84 recordings](../2026-09-22-jitter-by-group/README.md): 400 mouse-clustered
bootstrap draws, 2,000 label permutations, leave-one-out per group. **Data:** the default export
`2026-09-23_revised_2v_long_senktide_ttx_STEPS_AND_PINS_EXCLUDED` (role `senktide_ttx`), confirmed
by Tony in this session — 66 recordings from 36 mice, senktide- and TTX-first only, `t50rise`
onsets, baseline analysis windows only (FOUNDATIONS §9). **Record:** `jitter_correlogram.json`.
**Figures**, here and in the darkroom under `bugarach/correlogram/2026-09-23-66/`: **Figure 1**
`jitter_by_group.png`, **Figure 2** `raw_correlograms.png`, **Figure 3** `one_recording_leverage.png`.
Groups are listed DI, OVX, MALE, ORX throughout, from `bugarach.groups`.

## The answer

**Neither stream shows a width difference between groups, and that is the same answer the 84 gave.**

**Fast:** the four groups span 0.147 s (OVX) to 0.197 s (MALE), a spread of **0.051 s** — below the
0.072 s median spread that shuffled group labels produce. **p = 0.757.**

**Slow:** spread **0.080 s** against a shuffled 95th percentile of 0.082 s, **p = 0.055**, which
reads like the 84's 0.054. It is no more a group difference here than it was there, and the 66 make
the reason plainer, because **the test crosses 0.05 in both directions depending on which single
recording is removed**:

| slow, 66 recordings | DI | OVX | MALE | ORX | spread | p |
|---|---:|---:|---:|---:|---:|---:|
| as recorded | 0.214 | 0.220 | 0.264 | 0.184 | 0.080 s | 0.054 |
| without `20250806_174` (ORX's mover) | 0.214 | 0.220 | 0.264 | **0.232** | 0.049 s | 0.474 |
| without `20250829_204` (OVX's mover) | 0.214 | **0.167** | 0.264 | 0.184 | 0.097 s | 0.047 |
| without both | 0.214 | 0.167 | 0.264 | 0.232 | 0.097 s | 0.067 |

A four-way statistic that one recording can push to 0.47 or to 0.047 is measuring recordings, not
groups.

**Yes, `20250806_174` still carries slow ORX.** Removing it moves that group **0.184 s → 0.232 s**
(+0.048 s), the same effect and nearly the same size as on the 84 (0.183 s → 0.229 s). It is also
ORX's biggest mover on fast (0.158 s → 0.097 s).

## Per group, on the 66

| stream | group | recordings | mice | ROIs | onsets | half-width (s) | 95% interval | σ (s) |
|---|---|---:|---:|---:|---:|---:|---|---:|
| fast | DI | 17 | 10 | 512 | 14,118 | 0.192 | 0.173–0.225 | 0.108 |
| fast | OVX | 17 | 9 | 533 | 11,809 | 0.147 | 0.080–0.297 | 0.081 |
| fast | MALE | 13 | 8 | 446 | 6,874 | 0.197 | 0.141–0.272 | 0.111 |
| fast | ORX | 19 | 9 | 618 | 4,745 | 0.158 | 0.082–0.323 | 0.088 |
| fast | **pooled** | 66 | 36 | 2,109 | 37,546 | **0.186** | 0.158–0.220 | **0.105** |
| slow | DI | 17 | 10 | 512 | 9,762 | 0.214 | 0.206–0.242 | 0.122 |
| slow | OVX | 17 | 9 | 533 | 4,063 | 0.220 | 0.062–0.238 | 0.125 |
| slow | MALE | 13 | 8 | 446 | 6,142 | 0.264 | 0.247–0.316 | 0.152 |
| slow | ORX | 19 | 9 | 618 | 2,712 | 0.184 | 0.170–0.652 | 0.104 |
| slow | **pooled** | 66 | 36 | 2,109 | 22,679 | **0.228** | 0.211–0.256 | **0.131** |

σ is the timing spread of the cells taking part in a shared moment, read off the simulator
calibration. Both benches now plant the values this measure produced (`8137da71`), so σ is not to
be quoted against the bench as a finding.

## The 84 against the 66

Every recording file in the 66 is byte-identical (sha256) to its copy in the 84 — the producer
checked it on arrival and `current_export.toml`'s `senktide_ttx` note records it — and the sidecars
are row-identical on those recordings. **So nothing below differs because of event derivation. It
differs because of which recordings are in the folder**: MALE 22 → 13, ORX 25 → 19, OVX 20 → 17,
DI 17 → 17 (DI is the same 17 recordings in both).

| stream | group | recordings | half-width (s) | zero-lag peak (excess coincidence) |
|---|---|---:|---:|---:|
| fast | DI | 17 → 17 | 0.192 → 0.192 | 4.5 → 4.5 |
| fast | OVX | 20 → 17 | 0.148 → 0.147 | 1.0 → 0.9 |
| fast | MALE | 22 → 13 | 0.183 → 0.197 | 4.0 → 3.5 |
| fast | ORX | 25 → 19 | 0.148 → 0.158 | 2.0 → 2.2 |
| fast | **pooled** | 84 → 66 | 0.183 → 0.186 | 3.0 → 2.9 |
| slow | DI | 17 → 17 | 0.214 → 0.214 | 32.4 → 32.4 |
| slow | OVX | 20 → 17 | 0.235 → 0.220 | 20.3 → 18.4 |
| slow | MALE | 22 → 13 | 0.261 → 0.264 | 24.6 → 23.1 |
| slow | ORX | 25 → 19 | 0.183 → 0.184 | 17.0 → 18.4 |
| slow | **pooled** | 84 → 66 | 0.230 → 0.228 | 27.5 → 27.1 |

The zero-lag peak height is the excess coincidence at lag 0 — observed ÷ expected onset pairs − 1,
dimensionless, 0 meaning no more pairs than the ROIs' own rates predict. It is in the table because
Figure 1's normalised panels deliberately hide it, and because it is where the groups differ most:
on slow, DI's peak stands at 32.4 against ORX's 18.4, while their widths are 0.214 s and 0.184 s.
**Height is not width**, and nothing here has tested whether the heights differ.

Widths move by at most 0.015 s (fast MALE, the group that lost 9 of its 22 recordings) and DI does
not move at all, which is what it should do: its recordings are the same ones.

## The three recordings that carry a group

Rendered from the baseline analysis window, fast and slow, with
`tools/make_real_detection_figure.py --window baseline`, into
`<darkroom>/bugarach/2026-09-23-recordings-that-carry-a-group/`. The `--window` option is new here:
the tool drew whole recordings only, so there was no way to see the window every baseline-only
measurement actually reads. Detectors still run on the whole recording; the flag crops what the
panels show, and the header says which. Marks sit in a lane above the raster and nothing is drawn
on the raster.

**`20250806_174` — ORX, mouse 58, TTX-first, 36 ROIs.** Quiet in both streams: fast 222 onsets at
0.0051 Hz per ROI, slow 298 at 0.0069 Hz per ROI, against a measured baseline interquartile band of
0.0052–0.0190 Hz per ROI, so it sits at or just under the lower quartile. The slow raster is nearly
empty for its first 16 minutes and then carries five or six near-vertical columns in the last three
and a half, each spanning most of the population; SCE and LoCo both claim there. The fast raster
does the same at the two ends of the window. **Few onsets, and most of them inside a handful of
near-simultaneous moments** — which is exactly the shape that makes a tall, narrow zero-lag peak out
of very little material, and is why one recording can set a sparse group's width.

**`20260702_334` — OVX, mouse 85, TTX-first, 36 ROIs.** The mirror image on fast: 733 onsets at
0.0170 Hz per ROI, near the top of the band, with a **dense burst across most of the population in
the first three minutes** where SCE claims almost continuously, and a much sparser remainder in
which activity sits mostly in the more active rows. Slow is quiet by comparison, 235 onsets at
0.0054 Hz per ROI, with tight columns at about 13.3, 13.8, 18.3 and 19.8 minutes.

**`20260115_243` — ORX, mouse 69, senktide-first, 43 ROIs.** The busiest of the three and the one
that does not look like the others: fast 1,041 onsets at 0.0212 Hz per ROI, above the band's upper
quartile, slow 703 at 0.0143 Hz per ROI. Both rasters are densely and fairly evenly filled across
the whole window with no single episode dominating, and SCE's claims are scattered throughout. Its
influence is **weight of numbers** — it contributes more onset pairs than its peers do — rather than
one striking episode.

**What none of them shows** is a signature of the artifacts this corpus has already had removed:
no whole-population column at a single frame, no flat stretch pinned at a floor. Two of the three
are quiet recordings whose onsets arrive in a few near-simultaneous moments; the third is simply
busy. **Which recordings belong in the folder is the producer's call** (Tony, 2026-09-23), and
nothing here filters, weights or excludes anything.

## What this does not settle

⚠ **The permutation test still shuffles labels at fixed mouse count, not at fixed onset count**, and
the groups' onset counts are further apart on the 66 than on the 84: ORX brings 2,712 slow onsets
against DI's 9,762. A shuffled group of 9 mice usually carries more onsets than the real ORX, so its
width is the better-estimated one, the null spread comes out too tight and p too small. The 0.055 is
an optimistic number, and the leave-one-out above says the same thing more directly.

⚠ **Peak height is untested.** It differs by group by nearly a factor of two on slow and this run
says nothing about whether that difference survives the same scrutiny the width got.

⚠ **13 recordings from 8 mice is what MALE now is.** Its fast width moved 0.183 → 0.197 s on losing
9 recordings; that is a smaller shift than the 0.047 s one recording of it can produce.
