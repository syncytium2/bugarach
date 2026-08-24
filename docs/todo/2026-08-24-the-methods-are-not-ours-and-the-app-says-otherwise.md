---
status: open
filed: 2026-08-24
---

# None of the six methods is ours to claim, and that turns out to be fine

Two things arrived from outside this repo on 2026-08-24 and neither is a
bugarach finding. This file is what they change here.

> **Tony settled the tone of this on 2026-08-24, and it binds the rest of the
> file:** *"I don't think anyone is going to jump on us for a technique used in
> radar analysis from 1968. In fact I feel most researchers would be kind of
> thrilled with the link. We acknowledge its origins, don't worry about finding
> the lit after we built it, it's a tool and it's useful."*
>
> **So priority is closed, and it was never the interesting part.** Deriving
> cell-averaging CFAR from a calcium-imaging problem is evidence the design space
> is real, not a debt — and it is the kind of link a reader enjoys. Cite the
> origins, say plainly that we arrived independently, and stop there. **Nothing in
> this file is a reason to be anxious about credit.**
>
> **What survives the decision is engineering.** The radar literature spent fifty
> years on these detectors and its results transfer whoever published first:
> GO-CFAR masks a real target shortly after a high-rate stretch, and an additive
> threshold does not hold a false-alarm rate as the background moves. Those are
> testable predictions about `loco_detect` and `rate_detect` on wash-in data,
> arriving free. Read §3 and §4 below as findings about the instrument, which is
> what they are — not as an attribution problem.
>
> **One item is not covered by this decision and must not be filed under it:** the
> **CICADA label**. That is not "we built it and later found the literature" — we
> knowingly ported a living lab's named tool, changed two things about it, and put
> their name on the result in a public UI. Still Tony's call; just a different
> question.

**The first is a root citation.** The SCE rule — the one `sce_detect` implements
and the one this repo has spent three documents trying to source — is
**Cossart, Aronov & Yuste (2003), *Nature* 423(6937):283–288**, and its Methods
state the entire algorithm in one paragraph:

> "To identify peaks of synchronous activity that included more cells than
> expected by chance, we used **interval reshuffling** (randomly reordering of
> intervals between events for each cell) to create sets of surrogate event
> sequences. Reshuffling was carried out **1,000 times** for each movie, and a
> surrogate histogram was constructed for each reshuffling. The threshold
> corresponding to a significance level of **P < 0.05** was estimated as the
> **number of coactive cells exceeded in a single frame in only 5% of these
> histograms.**"

Coactive cells per frame, a rate-preserving per-cell surrogate, a thousand
iterations, pooled, percentile cut. That is `sce_detect`, twenty-three years
early. **`n_surrogates: int = 1000` in `sce.py` matches the 2003 paper by
coincidence**, having been carried here from MATLAB that cited nothing.

**The second is that it was never the Cossart-lab rule.** Rosa Cossart is first
author in **Rafael Yuste's lab at Columbia**; the method travelled with her to
Marseille, became the house method there, and eventually became CICADA. This
repo has had the direction of transmission backwards, and so did the report that
corrected it — which is why that report now opens by saying so.

**And 2003 is a floor, not a bottom.** The paper credits the technique to
**Mao, Hamzei-Sichani, Aronov, Froemke & Yuste (2001), *Neuron* 32(5):883–898**,
whose full text nobody has obtained (bronze OA at cell.com; the PDF endpoint
refuses automated fetch). Cite 2003 as the root **we have reached**.

## Where this came from, and what is second-hand

The audit is interface2's, on its branch `coord-attribution`, addressed to this
repo as `docs/exports/2026-08-21_bugarach_method_attribution.md` with the full
working at `docs/coordination_method_provenance.md`. **It is pushed and
unmerged**, so it can still change under us; the quotations above were read out
of that branch in this repo's own session, not retyped from an email.

**What this repo has verified first-hand: nothing about the papers.** No one here
has opened the 2003 PDF. The Methods paragraph is carried verbatim from a session
that did read it, and the shelf discipline in
[`detector_history.md`](../detector_history.md) applies — this is *reported*, not
*read*, until `cossart_2003_attractor_dynamics.pdf` sits on the darkroom shelf
next to `malvache_2016_awake_reactivations.pdf`. **Shelving it is step one.**

## The ledger — six rows, six citations to add

interface2 audited all six and found published prior art for every one. Two of
the closures were their own second pass reversing their own first, and one of
them — `rate_detect` — was held back as "ours as far as we know" until it wasn't.
**This is a list of citations to add, not of claims to withdraw**, because no
shipped claim rests on priority: the scoreboard already forbids
"competes with state-of-the-art" and `bakeoff.md` already reports a tie.

| detector here | the **method** is | must cite |
|---|---|---|
| `rate_detect` | cell-averaging CFAR, 1968 | Finn & Johnson 1968 |
| `sce_detect` | **published 2003, Yuste lab**, crediting 2001 | Cossart 2003; Mao 2001; then Dard 2022 / Bocchio 2020 |
| `cicada_detect` | published, and **modified** here | Denis 2020 (Zenodo); Dard 2022 |
| `sync_detect` | measure published; detection layer *not* novel either — see [the Kreuz note](2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md) | Kreuz 2015; Satuvuori 2017 |
| `loco_detect`, `coact_detect` | Unitary Events 2002; `maxlt` is GO-CFAR 1973 | Grün 2002a & 2002b; Amarasingham 2012; Hansen 1973 |

**This repo half-knew.** [`detector_history.md`](../detector_history.md) derived
the CFAR connection independently on 2026-08-22, retrieved two of the radar
primaries, and named Finn & Johnson 1968 in its own §5 — while §2 still filed
`rate_detect`, LoCo and CoactDetect under *"Tier 3 — our constructions on common
ideas"*. The two halves of this repo's own document disagree, and the audit
settles it in favour of §5.

## What to change here, checked against this tree today

Item 1 is about a name. Items 2 through 5 are about **behaviour** and would be
worth acting on with no citation attached to any of them — which is the useful
half of finding the literature after the fact.

1. **`cicada_detect` is labelled "CICADA" on a public website, and it is a
   modified CICADA.** We feed our own upstream-detected events instead of running
   CICADA's transient detection, and we paint the rise interval where the original
   paints the transient duration — both recorded in `cicada.py`'s own docstring.
   interface2's ADR-0016 is *"we can't say we used it if we turned off half of
   it"*, and their highest-priority ask is that the user-visible label become
   something like **"CICADA-derived (modified)"**. The name is in the glossary, the
   README, the viewer page, the scoreboard and every figure legend. **Tony's call;
   not made here.**
2. **`cicada_detect` has no `min_rois` floor and the other three do.** Verified:
   `grep min_rois src/bugarach/detectors/cicada.py` returns nothing, against
   `min_rois: int = 3` in SCE, LoCo and CoactDetect. In a quiet slice the surrogate
   null is nearly all zeros, its high percentile floors at about one cell, and
   one- and two-cell frames get reported as coordinated events. It is
   interface2's open defect, awaiting Tony, and it compounds with (1): a public app
   showing a one-cell "coordinated event" under another lab's name.
3. **`rate_detect`'s false-alarm rate is not rate-controlled, and nothing says
   so.** CFAR scales the reference estimate multiplicatively so the false-alarm
   rate holds as the background moves; `rate_detect` uses a fixed additive excess
   in Hz, so for roughly Poisson counts the implied z falls as √µ rises. It gets
   *more permissive as activity rises* — which is the non-stationarity failure the
   whole detector line exists to fix, present under no name. ⚠ **Predicted from the
   construction, not measured**, by interface2 or here. Nobody is asking for a
   threshold change; every tuned setting downstream depends on it. The ask is not
   to present its false-alarm behaviour as rate-controlled. This is the same
   quantity [`RESET.md`](../RESET.md) §6 calls the largest unreported confound,
   reached from the other direction.
4. **`loco_detect`'s low false-alarm rate is not a free win.** `maxlt` is GO-CFAR,
   and GO-CFAR's documented cost is target masking: a real event shortly after a
   high-rate stretch is judged against that stretch's raised bar and preferentially
   missed. For a drug wash-in that is the worst place to lose sensitivity. The
   benchmark plants events across a background ramp, so the condition is in the
   data — but the scorer breaks **false alarms** down by density and reports **no
   recall-by-density**, so it is structurally blind to the other half. The `maxlt`
   default was chosen on the half of the picture that could be seen.
5. **`percentile-of-pool` is not a multiplicity control.** It is a per-bin
   false-positive rate: 99.9th percentile implies about 10⁻³, so
   E[false alarms] ≈ (1 − pctile/100) × n_bins. Any false-alarm count this app
   reports is largely what the percentile setting produces.
6. **The "empty cell" and "two teams" framings, if any copy inherited them.**
   `detector_history.md` already quotes both and already flags them; the audit
   confirms the retraction. The "two teams" were two branches of interface2's repo
   on the same day — internal duplication, not independent replication.

## The third surrogate slot is empty, and history now says what belongs in it

`sce_detect` carries `surrogate_model="circular_shift"` and a reserved `"jitter"`
that raises `NotImplementedError` — faithfully ported from `generate_sce.m`, which
reserves the same dispatch point and errors the same way. **The historically
correct third option is `interval_reshuffle`**: the 2003 original resamples by
reordering each cell's inter-event intervals, where CICADA, Bocchio 2020,
Dard 2022, interface2's MATLAB and this port all use a circular shift. Both
preserve per-cell rate. They are not the same surrogate, and nothing here has ever
compared them.

**Parity is the product, so this is not a free addition.** A third surrogate model
is a divergence from the MATLAB original unless interface2 adds it first, and it
would land as a named alternative behind a flag with the current behaviour as the
default — [`forks.md`](../forks.md) is where that choice gets recorded. Filed as a
question for interface2, not a change here.

## What the term "SCE" is called after remains unsourced

Not Crépel 2007's abstract, not Allène 2008 (which uses cSPA/cENO/cGDP), and a
EuropePMC full-text sweep of 1995–2015 turns up nothing in this field. It is in
routine use by 2020. **The method has a root citation; the name does not** — so do
not attribute the term to a paper, here or in the app.

## Three answers interface2 asked for, all of them Tony's

1. **The CICADA label** — rename or not. Their docs will match whichever way it
   goes, so an unanswered question leaves the two projects citing differently,
   which is the failure this ecosystem already hit once on `width_sec`.
2. **Whether this port carries the "adaptive" name** — it does, in
   `sync.py`, the glossary and the served viewer page. The Kreuz note is where
   that one is argued.
3. **Where citations live in this app** — a methods page, per-detector tooltips,
   the README table, or the viewer's own help panel. Nothing here has a home for a
   reference list, and the README's table currently carries three upstreams where
   the ledger above needs fifteen.

**Rewriting the README's "Licensing & citations" section is a murderboard
deliverable** (CLAUDE.md), not a patch — it is the page a stranger reads, and the
last version of this ledger changed twice in three days.

## Why the murderboard passed a wrong attribution, which is the durable part

interface2's role 2 verifies that a citation **exists and is correctly
attributed**. It never asks whether it is the **earliest** source or merely the
oldest one the session happened to reach. Cossart 2003 took one search, and its
Methods hand over the next link in a single line — so the check that was missing
is cheap: *for a method citation, read the cited paper's own Methods for where
**it** got the technique, and either follow it or record it as an unreached
floor.* interface2 has written this up as a proposed upstream rule against
`syncytium2/murderboard`. **This repo vendors that skill and must not edit it in
place** (CLAUDE.md); when the rule lands upstream, re-vendor and bump the stamp.
Filed here so the reason survives if the upstream proposal stalls.
