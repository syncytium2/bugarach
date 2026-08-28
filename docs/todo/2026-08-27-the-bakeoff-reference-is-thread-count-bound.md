---
status: done
filed: 2026-08-27
closed: 2026-08-28
---

> **Done 2026-08-28 — and this file's diagnosis was incomplete.**
> `learn.train.THREADS` pins the count to 1, `Trained.threads` carries it, and
> `docs/learned/bakeoff.json` was regenerated under the pin. The skip this file
> authorised is gone.
>
> **Pinning threads was necessary and not sufficient, and CI said so.** The first
> run after the fix still failed, at fold 0, 69 detections against 72. The
> reference is generated on macOS arm64; the runners are Linux x86_64. Different
> CPU kernels reduce and fuse differently and 900 steps of gradient descent
> amplify that, exactly as they amplified the thread count. **The reference is
> platform-bound, not merely thread-bound** — this file measured the one variable
> it happened to vary and read it as the whole cause.
>
> What ships instead of a false claim of portability: the test asserts the
> genuinely platform-independent things **everywhere** — the fold split, the
> parameter count, the planted-event counts, all drawn through
> `numpy.random.RandomState` and bit-identical anywhere — runs the exact per-fold
> comparison only where exactness is meaningful, and elsewhere bounds the mean by
> the reference's **own** fold spread rather than by a number chosen to make it
> pass. Loosening the exact assertions until they passed on both platforms was
> never available: this file's own next section refuses it, and is right that a
> check wide enough to absorb an architecture change cannot see a regression.
>
> **Two more things were true that this file did not know**, and both moved the
> numbers more than the thread count did.
>
> **The reference was already stale.** SCE's knob grid on `main` had been extended
> downward (floor 90 -> 75) after `bakeoff.json` was generated, so the sweep could
> reach an operating point the reference never had. SCE moves 90 -> 75 on three of
> four folds for that reason alone, with or without this fix. A reference that no
> longer reflects the bench scoring it is the same defect as one that no longer
> reflects the machine running it.
>
> **The threshold was picked on the fitting recordings** — found independently by
> the learned-detector-page murderboard, fixed here as `learn.train.fold_maker`.
> That is what actually moved the learned rows: centre-surround **0.668 -> 0.681**,
> pooled trace 0.131 -> 0.118, per-cell bank unchanged at 0.125. The six are
> unchanged to four decimals apart from SCE, which is the control this file wanted:
> they never touch torch.
>
> **What it exposed.** Picking the threshold honestly pushed the optimum through
> the *bottom* of a grid that had a hard floor at 0.05 and a dense tail only
> towards 1. The grid is now open at both ends — and under it the pooled trace
> joins the per-cell bank on the floor, so **two of three architectures have no
> operating point** rather than one:
> [`2026-08-28-two-architectures-have-no-operating-point.md`](2026-08-28-two-architectures-have-no-operating-point.md).
>
> Answering this file's own two questions: the report prose *does* quote the mean
> F1, so moving it is a `/murderboard` job and was kept out of this commit. And one
> thread is not slow — the per-cell bank trains **faster** at 1 thread than the
> 236 s/fold the reference recorded at 10.

# The published bakeoff numbers only reproduce on a 10-thread machine

> **Open, not waiting-on-tony**, though it ends in a decision only Tony can take. That
> status drives the briefing's *"FINISHED and waiting on Tony — nothing else unblocks
> these"* block, and this is neither finished nor blocking: it is a filed defect with a
> proposed fix. Putting it there also pushed the briefing to 9001B against a 9000B budget
> and degraded it to TERSE in CI, which is
> [its own open item](2026-08-27-the-board-digest-is-213-bytes-from-degrading.md) and a
> fair warning that the block is not free.

> **Not murderboarded** — a measurement, not a document. Every number below is one
> `pytest` run away and the command is given.

## What was measured

While wiring torch into CI ([ADR-0004](../adr/0004-ci-installs-torch-from-the-cpu-wheel-index.md)),
`test_the_server_reproduces_the_published_bakeoff` turned out to fail on any machine
whose torch intra-op thread count is not the one that produced the reference.

`src/bugarach/learn/train.py` calls `torch.manual_seed(seed)` and pins nothing else —
no `set_num_threads`, no `use_deterministic_algorithms`, no explicit device. So torch
reads the thread count off the hardware. On the Mac that generated
`docs/learned/bakeoff.json` that is **10**. Vary it and the CPU reduction order varies,
and 900 steps of gradient descent amplify the difference:

```
threads   mean F1     delta       n_detected per fold (published -> run)
     10   0.667972   +0.000000    71->71  47->47  58->58  45->45   <-- reproduces
      1   0.685781   +0.017809    71->76  47->47  58->58  45->62
      2   0.685781   +0.017809    71->76  47->47  58->58  45->62
      4   0.685781   +0.017809    71->76  47->47  58->58  45->62
```

Reproduce with:

```
OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 pytest \
  tests/test_lab_server.py::test_the_server_reproduces_the_published_bakeoff
```

which fails at the first exact-integer assertion — `n_detected` fold 0, `assert 76 == 71`.

## What it does and does not mean

**The model is fine.** Mean F1 moves 0.667972 → 0.685781, about 2.7% relative. Folds 1
and 2 reproduce exactly. The 1-, 2- and 4-thread runs are byte-identical to each other,
so this is a reduction-order code path switching, not chaos — which is the good news,
because it means pinning threads would make the result genuinely portable.

**The published number is not reproducible from the repository alone.** It needs
hardware whose torch defaults to 10 intra-op threads. That is the defect. For a tree
whose clean-room and parity machinery exists to make results regenerable from declared
state, a headline figure that quietly depends on a core count is the same class of
problem those processes were built for.

**It is not the drift the test anticipated.** That test's docstring pre-authorised
loosening tolerance for *"a small per-fold difference on a different platform."* Fold 3
moves 45 → 62 detections. Loosening tolerance far enough to absorb that would leave a
check that could not fail, which the same docstring refuses in the next sentence.

## The likely fix, and why a session did not take it

Pin the thread count where the trainer starts — `torch.set_num_threads(1)` is the
conventional choice, since 1 is the only value available on every machine — then
regenerate `docs/learned/bakeoff.json` and re-render whatever `report.html` prints from
it.

That last step is why this is filed rather than done. Regenerating changes numbers on a
page written for outside readers, and by the murderboard rule a document deliverable is
not a session's to redraft unasked. It is also cheap to undo and cheap to verify, so it
wants ten minutes of your attention rather than a plan.

Two questions that come with it:

- **Does the report quote the mean F1 in prose?** If so the text moves with the JSON,
  and that is a `/murderboard` job, not a regeneration.
- **Is 1 thread acceptably slow?** The test takes ~24 s at 10 threads and ~27 s at 1,
  so for this workload the answer looks like yes.

## What was done instead

`test_the_server_reproduces_the_published_bakeoff` now skips when
`torch.get_num_threads()` is not the reference's 10, and the skip message says why and
points here. That converts a failure that would have looked like a broken server into a
stated precondition. It is still a skip, which ADR-0004 spent its whole length arguing
against — the difference is that this one announces its reason, and this file is the
reason it is temporary.
