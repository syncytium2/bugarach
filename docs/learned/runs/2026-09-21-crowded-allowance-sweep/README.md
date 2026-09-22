# The merge-gap verdict only moves once the search is pinned at the end of its own gap grid

Run 2026-09-21 on WSMIP064, 08:44 to 09:33 (3,773 s elapsed, 22 of 22 rows, 0 errors).
**Working material, not murderboarded** — same standing as the other run records here.
Nothing for an outside reader.

**This measures and adjudicates nothing.** No operating point moves, `bench.MAX_CROWDED_DROP`
is untouched at 0.02, and `docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/` is not
edited. Whether any of this changes what the merge-gap page may claim is Tony's call.

**Tool:** `tools/tune_net_merge_gap.py select --max-drop <allowance>` (the `--max-drop` flag is
this branch's addition; tests in `tests/test_tune_net_merge_gap.py`).
**Figure:** `tools/make_crowded_allowance_figure.py` → `crowded_allowance.png` / `.html`.
**Record:** `sweep_summary.json` (every allowance, both draws), `progress.json` (per-row timing),
and four `*.wanted.json` files naming the selections that could not be scored.
**Bulk** — the 22 per-row grid files, 7.8 MB — is in the darkroom beside this record, not here.

## The question

Option B's ungated half from
[`todo/2026-09-20-why-the-merge-gap-page-would-not-converge.md`](../../../todo/2026-09-20-why-the-merge-gap-page-would-not-converge.md):
the merge-gap result was reported against an **unsigned 0.02 allowance** — goal 1's rule that a
wider gap may not cost more than 0.02 mean **F1** (the harmonic mean of recall and precision) on
the crowded recordings than the choice it would replace. The allowance was inherited, not
derived. Does the verdict depend on it?

Only the `select` stage re-runs, over the decodings the 2026-09-18 fair comparison already
cached. **Nothing was retrained and nothing re-decoded**: 1,938 fits, all reproducing at the
as-run 2 s gap. Gap grid 0, 1, 2, 3, 5, 8, 15, 30 s; `min_gain` 0.002 inner F1; crowded
recordings `bench.make_tail_recording`, seeds 1 to 12, both backgrounds (24 recordings).

## The answer, and the caveat that governs it (Figure 1)

**Figure 1, the swept allowance** (`crowded_allowance.png`) has three panels: **A** ungated
(gap picked on F1 alone), **B** gated (gap and threshold together under the shared rate budget),
**C** how many of the 32 selections — 4 nets × 4 outer folds × 2 selection rules — chose the top
of the gap grid.

**The verdict does move, but not near 0.02, and not for a reason the sweep can use.** At the
adopted 0.02 allowance CoactDetect is ahead of every net in both draws and both selection rules,
except one cell inside noise:

| selection | draw | chorus | chorus-gain | line-length | tube |
|---|---|---|---|---|---|
| ungated | run | **+0.0043** (inside noise) | −0.0374 | −0.0322 | −0.1141 |
| ungated | replicate | −0.0483 | −0.0185 | −0.0315 | −0.0996 |
| gated | run | −0.0181 | −0.0167 | −0.0372 | −0.1492 |
| gated | replicate | −0.0827 | −0.0153 | −0.0425 | −0.1291 |

Mean ΔF1, net minus CoactDetect, on the held-out outer folds; negative is CoactDetect ahead.

Nets first pass CoactDetect between 0.10 and 0.25, depending on the net and the selection rule.
**Panel C is why that number cannot be read as a finding.** The count of selections sitting at
the 30 s grid edge is **0 at every allowance through 0.05**, then 1 at 0.10, then 19 (run) and
15 (replicate) at 0.15, then **all 32 at 0.25 and looser**. The flips and the pinning arrive
together. A search that has run off the end of its own grid has not found a better gap; it has
found that the grid stopped, so the allowances where the verdict changes are exactly the
allowances where the measurement stops meaning what it says.

Three further things the sweep shows:

- **0.25, 0.35 and no-check are identical in every cell.** Above roughly 0.25 the crowded check
  is inert — it refuses nothing. The allowance therefore has a ceiling beyond which it is not a
  parameter at all.
- **The two seed draws disagree by more than the allowance does, near 0.02.** Ungated chorus
  reads +0.0043 on the original draw and −0.0483 on the replicate, a spread of 0.0526 — larger
  than the 0.02 allowance whose effect the sweep set out to measure. Whatever the allowance is
  worth at its adopted value, draw-to-draw variance is the larger term.
- **tube never flips.** CoactDetect leads it at every allowance including no-check, by 0.028 to
  0.155 mean F1 across draws and selection rules.

## What is missing, and it is the strict end

Four rows were planned and not scored, because they need crowded scores for configurations the
2026-09-18 run never cached: **run at 0.000, and replicate at 0.000, 0.005 and 0.010.** The
selections each one wants are listed in `run_0p000.wanted.json` (40 configurations) and the
three `replicate_*.wanted.json` (60 each). Closing them needs a `crowded` top-up pass over those
configurations and a re-select.

So **0.000 — the strictest allowance, where no drop at all is permitted — has no row on either
draw**, and the replicate's two strictest measured rows are absent. Panels A and B begin at
0.005 for the original draw and 0.02 for the replicate for that reason, not because the strict
end was judged uninteresting. The board's earlier note that low allowances "run far slower"
holds: the 0.000 attempt ran past 13 minutes before it was cut.

## What would settle the part the sweep could not

Extending `gaps_sec` past 30 s and re-running the loose end, which would separate "the nets
prefer a wider gap" from "the grid ended at 30 s". That is a re-select over cached decodings, not
a retrain, and it is not started here — it changes what a published page claims, and the page is
Tony's.
