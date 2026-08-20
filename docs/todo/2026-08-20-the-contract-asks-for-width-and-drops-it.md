---
status: open
filed: 2026-08-20
---

# The contract asks for `width_sec`, the producer now sends it, and the reader drops it

**`docs/export_folder_spec.md` asks for `width_sec` and `width_def` in bold — "asked for",
revision 5's headline addition. The producer built it. `load_folder` throws it away.**

> ## Do NOT ask for a re-export. The data is already there and it is good.
>
> Measured on `2026-08-18_revised_2v_periods`, not assumed:
>
> | stream | `width_def` | median | p95 | max |
> |---|---|---|---|---|
> | fast | `halfprom_width_findpeaks_w` | 0.90 s | 2.5 s | 50.8 s |
> | slow | `rise_interval_peak_minus_t50rise` | 2.00 s | 4.1 s | **5.5 s** |
>
> **Coverage is complete: 0 of 69,223 real events lack a width.** And the slow rule is
> rise-bounded — exactly the choice that keeps the number on a coincidence scale. The
> 186.9 s `fwhm` figure that appears in the producer page is what fwhm *would* have given
> on slow; it is the reason interface2 did not use it, not something they shipped.
>
> So this is **entirely a consumer-side gap**. Re-exporting would produce the same four
> columns this reader still discards. What is needed is the reader, below.
>
> One thing worth a producer's eye, not a re-export: fast width has a long tail — p95 2.5 s
> against a 50.8 s max. The median is a fine coincidence scale, so it is not a defect, but
> whether that tail is real events or an artifact of the half-prominence fit is cheaper for
> them to judge than for us.

## What actually happens

`_read_event_rows` in `src/bugarach/io.py` returns `(time | None, roi, stream)` per row and
reads no other column. `Stream.width` is only ever populated through
`from_arrays(durations=...)`, the programmatic path the simulator and bench use. Nothing
maps the `width_sec` **column** onto it.

Demonstrated on the real export, which has carried width since
`2026-08-18_revised_2v_periods`:

```
header:              roi,time_sec,stream,width_sec,width_def,peak_sec,amp
loaded Stream.width: all NaN
```

`peak_sec` and `amp` go the same way. The contract calls extra columns "ignored rather than
rejected" — which is right for *unknown* columns and wrong for columns the contract itself
requested.

## Why it is worth fixing rather than documenting away

- **A producer did work that reaches nothing.** interface2 added four columns because the
  contract asked. Their export is correct; our reader is where it stops.
- **The one consumer exists already.** CICADA's `active_duration_mode="per_event"` reads a
  per-event duration from `duration_field` on each `Stream`. It cannot be used from an
  export folder today because the field is always `NaN` there — so a whole detector mode is
  unreachable through the project's own input contract.
- **It fails silently, in the contract's own failure class.** Set the mode against a
  folder-loaded recording and you get `NaN` durations, not an error.

## What to do

Read `width_sec` into `Stream.width` in `load_folder`, and carry `width_def` alongside it so
a consumer can tell what the number means before using it — the spec is explicit that a
width without its rule is a column meaning two things. `peak_sec` and `amp` have `Stream`
fields already and should be filled from the same pass.

**Then decide what `per_event` should do when a folder supplies no width**, which is the
common case: refuse, or fall back to `fixed` and say so. Silently scoring `NaN` durations is
the one option ruled out.

## How this surfaced, which is the part worth keeping

interface2 reviewed the producer page and reported that `width_sec` **is** read, citing
`io.py`'s `from_arrays` docstring. That was wrong, and this repo took it at face value and
published a page asserting it. They corrected themselves a day later; tracing the code
rather than the docstring is what settled it.

**Twice in two days a claim from a reviewer was applied without being traced** — this, and a
`NaN`-handling bug that turned out to already have a guard. Both were caught, one by a test
and one by a second review. The cheap habit is to trace the path before editing prose about
it: a docstring describing a *parameter* is not evidence about a *column*.
