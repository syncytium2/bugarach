# Step B of the slow bench: a pilot of the nets against the coded reference, both benches

Written 2026-09-21 on WSMIP064 for `docs/handoffs/2026-09-21-slow-bench.md`. Working material, not murderboarded.
A pilot, not the comparison: two nets, untuned, no false-alarm gating, one draw.

**Protocol** (`slow_pilot.py`, run once per bench): `chorus_norm` and `tube` at goal 2's
untuned configuration (`tune_learned_vs_coact.UNTUNED`, crop 4,096 frames, batch 3, 10 fitting
recordings), training seeds 0–2, on the GPU, fitted on that bench's seeds 1000–1023 on both
backgrounds through `fold_maker` (threshold block kept apart), decoding at each fit's own
threshold and the default 20-frame merge gap. The coded reference is each bench's
`OPERATING_POINTS`: on slow, the adopted slow settings; on fast, `bench.OPERATING_POINTS`,
which runs CoactDetect and LoCo **binned** (goal 1's sliding values are not on `main`), so
the fast coded numbers are below what goal 2 compared against. Scored on fresh seeds
4000–4023 per background (3000–3047 are kept for a final run); calls per hour on the
no-coordination recording at seeds 54000–54011. Each fit took 5–16 s on the GPU.

**Figure 1** (`2026-09-21-slow-pilot.png`, and the darkroom's `bugarach/2026-09-21-slow-pilot.png`).
The two panels' x-axes differ in range; read the spans below, not the dots' spread.

| mean F1 | fast bench | slow bench |
|---|---|---|
| CoactDetect | 0.708 | 0.859 |
| LoCo | 0.700 | 0.849 |
| SPIKE-synch | 0.450 | 0.844 |
| `chorus_norm`, seeds 0 / 1 / 2 | 0.739 / 0.692 / 0.720 | 0.842 / 0.827 / 0.835 |
| `tube`, seeds 0 / 1 / 2 | 0.670 / 0.686 / 0.654 | 0.843 / 0.842 / 0.836 |

**What it answers.** The slow bench separates far less. Every detector and every fit sits
between 0.827 and 0.859 — a span of 0.032 F1, against 0.29 on fast (0.085 without SPIKE-synch).
On slow the nets sit just below CoactDetect (by 0.016 to 0.032), about the spread one
net shows across its own training seeds (up to 0.015). A full comparison on this bench would be
asked to resolve differences of about 0.02 F1 against a between-draw noise goal 2 measured at
0.010 on fast — possible with a replicate, but the likely answer is a tie.

**What it does not answer.** Tuned nets, the shared false-alarm budget, and the jitter
question (step A): the slow bench's jitter may move from 0.30 to 0.46 s, which costs two coded
detectors about 0.09 F1 and would widen the field somewhat. The nets' 20-frame merge gap was
not varied.
