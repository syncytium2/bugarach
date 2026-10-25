# How close can two coordinated events be and still be told apart?

The floor that detectors and human raters will be compared against: the smallest separation Δ
between two coordinated events that *any* method could resolve from onset times alone, under
the lab's jitter, participation, background rate and frame rate.

![Figure 1](synth_recovery_plot_separation-floor-any-method_20261025.png)

**Figure 1. The resolution floor against event size.** Panels **a–c** plot the resolvable separation
Δ against the number of cells per event *k*, for σ = 0.105 s (fast-stream jitter), 0.131 s
(slow-stream jitter) and 0.5 s, all at the lab's background, b = 0.0096 Hz per cell. Δ is the
centre-to-centre separation at which a test with 5 % false alarm calls the pair "two events".
Filled markers on solid lines give 80 % power; open markers on dashed lines give 50 % power.
- Blue circles: no cell identity (onsets pooled).
- Orange squares: cell identity, with the within-cell floor at one frame, which is the model as
  stated.
- Green triangles: cell identity, with the measured within-cell floor (0.4 s fast in a and c,
  3.2 s slow in b).
- Grey diamonds: the membership oracle, which knows which event every onset belongs to.

Points drawn on the bottom edge (0.035 s) mean the power is already reached at Δ = 0, from
shared cells alone. A missing point means the power was not reached on the simulated grid.
Grey horizontal lines, labelled at the right, mark the assessor's 3 s floor, the 5th-percentile
real inter-event gaps (3.8 s fast, 7.1 s slow), the 2σ unimodality boundary and the 0.1 s frame.
Panel **d** shows power against Δ at the lab's two operating points: fast (σ 0.105 s, 7 cells,
g 0.4 s) as solid lines and slow (σ 0.131 s, 13 cells, g 3.2 s) as dashed lines. Blue is pooled
onsets; green is cell identity. Every curve is 300 simulated pairs per Δ. Numbers are in
`bound_output.txt`; `bound.py` regenerates everything.

**The answer.** At the lab's parameters, the smallest separation any method can resolve with
80 % power at 5 % false alarm is:

| stream | 7 cells per event | 13 cells per event |
|---|---|---|
| fast (σ 0.105 s) | **0.44 s** | **0.26 s** |
| slow (σ 0.131 s) | **0.76 s** | **0.59 s** |

These use b = 0.0096 Hz and a 0.1 s frame. At 50 % power the floor is 0.19–0.58 s. In every case
the floor is about 2–6 σ, so the jitter sets it, not the frame.

That is roughly **one-fifth to one-tenth of the assessor's 3 s floor**. It is also far below the
real 5th-percentile inter-event gaps of 3.8 s (fast) and 7.1 s (slow). Without cell identity
the floor is 0.61 s in both streams.

Cell identity helps only through cells recruited by both events. Those cells must also fire
twice, which real cells cannot do inside their within-cell floor (0.4 s fast, 3.2 s slow). So
identity lowers the fast floor by about 0.2 s and leaves the slow floor almost unchanged. §6 has
the comparison.

---

## 1. Model and symbols

| symbol | meaning | values used |
|---|---|---|
| N | cells imaged | 33 cells |
| k | cells recruited per event (k_A = k_B = k) | 5, 7, 10, 13, 20 cells |
| Δ | separation between the two event centres | the unknown |
| σ | jitter: SD of a participant's onset about its event centre | 0.105, 0.131, 0.5 s |
| σ′ | jitter of the one-event alternative, a free parameter | fitted |
| b | independent Poisson background, per cell | 0, 0.0096, 0.05 Hz |
| h | frame: onsets are rounded to multiples of h | 0.1 s |
| g | within-cell floor: a cell's onset closer than g to its previous onset is not seen | 0.1 s (one frame), 0.4 s, 3.2 s |
| S | number of cells recruited by both events | hypergeometric |
| α, 1−β | false-alarm rate, power | 5 %; 50 % and 80 % |
| n | pooled onsets, n = 2k in the clean case | |

Each event draws its k cells uniformly at random from the N cells, independently of the other
event, so the two memberships can overlap. A participant's onset is the event centre plus
N(0, σ²). Onsets are rounded to frames. Every cell also emits background onsets at rate b.

The null hypothesis H0 is a single event whose members are the union of the two memberships,
with free centre and free jitter σ′. The alternative H1 is two events, Δ apart.

**The within-cell floor g is an addition to the model as posed, and it decides one of the
answers.** As posed, a cell in both events contributes two onsets Δ apart. A real onset
extractor cannot emit two onsets closer than the cell's shortest within-cell interval. The repo
measured that interval in the senktide baseline windows at **0.40 s fast and 3.20 s slow** (2.80 s
slow on the field-step-excluded folder); see the 2026-09-10 coordination-without-labels review.
So I report three values of g: one frame (0.1 s, the model as stated), 0.4 s and 3.2 s.

"Resolvable Δ" (Δ₅₀, Δ₈₀) is the smallest separation at which the test reaches 50 % or 80 %
power, with the false-alarm rate held at 5 %.

## 2. The clean case: two Gaussian bursts, labels unknown

Take b = 0, no rounding, disjoint memberships, and discard cell labels. The data are then n = 2k
draws from

  f(t) = ½ φ_σ(t − c + Δ/2) + ½ φ_σ(t − c − Δ/2),

and the question is whether f has one component or two. The results scale with σ, so this
section works in units of σ.

### 2.1 The classical result: unimodal for Δ ≤ 2σ

An equal-weight, equal-variance two-Gaussian mixture is unimodal if and only if Δ ≤ 2σ
(Robertson & Fryer 1969; Behboodian 1970; restated for applied readers by Schilling, Watkins &
Watkins 2002). At the lab's jitters 2σ is **0.21 s fast and 0.26 s slow**.

The 2σ rule is a statement about the density, not about a sample. With k ≤ 20 cells, a test
detects a pair at exactly Δ = 2σ only 6–10 % of the time, against 5 % at Δ = 0. With 200 cells
per event it would detect 72 %. A visible dip is not the limit, and its absence is not one
either.

### 2.2 Why the information vanishes near Δ = 0, and the closed forms

Write the onset as X = c + σZ + (Δ/2)·ε, with ε = ±1 equally likely. The cumulants of X are

  κ₁ = c,  κ₂ = σ² + Δ²/4,  κ₃ = 0,  κ₄ = (Δ/2)⁴·κ₄(ε) = −Δ⁴/8.

H0 has a free centre and a free σ′, so it matches κ₁ and κ₂ exactly. κ₃ vanishes by symmetry. The
first cumulant H0 cannot copy is κ₄. Equivalently, the score for Δ is identically zero at
Δ = 0, and so is the score for Δ² once σ′ is free. The Fisher information about Δ is zero at the
boundary. That singularity is why the textbook χ² asymptotics fail (§2.3), and why the
resolvable Δ shrinks only slowly with sample size.

**σ′ free, which is the model's null.** The excess kurtosis of the mixture is

  γ₂ = −2r⁴ / (1 + r²)²,  r = Δ / (2σ).

Under H0 the sample excess kurtosis is asymptotically N(0, 24/n). A one-sided kurtosis test
reaches power 1−β where

  2r⁴ / (1 + r²)² = (z_α + z_β)·√(24/n),

and for small r this gives

  **Δ ≈ 2σ·[(z_α + z_β)·√6]^{1/4}·n^{−1/8}**, which is 3.14 σ·n^{−1/8} at 80 % power.

The rate is n^{−1/8}. Halving the resolvable Δ takes 256 times as many cells. This is the
known slow rate for over-fitted mixtures when the first two moments are absorbed by the null
(Chen 1995 gives the n^{−1/4} rate for strongly identifiable families; Ho & Nguyen 2016 treat
the weakly identifiable Gaussian location–scale case).

The closed form is **not usable at the lab's sizes**. It needs √(24/n) small, but at n ≤ 40
onsets the asymptotic variance 24/n overstates the true small-sample variance of the kurtosis
several-fold. The formula then returns no solution or a large overestimate (Table 1, "kurt.
closed"). Simulation gives the actual numbers.

**σ known in advance (not the model's null; for reference).** If the jitter were known, κ₂
would already be informative. The variance test n·s²/σ² ~ χ²_{n−1} then gives

  Δ ≈ 2σ·(z_α + z_β)^{1/2}·2^{1/4}·n^{−1/4}, about 3.75 σ·n^{−1/4} at 80 % power.

This closed form matches simulation to within 0.2 σ from n = 20 onsets up (Table 1). It
overstates Δ by up to 0.5 σ at n = 10. The
imaging and radar resolution limits in §7 are this case: their point-spread function is known.
The lab does measure σ (0.105 / 0.131 s), but as an average over events. Treating it as known
for each event would be an assumption the model does not grant.

### 2.3 The likelihood-ratio test and its non-standard asymptotics

The natural general test is the likelihood ratio (LR) of one Gaussian against a two-component
mixture with common variance. Its asymptotics are non-standard:

- **Hartigan (1985).** With unrestricted means, 2 log LR under H0 diverges in probability, like
  log log n (Bickel & Chernoff 1993).
- **Compact parameter spaces.** There the limit is the supremum of a squared Gaussian process,
  not χ² (Dacunha-Castelle & Gassiat 1999; Chen & Chen 2001).
- **Common variance unknown.** In this "structural parameter" case, Chen & Chen (2003) and Qin &
  Smith (2004) obtain a 50:50 mixture of χ²₁ and χ²₂ for the ordinary and modified LR.
  Its 95th percentile is 5.14.

The simulated 95th percentiles at the lab's sizes are far from any limit. With free weights they
are 7.82 at n = 10, 6.81 at n = 40 and 5.91 at n = 400 onsets. With weights fixed at ½ they are
6.05, 3.89 and 3.12. Every test here is therefore calibrated by simulating the null (a
parametric bootstrap, as McLachlan 1987 recommends for mixture LR tests), never by a χ² table.

### 2.4 Table 1: clean-case resolvable Δ/σ

At 5 % false alarm, from simulation (10 000 null and 1 000 alternative samples per point for
k ≤ 20 cells; half that above). Grid step 0.5 σ, with linear interpolation.

| k (cells/event) | n | LR, free weights 50 % / 80 % | LR, equal weights | kurtosis test | kurtosis closed form | σ known: variance test | σ known: closed form |
|---|---|---|---|---|---|---|---|
| 5 | 10 | 4.69 / 5.88 | 4.18 / 5.26 | 3.83 / 4.93 | >max / >max | 1.81 / 2.45 | 2.03 / 2.93 |
| 7 | 14 | 4.07 / 5.09 | 3.66 / 4.53 | 3.50 / 4.42 | >max / >max | 1.69 / 2.26 | 1.80 / 2.52 |
| 10 | 20 | 3.69 / 4.43 | 3.24 / 3.95 | 3.16 / 3.92 | 8.64 / >max | 1.54 / 2.01 | 1.60 / 2.19 |
| 13 | 26 | 3.39 / 4.10 | 2.93 / 3.69 | 2.91 / 3.75 | 5.66 / >max | 1.41 / 1.89 | 1.48 / 1.99 |
| 20 | 40 | 3.02 / 3.59 | 2.59 / 3.22 | 2.64 / 3.33 | 3.98 / 14.50 | 1.27 / 1.72 | 1.30 / 1.72 |
| 50 | 100 | 2.35 / 2.80 | 2.15 / 2.48 | 2.18 / 2.64 | 2.64 / 3.77 | 0.96 / 1.30 | 1.01 / 1.29 |
| 100 | 200 | 2.07 / 2.41 | 1.84 / 2.26 | 1.87 / 2.30 | 2.14 / 2.76 | 0.77 / 1.05 | 0.84 / 1.06 |
| 200 | 400 | 1.78 / 2.15 | 1.64 / 1.93 | 1.66 / 1.98 | 1.80 / 2.22 | 0.70 / 0.91 | 0.70 / 0.87 |

Three findings:

- **At the lab's sizes, two Gaussian bursts with unknown labels are resolved at 80 % power only
  beyond about 4.4–4.5 σ (7 cells) or 3.7 σ (13 cells).** That is 0.46 s fast and 0.48 s slow
  for the best clean test, before background, rounding or cell identity.
- **The free-weight LR is not the most powerful test.** The equal-weight LR and the kurtosis
  test both use the known symmetry and gain 0.5–0.7 σ at small k.
- **The rate check matches the theory.** Δ₈₀·n^{1/8} (σ′ free) still falls from 7.8 to 4.5 at
  n = 400, slowly approaching the asymptotic 3.14. Δ₈₀·n^{1/4} (σ known) is flat at 4.0–4.4.

## 3. Cell identity

### 3.1 Shared cells: direct evidence of two events

The two memberships are independent uniform k-subsets of N cells. The number of shared cells S
is then hypergeometric(N, k, k), with E[S] = k²/N and

  P(S ≥ 1) = 1 − C(N−k, k)/C(N, k) ≈ 1 − (1 − k/N)^k.

| k (cells/event) | P(S ≥ 1) exact | 1 − (1 − k/N)^k | E[S] = k²/N |
|---|---|---|---|
| 5 | 0.586 | 0.560 | 0.76 |
| 7 | 0.846 | 0.812 | 1.48 |
| 10 | 0.988 | 0.973 | 3.03 |
| 13 | 1.000 | 0.999 | 5.12 |
| 20 | 1.000 | 1.000 | 12.12 |

Under H0 every cell has at most one event onset. **With no background, a cell showing two onsets
is impossible under H0.** Such a cell rejects H0 with zero false alarm, at any Δ.

A shared cell's two onsets differ by D ~ N(Δ, 2σ²). The second onset is seen when |D| ≥ g, so

  P_seen(Δ) = Φ((Δ − g)/(σ√2)) + Φ((−Δ − g)/(σ√2)),

  power_shared(Δ) = 1 − Σ_s P(S = s)·(1 − P_seen(Δ))^s.

Its ceiling as Δ → ∞ is P(S ≥ 1). So for k = 5 cells, sharing alone can never reach 80 %.

Resolvable Δ (s), 50 % / 80 % power, from shared cells alone at b = 0 (closed form, `bound_output.txt` §2b):

| σ (s) | g (s) | k = 5 | k = 7 | k = 10 | k = 13 | k = 20 |
|---|---|---|---|---|---|---|
| 0.105 | 0.1 | 0.22 / >max | any / 0.28 | any / any | any / any | any / any |
| 0.105 | 0.4 | 0.53 / >max | 0.37 / 0.58 | 0.28 / 0.39 | 0.23 / 0.32 | 0.16 / 0.23 |
| 0.131 | 0.1 | 0.24 / >max | any / 0.31 | any / any | any / any | any / any |
| 0.131 | 3.2 | 3.36 / >max | 3.17 / 3.43 | 3.05 / 3.18 | 2.99 / 3.09 | 2.91 / 2.99 |
| 0.5 | 0.1 | any / >max | any / 0.12 | any / any | any / any | any / any |
| 0.5 | 0.4 | 0.96 / >max | any / 1.22 | any / any | any / any | any / any |
| 0.5 | 3.2 | 3.83 / >max | 3.07 / 4.06 | 2.64 / 3.14 | 2.40 / 2.80 | 2.08 / 2.39 |

**This is where the model as posed misleads.** With g = one frame, shared cells give 50 % power
at Δ = 0 for k ≥ 7 cells, and 80 % for k ≥ 10. The "two events" are then told apart while
coinciding, purely because one cell fired twice inside a jitter width. Real cells cannot do
that.

With the measured floors the shared-cell route only opens once Δ is past g:
- **fast** (g = 0.4 s): Δ₈₀ is 0.58 s at 7 cells and 0.32 s at 13 cells;
- **slow** (g = 3.2 s): Δ₈₀ is 3.43 s at 7 cells and 3.09 s at 13 cells.

In the slow stream, the measured within-cell floor of 3.2 s is itself longer than the assessor's
3 s floor.

### 3.2 Membership differences carry no information by themselves

Suppose memberships are drawn fresh and at random for every event, and no cell is shared. Then
the cells in A and the cells in B form a uniformly random partition of the participants. It is
independent of the onset times, and has the same law as a random subset of the union under
H0. The likelihood ratio does not depend on which cells fired, only on when. **Membership
lowers the floor only through shared cells (§3.1), or through knowledge of membership from
outside the pair.**

The simulation confirms this. With memberships forced disjoint (σ 0.131 s, 7 cells, b 0.0096 Hz),
the per-cell identity test and the pooled test have the same resolvable Δ (§5, "membership-only
check").

Outside knowledge would be, for example, recurring ensembles: cells that reliably fire together
across many events. That information is not in the onset times of the pair. Its maximum value is
the **membership oracle**, a two-sample t test on onsets labelled by event:

  Δ ≈ (t_{α/2, 2k−2} + z_β)·√(σ² + h²/12)·√(2/k)  (exact noncentral-t value in `bound.py`).

The oracle resolves Δ₈₀ = 0.18 s fast (7 cells) and 0.15 s slow (13 cells). Perfect ensemble
knowledge would lower the floor three- to four-fold. The pairs do not supply it.

## 4. Background and the 0.1 s frame

### 4.1 Background

**Pooled onsets.** Background adds a flat intensity N·b to the pooled onset process, which is
0.32 onsets/s at the lab's 0.0096 Hz per cell. The pooled likelihood becomes that of a Poisson
process,

  λ(t) = N·b + a_A·φ_σ(t − c_A) + a_B·φ_σ(t − c_B)  against  N·b + a·φ_σ′(t − c).

Its log is Σᵢ log λ(tᵢ) − ∫λ, which `bound.py` maximises by EM with b known. Within ±2σ′ of
the pair, the expected number of chance onsets is 4σ′·N·b:
- at b = 0.0096 Hz, about 0.17 onsets (σ′ = 0.13 s) to 0.6 onsets (σ′ = 0.5 s), against 2k event
  onsets — a small cost;
- at b = 0.05 Hz, 0.9 to 3.3 onsets, which costs real power at small k and large σ.

The background also makes the null harder to fit. A single burst can latch onto one cluster and
explain the other as background, so the fit needs starts from both dense regions. An early run
missed this, and its power stalled at 0.9 for Δ = 3 s; this run fixes it.

**Shared cells.** With b > 0 a cell can show two onsets under H0: its event onset plus a chance
one. In a window of length L the expected number of such cells is about m·b·L, where m is the
number of participants:

  13 participants (k = 7) × 0.0096 Hz × 12 s ≈ 1.5 cells.

**So one doubly-firing cell is no longer significant evidence by itself.** The evidence must come
from several shared cells whose second onsets agree in time with each other, and with the
second burst in the pooled onsets. Chance onsets are uniform in time. For two of them to agree
within ±2σ has probability about (m choose 2)·(bL)²·4σ/L, roughly 0.01. The per-cell likelihood
in `bound.py` carries this weighting automatically: background, membership, and the possibility
that a shared cell's two onsets merged under the floor g.

### 4.2 The frame

Rounding to h = 0.1 s does three things:

1. **It adds variance h²/12 (Sheppard's correction).** The effective jitter becomes 0.109 s
   (fast) and 0.135 s (slow). This is negligible for every test whose floor is several σ.
2. **It sets a hard floor on the shared-cell route.** Two onsets of one cell in the same frame
   are one onset, so g ≥ h whatever the indicator does.
3. **It sets a hard floor on any test when σ ≪ h.** All onsets then fall in one or two frames,
   and a Δ below h moves no onset with probability about 1 − Δ/h.

At the lab's jitters σ ≈ h, so the jitter dithers the rounding. Even the oracle resolves Δ₈₀ ≈
0.10–0.15 s at 20 cells, and no unlabelled test comes near h. **The frame is a hard floor only for
the shared-cell route. For the population tests the binding limit is the jitter, at several σ.**

## 5. Table 2: the full model

Resolvable Δ in seconds, at 5 % false alarm, 50 % / 80 % power. Each entry is 300 simulated
pairs per Δ, with 1 200 null pairs at each of 7 null jitters σ′.

- **pooled**: LR with cell labels discarded.
- **id g**: per-cell LR, with within-cell floor g.
- **oracle**: membership known.
- **any**: the power is reached at Δ = 0, from shared cells.
- **>max**: not reached on the grid, which runs to 16σ or 4 s, whichever is larger.

The floor for any method is the smaller of the pooled and identity columns at the relevant g.
The oracle is what outside membership knowledge could add.

**σ = 0.105 s, b = 0.0 Hz per cell**

| k (cells/event) | pooled | id, g = 0.1 s | id, g = 0.4 s | id, g = 3.2 s | oracle | P(S ≥ 1) |
|---|---|---|---|---|---|---|
| 5 | 0.55 / 0.68 | 0.13 / 0.48 | 0.36 / 0.53 | – | 0.15 / 0.22 | 0.586 |
| 7 | 0.46 / 0.57 | any / 0.15 | 0.26 / 0.42 | – | 0.12 / 0.18 | 0.846 |
| 10 | 0.39 / 0.48 | any / any | 0.21 / 0.32 | – | 0.10 / 0.14 | 0.988 |
| 13 | 0.37 / 0.45 | any / any | 0.15 / 0.26 | – | 0.09 / 0.12 | 1.000 |
| 20 | 0.34 / 0.40 | any / any | 0.10 / 0.18 | – | 0.07 / 0.10 | 1.000 |

**σ = 0.105 s, b = 0.0096 Hz per cell**

| k (cells/event) | pooled | id, g = 0.1 s | id, g = 0.4 s | id, g = 3.2 s | oracle | P(S ≥ 1) |
|---|---|---|---|---|---|---|
| 5 | 0.56 / 0.75 | 0.42 / 0.58† | 0.45 / 0.64 | – | 0.15 / 0.22 | 0.586 |
| 7 | 0.51 / 0.61 | any / 0.42 | 0.33 / 0.44 | – | 0.12 / 0.18 | 0.846 |
| 10 | 0.47 / 0.55 | any / any | 0.25 / 0.34 | – | 0.10 / 0.14 | 0.988 |
| 13 | 0.42 / 0.48 | any / any | 0.19 / 0.26 | – | 0.09 / 0.12 | 1.000 |
| 20 | 0.36 / 0.43 | any / any | 0.12 / 0.19 | – | 0.07 / 0.10 | 1.000 |

**σ = 0.105 s, b = 0.05 Hz per cell**

| k (cells/event) | pooled | id, g = 0.1 s | id, g = 0.4 s | id, g = 3.2 s | oracle | P(S ≥ 1) |
|---|---|---|---|---|---|---|
| 5 | 0.74 / 2.30 | 0.61 / 1.10† | 0.62 / 0.98† | – | 0.15 / 0.22 | 0.586 |
| 7 | 0.56 / 0.72 | 0.37 / 0.60† | 0.41 / 0.60† | – | 0.12 / 0.18 | 0.846 |
| 10 | 0.47 / 0.57 | any / 0.28† | 0.30 / 0.40† | – | 0.10 / 0.14 | 0.988 |
| 13 | 0.44 / 0.51 | any / any | 0.25 / 0.31 | – | 0.09 / 0.12 | 1.000 |
| 20 | 0.37 / 0.44 | any / any | 0.17 / 0.23 | – | 0.07 / 0.10 | 1.000 |

**σ = 0.131 s, b = 0.0 Hz per cell**

| k (cells/event) | pooled | id, g = 0.1 s | id, g = 0.4 s | id, g = 3.2 s | oracle | P(S ≥ 1) |
|---|---|---|---|---|---|---|
| 5 | 0.63 / 0.81 | any / 0.57 | – | 0.61 / 0.79 | 0.19 / 0.27 | 0.586 |
| 7 | 0.55 / 0.69 | any / 0.19 | – | 0.54 / 0.65 | 0.15 / 0.22 | 0.846 |
| 10 | 0.50 / 0.60 | any / any | – | 0.47 / 0.59 | 0.12 / 0.18 | 0.988 |
| 13 | 0.45 / 0.56 | any / any | – | 0.45 / 0.57 | 0.11 / 0.15 | 1.000 |
| 20 | 0.41 / 0.48 | any / any | – | 0.47 / 0.56 | 0.09 / 0.12 | 1.000 |

**σ = 0.131 s, b = 0.0096 Hz per cell**

| k (cells/event) | pooled | id, g = 0.1 s | id, g = 0.4 s | id, g = 3.2 s | oracle | P(S ≥ 1) |
|---|---|---|---|---|---|---|
| 5 | 0.72 / 0.96 | 0.45 / 0.79 | – | 0.73 / 0.90 | 0.19 / 0.27 | 0.586 |
| 7 | 0.64 / 0.77 | any / 0.53 | – | 0.58 / 0.76 | 0.15 / 0.22 | 0.846 |
| 10 | 0.55 / 0.66 | any / any | – | 0.48 / 0.64 | 0.12 / 0.18 | 0.988 |
| 13 | 0.50 / 0.61 | any / any | – | 0.48 / 0.59 | 0.11 / 0.15 | 1.000 |
| 20 | 0.44 / 0.51 | any / any | – | 0.50 / 0.62 | 0.09 / 0.12 | 1.000 |

**σ = 0.131 s, b = 0.05 Hz per cell**

| k (cells/event) | pooled | id, g = 0.1 s | id, g = 0.4 s | id, g = 3.2 s | oracle | P(S ≥ 1) |
|---|---|---|---|---|---|---|
| 5 | 0.87 / >max | 0.76 / 1.90† | – | 1.16 / >max† | 0.19 / 0.27 | 0.586 |
| 7 | 0.70 / 0.90 | 0.52 / 0.77† | – | 0.76 / 1.43† | 0.15 / 0.22 | 0.846 |
| 10 | 0.59 / 0.71 | any / 0.41† | – | 0.62 / 0.85† | 0.12 / 0.18 | 0.988 |
| 13 | 0.53 / 0.64 | any / any | – | 0.55 / 0.72† | 0.11 / 0.15 | 1.000 |
| 20 | 0.45 / 0.52 | any / any | – | 0.56 / 0.71 | 0.09 / 0.12 | 1.000 |

**σ = 0.5 s, b = 0.0 Hz per cell**

| k (cells/event) | pooled | id, g = 0.1 s | id, g = 0.4 s | id, g = 3.2 s | oracle | P(S ≥ 1) |
|---|---|---|---|---|---|---|
| 5 | 2.40 / 3.03 | any / 2.31 | 0.78 / 2.24 | 2.14 / 2.84 | 0.71 / 1.01 | 0.586 |
| 7 | 2.07 / 2.62 | any / any | any / 1.18 | 1.89 / 2.33 | 0.57 / 0.82 | 0.846 |
| 10 | 1.80 / 2.24 | any / any | any / any | 1.72 / 2.18 | 0.46 / 0.66 | 0.988 |
| 13 | 1.76 / 2.10 | any / any | any / any | 1.64 / 1.97 | 0.40 / 0.57 | 1.000 |
| 20 | 1.53 / 1.85 | any / any | any / any | 1.66 / 2.00 | 0.32 / 0.46 | 1.000 |

**σ = 0.5 s, b = 0.0096 Hz per cell**

| k (cells/event) | pooled | id, g = 0.1 s | id, g = 0.4 s | id, g = 3.2 s | oracle | P(S ≥ 1) |
|---|---|---|---|---|---|---|
| 5 | 3.33 / 5.36† | 2.73 / 4.76† | 2.84 / 5.00† | 3.00 / 4.91† | 0.71 / 1.01 | 0.586 |
| 7 | 2.53 / 3.41† | 1.51 / 2.83† | 1.71 / 2.65† | 2.38 / 3.22† | 0.57 / 0.82 | 0.846 |
| 10 | 2.00 / 2.53 | any / 1.18 | any / 1.27 | 1.94 / 2.41 | 0.46 / 0.66 | 0.988 |
| 13 | 1.83 / 2.23 | any / any | any / any | 1.74 / 2.20 | 0.40 / 0.57 | 1.000 |
| 20 | 1.59 / 1.90 | any / any | any / any | 1.74 / 2.16 | 0.32 / 0.46 | 1.000 |

**σ = 0.5 s, b = 0.05 Hz per cell**

| k (cells/event) | pooled | id, g = 0.1 s | id, g = 0.4 s | id, g = 3.2 s | oracle | P(S ≥ 1) |
|---|---|---|---|---|---|---|
| 5 | >max / >max | >max / >max | >max / >max | >max / >max | 0.71 / 1.01 | 0.586 |
| 7 | 6.88 / >max† | 4.07 / >max† | 3.84 / >max† | >max / >max† | 0.57 / 0.82 | 0.846 |
| 10 | 2.62 / 3.75† | 2.06 / 3.28† | 2.14 / 2.99† | 2.77 / 3.97† | 0.46 / 0.66 | 0.988 |
| 13 | 2.22 / 2.82† | any / 1.73† | 0.31 / 1.75† | 2.47 / 3.29† | 0.40 / 0.57 | 1.000 |
| 20 | 1.70 / 1.99† | any / any† | any / any† | 2.32 / 3.14† | 0.32 / 0.46 | 1.000 |

**Membership-only check.** σ 0.131 s, 7 cells, b 0.0096 Hz, g 0.1 s:
- memberships forced disjoint: pooled 0.63 / 0.78 s, identity 0.61 / 0.78 s;
- random (overlapping) memberships: pooled 0.64 / 0.77 s, identity any / 0.53 s.

Identity gains nothing unless cells are shared (§3.2).

The identity test is not uniformly better than the pooled one. Its per-cell model is an
approximation: for example, the merged-onset term places the surviving onset by a mixture. At
g = 3.2 s with 20 cells it is worse (0.50 / 0.62 s against 0.44 / 0.51 s). Hence "the floor is
the better of the two".

## 6. The floor at the lab's parameters, and how it compares

**The floor.** The resolvable separation at 5 % false alarm, using the better of the pooled
and cell-identity tests. Within-cell floor g = 0.4 s fast, 3.2 s slow; b = 0.0096 Hz per cell.

| stream (σ) | k = 7 cells: Δ₅₀ / Δ₈₀ | k = 13 cells: Δ₅₀ / Δ₈₀ | what sets it |
|---|---|---|---|
| fast (0.105 s) | **0.33 / 0.44 s** | **0.19 / 0.26 s** | shared cells firing twice, once Δ clears 0.4 s |
| slow (0.131 s) | **0.58 / 0.76 s** | **0.48 / 0.59 s** | the burst shape (pooled onsets); shared cells cannot help below 3.2 s |

Without cell identity, using onset times alone, the floor is 0.51 / 0.61 s (fast, 7 cells) and
0.50 / 0.61 s (slow, 13 cells). **In round numbers, no method can split two lab-like events whose
centres are closer than about 0.2–0.6 s.** At about 0.25–0.75 s a good method splits them 4
times in 5. That is 2–6 σ, set by the jitter, not by the frame.

The model taken literally (g = one frame) gives a lower floor, often "any" in Table 2. That
number is an artefact of letting one cell fire twice within a jitter width (§3.1).

**Against the assessor's floor (about 3 s).** The assessor bins at 1 s and merges clusters
within 2 bins, so it cannot score two events closer than about 3 s as two. That is **4–12 times
the information floor**. At Δ = 1 s the pooled test alone already has power 0.97–1.00 at 7 or
more cells per event, at either jitter. Between about 0.6 s and 3 s, then, a detector or rater
could in principle split pairs that the assessor will score as one. A detector that does so
would be marked down for it. The assessor's floor is a property of the scoring, not of the
data, and any comparison in that band measures the scoring.

**Against the real inter-event gaps.** The 5th-percentile gap is 3.8 s fast and 7.1 s slow, which
is 9–15 times the 80 % floor (0.26–0.76 s). Pairs near the floor are therefore rare in the real
recordings. Fewer than 5 % of gaps fall below 3.8 s, and only a small fraction of those come
near 1 s. Neither the floor nor the assessor will often bind on real data.

Where they do bind, the order is the information floor (0.2–0.8 s), then the assessor
(about 3 s), then the shortest common real gaps (3.8 s and 7.1 s). The slow stream's measured
within-cell floor (3.2 s) falls, by coincidence, at the assessor's floor. In the slow stream,
shared cells add no evidence for pairs the assessor could score.

**For σ = 0.5 s** (a much looser event) the floor rises to 1.6–3.4 s at 80 % power and the lab's
background (Table 2). That sits at or above the assessor's floor for k ≤ 7 cells.

## 7. Radar, imaging and seismology

- **Radar range resolution.** The textbook range resolution c/(2B), the matched-filter width,
  is a Rayleigh-type criterion. It is the analogue of the 2σ unimodality rule (§2.1), not a
  statistical bound.
- **Statistical resolution limits.** The directly usable results come from statistical
  resolution in radar, array processing and imaging:
  - Smith (2005) defines the resolution limit as the separation at which the Cramér–Rao bound
    on the separation equals the separation.
  - Shahram & Milanfar (2004) pose it, as this note does, as a test of one source against two
    and derive the minimum detectable separation at given SNR.
  - Kulaitis, Munk & Werner (2021) treat Poisson point data (photon counts), which is the closest
    analogue to onsets. They give minimax detection boundaries for "one object or two of the
    same total intensity".

  All three assume a **known point-spread function**. In that setting the second moment is
  informative, and the minimum separation scales as SNR^{−1/4}, equivalently n^{−1/4} in counts.
  That is exactly the σ-known column of Table 1, whose closed form matches simulation from about 20 onsets up. These
  results transfer as they stand only if each event's jitter is treated as known. With σ′ free,
  as the model specifies, the second moment is absorbed and the rate drops to n^{−1/8} (§2.2).
  The radar and imaging literature does not cover that case, because there the PSF is a property
  of the instrument.
- **Seismology.** For overlapping arrivals, the classical vertical-resolution criteria are
  Rayleigh's λ/4 and Widess's λ/8 for thin beds (Widess 1973; Kallweit & Wood 1982).
  They are deterministic waveform-interference limits for a known wavelet. Catalogue-level
  separation of overlapping earthquakes relies on waveform cross-correlation (template matching),
  not on arrival times alone. **No seismological result gives a usable onset-times-only bound**
  for this problem. The nearest equivalent is again the known-wavelet n^{−1/4} regime above.

## 8. Method, checks and limits

- **Tests.** There are three:
  - pooled: Poisson-process EM, two bursts against one on a known flat background, free
    amplitudes, common jitter floored at 0.05 s, several starts including both densest points;
  - identity: per-cell mixture over roles (A only, B only, both seen, both merged under g,
    background), with Bernoulli membership p (H1) or q (H0) free, background known, EM over
    two starts;
  - oracle: exact noncentral t.
- **Calibration.** Critical values come from simulating the null at 7 values of σ′, from σ up to
  √(σ² + Δ_max²/4). The value applied to a dataset is the largest null 95th percentile over σ′
  within a factor 2 of the fitted one-event jitter, a Berger & Boos (1994) style supremum over a
  nuisance neighbourhood. The realised false-alarm rate is reported per condition ("size"). It is
  within simulation error of 5 % for the pooled test at σ ≤ 0.131 s. It is also within error for the identity test at the lab's background, at worst 0.077. It is inflated (above 0.075; marked † in Table 2) at σ = 0.5 s with background and few cells, where it reaches 0.10–0.27. Those entries are optimistic. The size check reuses the calibration nulls, so the values of exactly 0.050 are in-sample.
- **Optimality.** These are likelihood-ratio tests of the stated model, calibrated exactly. They
  are not proven uniformly most powerful; none exists for this composite problem. Table 1 shows
  the free-weight LR losing to simpler symmetric tests by ~0.6 σ at small k. The floors are
  therefore attainable values, an upper bound on the true floor, within a few tenths of σ of it
  in the clean case.
- **Truncation.** Cells with more than 4 onsets in the 12 s window keep the 4 nearest the window
  centre (0.06 % of simulated cells, almost all at b = 0.05 Hz).
- **Δ grid.** 0 to 6σ in 0.5σ steps, then 7σ to 16σ in 1σ steps, plus 0.2–4.0 s in 0.3 s steps.
  Resolvable Δ is linearly interpolated on the running maximum of the power curve. With 300
  pairs per point, the power SE is ≤ 0.03.
- **Not modelled.** These all make real data harder, so the floor stays a floor:
  - events with different k_A ≠ k_B (the free-weight test covers this);
  - jitter that differs between the two events;
  - onset-detection misses;
  - a third event nearby.

Reproduce with `python bound.py`. It takes about 80 min on 24 cores; `--quick` runs a smoke test and
`--figure` redraws the figure from the saved results. It writes
`bound_output.txt`, `bound_results.json` and `synth_recovery_plot_separation-floor-any-method_20261025.png`.

## References

- Behboodian, J. (1970). On the modes of a mixture of two normal distributions. *Technometrics* 12, 131–139.
- Berger, R. L. & Boos, D. D. (1994). P values maximized over a confidence set for the nuisance parameter. *JASA* 89, 1012–1016.
- Bickel, P. J. & Chernoff, H. (1993). Asymptotic distribution of the likelihood ratio statistic in a prototypical non regular problem. In *Statistics and Probability: A Raghu Raj Bahadur Festschrift*, 83–96.
- Chen, H. & Chen, J. (2001). The likelihood ratio test for homogeneity in finite mixture models. *Canadian Journal of Statistics* 29, 201–215.
- Chen, H. & Chen, J. (2003). Tests for homogeneity in normal mixtures in the presence of a structural parameter. *Statistica Sinica* 13, 351–365.
- Chen, J. (1995). Optimal rate of convergence for finite mixture models. *Annals of Statistics* 23, 221–233.
- Dacunha-Castelle, D. & Gassiat, E. (1999). Testing the order of a model using locally conic parametrization. *Annals of Statistics* 27, 1178–1209.
- Hartigan, J. A. (1985). A failure of likelihood asymptotics for normal mixtures. In *Proceedings of the Berkeley Conference in Honor of Jerzy Neyman and Jack Kiefer*, vol. II (L. Le Cam & R. A. Olshen, eds.), 807–810. Wadsworth.
- Ho, N. & Nguyen, X. (2016). Convergence rates of parameter estimation for some weakly identifiable finite mixtures. *Annals of Statistics* 44, 2726–2755.
- Kallweit, R. S. & Wood, L. C. (1982). The limits of resolution of zero-phase wavelets. *Geophysics* 47, 1035–1046.
- Kulaitis, G., Munk, A. & Werner, F. (2021). What is resolution? A statistical minimax testing perspective on superresolution microscopy. *Annals of Statistics* 49, 2292–2312.
- McLachlan, G. J. (1987). On bootstrapping the likelihood ratio test statistic for the number of components in a normal mixture. *Applied Statistics* 36, 318–324.
- Qin, Y. S. & Smith, B. (2004). Likelihood ratio test for homogeneity in normal mixtures in the presence of a structural parameter. *Statistica Sinica* 14, 1165–1177.
- Robertson, C. A. & Fryer, J. G. (1969). Some descriptive properties of normal mixtures. *Skandinavisk Aktuarietidskrift* 52, 137–146.
- Schilling, M. F., Watkins, A. E. & Watkins, W. (2002). Is human height bimodal? *The American Statistician* 56, 223–229.
- Shahram, M. & Milanfar, P. (2004). Imaging below the diffraction limit: a statistical analysis. *IEEE Transactions on Image Processing* 13, 677–689.
- Smith, S. T. (2005). Statistical resolution limits and the complexified Cramér–Rao bound. *IEEE Transactions on Signal Processing* 53, 1597–1609.
- Widess, M. B. (1973). How thin is a thin bed? *Geophysics* 38, 1176–1180.
