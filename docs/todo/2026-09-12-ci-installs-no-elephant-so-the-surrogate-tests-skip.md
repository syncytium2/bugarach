---
status: open
filed: 2026-09-12
---

# CI installs no Elephant, so the surrogate screen's tests skip where it matters most

A design decision — which surrogate a label-free detector trains against — is being taken from the
surrogate screen's measurements. The tests that guard the screen's generators do not run in CI.

## What

`.github/workflows/ci.yml` installs `pip install -e ".[ui,dl]" pytest playwright`. There is no
`surrogates` extra in that line, and on `origin/main` there is no such extra to install: it exists
only on the draft branch carrying the screen (`surrogates = ["elephant==1.2.1"]`, with Elephant also
added to `dev`). `tests/test_surrogates.py` opens with `pytest.importorskip("elephant")`, so without
the package those tests report as skipped rather than failed. The screen's own in-flight handoff puts
the number at 98 tests.

**The skip is silent by design and correct by design** — that is what `importorskip` is for. The
defect is the combination: the seven Elephant-backed candidates are the ones whose defects the
adapter exists to correct, and CI never exercises a single correction.

## Why it matters more than a normal skipped test

The adapter was written because running Elephant 1.2.1 at this project's timescale showed it failing
quietly: joint-ISI dither returning sparse trains unchanged and falling back to uniform dither without
saying so, a dead time silently capped, no seed, millisecond defaults. Each correction ships with a
test that fails if the correction is removed. Those tests are the only thing standing between a quiet
upstream change and a surrogate that is not what the report says it is — and they run on one laptop.

## What to do

- Add the `surrogates` extra to the CI install line when the screen lands, so the three Python legs
  install `elephant==1.2.1`.
- Decide whether Elephant enters `dev` for every clone or stays optional. It is pure Python and small
  next to torch, which CI already installs from the CPU wheel index.
- If it is deliberately left out of CI, the reason belongs in `ci.yml` beside the install line, and
  the screen's report must say its generators are untested in CI.

⚠ **Ordering.** The extra is defined on the draft branch, not on `main`. This closes with, or after,
that branch landing — not before.

## Closes when

CI installs Elephant and the surrogate tests run on all three Python versions, or `ci.yml` records
why they do not.
