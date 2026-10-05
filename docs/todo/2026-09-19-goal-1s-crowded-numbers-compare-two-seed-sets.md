---
status: open
filed: 2026-09-19
---

# Goal 1's published crowded numbers for sliding CoactDetect and LoCo compare two seed sets

**Found** by the fair comparison's review (round 3, role 3) and confirmed against goal 1's own run
record, `<darkroom>/bugarach/archive/2026-09/2026-09-17-full-search/sliding5/search.json`, on 2026-09-19.

The goal 1 page (`docs/goals/coded-detector-optimization.md`, the row on sliding LoCo and
CoactDetect) and `HANDOFF-coded-detectors.md` record, for the sliding values now in `bench.py`:
*"crowded 0.818 against 0.808"* for CoactDetect and *"0.827 against 0.816"* for LoCo. The two numbers
in each pair come from different recordings:

- **0.818 and 0.827** are the candidates' held-out crowded scores, from `held_out()` in
  `tools/search_all_settings.py`, which scores crowded recordings on the held-out seeds' first
  twelve (seeds 49 to 60).
- **0.808 and 0.816** are the crowded reference, the shipped operating points scored by the
  `Evaluator` on the selection seeds' first twelve (seeds 1 to 12).

On the same held-out crowded recordings, the run record's own `held_out` block gives the shipped
points **0.859** (CoactDetect) and **0.869** (LoCo). So on common recordings the sliding values lose
0.040 and 0.042 mean F1 on crowded recordings against what they would replace, twice the 0.02 the
crowded-recording check allows. On the selection seeds, where the check ran, they gain (0.826 and
0.834 against 0.808 and 0.816, `docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/crowded_check.json`).

**Why it matters.** The claim that the sliding values improve both held-out F1 and the crowded score
rests on a comparison across two seed sets. The check that admitted them looked only at seeds 1 to
12. Whether the held-out loss is noise over twelve recordings or a real cost is not established.

**What to do.** Not a fix in the goal pages from here: the project lead decides what goal 1's record
says (the fair comparison's brief said not to edit `docs/goals/`). The measurement that would settle
it: score the shipped and sliding points on one set of crowded recordings large enough to separate
0.04 from zero, and state the comparison on common seeds.
