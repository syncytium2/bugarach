---
status: open
filed: 2026-08-29
---

# `manifest.csv` is not a reserved name, so the loader tries to read it as a recording

> **Not murderboarded** — a finding for sessions in this tree. Every claim is one
> command away.

`io.RESERVED` holds three names — `metric_dictionary.csv`, `regions.csv`,
`slices.csv`. `dataset._NOT_A_RECORDING` holds five, a different set. **Neither holds
`manifest.csv`**, and the DANDI importer's raw output directory contains one.

Point `load_folder` at a folder with a manifest in it and you get:

```
ValueError: manifest.csv must have columns 'time_sec' and 'roi'
            (found ['session', 'subject', 'age', 'n_roi', 'n_frames',
                    'rate_hz', 'dur_s', 'n_onsets'])
```

## Why this is a contract bug and not a one-off

`docs/export_folder_spec.md` says **any producer can write a folder**, and
`tools/import_dandi.py`'s own docstring makes the point that DANDI:000219 was the first
test of that tolerance — *"Nothing had ever tested that, because every folder bugarach
has read came from one exporter."* A manifest or index file beside the recordings is an
ordinary thing for a producer to ship. The next outside folder that carries one fails on
arrival, with an error naming a column contract the caller never mentioned — the exact
failure mode `dataset.kind()` was written to replace.

## The sharper half: a manifest is silently a RECORDING to `kind()`

`dataset.kind()` counts non-reserved `.csv` files to decide what a directory is. So a
directory holding nothing but `manifest.csv` and a `sessions/` subdirectory reports as

    export_folder — 1 recording CSVs

which is how `<data root>/dandi_000219`, the **raw download**, passes
`require(want="export_folder")`. That is the same defect
[the resolver ordering fix](2026-08-28-the-resolver-exists-and-is-invisible.md) works
around from the other end: PR #395 makes the *name* resolve to the export folder, but the
raw directory still misidentifies itself to anything that looks at it directly.

**Two independent guards, and each covers a hole the other leaves.** Reserving the name
is the one that fixes the shape check.

## What to do

1. **Add `manifest.csv` to both lists** — `io.RESERVED` and
   `dataset._NOT_A_RECORDING`. They are already documented as needing to be "kept in
   step" and they are not; that is the second finding here.
2. **Consider reconciling the two sets outright.** One is used to decide what a folder
   *is* and the other to decide what to *read*, so they need not be identical — but the
   divergence should be deliberate and stated, and right now `dataset.py`'s comment
   claims they are kept in step with `io.RESERVED` while listing two names it does not
   have.
3. **A test with a synthetic folder** carrying an unknown extra CSV, asserting the loader
   ignores it rather than dying on it — or, if the decision is that unknown CSVs must
   fail loudly, asserting THAT and saying so in the contract. Either is defensible;
   silence is not.
4. **Then ask the contract question**: should an unrecognised `.csv` in an export folder
   be ignored, or refused? Ignoring risks reading a folder as smaller than it is (the
   1-recording case above). Refusing breaks producers who ship an index. The contract
   should answer it rather than leaving it to whichever list a caller happens to hit.

## How it surfaced

Chasing whether an overnight K scan had read the Cossart corpus correctly. It had — the
scan used an explicit path to the export folder and scored 59 of 59. The manifest error
came from a verification command that resolved to the raw directory instead, which is
[its own hazard](2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md).
