# HANDOFF — learned detectors: the loop runs, the report page does not describe it

Branch `learned-detectors-framework`, PR #52. Everything is committed and pushed.
Delete this file when the two ⚠ BLOCKING items below are closed.

⚠ **This handoff has not been through the murderboard.** `CLAUDE.md` asks for one on
a human-facing handoff and there was no session left to run it. Treat its claims as
checkable rather than checked; every number in it is in a JSON in `docs/learned/`.

## The one-paragraph version

Two things happened. A murderboard on the existing learned-detector report
**retracted its conclusion three times** and the corrected page now says the model
is level with the six rather than ahead of them. Then the per-lab loop was built and
run end to end on live data: 85 real recordings assessed without a detector, one
generator spec derived from that measurement, one corpus generated, and every
detector — hand-written and learned — fitted on three folds and scored on a held-out
fourth. On that footing the learned model **ties** the best hand-written detectors
(0.668 ± 0.061 against CoactDetect's 0.651 ± 0.044) and **detects 4–17× faster** at
1,149 parameters and 5.6 s to train.

## ⚠ BLOCKING — do these before anything else

1. **The darkroom serves the withdrawn report.**
   `<darkroom>/bugarach/2026-08-16-learned-detectors/report.html` is `fa29612` — the
   version claiming the model beats the six, which no matched comparison supports.
   The corrected page is `5ebfe44` in `docs/learned/`. The darkroom is shared across
   machines: **claim it on `docs/SESSIONS.md` before writing.** (An earlier note of
   mine on that board said the copy was never made; that was wrong and is corrected
   in place.)
2. **`docs/learned/report.html` predates the bake-off.** It describes the old
   synthetic bench, not the corpus derived from real recordings, and its numbers
   come from a different generator configuration (flat background). Nothing in it is
   *false* as written — it is scoped to the old bench — but a reader will take it for
   the current result. Either fold `docs/learned/bakeoff.md` into it or mark it
   superseded.

## What is new and working

| | |
|---|---|
| `tools/assess_archive.py` | points the ported assessor at a store of real `.mat` recordings; **baseline regions only**, counted-and-skipped otherwise. 85/85 slices, 1000 surrogates, 118 s |
| `tools/derive_spec.py` | assessment → generator kwargs. Refuses to choose K; ships the whole scan beside the choice. Turns on the fitted heterogeneous + bursty background |
| `tools/fair_bakeoff.py` | one corpus, one selection procedure for hand-written and learned alike, one scorer, k-fold held-out, and cost measured in the same run |
| `tools/make_bakeoff_figures.py` | accuracy with every fold drawn, and the deployability plane |
| `docs/learned/bakeoff.md` | the result, with what it does not establish |
| `bench.pool_scores` | the single pooling path; `evaluate` is built on it |
| `tests/test_learn_nets.py` | 11 tests on the architecture claims the report makes; `nets.py`/`train.py` had none |

**Data source, confirmed:** `event_store_onset_revised_2v_alive_rescued` —
interface2 branch `dead-roi-store` @ `752855a`, built 2026-08-16. Rule *keep any ROI
that fires anywhere*; 48 of 66 rescued, the 18 dropped silent in FAST, SLOW and
custard everywhere. Chosen over its sibling `..._alive` (roster rule, drops all 66)
because FOUNDATIONS §9 says an ROI is dead only if silent at baseline **and** drug
**and** high-K⁺. It is **unclaimed on interface2's board** and its commits are not on
their main — we only read it.

**Not used:** the `2R/2026-08-15` hi-K re-export. Per-ROI aggregate "custard", no
per-event onset column; bugarach cannot read it under either code path. It is the
fireflies/R consumer's artifact.

## Two findings that were not the objective

- **The bench's regimes reproduce on data they were not fitted to.** Per-ROI rate
  across the 85 slices has an IQR of **0.0037–0.0185 Hz**; the bench's quiet/busy
  endpoints are **0.0038 / 0.0175**.
- **38% of slices have a median ROI that never fires in baseline** — FOUNDATIONS §9's
  "roughly 35%", on a store it was never measured on. This also disqualifies
  `roi_rate_med` as a background rate; using it gave 0.0023 Hz, below anything this
  project has recorded. The code says so where the next reader will hit it.

## ⚠ Open, in rough priority order

1. **Multi-seed within a fold.** Every learned number is one training run per fold,
   so fold spread confounds data variation with training variation. Cheapest thing
   that could change a conclusion.
2. **The probe cannot fail** — `docs/todo/2026-08-16-promiscuity-probe-cannot-fail.md`.
   Firings leave both numerator and denominator. Until it has a budget assertion, no
   "this detector does not fire on dense random activity" claim is supported.
3. **K=3 was chosen by a human and moves the corpus.** The scan is in
   `generator_spec.json`; K=4 halves the event rate.
4. **The architecture conclusion is not controlled** — the winning model trains at
   10× the learning rate of the two it is contrasted with, and the project's own
   diagnostic ranks `pos_weight`/batch size as the leading *untested* cause of their
   failure to descend.
5. **Drop the raw brightness channel and re-run.** One line. It would settle whether
   the transfer asymmetry is the variance story or the one channel that never had its
   background subtracted.
6. **interface2 has an unanswered message to us** —
   `docs/teams/inbox/2026-08-16-bugarach-vendoring-ownership-and-two-bad-stamps.md`:
   two of the three files a bugarach session proposed re-vendoring are wrong, and
   `docs/writing_conventions.md` has **no upstream in interface2 at all** while a
   freshness gate reports it current. That last one is our bug and it is live.
7. **`docs/todo/2026-08-16-learned-detectors-handoff.md`** still carries the retracted
   "the regime-shift guard does not reproduce the failure it exists to catch", plus
   four stale numbers. Left deliberately — rewriting another session's handoff felt
   like the wrong unilateral call.

## Where the reviews are

- `docs/reviews/report_2026-08-16-round2.md` — the murderboard, 11 roles × 2 models,
  2 rounds, with the residual ⚠ list and what a third round should look at.
- The page has **never survived a round unchanged**, and three of round 2's blocking
  findings were introduced by round 1's repairs. Assume a third round finds more.
