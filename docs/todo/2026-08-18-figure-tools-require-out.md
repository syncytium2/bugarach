---
status: open
filed: 2026-08-18
---

# Half the figure tools require `--out`; the other half default to the darkroom

Six figure tools take `--out` as required. Five take it with `default=None` and fall
back to `bugarach.paths.darkroom()`. Nothing marks which is which, so whether a figure
reaches the place people read from depends on which tool drew it.

## How this surfaced

The report builder had the required form, and the assembly report went to
`docs/learned/` and nowhere else. Tony opened the repo copy and asked why it was not in
Dropbox — which is the entire failure: a deliverable that lives only in a git checkout
cannot be read by anyone who does not have one, and FOUNDATIONS §5 puts report output in
the darkroom for that reason.

Sapper **SAP006** now blocks the required form, but deliberately only in
`tools/build_*.py` and `tools/md_to_page.py`. It is scoped that narrowly because the same
regex fires on tools where requiring `--out` is correct — `derive_spec.py`,
`assess_archive.py` and `fair_bakeoff.py` write data for a pipeline, not a deliverable
for a person, and a rule that fires on correct code is a rule someone switches off.

## The ones still requiring it

| tool | draws |
|---|---|
| `make_regime_figure.py` | regime figure |
| `make_tolerance_figure.py` | scoring-tolerance figure |
| `make_architecture_figures.py` | architecture figures |
| `make_bakeoff_figures.py` | bake-off figures |
| `make_learned_figures.py` | learned-detector figures |
| `make_explainer_figures.py` | explainer figures |

Already defaulting to the darkroom: `make_diagnostic.py`, `make_roi_rate_distribution.py`,
`make_reality_check.py`, `make_generator_figures.py`, `assembly_power.py`,
`make_assembly_figure.py`, `make_membership_example.py`, `make_tube_figure.py`.

## What to do

Give the six the same shape as the eight — `default=None`, then
`out = args.out or darkroom()`, printing `unresolved_message()` and returning 1 when it
cannot be found. Then widen SAP006's `include` to `tools/make_*.py` so the split cannot
reopen.

Not done in the same change because each of the six writes a different figure set and
none was exercised in that session; changing an output path untested is how a figure
quietly stops being written at all. Each wants a run and a look at what it produced.

## The adjacent gotcha, for whoever picks this up

`~/Dropbox-UniversityofMichigan` is a **symlink** to
`~/Library/CloudStorage/Dropbox-UniversityofMichigan`. Both paths are the same directory.
A session checking whether a file "really" reached Dropbox can look at one, see the other
in a tool's output, and conclude they are different places. They are not — verify with
`ls -ld` before concluding anything is missing or duplicated.
