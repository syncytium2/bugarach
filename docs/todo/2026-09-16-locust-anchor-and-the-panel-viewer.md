---
status: open
filed: 2026-09-16
---

# What locust's per-event duration left open: the anchor, and `bugarach view`

> **Status is `open`, not `waiting-on-tony`, and the decision below is still his.** It was
> put to Tony in the session that filed this. The briefing has no room for another
> waiting item — adding one failed CI's briefing tests
> ([`2026-08-30-the-briefing-has-one-todo-of-headroom.md`](2026-08-30-the-briefing-has-one-todo-of-headroom.md))
> — and the ruling there is to clear waiting items, not raise the budget. `docs/INDEX.md`
> ("which duration locust uses") points here.

**Context.** On 2026-09-16 locust's shipped operating point stopped holding every cell
active for a fixed second and started reading each event's own `width_sec` — the
column FOUNDATIONS §7 says it paints. `bugarach detect` and the bench run it that way
now; the FAST percentile was re-derived under it (it stays 99.999; the numbers are in
`bench.OPERATING_POINTS["cicada"].source`). Two things were deliberately not changed
in the same step.

## 1. The two readers anchor locust on different times

- **Python** (`bugarach detect`, the bench): the default `onset_field="locs"`. On an
  export folder `locs` is `time_sec`, the **half-rise** (`bugarach.io`).
  `export_folder_spec.md` revision 8 calls that deliberate.
- **Browser**: the **peak**, from `peak_sec`, and it refuses a folder without one. Its
  own comment calls that "not a bug to fix".
- `detect_folder.ONSET_FIELD`'s comment said "CICADA anchors on the peak (`locs`)" —
  true of a `.mat` store, where `locs` is the peak, and false of every folder. It now
  says so.

So the same folder gives locust two different event sets depending on which reader
opens it, and each reader's documentation describes its own choice as settled. With a
per-event width this matters more than it did at a fixed second: the width is painted
**forward from the anchor**, so the half-rise anchor covers `[half-rise, half-rise +
width]` and the peak anchor covers `[peak, peak + width]` — different spans of the same
event. Which span the width was meant to cover is a question about the producer's
column, and the column's meaning is not written in this repo (FOUNDATIONS §7).

**Decision needed (Tony):** which anchor locust uses with a per-event width, in both
readers. The bench cannot answer it — its events have one time, so peak and half-rise
coincide there, which is also why the percentile re-derivation does not depend on it.

## 2. `bugarach view` still runs the fixed second

The Panel viewer (`src/bugarach/ui/app.py`) exposes `active_duration_sec` as a widget
and never passes `active_duration_mode`, so it paints 1 s on every event and anchors on
`t50rise`. Its percentile widget still takes the calibrated value, which was re-derived
for the per-event setting — so the viewer now shows a percentile tuned for a different
duration rule than the one it runs. The widget default became a literal `1.0` with a
comment naming this, because the import-time check refuses a CALIBRATED widget the
operating point no longer declares.

**To do once (1) is decided:** give the viewer a per-event mode defaulting on for
folder input, matching `detect`.

## Also recorded

- **SLOW's percentile (99.9999) has no bench evidence** at either duration: the bench is
  a single-stream FAST instrument. SLOW now runs per-event on the same untested value.
- **What the bench can and cannot show.** Its widths are drawn independently of which
  events are coordinated, so it can re-derive a percentile under per-event durations but
  cannot show per-event durations *helping*. At the same percentile, per-event scored
  slightly below the fixed second on the busy background (24 recordings, F1 0.519
  against 0.546 at 99.999). That is a property of widths that carry no signal, not
  evidence about real ones.
