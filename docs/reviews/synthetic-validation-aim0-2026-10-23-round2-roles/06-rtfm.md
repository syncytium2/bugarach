GRANT 6 MISMATCH — missing none (WebFetch/WebSearch arrived deferred and were loaded); holds Edit, Write, NotebookEdit, PowerShell, Agent, Artifact, Skill, ToolSearch, MCP tools (forbidden editing tools held, not used on any tracked file)

**Blindness breach, disclosed.** I ran a broad grep over `docs/` for "0.105|0.131" and its output included lines from `docs/reviews/synthetic-validation-aim0_2026-10-23-roles/03-cross-examiner.md` and `...-round2-roles/01-prove-it.md` and `03-cross-examiner.md`. I did not open those files. The lines showed one earlier finding: that the glossary's jitter values are σ, not half-widths. I then checked it against the run record myself (finding 8). Finding 8 is therefore **not blind**. All the other findings were reached before that grep, or have nothing to do with it.

**Process notes (about the run):**
- The lit-cache check `fetch_paper.py --have Kreuz synfire` found nothing.
- `fetch_paper.py` caches into the Dropbox library, and the r2 rules forbid Dropbox writes. So I fetched Kreuz 2017 (arXiv 1610.07986v4) and Kreuz's 2025 review (arXiv 2510.07140) into `_scratch/r2-role-06/dl/` instead.
- Kreuz et al. 2022 (JNM 381:109703) and Mariani et al. 2025 (JNM 416:110378) were not opened. They should go on `--need`, which I did not run because it also writes to Dropbox.
- PySpike 0.9.0 failed to build its Cython parts. I used the sdist's pure-Python backend from scratch and ported `sim_ann_cython` line for line.
- `theory.py check()` writes into the repo, so I ran it with its output folder pointed at `_scratch/r2-role-06/`.

## Findings
Format: location · issue · severity · suggested fix · verified against a source

1. **`theory.py` §1 (`s_eff`); page, "What is added here … (window sharing g_n, with frame rounding)"** · The frame-rounding term is wrong. Event times are continuous (`_place_renewal`) and the windows sit on the frame grid. Under uniform phase, E|round(a) − round(b)| = |a − b| exactly, so rounding adds no window-sharing loss in expectation; the range of n onsets behaves the same way.
   - Monte Carlo, 400k events, the tool's two window offsets, σ = 0.05 s, w = 1 s: g₂ measured 0.9441 against the s_eff model's 0.9349 and the unrounded σ's 0.9436. g₃: 0.9159 measured, 0.9023 model, 0.9154 unrounded.
   - Effect: on noiseless cumulants the joint fit reads planted 0.05 s as **0.041 s (−18 %)**, 0.1 as 0.096 and 0.2 as 0.198; k and λ are unaffected. Part of "jitter not resolved at the frame scale" is model error, not noise.
   - **Medium** · Use σ, not s_eff (or derive the exact discrete form), rerun `check()`, and drop "with frame rounding" from the claimed additions. · yes (`_scratch/r2-role-06/g_round.py`, `fit_bias.py`)

2. **Page, "Against Kreuz's synfire measure" (the three differences)** · "Coincidences come from ISI-adaptive windows" understates the problem. On trains this sparse the adaptive window spans neighbouring events.
   - Test: 33 cells, 10 per event, events every about 25 s, no background, Kreuz eqs 1–2/7/12–14 written from the paper. It counts **3591 coincidences against 2700 true co-participations (+33 %)**; with `max_tau` = 2 s it counts 2634. My code matches PySpike's backend exactly (F 0.1922).
   - The 0.28 normalization claim holds approximately: F_PySpike / F_known-events = 0.258 at the true order, against (k−1)/(N−1) = 0.281.
   - The extra cross-event pairs carry order-free signs, so they add to the sorted no-order bias, and their number depends on spike density. That is another mechanism for the August spike-count anti-correlation. `synfire_scan.py` sets no `max_tau`.
   - Kreuz 2017 §2.1 provides τ_max for this case, and the 2025 review §4.2 describes these "spurious matches" from overlapping events.
   - **Medium** · Add this as a fourth difference, and in plan item 1 run `synfire_scan` with and without `max_tau`. · yes (`kreuz_own.py`, `pyspike_dbg.py`)

3. **`order_limit.py` docstring ("local search … standing in for the simulated annealing … which can only do as well or better"); page "0.50 under a local search that stands in for annealing"** · This is false for PySpike's annealer: neighbour swaps only, T from 2·max D, α = 0.9, and it stops at the first temperature with no accepted move.
   - Ported annealer on the same D matrices, best of 3 restarts: c = 0.475 against 0.487 for local search at E = 200, and 0.482 against 0.497 at E = 50. Annealing ended below local search in 80–87 % of repetitions.
   - Side note: PySpike's annealer draws from libc `rand()`, so `synfire_scan`'s `np.random.seed` does not seed it, and "a rerun reproduces" does not hold for the sort.
   - **Minor** · Say that local search is an approximate stand-in (annealed c ≈ 0.48 here), not an upper bound. · yes (`sa_vs_ls.py`; Cython source read)

4. **Page, membership/order intro: the August null is "a variant of Kreuz et al.'s order surrogates (2017, sec. 2.5)"** · Kreuz §2.5 keeps the coincidence structure (every spike's SPIKE-Sync value) and swaps order within coincident pairs at the level of order values. It explicitly avoids changing spike times, because that would alter ISIs and coincidences. `synfire_scan._relabel` permutes ROI labels over all pooled spikes, which changes ISIs, coincidences and membership. It is a different null.
   - **Minor–medium** · Say "unlike Kreuz's §2.5 surrogates, which keep every coincidence and swap only order". · yes

5. **Page, "Kreuz's lab still anneals the sort (Kreuz et al. 2022 …)"; "Mariani 2025 replaced annealing … with a direct estimate"** · Kreuz's 2025 review gives 2022 as "Latency correction in sparse neuronal spike trains": its annealing is over latency shifts, not the sort, and it already proposed direct shifts. The review cites the sort's annealing to 2017. Mariani 2025 adds an Extrapolation direct shift and reduced-matrix annealing for overlapping events ("almost the same performance … much faster"). The figures 9.7 s against 861.8 s are unverified.
   - **Minor** · Cite 2017 for the annealed sort, and describe 2022/2025 as latency-correction work. · partly (review only; neither primary paper opened)

6. **Page, "Under one template F = (2/π) arctan τ (A)"; Figure 4A** · The closed form holds at the true template order; the score sort plotted departs from it at both ends.
   - τ = 0.25: score sort 0.176–0.179 against 0.156 predicted (+13–15 %, the no-order bias).
   - τ = 5: 0.854–0.857 against 0.874. The true order gives 0.869 and local search 0.874, so here the sort itself misorders cells.
   - **Minor** · Say that the bias-in-quadrature form also applies at M = 1, and that the sort loses about 2 % at large τ. · yes (`one_tmpl.py`)

7. **Page, chance clusters "predicted … 0.02 … (measured … 0.04)" at K = 4, 0.01 Hz** · The 10-recording arm holds 16 clusters in total and cannot resolve a 2× difference. Over 200 background-only recordings through the shipped assessor clustering:

   | condition | measured (per min) | predicted |
   |---|---|---|
   | K = 4, 0.01 Hz | 0.0181 | 0.0191 |
   | K = 3, 0.01 Hz | 0.269 | 0.256 |
   | K = 6, 0.05 Hz | 0.297 | 0.284 (the page quotes 0.22) |

   The formula is confirmed; the quoted value misleads, and there is a small +4–5 % excess at two Ks.
   - **Minor** · Requote from a larger chance arm. · yes (`chance.py`)

8. **GLOSSARY jitter entry (L468–476) and page Symbols parenthesis** — *not blind, see the breach note* · The glossary's 0.105 / 0.131 s are the **calibrated σ** (`jitter_sec`), not half-widths. The run record `docs/learned/runs/2026-09-23-jitter-by-group-66/README.md` L51/56 gives half-widths 0.186 / 0.228 and σ 0.105 / 0.131. The new "Two measures" note invites dividing 0.105 by 1.67. The 1.67 conversion itself is right: 0.186 / 0.105 = 1.77 with frame effects.
   - **Major** · Relabel the values as σ calibrated from the half-width. · yes

## Checked and clean
- **Coordination-rates derivation:** f₂/f₃ with the at-most-one-event term, and the surrogate terms (1 − 1/N) and (1 − 1/N²) re-derived from the per-cell Bernoulli counts. The predictions do pass through the tool's `solve()`.
- **Quoted numbers:** every number from `theory.check()`/`summary()` that the page quotes reproduces exactly, including the 17/720 refusals, the joint-fit σ, k and λ values and the at-bound counts.
- **Chance formula against `_clusters`:** clusters merge when fire bins are ≤ 2 apart, which gives q(1−q)², and the ±1.5 s gather always reaches K.
- **Assessor ceiling:** ±1.5σ truncated SD = 0.743, as quoted.
- **Event floor:** 6 cells at 0.01 Hz and 12 at 0.05 Hz for 33 cells (`window_floor`, 200 draws against the shipped 1000; both halves stable).
- **Kendall/Greiner:** (2/π) arcsin ρ = (2/π) arctan τ. The `pred_many` variance identity holds.
- **Membership:** measured within 1–3 % of 1 + (E−1)/M.
- **PySpike internals:** `spike_train_order_multi` computes e_total/m_total, which is eq. 14 with m = n_a + n_b, so 0.28 = (k−1)/(N−1) is right. MRTS defaults to 0 (the original adaptive windows).
- **Kreuz §3.1:** the finite-size statement is confirmed verbatim. §3.1 also says F "is strongly influenced by the statistics of the dataset and thus is in itself not sufficient to reliably compare two datasets with widely different number of spike trains and spikes". That sentence is worth citing for the August caveat.
- **Shipped parameters:** Aim 1a used the tool's shipped settings (20 surrogates; windows 1, 2, 4 s). The assessor ran at 120 surrogates, but only its observation-side outputs (`jit_obs`, `part_n_obs`, `clusters_permin`) are used, and those do not depend on surrogates.

Scripts and fetched papers are in `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\_scratch\r2-role-06\`.
