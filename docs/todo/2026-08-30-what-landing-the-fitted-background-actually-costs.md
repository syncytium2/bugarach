---
status: done
filed: 2026-08-30
---

# What landing `bench-background-is-not-flat` actually costs — measured, not estimated

The branch has been sitting unmerged behind two stated blockers. Both were
checked against the current tree on 2026-08-30 and **one of them is wrong**.

## The blockers as handed over

> The only decision left from tonight is `bench-background-is-not-flat` — it
> merges cleanly and can't land green, for two reasons that are both yours to
> call: three tests its own author left red on purpose ("re-baselining them would
> delete a finding"), and `bakeoff.json` was computed on the flat field, so the
> published numbers go stale the moment it's wired.

## What is actually true

**It merges cleanly onto `ced0da4`.** Six tests fail, and only four are about the
branch:

- **Three `test_background_curve` tests** — real, and the finding is genuine.
- **`test_the_server_reproduces_the_published_bakeoff`** — fails at `29 == 28`.
  One extra hit on fold 3.
- **Two site-date tests** — artifacts of an *uncommitted* merge: git reads the
  change date as today while the page's stamp says yesterday. The merge does not
  touch `docs/site/` at all. They resolve on commit.

**Three of the four decisions in the original handoff were already applied** on
later commits of the same branch (`dcbbf7a`, *"Three rulings applied: the grid
widens, the tolerance moves, and rate's regime failure was the tolerance all
along"*). coact's grid edge, rate's regime swing and the tolerance plateau do not
fail any more. The handoff was written before those commits and was never updated.

## `bakeoff.json` was never computed on the flat field

`docs/learned/generator_spec.json` — what `fair_bakeoff` generates from — already
carries `bg_rate_shape: 0.275` and `bg_burst_shape: [1.547, 1.388]`. It is derived
from real recordings by `derive_spec.py` and has been non-flat all along. The
branch changes `BENCH_RECORDING` in `bench.py`, which is the *bench's own*
synthetic recording, used for calibration sweeps and `test_background_curve`. The
bake-off never touches it.

**The proof is not an argument.** The bake-off was run on both trees, same spec,
same seeds:

| detector | flat F1 | fitted F1 | Δ | probe firings |
|---|---|---|---|---|
| binned SCE | 0.420 | 0.451 | **+0.031** | 59.2 → 59.5 |
| SPIKE-synch | 0.254 | 0.267 | +0.013 | identical |
| tube_guard | 0.673 | 0.680 | +0.007 | identical |
| LoCo | 0.638 | 0.645 | +0.007 | identical |
| tube | 0.681 | 0.686 | +0.006 | identical |
| pooled trace | 0.118 | 0.110 | −0.008 | identical |
| **coact, rate, the sixth, both ratio cells, per-cell bank** | | | **0.000** | identical |

**Probe firings are identical for every detector.** If the background had changed,
the recordings and therefore the detections would differ and those counts would
move. They did not. The same recordings were scored twice.

## What moved is the tolerance, and only for the coarse detectors

`fair_bakeoff` calls `score_stream(gt, d)` with no explicit tolerance, so it
inherits the default — `1.5` on main, `TOL_SEC = 2.5` on the branch. Everything
that moved is a detector whose localization is coarse: binned SCE reports a bin's
*left edge*, so a wider window is exactly what it needs; SPIKE-synch next. The
detectors whose calls already landed inside 1.5 s did not move at all. The
`29 == 28` failure is one extra hit at the wider tolerance.

**So landing this costs a re-quote of four numbers, not a re-baseline.** The
2026-08-30 guard-screen figure survives intact — the finding there is 20.5 vs 4.8
probe firings, identical on both sides.

## What is genuinely still open

The three `test_background_curve` tests, and that session **already measured the
answer** in `docs/handoffs/2026-08-28-the-winner-stopped-changing.md`: reading (a),
the axis still discriminates (own-range 0.185 → 0.136, between-detector spread
0.117 → 0.098 — both shrank modestly, neither collapsed), and the four-place rank
change was real but lived in a crowded low-F1 tail the flat field manufactured.

What that leaves is narrower than "rewrite or not": their run found **two**
winners along the axis where the tests' own seeds found **one**, and they say
plainly that gap is inside seed noise at that count. A rewrite needs a deliberate
seed count and a stated regime — only `baseline_quiet` was swept.

## ⚠ A quote in that branch needed correcting — DONE 2026-08-30

`docs/handoffs/2026-08-28-the-winner-stopped-changing.md` opens:

> Tony, 2026-08-28, on the four decisions the background change surfaced:
> *"don't get 4."* Fair — it was handed over as a test failure. It is a result.

Tony, 2026-08-30: *"I meant I didn't understand 4 and it inferred something
else."* That is a misread question standing in a durable document as a ruling —
the defect
[`2026-08-27-an-attribution-to-a-person-in-the-room-is-not-checked.md`](2026-08-27-an-attribution-to-a-person-in-the-room-is-not-checked.md)
was filed about. The measurement that session then did is good work and stands;
only the framing of it as a granted decision is wrong.

The reply that produced it is now caught by a user-level `UserPromptSubmit` hook
(`~/.claude/hooks/ambiguous-reply-confirm.sh`, 2026-08-30) which fires on exactly
that shape in every project on this machine.

## Landed 2026-09-06

Tony, asked what happens to the branch: *land it, in two PRs*. The documents went first
(#486); the code followed with the three `test_background_curve` tests rewritten to what was
measured at twelve seeds — one winner across the axis on the fitted field, the reordering
the flat field showed lived in a tail it manufactured — and `docs/learned/bakeoff.json`
regenerated at the 2.5 s tolerance with the same spec, folds and seeds, so the lab-server
reproduction test compares like with like. The re-quote landed in `README.md` and
`docs/learned/bakeoff.md`, from the JSON, not from memory.
