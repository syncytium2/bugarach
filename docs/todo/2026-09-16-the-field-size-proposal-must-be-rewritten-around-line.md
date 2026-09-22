---
status: open
filed: 2026-09-16
---

# The field-size proposal is held back: it was written without knowing `line` exists, and on the wrong rate

**Where it is:** `claude/net-design-proposal-hw8rve`, unmerged, with the three proposed
architectures, their draughtsman figures and the page. **Nothing on that branch is registered
here**, which is the point — PR #589 was split down to the probe and this note, and the nets stay
out of the lab server's capabilities and the browser's model picker until something runs them.

> ⚠ **Superseded on that one point, 2026-09-22.** `gauge` and `chorus` (with four chorus
> repairs) **are** registered on `main` now — they landed with #680 on 2026-09-21, and because the
> folder is the registry they reached `/api/capabilities` and the model picker with them. Tony ruled
> on 2026-09-22 to **leave them there**, each carrying its warning note. `quorum` is still
> unregistered. Items 1–5 below are untouched by this; item 6 is answered.

Tony asked, 2026-09-16: *some recordings have 13 cells and some have 50, 500+ in another lab's;
tube and line were two nets designed by my word description of an approach; propose three new
classes.* A review on the PR caught three things before any of it landed.

## 1. `line` exists, and the page says it does not

The page reads *line* as `trace` and states there is no architecture of that name. That is
**false**: `src/bugarach/learn/nets/line.py` and `line_length.py` are registered on
`unsup/rigid-shift-controls` (PR #588), `line` was trained overnight on 2026-09-15/16, and its
docstring quotes Tony's own description from 2026-09-15 — the raster read as a one-dimensional
line, length and orientation as two sensors. So *tube and line* meant `tube` and `line`, and the
question was answered against the wrong pair.

**It was one `git fetch` away.** The branch was on the remote the whole time and the session read
only what was on `main` and in its own worktree.

⚠ **`chorus` largely duplicates `line`.** Both smooth each ROI on its own, cap each at one vote
with a sigmoid, and average the votes over ROIs. What `chorus` adds is a spread channel and a
top-*m* channel beside that mean. **The proposal cannot be read until it says what those two
channels buy over `line`, measured** — and `line` has an overnight run to compare against, written
up on that branch as `docs/pipelines/learned-model-evaluation.md`.

## 2. The per-cell rate was a median of medians, which this repo already calls a trap

The probe read `roi_rate_med` from the committed assessments. On this lab's folder **128 of 340
windows have a median of zero**, so the median-of-medians is 0.00083 Hz — **six times below the
bottom of the baseline range FOUNDATIONS §9 gives for the same quantity**, 0.0052–0.0190 Hz.
`src/bugarach/adapt.py` documents this exact trap in its header, calls it *a third trap*, and
moved to the mean. Nobody checked the number against §9 until a reviewer did.

**Fixed in `tools/probe_field_size.py` and landed on its own** (PR #589). Both statistics now
travel in `docs/learned/field_size.json` so the correction stays checkable. What it moves:

| | as first published | corrected |
|---|---|---|
| this lab, per-cell rate | 0.00083 Hz | **0.0097 Hz** |
| Cossart ÷ this lab | 19.6× | **2.4×** |
| chance floor at 32 / 566 / 1,050 cells | 3 / 6 / 7 cells | **5 / 17 / 25 cells** |
| a fixed count set at 32 cells, carried to 566 | 334× over budget | **~19,800× over budget** |

- ⚠ **The confound warning does not survive.** Field size differs 117× and rate only 2.4×, so the
  cross-lab difference is mostly field size — which is a *stronger* result than the hedged one the
  page printed, and the page still prints the hedge.
- **The shape survives.** The floor still grows sub-linearly (×5 across a ×117 span), so neither a
  fixed count nor a fixed fraction has the right shape. That is the one claim the three designs
  rest on and it is unharmed.
- Every floor scales with the assumption that each onset is widened to **9 frames**; the page
  never says so.

## 3. Defects in two of the three, as built

- **`gauge` is not permutation invariant**, and that is the one ledger row the page calls
  structural in every net. Its surrogate shifts row *i* by `(i + 1) × stride`, so relabelling the
  cells changes the null and therefore the output. Measured on an untrained model at 24 cells:
  max |Δ| 0.0014 under a permutation, against `tube`'s exactly 0.000000. The same arithmetic
  aliases: with a 600-frame window, rows 600 apart get identical shifts and keep their alignment,
  which bites precisely at the thousand-cell fields the class exists for.
- **`quorum` cannot learn its exponent on the current bench.** Every bench recording has one field
  size, so `coefficient × n^exponent` is a single number during training and the two parameters are
  not separable. Its stated acceptance test — *the fitted exponent lands strictly inside its
  bounds* — cannot be run until the generator has a field-size axis. `clamp(0, 1)` also zeroes the
  gradient at a bound.
- **`chorus`'s pooled channels are a fraction and a fixed count** — a mean over cells and a fixed
  top-4 — which are the two shapes Figure 2 of the page argues against.

## What has to be true before any of it is quoted or run

1. Read `line` and #588's evaluation write-up, then rewrite the proposal knowing both.
2. Say what `chorus` adds over `line`, and drop it if the answer is nothing.
3. Make `gauge`'s null order-free, or withdraw the claim that it is permutation invariant.
4. Move `quorum`'s acceptance bar behind the field-size axis it needs.
5. Re-run every number on the page against the corrected rate.
6. Registration belongs to whoever owns the learned-model evaluation pipeline, as the first stage
   of running a net — not to a proposal.

## The general lesson, which is not about this page

**A number six times outside the range this project's own FOUNDATIONS gives for that quantity
should stop a session.** §9 was read at session start and the contradiction still went out. When a
probe produces a rate, a participation or a width, put it beside §9 before building on it.
