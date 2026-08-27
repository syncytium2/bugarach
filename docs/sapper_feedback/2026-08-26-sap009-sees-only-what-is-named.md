---
kind: new-rule
rule: SAP009
filed: 2026-08-26
status: landed-with-a-known-blind-spot
---

# SAP009 forbids drawing on the raster, and it sees only what is named

## The rule

Tony, 2026-08-26: *"please, lets never draw on the raster. i know i've changed my mind
on this. for now, all new rasters are drawn black and white. any detection or cue is
drawn above the raster with symbols (or hashes if there's need for rows)."*

Now in CLAUDE.md's plot conventions, and mechanized as SAP009 over `tools/**` and
`src/bugarach/ui/**`:

```
(raster_panel\([^\n]*\)\s*\* | \braster\w*\s*\*\s*hv\.)
```

## The blind spot, stated plainly

**It catches the mistake only when the variable is called `raster`.** The code that
prompted the rule — `tools/make_benchmark_figures.py`, the day before — held the raster
in a variable called `panel` and overlaid onto it across several statements:

```python
panel = raster_panel(...)
...
panel = panel * hv.VLine(t)      # SAP009 does not see this
```

Sapper is a line matcher by design and a rule that tracked "is this variable a raster"
across statements would need a parser. So the rule is paired with a naming convention —
CLAUDE.md says *hold a raster in a variable called `raster`* — and the convention is
what makes a one-line regex able to see the thing it guards.

**That is a real gap and it should be recorded rather than discovered.** A session that
names the variable `panel`, `fig`, `ax` or `row` gets no warning at all.

## Why it was landed anyway

Three reasons, in order of weight:

1. **It catches the shape that is always wrong on one line** —
   `raster_panel(...) * hv.Something(...)` — which is the form a session reaches for
   first, because it is the shortest.
2. **The naming convention is cheap and self-reinforcing.** The rule's own message
   states it, so the first person it fires on learns it.
3. **The alternative is a parser.** An AST rule that traced assignment would be the
   first of its kind in `sapper.py` and would change what the tool is. That is a
   bigger decision than this rule needs, and it should be made on its own merits
   rather than smuggled in under a plot convention.

## What would close it

Either of these, if someone wants it:

- **A runtime guard instead of a text one.** `raster_panel` could return a thin wrapper
  whose `__mul__` raises with the same message. That catches every name, cannot be
  worked around by accident, and fires at the moment of the mistake — but it changes a
  public return type that `ui.app` and `ui.diagnostic.coordination_diagnostic` both
  consume, so it needs a look at those first.
- **An AST pass in sapper for a small set of "tainted" constructors.** More general,
  and a much larger change to what `sapper.py` is.

## Note on the fixture

`fixture_bad` is assembled by concatenation, like `_UM` at the top of `sapper.py`.
Written whole it is itself a line that draws on a raster, so the tree scan fires on the
rule that forbids it. That is the fourth time a self-describing string has tripped its
own rule in that file, and the comment there now says so.
