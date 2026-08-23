---
status: done
filed: 2026-08-16
closed: 2026-08-23
---

# Data must not load without a sampling interval — the 0.1 s fallback has to go

**CLOSED 2026-08-23.** Everything below is the record of the defect and the
reasoning that shaped the fix; what shipped, and the two questions it had to
settle on the way, are in "How it closed" at the foot of the file. One thing is
NOT closed and is filed separately there: SPIKE-synch's operating point has only
ever been measured at a 10 Hz bin.

FOUNDATIONS §6 was rewritten on 2026-08-16 to require dt at the load boundary.
The code still did the old thing. This was the gap.

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

---

## How it closed, 2026-08-23

The interval is a typed field on the recording, every construction path has to
state it, and no code anywhere chooses a number. `GRID_DT_FALLBACK`,
`GridDtNotSetWarning` and CICADA's `imaging_rate_hz = 10.0` are gone; `Slice.dt`
is a float read once out of `slices.csv` instead of a string in `meta` that four
consumers each re-parsed. Every parity fixture still matches to 1e-9, which is
the whole constraint: this moved where the number comes from and changed no
detector's arithmetic.

### The two questions it had to settle

**1. What is a recording with no interval?** Not a `TypeError` at the folder
reader, which was the first instinct and is wrong. `docs/export_folder_spec.md`
makes `slices.csv` optional — *"only the recording files are required"* — so a
folder with no sidecar is **conforming**, and a loader that refused one would be
the consumer overruling a conforming producer, which is the defect class
contract revision 6 exists for. The spec also says what to do instead: *"if it
is not there, the app asks for it at load, and will not proceed until it has
one… a caller with no interface supplies the value the same way the prompt
would, and gets the same refusal if it does not."*

So the answer separates **silence** from **"we do not know"**, which used to be
the same state of the program:

- `dt` is a required argument everywhere. Omitting it is a `TypeError` at the
  line that omitted it. This is the gate, and it is the thing that was missing.
- `None` is a legal *value* meaning nobody has said. It is reachable from
  `load_folder` on a conforming sidecar-less folder, and from a caller who
  genuinely does not know. Such a recording draws — a raster needs no interval —
  and cannot be measured.
- `Slice.require_dt()` is the only way anything reads the interval, and it
  cannot return `None`. The refusal names `frame_interval_sec`, `slices.csv`,
  `load_folder(folder, dt=...)` and this section.
- `load_folder(folder, dt=...)` is the script's version of the spec's prompt. A
  producer's declaration beats it: `dt=` fills a gap, it does not overrule an
  answer the folder gave, because a caller who could overwrite a declared
  interval could silently rescale somebody else's recording.

One deliberate narrowing: a declared value that will not read as a positive
number of seconds — `30fps`, `0` — does **not** raise in the loader. It becomes
`None` while the producer's raw string stays in `meta`, because `bugarach check`
is what names a producer's typo and it has to be able to read the folder in
order to say so. The loader's guarantee is the narrow one that matters: no
unreadable value ever becomes a number.

**2. Is SPIKE-synch's `dt` an acquisition property?** No — it is a detection
resolution, and the reasoning is written at `sync.PROFILE_BIN_SEC` where the
next person to grep for a hardcoded 0.1 will find it. In short: nothing upstream
of the binning touches a grid at all (`adaptive_profile` works on continuous
event times and ISI-derived windows), and the bin is not a display choice
because the hysteresis rule counts **in bins** — `min_n` floors a sum of `Cn`,
`max_gap` compares bin-centre separations, `peak_min_distance_sec` is divided by
it. `C_threshold`, `C_min`, `max_gap` and `min_n` were all fitted at this bin
width. Wiring `Slice.dt` in would move the detector off its measured operating
point silently, one recording at a time, while the bench went on reporting the
old F1. So the deliverable was the argument and a named constant, not a change:
the parameter keeps its default, the default is now `PROFILE_BIN_SEC` rather
than a literal, and `tests/test_sync_detect.py` pins both the constant and the
fact that rebinning changes the answer.

### Still open, and now separable

**SPIKE-synch's operating point has only ever been measured at a 10 Hz bin.** At
10 Hz the calibrated 0.1 s bin is exactly one frame. A lab imaging at 1 Hz would
be running a grid finer than its own data and this detector's four thresholds
are not calibrated for that. The fix is a bench campaign — re-measure the point
per imaging rate — not a rescale from a caller. Nothing in this repo can show
the problem today, because every recording on the bench shares one grid, which
is the same blind spot the section above describes for learned models.

**`detect_folder` still parses `frame_interval_sec` out of `meta`.** It gets the
right answer from the right column, so this is redundancy rather than a defect,
but it is one of the four hand-written parses this work existed to delete and it
belongs to whoever holds that file.

### Where the mechanism lives now

- `src/bugarach/store.py` — `Slice.dt`, `Slice.has_dt`, `Slice.require_dt`,
  `FrameIntervalNotDeclaredError`, `validated_dt`, and `load_slice(path, dt=)`.
- `src/bugarach/io.py` — `slice_from_events(dt=)`, `load_events_csv(dt=)`,
  `load_folder(dt=)` and `_declared_interval`, which is the one place the
  producer's column becomes a number.
- `src/bugarach/detectors/rate.py` — no fallback, no warning, `grid_dt` required
  and moved to the front of the keyword arguments to say so.
- `src/bugarach/detectors/cicada.py` — `imaging_rate_hz` defaults to the
  recording's own interval.
- `src/bugarach/detectors/sync.py` — `PROFILE_BIN_SEC` and why it stays.
- `tests/test_store.py`, `tests/test_io.py`, `tests/test_cicada_detect.py`,
  `tests/test_sync_detect.py`, `tests/test_rate_detect.py`,
  `tests/test_single_stream_defaults.py` — the rule, mechanized.
