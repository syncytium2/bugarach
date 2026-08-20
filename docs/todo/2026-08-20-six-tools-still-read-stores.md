---
status: open
filed: 2026-08-20
rule: SAP007
---

# Six tools still read `.mat` stores instead of the export folder

SAP007 blocks reading a store from anywhere in `src/` or `tools/`. Six files are
excluded by name because they were doing it when the rule was written. **Each
exclusion is a defect, not a dispensation.** Fixing one means deleting a line from
the rule's `exclude` list, and the list shrinking to nothing is what done looks
like.

| tool | why it matters |
|---|---|
| `tools/make_assembly_closed_figure.py` | **produced numbers containing withdrawn recordings** |
| `tools/modularity_null.py` | **the other analysis in that incident** |
| `tools/fit_background_shape.py` | fits the generator's background from real slices — those constants are in `bench.py` |
| `tools/make_roi_rate_distribution.py` | the per-ROI rate figure, and the interquartile range quoted as the difficulty axis |
| `tools/make_reality_check.py` | renders the one released real raster (FOUNDATIONS §5) |
| *(the store reader, `matlab_ref`, `lab_excluded.py`)* | legitimately read stores; not on this list |

## One that is not like the others

`tools/assess_archive.py` is also excluded, and it is **not** a defect of the same
kind — it takes either input and its docstring says it prefers the folder, warning
when handed a store. The open question there is narrower: should the store fallback
exist at all? A fallback that is silently taken when someone passes the wrong path
is how this whole class of failure keeps happening, and "prefers" is a weaker
guarantee than "only".

## Why this is worth doing rather than grandfathering

The export folder is the corpus the lab approved. `generate_export_folder.m`
honours db4's `exclude` flag, drops what was withdrawn, and records the fact in
`PROVENANCE.md`. A store carries every recording ever processed and has no idea
which ones are usable.

On 2026-08-20 two withdrawn recordings were found inside every number this project
had published about the assembly question. The export was correct and had been for
days; the analyses simply never opened it. Anything on the list above can repeat
that, silently, because reading a store is not an error and produces a plausible
answer.

## What each one needs

Mostly the same change: take a folder rather than a store root, and call
`bugarach.io.load_folder` instead of `load_slice` per file. Two need more thought:

- **`make_reality_check.py`** renders a single real recording that is deliberately
  published (FOUNDATIONS §5 names it as the one exception). It needs one recording
  by id, which the folder can supply — but check the released PNG still matches
  after the switch, because the committed file is on the public site.
- **`fit_background_shape.py`** produced `MEASURED_RATE_SHAPE` and
  `MEASURED_BURST_SHAPE` in `bench.py`. Re-running it against the folder will
  change those constants if the folder's corpus differs from the store's — which
  is the point, since the folder excludes withdrawn recordings. **Expect the
  numbers to move, and treat that as the finding rather than an error.**

## The order to do them in

The two from the incident first, because they are the ones whose published numbers
are known to be affected and which someone may re-run before this is finished.
