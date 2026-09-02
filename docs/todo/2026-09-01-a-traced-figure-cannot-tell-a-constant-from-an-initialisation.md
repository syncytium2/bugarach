---
status: done
filed: 2026-09-01
---

# DONE — a traced figure cannot tell an architectural constant from an initialised value

`draughtsman` produced a revised model figure for the front page on 2026-09-01 —
a left-to-right boxed flow, every quantity read from a `torch.jit.trace` and a
`graph.json` rather than from `build_tube()`. Tony has asked for it to be
vendored here on the next deploy. **Its numbers were checked against the built
model and they hold** — total 1149, DoG bank 12 learned params, kernel 257
(`2·max_center_frames+1`), dilation 1 → 32, concat 5 channels, stack 8 channels.

**One of them is true only of an untrained model, and the tracing is exactly why.**

The figure labels the first stage *"widen each onset — max-pool, width 3"*. That
width is not in the architecture. It is
[`tube.py`](../../src/bugarach/learn/nets/tube.py)'s

```python
kmin = int(torch.exp(self.log_center.detach()).min().clamp(1, self.k))
pooled = F.max_pool1d(..., kernel_size=2 * kmin + 1, ...)
```

and `log_center` is a **trained parameter**. At initialisation the centre widths
are 1 / 2 / 4 / 8 samples, so `kmin == 1` and the pool is 3 wide. The class
docstring records trained widths of roughly 4–7 samples, which puts the same pool
at **9–15**. Measured, not inferred: instantiating `ARCHITECTURES["tube"]` and
reading `exp(log_center)` gives `[1.0, 2.0, 4.0, 8.0]` → `kmin = 1` → width 3.

So the figure states an initialisation as though it were a constant, and does it
in the one place where this repo has already drawn the line. `make_architecture_
diagram.py`'s docstring: *"No fitted values appear here. Centre widths are
initialised across a geometric spread and then trained, so a fitted width belongs
to one training run."* Two tools exist precisely to keep the two apart — that one
is true of the design, `make_architecture_figures.py` is true of a run.

**The general form, which outlives this figure.** A trace observes one
instantiation. It cannot see which of the values it recorded would survive
training and which are an artifact of the seed, because both are just numbers in
the graph by the time it looks. Anything derived by tracing therefore needs a
declared answer to *"is this quantity part of the design?"* that does not come
from the trace. Reading off the module instead does not solve this by itself —
it is the same numbers — but it puts the question in the drawing code, where
someone can answer it, rather than in a serialized graph where it is invisible.

## Settled 2026-09-01 — draughtsman took it, and the mechanism is in the tracer

**Every checklist item below is answered.** The short version: the distinction is
declared in draughtsman's `spec.json`, it is *demanded* by the tracer rather than
remembered by anyone, and the figure now reaches this repo through a pipeline that
runs over the live `build_tube()` instead of arriving as a snapshot.

**Where the distinction is declared, and why it needs no list.** The first proposal
here was a hand-maintained list of design quantities, with the objection stated in
the same breath: a list that goes stale exactly when the model moves. It is not
needed. `torch.jit.trace` already *says* it baked a Python value out of a tensor —

> `TracerWarning: Converting a tensor to a Python integer might cause the trace to
> be incorrect. We can't record the data flow of Python values, so this value will
> be treated as a constant in the future.` — at `tube.py:139`, which is the `kmin`
> line

— and draughtsman was discarding the warning. It now records those in `graph.json`
under `hazards`, and `check` makes quoting a traced constant an **error** while a
hazard from the model's own code stands, until the spec says why that particular
one is architectural. `architecture.spec.json` declares two — both dilations,
because `_dilated_stack` sets `d = 2 ** i` from the layer index — and quotes no
pool width at all. The declaration is a line in a diff, which is the same shape as
an explicit elision and needs no list.

**Provenance-walking was checked and is impossible, not merely hard.** `int()` on a
tensor leaves tensor-land, so `2*kmin + 1` is Python arithmetic torch never records
and the width arrives at `max_pool1d` as a bare `prim::Constant` — the same node
kind a literal `kernel_size=3` produces. Verified against torch 2.13 and pinned by
a test upstream, so the next attempt to out-clever the tracer finds it first.

**⚠ THE NEAR MISS, WHICH IS THE MOST USEFUL THING HERE.**
`tests/test_architecture_diagram_is_current.py::test_the_generator_is_deterministic`
was written for precisely this hazard — *"a figure that redrew itself per seed would
be describing a run"* — and it **cannot catch it**. `build_tube` initialises
`log_center` deterministically at 1/2/4/8 samples, so the baked `3` is perfectly
reproducible and both runs agree. Determinism and architecture are different claims:
a reproducible initialisation is still an initialisation. The gate is not weakened by
saying so, but it should not be read as covering this.

### The checklist, item by item

- [x] **Where the distinction is declared.** `spec.json`'s `constants` block,
      demanded by the tracer's own hazard record rather than by a list. No list to
      go stale.
- [x] **Drop or qualify `width 3`.** Dropped. The stage reads *"max-pool, width
      fitted"* and its note records that the width is `2·kmin+1` with kmin off a
      trained parameter, so the traced 3 belongs to an untrained instantiation.
- [x] **Label the 1×1 head's 9 params.** Labelled. The boxes now sum to the 1149
      in the title: 12 + 1128 + 9.
- [x] **Un-dash the bypass.** Solid, and a test upstream asserts it *stays* solid,
      with `eab8e59`'s reason in the docstring.
- [x] **The two dropped claims.** The receptive field is **not restored** — see
      below; it is the one item that did not fully land. Cell-count invariance is
      carried in the `mean over cells` stage note (*"Cells are summed, so the model
      never sees which cell is which"*) rather than in the shape line, which still
      shows the concrete `1×30×600` the trace was taken at.
- [x] **The typed-glyph colouring.** Restored, and answered better than colour
      alone can. Hue is now the family — the DoG bank and the dilated stack are both
      green, where before one was gold and they read as unrelated — and the figure
      carries a **generated legend** whose share is counted off `graph.json`:
      `Convolution — 38 ops, 1140 params` against a 1149-parameter model. That is
      Tony's *"how much of the model is convolution, at a glance"* as a fact rather
      than an impression. A box is not a layer here (one box collapses 26 traced
      ops), so box area could never have carried the proportion.
- [x] **The committed-graph objection.** Taken, and it is why the vendoring is
      shaped the way it is. `graph.json` is **not** committed: it is traced from the
      live `build_tube()` on every run of `tools/make_architecture_diagram.py`. What
      is vendored is the *spec* — the judgement layer, which carries no numbers —
      and draughtsman itself under `third_party/`.

### One item that did not land

**The receptive field (`sees 127 samples`) is still missing**, and the reason is a
real limit rather than an oversight. It is `1 + 2·Σ2ⁱ` over the stack's depth —
architectural, and derivable from the traced dilations — but draughtsman's reference
grammar has no arithmetic, and its first rule is that the agent writing the spec
supplies no facts. So the figure can either quote a number nobody traced (forbidden,
and it is the failure the whole tool exists to prevent) or say nothing. It says
nothing. Filed upstream as a derived-fact feature; until then the receptive field
belongs in the page's prose, where `receptive_field(depth)` can be called directly.

## What to do (original, all items now answered above)

Not a defect to file against `draughtsman` — the figure is good and it is better
than what ships today in two ways worth keeping (it has explicit input and output
boxes, and a one-row layout against a current diagram that is about 40% air).
This is the thing to settle **before** it is vendored.

- [ ] Decide where the constant/fitted distinction is declared. If the figure
      keeps tracing, it needs a hand-maintained list of "these are design
      quantities" — which is a list that can go stale, so it wants a test.
- [ ] Drop or qualify `width 3`. `2·kmin+1`, or "widen each onset (width is
      fitted)", or nothing at all, which is what the current figure does.
- [ ] Label the 1×1 head's **9 params**. The boxes read 12 + 1128 = 1140 against
      a stated total of 1149; the split itself is right and arguably better than
      the current figure's lumped 1,137, but the head's own box carries no count.
- [ ] Un-dash the bypass. `eab8e59` exists partly because the previous diagram
      "drew the bypass as a dashed afterthought" — it is a first-class fifth
      channel into the concat and dashed reads as optional.
- [ ] Decide what happens to two claims the revision drops: `N = cells, any
      number · the model never sees which cell is which` (the revision
      substitutes a concrete `1×30×600`, which is more legible and less true —
      cell-count invariance is a real property), and the receptive field
      (`sees 127 samples`).
- [ ] Decide whether the typed-glyph colouring survives. Tony's stated reason for
      wanting an Inception-style figure on 2026-09-01 was *"how much of the model
      is convolution, at a glance"*; the revision colours by stage and ships no
      legend, which is a stage diagram again — a much better-looking one.
- [ ] If a `graph.json` is checked in rather than traced at build time, note that
      it is a file a human regenerates by hand, which is the defect
      `tests/test_architecture_diagram_is_current.py` was added to close for the
      SVG. Whatever ships, something has to fail when the model moves.

## Related

- [`2026-08-15-draw-the-pipeline-instead-of-describing-it.md`](2026-08-15-draw-the-pipeline-instead-of-describing-it.md)
- `tools/make_architecture_diagram.py` — the current generator, and its docstring
  is the argument this todo is defending.
- `tests/test_architecture_diagram_is_current.py` — the gate that the *committed*
  figure still matches the model.
