---
status: open
filed: 2026-08-27
rule: SAP009
---

# SAP009 reports clear on a file that shades a treatment window across a raster

> Found by the murderboard on the learned-detector page
> ([`docs/reviews/learned_detector_2026-08-27.md`](../reviews/learned_detector_2026-08-27.md)),
> while judging whether `tube_view.png` could be used on a public page. It cannot,
> and the reason the tree did not already know that is this gap.

**Not a dispute with the rule.** SAP009 is right, its crudeness is deliberate, and
[`2026-08-26-sap009-sees-only-what-is-named.md`](2026-08-26-sap009-sees-only-what-is-named.md)
already records that it works by naming. This is a **second** blind spot, adjacent to
that one and not covered by it, with a live instance in the tree.

## The instance

`tools/make_tube_figure.py:153`:

```python
rowA = _probe(raster * ticks * dmark)
```

`ticks` and `dmark` are marker rows and `_probe` adds an `hv.VSpan` for the probe
block, so this composes **two marker rows and a shaded window onto the raster inside
panel A** — three things the convention puts in a lane above. `python tools/sapper.py
--all` returns `sapper: clear`.

## Why the pattern misses it

```
(raster_panel\([^\n]*\)\s*\*|\braster\w*\s*\*\s*hv\.)
```

Two alternatives, and the line satisfies neither:

- it is not `raster_panel(...) *` — the raster is a plain variable here;
- it is `raster * ticks`, not `raster * hv.` — the right operand is a **bound
  variable**, not a literal `hv.` constructor.

So the recorded blind spot ("only what is named") is about the **left** operand, and
this is the **right** one. The file names its raster `raster`, exactly as the
convention asks. It complies with the thing that makes the rule work and the rule
still cannot see it.

## The other half: the tool was half-fixed and its artifact never re-rendered

`aa9a8b4` (2026-08-26, *"A marker above a raster points at the raster"*) changed this
file's markers to `inverted_triangle`. That fixed the **direction** rule and left the
**overlay** rule broken — the markers still ride on the raster, they now point down
while doing it. And `docs/learned/tube_view.png` was committed 2026-08-16 and never
re-rendered, so the published artifact still has up-pointing triangles.

A rule firing here would have caught both.

## Suggested change, and its cost

Widen the second alternative to any `*` between a `raster`-named variable and
anything:

```
\braster\w*\s*\*(?!\s*=)
```

**This will fire more.** `raster * hv.Something` is the common legitimate-looking
shape and it is exactly what the rule wants to catch, but a file that composes a
raster with another *raster* would trip too. Worth checking against the tree before
adopting — if the false-positive count is zero or one, take it; if it is more, the
honest alternative is to leave the pattern alone and record this second blind spot
beside the first, which is what this file does in the meantime.

**A related one, out of scope here:** `docs/learned/problem_view.png` has the same
violation and **no generator anywhere in `tools/`**. It is an orphan that cannot be
re-rendered to fix it, so no line rule can ever help; it needs deleting or
reproducing from scratch.
