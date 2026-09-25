GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch (plus SubagentHandback, the hand-off channel. I hold no Edit, Write or NotebookEdit.)

# Role 6, Methods / domain expert ("RTFM"): findings

Artifact: docs/proposals/2026-09-25-hebbian-coupling-detector.md. I also reviewed its analysis code, tools/make_hebbian_kernel_figure.py, as code: I ran it with `--no-png --out <scratch>/mb2/fig`, and it wrote only to scratch.

Sources I grounded in:
- clamor's `clamor:clamor/malsburg1986.py`, read in full: `coactivity`, `control`, `modulate`, `selftest`.
- `src/bugarach/graph.py`: `sttc`, `sttc_matrix`, `jitter_trains`, `modularity_vs_null`.
- The `src/bugarach/assembly.py` docstring on the curveball and uniform nulls.
- The jitter README and `docs/decisions_pending.md` item 2.
- The Aicher et al. arXiv abstract.
- The Kempter 1999 citation, confirmed by search. The PDF downloaded (6 pages), but I could not extract its text: there is no poppler or pypdf on this machine. The zero-integral claim is therefore checked against the citation and standard knowledge, not the paper body.
- Lit-cache: `fetch_paper.py` is not vendored here (CLAUDE.md deviation), so I could not run `--have` or `--need`. I did not reach the von der Malsburg 1986 paper either.

All simulations are single-shot `python3 -c` runs. Nothing was written outside the scratchpad.

## Findings

Format: location · issue · severity · suggested fix · verified against a source?

**1.** "What could make this worthless", busy-core check · **As specified, the check cannot trip its own stop.** I simulated pure one-core recordings: 32 ROIs, 600 s, 30 events, independent Bernoulli participation with p_i drawn from U(0.05, 0.6), σ = 0.106 s, 0.01 Hz background, onsets on a 0.1 s grid. STTC at a 0.15 s tile against 60 surrogates from `graph.jitter_trains(±20 s)`. **12 of 12 recordings PASS ("structure beyond one core").** Real λ2 was 0.60–0.96; the surrogate 95th percentile of λ2 was about 0.28.
- The cause is event-sampling noise around a rank-1 mean. Membership that varies from event to event raises λ2–4 far above a timing-destroyed surrogate. This is the same defect the page itself names for readout 1 ("a timing-destroying null says yes everywhere").
- The planned control ("a planted one-core-plus-noise matrix must trip the stop") would miss this if it plants a matrix rather than trains, because that bypasses the surrogate path.
- Three λ tested at an uncorrected 95th percentile also give roughly 14% false passes per recording, before counting the sampling effect.
- · **High** · Use a null that keeps the events and moves only membership: curveball on the cell×event matrix, which fixes each cell's participation total and so reproduces a rank-1 core with its sampling noise, or a parametric rank-1 bootstrap. The control must plant *trains*, not a matrix. State whether eigenvalues are ordered by signed value. · **yes** (simulation with repo code)

**2.** Method detail, "Whole frames": "Onsets are floored to frames before lags are taken" · **The export's onsets are already on the 0.1 s grid** (jitter README: "every offset under 0.00001 frames"). Plain `floor(t/dt)` on those floats puts a share of onsets in the previous frame: **4.1%** for `k*0.1`, and **32%** if values are stored rounded to 6 decimal places. That turns same-frame pairs into lag-1 pairs (Co 1 → cos(π/m)) at random. · **High** (for the implementation spec) · Specify `round(t/dt)`, or `floor(t/dt + 1e-9)` as `bench.py:127` already does. · **yes** (computed)

**3.** Busy-core and just-STTC checks, "tile of half the coincidence span" · **At even m (2, 4, 6) the tile equals a whole number of frames.** Grid lags then sit exactly on the tile boundary, and whether they count as a coincidence is decided by floating-point error. `|k*0.1 − (k−1)*0.1| <= 0.1` holds for 47% of consecutive grid pairs, and the two-frame case holds for 60%. Separately, **`graph.jitter_trains` does not snap to frames**: it adds continuous uniform displacement and wraps with `np.mod`. The prose says the surrogates are "jittered uniformly within ±20 s and snapped to frames (`graph.jitter_trains` …)". · **Medium** · Use half-integer tiles, (m ± 1)/2 frames, or compute coincidences in integer frames. Add an explicit snap step to the surrogates, or correct the prose. · **yes** (code read, computed)

**4.** "Where the code comes from" / "The step and the clamp" ("the bound needs the clamp in clamor's `modulate()`") · **clamor's `modulate()` verbatim cannot run the rule this page specifies.** It:
- updates one row, or one column, per call, not W_ij and W_ji together;
- compares only against each other cell's *most recent* break-off (`last_break`), so it pairs nearest neighbours, not every pair of onsets within ±m;
- applies its own subliminal gate |dt| ≤ period + burst/2 = **2.5m**, and past m that gate lets wrapped lags through (a lag of 2m scores +1);
- calls `coactivity`, which has **no half-weighted ends**, so the lag sum is −1 and rate neutrality is lost.

Only `control()`, `coactivity()` (after gating, then halving ends), and `S_MIN` / `S_MAX` are usable as they stand. The update loop has to be new code. · **Medium** · Say so. The reason given for copying the whole module ("copying two methods would have lost the clamp") no longer holds: the clamp is `S_MIN` / `S_MAX` plus one `clamp` call. The new loop needs its own test against the page's lag-sum-0 invariant. · **yes** (source read)

**5.** Method detail, "The step and the clamp": "each entry of D records the sign of its first pair of onsets" · **Overstated.** From rest, a step of 0.01·Co crosses the clamp only if |Co| ≥ 0.96. That means only a same-frame first pair (Co = 1) sticks at the upper clamp. With ends halved, the most negative weight is −0.866 (m = 6, lag 5), so no single first pair sticks at the lower clamp at any m from 3 to 6. Entries stick later, whenever any step overshoots. · **Medium** · Rewrite as: "a same-frame first pair pins the coupling at the upper clamp for good, and any later step that overshoots pins it too, so D saturates rather than learns". · **yes** (arithmetic from eq 8)

**6.** Figure 1B caption and code; "The span" · Four linked problems with how panel B is used:
- **(a) The metric does not count what the label says.** `measure()` computes Σ p_k·w(k) over *all* coordinated onset pairs, including those beyond ±m that never update. The y-axis says "expected Co per update" and the prose says "coordinated updates". Conditioned on an update actually happening, m = 2 gives fast 0.160 (not 0.144) with **25%** of updates negative (not 22%), and slow 0.104 with **30%** negative (not 24%).
- **(b) The rationale for the sweep doesn't follow from the tool's own output.** m = 3 puts *more* updates on the negative lobe than m = 2: fast 30%, slow 37%. Slow m = 5 (19%) is about the same as m = 2. "About a fifth at two jitters, therefore sweep 3–6" is not supported. Expected Co does rise monotonically (fast 0.144 / 0.313 / 0.486 / 0.622 / 0.718), and that is the defensible reason.
- **(c) The headline numbers are at a span the run will never use.** "0.144 … an artifact weighs about seven coordinated pairs" is at m = 2, which is outside the 3–6 sweep. At m = 3 an artifact weighs about 3.2 fast pairs (1/0.313) or 5 slow pairs (1/0.200); at m = 6 about 1.4.
- **(d) Slow is modelled as Gaussian.** The README says slow has a long tail out to about 1.5 s, so the slow negative-lobe share is understated.
- · **Medium** · Relabel as "per coordinated onset pair", or condition on |k| ≤ m. Justify 3–6 by expected Co. Quote the artifact ratio at the swept m. Flag the slow tail. · **yes** (ran the tool, recomputed)

**7.** Readout 2: "a weighted stochastic block model (Aicher, Jacobs & Clauset 2015) handles signed weights" as a candidate for "a method that lets one ROI join several" · **The weighted SBM (WSBM) is a partition model.** The abstract says "learning a network partition", so each vertex gets one block. It cannot return overlapping groups: it has the same one-group-per-cell blind spot as modularity, which is the risk this readout exists to address. Normal-distributed weights do handle signed values. · **Medium** · Replace it with a mixed-membership or overlapping model (e.g. mixed-membership SBM, Airoldi et al. 2008), or keep the WSBM but drop the overlap claim. Journal reference: *J Complex Networks* 3(2):221–248. · **yes** (arXiv abstract)

**8.** "The call" comparison: "E(t) with Z replaced by its own mean (a squared active count)" · **Contradicts readout 3.** E(t) is defined as the *mean* of Z over the pairs in A(t). Replace Z with a constant and E(t) is that constant whenever |A(t)| ≥ 2: a binary "two or more active" call, not a squared active count. "Squared active count" describes the sum form the page rejected. · **Medium** · Pick one comparator: the sum of a constant (a pair count), or the active count itself. · **yes** (arithmetic)

**9.** Readouts and the just-STTC rank arm · **Z is undefined, not tied at 0, for sparse pairs.** A pair that never updates in the data, and whose surrogates never update either, has surrogate SD 0, so Z = 0/0. A pair with D = 0 but some surrogate updates gets Z = −μ/σ, which differs from pair to pair. The τ-b rationale ("sit tied at 0") describes D, not Z.
- Also unspecified: which null standardizes Z for readout 2 (jitter or curveball). Comparing λ(Z) against λ over surrogates needs each surrogate's own Z, meaning nested or leave-one-out standardization, and that cost is not counted.
- · **Low–Medium** · Define Z when SD = 0 (exclude the pair, or floor the SD). Say which null Z uses per readout. Budget the nested surrogates. · **no** (reasoning from the definitions)

**10.** Readout 2 null · **The curveball null has a documented blind spot.** `assembly.py`'s docstring says the fixed-margin null "goes blind exactly where the signal is purest" and that "neither is sufficient alone", which is why it runs next to `pvalues_uniform`. The page uses curveball alone and does not mention this. · **Medium** · Carry both nulls, or state the blind spot. · **yes** (source read)

**11.** Freezing, and q0 = 0.004 · **At q0 = 0.004 the coupling saturates quickly.** 3 same-frame coincidences take a coupling to 90% of the half-band, or 11 at mean Co 0.32. At q0 = 0.01/12 it takes 17 and 53. In a simulation of independent 1 Hz trains at q0 = 0.004, the SD of D was about 0.0097, roughly the whole half-band. At the larger step, the top of the ranking compresses and a few artifact frames dominate. · **Low** · Note it beside the sweep. Planted-pair AUC at the middle strength may not show it; add a high-strength point. · **yes** (computed and simulated)

**12.** "Rate neutrality is in the mean … Before the clamp that is exact" · Exact in expectation for additive steps. With the state-dependent q(s) it needs each Co to be independent of the current s. Kempter et al. also derive under slow learning. My simulation found no drift: independent Poisson trains at 0.3 and 1 Hz, m = 3 and 4, q0 = 0.004 and 0.01/12, 1,500 pairs each, gave mean D within |z| ≤ 1.7 of 0 in all 8 conditions. The claim is plausible, but "exact" is stronger than the argument shown. · **Low** · Say "zero in expectation, to first order in q0", or cite the simulation. · **partly** (simulation yes; Kempter body not read)

**13.** Readout 3, cross-fitting: "no frame is scored by couplings it built" · Frames within m of the halves' boundary have A(t) sets that include onsets from the learning half. · **Low** · Drop an m-frame guard band at the split. · **no** (reasoning)

**14.** Readout 1: "surrogates that keep each ROI's slow rate changes" · `jitter_trains` wraps with `np.mod`, which moves onsets from one end of the window to the other within 20 s of each edge. It can also put two onsets of one ROI in the same frame, with no dead time kept. · **Low** · State both, or use reflecting or truncating jitter. · **yes** (code read)

## Checked and consistent (no finding)

- **Lag sum:** −1 unweighted and 0 with half-weighted ends, for m = 2–6. The script's output matches the identity for 2m roots of unity.
- **Kernel shape:** Co(k) = cos(πk/m) is clamor's cosine at period 2m and burst m, the case `selftest()` pins (period 6, burst 3).
- **Wrap at |k| = m:** clamor's wrap uses `torch.round`, which rounds half to even, so a lag of exactly ±m does not fold to +1.
- **Step size and clamp:** the limit q0 ≤ s0·s_d/2 = 0.0048 is correct, derived as (1−x)(h − q0(1+x)) ≥ 0. The 0.0220 vs 0.0216 figure and S_MIN / S_MAX are correct.
- **STTC:** NaN for an empty train, matching the page's "undefined". `dt` is the half-width, so "half the span" does match the positive lobe |k| < m/2.
- **Surrogate count and old tile:** 200 surrogates and the 2 s tile match `modularity_vs_null`'s defaults.
- **Jitter σ:** per participant, with lags at σ√2, consistent with the jitter README and `decisions_pending` item 2. The calibrated σ already accounts for grid rounding, so flooring in panel B is consistent.
- **Citations** checked against sources: Kempter, Gerstner & van Hemmen 1999 (*Phys Rev E* 59:4498); Aicher, Jacobs & Clauset 2015.
- **Figure 1C** marker positions are 0.02200, 0.01600 and 0.01283.

## Files

- docs/proposals/2026-09-25-hebbian-coupling-detector.md
- tools/make_hebbian_kernel_figure.py (`measure()`, lines 75–89: the per-pair vs per-update metric)
- clamor:clamor/malsburg1986.py (`modulate`, lines 250–285: 2.5m gate, last-break only, row only)
- src/bugarach/graph.py (`jitter_trains`, lines 249–265: no snap to frames, wraps at the edges)
- src/bugarach/bench.py:127 (the `+1e-9` floor precedent)
- src/bugarach/assembly.py (lines 17–30: the two-null caveat)
- Scratch: <scratchpad> (`fig/hebbian_kernel.svg`, `k99.pdf`)

Sources:
- [Aicher, Jacobs & Clauset, arXiv:1404.0431](https://arxiv.org/abs/1404.0431)
- [Kempter, Gerstner & van Hemmen 1999, Phys Rev E](https://link.aps.org/doi/10.1103/PhysRevE.59.4498)
- [Kempter99.pdf (EPFL)](https://lcnwww.epfl.ch/gerstner/PUBLICATIONS/Kempter99.pdf)
