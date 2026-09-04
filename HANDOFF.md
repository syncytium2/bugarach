# Handoff — walk the loop end to end, and validate it

**In flight: [#466](https://github.com/syncytium2/bugarach/pull/466)** — the field-step
figure, held because it is a figure with a caption and was never murderboarded. When it
closes this file is spent and `tests/test_handoff_is_honest.py` says so out loud.

*(MAHICE in the webapp landed while this handoff was in review, so it is named below as
work to walk rather than here as work in flight. The gate reads the first forty lines
and every PR it finds there must still be open — which is the gate doing its job, and it
caught this one.)*

> **Not murderboarded** — working material for sessions in this tree, same standing as
> `docs/run_records.md` and the K todo. Nothing here is for an outside reader; if any of
> it becomes one, murderboard that artifact first.

**No counts in this file, deliberately.** The handoff it replaces put its own rot on the
record twice in three days. Derive them:

| what | how |
|---|---|
| `main`, the suite, sapper | `git rev-parse --short origin/main` · `pytest -q` · `python3 tools/sapper.py --all` |
| the boards | `bash tools/board_digest.sh` |
| what is established, how strongly | [`docs/MILESTONES.md`](docs/MILESTONES.md) |

---

## The job

**The point of the walk is that Tony sets K on the approved folder.** Everything else
here is in service of that, and reading it the other way round gets the priorities
backwards. Tony, 2026-09-03: *"we've been waiting for the walkthru to do this very
step."*

K is the one quantity nobody can compute and nothing downstream can proceed without —
it moves the headline by an order of magnitude, and the generator's cluster rate, the
simulated data set, the operating points fitted against it and every score quoted from
them all inherit it. Until 2026-09-03 there was no way to set it that left a record; now
there is, and it has never been used on real recordings.

**So the deliverable is a `mahice.json` for this folder**, with a percentage Tony set
having looked, his name on it, and the ROI population it resolved against. Not a number
in a conversation — the file.

**Walking the loop is how that setting becomes trustworthy rather than another number
nobody can defend.** Each step below is a chance for the sequence to break somewhere that
only shows end to end, and a K set on top of periods that were read wrong is worth no
more than the one it replaces. So: walk it, on the real folder, as a person would — and
say where it breaks.

Six things landed on 2026-09-03 and every one was verified *in isolation*. **The sequence
has never been run.** That is the gap this handoff exists to close, and it is the kind
that only shows up end to end: each piece passing its own tests says nothing about
whether *derive the spec* can read what *confirm the events* wrote.

The loop is [`docs/RESET.md`](docs/RESET.md) **§2** — Tony's own statement of it, with
the four places reality differs marked. **§3** is the built/not-built table. **Read §2
before starting**; the app-build plan in `workflow_plan.md` is *not* the loop, and a
session on 2026-09-03 lost half a day to reading it as one.

### The folder to walk it on

```
<data>/exports/bugarach/2026-09-03_revised_2v_long_PRE_ARTIFACT_KILLER
```

interface2's draft-final-run export. 84 recordings, both streams, raw db4 periods **and**
`long_window_20` analysis windows. Its own `README.md` and `PROVENANCE.md` sit beside the
CSVs and are the authority on it.

⚠ **The name is the caveat and it is load-bearing.** Whole-field brightness steps that
produce false coordinated events are still in this data. Use it for the draft run; **do
not publish a coordination result from it** without saying it is pre-artifact-killer. A
successor without that suffix has had the artifact work applied.

⚠ **`current_export.toml` still declares the August folder.** Anything reading
`dataset.current()` gets `2026-08-18_revised_2v_periods`, which holds the same recordings
with **no** `analysis_*` columns — so it scores whole raw periods where this one scores
`long_window_20`. Same events, different windows, different numbers. Redeclaring is
Tony's call and the file says to change the name there and nowhere else.

### The steps, by name, and what to check at each

**Named, not numbered** — `docs/writing_conventions.md`: *"Name things; don't index
them."* A step called "stage 4" asks the reader to hold a private taxonomy in their head
and carries no meaning on its own; **confirm the events** tells them what it is. Refer to
them below by these names.

**Import the folder** — `bugarach check <folder>`
: Expect conforming, and the header telling you loudly if treatment timing or analysis
  windows are missing. This folder has both, so the header should be **silent**; a false
  alarm here is a bug.

**Declare the periods** — `bugarach windows <folder>`
: What each recording says about its periods. Try `--create` on a **copy** with
  `regions.csv` removed and confirm the scaffold refuses to be shipped: *import the
  folder* must fail on the placeholder label until it is a real treatment name.

**Assess coordination** — `bugarach assess <folder> --k-percent 5,10,15,20,25`
: The scan in the space K is set in, with no detector involved. Check that the resolved
  count varies with the field size and the percentage does not.

**Confirm the events, and set K** — MAHICE, in the browser
: `docs/site/raster_viewer.html` — open the folder, assess, *Confirm the events*, judge a
  sample, **set K as a percentage**, download `annotations.csv` and `mahice.json`.
  **This is the step the job is for, and the one that has never touched real data** — it
  has only ever been driven on simulated recordings.

**Derive the spec** — `derive_spec --annotations annotations.csv --session mahice.json`
: The spec should carry `k_source: "mahice"`, the percentage, and the cross-check.
  ⚠ *Assess coordination* must have been run at a scan containing the K the percentage
  resolves to, or this refuses and tells you to re-assess at that percentage.

**Simulate and compare**
: Simulate from the spec, then put its statistics beside the real folder's. Both exist;
  neither has been driven from a `mahice.json`.

**Detect on the real folder** — `bugarach detect <folder>`
: Writes `detections.csv`, `detector_settings.csv`, `run.json`.

### What is already verified, so you do not redo it

- `check` / `assess` / `detect` on all 84 recordings of this folder — 84/84 conforming,
  32,078 detections in 41 s, 238 windows recorded, nothing skipped.
- The *import the folder* header: correct on a folder missing periods, **silent** on
  this one.
- `assess --k-percent` on three of its recordings: 20% is K=7 on the 34-ROI recording and
  K=6 on the 31-ROI one, from one setting.
- MAHICE in the browser, driven by clicking, **on simulated data**: 91 candidates → judge
  → Set K → `mahice.json` → round-tripped through the Python's own `read_session`.

### What is NOT verified, and is the point of the walk

- **Any of it as a sequence.** Nothing has carried a real `mahice.json` into
  `derive_spec` and out the other side.
- **The browser against the real folder** — *confirm the events, and set K*.
- **The spec → simulate → compare arc** from a person's K rather than a fixture's.

---

## Known gaps, carried forward

**The browser proposes candidates at K≥3**, so its own labels can never validate a
smaller K — the cross-check says so honestly rather than returning the floor as an
answer. Closing it means the assessment scan reaching down to 2 on both sides at once:
`tests/test_webapp_assessment_parity.py` asserts `sorted(js) == sorted(py)`, so the
browser's scan is pinned to Python's exactly. `assess.PROPOSAL_MIN_ROIS` and
`bugarach assess --for-annotation` are the Python half and already exist.

**Nobody has set a K for the approved folder** — which is the job above, not a gap
beside it. It is expert attention rather than compute: a couple of hundred confirmations
at a low proposal floor, an afternoon. ⚠ **Do not set it for him.** The whole design is
that a person looks at their own recordings and decides; a K a session picked and wrote
into the file would pass every test in this repo and be exactly the thing the record was
built to prevent.

**Two regions are still never compared.** No function in `src/` puts two side by side, so
the loop ends one analysis short of the question it opens with —
[`the question nothing computes`](docs/todo/2026-08-23-the-treatment-contrast-is-the-question-nothing-computes.md).

**No tool here runs a campaign.** The walk over detector × regime is still
`optimize_detectors.m` in interface2.

**The `analysis_*` columns reject `NA`**, which is the contract's own spelling of
missing — [filed](docs/todo/2026-09-03-analysis-bounds-reject-the-contracts-own-na.md),
found on a fixture so nothing has been mis-analysed.

---

## Traps that cost time on 2026-09-03

- **A worktree imports the primary checkout's `src`.** `PYTHONPATH=$PWD/src` on every
  run, and confirm it took. Filed three times, still open.
- **`docs/site/raster_viewer.html` is ASSEMBLED**, from `viewer.template.html` plus
  `docs/site/detectors/*.js`. Hand-edit the page and the next build discards it;
  `python3 tools/assemble_viewer.py --check` is what catches you. Its version stamp must
  move **in the same commit** as the page.
- **`merge_when_green.sh` reaps the worktree when the PR merges.** Do not claim and build
  in the same worktree.
- **`tools/show.py --project bugarach`** is how a figure reaches Tony —
  `SendUserFile` returns success and delivers nothing in the VS Code extension. It
  crashes on a file already in the darkroom
  ([#468](https://github.com/syncytium2/bugarach/pull/468)); pass the `--also` repo copy.
- **`.claude/settings.json` carries `skip-worktree`**, so `git add -A` skips your edit
  silently.

## Still waiting on Tony

Unchanged, all in [`docs/MILESTONES.md`](docs/MILESTONES.md): the `rate` promiscuity
ceiling, which K for the Cossart folder, run-record naming, and what happens to
`bench-background-is-not-flat` — the last is upstream of the ceiling decision and is the
only genuinely unlanded branch in the tree.
