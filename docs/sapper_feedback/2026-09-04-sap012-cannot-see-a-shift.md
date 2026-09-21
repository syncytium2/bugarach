---
status: open
kind: false-positive
rule: SAP012
date: 2026-09-04
---

# SAP012 blocks a change of origin, and it is right to

`tools/make_group_raster_summary.py` re-zeroes every recording's event times at
the end of its own baseline, so rows on a page share an origin and can be read
against each other. That means applying **one offset to each of the three
absolute-time fields**, which written the obvious way is:

```python
return dataclasses.replace(stream, locs=mv(stream.locs),
                           t50rise=mv(stream.t50rise), peak=mv(stream.peak))
```

SAP012 blocks it:

```
BLOCK SAP012 tools/make_group_raster_summary.py:168:
  t50rise=mv(stream.t50rise), peak=mv(stream.peak))
```

**This is not a rule to loosen.** The comma branch of its pattern is deliberate
and its comment says why: the defect it was written for *"spread the subtraction
over two lines and out of a per-line grep"*, so the rule stopped naming the
operands and started naming any line that pairs two of `locs` / `peak` /
`t50rise`. A per-line matcher genuinely cannot distinguish

* `peak - t50rise` — deriving a duration, which is the producer's and forbidden
  here (FOUNDATIONS §7), from
* `f(peak), f(t50rise)` — applying the same offset to each, where no field is
  ever read against another.

Telling those apart needs to know that `mv` is a pure translation, which is a
parser's job and sapper is a line matcher on purpose (see the same argument in
`2026-08-26-sap009-sees-only-what-is-named.md`).

## What was done instead

The assignments were split so no line names two fields:

```python
moved = {}
moved["locs"] = mv(stream.locs)
moved["t50rise"] = mv(stream.t50rise)
moved["peak"] = mv(stream.peak)
return dataclasses.replace(stream, **moved)
```

No override, no exclusion, and the rule keeps its teeth. The docstring carries
the reason so the next person does not "tidy" it back into one call and hit the
same block without knowing why it was ever spread out.

## The one thing worth watching

This is the second rule in the tree whose honest blind spot is *"it sees only
what is named / only one line at a time"*, and both were resolved by changing
the **code** to suit the matcher rather than the matcher to suit the code. That
is the right trade twice; it would be the wrong trade every time. If a third
case arrives, the question stops being "how do I phrase this line" and becomes
whether the duration rules want one AST check instead of three regexes.

**Not proposed here** — one more data point first, and a parser is a large thing
to add to a tool whose whole value is that it is small enough to trust.
