# The transfer experiment, and two things I corrected myself on — 2026-08-29

**The next piece of work is a cross-corpus transfer test, everything it needs is now on
`main`, and the two numbers most likely to be quoted from this session are both
superseded versions of numbers I reported earlier the same day.** Those corrections are
the reason this file exists; the design is the rest of it.

> **Filed here rather than at the root, deliberately.** Nothing is half-done. Everything
> landed: **#394** (the locust caption), **#395** (variants, seed axis, resolver fix,
> `[cossart]` role), **#396** (two hazards, open with a watcher). A root `HANDOFF.md`
> means *work is in flight*, and this is a cue sheet, not a rescue.
>
> Assembled off `main` at `1982bb9` + #395.

---

## Two corrections, because the superseded versions are the quotable ones

**1 · The guard does not lead. I said it did, off one seed.** After seed 1 of the
overnight screen I reported `tube_guard` as the best cell at F1 **0.668** with probe
firings down to **25.0 ± 4.76**. Across all five seeds it is **0.662** — identical to the
shipped tube to three decimals — with firings **30.35**. The single-seed reading was
noise, which is precisely what the seed axis was built to catch; it caught me first. **Do
not cite 0.668.**

**2 · K=3 does not fail in the Cossart data; it understates.** From a 5-recording sample
I drew a figure claiming K=3 sat *below the point where the statistic discriminates at
all*, with their median field at 405 ROIs. Over all 59 recordings their median field is
**566 ROIs** and K=3 sits at **61% of their peak excess** — off-peak by roughly half, not
dead. The shape claim survives; the strength of it did not. **Do not cite "below where
the statistic works."**

Both figures rendered from those numbers exist in a scratchpad and are superseded. If a
version of either reaches a reader, it must be regenerated from
`docs/learned/`-adjacent sources or from a fresh run, not from those PNGs.

---

## What the overnight screen actually found

5 training seeds × 4 folds = **20 fits per architecture**, fitted background, 2.5 s
tolerance, `k_chosen: 3` inherited from `generator_spec.json`.

| | F1 | sd(fold) | sd(seed) | probe firings | recall |
|---|---|---|---|---|---|
| tube_guard | 0.662 | 0.043 | 0.008 | 30.35 | 0.780 |
| **tube** (control) | 0.662 | 0.038 | 0.011 | 38.10 | 0.793 |
| coact | 0.660 | 0.011 | — | **2.25** | 0.796 |
| tube_ratio | 0.533 | 0.055 | 0.018 | **0.15** | 0.615 |
| tube_ratio_guard | 0.460 | 0.076 | 0.040 | 0.30 | 0.613 |

- **V2 (ratio) failed its own pre-registered test.** The four-variants todo said in
  advance: firings collapse *without recall falling*, or the ratio is buying its clean
  probe by refusing to fire. Firings 38.1 → 0.15; recall 0.793 → 0.615.
- **V1 (guard) does nothing to F1** and trims firings by a fifth — not the 6–13× the tube
  needs to reach the hand-written detectors.
- **The interaction went backwards.** ratio+guard is *worse* than ratio alone, which
  contradicts the `rate` result the 2×2 was designed around.
- **The seed gap is small, and that is the useful finding.** Seed spread 0.008–0.011
  against fold spread 0.038–0.043. Almost all variance is the data split. **Multi-seed
  does not rescue the tie at the top** — tube 0.662 vs coact 0.660 is a real tie. Item 1
  of `model_track.md` is answered, in the negative.

**⚠ The test the four-variants todo actually prescribes for V1 was NOT run.** It says
report *crowded-band gain minus control-band gain*, not F1, because a gain flat across
the neighbour gap is a threshold shift wearing a mechanism's clothes.
`bench.nearest_neighbour_gaps` exists; `fair_bakeoff` does not call it. **V1 is not
settled — it is unmeasured on its own criterion.**

Raw JSONs are in a session scratchpad, not the repo. `tools/run_tube_screen.sh` regenerates
them; nothing was written to `docs/learned/`, and that regeneration is one pass and is not
this.

---

## The transfer experiment — the next piece, and why it has this shape

**The question:** does a model trained on our corpus work on another lab's? It is the
first thing any reviewer asks about a learned detector, and this project can answer it
with two real corpora and a ground-truth-bearing simulator.

**The 2×2:**

| | scored on sim-from-ours | scored on sim-from-theirs |
|---|---|---|
| trained on ours | the number we have | **the transfer penalty** |
| trained on theirs | reverse transfer | the ceiling |

Run `locust` the same way — our operating point vs re-optimised on theirs — and it becomes
*does a learned model transfer better or worse than a hand-tuned detector*.

**Three constraints that are not negotiable:**

1. **No F1 on their real recordings.** No ground truth; RESET §10 reserves that word for
   planted events. Transfer runs through a simulation parameterised from *their* measured
   statistics.
2. **No cross-lab event matching.** Their data is binarised, `time_sec` is a rising edge
   not a t50rise, and their `PROVENANCE.md` says coincidence within a tolerance is not
   available from these files. The comparison lives in the simulation.
3. **Do not transplant K.** Measured across both full corpora: ours peaks at **K=3**,
   theirs at **K=12**. The bar comes from each corpus's own null — which is what the
   Cossart lab's own SCE method does and what `sce.py` ports. Written into the `[cossart]`
   role in `current_export.toml`.

**What exists:** `dataset.current("cossart")` resolves (since #395), the assessor runs on
their folder, `derive_spec` builds a spec, `fair_bakeoff --spec` scores one. **What does
not:** train-on-A-score-on-B. That is the piece to write, and it is a modest extension of
`run()`'s learned loop — the same loop `--train-seed` was threaded through.

---

## Decisions waiting on Tony

- **The website is the priority**, and the resume artifact is the *result*, not the app.
  Tony, 2026-08-29: the goal is a "resume honeypot".
- **Training in the webapp for outside users is decided against.** Phase 3b (the JS
  trainer) is off the critical path.
- **The scoreboard is built and hidden** behind the lab gate awaiting a copy review. It is
  the most portfolio-relevant screen in the project and no visitor can see it.
- **The site is behind** — `tools/site_staleness.py` said 14 commits with one serving
  change before #394 added a second. A redeploy needs Tony's Cloudflare credential.
- **Model swapping / distribution is v2.** It demonstrates packaging, not deep learning.

## Open, filed, not done

- [derive K from confirmed events](../todo/2026-08-28-derive-k-from-confirmed-events.md)
  — propose at K=2 or lower, or the candidate set is censored at the floor being estimated.
- [lookahead, not throughput](../todo/2026-08-29-lookahead-not-throughput-is-the-real-time-question.md)
  — every detector is >28,000× real time, so speed is settled; the tube needs **12.8 s of
  future** and nothing measures it.
- [manifest.csv is not reserved](../todo/2026-08-29-manifest-csv-is-not-reserved-and-the-loader-reads-it.md)
  and [the worktree-src hazard](../todo/2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md),
  both in #396.
- `tube-variants-overnight` is redundant since #395 cherry-picked off it — **reap it.**
