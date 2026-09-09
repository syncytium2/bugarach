# Handoff — MAHICE is usable, and nobody has run one yet

**In flight: [#484](https://github.com/syncytium2/bugarach/pull/484)** (turbo mode, merging
on green) and **[#466](https://github.com/syncytium2/bugarach/pull/466)** (the field-step
figure, held because it is a figure with a caption and was never murderboarded). The
predecessor to this file is
[`docs/handoffs/2026-09-04-build-the-loop.md`](docs/handoffs/2026-09-04-build-the-loop.md) —
its summary-page section and its trap list are still the best account of both and are NOT
superseded by this file.

> **Not murderboarded** — working material for sessions in this tree, same standing as
> `docs/run_records.md` and `docs/pipeline.md`. Nothing here is for an outside reader.

**No counts in this file.** Derive them: `git rev-parse --short origin/main` ·
`pytest -q` · `python3 tools/sapper.py --all` · `bash tools/board_digest.sh`.

---

## Where Tony is, and what must not be broken

**He judges out of `../bugarach-worktrees/mahice`, which is DETACHED on purpose.**
`merge_when_green.sh` reaps a worktree when its branch lands, and on 2026-09-05 that deleted
his viewer mid-session. To move it when `main` advances:

```
git -C ../bugarach-worktrees/mahice checkout --detach origin/main
```

**Do not delete and recreate it. Do not reap it.**

**His verdicts live in `localStorage`, keyed per channel** (`bugarach.mahice.review.fast`).
Checked, not assumed: Chrome treats every `file://` page as ONE origin, so a review saved at
one worktree path is readable at another — the path is not what holds it. They do **not**
survive Discard, and they do not leave the browser until `Download annotations.csv`.

---

## The thing that is still not done

**Nobody has completed a MAHICE review on the approved folder. No K is set.**

That is what `docs/pipeline.md` has been waiting on since it was written. Every session
since has been clearing obstacles in front of it rather than doing it — the obstacles were
real and there were seven of them — but the work itself is expert attention, not compute,
and it is Tony's.

---

## What was wrong, because the shape repeats

Seven defects in two days and **five were one shape**: a thing that existed, worked, and
could not be reached from where the reader was standing.

- The judging step's rail chip was `disabled` until candidates existed — and the assessment
  does not survive a reload, so after any refresh the step was permanently shut **with its
  own instructions locked inside it**.
- Nothing called `paintAnnotChip` after an assessment, so the draw button never enabled. A
  disabled button fires no event and logs nothing: *"clicked, nothing happened"* was
  literally correct.
- The verdict buttons lived in a sidebar showing one step at a time, so clicking a mark
  selected it and left nothing to answer with.
- The confirm tool rendered whichever recording the shuffle put first while the raster and
  ledger showed another — **three panels, two recordings**; a verdict there answers a
  question nobody was looking at.

**The tests were green over all of it.** Every test in `test_webapp_mahice.py` reached past
the controls and called `startAnnotation()` in JS. 2000+ tests and not one pressed a button.
The new ones assert what a person actually has — an enabled control, a click that reaches
the loop, three panels naming one recording — and each was confirmed to FAIL against the
unfixed page before being kept.

**Several defects were caught only by rendering the page and looking**: a lane label drawn
as `lick a mark`, Accept/Exclude drawn as empty white boxes, region labels piling up once
the axis could zoom, a *"Resume it — 0 verdicts"* banner offering to discard live work.
Drive the real folder through the real controls, then look at the result.

⚠ **A pre-existing raw NUL byte** sat in `drawAnnotSample`'s key separator at `8a0e491`.
Harmless to JS, invisible in editors and diffs, and it **truncates the line in `awk`** — an
`awk` edit 600 lines away took the whole page's parse down mid-session. Separators are JSON
now and the file has no control bytes; check for them before trusting a text tool on it.

---

## Decisions that are Tony's and still open

**The K floor**, raised 2026-09-04 and still unrecorded outside the machine-local board. A
floor of 2 excludes K=1; it costs the fairness the percentage existed for, at the small end
only; and **it must move on the generator side in the same change** — `assess.k_from_fraction`
is `simulate.py`'s rule too, and if the two diverge a spec derived at 10% and a simulation
planted at 10% stop describing the same events. Binds 3 of 84 recordings at 10%, 38 at 5%.

Turbo makes it visible rather than hypothetical: **at 10% with a floor of 3 the floor binds
on 13 of the 38 TTX baselines.** ⚠ **A floor set in turbo is not yet a floor in
`k_from_fraction`** — whatever he lands on still has to reach that function.

**Two scorers, two winners** and **run-record naming**: both still FINISHED and waiting on
him, in `docs/todo/`.

---

## Parked, claimed, not finished

**`guards-ask-stale-questions`** — two guards that are delivered and ask questions whose
answers stopped meaning anything:

- the session-start unpushed-work alarm asks *"is this sha on a remote?"*, but squash-merge
  guarantees a merged branch's shas never reach one. **Measured 59% false positives, 10 of
  17.** Fix: `git cherry` patch-equivalence as a confirmation after the existing cheap
  filter.
- `check_vendor_freshness.sh` asks `syncytium2/interface2`, which 404s over `gh`, so it
  prints `UNKNOWN` — reading as *not checked yet* rather than *pointed at a repo that cannot
  answer*. Under that silence the vendored hook fell a full upstream commit behind
  (interface2 `a51bef82`: the escape hatch and SAFE MODE latch).

**Hooks are AUTHORED in interface2 and only COLLECTED by armory.** Do not restamp them to
armory — the stamps are right. Armory is the routing and findings hub, and its README is
emphatic: **submit, do not merge.** A third instance of the same family is already filed in
armory's `FINDINGS.md` §9 (`# instrument:` on line 2 displaces the vendoring stamp to line 3,
where the parser does not look).

---

## Two data folders exist that did not before

`2026-09-03_revised_2v_long_STEPS_EXCLUDED_TTX` (38 recordings) and `..._SENKTIDE` (29),
split from the approved export on **first treatment slot only** — Tony's rule, recorded in
the TTX folder's own README with his words on it. **Copies, not moves**; the parent is
untouched at 84.

⚠ **Neither is declared in `current_export.toml`**, so `dataset.current()` and every
`--dataset <name>` still resolve `2026-08-18_revised_2v_periods`. If these are the study's
datasets they want entries there — not done, because it is a real decision about what
"current" means and these are derived folders rather than producer exports.

---

## Read before building

`docs/pipeline.md` is the plan. `docs/INDEX.md` when a lookup fails.
`docs/FOUNDATIONS.md` §9 wins over anything in this file.
