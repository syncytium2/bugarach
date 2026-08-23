---
status: done
filed: 2026-08-16
closed: 2026-08-23
---

# The frame interval does not travel with the recording, so gating the loader only covers half the paths

**CLOSED 2026-08-23.** It travels now: `Slice.dt`, a typed field with no
default, set by every producer of a recording — the simulator included, which
passes its own `grid_sec`, so `bench.py`'s hand-maintained coupling is no longer
the only thing holding the generator and the detectors on one grid. "The
direction, not yet a recommendation" below is what got built, and the naming
complaint it opens with was the sharpest observation in it: the rule really was
scoped by one detector's parameter name, and the two silent defaults really were
the cost. Both are gone.

One of the three turned out not to be this quantity at all. SPIKE-synch's `dt`
is the bin width its hysteresis thresholds were calibrated at, not an
acquisition interval, and it keeps its default on purpose. The full record — the
loader contract, why a conforming folder with no sidecar is not refused, and the
SPIKE-synch argument — is in
[`2026-08-16-dt-must-be-required-at-load.md`](2026-08-16-dt-must-be-required-at-load.md),
"How it closed".

The upstream fix this file argues for at the end — the stores carrying their own
interval — **is still worth having and is still interface2's to make.** What
changed is that it is an improvement rather than a prerequisite: a store that
declared its interval would let `load_slice` read it instead of being told, and
would spare this lab typing a number it already knows. Everything downstream is
built to receive it.

## The finding

`Slice` has four fields — `slice_id`, `streams`, `regions`, `roi_ids` — and none of
them is the acquisition interval. So the interval is not a property of a recording;
it is an argument passed separately to whichever detector needs it, by whoever
happens to be calling.

**There are two producers of recordings and only one of them is a loader.**

| producer | gated by a load-boundary check? |
|---|---|
| the store / CSV loaders | yes — that is what the required-interval rule covers |
| `simulate.simulate_coordination` | **no** — `bench.make_recording` calls it directly and hands the result straight to the detectors |

So every synthetic recording reaches the detectors with their interval defaults
intact, no matter what the loader refuses.

## Verified, 2026-08-16

- `grep -rn "grid_sec" src/bugarach/bench.py src/bugarach/detectors/` returns
  **nothing**. The generator's own imaging grid never reaches a detector.
- `bench.OPERATING_POINTS["rate"]` sets `grid_dt=0.1` with the source string
  *"grid_dt is the generator's own 0.1 s grid"* — so the coupling is known and
  **hand-maintained, for the one detector that already warns**. The two silent ones
  were never wired.
- Three detectors assume an interval; one complains when it is missing:

  | detector | parameter | default | warns |
  |---|---|---|---|
  | `rate_detect` | `grid_dt` | `None` | **yes** |
  | `sync_detect` | `dt` | `0.1` | no |
  | `cicada_detect` | `imaging_rate_hz` | `10.0` → `dt = 0.1` | no |

  Every reference to the warning class in the tree sits inside `rate.py`, although
  the class is exported from `detectors/__init__.py` as if it were a package-level
  concept.
- The three agree on 0.1 s **by coincidence, not by construction** — and
  `docs/generator.md` carries a figure that sweeps the generator's grid. At any
  non-default value the data sits on one grid while two detectors assume another,
  and nothing anywhere says so. A bench sweep over that knob would produce quietly
  wrong scores for two detectors while the third stayed correct.

## Why the naming hid it

FOUNDATIONS §6 is titled *"grid_dt is the caller's responsibility"* and states its
rule in terms of `grid_dt` — which is one detector's parameter name. The
**principle** governs all three. The other two sit outside canonical truth purely
because they spell the same physical quantity differently. The rule is correct and
its scope is an accident of naming.

## The direction, not yet a recommendation

**Make the interval a property of the recording rather than an argument to three
detectors.** Then both producers are covered, the hand-maintained coupling in
`bench.py` dies, and the two silent defaults become unreachable rather than
better-warned. The generator already knows its own grid and would supply it for
free; the case the rule exists for is foreign data, which carries no interval
anywhere.

Cost not yet paid: it touches the fixture chain, and FOUNDATIONS §2 makes 1e-9
parity the product. It changes where the number comes from and must not change what
any detector computes from it, so every fixture must still match afterwards.

**Out of scope, deliberately.** Making the detectors take samples rather than
seconds is a different and much larger proposal. Parameters are physical claims — a
one-second coincidence window is about neurophysiology, ten frames is about the
camera — and putting them in samples makes every calibrated operating point
rig-dependent. Internals may live on the sample grid; parameters should not. The
interval is what makes the two interconvertible, which is the argument for requiring
it rather than defaulting it.

## One upstream fix would beat every option above, for the lab's own data

The direction above makes the interval a property of the recording *inside
bugarach*. For **foreign** data that is the whole answer — it carries no interval
anywhere, so somebody has to state it. But for this lab's own recordings there is
a better place to fix it than anywhere downstream.

FOUNDATIONS §6 records that the onset stores **do not carry** the frame interval,
and that this is filed in interface2's todo map. If they did, the number would
arrive with the data: no default to warn about, no argument to thread, nothing to
refuse at a door, and no coupling for `bench.py` to hand-maintain. Both producers
close at once, because the generator already knows its own grid and the store
would know its own.

That is interface2's to decide, not bugarach's, and an interface2 session has been
reading that tree. **Worth asking before building either option above** — the
cheaper fix may already be someone else's one-line schema change, and the
downstream work is only unavoidable for data that comes from outside the lab.

## Provenance

Found by cross-session conversation on 2026-08-16 between the workflow-plan session
(PR #45), the dt session (PR #48), and the generator-doc session; each claim above
re-verified against `origin/main` by more than one session. **Written down because
none of that conversation is durable** — FOUNDATIONS §8: anything not pushed does
not exist to the next session or the next machine.

Related: [`docs/export_folder_spec.md`](../export_folder_spec.md) makes the interval
a required field refused at the door, which covers the loader half.

**Read with [`2026-08-16-dt-must-be-required-at-load.md`](2026-08-16-dt-must-be-required-at-load.md).**
Filed the same day by a different session, and neither knew about the other. That one
carries the rule and the file/line inventory of the fallback to remove; this one carries
why there is nowhere to put the answer. FOUNDATIONS §6 now states the rule — that
landed 2026-08-18, three days after it was written.
