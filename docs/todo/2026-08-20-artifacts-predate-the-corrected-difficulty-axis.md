---
status: open
filed: 2026-08-20
---

# Committed figures and learned/*.json were computed at the old difficulty axis

`bench.REGIMES` moved on 2026-08-20 (PR #184): `baseline_quiet` 0.0038 → 0.0052,
`baseline_busy` 0.0175 → 0.0190, re-derived from the export folder rather than the `.mat`
store. **Every committed artifact that scored a detector predates it.**

They are stale, and — this is the problem — **they do not look wrong.** A figure drawn at
the old endpoints renders identically in shape; only the numbers underneath moved, and
they moved by less than seed noise. Nothing will fail. Somebody will quote them.

## What is affected

Anything produced by a tool that reads `REGIMES`, which is:

    docs/learned/bakeoff.json + bakeoff.md + bakeoff.png
    docs/learned/learned_results.json, learned_*.png/html
    docs/learned/regime_shift.json
    docs/learned/tolerance_sweep.json
    docs/learned/model_track.html, architecture_fitted.*
    the generator sweep figures (make_generator_figures.py)
    docs/learned/assessment_real.json  — only if regenerated against the bench

`docs/generator.md` also carries three **realized-total ratios** — 0.0114 against a
nominal 0.0038 (3.0×) and 0.0255 against 0.0175 (1.5×) — measured at the old endpoints and
flagged stale in place rather than recomputed. The point they make survives (a nominal
background rate is not the realized total); the three numbers do not.

## What regenerating costs

It re-scores every detector and redraws the bake-off. That is not a refactor: the
bake-off table and its figure are quoted in `README.md`, and the learned-detector report
is on the public site. Expect the numbers to move **within seed noise** — measured, 12
seeds, no detector shifting more than its own spread and the ranking unchanged — so the
regeneration should be checkable as a no-op-in-substance.

**CICADA is the exception and must be read separately.** Its FAST `sce_percentile` was
retuned 99.99 → 99.999 in the same PR, so its numbers move for a real reason: 18-fold
fewer false positives, F1 +0.03 at the quiet endpoint and −0.04 at the busy one. Any
regenerated artifact showing CICADA moving is showing that, not drift.

## Do this before quoting any bench number

1. Regenerate, one tool at a time, checking each against its predecessor.
2. Where a number moves more than seed noise and is not CICADA, stop — that is a finding,
   not a refresh.
3. `README.md`'s bake-off table and the site's learned report are the two a stranger
   reads. They come last and they get looked at.

⚠ **Not started.** Filed at the end of the session that moved the axis, deliberately
rather than rushed, because a half-regenerated `docs/learned/` is worse than a
consistently stale one: it would mix two calibrations with nothing saying which is which.
