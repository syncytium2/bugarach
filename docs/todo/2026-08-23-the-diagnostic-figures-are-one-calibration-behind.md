---
status: open
filed: 2026-08-23
---

# The front page's diagnostic figures predate CICADA's recalibration

The two committed renders — `docs/generator/coord_diagnostic_bench_quiet.png` and its
`_hero` crop — and the sidecar beside them are from before the 2026-08-20 CICADA
retune and the re-derived regimes. The README quotes them, so the page and the picture
agree with each other and both lag the tree.

**Measured, by running the README's own command today:**

| | committed figure | re-run, same seed |
|---|---|---|
| CICADA, probe-block firings | 85 | **35** |
| binned SCE, probe-block firings | 28 | **29** |
| LoCo · CoactDetect | 0 · 0 | 0 · 0 |

So the finding the figure exists to make — two detectors take the activity bait and
two ignore it — survives intact, and the number a reader would quote does not. The
README carries a note saying exactly this, in both places the counts appear.

## This is now unblocked

It was blocked until a few hours ago: `tools/make_diagnostic.py` called the viewer's
compute function without the `dt` it had grown, every detector raised, the failures
were swallowed into the sidecar, and the command still exited 0 having drawn a figure
with no lanes. **`built-site-works` fixed both halves of that** — `dt` comes from the
generator's own `grid_sec`, `StreamResult`'s fields are read by name so a sixth cannot
break it again, and the site build now refuses when any detector did not run. The
command reproduces all six detectors cleanly.

## What is left

Rebuild the two committed figures and re-quote the two counts in the README, then
delete its two notes. Deliberately not done in the same pass as the prose repair: these
are **published artifacts** — the hero is on the public site — and replacing them is a
change to what the site serves, which wants its own claim on the board rather than
riding along with a documentation fix.
