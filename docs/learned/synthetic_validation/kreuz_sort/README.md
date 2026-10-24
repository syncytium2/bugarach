# Does the Kreuz group have a fast sort or a null for the Synfire Indicator? (2026-10-24)

Tony asked two research agents to search the Kreuz group's literature, code and website for the
question the goal page left open (*Waiting on Tony*): does a fast, non-annealing sort, or an
analytical null for the Synfire Indicator, already exist? The lab had not followed this up before
because the indicator was slow. Both reports are kept verbatim, apart from local paths.

| file | what |
|---|---|
| `literature_report.md` | Kreuz et al. 2017, the PySpike paper, Kreuz et al. 2022, Mariani et al. 2025, the 2026 review, Satuvuori et al. 2020, Cecchini et al. 2021 and Tomlinson et al. 2019, with short quotes and sections |
| `code_report.md` | PySpike (master and the unmerged `Kevin` branch), cSPIKE v1.5, SPIKY v3.1 and the website, with files and line numbers |
| `compare.py`, `compare2.py` | the code agent's own re-implementation of PySpike's annealing schedule against a Borda sort plus insertion search, on synthetic order matrices. Not their code; output not saved |

**What they found, in brief.**
- **Sorting.** Every paper and codebase sorts by simulated annealing. It starts from the input
  order and swaps neighbours. The only stated reason is a travelling-salesman analogy (N! orders,
  2017 sec. 2.3). No ranking, Borda, greedy or insertion sort appears anywhere. SPIKY computes the
  row sum of the order matrix, our score, in its synfire plot and does not use it to sort.
- **The objective.** The order matrix is exactly antisymmetric and the normaliser does not depend on
  the order, so maximising the indicator is the linear ordering problem. Ranking by net wins is
  its standard approximation; the Kreuz papers do not cite this literature.
- **Null and bias.** The 2017 paper declines an analytical null and uses 19 order-swap surrogates,
  each re-annealed, which absorbs the finite-size bias without stating it. No formula for the
  bias, no expected no-order value and no closed form for one template appears in any source.
  The paper warns that the indicator cannot be compared across datasets with very different
  numbers of spikes.
- **Cost.** No source gives runtimes for the sort. The annealer is cheap per run in compiled code.
  The likelier cost is running it 20 times per test and building the matrix, often in MATLAB.
- **A tentative result, synthetic only.** In the re-implementation the annealer matches the Borda
  sort plus insertion search up to about 60 trains, and ends below it from about 100. If that
  holds on real order matrices, published values at large N are lower bounds that depend on the
  optimiser. Not yet confirmed.
- **Closest prior art to the score sort.** Mariani et al. 2025 replaced annealing with a direct
  row average, but for latency correction, not the order. Tomlinson et al. 2019, a clinical
  group, ranked electrodes by a net upstream–downstream score.

**What it means for the goal page.** The score sort, the c/√n̄ no-order bias and the one-template
closed form were not found in the group's work. The open question is now for Kreuz himself; a
draft note is with Tony.
