---
status: open
filed: 2026-08-16
---

# Data must not load without a sampling interval — the 0.1 s fallback has to go

FOUNDATIONS §6 was rewritten on 2026-08-16 to require dt at the load boundary.
The code still does the old thing. This is the gap.

**Read with [`2026-08-16-dt-does-not-travel-with-the-recording.md`](2026-08-16-dt-does-not-travel-with-the-recording.md).**
Two sessions filed on this the same day and neither knew about the other. They are
halves rather than duplicates: this one is the fallback that has to go, that one is
why the interval has nowhere to live — it is not a field on `Slice`, so it arrives
in `meta` as a string and only `conform.py` ever reads it, to validate it and print
it. It also names the cheaper fix, which is upstream and not ours.

> Tony, 2026-08-16: *"we cannot allow data loading without the user specifying a
> dt."*

## What the code does today

`grid_dt` is optional at **detection** time and falls back to 0.1 s:

- [`src/bugarach/detectors/rate.py:40`](../../src/bugarach/detectors/rate.py#L40) —
  `GRID_DT_FALLBACK = 0.1`, the MATLAB original's hardcoded 10 Hz MLspike grid.
- [`src/bugarach/detectors/rate.py:48`](../../src/bugarach/detectors/rate.py#L48) —
  `_resolve_grid_dt` warns `GridDtNotSetWarning` and returns the fallback.
- Reached from `event_rate`, `rate_context` and `rate_detect`.

**Three detectors assume the acquisition interval and only one complains.**
Reported by the `refresh-murderboard-vendor` session (PR #45) and verified here
against `origin/main`:

| detector | how it gets the interval | says anything? |
|---|---|---|
| `rate_detect` | `grid_dt=None` -> `_resolve_grid_dt` | **warns** (`GridDtNotSetWarning`) |
| `sync_detect` | `dt: float = 0.1` | **silent** |
| `cicada_detect` | `imaging_rate_hz: float = 10.0`, then `dt = 1/rate` | **silent** |

Every one of the 7 `GridDtNotSetWarning` references in the tree is inside
`rate.py`. So a lab imaging at 20 Hz that supplies nothing gets **one warning and
two quietly wrong answers** — which is a sharper version of this todo's own
argument: the warning is not merely late, it is also outnumbered two to one by
paths that do not raise it.

Nothing at the **load** boundary asks for it at all: `bugarach.store` readers and
`bugarach.io.slice_from_events` construct a `Slice` with no sampling interval.

## Step 5 has landed. The loader half has not, and it is the half that matters

The Panel viewer no longer carries a defaulted `grid_dt` widget or a hardcoded
`imaging_rate_hz`. It reads `frame_interval_sec` out of `Slice.meta`, shows the
value and where it came from, derives rate+context's `grid_dt` and CICADA's
imaging rate from it, and **refuses to run any detector on a recording that does
not state one** — the rasters still draw, because they need no interval. A person
who knows the interval types it into the one field that asks for it.

That closes item 5 below and nothing else:

- **`Slice` still has no `dt` field.** The interval arrives as a *string* in
  `meta`, because that is where `load_folder` parks the whole `slices.csv` row, so
  every consumer that wants it has to know the column name and parse it. The
  viewer now does; nothing else does.
- **`slice_from_events` and the store readers still admit data with no interval
  at all**, which is exactly what §6 says must be refused. The viewer's refusal
  fires one boundary too late — at analysis, not at load — and it is the only one
  that fires.
- **`GRID_DT_FALLBACK` and `GridDtNotSetWarning` remain reachable** from every
  caller that is not the viewer.
- **`sync_detect`'s `dt: float = 0.1` is deliberately untouched.** The viewer does
  not hand it the recording's interval: `bench.OPERATING_POINTS["sync"]` does not
  declare `dt`, so the calibrated SPIKE-synch point *is* the 0.1 s profile grid,
  and rescaling it from the viewer would move a detector off its measured
  operating point rather than fix a bug. It belongs with this work, where the
  interval can be threaded through and the point re-measured in one go.

The remaining work is owned by whoever holds `src/bugarach/io.py`,
`src/bugarach/store.py` and the three detector signatures — not the viewer.

## Why a warning is the wrong instrument

A warning fires *after* the number exists. By the time anyone reads stderr the
trace is computed, the figure may be drawn, and the export may be on disk — and
FOUNDATIONS §8's own cautionary case is exactly this shape: *artifacts outlive
the settings that made them*, indistinguishable at a glance from current output.

It is also silently correct here and silently wrong elsewhere. 0.1 s **is** this
lab's rate, so every warning raised in this repo has been a false alarm in
practice, which is the fastest way to train a team to filter one out. A lab
imaging at 1 Hz or 30 Hz gets a wrong answer with a warning nobody reads.

## Who is doing it

**The wiring belongs to the workflow-app input contract (PR #45), by agreement
between the two sessions on 2026-08-16.** That branch already defines a
`frame_interval_sec` field and its first milestone threads it into the three
detectors above. Its entry point *is* the load boundary this todo argues for, so
duplicating it here would be two sessions editing the same three signatures.

This file stays the rationale and the inventory. **Do not start the wiring from
here without checking PR #45 first.**

## The shape of the fix

1. **`Slice` carries `dt`**, set at construction, with no default. Loaders take it
   as a required argument; `slice_from_events` likewise.
2. **Refuse rather than default.** Loading without dt raises. There is no
   "unknown" state for a loaded recording to be in.
3. **Detectors read dt off the slice** instead of accepting a per-call `grid_dt`,
   where that does not disturb parity — see the constraint below.
4. **Retire `GRID_DT_FALLBACK` and `GridDtNotSetWarning`** once nothing can reach
   them. Leaving a dead fallback in place invites its reuse.
5. ~~**The viewer asks once, at file intake**, not per detector run.~~ **Done** —
   see "Step 5 has landed" above.

## Constraints a fix must respect

- **Parity is the product (§2).** The six ports' seconds-valued parameters are
  part of the MATLAB contract and must not be reinterpreted. This work changes
  where dt *comes from*, never what a detector computes from it. Every parity
  fixture must still match to 1e-9 afterwards.
- **`bench.py` passes `grid_dt=0.1` explicitly**
  ([`src/bugarach/bench.py:116`](../../src/bugarach/bench.py#L116)) because that
  is the generator's own grid. It is already correct and should keep working.
- **The generator knows its grid** (`grid_sec`), so a simulated `Slice` can carry
  dt for free — no user prompt needed on synthetic data.
- **Foreign/CSV data has no dt anywhere in it.** That is the case this rule
  exists for, and the answer is to ask, not to infer.

## Why it matters beyond tidiness

Anything learned from this data has a receptive field measured in **frames**. At
0.1 s a 0.36 s event spans ~4 frames; at 30 Hz the same biological event spans
11. A model trained here and deployed there has silently learned this lab's
imaging rate, and **nothing on our bench would show it** — every recording on the
bench shares one grid. Guaranteeing dt at the boundary is what makes the
seconds↔samples conversion total, and therefore what makes it safe for downstream
code to work in samples, which is the unit that actually generalizes.
