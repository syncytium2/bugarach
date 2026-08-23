---
status: done
filed: 2026-08-20
closed: 2026-08-23
---

# Two implementations of one contract, and only one of them read the width

**This was filed as a missing feature. It was not one. `docs/export_folder_spec.md`
asks for `width_sec`, `width_def`, `peak_sec` and `amp`; the producer sends all four;
the browser viewer reads all four; the Python reader read none of them.** The same
folder, opened two ways, produced two different recordings — and each implementation
stood as evidence that the other was right.

That is the sharper version of the complaint, and it is why this cost more than a
column. `docs/site/raster_viewer.html` anchors CICADA on the peak and refuses to run it
on onsets, in a comment explaining at length that anchoring on the half-rise would call
almost any two events coincident. `src/bugarach/io.py` handed the same detector a
recording whose peaks *were* its half-rises, with nothing anywhere saying so. Neither
side was wrong about the contract. They simply were not the same reader.

**Closed 2026-08-23.** `load_folder` reads all four columns, `bugarach check` reports
the width rules a folder carries, and CICADA's per-event mode is reachable from a
folder-loaded recording. One line remains open, in a file this work did not own — see
"What is left".

## What was wrong

`_read_event_rows` returned `(time | None, roi, stream)` per row and read no other
column. `Stream.width` was only ever populated through the programmatic
`slice_from_events(durations=...)` path the simulator and bench use. Nothing mapped the
`width_sec` **column** onto it.

```
header:              roi,time_sec,stream,width_sec,width_def,peak_sec,amp
loaded Stream.width: all NaN
```

The consequence with a name: CICADA's `active_duration_mode="per_event"` reads a
per-event duration off `duration_field` on each `Stream`. From an export folder that
field was always `NaN`, and `_build_raster` turns a `NaN` duration into a one-frame run
— so the mode did not fail, it quietly became `fixed`. A whole detector mode was
unreachable through this project's own input contract, and unreachable in the
contract's own failure class: a plausible answer instead of an error.

## Do NOT ask for a re-export. The data is already there and it is good.

Measured on `2026-08-18_revised_2v_periods`, not assumed:

| stream | `width_def` | median | p95 | max |
|---|---|---|---|---|
| fast | `halfprom_width_findpeaks_w` | 0.90 s | 2.5 s | 50.8 s |
| slow | `rise_interval_peak_minus_t50rise` | 2.00 s | 4.1 s | **5.5 s** |

Coverage is complete: across the two current exports, **0 of 429,066 events lack a
width and none lacks a peak.** The slow rule is rise-bounded — exactly the choice that
keeps the number on a coincidence scale. The 186.9 s `fwhm` figure in the producer page
is what fwhm *would* have given on slow; it is the reason interface2 did not use it, not
something they shipped.

One thing worth a producer's eye, not a re-export: fast width has a long tail — p95
2.5 s against a 50.8 s max. The median is a fine coincidence scale, so it is not a
defect, but whether that tail is real events or an artifact of the half-prominence fit
is cheaper for them to judge than for us.

## What was built

**Four columns onto the stream.** `width_sec` → `Stream.width`, `amp` → `Stream.amp`,
`peak_sec` → `Stream.peak`, `width_def` → `Stream.width_def`. `Stream.has_width` and
`Stream.has_peak` answer the question a caller actually has.

**A width carries its rule or it does not travel.** Two refusals, both at the read,
because after the read nothing can separate what has been pooled:

- a `width_sec` with no `width_def` on its row is refused, naming the line;
- two different `width_def` values inside **one stream** are refused, naming both.

Two rules across two streams is the *expected* shape, not an error: a fast transient and
a slow one are not the same measurement, which the spec says in terms and Tony confirmed
on 2026-08-20.

**The peak, by the two routes the contract allows and no third.** `peak_sec` when the
producer sends it; otherwise `time_sec + width_sec`, but only where `width_def` names a
width that reaches a peak. The accepted names are `rise_interval_peak_minus_t50rise` and
`t50rise_to_peak` — identical to `WIDTH_REACHES_PEAK` in the browser, which is the whole
point, since the complaint here is two readers disagreeing. A half-prominence width added
to an onset is not a peak and never was.

**Events sort with their columns.** The loader sorted times with `np.sort` and left any
parallel array where it lay. Harmless while nothing was parallel; a wrong number the
moment something is. Ordering is now one `argsort` applied to every per-event column at
once.

## What a folder with no width does, and why

**It loads.** `width_sec` is asked for and not required, and every detector still runs
without it. A loader that refused would be the consumer overruling a conforming
producer, which is revision 6's exact defect class and has already cost this project a
real error.

**And the caller can tell which happened.** `Stream.has_width` is `False` exactly when
no rule arrived — the absence is a value, not something to infer from a run of `NaN`.
For the caller who genuinely cannot proceed, `load_folder(..., require_width=True)`
raises `WidthNotSuppliedError` naming the recordings and streams that lack one. Refusal
belongs where the need is known, and it fires at load, before any number exists —
FOUNDATIONS §6's shape applied to a different field.

`bugarach check` says the same thing in prose: it names the width rules a folder carries,
and a folder with none gets a note saying what that costs.

What is ruled out is the third option, which is what happened before: scoring `NaN`
durations and reporting the result.

## Reaching CICADA's per-event mode from a folder

Available today, with no detector change:

```python
cicada_detect(slice_, onset_field="peak",
              active_duration_mode="per_event", duration_field="width")
```

`cicada_detect` resolves `onset_field` with `getattr(stream, onset_field)`, so the new
`peak` attribute is reachable through the parameter that already exists. On
`20240708_13` the two duration modes genuinely differ — fast 34 → 39 events, slow
143 → 138 — which is the evidence that durations are being read rather than defaulted.

## What is left, and who owns it

**`load_folder` does not move the peak into `locs`, and `cicada_detect` still defaults
to `locs`.** For a store, `locs` *is* the peak. For a folder it is the half-rise,
because that is the only time the contract guarantees. So a folder-loaded recording run
through `cicada_detect` with default arguments still anchors on onsets and still says
nothing about it — the behaviour the browser refuses.

Promoting `peak_sec` into `locs` at load would fix the default, and was deliberately not
done. It would change what every detector sees *depending on which optional columns the
producer happened to send*, with no tell — a data-dependent silent change is worse than
the gap it closes, and it would move the ground under the `bugarach detect` work running
in parallel.

The fix belongs in `src/bugarach/detectors/cicada.py`, which this work did not own: when
a slice has `Stream.has_peak is False` **and** its `locs` equals its `t50rise` — the
signature of folder input with no peak — `cicada_detect` should refuse rather than anchor
on the half-rise, the way `cicadaTrains` does in the viewer. Filed here rather than done
there.

## How this surfaced, which is the part worth keeping

interface2 reviewed the producer page and reported that `width_sec` **is** read, citing
`io.py`'s `from_arrays` docstring. That was wrong, and this repo took it at face value
and published a page asserting it. They corrected themselves a day later; tracing the
code rather than the docstring is what settled it.

**Twice in two days a claim from a reviewer was applied without being traced** — this,
and a `NaN`-handling bug that turned out to already have a guard. Both were caught, one
by a test and one by a second review. The cheap habit is to trace the path before
editing prose about it: a docstring describing a *parameter* is not evidence about a
*column*.
