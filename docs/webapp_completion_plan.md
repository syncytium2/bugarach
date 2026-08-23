# Finishing the webapp — the seven stages, the phase order, and who can work at once

> **Scope.** This is the execution plan for the WEBSITE track
> ([`docs/webapp_spec.md`](webapp_spec.md) is the requirement; this is the route). The
> MODEL track is [`docs/model_track.md`](model_track.md) and nothing here waits on it.
>
> **Written 2026-08-19**, from Tony: *"I need the webapp to work the full pipeline …
> scan a set of files in a folder, visualize the rasters, run the assessor, generate
> simulated data based on the real data, allow the user to view the simulated data and
> verify its qualities, then optimize the six detectors and train the tube network, then
> show the performance on new ground truth (including performance parameters), then
> process the real data and show the results."*
>
> **Not murderboarded.** It is an internal build plan for sessions in this tree, not a
> handed-over deliverable. Every number in it is quoted from a file in the tree and
> named at the point of use, so it is checkable. If any of it goes to an outside
> reader, run `/murderboard` on that artifact first.

## The one-paragraph version

The webapp is a single zero-network HTML file that already opens a lab's folder, draws
its rasters, measures coordination without a detector, generates a simulated data set from
that measurement, runs detectors and sweeps one knob against planted truth. What it
cannot do is **train the tube network**, **fit anything across folds**, and **write a
file**. Five green PRs waiting to merge take it from two of the six detectors to five.
Training arrives first through a **loopback lab server** that calls the functions which
produced the published numbers ([ADR-0001](adr/0001-the-lab-server.md)), and the
no-install JS trainer follows it with a reference to check against. The server is the long
pole, and it is the one piece that can start today without touching anything anybody else
is holding.

## Where each stage stands

| # | the stage Tony asked for | in the browser today | in Python today |
|---|---|---|---|
| 1 | scan a folder of files | ✅ folder reader, conformance report, remembers the directory | ✅ `bugarach check` / `assess` |
| 2 | visualize the rasters | ✅ lanes, treatment windows, ROI ordering | ✅ `bugarach.ui.app` |
| 3 | run the assessor | ✅ ported, parity-tested against `bugarach.assess` | ✅ `bugarach.assess` |
| 4 | simulate from the real data | ✅ generator ported to JS, writes a conforming folder | ✅ `simulate.py` + `adapt.py` |
| 5 | view the simulation and verify its qualities | ⚠️ you can look at it; nothing puts its measured statistics **beside** the real folder's | ⚠️ split across `tools/` |
| 6a | optimize the six detectors | ⚠️ sweeps **one** detector's **one** knob on **one** recording — no folds, no held-out set | ✅ `tools/fair_bakeoff.py`, four folds, nine detectors |
| 6b | train the tube network | ❌ **nothing** | ✅ `bugarach.learn.train` (PyTorch) |
| 7 | performance on new ground truth, with parameters | ⚠️ one F1 for one recording | ✅ published in `docs/learned/bakeoff.json` |
| 8 | process the real data, show the results | ⚠️ detections draw on the lanes; **nothing is ever written to a file** | ✅ CLI |

Two facts behind that table are worth stating on their own.

**The app writes no file.** There is no `Blob(`, no download, anywhere in
`docs/site/raster_viewer.html`. `docs/webapp_spec.md` calls the output contract the
point of the exercise rather than an afterthought, and it is still unbuilt.

**Five green PRs are unmerged**, and they are the difference between two detectors and
five: **#128** (one registry row per detector — the seam every later phase plugs into),
**#129** LoCo, **#130** CoactDetect, **#131** SCE, **#133** the user-stated analysis
windows. All three CI jobs pass on each. Roughly 25 of the 35 worktrees on this machine
are fully merged into `origin/main` and can be pruned.

## The constraint that decides the architecture

The published page promises a lab that its recordings never leave the computer, and
[`tests/test_site_viewer.py`](../tests/test_site_viewer.py) makes that a property of the
file rather than a paragraph: no `fetch(`, no `XMLHttpRequest`, no `<script src`, no
`import(`. `tools/build_site.py` refuses to publish it otherwise, and a Cloudflare
beacon injection already proved the check earns its keep.

So **the published page reaches nothing**, and no CDN-hosted ML library is available to
it. Training happens either in hand-written JS inside the page, or in a process beside it
that the published page does not know about.

**Settled 2026-08-19 — the local server first, the JS trainer after it.**
[`ADR-0001`](adr/0001-the-lab-server.md) has the reasoning; the shape in one paragraph:
the page owns the training panel, inert, behind `if (window.__lab)`; `bugarach lab` serves
that same file from disk with a shim appended that defines `window.__lab` and holds the
only `fetch(` in the system. The published page is unchanged and dead by **absence**
rather than by stripping, so `test_site_viewer.py` and `build_site.py` need no edit. The
server binds loopback, touches no file — the page already holds the folder through the
File System Access API and posts trains as JSON — and calls the same
`bugarach.learn.train` and `bench.pool_scores` that produced `bakeoff.json`. Descends from
`colonel_kernel` ADR-0048.

**What that buys and what it costs.** A working end-to-end demo in a few hundred lines
over code that already has parity tests, instead of a thousand lines of new numerics
before anything runs at all. The cost is that training stops being installable-free:
stages 1–5 and detection stay pure-browser, and *"train the tube on my folder"* becomes
the one step that wants `pip install bugarach[dl]`.

**The JS trainer is resequenced, not cancelled.** It is still the route to training with
no install, and the server makes it cheaper — it turns lane C from *invent the numerics*
into *match this*. The model is 1,149 parameters and the operation list is closed and
short:

- dilated `conv1d` (k=3, dilation doubling) ×6, plus a 1×1 — forward and backward
- GELU
- `max_pool1d`, stride 1 — backward is argmax routing
- the difference-of-Gaussians kernel, with gradients through `log_center`, `log_ratio`
  and `gain` (exp, clamp, gaussian, area-normalise)
- `BCEWithLogitsLoss` with `pos_weight`
- Adam, 300 steps, batch 4, 4,096-frame crops

PyTorch trains it in 5.6 s and scans a held-out fold in 0.014 s. Typed-array JS in a
Web Worker should land in the tens of seconds — slow enough to need a progress row,
fast enough to be a demo. Parity against PyTorch will be **behavioural, not 1e-9**;
[`docs/testing_a_sampling_port.md`](testing_a_sampling_port.md) already sets that bar
for ports that cannot be exact.

**The route not taken.** Shipping pretrained weights for browser inference is the cheapest
option and removes the very thing being demonstrated — training to *this lab's* dataset.
It is not on this plan at any phase.

## Phase order

**Phase 0 — land the green work.** Merge #128 → #129 → #130 → #131 in that order
through `tools/merge_when_green.sh`; #133 only with its session's say-so (it is ACTIVE
on the local board). Push or discard `preview-everything`, which carries the stack
locally on **no remote**. Prune the merged worktrees. *Hours, no risk, five of six
detectors live.*

**Phase 1 — the sixth detector, and a file that comes out.** CICADA as one more
registry row. Then `detections.csv` and `run.json` to the contract already written in
`docs/webapp_spec.md`: `slice_id` from the data and never a filename, `treatment`
carried and never inferred, one row per event per detector with no consensus merging,
seconds on the recording's own clock, a slice with no detections emitting no rows but
still listed in the roster, and no viability column of any kind.

**Phase 2 — a data set, not a recording.** Today assess, simulate and tune each act on one
recording. This phase adds folder-level assessment, **the K screen** — the one screen
that cannot be a spinner: it shows the scan, takes the decision, and records the
decision with the data set it produced — then generation of N recordings, a fold split,
and fit-on-three-score-on-the-held-out-fourth. This is what makes *"optimized to the
same ground truth"* a true statement rather than a slogan.

**Phase 3 — the tube trains, through the lab server.** [`ADR-0001`](adr/0001-the-lab-server.md).
The inert panel in the page, the `bugarach lab` server and its shim, and the gate that
asserts the published page carries no transport and ships byte-identical to its source.
The threshold is picked on held-out training-regime data and **never** re-picked on the
recording being analysed — moving training to a process with more room does not make that
button acceptable.

**Phase 3b — the same training with no install.** The JS trainer: autodiff, the model,
Adam, a Web Worker so the page stays alive, and a parity harness that now has Phase 3's
implementation to check against rather than an open question. Off the critical path to a
working demo, and it is what makes the demo reach a lab that will not install Python.

**Phase 4 — the scoreboard.** One row per detector: F1 with fold spread, recall,
precision, fit seconds, detect seconds, parameter count. With the caveat the numbers
require — the bench scores a hit at a 1.5 s edge gap against a median realized event
0.80 s wide, so the *ranking* is safe and a bare number implying timing accuracy is
not (`docs/learned/tolerance_sweep.png`).

**Phase 5 — the real folder.** Every detector across every slice and every region,
drawn on the existing lanes and exported. The app may say *these are the detections*;
it may not say *these are the events*.

**Phase 6 — verify the simulation.** Re-run the assessor on the generated data set and
put its statistics beside the real folder's on one screen. Cheapest phase in the plan,
and it is Tony's stage 5.

## What can run at the same time

**The binding constraint is one file.** `docs/site/raster_viewer.html` is ~3,000 lines
and every UI phase edits it. Five PRs already queue on it. So:

> **`docs/site/raster_viewer.html` is a single-holder resource.** Claim it by name on
> the machine-local board before editing, the way a MATLAB process or the darkroom is
> claimed. A second session editing it in parallel buys a merge conflict worth more
> than the work.

Lanes below are ordered by how much they are worth starting **now**.

| lane | what it is | touches the viewer? | blocked by | notes |
|---|---|---|---|---|
| **A · merge train** | Phase 0 | **holds it** | nothing | one session, fast, must finish before B, D2 or H2 |
| **H1 · the lab server** | Phase 3's engine: `bugarach lab`, the shim, the publish gate | **no** — new module, `src/` and `tools/` | nothing | **now the long pole, and the best parallel lane.** [ADR-0001](adr/0001-the-lab-server.md). A few hundred lines over `learn.train` and `bench.pool_scores`, which already have parity tests |
| **E · fold scoring** | port `bugarach.bench.pool_scores` and the fold split to JS | **no** — pure functions | nothing | tested against Python on fixed inputs; Phase 2 and 4 both consume it |
| **D1 · the writer, Python side** | `detections.csv` + `run.json` writer in the library, with a round-trip test | **no** | nothing | both callers must agree, so the shape gets settled once here rather than twice |
| **F · model track** | multi-seed, drop the raw brightness channel | **no** — `learn/`, `tools/` | nothing | decides whether *"the tube outperforms"* is a claim we own; see below |
| **G · housekeeping** | prune ~25 merged worktrees, push or drop `preview-everything` | **no** | nothing | ten minutes, removes most of the confusion |
| **B · CICADA port** | Phase 1's detector | **holds it** | lane A | one registry row once #128 lands |
| **D2 · the writer, browser side** | download button + the same CSV shape | **holds it** | lanes A, D1 | small once D1 fixed the shape |
| **H2 · the training panel** | the inert `if (window.__lab)` panel in the page | **holds it** | lanes A, H1 | H1 settles the request and response shapes first |
| **C · JS tube trainer** | Phase 3b: autodiff, the model, Adam, Web Worker | **no** — standalone block, spliced later | lane H1 (for the reference it checks against) | **resequenced, not cancelled.** Start it once H1 answers what correct looks like |

So **five lanes (H1, E, D1, F, G) start immediately and in parallel**, none of them
touching the viewer or each other. Lanes A, B, D2 and H2 are one serial queue on the one
file. Lane C waits on H1 by choice rather than necessity — it *can* be written blind, and
writing it after H1 replaces guesswork with a reference implementation.

## Before anyone writes app copy: the claim is not yet ours

`docs/learned/bakeoff.md`, on the data set measured from 85 real recordings with every
detector fitted on three folds and scored on a held-out fourth:

| detector | F1 (mean of 4 folds) |
|---|---|
| tube / centre−surround (learned) | **0.668 ± 0.061** |
| CoactDetect | **0.651 ± 0.044** |
| LoCo | 0.638 ± 0.053 |
| rate+context | 0.571 ± 0.085 |
| CICADA | 0.541 ± 0.070 |
| binned SCE | 0.422 ± 0.083 |
| SPIKE-synch | 0.254 ± 0.065 |

That is a **tie at the top, not an outperformance**, and every learned number is one
training run per fold, so no seed error bars exist to test it with. What the tube
demonstrably wins on is cost — 1,149 parameters, 5.6 s to fit, 0.014 s to scan a fold.
It also **transfers worse** than two of the six from a quiet background to a busy one,
which is a negative result about its own central claim; fit busy, deploy quiet.

**The webapp's job is to show this comparison honestly.** Making the tube actually lead
is lane F and the model track, whose cheapest unopened items are exactly the ones that
could move it: multi-seed, dropping the raw brightness channel, non-maximum suppression
on the probability trace, and pretraining on the six hand-written detectors over
unlabelled real recordings before fine-tuning on the simulation. That last one is the
per-lab-adaptation story the demo is really about, and it is unmeasured.

Two phrases that must not appear in app copy, both for reasons already recorded:
*"competes with state-of-the-art"* — the comparison contains **no published learned
method** and none of the assembly-detection family — and any wording implying a
detector is right about a **real** slice, because everything measured so far is on
simulated data.

## How we will know it worked

Point the app at a generated data set and **its exported table must agree with
`bakeoff.json`** — same detections, same counts. That check exists from Phase 1
onward rather than after the UI is built, which is the whole reason the writer comes
before the screens.
