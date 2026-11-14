GRANT 6 MISMATCH — missing WebSearch, WebFetch (deferred, never loaded or used); holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch, mcp__claude_ai_Claude_Docs__update, mcp__claude_ai_Claude_Docs__guide (none used; nothing written outside scratch `work-r2-6/`)

# Role 6 — Methods / domain expert ("RTFM"), blind verify round 2

**Artifact:** `docs/dissertation/chapter-1-aim0.md`. I confirmed the hash cdc8fbf6afea9df5c496b218e3e5c99fc2a8c881 before reviewing.

## What I grounded in, and what holds up

**Code read against the chapter's description of each tool**
- **Coordination-rates tool** (`tools/measure_coordination_rates.py`). The chapter's description matches the code:
  - `factorial_cumulants` gives κ[2] and κ[3] of the population count.
  - Counts are non-overlapping bins at two offsets, 0 and w/2.
  - Surrogates shift each cell circularly by its own offset; offsets are distinct multiples of 2w.
  - The fixed model `solve` uses k = f3/f2 + 2 and λ = f2/(w k(k−1)), and refuses when f2 ≤ 0 or f3 ≤ 0.
- **The two excess formulas (1.4.2).** I re-derived both: the hard-core factorial cumulant, minus a surrogate made of N independent Bernoulli-like cells with κ[2] = −m² and κ[3] = 2m³. f₂ and f₃ come out exactly as printed, including (1 − 1/N) and (1 − 1/N²).
- **Assessor** (`src/bugarach/assess.py`): `merge_bins=2`, merging when `fire[q]-fire[q-1] <= 2`. **Count detector** (`src/bugarach/detectors/count.py`): `edges[b]-edges[prev+1] <= 3.0` with 2 s bins. Both mean "at most one untriggered bin between", so m = 2 and the half-plateau at 2.5 bins in 1.7 are correct. The run-start rule behind 60 q(1−q)² also matches the assessor.

**Closed forms recomputed independently** (scratch `chk.py`, `unif.py`)
- **g₂.** The closed form agrees with Monte Carlo to within 3e-4.
- **k̂/k** for 10-cell events is 0.907 at σ = w/6 and 0.451 at σ = w. Matches.
- **Gaussian against uniform g_n:** largest gaps 0.020 for g₂ and 0.036 for g₃. Matches "0.02 and 0.04".
- **Chance-cluster rates:**
  - 0.256 and 0.019 per minute at 0.01 Hz.
  - 7.97, 3.86 and 0.284 per minute at 0.05 Hz.
  - Smallest safe threshold: K = 5 at 0.01 Hz and K = 8 at 0.05 Hz. At 0.0096 Hz, K = 4 gives 0.983 per hour.
  - 0.23 expected clusters in the K = 6 arm.
- **Order indicator:**
  - (2/π) arctan r = 0.500 at r = 1 and 0.758 at r = 2.5.
  - c(33, 10) = 0.376.
  - (k−1)/(N−1) = 0.28.
  - The M-template prefactor at r = 2.5 is 0.649.
- **Statistics:**
  - Sign tests: 24/32 p = 0.007, 18/32 p = 0.60, 35/48 p = 0.002, 18/48 p = 0.11.
  - Clopper–Pearson interval for 8/60: 5.9–24.6 %.

**Source papers read against the claims they support**
- **Kish 1995, p. 63** (rendered from the scan): roh = (deft² − 1)/(n/a − 1). So deft² = 1 + roh(b̄ − 1) is as cited.
- **Grün et al. 1999, eq. 5:** the fission probability. Correct.
- **Louis, Borgelt & Grün 2010:**
  - Fig. 7 legend: "two straight lines with disjoint regions". Correct.
  - Fig. 6 shows multiple groups, which "become hard to disentangle as their sizes converge". Correct.
- **CuBIC eq. 3:** κ_m[Z] = ν μ_m[A]. Correct.
- **Coppersmith et al.:** the 5-approximation needs the "probability constraints" w_uv + w_vu = 1. Correct.
- **Shah & Wainwright:** they assume observations are independent across pairs. Correct.
- **Kreuz et al. 2017:** the "not sufficient to reliably compare" quote is in the text.
- **Thomas 1949:** quadrat counts only. Correct.
- **Kruskal 1958:** see finding 6.

**Numbers checked against the records**
- `theory.py --from-record`, `ch1_followups/like_for_like.txt` and `correlogram_vs_joint.txt` reproduce every 1.4.4–1.4.6 number I checked.
- `separation/assessor_split/derivation.md`: 72 recordings × 400 pairs = 28,800 pairs, at 576 points of n = 400. So "28,800 pairs" (1.7) and "400 pairs each" (Fig. 1.10) are consistent.

**Shipped settings**
- The coordination-rates validation calls `mcr.measure` with its defaults: windows 1, 2 and 4 s, 20 surrogates.
- The assessor's chance arm uses 20 surrogates and the main arm 120. Cluster counts don't depend on the surrogate count, so this is fine.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source |
|---|---|---|---|---|---|
| 1 | 1.4.6, "Against the correlogram tool, run as shipped on the same 240 recordings (Table 1.2)"; also 1.8 ("beats the existing bin-free estimator above about 0.5 s jitter") and 1.10 | **The correlogram is not run as shipped.** The shipped tool pools the numerator and denominator over recordings before dividing (`tools/measure_jitter_correlogram.py` docstring and `main()` → `pooled(real)`), and its calibration is pooled too. Table 1.2 applies it to one 45-minute recording at a time. The follow-up record itself prints the shipped, pooled reading, and it changes the busy-background result: at 0.05 Hz it reads 0.89 [0.83–1.11] at 0.5 s and 0.94 [0.88–0.99] at 1.0 s (2 of 4 conditions off the curve). The per-recording table gives 0.81 and 0.42. At 0.01 Hz and 1 s, the "failure" is the calibration grid ending at 1.0 s. The same widths read through the plain Gaussian conversion give 0.97 [0.91, 1.08], with none off. So "it fails at 1 s" and "the joint fit is better … at the busier background" depend on per-recording use and on the calibration's range. | major | Call Table 1.2 what it is: a per-recording use of the correlogram's estimator, which is not how the tool ships. Add the pooled column, the shipped form, beside it. Say the 0.01 Hz, 1 s miss is a calibration-range limit. Restate the comparison as "per recording, the joint fit is better from 0.5 s up". Soften 1.8 and 1.10 to match. | yes (`ch1_followups/correlogram_vs_joint.txt`, tool source) |
| 2 | 1.4.6, "On realistic event trains the fit takes the train's measured intervals"; "Participants (0.97–1.05) and rate (0.86–1.03) are tight"; "Without the general form … 1.62 and 1.43 times planted" | **The general-form fit is given the generator's own interval law.** It gets `EventTrain.renewal(intervals=gaps)`, the same gap list the recordings were simulated from, plus `n_events = m_bar` (`ch1_followups/lab_values.py`, lines 62 and 89). On real data, the event train's pair correlation is unknown until the events have been found, so this is an oracle input. The `n_events` term is only a CV²/m correction (`event_train.fixed_count`); the interval law is what matters. That is exactly the part that removes the 1.62× and 1.43× jitter bias. As written, "measured intervals" reads like something available from the recording. The tight participant and rate results are conditional on knowing the train. | major | Say that the fit was given the true interval distribution, and that on data it must come from somewhere, such as a detector's intervals or an iterated estimate. Either test the fit with a misspecified or estimated train, or state the result as an upper bound. Add this to the 1.9.4 limitations. | yes (code) |
| 3 | 1.3, "Every prediction is passed through the tool's own estimator, so prediction and measurement are the same calculation" | **Not the same calculation.** The prediction is `solve(E[f₂], E[f₃])`, the estimator applied to the expected cumulants. The measurement is the median over recordings of `solve(f̂₂, f̂₃)`. Because k̂ = f₃/f₂ + 2 is nonlinear, the two can differ even under an exact theory. I sized the gap from the per-recording cumulants in both records, comparing median(k̂) with the ratio of means, for events of 10 or more cells. The systematic part is small: median −0.0008 to −0.0014 of k, mean up to −0.0035 on the held-out record at 0.01 Hz. Per-setting signs are not significant (p ≥ 0.21). So it does not explain the ~1 % overprediction, but it is a real, unstated component of every residual. | minor | Reword it, for example: "the prediction is the tool's estimator applied to the expected cumulants". Add one sentence that the median-of-ratio versus ratio-of-means gap is about 0.1 % of k on these records, so it is negligible beside the 1 % residual. | yes (own computation from `aim1_one_source.json`, `aim1_one_source_heldout.json`; scratch `ratio.py`) |
| 4 | 1.5, "Whether a planted event reaches K is not modeled here"; 1.8 "It does not predict whether a planted event reaches a threshold"; 1.9.5 item 3 | **Contradicted by 1.7 and its derivation.** `separation/assessor_split/derivation.md` computes π_K (the chance one event reaches K) and P(at least one cluster) exactly, with the `dp_groups` recursion. The prediction matched simulation: 205 informative points, z mean −0.02, SD 0.91. The chapter uses π_K itself in 1.7. | major (internal inconsistency on scope) | Say that per-event detection *is* predicted for isolated pairs at the separation grid's settings (the 1.7 recursion). Then narrow the "not modeled" claim to whatever remains, such as the assessor's reported participants and jitter, or the 1.5 recall figures, if those really weren't compared. | yes |
| 5 | 1.4.4, "because the standard error of a median of 5 values is heavy-tailed" | **Wrong object, and a hidden assumption.** What is heavy-tailed is the z-statistic built from an SE *estimated* from the same 5 values (1.2533·SD with ddof 0, divided by √5; `theory.summary`). Its null rate of 0.118 was simulated assuming the per-recording estimates are normal. If k̂ is skewed, the "about 6 expected" is off. Separately, the pooled sign test (24/32, p = 0.007) pools in a record that was used for model choices, including the frame term, which changes g_n and so the k̂ prediction. Each record alone gives 12/16 (p = 0.077). | minor | Reword it, for example: "a z with the SE estimated from the same 5 recordings has heavier tails than normal; its null rate, 0.118, was simulated under normal errors". Report the held-out sign test alone beside the pooled one. | yes (code) |
| 6 | 1.6.2, "τ = (2/π) arcsin ρ (Kruskal 1958, derived in secs. 3–4)" | **Overstated.** Kruskal *states* the relation; he does not derive it. In sec. 3 he gives the quadrant-measure version and cites Cramér (p. 290). In sec. 4 he calls the τ form "a direct consequence". The only worked derivation in Kruskal is for ρ_s, in sec. 6. The Esscher credit is fair: Kruskal says Esscher stated τ's population meaning and worked in the bivariate normal case. | minor | Change to "stated in secs. 3–4, citing Cramér". | yes (Kruskal text, lines 400–402 and 564–567) |
| 7 | 1.4.6, "its own calibration … reads 3–14 % low on this one" | The source (`ch1_followups/README.md`) limits this to 0.2–1.0 s and, in context, to 0.01 Hz. At 0.05 Hz and 0.5 s, the calibrated per-recording reading is 0.81, which is 19 % low. The chapter drops both qualifiers. | minor | Add "at 0.01 Hz, 0.2–1.0 s", or give the range across both backgrounds. | yes |
| 8 | 1.6.2 and Fig. 1.8, "randomized to an exact 5 % size" | Exact only against the empirical 3,000-recording null (`order_power.py`: c and γ come from `big`), not against the true null. The Monte Carlo error on a 5 % tail from 3,000 draws is about ±0.4 points. | minor | Change to "randomized to 5 % against a 3,000-recording null". | yes (code) |
| 9 | 1.6.2 order results generally, and 1.9.4 item 4 | **No frame grid in the order simulations.** The power table uses σ = 0.2 s with no frames. At the chapter's realistic σ (0.105 s) and 0.1 s frames, ties within an event become common, and F's handling of ties isn't specified. Limitation 4 discloses a 9 % drop from rounding, but only from a review agent's test that wasn't kept, and the r-scaling argument fails once ties appear. | minor | Either rerun one row of Table 1.3 with frame rounding and stated tie handling, or say explicitly that Table 1.3 does not cover realistic σ at the 0.1 s frame. | partly (code; no rerun) |
| 10 | 1.4.5, "but not on the held-out record (18 of 48, p = 0.11)" | Accurate, but on the held-out record the rate sign *reverses*: measured is below predicted in 30 of 48. "Not on the held-out record" reads as if the bias merely disappeared. | minor | Add "(where the sign reverses)". | yes |

## Bottom line for sign-off
Most of the method is correct as derived and as implemented in the tools. Every core formula and tool convention I checked against code and source holds: g₂, f₂, f₃, k̂, the chance-cluster rate, m = 2, Kish, CuBIC, Grün, Louis and Coppersmith. The two changes I would require before signing are both about validation:
- **Finding 1:** the correlogram comparison must use the tool as shipped, or say plainly that it doesn't.
- **Finding 2:** the realistic-values joint fit is given the true event-train law, and the chapter must say so.

I would also require finding 4 (the chapter contradicts itself on whether per-event detection is modeled). The rest are wording fixes.

**Residuals:** no paywalled sources were needed beyond the local shelf. I did not check the M-template asymptote's derivation or the F_Kreuz normalization against Kreuz's code beyond the arithmetic.
