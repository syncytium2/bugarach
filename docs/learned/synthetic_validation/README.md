# Synthetic validation: Aim 0 and Aim 1 records

Goal page: [`docs/goals/synthetic-validation.md`](../../goals/synthetic-validation.md). Synthetic
recordings only; nothing here reads a real recording.

| file | what |
|---|---|
| `aim1_one_source.py` | Aim 1a: one source, random membership. Simulates a grid (jitter 0.05/0.2/0.5/1 s, participation 0.15/0.3/0.6, 15 or 45 events, background 0.01 or 0.05 Hz per cell, 5 seeds; 33 cells, 45 min) and measures each recording blind with `measure_coordination_rates` (1, 2, 4 s windows) and `assess_coactivity` (K = 3, 4, 6 cells). About a minute on 24 workers. |
| `aim1_one_source.json` | its run record: planted values, every estimate and the raw excess cumulants per recording, plus 200 background-only recordings (100 per background) for the chance-cluster test |
| `theory.py` | Aim 0: the predictions (window sharing g_n, the excess cumulants with the at-most-one-event term, passed through the tool's own `solve()`, the joint fit of jitter, participants and rate across windows, chance clusters at K); `check()` tests each against `aim1_one_source.json` per condition |
| `theory_check.json` | `theory.py`'s record: every prediction beside the measured median, per condition, with NaN and search-bound counts . `theory.py --from-record` prints the page's Aim 0 and Aim 1a numbers from the two records without rerunning |
| `event_train.py` | 2026-10-28: the coordination-rates prediction for any stationary event train, ported from [`separation/real_intervals/`](separation/real_intervals/derivation.md). `EventTrain.poisson()`, `hard_core(d)`, `renewal(intervals \| density, mean)`, `palm(intervals, lam)` for real data (untested on real data), `from_times(...)`, and `.fixed_count(m)`; `coefficients(w, sigma, n_cells, train)` gives f2, f3's coefficients with the tool's own surrogate, cached on the train. `theory.py` takes it as `train=` in `predicted_excess_cumulants`, `predict_solve` and `fit_joint`; without `train` it is unchanged |
| `theory_check_empirical.json`, `theory_check_analytic.json`, `theory_check_hardcore-dependent.json` | `theory.py --train <name>`: `check()` again under the general form, for the generator's empirical pair correlation (20 000 redrawn trains; the run record has no event times), its analytic interval law, or the 20 s hard core with the tool's surrogate. Each row also keeps the page's prediction and solve() on the condition's mean f2, f3. `--train <name> --from-record` reprints them, with the page and general residuals side by side. `theory_check.json` is untouched |
| `theory_check_real.json`, `theory_check_real.txt` | `theory.py --check-real`: 40 recordings per k (7, 13) of a renewal train of real fast-stream gaps, measured with the shipped tool; the page's form against the general form (renewal and Palm) and the joint fit under each. The `.txt` is the run's printout |
| `blind_README.md`, `blind_a/`, `blind_b/` | the two blind theory passes, kept as they ran |
| `separation/` | 2026-10-25: the minimum separation of two events: the floor for any method, the assessor's and count detector's split probability, and the coordination-rates prediction for events that can share a window |
| `kendall_w/` | 2026-10-24: the no-order mean of the order indicator under the score sort, derived exactly (Durbin / Skillings–Mack rank-sum covariance; Kendall's W when every cell joins), c = √(4(k + 1)/(3πN)), with the checking script and its output |
| `prior_art/` | 2026-10-24: four more searches (Grün's literature, the Elephant code, other order literature, a naive cross-field survey) and one verdict table: what in Aim 0 was already known |
| `kreuz_sort/` | 2026-10-24: two agents' search of the Kreuz group's literature, code and website for a fast sort or an analytical null for the Synfire Indicator (none found), with a synthetic annealer-versus-Borda comparison |
| `aim1_one_source_shared_seeds.json` | the first Aim 1a record, whose conditions shared five backgrounds; the blind passes ran on it |
| `membership_limit.py`, `membership_limit.json` | Aim 0: assembled against random participation as assemblies multiply (`bugarach.assembly.stat_dispersion`); prediction 1 + (E − 1)/M, and per-recording detection by the package's `AssemblyResult.verdict()` |
| `order_limit.py`, `order_limit.json` | Aim 0: an order indicator by score sort and by local search, with its closed forms (one template, M templates), the fitted no-order constant across field sizes, and the no-order indicator's mean and spread at small event counts |
| `aim1_figure.py` | Figure 1, measured recovery against planted jitter for events of 10+ cells (with the joint fit), to the darkroom and here |
| `aim0_figures.py` | Figures 2–4: predicted against measured; membership; order |
| `synth_recovery_plot_one-source-jitter_20261023.png` | Figure 1 |
| `synth_recovery_plot_one-source-predicted-against-measured_20261023.png` | Figure 2 |
| `synth_assembly-membership_plot_assemblies-converge-to-random_20261023.png` | Figure 3 |
| `synth_recovery_plot_order-indicator-closed-forms_20261023.png` | Figure 4 |

Reproduce, from the repository root:

    PYTHONPATH=src python docs/learned/synthetic_validation/aim1_one_source.py --workers 24
    PYTHONPATH=src python docs/learned/synthetic_validation/theory.py
    PYTHONPATH=src python docs/learned/synthetic_validation/theory.py --train empirical   # also analytic, hardcore-dependent
    PYTHONPATH=src python docs/learned/synthetic_validation/theory.py --check-real
    PYTHONPATH=src python docs/learned/synthetic_validation/membership_limit.py
    python docs/learned/synthetic_validation/order_limit.py
    PYTHONPATH=src python docs/learned/synthetic_validation/aim1_figure.py
    PYTHONPATH=src python docs/learned/synthetic_validation/aim0_figures.py

Pass `--out DIR --no-repo` to either figure script to write only to DIR. The captions and what
each figure shows are on the goal page.

## Prior art

What the goal page's Aim 0 rests on, and how far each source was read. ⚠ marks a source not
opened, or read as abstract only.

**Window sharing and the joint fit.**
- The generator is a Neyman–Scott cluster process (Neyman & Scott 1952, *ApJ* 116:144, restated
  1958 in *J R Stat Soc B* 20:1; ⚠ abstract only). Its Gaussian-scatter case is now called the
  Thomas process, after Thomas 1949 (*Biometrika* 36:18; ⚠ not opened). Here the number of events
  is fixed and they are held apart rather than Poisson-placed.
- The coordination-rates tool's route is CuBIC's cumulant route (Staude, Rotter & Grün 2010,
  *J Comput Neurosci* 29:327; read) on the multiple-interaction model of Kuhn, Aertsen & Rotter
  2003 (*Neural Comput* 15:67), with factorial rather than ordinary cumulants.
- Grün et al. 1999 (*J Neurosci Methods* 94:67; read) derived the two-onset, uniform-jitter case
  of window sharing ("fission probability") and read the coincidence width from the analysis
  width; it credits the effect to Grün's 1996 thesis (⚠ not opened). Pazienti et al. 2008
  (*Brain Res* 1225:39; ⚠ abstract only) estimated synchronization precision from how detection
  decays with the dither width at one fixed window.
- Louis & Grün 2009 (*BMC Neurosci* 10(Suppl 1):P253; read) and Louis, Borgelt & Grün 2010
  (*Neural Netw* 23:705; ⚠ abstract only) fit group size and jitter together by following the
  population count's distribution across bin widths, on the complexity distribution of Grün,
  Abeles & Diesmann 2008 (*LNCS* 5286:96). This is the joint fit's closest precedent.
- In spatial statistics a Thomas process's scatter and parent rate are fitted by minimum contrast
  on its pair-count curve across scales (Pfanzagl 1969, *Metrika* 14:249; Diggle & Gratton 1984,
  *J R Stat Soc B* 46:193; Waagepetersen 2007, *Biometrics* 63:252; ⚠ software documentation
  read, not the papers).
- Not found in the sources read: g_n for Gaussian jitter and n onsets, the pair-and-triple form
  with the at-most-one-event term, and the event rate in the same fit. ⚠ Not searched:
  quadrat-variance ecology, physics counting statistics, composite and Palm likelihood for
  cluster processes (Guan 2006; Tanaka, Ogata & Stoyan 2008).

**Membership.** Kish's design effect (1965; ⚠ book not opened) has the form of 1 + (E − 1)/M.
The detectability threshold for planted low-rank structure (plan item 6) is random-matrix theory:
Baik, Ben Arous & Péché 2005 (*Ann Probab* 33:1643) and Baik & Silverstein 2006 (*J Multivariate
Anal* 97:1382; ⚠ neither opened). The PCA assembly method with a Marchenko–Pastur null comes from
Peyrache et al. 2009 (*Nat Neurosci* 12:919) and 2010 (*J Comput Neurosci* 29:309), building on
Chapin & Nicolelis 1999 (*J Neurosci Methods* 94:121); Lopes-dos-Santos et al. extended it in 2011
(*PLoS ONE* 6:e20996; read) and restated it in 2013 (*J Neurosci Methods* 220:149).

**Likelihood bounds** (plan item 7). Wang, Degleris, Williams & Linderman (*JASA* 119:2382, 2024)
do Bayesian inference for Neyman–Scott processes; PP-Seq (Williams, Degleris, Wang & Linderman,
NeurIPS 2020) is a Neyman–Scott process with per-neuron offsets.

**Order.**
- Kreuz, Satuvuori, Pofahl & Mulansky 2017 (*New J Phys* 19:043028; read): SPIKE-order and the
  Synfire Indicator, eq. 14, the surrogates (sec. 2.5) and the finite-size effect (sec. 3.1).
- Kreuz et al. 2022 (*J Neurosci Methods* 381:109703) introduced latency correction by annealing;
  Mariani et al. 2025 (*J Neurosci Methods* 416:110378; arXiv 2410.15018) replaced it with a direct
  shift (9.7 s against 861.8 s on one 183-train dataset, read in the arXiv version). Kreuz's
  review (*Biol Cybern* 120(3–4):21, 2026; doi 10.1007/s00422-026-01045-5) still sorts by
  annealing. Cecchini et al. 2021 (*PLoS Comput Biol* 17:e1008963; read with its S2 Appendix)
  applied the framework to wide-field calcium imaging. The full search of the group's work is in
  [`kreuz_sort/`](kreuz_sort/README.md).
- Greiner's relation via Kruskal 1958 (*JASA* 53:814; ⚠ neither opened).
- Sorting by net wins comes within a factor of 5 of the fewest disagreements when each pair's
  weights sum to 1 (Coppersmith, Fleischer & Rudra, SODA 2006, *ACM Trans Algorithms* 6(3), 2010;
  ⚠ abstract). Borda counting is optimal up to constants for top-k recovery from noisy pairwise
  comparisons (Shah & Wainwright 2018, *JMLR* 18(199); ⚠ abstract).
- ⚠ Not searched: hippocampal replay and cortical sequence rank-order methods (Lee & Wilson 2002,
  *Neuron* 36:1183; Luczak et al. 2007, *PNAS* 104:347).

**Correspondence.** The repository's letters with Kreuz (April 2026; the August–September
`max_tau` thread) do not cover a fast sort or an analytical null; the goal page's *Waiting on
Tony* holds the open question.
