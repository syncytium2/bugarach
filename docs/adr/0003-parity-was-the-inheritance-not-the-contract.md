# ADR-0003: Parity was the inheritance, not a standing contract

## Status

Accepted, 2026-08-25, by Tony. **Amends [`FOUNDATIONS.md`](../FOUNDATIONS.md) §2,
which is titled "Parity is the product" and is canonical.** Nothing here edits
FOUNDATIONS; §2 is named as the section this would change and folding it in is
Tony's call, not a session's — the same rule [`RESET.md`](../RESET.md) follows.

Until that happens, **§2 as written wins on the letter and this ADR wins on the
intent**, and a session that finds the two in conflict should say so rather than
pick. Eighteen places in the tree repeat "parity is the product"; they are not
swept by this ADR, and each is true about the past.

## Context

Tony, 2026-08-25:

> *"It is unlikely constellation will work further on this project. bugarach is
> the inheritor of their efforts and we matched their output when it was crucial.
> We are moving on and I cannot maintain two repos for this aspect of the project.
> We should no longer be concerned about matching their output and updating their
> code to match our progress."*

**What §2 was for.** Six detectors and the coactivity assessment were ported from
interface2's MATLAB and held to 1e-9 on committed fixtures, *"in every mode — that
is what makes the ports citable in place of the originals."* That was the whole
job at the time: a lab could stop needing MATLAB without anybody having to
re-argue whether the Python computed the same thing. It worked, and the receipts
are in `tests/` and regenerable through `tools/matlab_ref/`.

**The lineage, in Tony's words rather than mine** (2026-08-25, clarifying the
above — the first draft of this ADR read the decision as a counterparty
disappearing, and that is not what it is):

> *"The constellation team gave birth to bugarach. bugarach serves two purposes,
> coordination detection for our lab work and a portfolio piece to illustrate my
> approach to a deep learning project. Parity with constellation suite is a lot of
> work and not relevant to our immediate goals. At some point in the future, it
> might be interesting to move back to MATLAB. But that is not a concern at this
> time."*

**So this is a cost-and-priority call, not a divorce, and not permanent.** Parity
is a two-repo property and it costs something to hold: every mechanism change has
to land behind a flag defaulting to the MATLAB's behaviour
([`forks.md`](../forks.md) §1), and correcting a defect found here means either not
correcting it or maintaining the divergence in two places. That price bought
comparability with an active campaign. It is a lot of work, and it is not what
either of bugarach's two purposes needs right now.

**Both purposes are worth naming, because they pull differently on this.**
Coordination detection for the lab wants the *right* answer, which is what parity
was preventing. The portfolio piece (FOUNDATIONS §8) wants the **credential** —
*"six MATLAB detectors and the coactivity assessment ported and matched to 1e-9 on
committed fixtures"* is a strong, checkable claim about how this author works, and
it survives untouched. The two purposes agree on the outcome for opposite reasons,
which is why the tests stay while the constraint lifts.

**Returning to MATLAB is explicitly left open.** That is not a courtesy line; it
decides something below. If a move back is ever interesting, what makes it
tractable is a **list of exactly where the two diverged** — which is why
consequence 3 is not optional bookkeeping but the bridge back.

**What forced the question.** The null test (2026-08-24) found the coactivity
excess is mostly a selection artifact — at the busy background 96% of it survives
replacing the data with a draw from its own null. The remedy is known, cheap, and
reuses the ensemble already computed. Every argument against taking it was an
argument about parity, and
[`the fork decision figure`](../learned/assess_fork_decision.png) put that cost in
a column. This ADR is Tony reading that column and saying the cost is not worth
paying for a goal that is not current.

**What forced the question.** The null test (2026-08-24) found the coactivity
excess is mostly a selection artifact — at the busy background 96% of it survives
replacing the data with a draw from its own null. The remedy is known, cheap, and
reuses the ensemble already computed. Every argument against taking it was an
argument about parity, and
[`the fork decision figure`](../learned/assess_fork_decision.png) put that cost in
a column. This ADR is Tony reading that column and saying the cost is no longer
worth paying.

## Decision

**Parity with interface2's MATLAB is a historical guarantee about the point of
inheritance. It is not a constraint on what bugarach may compute next, and holding
it is not current work.**

**Deferred, not abandoned.** A move back to MATLAB is explicitly on the table for
some later time. Nothing here forecloses it, and consequence 3 is what keeps it
affordable.

Three consequences, and the second and third are what make this reversible.

1. **A correction no longer needs permission from the MATLAB.** Where bugarach
   finds a defect, it may fix it. The question becomes *"is this right"* rather
   than *"does this match"*.
2. **The parity tests stay, and they keep running.** They are not the contract any
   more; they are the **provenance record**, and deleting them would throw away
   the evidence for a claim this project should keep making — that the port was
   faithful when it was handed over. They are also plain regression tests for
   everything nobody has deliberately changed.
3. **Divergence is enumerated, never ambient — and this is the route back.** When
   a fork is taken, the parity test for that quantity gets an explicit, named
   exemption pointing at the `forks.md` entry that authorised it. Two reasons, and
   the second is the one that makes it non-negotiable:
   - A parity test that starts failing because somebody edited arithmetic *without
     deciding to* is still a bug, and must still look like one. "We don't do
     parity any more" must not become "a failing parity test is nothing to worry
     about."
   - **If returning to MATLAB is ever interesting, the enumeration is the map.**
     A short list of named, argued divergences is a tractable afternoon. Ambient
     drift discovered later is an audit of every line of six detectors, and it is
     the difference between a door and a wall.

**bugarach does not update interface2's code to match, for now.** One repo for
this aspect, at this time.

## What this does not decide

- **Whether `forks.md` §1 still requires flags defaulting to old behaviour.** Its
  stated reason was parity, so *that* reason is gone. **Open — Tony's call**, with
  one argument he has already supplied against dropping it: leaving a return to
  MATLAB open means every flag is a divergence that is still switchable rather
  than one that has to be reconstructed. The counter-argument is that the
  enumeration in consequence 3 already records the divergence, and a flag is a
  second, costlier way of recording the same thing — every knob defaulting to
  behaviour nobody uses is a knob somebody has to keep working.
- **Whether the six detectors' arithmetic should now change.** Nothing here says a
  detector is wrong. The revision plan and
  [`the four variants of the tube`](../todo/2026-08-23-four-variants-of-the-tube.md)
  are unaffected and still want evidence per change.
- **What happens to numbers already published from the MATLAB.**
  `darkroom/constellation/` holds a campaign computed with the old arithmetic.
  Nothing in this repo overwrites it, and a comparison against it after a fork is
  a comparison of two measurements — which is now something to state, not
  something to prevent.
- **Whether interface2 is told.** It costs a message and it is not a session's to
  send.

## What may still be said, and what may not

**May be said**, and should be, because it is the credential: *six MATLAB
detectors and the coactivity assessment were ported and matched to 1e-9 on
committed fixtures.* True, evidenced, and unaffected by anything after it.

**May not be said** once a fork lands: *"bugarach computes the same thing as the
MATLAB."* It will compute something deliberately different in named places, and
those places are `forks.md`.

## Consequences for what is open right now

**Decision 1** — fork the assessor's excess or caveat it — was blocked on exactly
this. Its cost column read: parity breaks, bugarach and constellation go onto
different definitions of one word, everything derived needs regenerating. The
first two are now spent; the third is real and RESET §5 already requires that
regeneration for other reasons.

**The K decision** (RESET §7 item 3) is downstream of decision 1 and stays blocked
on it, not on this.
