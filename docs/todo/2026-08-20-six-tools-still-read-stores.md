---
status: done
filed: 2026-08-20
closed: 2026-08-20
rule: SAP007
---

# Six tools read `.mat` stores instead of the export folder — done

All six now take `--folder` and read the export folder through
`bugarach.io.load_folder`. **SAP007's exclusion list no longer names any of them**,
which is what done looks like here: fixing one meant deleting a line, and there are
no lines left.

| tool | what changed |
|---|---|
| `modularity_null.py` | reads the folder — and its spreadsheet-reading exclusion workaround is **deleted**, see below |
| `make_assembly_closed_figure.py` | takes `--folder`; refuses by name if the recording is not in the corpus |
| `make_roi_rate_distribution.py` | `--folder` required, with the reason in the error |
| `make_reality_check.py` | `--folder` required; the guard is loudest here because the figure is published |
| `fit_background_shape.py` | `--folder` required; it fits the generator constants |
| `assess_archive.py` | unchanged — it already preferred the folder; see the open question below |

## The workaround that went away

`modularity_null.py` had grown a `--exclude-file` and a `load_excluded()` call
reading the lab's spreadsheet directly, added after the incident. That is the wrong
shape twice over: it re-derives downstream what the producer already decided, and
it only ever protected the one tool somebody remembered to patch. The folder
excludes by not containing, so the flag, the loader and the `skipped["excluded"]`
counter are all gone.

## What moved, and it is the export doing its job

Reading the approved corpus instead of the store changes numbers, because the
corpus is smaller and different. **Tony, 2026-08-20: "axis shift is expected. the
export has done it's job."** Recorded so nobody reads a moved constant as a
regression:

| quantity | on the store | on the folder |
|---|---|---|
| recordings surveyed | 85 | **84 (80 usable baseline windows)** |
| per-ROI rate p25 (`baseline_quiet`) | 3.8 mHz | **5.2 mHz** |
| per-ROI rate p75 (`baseline_busy`) | 17.5 mHz | **19.0 mHz** |
| difficulty span | 4.61× | **3.65×** |
| `MEASURED_RATE_SHAPE` | 0.275 | **0.277** |
| `MEASURED_BURST_SHAPE` at 60 s | 1.388 | **1.429** |

**None of these were applied.** `bench.REGIMES` and the measured shapes are
untouched, because changing them re-scores every detector's operating point, and
that is a calibration decision under FOUNDATIONS §9 rather than a side effect of a
refactor. The two shape constants barely move and would change little. The
difficulty axis moves a lot, and `bench.py` currently argues that p25 "lands within
5% of the TTX median (0.0040)" — an argument that does not survive the shift.

**Open: decide whether to re-derive `bench.REGIMES` from the folder.** Every bench
number in the repo was computed against a range fitted to a corpus that included
recordings the lab withdrew.

## The published figure was checked, not assumed

`make_reality_check.py` draws the one real recording that is committed and on the
public site (FOUNDATIONS §5). Its data is identical from both sources — 37 ROIs,
633 fast events, one region — so the recording is unaffected. The rendered PNG
differs in bytes because the local chromium moved 1228 → 1234 the same day, and
the committed file was **deliberately not regenerated**: that diff would look like
a data change and is not one.

## Still open

**Should `assess_archive.py` keep its store fallback?** It prefers the folder and
warns when handed a store, which is better than the six were. But "prefers" is a
weaker guarantee than "only", and a fallback silently taken when somebody passes
the wrong path is how this class of failure keeps happening.

**`cli.py` and `ui/app.py`** stay excluded from SAP007 as the store path's own
entry points under FOUNDATIONS §4. Whether that path should exist at all is a
product question rather than a gate's.
