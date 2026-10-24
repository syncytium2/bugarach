# Synthetic validation: Aim 0 and Aim 1 records

Goal page: [`docs/goals/synthetic-validation.md`](../../goals/synthetic-validation.md). Synthetic
recordings only; nothing here reads a real recording.

| file | what |
|---|---|
| `aim1_one_source.py` | Aim 1a: one source, random membership. Simulates a grid (jitter 0.05/0.2/0.5/1 s, participation 0.15/0.3/0.6, 15 or 45 events, background 0.01 or 0.05 Hz per cell, 5 seeds; 33 cells, 45 min) and measures each recording blind with `measure_coordination_rates` (1, 2, 4 s windows) and `assess_coactivity` (K = 3, 4, 6 cells). About a minute on 24 workers. |
| `aim1_one_source.json` | its run record: planted values, every estimate and the raw excess cumulants per recording, plus 20 background-only recordings for the chance-cluster test |
| `theory.py` | Aim 0: the predictions (window sharing g_n with frame rounding, the exact excess cumulants passed through the tool's own `solve()`, the joint fit of jitter, participants and rate across windows, chance clusters at K); `check()` tests each against `aim1_one_source.json` per condition |
| `theory_check.json` | `theory.py`'s record: every prediction beside the measured median, per condition, with NaN and search-bound counts |
| `blind_README.md`, `blind_a/`, `blind_b/` | the two blind theory passes, kept as they ran |
| `aim1_one_source_shared_seeds.json` | the first Aim 1a record, whose cells shared five backgrounds; the blind passes ran on it |
| `membership_limit.py`, `membership_limit.json` | Aim 0: assembled against random participation as assemblies multiply (`bugarach.assembly.stat_dispersion`); prediction 1 + (E − 1)/M, and per-recording detection |
| `order_limit.py`, `order_limit.json` | Aim 0: an order indicator by score sort and by local search, with its closed forms (one template, M templates) and the fitted no-order constant across field sizes |
| `aim1_figure.py` | Figure 1, measured recovery against planted jitter (with the joint fit), to the darkroom and here |
| `aim0_figures.py` | Figures 2–4: predicted against measured; membership; order |
| `synth_recovery_plot_one-source-jitter_20261023.png` | Figure 1 |
| `synth_recovery_plot_one-source-predicted-against-measured_20261023.png` | Figure 2 |
| `synth_assembly-membership_plot_assemblies-converge-to-random_20261023.png` | Figure 3 |
| `synth_recovery_plot_order-indicator-closed-forms_20261023.png` | Figure 4 |

Reproduce, from the repository root:

    PYTHONPATH=src python docs/learned/synthetic_validation/aim1_one_source.py --workers 24
    PYTHONPATH=src python docs/learned/synthetic_validation/theory.py
    PYTHONPATH=src python docs/learned/synthetic_validation/membership_limit.py
    python docs/learned/synthetic_validation/order_limit.py
    PYTHONPATH=src python docs/learned/synthetic_validation/aim1_figure.py
    PYTHONPATH=src python docs/learned/synthetic_validation/aim0_figures.py

Pass `--out DIR --no-repo` to either figure script to write only to DIR. The captions and what
each figure shows are on the goal page.
