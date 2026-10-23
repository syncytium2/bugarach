# Synthetic validation: Aim 1 records

Goal page: [`docs/goals/synthetic-validation.md`](../../goals/synthetic-validation.md). Synthetic
recordings only; nothing here reads a real recording.

| file | what |
|---|---|
| `aim1_one_source.py` | Aim 1a: one source, random membership. Simulates a grid (jitter 0.05/0.2/0.5/1 s, participation 0.15/0.3/0.6, 15 or 45 events, background 0.01 or 0.05 Hz per cell, 5 seeds; 33 cells, 45 min) and measures each recording blind with `measure_coordination_rates` (1, 2, 4 s windows) and `assess_coactivity` (K = 3, 4, 6 cells). About a minute on 24 workers. |
| `aim1_one_source.json` | its run record: planted values and every estimate, per recording |
| `aim1_figure.py` | Figure 1, recovered ÷ planted against planted jitter, to the darkroom and here |
| `synth_recovery_plot_one-source-jitter_20261023.png` | Figure 1 |

Reproduce, from the repository root:

    PYTHONPATH=src python docs/learned/synthetic_validation/aim1_one_source.py --workers 24
    PYTHONPATH=src python docs/learned/synthetic_validation/aim1_figure.py

What Figure 1 shows is on the goal page, *Aim 1a, first result*.
