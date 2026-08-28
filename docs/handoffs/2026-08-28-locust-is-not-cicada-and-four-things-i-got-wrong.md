# Locust is not CICADA, and four things this session got wrong on the way there

**Written straight into this directory** — nothing here is half-done, so it was never a
root signal. `HANDOFF.md` at the root belongs to the 2026-08-27 session and is still
honest: its five PRs (#304, #292, #270, #53, #50) are all open. **Do not replace it.**

Everything below is merged on `main` except **PR #364** (deploy notes 2), which was green
and merging when this was written.

---

## The finding, if you read one thing

**Locust is a modified port of a port, validated only at its last link, and the public page
said it *is* CICADA's method.**

```
Cossart CICADA  ──── never validated ────▶  interface2 generate_sce_cicada  ──1e-9──▶  locust
   (their code, MIT, 2019)                   (PARKED in f55643bf for
    "faithful" is an assertion                over-detecting on our
     in both repos, tested nowhere)           long SLOW transients)
```

`tools/matlab_ref/gen_ref_cicada.m` builds the parity fixture by running **interface2's
own `generate_sce_cicada`**, so the 1e-9 result validates bugarach against interface2 and
says nothing about CICADA. Both repos assert "faithful port"; neither contains any
comparison against the Cossart source (grepped both).

It is also a **documented partial port** — `generate_sce_cicada.m`: *"we already have
events, so their per-cell transient-detection step is skipped."*

**Established this session, so nobody re-derives it:**

- **It was ported from their CODE, not the paper.** `sce_stats_utils.py` exists at the
  cited path in `gitlab.com/cossartlab/cicada` and defines both named functions —
  `get_sce_threshold(rasterdur, …)` and `detect_sce(traces, raster, …)`. The first
  parameter, `rasterdur`, independently confirms the duration model the port replaces.
- **The citation is correct.** Zenodo `10.5281/zenodo.10041434` = CICADA v1.0.3, five named
  authors, 20 July 2020, CC-BY-4.0. Checked deliberately because the lit shelf holds
  `denis_2020_deepcinac.pdf` — a different tool, same five authors, same year. No conflation.
- **The lit shelf has no CICADA paper.** Only DeepCINAC. Every claim about what CICADA does
  is sourced from its code and interface2's notes. Fetching Dard et al. (STAR Protocols)
  would close this.
- **The duration diagnosis has been written down since July.** interface2's
  `docs/coordination_detectors_methods.md` §3, "Provenance (important)", names two changes
  *"beyond tuning"* and says the original *"over-detects catastrophically on our long SLOW
  transients (median ~4.6 s of duration-overlap swamps onset-synchrony)."*

`#360` fixed the front page. **Two other sessions found more instances within the hour** —
#363 (a handoff) and #365 (the bake-off page) — so assume there are surfaces still saying it.

## ⚠ The live page is still wrong, and that is a decision waiting

`bugarach.tonydefazio.com` **right now** says *"The lane marked locust **is** CICADA's
method"* and, four sentences later, *"No method from the literature has yet been run on
this project's recordings."* Both bold; they cannot both hold. Verified by fetching the
page, not from git.

`ed5e02e` fixes it and is **queued behind the deploy hold**. `DEPLOY_HOLD.md`'s own text
says an actively misleading page is a reason to lift deliberately rather than route around.
**Raised in [deploy notes 2](2026-08-28-deploy-notes-2.md), not acted on.** Tony's call.
⚠ That note is **PR #364**, still open when this was written — if the link 404s it has not
landed, and the decision above is then recorded only here.

## What I got wrong, because the pattern matters more than the fixes

Four corrections in one session, all the same shape — **a claim that was true of one
context asserted about another**:

1. **Filed a todo saying `cicada_detect` anchors on "the wrong landmark" and proposed a
   bench run at `onset_field="peak"`.** Wrong, and acting on it would have moved the
   detector onto the peak — the direction the project deliberately came *from*. Retracted
   the same day in #354. The truth is **fields vs values**: `locs` is a legacy `findpeaks`
   name holding the peak time in the store and `t50rise` in the coordination data. Tony:
   *"pretty quickly we put t50rise into the coordination data field locs. hence the crisis."*
2. **Compared their active-stamp duration against our full transient** and reported a
   hundredfold gap that did not exist. The rise-interval substitution had already closed it.
3. **Called the Cossart raster "the authors' own inference (CICADA / DeepCINAC)"** — a guess
   about a third party's pipeline. Corrected to say only that it arrived binarised.
4. **Reported test counts from the wrong source tree** (see the hazard below).

**The one real defect that survived all that**: `rise_durations()` computes `locs -
t50rise`, which is the rise interval on a store and **identically zero on a folder**.
Verified: 2215 events, min 0.0, max 0.0. Latent, not live —
`OPERATING_POINTS["cicada"]` uses fixed `active_duration_sec=1.0`. Filed as
[`…locs-is-a-field-name-and-rise-durations-is-zero.md`](../todo/2026-08-28-locs-is-a-field-name-and-rise-durations-is-zero.md).

## ⚠ Hazard that will bite the next session

**A worktree's `pytest` imports the PRIMARY checkout's `src`.** One editable install in
`.venv`, and the two are rarely at the same commit.

```bash
PYTHONPATH="$PWD/src" .venv/bin/python -m pytest tests/ -q    # correct
.venv/bin/python -m pytest tests/ -q                          # tests another branch's code
```

It already corrupted two reported numbers: *"1454 passed, 16 skipped"* went into two PR
messages measured against the primary tree; the true figure was **1498 passed, 3 skipped,
1 xfailed**. **It fails toward green** — a worktree editing `src/` can pass a suite that
never ran its change. Filed with three ranked fixes at
[`…a-worktree-pytest-run-tests-the-primary-checkouts-src.md`](../todo/2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md);
**Tony asked for the fix proposal next and it is not started.**

Second, smaller: **`merge_when_green` correctly refuses a PR with no checks reported**, and
GitHub sometimes creates no workflow run for a push. Re-push; it appears. Not a path
filter — there is none.

## bugarach now reads another lab

`tools/import_dandi.py` (#353) turns the Cossart lab's DANDI:000219 into an export folder:
**59 recordings, 935,965 events, 1,303 zero-event ROIs kept as `NA` rows.** `bugarach
check` passes on all 59, `assess` runs end to end, and `build_viewer` holds their corpus
beside ours.

Written to **`<data>/exports/external/dandi_000219/`** — deliberately *not*
`exports/bugarach/`, which `dataset.resolve()` searches for bare names. **Pass it by path;
it is not in `current_export.toml`.**

Their data is binarised, so `time_sec` is a rising edge, not a `t50rise`, and there is no
`peak_sec` or `amp`. `PROVENANCE.md` in the folder states the cost: rates, counts and
rankings are safe; cross-lab coincidence-within-tolerance is not available from these files.

**This was the first time the project read a recording it did not produce**, which is what
made the contract's "any producer" claim testable at all.

## Data rules Tony gave this session — follow these, do not re-derive

> *"Stop — don't read the .mat event store. The export folder is the input."*

```python
from bugarach import dataset
folder = dataset.current()          # 2026-08-18_revised_2v_periods, 84 recordings
folder = dataset.current('pensub')  # 2026-08-20_pensub_revised_2v, the same 84
```

- **Width is already in the data.** `fast width_sec = halfprom_width_findpeaks_w` (real
  transient width, median 0.90 s); `slow width_sec = rise_interval_peak_minus_t50rise`
  (= `peak_sec - time_sec`, median 2.00 s, max 5.5 s). **Read `width_def`, never the column
  name.**
- **Fast only, for now.** Tony: *"fast is closer to classical calcium events… stick with
  fast."* There is **no declared default stream in code** — whether there should be is
  question 2 below.
- **Ask when there are options; do not analyse all of them.** And *"if you cannot find the
  specific data associated with this project, FULL STOP."* Both are standing instructions,
  earned the hard way — the case report is in `syncytium2/short-course`.

## Open decisions, all Tony's

1. **Lift the hold for `ed5e02e`?** The live page is misattributing a result to another lab.
2. **Should "fast" become a declared default stream?** FOUNDATIONS §3 declines to privilege
   one *on purpose* (streams are generic; most labs have one), so declaring a default
   contradicts a deliberate design decision. Filed nowhere — it is in the `SESSIONS.md`
   block and here.
3. **The `conftest.py` + guard-test fix** for the worktree hazard. Tony: *"then we can
   continue with your fix proposal."* Not started.
4. **`syncytium2/short-course` audience call** — the case report recommends itself for the
   beginner course and competes with the sibling case for one slot.

## Filed this session, all open

| file | what it is |
|---|---|
| [`docs/todo/…locs-is-a-field-name…`](../todo/2026-08-28-locs-is-a-field-name-and-rise-durations-is-zero.md) | `rise_durations()` is zero on folder input; latent, not live |
| [`docs/todo/…worktree-pytest…`](../todo/2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md) | the hazard above, three ranked fixes |
| [`docs/sapper_feedback/…sap007…`](../sapper_feedback/2026-08-28-sap007-cannot-tell-an-importer-from-an-analysis.md) | SAP007 cannot tell an importer from an analysis; also, its exclusion list is now half backlog and half permanent, so its length measures nothing |

## Provenance

Written 2026-08-28 by the session that made #353, #354, #360 and #364, at Tony's request
when nearing compaction. Landed also: `syncytium2/short-course` `42e981c`, a case report on
this session's own data-fabrication failure. Every number here was re-derived at writing
time; the live-page quotes were fetched over HTTP. **Review scope: a single-pass claim
check (role 1) against git, the files and the live page — not an eleven-role murderboard**,
stated because a handoff claiming more review than it had is the defect this repo files
incidents about.
