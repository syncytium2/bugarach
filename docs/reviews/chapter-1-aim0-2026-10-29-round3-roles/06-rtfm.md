GRANT 6 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred, loadable via ToolSearch), plus PowerShell, Agent, Artifact, Skill and MCP write tools (Claude Docs batch/update, Gmail, Dropbox). I used only Read, Grep, Glob and Bash. I wrote nothing outside `scratchpad/mb/work-r3-6/`. WebSearch and WebFetch were held (deferred) but I did not need them.

# Role 6 (RTFM, methods expert): blind verify, round 3
Artifact: `docs/dissertation/chapter-1-aim0.md`, hash a4fbb30ebe9e70313f10034927ccf32341948290 (I confirmed the hash).

## What I checked against the code and the sources (these held up)
- **g₂ closed form (1.4.2)**: matches Monte Carlo at w/σ = 5, 1 and 4 to 4 decimals.
- **k̂/k for 10-cell events (1.4.2)**: 0.907 at σ = w/6 and 0.450 at σ = w, using `theory.g`.
- **Uniform vs Gaussian jitter (1.4.2)**: largest gap 0.021 (g₂) and 0.034 (g₃) by Monte Carlo, inside the stated 0.02 / 0.04.
- **f₂ and f₃ (1.4.3)**: I re-derived both as factorial cumulants, assuming an independent surrogate. They match `theory.py` and `separation/real_intervals/derivation.md` §5.
- **Coordination-rates tool**: `factorial_cumulants`, the two offsets (0 and w/2), `solve()` (k̂ = 2 + f₃/f₂) and N_SURR = 20 all match the shipped defaults in `tools/measure_coordination_rates.py`.
- **Assessor (`src/bugarach/assess.py` `_clusters`)**:
  - merge rule `merge_bins = 2`
  - center = mean of the bin centers
  - gather of the nearest onset within ±1.5 s, kept at ≥ K cells
  - SD with ddof = 1, then the median over clusters
  - The run-start factor q(1−q)² follows from the merge rule.
- **Chance-cluster rates and thresholds (1.5.1)**:
  - Rates 0.2558 / 0.0191 / 7.973 / 3.860 / 0.2838 per minute.
  - Smallest thresholds under one chance cluster per hour: K = 5, 8 and 4 (0.983 per hour at 0.0096 Hz).
  - All reproduced from the formula.
- **Count detector**: 2 s bins with `merge_gap_sec = 3` gives "at most one uncalled bin", and the separation script calls it that way.
- **Truncated-Gaussian ceiling (1.5.2)**: 0.7426 s.
- **Sign tests**:
  - 24/32 gives p = 0.0070; 18/32 gives 0.597; 35/48 gives 0.0021; 18/48 gives 0.111.
  - The 95 % interval for 8/60 is 5.9–24.6 %.
- **Order-indicator constants (1.7.2)**: c(33, 10) = 0.3761; the many-template asymptote is 0.649; (2/π) arctan r is 0.500 and 0.758; the ρ = r/√(1+r²) mapping holds.
- **Residuals, ranges and counts in 1.4.4–1.4.6**: checked against `ch1_followups/like_for_like.txt` and `theory.py --from-record`, which I reran.
- **Table 1.2**: matches `ch1_followups/correlogram_table.txt`.
- **Randomized exact-size test**: implemented correctly in `order_power.py`.
- **Frame rounding and g_n**: the claim agrees with the `s_eff` docstring.
- **Joint-fit bound**: `SIGMA_BOUNDS = (0.005, 5.0)`.
- **Kish 1995 pp. 63–64**: I rendered the scanned pages and read them.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source |
|---|---|---|---|---|---|
| 1 | 1.2.2, "the assessor reports the median over all its clusters"; 1.1 failure 2; 1.5.2 | **The assessor's jitter output is read without its paired null.** `assess.py` (module docstring, statistic 2) defines the jitter output as "the SD of participating ROIs' onsets within a co-active cluster, **against the same statistic computed on every surrogate**". It returns `jit_obs`, `jit_null` and `jit_excess` together, and its headline is the surrogate-corrected `coact_excess`. The chapter treats bare `jit_obs` as "the assessor's jitter reading" and calls the flat reading a tool failure. The first experiment (`aim1_one_source.py`) ran 120 surrogates against a shipped 1000 and kept only observation outputs, so `jit_null` was never looked at. The chance-cluster contamination that 1.5.2 derives is the thing the tool's null comparison exists to handle. Separately, the mixture's "chance part taken from simulation" is what the tool already estimates per recording as `jit_null`. | major | Describe the null comparison in 1.2.2. Say explicitly that 1.1 and 1.5.2 analyze the observed component only. Report `jit_null` / `jit_excess` on the same 240 recordings at the shipped 1000 surrogates. Consider using the tool's own `jit_null` as the chance-cluster spread, which would make the mixture per-recording rather than semi-analytic. | yes |
| 2 | 1.3, "the measurement is the median over recordings of the same estimator applied to each recording's counts"; "The tool refused … in 17 of 720"; "that gap is about 0.1 % of k" | **The validated estimator is not the tool's reporting path.** Shipped `summarize()` → `per_recording()` pools f₃/f₂ across recordings, weighted by window count ("one recording's f3 is noisy"), and then takes each recording's λ from its own f₂. So the shipped per-recording k is the same for every recording, and the shipped path cannot refuse one recording. The chapter validates per-recording `solve()` followed by a median of 5, which is a different estimator. The nonlinearity gap is also quoted for k only. `separation/real_intervals/derivation.md` §7.2 records that the median of five per-recording `solve()` **rate** ratios runs about 0.008 above `solve()` on pooled cumulants "under every prediction". That is about 40 % of the general-form median rate residual (0.020) and more than half its bias (+0.013) quoted in 1.4.5. | major | State which estimator is validated (per-recording `solve()`), and that the shipped report pools f₃/f₂. Report the residuals on the pooled path; `theory.py check` already writes a "pooled" column. Restate the nonlinearity gap for rate (about 0.008) beside the rate residuals. | yes |
| 3 | 1.2.2, "shifted in time by its own random offset"; Figure 1.3 A caption; 1.4.3, "it carries each cell's coordinated onsets … but scatters them. The excess pair and triple counts the tool measures are then" | **The surrogate is described wrongly, and the 1.4.3 formula silently assumes the wrong surrogate.** `shifted()` does not draw independent random offsets. It uses a random permutation of lattice multiples of 2w, so every two cells sit at least 2w apart and the offsets span 64 s at 1 s and 256 s at 4 s. That lattice is why the surrogate depends on the event train: 48 % of cell pairs at w = 1 s are offset by less than the 20 s hard core (derivation §4). The surrogate's own f₂ is 4–15× the independent-offset value (§7.1), which is about +0.4 to +1 % of the excess f₂ and is the identified cause of the 1 % participant/rate bias. 1.4.3 presents the hard-core formulas as "the excess counts the tool measures", although they assume independent offsets. 1.4.5 admits the omission, but 1.2.2 never says what it is. | major | Describe the lattice offsets in 1.2.2 and in the Figure 1.3 caption. In 1.4.3, say the hard-core form takes the surrogate's offsets as independent, which the tool's lattice violates, and give the size (§7.1). | yes |
| 4 | 1.7.2, "(Copeland's rule…)"; 1.1 contribution 7, "the ranking it uses is Copeland's"; 1.7.2 last paragraph; Table 1.6 | **The ranking is misattributed.** The score is the sum of net pairwise margins over events (Figure 1.3 C: +3, +5, −3, −5). The repository's own derivation calls this a Borda count, equivalent to Durbin's centered rank sum (`kendall_w/derivation.md` §1), and so does `kreuz_sort/code_report.md` ("Borda when D is weighted, Copeland when sign(D) is used"). Classical Copeland (1951, cited ⚠ and unread) counts pairwise-majority wins. On Figure 1.3 C that would score cells 1 and 2 as +2 each, which is a different order. Shah & Wainwright's "Copeland counting" (summed wins, "a special case of the Borda count") supports the chapter's usage. Coppersmith et al. call it "Borda's method". | minor | Call it the Borda (row-sum) score, "Copeland counting" in Shah & Wainwright's sense. Drop the attribution to Copeland 1951 as a rule, or qualify it. | yes |
| 5 | 1.7.2, "No order. … the mean of F is exact for every N, k and E" | **The exactness claim omits its tie assumption.** The derivation's assumption A2 requires continuous onsets with no ties. At the 0.1 s frame, 19.6–26 % of pairs tie (1.7.2's own rounding paragraph), so the mean is not exact for production-rounded onsets. The rounding paragraph only mentions powers. | minor | Add "for continuous (unrounded) onsets", and note that rounding pulls the null mean down. | yes |
| 6 | 1.2.2, "converts the width to jitter through a calibration curve"; 1.4.6 | **The calibration's conditions are not stated.** The calibration was built on the fast bench (its participation, event rate, silent and hot cells, distractors, elevated-rate stretch). The tool's docstring says the conversion holds "at the bench's participation and rate", and `correlogram_vs_joint.py` says the curve was used outside those conditions. Applying it to the flat-field grid at 0.05 Hz with 10–20-cell events is outside calibration. The Gaussian column is also low there, so the conclusion survives, but the shipped-curve column is partly confounded. | minor | State in 1.2.2 or in the Table 1.2 caption where the curve comes from and what it holds fixed. | yes |
| 7 | 1.7.1, Figure 1.12 B, "with 200 surrogates per null" | **The membership test was not run at shipped settings.** `membership_limit.py` uses N_SURR = 200, against the shipped `assess_assemblies` default of 1000. The verdict is Bonferroni at α/2 per statistic. At the borderline point (reuse 0.045, 8/60) the p-value granularity (1/201 vs 1/1001) can move calls. | minor | Rerun the low-reuse points at 1000, or say the setting differs from shipped. | yes (setting); effect not measured |
| 8 | 1.4.6, "The dependence on w enters only through g₂ and g₃" | **Imprecise wording.** w also enters explicitly through p = λw. What is meant is that σ enters only through g_n. | minor | Reword to "σ enters only through g₂ and g₃, which change with w". | yes |
| 9 | 1.7.1, "deft² = 1 + roh(b̄ − 1), with b̄ the mean cluster size … (Kish 1995, pp. 63–64; it is the intraclass correlation)" | **The citation does not match the cited pages.** Kish 1995 p. 63 gives roh = (deft² − 1)/(n/a − 1), calling it a "synthetic but useful ratio of homogeneity". p. 64 gives deft² = 1 + roh(n_c/a − 1). The b̄ notation and the intraclass-correlation gloss are not on those pages. | minor | Use Kish's n/a notation, or cite Kish 1965 for b̄. Source the intraclass-correlation reading separately. | yes |
| 10 | 1.4.6, "Events of 5 cells read anywhere from 0.1 to 3.6 times planted" (follows "held-out") | **Wrong record quoted.** 0.10–3.56 is the first experiment. The held-out record gives 0.10–3.71 (`like_for_like.txt`). | minor | Say which record, or quote both. | yes |

## Residuals
- I did not open Copeland 1951 (unpublished notes, ⚠).
- I did not check how the event floor ("6 and 12 cells", sliding 2 s scan) was computed.
- I did not verify the many-template asymptote's derivation beyond its value.
- No paywalled DOIs are needed for these findings.

## Sign-off
I would sign once findings 1–3 are addressed.
- Findings 1 and 2 are cases where the chapter tests or critiques something other than the shipped tool's output: the assessor's jitter without its null, and the per-recording `solve()` instead of the pooled report.
- Finding 3 misdescribes the surrogate that the general-form result depends on.
- Findings 4–10 are wording, attribution and assumption fixes.

Scratch work is in `scratchpad/mb/work-r3-6/`: `chk.py` and the rendered Kish pages.
