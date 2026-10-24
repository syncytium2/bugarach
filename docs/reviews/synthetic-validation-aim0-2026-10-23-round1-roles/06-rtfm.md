GRANT 6 MISMATCH — missing none (WebSearch and WebFetch were deferred and I loaded them); holds forbidden tools: Edit, Write, NotebookEdit (deferred), plus PowerShell, Agent, Artifact, Skill and the Dropbox, Gmail and Claude Docs MCP tools.

I did not edit any tracked file. I used Write only for scratch scripts under `_scratch/role-06/`.

**Sources I grounded in.**
- **Lit-cache tooling is missing.** There is no `fetch_paper.py` anywhere under `C:\Users\defazio\bugarach`, and `MURDERBOARD_LIT` is unset, so I could not run `--have` or `--need`.
- **Kreuz et al. 2017.** I read the open-access text (NJP 19:043028) via WebFetch. Its equations are images, so for the exact normalisation I read the PySpike 0.9.0 sdist source instead (`_scratch/role-06/src_dl/pyspike-0.9.0`).
- **PySpike would not build from pip** (no compiler for its Cython parts). I ran its pure-Python backend for `spike_train_order`. The annealer needs Cython, so I could not run it; I used an insertion-move local search as a stand-in.
- **Project code read:** `theory.py`, `order_limit.py`, `membership_limit.py`, `aim1_one_source.py`, `aim1_figure.py`, `measure_coordination_rates.py`, `assess.py` (`_coact_count`, `_clusters`), `simulate_coordination` and `synfire_scan.py`.

**What checked out:**
- `g2_closed` equals the `_range_cdf` integral, and `g3` matches Monte Carlo to 1e-3.
- The factorial-cumulant algebra in `coord_rates_exact` is right.
- `k_hat = (k−2)g3/g2 + 2` is right.
- The merge rule `q(1−q)^merge_bins` matches `_clusters`: gaps of 2 bins or fewer merge.
- The truncated SD of 0.74 s is right.
- `(2/π)arctan τ` for one template is right.

## Findings
*location · issue · severity · suggested fix · verified against a source (yes/no)*

1. **The jitter fit omits the at-most-one-event term.**
   - **Location:** `theory.py` docstring §3 and `jitter_from_windows`; goal page, Aim 0 first result, bullet "Jitter from how the pair count changes with window".
   - **Issue:** §3 says "only g_2 depends on w". Under the file's own exact form that is false: f2(w)/w = λk(k−1)g2 − λ²w·k²(1−1/N). The fit uses the Poisson model.
   - **Evidence:** I fed noise-free exact f2 at the Aim 1a parameters to `jitter_from_windows`. Planted 0.2 s comes back as 0.155 s (45 events) or 0.186 s (15 events). Planted 0.05 s comes back as 0.007 s or 0.03 s.
   - **Consequence:** the reported "0.2 → 0.17" and "floors near the 0.1 s frame (0.05 reads 0.02)" are at least partly this model error, not the frame.
   - **Severity:** high.
   - **Fix:** fit A·g2 − B·w with B = λ²k²(1−1/N) (or fit jointly, as blind A did), then rerun. Reword the attribution to the frame.
   - **Verified:** yes (`_scratch/role-06/theory_checks.py`).

2. **The score (Borda) sort is not the optimiser, and the null-bias constant is Borda's.**
   - **Location:** `order_limit.py` and the goal page: "Under the template model the optimal order is the score order in expectation", and "F ≈ 0.375/√n̄ … the optimisation's own bias".
   - **Issue:** maximising F over orders is the linear-ordering problem. Borda is only a heuristic. It is optimal only for the expected tournament with a single template, not on realised data and not for M > 1.
   - **Evidence:** a local search on the same matrices beats Borda.

     | case | Borda | local search |
     |---|---|---|
     | no order, F·√n̄ | 0.37–0.40 | 0.49–0.52 (about 30 % higher) |
     | with order, M = 1 to 64 | — | 1–3 % higher |

     Annealing in `synfire_scan.py` would sit at or above the local search. So 0.375 is not the bias of the method it is compared with, and "the closed form replaces the brute force" fails exactly in the null case that is tied to the real data.
   - **Severity:** high.
   - **Fix:** state "Borda lower bound". Either derive or measure the optimiser's null constant, or drop "optimal".
   - **Verified:** yes (`_scratch/role-06/order_opt.py`).

3. **The indicator's normalisation differs from Kreuz/PySpike, and the difference is not a constant.**
   - **Location:** goal page, order paragraph ("Two changes from the published method", "the indicator F the share of pair agreements") and the ⚠ that "constants change, scaling laws are the claim".
   - **Issue:** PySpike's `spike_train_order` divides by the multiplicity of every spike in both trains, coincident or not: Σ_pairs (n_i + n_j), i.e. Kreuz's (N−1)·M. `order_limit` divides by the number of coincidences. That makes a third change, and the doc does not list it.
   - **Evidence:** I evaluated both at the same order, with N = 33, k = 10, τ = 1, 45 events.

     | background | order_limit F | PySpike F |
     |---|---|---|
     | none | 0.545 | 0.153 (= ×(k−1)/(N−1) = 0.28) |
     | 0.01 Hz | 0.493 | 0.045 |

     The factor depends on participation fraction and background share. So PySpike's indicator carries a spike-count dependence the Aim 0 scaling law leaves out.
   - **Severity:** high.
   - **Fix:** list the normalisation as a change. Model F_PySpike ≈ F × (coincident spikes / all spikes), or rerun with PySpike on the same trains.
   - **Verified:** yes (`_scratch/role-06/pyspike_cmp.py` and the PySpike source).

4. **The August ρ = −0.75 is attributed to the 1/√n̄ bias without a test.**
   - **Location:** goal page: "That is the August finding … (fast ρ −0.75) … and why the order-free control's median sat at 0.10".
   - **Issue:** ρ was measured across real recordings, not order-free ones. Dilution by non-coincident spikes (finding 3) and PySpike's adaptive τ, which shrinks with rate, also predict a negative correlation. The 0.10 control median was never computed from the formula.
   - **Severity:** medium.
   - **Fix:** say "consistent with". Compute the predicted control value at the bench's parameters under PySpike's normalisation.
   - **Verified:** partly (alternative mechanism shown; real data not rerun).

5. **The chance-cluster check is only met as a pooled median.**
   - **Location:** goal page: "predicts the measured cluster rate within about 10 % at every K and background"; `theory.check` and `aim1_figure.py` (prediction = chance + every planted event).
   - **Issue:** the comparison is keyed by (bg, K, n_events) and pools k and jitter. Per cell at 0.01 Hz and 45 events:

     | K | k | σ | measured /min | predicted /min |
     |---|---|---|---|---|
     | 6 | 5 | any | 0–0.16 | 1.0 |
     | 6 | 10 | 1.0 | 0.29 | 1.0 |
     | 4 | 5 | 1.0 | 0.22 | 1.02 |

     The pooled median hides a 3–20× miss. The model assumes every planted event makes exactly one cluster.
   - **Severity:** medium.
   - **Fix:** report it per (k, σ, K), add an event-detection term P(event reaches K) from k, σ and the bin, or restrict the claim to chance clusters.
   - **Verified:** yes (`aim1_one_source.json`).

6. **The "exact" form leaves out the surrogate's cross-cell covariance.**
   - **Location:** `theory.py`, `coord_rates_exact` docstring ("the shift surrogate … removes only its within-cell share"); goal page "predicted exactly".
   - **Issue:** `shifted` uses offsets that are multiples of 2w, spanning about 66–264 s. Over that span the renewal event train (min_sep 20 s) has a non-flat pair correlation. So shifted cells are not independent.
   - **Evidence:** in coordinated-only runs the mean surrogate f2 is 4–14× the predicted −(pk)²/N. For example −0.046 against −0.0034 at k = 20, w = 1; that is 30–40 % of the correction term. The effect on f2 is about 1 % and on k̂ under 1 % (pooled 0.828 against exact 0.836).
   - **Severity:** low.
   - **Fix:** call it "exact to about 1 %" or add the term ∫(ρ(Δ)−1) over the offset distribution. This could be the unexplained residual blind B saw (f3 5–7 % low).
   - **Verified:** yes (`theory_checks.py`, `f3_check.py`).

7. **A noise screen is coupled into the jitter fit.**
   - **Location:** `theory.f2_of` / `jitter_from_windows`.
   - **Issue:** f2 is rebuilt from `solve()` output, and `solve` returns NaN whenever f3 ≤ 0. A recording with a valid f2 but negative f3 is therefore dropped from the jitter fit. That is a selection the method does not need, and it biases the weak cells.
   - **Severity:** low.
   - **Fix:** fit on the raw `m["cum"][w]["f2"]`.
   - **Verified:** yes (code read).

8. **Aim 1a does not run `assess_coactivity` at its shipped settings.**
   - **Location:** `aim1_one_source.py`.
   - **Issue:** it runs with `n_surrogates=120` (shipped default 1000) and explicit K = 3, 4, 6, which bypasses the `k_from_fraction` and floor path. Cluster rate, participants and jitter come from the observation, so the Aim 0 comparisons are unaffected. Any surrogate-based number (excess, p) is not at shipped settings.
   - **Severity:** low.
   - **Fix:** note it in the record, or use 1000 for anything surrogate-derived.
   - **Verified:** yes (code).

9. **The run itself took a fallback path.**
   - **Location:** run record.
   - **Issue:** the GRANT mismatch above (editing tools held). The lit-cache tool (`fetch_paper.py`, `MURDERBOARD_LIT`) is absent. PySpike's annealer could not be run, so finding 2 uses local search as a lower bound on what annealing reaches.
   - **Severity:** low (about the run, not the artifact).
   - **Fix:** the `roles:` line should state the fallback. Add to the want-list: a compiled PySpike, for a direct annealed comparison.
   - **Verified:** yes.

**Not checked:** the ADR-0008 floor and `event_floor.py` claims, Charlier-noise results and count-detector claims reported from blind passes A and B. I did not derive the membership `1 + (E−1)/M` formula independently; its numerical check is in-file and plausible, and the file does not misuse any method.

**Scratch scripts** (all under `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\_scratch\role-06\`):
- `theory_checks.py`
- `f3_check.py`
- `order_opt.py`
- `pyspike_cmp.py`
- `src_dl\pyspike-0.9.0\` (the PySpike source)
