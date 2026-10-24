# Blind pass B: final report, verbatim (2026-10-23)

Kept so the goal page's attributions to blind pass B can be checked (murderboard 2026-10-23,
roles 1 and 3). The agent worked in a detached checkout of `main` at c442014a and ran against
the first Aim 1a record, now `../aim1_one_source_shared_seeds.json`. Personal paths are replaced
by `<worktree>`; nothing else is changed. Its scripts and their `.txt` outputs are beside this
file; the scripts do not run in place (their paths assume the worktree's `_scratch/`).

---

## Is there an analytical prediction? Yes, for most of Aim 1a and much of Aim 2

I worked only in `<worktree>/_scratch/`. Nothing tracked was edited. Under the generator's assumptions (fixed k, Gaussian jitter σ, 0.1 s frames, stationary Poisson background, events ≥20 s apart), almost every Aim 1a number follows from closed forms, plus Monte Carlo of **one event** where needed (never a whole recording). On `aim1_one_source.json` the predictions land within a few percent, with one residual I can't fully explain.

### 1. Coordination-rates tool (factorial cumulants)
Notation: p = n_ev·w/T events per window, m = p·k signal onsets per window, P_r = E[(1 − R_r/w)₊], R_r = range of r onsets of one event, averaged over the tool's two tilings.

- **f2 = p·k(k−1)·P2 − m²(1 − 1/N)**
- **f3 = p·k(k−1)(k−2)·P3 − 3m·p·k(k−1)·P2 + 2m³**
- Then solve(fixed): **k̂ = f3/f2 + 2**, λ̂ = f2/(w·k̂(k̂−1)), share = λ̂·k̂/N.
- Small σ: P_r ≈ 1 − E[R_r]/w, with E[R2] = 1.13σ and E[R3] = 1.69σ. That gives **k̂/k ≈ 1 − ((k−2)/k)·[0.56·σ/w + λwk(3/(k−2) − 1/(k−1))]**.

The m-terms are new. They are a **hard-core bias**: the estimator's chance subtraction assumes events can share a window, and the generator's min_sep forbids it. They explain the ~10–13% k undercount at w = 4 s even at σ = 0.05. The formula sets two opposing pulls on the window: jitter wants it large, the hard-core term wants it small. The optimum is roughly w* ≈ √(0.28σ/λ), about 1.8 s at σ = 0.2 and one event per minute.

**Noise** (delta method; background μ = N·b·w; Charlier orthogonality makes background f2 and f3 uncorrelated):
- Var f2 ≈ [2μ²a₂ + 4μE[S²]a₁]/n + n_ev·Var(C2)/n²
- Var f3 ≈ [6μ³a₃ + 18μ²E[S²]a₂ + 9μE[S₍₂₎²]a₁]/n + n_ev·Var(C3)/n²
- n = T/w windows, S = signal onsets in a window, C_r = one event's window-summed c(c−1)…, a_j = (1 + 2⁻ʲ)/2 for the two tilings.

Test against the json, 144 cells (w × σ × k × n_ev × b):

| | median error | max | b = 0.01 cells only |
|---|---|---|---|
| k̂ | 4.6% | 14% | 1.2% |
| λ̂ | 10% | 41% | 3.7% |
| share | 5.5% | 26% | 3.2% |

Examples (pred | obs, median of 20 recordings): k̂/k at w=1, σ=1, k=20 is 0.36 | 0.34; w=1, σ=0.5, k=10 is 0.63 | 0.58; w=4, σ=0.05, k=20 is 0.90 | 0.87. λ̂/λ at w=1, σ=1, k=20 is 2.21 | 2.36. Share at w=4, σ=0.05, k=10 is 1.06 | 1.11.

Noise against 40–60 extra seeds per case: f2 SD predicted within 0–10% in all 8 cases; f3 SD within 0–40% (overpredicted at w = 4 with high background). Predicted f3 signal-to-noise against how often f2 or f3 came out ≤0 (estimate undefined): below 1 → 56% undefined; 1–2 → 7%; above 2 → about 0%.

**Residual I can't explain.** At b = 0.05, f3 is 5–7% below prediction (60 seeds, about 4σ). It is absent at b = 0.01. It drives most of the λ and share error at k = 5. On top of that, **the json reuses seeds 0–4 in every cell**, so each background is identical across all 24 cells that share a rate. Seed explains up to 49% of the residual variance (b = 0.05, w = 4). Those five seeds also happen to be low: their f3 is 0.56 against a 60-seed mean of 0.76. Some of the "systematic" trends in Figure 1 are five shared background draws.

### 2. `assess_coactivity`: fully predictable
- **False clusters per minute**: R_false(K) = 60·π_K·(1 − π_K)², with π_K = P(Binom(N, 1 − e^(−b)) ≥ K) on 1 s bins. The 2-bin merge rule is why a cluster start needs the two previous bins below K. At b = 0.05 this gives 7.97, 3.86 and 0.28 per minute for K = 3, 4, 6, against 0.33–1 planted events per minute. That is the whole "K must rise with background" result. A background-only check of the clustering agrees within 1%.
- **Observed clusters/min** = R_false + (events per minute) × (clusters one event adds, from one-event MC).
- **part and jit** are medians of a mixture of false and event clusters, weighted by their rates. For a detected event with σ ≪ 1 s, part ≈ k + (N−k)(1 − e^(−3b)).
- **Why jitter saturates**: onsets are gathered within ±1.5 s, so a σ = 1 Gaussian reads as SD 0.74. False clusters read 0.6–0.75 s, and at b = 0.05 they dominate the median at K = 3–4. That is why jit_obs sits near 0.6–0.7 whatever was planted.

Per-cell test, 141–143 cells:

| | median error | 90th percentile | correlation (log) |
|---|---|---|---|
| clusters/min | 1% | 12% | 0.998 |
| participants | 0% | 10% | 0.994 |
| jitter | 2% | 19% | 0.974 |

For example at σ = 1, k = 10, 45 events, b = 0.01, K = 6: 0.25 | 0.29 clusters/min, 10 | 10 participants, 0.59 | 0.63 s jitter.

### 3. ADR-0008 chance floor (closed form)
Upcrossing rate ν_K = Σᵢ bᵢ·e^(−bᵢw)·P(other ROIs co-active = K−1), using the Poisson-binomial distribution and w = 2 s. Floor = smallest K with 3600·ν_K ≤ 1.

Against `window_floor` (200 draws) on 30 simulated recordings (N 15/33/100, b 0.01–0.1, uneven rates across ROIs, with and without events): exact in 25, off by ±1 in 5.

The floor is 6 at N = 33, b = 0.01 and 12 at b = 0.05. So k = 5 events can never pass it at either background, which is a capability edge you can state in advance.

One quirk: for a saturated field, ν_K is not monotone at small K. `floor_of` searches upward from K = 1, so it could in principle return a tiny floor. N = 100, b = 0.05 was borderline (0.8 calls/h at K = 1).

### 4. Aim 2 preview: count detector
Recall = 1 − E[∏ over bins P(Binom(N−k, q) < K − participants in that bin)]; false alarms per hour = 1800·π_K(1 − π_K)². Over 24 conditions × 6 seeds, recall agrees within about 0.03 in most cells (e.g. 0.344 vs 0.330; 0.851 vs 0.841). It is underpredicted by up to 0.12 at b = 0.05 and high K, because nearby background bins add lucky hits. False alarms agree within ~10% (e.g. 262 vs 247 per hour, 5.3 vs 5.1).

### 5. A better jitter estimator the theory suggests
f2(w)/w ∝ P2(σ, w), and λ and k cancel even if k varies. So the ratio of pair excess at two windows gives σ blind. Run on the existing json with no new simulation, at the 1 s / 4 s pair:

| σ planted | 0.05 | 0.2 | 0.5 | 1.0 |
|---|---|---|---|---|
| this estimator, σ̂/σ | 1.7–2.1 | 1.08–1.15 | 1.00–1.05 | 1.04–1.08 |
| assess K = 4, for comparison | 2.4–13 | 1.2–3.3 | 0.99–1.32 | 0.69 |

It is undefined in 0–18% of recordings. At σ = 0.05 it fails because the windows are too coarse; a 0.2–0.5 s window would be needed. This is essentially the integrated correlogram, so it could stand in for open item 4.

### What still needs simulation
- Non-Poisson backgrounds: bursty per-ROI rates, shared slow comodulation, the probe stretch. Rigid-shift and circular nulls then keep structure that has no closed form.
- Detectors with local or adaptive nulls under non-stationarity: LoCo's rolling percentile, CoactDetect's rate-local surrogates. (Binned SCE's percentile threshold is a Poisson-binomial quantile when the background is stationary.)
- Tuning-budget outcomes, the assembly recurrence test, scoring edge cases (splits and merges when σ ≈ bin), and the Aim 3 loop end to end.
- Two sources near degeneracy. One firm statement: with f2 and f3 only, **two sources with equal jitter are not identifiable** (only Σλk(k−1) and Σλk(k−1)(k−2) are seen). Separating them needs f4 or higher, or participant-count distributions. Different jitters separate through the f2(w) curve, down to a noise-limited ratio that a few simulations should set.
- The unexplained 5–7% f3 shortfall at high background.

### Other analytic routes, not pursued
- Likelihood / Cramér–Rao bounds for (λ, k, σ), from a Poisson-cluster model of the population count. This is the principled answer to "where do parameters stop being identifiable" in Aim 1.
- Scan statistics / Poisson clumping for sliding-window detectors (generalises section 3).
- Gaussian fits to the pairwise correlogram for σ (equivalent to section 5).

### Recommendation
1. Replace most of Aim 1a's brute force with these curves. Re-plot Figure 1 against the few dimensionless groups that set the outcome: σ/w, σ/bin, λw, μ = Nbw, and k relative to K or the floor. Keep simulations as spot checks where theory is weak: signal-to-noise 1–3, σ ≈ w, non-Poisson backgrounds.
2. Use independent seeds per cell, or say plainly that backgrounds are shared.
3. Place the Aim 2 grid on the predicted recall transition (k near the floor(b, N), σ near bin/2) rather than uniformly. Spend simulation on bursty/comodulated backgrounds and adaptive-null detectors.
4. In the tools: correct the hard-core term, or note it (real data may not have a minimum spacing between events). Choose K from R_false(K, b) ≪ event rate. Consider the window-ratio jitter estimator.

Uncertainty: everything here assumes the generator's own model. The real-data transfer is exactly the part theory cannot certify.

### Scripts (all in `<worktree>/_scratch/`)
Each has a `.txt` output beside it.
- `theory_cumulant2.py`: cumulant mean and noise prediction vs the json (`theory_cumulant.py` is the earlier version without the hard-core term)
- `sim_cumulant_check.py`, `check_f3.py`, `check_row.py`: extra-seed checks of f2/f3 mean and SD, and the shared-seed finding
- `theory_assess.py`: assess cluster rate, participants and jitter vs the json
- `theory_floor.py`: chance floor vs `window_floor`
- `theory_count_detector.py`: count-detector recall and false alarms
- `jitter_from_window_ratio.py`: the blind jitter estimator
