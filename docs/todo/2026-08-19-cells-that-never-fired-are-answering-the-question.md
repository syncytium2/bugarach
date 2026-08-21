---
status: open
filed: 2026-08-19
---

# A cell that contributed nothing is being counted as evidence, in two instruments

Two of this project's measures hand **cells that contributed nothing to the data being
tested** to a statistic and let them shape the answer. One is an outright defect and is
fixed; the other is a defensible choice nobody has measured the size of. They are the
same shape, which is why they are filed together.

**The title of this file said "never fired" when it was written, and that was wrong** —
see the census below. It is kept so the link does not rot, but the accurate phrase is
"contributed nothing to the observed data being tested", and what that means differs
between the two instruments: for synfire, no event **in the analysis window**; for
assembly, never a member of **any coordinated cluster**. Neither means dead.

## Fixed: the synfire indicator counted an empty train as perfect order

`tools/synfire_scan.py` passed every ROI to `optimal_spike_train_sorting`, including
those with nothing in the window — **1941 of 5260 (ROI, stream) pairs, 37%.**

PySpike's `spike_train_order` averages a per-pair ratio and scores a pair of trains that
are **both empty** as `(e=1, m=1)` — the value it gives a *perfectly ordered* pair. So
every pair of empty trains added a maximal-order term, quadratic in the number of cells
with nothing to say in that window.

### The census, because "empty" was doing too much work

Of those 5260 (ROI, stream) pairs in the v2 export:

- **122** produce no event anywhere in the recording. This is exactly the count the
  export's own `PROVENANCE.md` reports under "silent (roi, stream) pairs", which is a
  clean cross-check that this reader agrees with the producer.
- **1819** fire somewhere in the recording and simply not in the **baseline analysis
  window** — the window the synfire question is scoped to.

Both arrive at the sorter as an empty train, and both should be dropped: a cell with no
event in the window has no latency to be ordered by, whatever it does later under drug.
But **94% of them are not quiet cells**, and the first version of this note called them
that. The dead-ROI verdict is the producer's and was already applied upstream by the
choice of store — `event_store_onset_revised_2v_alive` — not by anything here.

Measured on the export corpus (numbers below from the **periods** export; the same
recordings on the v2 export differ, see the windowing note), the effect is concentrated
exactly where it does most damage — the sparse recordings at the top of the distribution:

| recording | events | trains (empty) | indicator, pre-fix | empty trains dropped |
|---|---|---|---|---|
| `20240723_22` fast | 17 | 24 (21) | **0.353** — top of the corpus | 0.059 |
| `20260225_275` fast | 29 | 29 (25) | 0.273 | 0.046 |
| `20250904_211` slow | 53 | 45 (39) | 0.247 | 0.098 |

**The verdict tally does not move in a consistent direction, and the conclusion is
untouched.** All four seeded (export × stream) combinations, pre-fix against corrected:

| export | stream | pre-fix | corrected | median indicator | rho(F, spikes) |
|---|---|---|---|---|---|
| v2 (analysis window) | fast | 23 / 80 | **26 / 80** | 0.0351 → 0.0318 | −0.74 → −0.57 |
| v2 | slow | 45 / 81 | **44 / 81** | 0.0980 → 0.0844 | −0.39 → −0.19 |
| periods (raw baseline) | fast | 25 / 81 | **23 / 81** | 0.0331 → 0.0315 | −0.76 → −0.61 |
| periods | slow | 43 / 82 | **44 / 82** | 0.0995 → 0.0821 | −0.40 → −0.18 |

+3, −1, −2, +1: the fix changes **which marginal recordings clear the α = 0.05 line
without systematically shifting the count**. The relabel null preserves each ROI's event
count, so empty trains stay empty in the surrogates and the inflation lands on both sides
of the comparison. Every flip is a recording sitting on the line.

**Two effects are consistent across both exports, and those are the quotable ones.**

- **The upper tail was contaminated.** Median |change| is 0.004 fast and 0.008 slow, but
  p90 is 0.038–0.043 and 0.085 — comparable to the median indicator itself.
- **`rho(indicator, spike count)` weakens substantially.** That correlation is the synfire
  handoff's **third reason** for not quoting the slow group result, and part of it was this
  artifact: sparse recordings scored high partly *because* they were sparse.

Figures `synfire_roi_{fast,slow}` from `tools/make_synfire_roi_figure.py`; runs and a
fuller write-up in `<darkroom>/bugarach/synfire/`, which holds `2026-08-19-corrected/`
beside `2026-08-19-original/` with the explanation in its `README.md`.

## Two defects found while re-running, both of which reached published numbers

- **No run reproduced any other run.** The scan seeded numpy with
  `abs(hash(slice_id))`, and Python salts string hashing per process unless
  `PYTHONHASHSEED` is set — so every run drew different surrogates while the docstring
  promised a rerun would reproduce. The ±1 verdict differences first reported for this fix
  were partly that noise. Now `zlib.crc32(slice_id)`; a rerun is field-for-field
  identical, asserted in subprocesses with hash randomisation forced on. **The synfire
  session's published files predate this**, so they are not re-derivable — not wrong, but
  not reproducible.
- **Three events were reported as the most ordered recording in the corpus.**
  `20240723_22` slow is 3 events across 3 trains; every relabelling is identical, so
  observed and null are both exactly 1.0 and there is no distribution. Rows now carry
  `defined` and summaries exclude them. This was wrong **before** the ROI fix too — the
  same recording was the pre-fix slow maximum at 0.774. Honest maxima: 0.414 and 0.625.

## The windowing note, because two exports are in play

`2026-08-17_revised_2v_v2` carries `analysis_start_sec`/`analysis_end_sec`;
`2026-08-18_revised_2v_periods` sends none, deliberately, so the scan falls back to the raw
baseline period. On slow, one shared recording differs by **0.377** in the indicator from
the window alone — larger than anything the ROI fix does to it. The published files used
v2. Numbers from the two exports must never be mixed.

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
