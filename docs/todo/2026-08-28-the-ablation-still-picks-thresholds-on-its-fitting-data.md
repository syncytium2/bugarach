---
status: open
filed: 2026-08-28
---

# `tools/ablate_tube.py` still picks its thresholds on the recordings it fitted

> **Found from outside this repo.** A case study in `syncytium2/short-course` was
> being written about #347 and the `fold_maker` fix, and its verification appendix ran
> the greps rather than trusting the commit message. `2bc3160` names **two** call sites
> for the leaky maker. There were **three**.

> **Not murderboarded** — a code reading and two JSON reads, not a document. Every claim
> below is one `git grep` or one `python -c` away and the commands are given.

## What was found

`2bc3160` fixed a maker of the shape `lambda seed: recs[seed % len(recs)]`, which maps
`train`'s seed block and `pick_threshold`'s seed block onto **one set of recordings** —
so the operating point was chosen on the data the model had just been fitted to, while
the assertion in `pick_threshold` kept passing because it compares *seeds*, not
*recordings*.

Its commit message says the maker was there *"in `fair_bakeoff.py` and in `lab.py`
identically."* On the pre-fix tree there were three:

```
$ git grep -n 'seed % len' 2bc3160^ -- '*.py'
src/bugarach/lab.py:390
tools/ablate_tube.py:82
tools/fair_bakeoff.py:180
```

Two were converted. On `main` today:

```
$ git grep -n 'seed % len' HEAD -- '*.py'          # ...tools/ablate_tube.py:82
$ git grep -ln 'fold_maker' HEAD -- '*.py'         # ...ablate_tube.py absent
```

`tools/ablate_tube.py:82` still reads

```python
mk = lambda seed, _t=tuple(tr_seeds): rec(_t[seed % len(_t)])  # noqa: E731
```

**It is not a dead line.** `train()` always calls `pick_threshold()` (`train.py:212`),
which draws `VAL_SEED_BLOCK + seed*1000 + i`. Under that maker every one of those seeds
comes back modulo onto the training recordings. The ablation leaks exactly the way
`fair_bakeoff` did, in the same file that imports `fair_bakeoff`'s helpers *"rather than
reimplementing them"* so the two halves of a comparison cannot end up on different
metrics.

## The half that is worse than a missed call site

`src/bugarach/learn/train.py:35`, in the docstring of `VAL_SEED_BLOCK` — the module's own
statement of the guarantee:

> *"That only separates recordings if the `make_recording` a caller supplies honours the
> boundary, and **until 2026-08-28 no caller did**."*

Past tense, repo-wide. One caller still does not. The fix's own documentation asserts a
state that was never reached, in the paragraph explaining why the fix exists — which is
the same defect class as `the-docstring-overclaims`, one file over.

## What this does and does not mean

**The report's conclusion is not retracted, and should not be.**
`docs/learned/coordination_report.src.html` compares the one-scale bank against the
four-scale bank — `s1_c40` **0.670** against `s4_c40` **0.668** — and concludes the bank
does not earn its parameters. **Both arms leak identically.** The leak is common-mode
across the comparison the page actually makes, so *"one scale scores the same as four"*
survives. Say this out loud when fixing it, or someone will withdraw a finding that holds.

**What broke is the comparability the tool claims about itself.** `ablate_tube.py`'s
module docstring:

> *"Both run through **the same fold procedure as the bake-off** … so the numbers are
> comparable with `bakeoff.json` rather than to each other only."*

That is now false in **three independent ways**, none of them the ablation's fault — the
bake-off moved underneath it on 2026-08-28 and nothing pointed here:

| | `tube_ablation.json` (2026-08-17) | `bakeoff.json` (2026-08-28) |
|---|---|---|
| fold procedure | `seed % len` — threshold picked on fitting recordings | `fold_maker` — training folds split again |
| threshold grid | hard floor at 0.05, dense tail toward 1 | open at both ends to 1e-4 |
| intra-op threads | **unrecorded** — no `machine` block in the JSON | pinned, `THREADS = 1`, `machine` recorded |

**The page's cross-reference is off by exactly the amount the fold fix moved the
bake-off.** It calls `s4_c40` *"the published four-scale"*, at **0.668**. That was the
published four-scale: `bakeoff.json`'s tube read 0.667972 until 2026-08-28. It now reads
**0.6808**. The built `docs/learned/coordination_report.html` has 0.668 baked in.

```
$ python3 -c "import json;a=json.load(open('docs/learned/tube_ablation.json'));\
b=json.load(open('docs/learned/bakeoff.json'));\
print(a['by_key']['s4_c40']['f1']['mean'], b['learned']['tube']['f1']['mean'])"
0.66795... 0.68083...
```

**And the store cannot say what produced it.** `bakeoff.json` carries a `machine` block;
`tube_ablation.json` carries none. For a tree whose clean-room machinery exists to make
results regenerable from declared state, an unrecorded thread count is the defect
[`2026-08-27-the-bakeoff-reference-is-thread-count-bound.md`](2026-08-27-the-bakeoff-reference-is-thread-count-bound.md)
was filed for, in a store nobody re-ran.

## The fix, and why a session did not take it

Two lines, and `fold_maker`'s signature was designed for them:

```python
mk, n_fit, _ = fold_maker(rec, tr_seeds)
tr = train("tube", mk, n_train=min(10, n_fit), ...)   # n_fit, not len(tr_seeds)
```

`fold_maker` returns `n_fit` precisely *"so a caller can size its own requests rather than
asking for more recordings than exist and receiving them back modulo"* — the bug being
fixed, in the accessor that fixes it. Add a `machine` block while there.

**Then `docs/learned/tube_ablation.json` has to be regenerated, and that is why this is
filed rather than done.** Regenerating changes numbers on a page written for outside
readers, and by the murderboard rule a document deliverable is not a session's to redraft
unasked. It is the same call #347 made when it left the bake-off prose alone, and the same
one `2bc3160` made when it wrote *"not touched: the prose that quotes these numbers."*

Sequencing: `the-numbers-moved` is ACTIVE on `bakeoff.md` / `bakeoff.html` /
`report.html` and explicitly not on `report.src.html`. This item is the *ablation* store
and `coordination_report.*`, which nobody holds. **They should not be merged into one
job** — that one transcribes numbers that already moved; this one moves numbers that have
not.

## Three questions that come with it

- **Does the conclusion survive regeneration?** Expected yes, because the leak is
  common-mode — but the reopened grid is exactly what turned *one* architecture with no
  operating point into
  [two](2026-08-28-two-architectures-have-no-operating-point.md). A one-kernel bank
  scored on recordings it has never seen is a candidate for the floor, and if it lands
  there the page's comparison stops being about parameters.
- **Should the page stop calling it "the published four-scale" regardless?** Even after
  regeneration the ablation is a separate run of a separate tool. Naming it *published*
  invites exactly the identification that just broke.
- **How many other call sites inherit a guarantee by reference?** This one was found
  because a case study checked a commit message against `git grep`. Nothing in the tree
  asks *"which callers of `train` do not go through `fold_maker`?"*, and that is one
  test — the same shape as `test_the_learn_suite_is_not_empty`, which #347 added for the
  same reason.
