---
status: open
filed: 2026-09-17
---

# The every-knob grids are a coordinate search's, and goal 2 scores the coded side inside nested cross-validation

**From WSMIP064 to WSMIP065 and Tony, before goal 1 declares `bench.FULL_GRIDS`.** Deciding it after
the grids are declared means declaring them twice.

## The mismatch

**Goal 1 searches by coordinate descent.** `tools/search_all_settings.py` moves one knob at a time
with the others held at the current best, in rounds. Its grids are per-axis lists, and the number of
settings it visits is a sum over axes, not a product.

**Goal 2 scores a coded detector inside nested cross-validation.** For each of the four outer folds,
every candidate is scored on that fold's 18 training recordings, the best is chosen, and only that one
is scored on the held-out fold. With CoactDetect and LoCo on three axes each, the candidates are the
full product: 99 and 72 configurations, cheap.

**Every knob makes the product impossible.** CoactDetect's ten searched parameters, LoCo's ten and
SPIKE-synch's thirteen (`HANDOFF-coded-detectors.md` §3 step 3) multiply out far past anything
runnable. `tools/tune_learned_vs_coact.py` refuses a product over 5,000 configurations rather than
guess, and says so.

## The options

| | what it means | cost | what it gives up |
|---|---|---|---|
| **A. Run goal 1's search inside each outer fold** | The coordinate search itself becomes the selection procedure: run it on each outer fold's training recordings under that fold's budget, then score its answer once on the held-out fold | 4 outer folds × 2 selections × one search. The 2026-09-16 search took 11 minutes for all six detectors, so this is minutes to hours, on the CPU, beside the nets' GPU fits | nothing in fairness: the search never sees the fold it is scored on. Needs `search_all_settings.py` to take a recording set and a budget, and to return the chosen settings |
| **B. Declare a product-sized subset per detector** | Goal 1 names the few axes that matter after its full search, and goal 2 takes the product of those | as now: seconds per configuration | the knobs left out are frozen at goal 1's values, chosen on all the recordings, including goal 2's held-out folds. A small leak, and it must be said in the readout |
| **C. Freeze goal 1's landed values** | The coded side runs at one setting, not tuned per fold | free | the comparison's own rule. The nets are chosen per fold; coded detectors chosen once, on every recording, are both advantaged (they saw more) and not a per-fold choice. It also revives the objection that started this: a reference tuned differently from what it is compared with |

**WSMIP064 recommends A**, with B as the fallback if the search cannot be made to take a recording set
and a budget in reasonable time. A keeps the guarantee the whole comparison rests on — nothing about a
configuration is chosen with the fold it is scored on — and it costs little, because the coded
detectors are cheap and the nets hold the GPU rather than the processors.

**What WSMIP064 needs, either way:** the declaration on `main` that says which, so both machines
search the same thing. The tuning tool imports `bench.FULL_GRIDS` already and will use a product where
one is declared.
