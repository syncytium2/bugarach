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

### 3. The front page types its own detector count in seven places, and they disagree

**REVISED 2026-08-30, after this file was first written.** The original said three
locations and recommended *deriving* the count. Both were wrong. Corrected below;
the original reasoning is left visible at the end of this section because the
argument against it is the useful part.

Re-counted on `main` at `0188362`, `tools/build_site.py`, reader-facing strings only:

| line | says | text |
|---|---|---|
| 171 | six | `<h1>bugarach…Six coordinated-event detectors ported from MATLAB` |
| 181 | **five** | `There are five in this build` — **and names the roster** |
| 222 | six | `All six work by finding moments that stand out…` |
| 248 | six | `…and where the six methods come from` |
| 779 | six | alt text: `Six detector lanes … and six analysis traces` |
| 783 | **five** | `…and what five detectors made of it` |
| 786 | **five** | `two of the five are named for what…` |

**Seven locations. Four say six, three say five.** Not a typo — `locust` is withheld
from the public build, so the "five" strings are right about the figure and the "six"
strings are right about the repo, and nothing reconciles them.

Not on this list, deliberately: line 283's *"about six of thirty-three"* is a
**participation** figure — ROIs recruited per event — not a detector count. It is
correct and must not be swept up by a fix that pattern-matches on numerals.

#### The fix is to remove the count, not to source it

**A sentence with no count in it cannot go stale.** A derived count is still a thing
that resolves a key at build time, and can silently resolve the wrong one. Removing
the number removes the failure mode rather than automating it.

It also dissolves the blocker the original version of this file spent a paragraph on:
`tools/build_site.py` imports nothing from `bugarach` — pure stdlib, verified twice
independently — so a derived count needs a *new* data source wired into the builder.
Eliminating the count needs none, and couples the site builder to nothing.

⚠ **One of the seven is not a count and needs a different answer.** Line 181 does not
merely say "five", it **names the roster** — so deleting the number there would still
leave five detector names typed by hand. A named list is worth more to a reader than
a count, and rots the same way. `_withheld_from_the_viewer()` (`build_site.py:41`)
already derives *which* detectors are withheld, by reading the viewer's
`const WITHHELD = new Set([...])` rather than restating it. **That is the mechanism
for line 181** — the roster, not the count.

<details>
<summary>What this section said first, and why it was replaced</summary>

It listed three locations instead of seven, and recommended deriving the count from
`bakeoff.json` on the grounds that its `hand_written`/`learned` keys enumerate exactly
what was scored, making one file the source of the page's numbers, its detector set
and its counts at once.

That is a real option and it is worse. It solves "the count is wrong" by building a
machine to keep it right, when the count carries almost nothing for the reader in six
of the seven places it appears. **Prefer deleting a fact to automating it, when the
fact was not load-bearing.** The exception is line 181, above, where it is.

</details>

#### Provenance of this revision, stated because it matters here

The elimination approach reached this file **relayed by another session**, quoting
Tony on 2026-08-30 as: *"maybe just rewrite the text so it is independent of how many
detectors are currently enabled?"*

**That is a hedged suggestion phrased as a question, and it is recorded here as one.**
It was relayed to this file's author as "the other instruction directly"; it is not an
instruction and this file does not treat it as a ruling. The reasoning above stands on
its own merits — no count cannot go stale, no source is needed, nothing gets coupled —
and would stand if Tony had never said it. **If the argument is wrong, it is wrong on
the argument, and no one should find a decision here that was never made.**
(This session mis-relayed a hedge of Tony's as a ruling earlier the same day; the
write-up is in `syncytium2/short-course`. Same failure, one hop over, caught this time.)

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
- **No typed detector count comes back.** A check that the front page's prose carries
  no detector count at all. It must **not** fire on line 283's participation figure —
  a rule keyed on bare numerals would, which is the trap that makes this check worth
  writing carefully rather than quickly. Sapper is the natural home;
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

## Who holds what — UPDATED 2026-08-30, nothing is held

`bugarach-63` landed **#411** (`0188362`) and **released every path it held** —
`docs/site/**`, `tools/build_site.py`, `tools/make_diagnostic.py`,
`tests/test_site_*`. Its worktree is reaped and its board block is closed.

**It declined this item, and the reason is a constraint on whoever picks it up.**
Tony pulled it up for scope — *"address this critique does not mean run wild"* — so
items 1, 2 and 4 are **his to release**, not for a session to start on its own
initiative. Item 3 overlaps work it has reserved but not started (`who-wrote-these`,
the authorship correction), also waiting on Tony.

**Nothing here is unblocked by the absence of a claim.** The paths are free; the work
is not authorized. Ask before starting.

The front-page count fix (item 3) **overlaps their attribution work**, which is also
rewriting the opening prose. Doing both in one pass is cheaper than sequencing them,
and the attribution correction has its own reason to change the `<h1>` anyway — it
currently reads *"Six … detectors ported from MATLAB"*, and
[`docs/detector_history.md`](../detector_history.md) says only **one** of the six is
a port.
