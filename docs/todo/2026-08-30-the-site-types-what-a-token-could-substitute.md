---
status: open
filed: 2026-08-30
---

# The site types by hand what a token could substitute, and the project is going to keep moving

> **Not murderboarded** — a work item for sessions in this tree, not a deliverable.
> Every claim below was re-verified against `main` at `c6df955` on 2026-08-30 and
> the command is given wherever it is not a file path.

> Tony, 2026-08-30: *"this project is an infant. all of this will change as it
> matures. the webapp must be able to adapt to these changes. nothing is fixed,
> final, YET. we just refined the bench yesterday if i recall."*

**This item does not decide what the site should report.** It makes deciding cheap,
and re-deciding free. Read the scope section before starting: the temptation is to
fold in the measure question while you are in there, and that is the one thing this
must not do.

## The requirement, in one line

**No number and no count on the site is typed by a person.** Every one resolves from
data at build time, so a bench revision propagates instead of rotting.

## What already meets it

`docs/learned/learned_detector.html` — **159 tokens** of the form
`{{N:store:path|fmt}}`, resolved by `tools/build_learned_report.py` against the JSON
stores at build time.

```
$ grep -o "{{N:[^}]*}}" docs/learned/learned_detector.src.html | wc -l
159
```

And it is not merely generated, it is **gated**: `_page_is_current()` in
`tools/build_site.py:426` rebuilds the page to a scratch path and compares bytes,
refusing to publish when they differ. Its docstring states the failure it exists to
catch — *"the stores move, the page does not, and the prose keeps quoting the
previous run in the previous run's own formatting."*

**That is the pattern. The rest of this item is applying it to three more surfaces.**

## What does not meet it

### 1. `docs/learned/bakeoff.md` — nine rows, no generator

Already filed as
[`2026-08-28-the-bakeoff-page-transcribes-what-a-token-could-substitute.md`](2026-08-28-the-bakeoff-page-transcribes-what-a-token-could-substitute.md);
this item supersedes it in scope and that file should be closed pointing here.

The page says so about itself:

> ⚠ *"The table below is transcribed by hand from `bakeoff.json`, and that is a
> known weakness of this page rather than a feature of it … every re-run needs a
> human to retype nine rows — and on 2026-08-28 one of its claims had been stale for
> eight days without anyone noticing."*

### 2. The README bake-off table — same defect, and it has already cost a branch

`README.md` carries the same nine rows, typed. **There is an orphan branch in this
repo whose entire purpose is hand-copying them when they move** —
`bakeoff-table-is-a-run-behind`, two commits, no PR, no board claim, unowned. Its
second commit is titled *"Sync the detect times to main's bakeoff.json, which moved
under this branch."*

That branch is the running cost of not having tokens here. **Landing this item
retires it**, and whoever does the work should say so in the PR rather than leaving
it to be reaped by someone who has to work out whether it still matters.

### 3. The front page types its own detector count, and the two halves disagree

`tools/build_site.py`, three places in the `INDEX` template:

| line | text |
|---|---|
| 171 | `<h1>bugarach<span class="sub">Six coordinated-event detectors…` |
| 222 | `All six work by finding moments that stand out…` |
| 776 | `<figcaption>… and what five detectors made of it` |

**Six in two places, five in a third, on one page.** Not a typo — `locust` is
withheld from the public build, so the caption is right about the figure and the
prose is right about the repo, and nothing reconciles them.

**The mechanism to fix it already exists and the prose does not use it.**
`_withheld_from_the_viewer()` (`tools/build_site.py:41`) reads the viewer's
`const WITHHELD = new Set([...])` rather than restating it, with a docstring saying
exactly why. So *which* detectors are withheld is already derived. Only the
**count** is typed.

⚠ **The blocker for whoever takes this:** `tools/build_site.py` imports nothing from
`bugarach` — pure stdlib, verified — so it has no detector list to count. It needs a
source. **Prefer `bakeoff.json`**: its `hand_written` and `learned` keys already
enumerate exactly the detectors that were scored, which makes one file the source of
the page's numbers, its detector set and its counts at once. Importing the registry
is the alternative and it couples the site builder to the package.

## 4. The measure-set is the point of the whole item

Items 1–3 make the *numbers* derive. This one makes **which measures are shown**
derive, and it is the part that answers the requirement rather than the symptom.

Today a results table's columns are written into the prose of each page. So
"add a column", "drop F1 to a secondary row", "report firings-per-minute instead of
a count" are prose edits in three files, done by hand, silently divergent.

**Declare the displayed measure-set once**, with its labels and formats, and render
every table from it. Shape is the implementer's call; the requirement is that
changing what the site reports is a one-place edit with a check behind it.

**Why this is the load-bearing item:** the scoring question is open on purpose and
is going to be re-answered more than once. Under the current arrangement each
re-answer is a manual sweep of three files. Under this one it is a line.

## Checks — each item needs one that fires by itself

Prose about keeping these in step is what this item exists to replace, so none of
the above lands as a convention.

- **A page that quotes a number is covered by the staleness gate.** `_page_is_current`
  is applied to the learned page specifically; the gate should cover every generated
  page, and a new page that quotes numbers without being gated should fail a test
  rather than be caught in review.
- **The README table matches `bakeoff.json`.** README is committed markdown, not a
  build artifact, so this is a *test* that parses the table and compares, not a
  generator — a red suite when the numbers drift, which is the alarm the orphan
  branch is currently standing in for.
- **No typed detector count survives.** A check that the front page contains no
  hardcoded numeral where a derived count belongs. Sapper is the natural home;
  `SAP011` is **reserved for a different unbuilt proposal**
  (`docs/sapper_feedback/2026-08-28-a-negative-claim-about-code-went-stale-in-a-contract.md`),
  so take the next free id and say so in the comment, per the convention that file
  already established.

## Out of scope — deliberately, and this is the part to hold

- **Do NOT decide which measures the site reports.** Recall / precision / probe /
  timing / F1 is an open question with Tony. This item makes that decision cheap;
  making it here would spend the flexibility on the first guess.
- **Do NOT touch `src/bugarach/bench.py`**, any operating point, or
  `pick_operating_point`. The selection rule already treats the promiscuity probe as
  a separate gate rather than a term in F1, which is the structure the reporting
  would describe. Nothing needs to move in the code for the pages to become accurate.
- **Do NOT re-run the bake-off** to make numbers "current" while doing this. If the
  tokens are right, the numbers follow whenever it is next run. A re-run inside this
  change makes the diff unreadable and confuses a mechanism change with a data change.

## Who holds what, as of 2026-08-30

`bugarach-63` is ACTIVE on `docs/site/**`, `tools/build_site.py`,
`tools/make_diagnostic.py`, `docs/learned/**` and `tests/test_site_coherence.py` for
site cosmetics, the raster `VSpan` removal and the authorship correction. **This item
is theirs to execute or to hand back** — it is written as a spec precisely so it does
not collide with work already in flight. Coordinate before starting; do not open a
second branch against those files.

The front-page count fix (item 3) **overlaps their attribution work**, which is also
rewriting the opening prose. Doing both in one pass is cheaper than sequencing them,
and the attribution correction has its own reason to change the `<h1>` anyway — it
currently reads *"Six … detectors ported from MATLAB"*, and
[`docs/detector_history.md`](../detector_history.md) says only **one** of the six is
a port.
