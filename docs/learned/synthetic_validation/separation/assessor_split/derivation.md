# When two coordinated events are read as two: the assessor and the count detector

Synthetic only. This answers item 1 of the minimum-separation handoff (the assessor's split
probability), the count detector's version of it (item 4's second tool), and the simulation check.
`split.py` computes every number here and writes `split_output.txt` (all 576 compared points) and
`synth_recovery_plot_assessor-split-against-separation_20261025.png`. Run it from the checkout with `PYTHONPATH=src`. It takes about 25 min on 44 workers;
`--resim` reruns only the simulation and `--plot-only` only the figure.

**In one line.** The tools set the minimum separation, and the data do not. A pair is split half as
often as it can be at a centre-to-centre separation of **2.5 s for the assessor** and **5.0 s for
the count detector**. That is (merge rule + ½) × bin width, almost whatever the jitter, the
participation or the background. Below **2 s (assessor) and 4 s (count) a pair is effectively never
split**, even when the two onset clouds are cleanly bimodal (Δ > 2σ = 0.21 s at the lab's jitter).
The data parameters (σ, k, b, K) instead set the **plateau**: whether each event is detected at
all.

## 1. The rules, read from the code

**Assessor** (`bugarach.assess`; defaults `bin_width_sec=None` → 1 s, `merge_bins=2`,
`wm_factor=1.5`):

1. Bin j holds onsets t with ⌊t / 1 s⌋ = j (`_coact_count`). The count is the number of distinct
   ROIs with at least one onset in the bin.
2. A bin triggers when its count is at least K (`counts >= K`).
3. Triggered bins merge into one group when consecutive triggered indices differ by at most `merge_bins` = 2,
   that is, with at most one sub-K bin between them (`_clusters`).
4. The group centre is tc = mean of (j + 0.5) over its triggered bins. Each ROI's nearest onset with
   |t − tc| ≤ 1.5 s is gathered, and the group is kept as a cluster when at least K ROIs gather.

**The gather never removes a group at these defaults.** The interval [tc − 1.5, tc + 1.5] fully
contains the bins b with tc − 1.5 ≤ b ≤ tc − 0.5, which are at least two consecutive bins b₀ and
b₀ + 1, with b₀ = ⌈tc − 1.5⌉. Since tc lies in [f₁ + ½, fₙ + ½] (f₁ and fₙ are the first and last
triggered bins), either b₀ = f₁ − 1, in which case the window also covers f₁, or b₀ lies in [f₁, fₙ].
In the second case b₀ is a triggered bin, or it is the single sub-K bin between two triggered bins, so b₀ + 1
triggers. Either way a whole triggered bin lies inside the gather window. Every ROI counted in that bin
therefore has an onset within 1.5 s of tc, so at least K ROIs gather. The argument needs
`wm_factor` ≥ 1.5 bins and `merge_bins` ≤ 2. Checked: merged groups equalled `_clusters`' output in
all 576 simulated recording-thresholds. The shipped `assess_coactivity` reported the same cluster
totals as the replica on the 8 recordings run through it. **So the "±1.5 s gather" in the
handoff's floor of about 3 s contributes nothing. The floor is the merge rule.**

**Count detector** (`detectors/count.py`, the bench's operating point `bin_sec=2`, `k_offset=0`,
`merge_gap_sec=3`, `min_rois` set to the ADR-0008 floor per `bench.FLOORED_SETTING`). The count is
the same distinct-ROI count in 2 s bins, calling bins with count ≥ floor. Two called bins merge when
`edges[b] − edges[prev+1]` ≤ 3 s, that is (b − prev − 1) × 2 s ≤ 3 s, so at most one uncalled bin
between them. There is no gather. **It is the assessor's automaton on 2 s bins.** (The function's
own default `min_rois=3` is not what the bench runs.)

**Thresholds used.**

| | b = 0.0096 Hz | b = 0.05 Hz |
|---|---|---|
| assessor, smallest K with ≤ 1 chance cluster per hour (`theory.chance_clusters_per_min`, N = 33) | 4 (0.98/h); the simulations here use 5 (0.054/h), one above it | 8 (0.53/h) |
| ADR-0008 event floor (`event_floor.window_floor` on 2 h of Poisson background, 1000 draws, 2 seeds, stable in both halves) | 6 | 12 |

The assessor is reported at 5 and 8 and the count detector at its floor, 6 and 12. All four K run
on both tools (`split_output.txt`).

## 2. The model and the assumptions

Two events, A at centre c and B at c + Δ. Each recruits k of N = 33 cells at random, independently
of the other, so the number of shared cells is m ~ Hypergeometric(33, k, k), with mean k²/N (1.5
at k = 7, 5.1 at k = 13). Every participant's onset is c + σZ, with Z standard normal and
independent across cells and events, then rounded half away from zero to the 0.1 s frame. This is
`simulate_coordination`'s rule. Background is an independent Poisson process at b Hz per cell.
Every cell carries it, participants included.

Assumptions, all of them the generator's own:

- **A1.** Bin-grid phase u = c mod w is uniform on [0, w). Here w is 1 s for the assessor and 2 s
  for the count detector.
- **A2.** Gaussian jitter, rounded to the frame. Round(c + σZ) falls in bin j iff c + σZ lies in
  [jw − 0.05, (j + 1)w − 0.05). This is exact, and no frame time lands on the wrong side of a bin
  edge in floating point (checked on 200,000 frames). So p_j(c) = Φ(((j+1)w − 0.05 − c)/σ) −
  Φ((jw − 0.05 − c)/σ).
- **A3.** Background presence per bin per cell is Bernoulli(p_b), with p_b = 1 − e^(−bw), and is
  independent across bins, cells and events.
- **A4.** The pair is isolated. No other event lies within the analysis region of ±(7σ + 3 bins)
  around the pair. Chance groups inside that region are counted in the prediction, and the
  simulation counts the same bins.
- **A5.** k is fixed, membership is uniformly random, and onsets are independent within an event
  (no common-mode jitter).

**Conditional independence of bins.** Let X_j be the number of distinct cells with an *event* onset
in bin j. Given the vector X, the bins trigger independently, with

  φ(x) = P(x + Binomial(N − x, p_b) ≥ K),

because the N − x cells without an event onset in the bin carry independent background (A3). The
correlation between bins comes entirely from X: each onset lands in exactly one bin.

**Exact law of X: a bin-by-bin multinomial.** Process the bins left to right. Use the hazard
h_j = p_j / Σ_{i≥j} p_i, the chance that a still-pending onset lands in bin j. The state is three
counts:

- α: cells with only an A onset pending (A-only cells, plus shared cells whose B onset has landed);
- β: cells with only a B onset pending;
- γ: shared cells with both onsets pending.

A shared cell whose B landed in an earlier bin behaves exactly like an A-only cell from then on. Its
A onset can no longer share a bin with its B onset. That is why three counters suffice. In bin j:

- i_A ~ Bin(α, h_jᴬ) and i_B ~ Bin(β, h_jᴮ) land;
- the γ cells split multinomially into "stay", "A only" (probability h_jᴬ(1 − h_jᴮ)), "B only" and
  "both in this bin" (probability h_jᴬ h_jᴮ);
- X_j = i_A + i_B + (number of γ cells with A only, B only or both), and a cell with both onsets
  in the bin counts once;
- the next state is α' = α − i_A + (γ→B only), β' = β − i_B + (γ→A only), and γ' = γ minus the γ
  cells that moved.

The initial state is (k − m, k − m, m), weighted by the hypergeometric law.

**Grouping automaton.** The state is "no group yet", or (g, d): g groups so far, capped at "3 or
more", and d sub-K bins since the last triggered bin, capped at 2. A triggered bin with d ≤ 1 stays in g. A triggered bin with
d = 2 opens group g + 1. A sub-K bin raises d. Both tools use this same automaton.

**The formula.** With π a vector over (placement state × automaton state):

  π_{j+1} = Σ_x T_j(x) π_j ⊗ [φ(x) F + (1 − φ(x)) F̄],

where T_j(x) is the placement transition restricted to X_j = x, and F and F̄ are the automaton's
triggered and untriggered maps. Then

  P(G = g | Δ, σ, k, K, b, N) = (1/w) ∫₀^w Σ_m H(m) · [π_final(u, m)]_g du.

The integral over u is a 32-point midpoint rule over one bin, and that quadrature is the only
approximation. Both clouds' tails beyond the region are folded into its end bins. The outputs are
P(two) = P(G = 2) and P(at least one) = 1 − P(G = 0), which tells missed events from merged ones;
P(G ≥ 3) is the chance of extra groups. `dp_groups` implements it. Every P sums to 1 to machine
precision.

**The closed form in the limit.** As σ → 0 and b → 0, each event's onsets fall in one bin, and the
pair splits iff ⌊(u + Δ)/w⌋ − ⌊u/w⌋ ≥ 3, that is, at least two sub-K bins between the two triggered bins.
With u uniform that gives

  P(two) → f_A f_B · clamp(Δ/w − 2, 0, 1),

where f is the chance one event reaches K on its own. The split probability is 0 below Δ = 2w,
rises linearly, is half its plateau at Δ = **2.5 w** and is complete at 3w. The exact curves follow
this closely (§4).

## 3. Simulation

Pairs were planted by hand the way `simulate_coordination` plants events, with `RandomState`
draws: `rng.choice(N, k, replace=False)` membership, `t + σ·randn()` clipped to [0, T], Poisson
background, and `matlab_round` to the 0.1 s frame. Each recording holds 400 pairs, with centres
40 s + U(0, 2) s apart. That makes the bin phase uniform for both tools, and pairs at least 30 s
apart. The grid is 2 jitters × 2 participations × 2 backgrounds × 9 separations = 72 recordings,
28,800 pairs, each read by both tools at all four K. A group counts for a pair when it overlaps that
pair's region, in exactly the bins the prediction recurses over.

The tools are the shipped code: `_coact_count` plus the merge, cross-checked against `_clusters`
and against `assess_coactivity` itself, and `count_detect`. Each pair's **realized separation** is
also kept: the median of B's rounded onsets minus the median of A's.

## 4. Results

### Comparison (P(two), predicted / measured, n = 400 per cell; z in brackets where 0.005 < p < 0.995)

| tool | σ (s) | k | b (Hz) | K | Δ = 0.25 | 0.5 | 1 | 1.5 | 2 | 3 | 4 | 5 | 8 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| assessor | 0.105 | 7 | 0.0096 | 5 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.01 / 0.01 (−1.0) | 0.90 / 0.90 (+0.2) | 0.91 / 0.92 (+0.6) | 0.91 / 0.92 (+0.7) | 0.91 / 0.91 (+0.2) |
| assessor | 0.105 | 13 | 0.0096 | 5 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.90 / 0.90 (−0.7) | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| assessor | 0.5 | 7 | 0.0096 | 5 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.04 / 0.04 (−0.0) | 0.33 / 0.30 (−1.2) | 0.37 / 0.40 (+1.2) | 0.37 / 0.38 (+0.1) | 0.37 / 0.37 (−0.2) |
| assessor | 0.5 | 13 | 0.0096 | 5 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.01 / 0.00 (−1.5) | 0.57 / 0.59 (+0.9) | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| assessor | 0.105 | 7 | 0.05 | 8 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.38 / 0.39 (+0.3) | 0.38 / 0.37 (−0.5) | 0.38 / 0.41 (+0.9) | 0.38 / 0.38 (−0.0) |
| assessor | 0.105 | 13 | 0.05 | 8 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.01 / 0.01 (+0.4) | 0.95 / 0.96 (+0.8) | 0.99 / 0.99 (+1.1) | 0.99 / 0.97 (−2.0) | 0.99 / 0.99 (+1.1) |
| assessor | 0.5 | 7 | 0.05 | 8 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.01 | 0.03 / 0.03 (+0.6) | 0.03 / 0.03 (+0.3) | 0.03 / 0.03 (−0.3) | 0.03 / 0.02 (−1.3) |
| assessor | 0.5 | 13 | 0.05 | 8 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.01 | 0.06 / 0.04 (−1.0) | 0.67 / 0.66 (−0.5) | 0.80 / 0.80 (−0.2) | 0.80 / 0.77 (−1.4) | 0.80 / 0.81 (+0.7) |
| count | 0.105 | 7 | 0.0096 | 6 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.44 / 0.48 (+1.5) | 0.91 / 0.93 (+1.1) |
| count | 0.105 | 13 | 0.0096 | 6 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.47 / 0.48 (+0.6) | 1.00 / 1.00 |
| count | 0.5 | 7 | 0.0096 | 6 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.01 / 0.01 (−0.1) | 0.24 / 0.23 (−0.1) | 0.58 / 0.61 (+1.4) |
| count | 0.5 | 13 | 0.0096 | 6 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.01 / 0.01 (−0.2) | 0.35 / 0.40 (+2.1) | 1.00 / 1.00 |
| count | 0.105 | 7 | 0.05 | 12 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.01 | 0.01 / 0.01 (−0.0) |
| count | 0.105 | 13 | 0.05 | 12 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.44 / 0.43 (−0.4) | 0.91 / 0.91 (−0.3) |
| count | 0.5 | 7 | 0.05 | 12 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| count | 0.5 | 13 | 0.05 | 12 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.22 / 0.20 (−0.9) | 0.57 / 0.61 (+1.3) |

**P(at least one cluster)**, predicted / measured at Δ = 0.25, 2 and 8 s. Where it falls below 1,
the shortfall in P(two) is missed events, not merging.

| tool | σ | k | b | K | Δ 0.25 | Δ 2 | Δ 8 |
|---|---|---|---|---|---|---|---|
| assessor | 0.105 | 7 | 0.0096 | 5 | 1.00 / 1.00 | 0.98 / 0.98 | 0.98 / 0.98 |
| assessor | 0.5 | 7 | 0.0096 | 5 | 1.00 / 1.00 | 0.88 / 0.85 | 0.84 / 0.84 |
| assessor | 0.105 | 7 | 0.05 | 8 | 0.99 / 0.99 | 0.79 / 0.80 | 0.79 / 0.78 |
| assessor | 0.5 | 7 | 0.05 | 8 | 0.89 / 0.87 | 0.32 / 0.33 | 0.30 / 0.30 |
| assessor | 0.5 | 13 | 0.05 | 8 | 1.00 / 1.00 | 0.99 / 0.99 | 0.99 / 0.98 |
| count | 0.5 | 7 | 0.0096 | 6 | 1.00 / 1.00 | 0.99 / 0.99 | 0.87 / 0.89 |
| count | 0.105 | 7 | 0.05 | 12 | 0.87 / 0.90 | 0.18 / 0.15 | 0.16 / 0.16 |
| count | 0.5 | 7 | 0.05 | 12 | 0.68 / 0.68 | 0.17 / 0.15 | 0.09 / 0.09 |
| count | 0.5 | 13 | 0.05 | 12 | 1.00 / 1.00 | 0.98 / 0.97 | 0.85 / 0.85 |

The other seven rows are 0.97–1.00 at every Δ. Merging also *rescues* sub-threshold events:
P(at least one) is higher at Δ = 0.25 s than at 8 s, because two 7-cell events in one bin make 14
cells.

**Agreement over all 576 points** (2 tools × 4 K × 72 recordings). There are 277 points with
0.01 < P(two) < 0.99. Their z has mean −0.01 and SD 1.02, with 15 beyond |z| > 2 (13.9 expected)
and none beyond 3. The exact two-sided binomial test gives p < 0.01 at 4 of 576 points (5.8
expected). For P(at least one), 205 informative points have z mean −0.02 and SD 0.91.

### Separation at 50 %

The first column is where P(two) reaches 0.5; "–" means its plateau never reaches 0.5. The second
is where it reaches half its own plateau, which is the resolution with detection factored out.

| tool, K | σ (s) | k | b = 0.0096 Hz: Δ₅₀ / half-plateau Δ (plateau) | b = 0.05 Hz: Δ₅₀ / half-plateau Δ (plateau) |
|---|---|---|---|---|
| assessor, K = 5 / 8 | 0.105 | 7 | 2.56 / 2.51 s (0.90) | – / 2.53 s (0.36) |
| | 0.105 | 13 | 2.59 / 2.59 s (1.00) | 2.53 / 2.52 s (0.99) |
| | 0.5 | 7 | – / 2.51 s (0.37) | – / 2.51 s (0.03) |
| | 0.5 | 13 | 2.92 / 2.92 s (1.00) | 2.72 / 2.58 s (0.80) |
| count, K = floor 6 / 12 | 0.105 | 7 | 5.11 / 5.01 s (0.90) | – (plateau 0.007) |
| | 0.105 | 13 | 5.06 / 5.06 s (1.00) | 5.12 / 5.01 s (0.89) |
| | 0.5 | 7 | 5.64 / 5.07 s (0.53) | – (plateau 0.002) |
| | 0.5 | 13 | 5.30 / 5.30 s (1.00) | 5.64 / 5.08 s (0.52) |

The plateau is reached from about 3 s (assessor) and 6 s (count), and it equals f². The other K
values are in `split_output.txt`. They have the same half-plateau separations and different
plateaus.

### What sets what

- **Resolution comes from the tool: 2.5 bins.** The bin width and `merge_bins` set it. σ moves it
  only by about 0.3–0.4 s at σ = 0.5 s and k = 13: a wide cloud spills into the gap bins, and
  those must stay below K. k, b and K barely move it.
- **Detection comes from the data: the plateau f².** At the lab's background, K = 5, the assessor
  detects 7-cell events at σ = 0.105 s with f ≈ 0.95 (plateau 0.90). At σ = 0.5 s, f ≈ 0.6
  (plateau 0.37), because seven onsets spread over two to three bins seldom put five in one. At
  0.05 Hz and K = 8, 7-cell events reach the threshold only with background help, and the plateau
  falls to 0.36 and 0.03. At its floor of 12, the count detector never sees 7-cell events at
  0.05 Hz.
- **The ripple in the curves is real.** At large Δ, P(two) oscillates with period w, for
  example 0.33 to 0.38 for the assessor at σ = 0.105 s, k = 7 and 0.05 Hz. Detection depends on
  each cloud's phase against the bin edges. When Δ is a whole number of bins both events share
  that phase, f_A and f_B are positively correlated, and E[f_A f_B] > E[f]². At 2 s bins with
  σ = 0.5 s the ripple reaches ±0.05.
- **Bimodality is irrelevant to these tools.** 2σ is 0.21 s (lab) or 1 s. Both tools merge pairs
  far above that.

### Planned against realized separation

Realized separation (the difference of the medians) tracks planned separation closely. At
σ = 0.105 s its 5th–95th percentile is Δ ± 0.1 s. At σ = 0.5 s it is Δ ± 0.5 s, and it is ≤ 0 in
23 % of pairs at Δ = 0.25 s and 6 % at Δ = 0.5 s. Those are exactly the separations neither tool
splits at all, so **binning by realized separation leaves every curve where it was** (Figure,
E–H). The split rate in each realized bin equals the planned-Δ rate within error, because the
tools' transitions (2–3 s and 4–6 s) sit where the realized spread (±0.5 s at most) is a fraction
of the bin width. For the human rater sheet, where splitting may happen below 1 s, the two
abscissae will differ. That comparison should use realized separation. Per-bin rates are in
`split_output.txt`.

![P(two clusters) against separation](synth_recovery_plot_assessor-split-against-separation_20261025.png)

**Figure.** P(a planted pair is reported as two clusters), with one column per (jitter SD,
background).

- **A–D:** against the planned centre-to-centre separation. Lines are the exact prediction of §2.
  Filled points are the simulation (400 pairs each, ±1 binomial SE).
- **E–H:** the same pairs against the realized separation (median onset of B minus median onset of
  A), binned at the planned values. Open points, with the prediction lines faint for reference.
- **Colour, line and marker:** solid lines with circles are the assessor at K = 5 cells
  (0.0096 Hz) or 8 (0.05 Hz). Dashed lines with squares are the count detector at its ADR-0008
  floor, 6 or 12 cells. Colour is the participation, 7 or 13 of 33 cells.
- **Grey dotted line:** 2σ, below which the two onset clouds are unimodal.
- **Red dash-dot line:** 3.8 s, the 5th percentile of real fast-stream gaps.
- Points are offset ±0.09 s sideways for legibility.

## 5. Where the prediction fails, and why

- **In the first run it failed, and the fault was mine, not the model's.** The simulation counted
  groups over ±6 s around each pair for both tools, while the assessor's prediction covered
  ±3 one-second bins. At b = 0.05 Hz and K = 5–6, below the assessor's chance K of 8,
  chance clusters run at 8–36 per hour. The extra 6 s of
  window added about 0.1 to P(two) at small Δ and moved P(two) into P(≥ 3) at large Δ. Fifty of
  the 54 failing points came from it (z up to 9.6). Matching the windows bin for bin removed it.
  **The lesson carries to real data: below the chance K, "two clusters" depends on the counting
  window, so a split rate quoted there must state its window.**
- **After the fix, nothing fails systematically.** The four points at p < 0.01 are scattered over
  tools, K and Δ, with no sign pattern. The most extreme is the assessor at σ = 0.5 s, k = 13,
  b = 0.0096 Hz, K = 6, Δ = 1.5 s: predicted 2.5 × 10⁻⁴, measured 2 of 400 (p = 0.005). With 576
  tests, about 6 such points are expected.
- **What the prediction cannot see** (outside A1–A5):
  - Events with variable k.
  - Correlated jitter within an event, or skewed onset distributions. Real t50rise onsets are
    not Gaussian.
  - Heterogeneous or bursty background (`bg_rate_shape`, `bg_burst_shape`). φ then needs the
    Poisson-binomial tail.
  - A third event within the region.
  - Membership that is not random. Shared cells change X only when a cell's two onsets share a bin,
    which happens only at separations the tools merge anyway.
  - Any analysis window edge. `_coact_count` clips the last onset into the final bin.
  - Bins and merging other than the defaults. The gather argument needs `wm_factor` ≥ 1.5 and
    `merge_bins` ≤ 2. Outside that, the gather has to be added to the recursion.
- **The quadrature over phase** (32 points) is the only numerical approximation. It was not
  separately converged. The agreement above bounds its error well inside the simulation's SE
  (about 0.01–0.025).

## 6. What this means for the lab's data

- **Real gaps** come from `gaps.csv`, baseline windows of 66 recordings, sliding 2 s count at the
  ADR-0008 floor, with events closer than 2 s merged before gaps were taken. The fast stream has
  174 gaps, with the 5th percentile at 3.8 s. 1.7 % are under 3 s, 6.3 % under 4 s and 7.5 % under
  5 s. The slow stream's 5th percentile is 7.1 s, and 0.9 % are under 5 s. **Those gaps are
  themselves censored at about 2 s** by their own merge, so the true share of close pairs is at
  least this.
- **The assessor** resolves about 98 % of fast-stream gaps: those above about 3 s, its full-split
  point. That holds only where both events are detected. At the lab's σ and background, 7-cell
  events at K = 5 pass 95 % of the time each.
- **The count detector** at its shipped 2 s bins merges essentially every fast-stream pair under
  4 s (6.3 %) and half of those near 5 s. That is about 7 % of fast gaps and 1 % of slow ones. Its
  5 s resolution also sits right on the low tail of the slow stream. A 1 s bin would halve it
  (resolution 2.5 w), at the cost of the bin's chance floor.
- **For the coordination-rates prediction** (handoff item 2): pairs closer than one window w are
  read as one event. This note does not model that window, but the same automaton with a
  w-second bin and no merge would.

## Prior art

The 2w floor and the linear ramp to 3w are the binned-detector analogue of range resolution
in radar: two returns closer than one range cell plus the detector's merge rule are one target,
whatever their separation in signal space. Grün et al. 1999 derived the same "fission" geometry
for two onsets in disjoint bins. The two-Gaussian bimodality limit (Δ > 2σ for equal clouds) is a
bound on what any method could see in the onset density. These tools sit 10–25 times above it at
the lab's jitter. That gap is the room handoff item 3's likelihood bound would measure.
