---
status: open
filed: 2026-08-28
---

# `bakeoff.md` retypes nine rows a token could substitute, and one of its claims went stale for eight days

> **Not murderboarded** — a note for sessions in this tree. The comparison it makes
> is between two files already in the repo.

## The two pages solved the same problem differently

`docs/learned/report.src.html` quotes numbers with `{{N:store:path|fmt}}` tokens
that `tools/build_learned_report.py` resolves against the JSON stores at build
time. Its own source comments say why, twice:

> *"The bake-off that superseded this page. The banner quotes it, and a superseding
> notice carrying its own stale transcription of the newer result would be the exact
> failure this substitution exists to stop."*

> *"The transfer test. Its numbers were typed into the prose of a first draft; six of
> them were right and that was luck, not a process."*

`docs/learned/bakeoff.md` has **no generator**. Its nine-row results table and every
number in its prose are typed by hand from `bakeoff.json`.

## What that cost, measured rather than predicted

Regenerating the bake-off on 2026-08-28 required a human to retype nine rows and
restate six derived claims — the F1 gap, two fold ranges, two speed multiples and
two cost ratios, none of which is in the JSON and all of which are arithmetic over
things that are. The `175×` detection ratio became `10×`; the `42×` training ratio
became `11×`.

And the failure the tokens exist to prevent had already happened here, in the
direction nobody was watching. *"The bench's regimes reproduce"* compared this
page's measured interquartile range against `bench.REGIMES`. **The bench moved on
2026-08-20** — re-derived from the approved export folder, 0.0038/0.0175 →
0.0052/0.0190 — and this page went on asserting the agreement for eight days. It
is retracted in the same commit as this file. Nothing in the results table depended
on it, which is precisely why nobody looked.

## What to do

Give this page the same treatment as the report: a `bakeoff.src.md` with tokens and
a build step, or fold it into `build_learned_report.py`, which already loads
`bakeoff.json` as store `b` and would need no new machinery.

**The derived claims are the interesting part**, and a token substitution alone does
not reach them. `0.023 s is 2.6× faster than CoactDetect's 0.062` is a ratio of two
stored numbers; so are the fold ranges, which are `min`/`max` over `per_fold`. Those
want either their own tokens (`{{RATIO:b:...}}`) or, more cheaply, a test that
recomputes each quoted ratio from the JSON and fails when the prose drifts. The
second is smaller and catches the same class.

**What it does not fix**, and what should be said plainly wherever this lands: a
token keeps a number current, not a *sentence*. *"A tie at the top"* and *"the
difference that survives is cost"* are judgements about numbers, and no substitution
tells you when one stops being true. The 2026-08-28 re-run left both standing —
centre−surround 0.681 ± 0.049 against CoactDetect's 0.651 ± 0.044, ranges still
overlapping — but that had to be checked by a person, and it always will.
