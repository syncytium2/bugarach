---
status: open
filed: 2026-08-21
---

# "Port of interface2's X" reads as someone else's algorithm, and undersells five of six detectors

Found by making the mistake. On 2026-08-21 a session read the detector
docstrings, concluded that four of the six detectors came from outside this
project, and was about to put that into app copy. Tony corrected it:

> *"the only detector that is ported is cicada. we use cSPIKE/pySpike to create a
> synchrony series that we run a detection algorithm on. RateDetect was written
> by me/us … SCE was derived from ideas in cicada, but it is essentially ours.
> Loco and coactDetect were the result of you and me brainstorming to solve this
> problem."*

## Why a careful reader gets it wrong

Every detector module opens the same way:

    rate.py    """rate+context coordination detector — port of interface2's `RateDetect` …
    sce.py     """Binned SCE — port of interface2's `generate_sce` …
    loco.py    """LoCo (Local Coincidence) — port of interface2's `detect_loco`.
    coact.py   """CoactDetect — port of interface2's `detect_local_coincidence` …
    sync.py    """SPIKE-synchronization detector — port of interface2's sync stack …
    cicada.py  """CICADA sliding-window SCE detector — port of interface2's
               `generate_sce_cicada`, itself a faithful port of the Cossart lab's CICADA …

**`port` is doing two entirely different jobs in that list.**

- For five of them it means *the Python translation of our own MATLAB* —
  interface2 is this project's own codebase. It is a statement about a
  **language boundary**, and it is load-bearing: the parity tests exist because
  of it.
- For CICADA it means *a reimplementation of a published method by another lab*.
  That one carries an MIT notice and a citation requirement.

Only `cicada.py` marks the difference, and it does so **one clause in**, after
the same opening words as the other five. `sync.py` is a third case again: the
Kreuz-lab synchrony profile is external, and the detector run on top of it —
hysteresis plus artifact flagging — is ours, which the first line does not
separate.

## Why it is worth fixing rather than knowing

**The README already gets this right.** Its licensing table says *"SPIKE-synchronization
**semantics** ported from its (BSD) source"* for PySpike and *"CICADA **detection
method** (ported)"* for CICADA — precise, and correct. So the repo contradicts
itself: the table says five of six are ours, the module headers imply the
opposite, and the module headers are what a reader lands in.

**And this repo is a portfolio artifact** (FOUNDATIONS §8) whose commit messages
and process docs are explicitly a presentation surface. A reviewer skimming
`src/bugarach/detectors/` concludes the author ported six detectors. The truth is
that they authored five and ported one — including the two that **lead the
comparison** in `bakeoff.md`. This is the rare defect that costs by
**understating**, which is why none of the existing guards catch it: every rule
in the tree is written against overclaiming.

## The fix

One line per module, distinguishing the language boundary from the method's
origin. Something in the shape of:

    rate.py    """rate+context coordination detector. Ours; Python port of
               interface2's own `RateDetect` (parity-tested against it).
    cicada.py  """CICADA sliding-window SCE detector. Method: Cossart lab
               (MIT, cited); Python port via interface2's `generate_sce_cicada`.
    sync.py    """SPIKE-synchronization detector. Synchrony profile: Kreuz lab
               (PySpike semantics, BSD). Detector on that series: ours.

Nothing about the code changes. The parity claims stay exactly as they are — they
are about the MATLAB↔Python boundary and are unaffected.

## Do not overcorrect

The temptation, having found an understatement, is to swing the other way. The
scoreboard's copy rules stand and are not softened by this: the comparison
contains **no published learned method**, `bakeoff.md` has the tube in a **tie**
with CoactDetect rather than ahead of it, and every number measured so far is on
simulated data. Authorship of the six is a separate question from how well they
do, and saying more about the first does not license saying more about the second.
