---
status: open
filed: 2026-08-19
---

# A cell that never fired is being counted as evidence, in two instruments

Two of this project's measures hand **cells with no activity** to a statistic and let
them contribute to the answer. One is an outright defect and is fixed; the other is a
defensible choice nobody has measured the size of. They are the same shape, which is why
they are filed together.

## Fixed: the synfire indicator counted silence as perfect order

`tools/synfire_scan.py` passed every ROI to `optimal_spike_train_sorting`, silent ones
included — **36% of ROIs in the fast corpus, 940 of 2630.**

PySpike's `spike_train_order` averages a per-pair ratio and scores a pair of trains that
are **both empty** as `(e=1, m=1)` — the value it gives a *perfectly ordered* pair. So
every pair of silent ROIs added a maximal-order term, quadratic in the number of cells
that never fired.

Measured on the export corpus, the effect is concentrated exactly where it does most
damage — the sparse recordings at the top of the distribution:

| recording | events | ROIs (silent) | indicator, as published | silent ROIs dropped |
|---|---|---|---|---|
| `20240723_22` fast | 17 | 24 (21) | **0.353** — top of the corpus | 0.059 |
| `20260225_275` fast | 29 | 29 (25) | 0.273 | 0.046 |
| `20240723_22` slow | 13 | 24 (20) | 0.397 | 0.103 |
| `20250904_211` slow | 53 | 45 (39) | 0.247 | 0.098 |

Corpus medians barely move (fast 0.033, slow 0.100 → 0.032, 0.081) because most
recordings have few silent ROIs. **The upper tail is where the silence lives**, and the
upper tail is what a "there is order here" claim is made of: median |change| is 0.004
fast and 0.007 slow, but p90 is 0.038 and 0.086 — comparable to the median indicator
itself.

**The verdict tally moves by one in each stream and the conclusion stands**: fast 22 of
81 above null pre-fix against 23 of 81 corrected, slow 43 of 82 against 44 of 82. The
relabel null preserves each ROI's event count, so silent ROIs stay silent in the
surrogates and the inflation lands on both sides; every flip is a recording sitting on
the α = 0.05 line. Figures: `synfire_roi_{fast,slow}` from
`tools/make_synfire_roi_figure.py`.

It also inflates the correlation the synfire handoff cites as its third reason for not
quoting the group result: `rho(indicator, spike count)` is −0.76 fast / −0.40 slow as
published, and −0.60 / −0.18 once silent ROIs are dropped. Sparse recordings scored high
partly *because* they were sparse.

Fixed in `_trains`, with `--keep-silent-rois` to reproduce the old numbers, and pinned by
`tests/test_synfire_roi.py` — including a test of **PySpike's** behaviour, so that if a
future release stops scoring empty pairs as ordered, the fix gets revisited rather than
silently kept.

## Open: the assembly uniform null draws participants from cells that never participate

`pvalues_uniform` ([`assembly.py:255`](../../src/bugarach/assembly.py#L255)) redraws each
event's participants with `rng.choice(n_roi, ...)` — **every ROI in the recording**. The
observed membership matrix spans the same `n_roi` columns
([`membership_matrix`](../../src/bugarach/assembly.py#L121)), so a cell that never joined
a coordinated cluster is an all-zero column in the observed data and **a candidate
participant in every surrogate**.

That is not obviously wrong. The uniform null is deliberately the generator's own
assumption (`simulate.py`, `rng.choice(nR)`), and "participation is not uniform across
this field's cells" is a true reading of the rejection. `docs/assembly_report.md` already
says the uniform null "fires on plain rate heterogeneity", and the core–periphery reading
rests on exactly that.

**What has not been measured is how much of the rejection is only that.** The report
quotes **45 of 47** fast and **36 of 38** slow as co-participation beyond per-cell rate.
If restricting the null to cells that participate at least once leaves those counts
standing, the claim is unaffected and this is closed with a sentence. If it does not, the
phrase is doing more work than the statistic supports.

**The check is bounded**: re-run `assess_assemblies` with the uniform null drawing from
participating cells only, on the same corpus, and compare verdicts. It changes no
published number unless it changes the answer.

⚠ **Not run here.** The assembly report and its instrument were another session's work
and are at murderboard round 4; this is filed rather than acted on so that work is not
disturbed mid-flight.

## The generalisation worth keeping

Both cases come from the same reflex: pass the whole field to the statistic and let it
sort them out. `bugarach.graph.modularity_vs_null` does the opposite deliberately, and
says why — zero-event cells "contribute no edges, and leaving them in would pad the node
count differently between observed and surrogate graphs." **Three instruments, two
conventions, no stated rule.** Whatever the answer to the open half, the rule should be
written down once and the instruments made to agree.
