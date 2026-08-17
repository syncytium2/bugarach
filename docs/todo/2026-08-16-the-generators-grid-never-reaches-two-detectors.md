---
status: open
filed: 2026-08-16
---

# The generator's grid never reaches two detectors, and a load-boundary check cannot fix it

Filed because it currently exists only in a cross-session message, and the
session that found it is ending. **Not a claim on `src/bugarach/detectors/`** —
whoever owns the `dt` work should take it.

## The acquisition interval is assumed three times and warned about once

| detector | parameter | when it is absent |
|---|---|---|
| `rate_detect` | `grid_dt` | raises `GridDtNotSetWarning` on the 0.1 s fallback |
| `sync_detect` | `dt: float = 0.1` | **silent** |
| `cicada_detect` | `imaging_rate_hz: float = 10.0` → `dt = 0.1` | **silent** |

A lab imaging at 20 Hz that supplies nothing gets one warning and two quietly
wrong answers, all three wrong in the same direction because they converge on the
same nominal grid. Found by another session, 2026-08-15; verified here.

**FOUNDATIONS §6 is correct and its scope is an accident of naming.** It says the
grid "must be the acquisition sampling interval" and that the fallback warning is
there "on purpose — do not silence it" — but it is written in terms of `grid_dt`,
which is one detector's parameter name. The other two are outside canonical truth
only because they spell the same physical quantity `dt` and `imaging_rate_hz`.

## Why PR #48's load-boundary refusal does not close it

`dt-required-at-load` moves the check from a warning at detection time to a
refusal at the load boundary — the right mechanism, because a warning fires after
the number already exists. But **there are two producers of `Slice` objects and it
gates one of them.**

`simulate.simulate_coordination` never passes through any loader:
`bench.make_recording` calls it directly and `bench.run_detector` hands the result
straight to the detectors. Every synthetic slice therefore reaches `sync_detect`
and `cicada_detect` with their defaults intact, whatever the loader refuses.

Verified 2026-08-16:

- `simulate.py:225` — `grid_sec: float = 0.1`, the generator's own imaging-grid
  quantization, recorded into `gt.params` at `:386`.
- `grep grid_sec src/bugarach/bench.py src/bugarach/detectors/` returns
  **nothing**. The generator's grid never reaches a detector.
- `sync_detect` and `cicada_detect` land on 0.1 s, agreeing with the generator
  **by coincidence, not by construction.**

The part that makes it a defect rather than a nitpick: `bench.OPERATING_POINTS`
sets rate's `grid_dt=0.1` with the source string *"grid_dt is the generator's own
0.1 s grid"*. The repo already knows this coupling exists and hand-maintains it
for exactly the one detector that already warns.

**It is reachable today.** [`generator.md`](../generator.md) carries a figure
sweeping `grid_sec` across values. At any non-default setting the generated data
sits on one grid, two detectors assume another, and nothing says so — a bench
sweep over `grid_sec` would produce quietly wrong scores for sync and cicada while
rate stayed correct.

## The question to settle

Which invariant is being enforced?

- **"No `Slice` exists without a known frame interval"** closes both producers,
  makes `dt` a property of the slice rather than an argument to three detectors,
  and kills the hand-maintained coupling in `bench.py`. Bigger, and it touches the
  parity fixture chain (FOUNDATIONS §2, 1e-9 on committed fixtures), so it needs
  MATLAB R2025b and an interface2 checkout to re-derive the oracle.
- **"No *loaded* data proceeds without a stated `dt`"** is worth having on its own,
  but the synthetic path still needs an answer and the two silent defaults do not
  become unreachable.

## Better than either, if it is available

FOUNDATIONS §6 notes the onset stores do not carry the frame interval, and that
this is filed in interface2's todo map. **If the stores could carry it, all three
fallbacks become unnecessary rather than better-warned or better-refused** — the
number arrives with the data and nobody has to be asked. That is a fix at the
source and strictly better than anything downstream of it. Worth asking an
interface2 session before building either option above.
