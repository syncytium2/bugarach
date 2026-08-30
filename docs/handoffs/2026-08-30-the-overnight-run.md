# The overnight run — objects, provenance, a rerun bake-off, and a live site

Tony, 2026-08-29, going to bed: *"in the morning i want to see optimizatoin and
training and performance charts for the detectors and the dl approaches. webiste
should be deployed and ready to test."*

All of it is done. **The site is live and current** —
`https://bugarach.tonydefazio.com` was 42 commits behind, 14 of which changed what
it serves; it is now built from tonight's tree, all six pages return 200, and the
served `viewer.html` is byte-identical to the built one (`8e1db40a…`). The deploy
is **released**: nobody holds it.

---

## Two findings, and they are the reason to read further

### The guard works, on the axis F1 cannot see

`docs/learned/guard_screen.png`

| cell | F1 | probe firings a fold |
|---|---|---|
| tube (subtract, no guard) | 0.681 | **20.5** |
| tube_guard (subtract + GUARD) | 0.673 | **4.8** |

Four folds of thirty planted events cannot separate 0.681 from 0.673. Read from
the bake-off bar chart alone, **the guard interval did nothing.** On the probe
block — which contains no planted events, so every firing in it is a false alarm
by construction — it fires a quarter as often for the same accuracy.

That is not a lucky seed, it is a prediction landing. Guard cells are what the
radar literature reached for on exactly this failure, and
[`detector_history.md`](../detector_history.md) §5 derived the same defect here
independently, before anyone in this project had read that literature: *"none of
the three excludes the moment under test from its own measurement."* This is the
first time it has been measured on a learned model in this repo.

⚠ The **ratio** arm is a different story and costs F1 (0.503 and 0.471). It is
drawn so the figure is a screen and not a highlight reel.

### Four of six detectors calibrate to a different operating point per fold

`docs/learned/optimization.png`

| detector | knob | across four folds |
|---|---|---|
| rate+context | `excess_threshold_hz` | one setting |
| SPIKE-synch | `C_threshold` | one setting |
| the sixth | `sce_percentile` | two |
| CoactDetect | `alpha` | two |
| **LoCo** | `threshold_pctile` | two — **and one is the floor of its grid** |
| **binned SCE** | `threshold_pctile` | two — **and one is the floor of its grid** |

`bugarach.bench` already has a standing refusal for this — *"it will not report an
optimum sitting on the edge of the grid it searched"* — because an edge value
means the search was still climbing when it ran out of room. That refusal governs
`bench`, not `fair_bakeoff`, so the condition arises inside the bake-off and is
reported rather than refused.

**What it costs:** a mean F1 over four folds calibrated four different ways is a
weaker quantity than it looks, and LoCo's and SCE's numbers rest partly on a grid
edge. Widening those two grids is the obvious next move and was not done — it
changes published numbers, which is your call and not an overnight one.

---

## What was built

**Detectors are objects.** `docs/site/detectors/{rate,sce,coact,loco,cicada,sync}.js`
— one file each, descriptor *and* algorithm. `const DETECTORS = {}` declares
nothing now; the folder is the list. `tools/assemble_viewer.py` splices them into
the page at build time (the page must stay one file making zero requests, so the
folder is a source layout and the single file is the artifact), and the assembled
page is **committed** so `git diff` still shows what an outside lab runs.
`--check` refuses drift between the two.

**Networks are objects.** `learn/nets.py` became `learn/nets/`: shared machinery in
`__init__`, one file per architecture beside it, auto-imported so a dropped-in
file registers with nothing else edited. There is deliberately **no list of
architecture names anywhere**. A broken architecture raises rather than quietly
shrinking the registry.

**Every run says what produced it.** `bugarach.provenance` replaced three different
answers under two identical names (`detect_folder` returned a git sha, `ui/app.py`
a package version, the browser a hardcoded `null`, `fair_bakeoff` nothing).
`run.json` gains a `provenance` block **beside** `code_version`, which stays a
scalar because other teams read it. `git_dirty` is tri-state: `None` means nobody
could check, `False` means checked and clean, and only the second lets you trust
the commit beside it.

Combined with #398's `score_spec`/`transfer`, a `bakeoff.json` now answers **which
code** and **which data**. Neither alone is enough for the cross-dataset test.

**Two gates that did not exist.** `test_registries_do_not_drift` compares the
viewer's detector list to the library's — nothing did, so adding a detector had a
silent second half. `test_architectures_are_files` pins both directions of the
registry. `assemble_viewer --check` catches a hand-edit of the generated page.

---

## Three things waiting for you

1. **PR #404 is armed to auto-merge and had not landed at deploy time.** So the
   site is deployed from a branch. That is checkable rather than asserted —
   `build_site.py` reads `docs/site/raster_viewer.html`, `docs/learned/*.html`,
   `docs/generator/reality_check.png` and `src/bugarach/**`, and the branch differs
   from `main` in exactly those. `site_staleness.py` will say *"MATCHES NO
   COMMITTED VERSION"* until #404 merges; that is the tool being right about a
   branch deploy, not a defect.
2. **The grid edges** on LoCo and binned SCE, above.
3. **ADR-0005 is drafted and uncommitted** in this worktree. It predates the
   ordering finding below and needs a pass before it lands.

## One thing that bit, and will bit again

**Detector order was incidental and is load-bearing.** `rate` was first only
because it was first in the literal; moving it to a file put it last, which moves
`detections.csv` row order, raster lane order, and *the sequence detectors draw
from the shared RNG*. `test_webapp_tune_picks` caught it — that was luck.
`DETECTOR_ORDER` declares it now, and an unlisted detector loads at the end.

**And the merge collision ADR-0005 predicted arrived on the first merge.** `main`
edited `raster_viewer.html` in three places while this branch made that file
generated. Git auto-merged it, which is meaningless for a build artifact; each
change was rehomed by hand (two to the template, one to `cicada.js`) and
reassembled. Every session that edits that file needs telling.

Suite **1,583 green**, sapper clear.
