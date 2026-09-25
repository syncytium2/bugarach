---
status: open
opened: 2026-09-25
area: bench figures; ADR-0009 follow-up
waits_on: nobody
---

# Eight figure and report tools still read the stretch off the planted bench recording

ADR-0009 decision 1 (PR A of the final-parameters night) took the elevated-rate stretch off
`BENCH_RECORDING` on the fast, slow and combined benches and put it in `ELEVATED_RATE_RECORDING`.
The scoring path, the search, the fresh-seed scorer, the floor probe and the two measurement tools
that compare against the stretch (`measure_coordination_rates.py`, `measure_rate_stretches.py`)
were moved with it.

These tools draw or describe the bench as it was when their run was made, and read
`BENCH_RECORDING["hot_window"]` or `gt.params["hot_window"]` off a planted recording. Rerun on the
current bench they raise, since that value is now `None`:

- `tools/build_fair_comparison_report.py` (Figure 1's probe row; the stretch rate in the text)
- `tools/make_replicate_report.py`
- `tools/make_methods_bench_figure.py`
- `tools/make_clutter_edge_figure.py`
- `tools/make_intro_figures.py`
- `tools/make_chorus_context_span_figures.py`
- `tools/probe_flat_vs_fitted.py`
- `tools/probe_rate_mechanism.py`

Their published outputs are unaffected: each describes a run whose bench did carry the stretch.
**Fix each one when it is next rebuilt**, rather than tonight: the fix is a change to the picture,
not a one-line rename. A planted recording no longer has a probe row to draw; the probe belongs
in a figure of its own recording.
