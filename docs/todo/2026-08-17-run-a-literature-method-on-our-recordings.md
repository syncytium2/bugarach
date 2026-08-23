---
status: open
filed: 2026-08-17
---

# Nothing from the literature has been run here, and one of them is a clean-room away

`docs/learned/README_for_the_webapp.md` already forbids the phrase "competes with
state-of-the-art" in app copy, for the right reason: the comparison set is six
detectors ported here plus our own networks. CICADA is the one published method in
it, and it reached us as a port of interface2's port. Everything else in the
report's positioning is an argument from absence.

The literature survey (`2026-08-17-literature-deep-dive-handoff.md`) changed what
this would cost. Three candidates, in order of how little stands in the way.

## 1. The coactivity frame gate — clean-room it, no licence question at all

**This is the one to do.** SGC, CORE and SVD (Mölter et al. 2018) each begin by
binarising per cell, counting coactive cells per frame, and keeping frames whose
coactivity level exceeds the 95th percentile (SVD: 99th) of a 1000-iteration
per-cell permutation null. That is a **population-event detector**, it is
described in about five sentences of their methods, and its output needs **no
adapter** — the high-coactivity frames *are* the events, in our scorer's terms.

It is also a textbook fit for `docs/clean_room/`: a published algorithm short
enough to specify, implemented from the spec alone, validated adversarially
against an independently written implementation. That process exists here, has
been run once (`find_peaks_halfprom`), and sidesteps every licence and dependency
problem below.

The comparison it buys is real: an independently-published gate, run through
`tools/fair_bakeoff.py` under the same fit-and-score procedure as everything else.

## 2. cnn-ripple and DOSED — legally and practically harder than they look

Both are learned event detectors with public code, and both would be the
headline comparison. Both have problems.

| | licence | ours | can we vendor? | runs? |
|---|---|---|---|---|
| `PridaLab/cnn-ripple` | **GPL-3.0** | BSD-3 | **No** | conda env pinned to Python 3.7 with linux-64 builds |
| `Dreem-Organization/dosed` | MIT | BSD-3 | Yes | `torch==1.0.0`, `h5py==2.8.0`, Cython 0.29 — will not install on 3.11 |
| `zebrain-lab/Toolbox-Romano-et-al` | **GPL-3.0** | BSD-3 | **No** | MATLAB |
| `DurstewitzLab/CADopti` | **GPL-3.0** | BSD-3 | **No** | MATLAB |
| `hanshuting/SVDEnsemble` | MIT | BSD-3 | Yes | MATLAB |

Two separate obstacles and they need separating. **Licence** blocks copying GPL
code into this BSD repo — it does not block *running* a program and reading its
output, so a bake-off against cnn-ripple as a separate process is fine, and only
distribution of a derived work is not. **Dependencies** are the practical wall:
both Python candidates are pinned to 2018–2021 stacks that do not install
alongside this project, so either one means an isolated environment and a file
hand-off, not an import.

Neither takes our input as-is either. cnn-ripple expects 8-channel LFP at
1250 Hz; DOSED expects EDF-shaped multichannel recordings. Feeding per-ROI calcium
to either is an adapter we would write, and a poor score would then be ambiguous
between the method and our adapter — which is the trap that makes a bad
comparison worse than none.

## 3. The three techniques, which are not code at all

Swept scoring tolerance, non-maximum suppression, and pretraining on a classical
detector are **ideas**, filed separately as
`2026-08-17-scoring-cannot-see-localization.md`,
`2026-08-17-no-suppression-of-overlapping-detections.md` and
`2026-08-17-pretrain-on-the-six-then-fine-tune.md`. No licence attaches to a
method described in a paper, and all three are implementable here in our own code
with no dependency at all. They are the portable part of this literature, and the
first of them is already measured.

## Recommendation

Do 1. It is the only one that produces a defensible published-method comparison
without an adapter, a licence question, or a dead dependency tree, and it uses a
process this repo already has. Treat 2 as optional and expensive, and only after
the scorer question is settled — running a literature model against a bench that
cannot see localization would waste the comparison.
