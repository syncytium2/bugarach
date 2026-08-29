---
status: done
filed: 2026-08-28
closed: 2026-08-29
---

# `locs` is a field name, not a value, and `rise_durations()` is zero on every folder

> **CLOSED 2026-08-29 — and the first half of what this file proposed is now
> forbidden.** Item 1 below offered two ways out, *"use the peak or refuse"*.
> Tony ruled, and only the second survives: *"matlab decides duration. bugarach
> python and webapp is not responsible for what the duration is derived from."*
> `rise_durations()` raises `DurationIsNotOursToDerive`; `peak - locs` — the
> repair this file suggested — is blocked by **sapper SAP012** alongside the
> subtraction it was meant to replace, because the rule is not *derive it
> correctly*, it is **do not derive it**. An event's duration arrives in
> `width_sec` under its `width_def` and the port paints what it is given.
> Items 2 and 3 landed as written (`tests/test_rise_durations_on_a_folder.py`,
> and the doc pass of 2026-08-29). Item 4 — `Stream.onset` / `Stream.peak_time`
> resolving per input kind — is **not done and still worth doing**; it is the
> only part of this file that is still live work. Read the rest as the record of
> how the derivation was found, not as a plan.

> **Replaces `2026-08-28-the-export-sends-a-peak-and-cicada-never-reads-it.md`,
> filed and retracted the same day.** That file claimed `cicada_detect` anchors on
> "the wrong landmark" for folder input and proposed a bench run at
> `onset_field="peak"`. **Do not do that — the anchor is correct.** The retraction
> matters more than the file: acting on it would have moved the detector off the
> onset and onto the peak, which is the direction this project deliberately came
> *from*.

## The thing that confuses everyone, stated once

**`locs` is a legacy FIELD NAME, and the VALUE in it changed.**

It comes from MATLAB `findpeaks`, which returns `[pks, locs]` — peak heights and
peak locations. To draw detected peaks on a calcium trace you plot `x=locs,
y=pks`. So in the **event store archive**, which carries `pks, locs, t50rise,
width, amp` plus the identifier columns, `locs` is the **peak time**.

**Coordination does not want the peak time.** It wants the onset, and `t50rise`
is the only onset measure the detection analysis produces. Tony's account of how
the field came to disagree with its name (2026-08-28):

> *"when i manually coded the early versions of the coordination routines, i just
> passed locs. the field name is probably locs. pretty quickly we put t50rise
> into the coordination data field locs. hence the crisis"*

So in the **coordination data**, the field named `locs` contains **`t50rise`**.
The name kept the old meaning; the contents did not. `bugarach.store.Stream`
records the consequence — a store's `locs` is the peak, a folder's is the
half-rise — and every *other* explanation of `locs` in the tree still uses the
store's meaning.

## What is actually broken

`rise_durations()` computes the rise interval as `locs - t50rise`. In a store
that is `peak - onset`, which is right. **On folder input the two fields hold the
same value, so it returns zero for every event.**

Verified on `dataset.current()`, `20240708_13`, fast:

```
rise_durations   2215 events   min 0.0   max 0.0   all zero
peak - locs      median 0.30 s   max 2.20 s        <- the real interval, unused
```

The interval **is available**: the producer sends `peak_sec`, `io.py` loads it
into `Stream.peak`, and nothing reads it. `has_peak` is defined in `store.py` and
has no callers anywhere in the tree.

## How bad, precisely

**Latent, not live. Nothing shipped is wrong because of this.**
`OPERATING_POINTS["cicada"]` runs `active_duration_sec=1.0` — *fixed* duration
mode — so `rise_durations()` is not on the deployed path. It bites only
`active_duration_mode="per_event", duration_field="rise_dur"`, the mode
`explore_sce` uses **to tame long SLOW transients**. Anyone reaching for that on
an export folder marks every cell active for **zero seconds**, and a detector
that then finds nothing looks like a detector that found nothing.

**The existing test cannot catch it.** `test_rise_durations_matches_definition`
runs on `SLICE.fast`, a *store* fixture, where `locs` genuinely is the peak. The
function is correct there and wrong on the input the project actually uses. No
test loads a folder and asks what a duration came out as.

## Not the producer's zero-width, which is already handled

`<darkroom>/constellation/cicada_zerowidth_explainer.png` documents a **different**
zero: a detected event's `width_sec` collapsing when member onsets fall outside
the peak's window, because co-activity was built from 1 s painted durations that
began earlier. Their fix — floor the width at the window scale — **is already in
this port** (`cicada.py`: *"member-onset span, floored at the window duration"*).
Read that figure before touching anything here. Theirs is the **output** width;
this is the **input** duration.

## The docs that now say the wrong thing

Each explains `locs` with the store's meaning in a context where the input is a
folder:

- `cicada.py`: *"the default is `locs` — the PEAK, not the onset."* On a folder it
  is the onset. The sentence after it — that anchoring on onsets *"would call
  nearly any two events coordinated"* — reads as a warning against what the code
  actually does, which is exactly how the retracted file went wrong.
- `detect_folder.py`'s `ONSET_FIELD` comment: *"CICADA anchors on the peak
  (`locs`)"*, in the module whose whole job is folders.
- `detector_settings.csv` emits `onset_field=locs` for cicada. A reader who looks
  that value up learns "peak". The run used the half-rise.

## What would settle it

1. **Make `rise_durations()` use the peak or refuse.** With `has_peak` the
   interval is `peak - locs`. Without it — any producer that sends no peak —
   there is no rise interval to compute, and returning zeros silently is the
   worst of the three available answers.

> **This is a fact about THIS LAB's data and none of it transfers to the Cossart
> corpus.** The `locs` / `t50rise` history above is ours: our MATLAB coordination
> routines, our field name, our substitution. Tony, 2026-08-28: *"this doesn't
> apply to the cossart dandiset. i have no clue what's in there."* What the
> imported DANDI folder carries is only what `tools/import_dandi.py` observed in
> the files — a binary raster and its timestamps — and that importer deliberately
> does not name the inference step that produced it. A reader must not carry this
> page's conclusions across into that corpus; the two share a loader and nothing
> else.
2. **A test on folder input**, not a store fixture. That gap is why this sat.
3. **Fix the three doc sites** to say what `locs` holds per input kind. The name
   cannot be changed cheaply — it is in the store archive, the MATLAB originals
   and the parity fixtures — so the name stays and the docs carry the warning.
4. Consider whether `Stream` should expose `onset` and `peak_time` properties
   that resolve per input kind, so callers stop reading `locs` directly and the
   legacy name survives only at the boundary.

Not fixed here: found from a branch that does not touch
`src/bugarach/detectors/**`, and the retracted version of this file is a standing
demonstration of what changing a detector on a misread would have done.
