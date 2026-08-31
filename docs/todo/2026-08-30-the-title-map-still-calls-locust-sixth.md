---
status: open
filed: 2026-08-30
---

# The title map still calls locust "sixth"

The viewer's `TITLES` map in `src/bugarach/ui/app.py` renders the `cicada` key as
**`sixth`**. Every other detector gets its proper name — `CoactDetect`, `LoCo`,
`rate+context`, `binned SCE`, `SPIKE-synch` — and this one gets an ordinal.

It surfaces anywhere `TITLES` is used for display. Two places found while building the
performance table: the table's own rendering, and `docs/learned/bakeoff.png`, whose x-axis
carries `sixth` between `rate+context` and `tube_ratio`.

**Why it is more than cosmetic.** The detector was renamed to **locust** on 2026-08-24
(ADR-0002) precisely so that a modified port would not carry the upstream's name in a
public UI — Tony's call, on the reasoning *"we can't say we used it if we turned off half
of it"*. `sixth` is not that name either. So a reader of the site or of the bake-off figure
sees a placeholder where the naming decision was supposed to land, and the one artifact
that most needs the rename to be visible is the one that shows it least.

The glossary records the rename and the code key: **the key stays `cicada`** — it is
output contract, including the `detector` column of `detections.csv` — while the display
name is *locust*. So this is a one-line display fix and explicitly **not** a key rename.

**What to check when fixing it**, because the name is threaded further than the map:

- `TITLES` in `src/bugarach/ui/app.py`.
- `docs/learned/bakeoff.png` and anything else built from `TITLES` — regenerate, do not
  hand-edit; `tools/make_bakeoff_figures.py` reads the map.
- The front page's detector-count prose, which a separate item already flags as
  disagreeing with itself in seven places.
- Do **not** touch the `cicada` key, `detections.csv`, or any parity fixture.

Noticed while writing [the performance table](../performance_table.md), which prints
`sixth` verbatim rather than quietly correcting it — a document that silently renames what
the code emits is a document a reader cannot check against the code.
