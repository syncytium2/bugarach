---
status: open
filed: 2026-09-01
---

# A traced figure cannot tell an architectural constant from an initialised value

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

## What to do

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
