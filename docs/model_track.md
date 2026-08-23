# The model track — separate from the website, on purpose

> **This is the MODEL track.** The website is [`docs/webapp_spec.md`](webapp_spec.md).
> Tony, 2026-08-18: *"separate out the two main tasks (model and website)"*, and
> *"invest in building out the full infrastructure then refine the model"* — so the
> website has priority and nothing here blocks it.
>
> **Nothing here is approved to run.** The experiments and their costs are in
> [`docs/overnight_spec.md`](overnight_spec.md) Track B, which carries its own refusal
> block.

## Where the model actually stands

- **Centre−surround ties the best hand-written detectors** — 0.668 ± 0.061 against
  CoactDetect's 0.651 ± 0.044 — and wins on cost: 0.014 s to scan a held-out fold,
  1,149 parameters, 5.6 s to train.
- **It transfers worse than two of the six** from a quiet background to a busy one,
  which is a negative result about its own central claim. Fit busy, deploy quiet.
- **The multi-scale bank is redundant on this data set** — one kernel scores the same for
  81 fewer parameters. Probably the data set, which plants one event width.
- **The surround clamp is a wart, not a cause** — raising it changes nothing.
- **The per-cell architecture does not train**, and why is unresolved; it also trains at
  a tenth the learning rate of the model that works, so the comparison is uncontrolled.
- **Every learned number is one training run per fold.** No seed error bars anywhere.

## What is not established, and must not be claimed

- **Nothing here says any detector is right about a real slice.** The data set is
  simulated; its settings are measured.
- **"Competes with state-of-the-art models from the literature" is not supported —
  but the earlier phrasing of this was wrong and Tony corrected it.** *Published
  methods are in the comparison*: **CICADA** is the Cossart lab's, ported here (MIT,
  © 2019 Cossart Lab) and scoring 0.541, and **SpikyDetect** runs on cSPIKE/PySpike's
  adaptive SPIKE-synchronization profile (Kreuz lab) — a published measure with our
  event detector on top. So the accurate claim is narrower and still worth making:
  the comparison contains **no published *learned* method**, and **none of the
  assembly-detection family** — ICA/PCA, CAD, graph and item-set methods — which is
  where the coordination literature actually concentrates. See
  [`docs/todo/2026-08-17-literature-deep-dive-handoff.md`](todo/2026-08-17-literature-deep-dive-handoff.md),
  whose first item is to run two or three of them rather than search harder.

## Why the assembly-detection family cannot be ported yet

**Our generator plants no assemblies.** `simulate.py` draws each planted event's
participants fresh — `rois = rng.choice(nR, size=np_, replace=False)` — so every event
has a different random subset of cells and no group ever recurs.

That matters more than it looks. The whole assembly-detection literature works by
finding **recurring co-activation patterns**: ICA/PCA assembly detection projects onto
patterns that repeat, CAD finds groups with consistent lag constellations, item-set
mining counts sets that appear often. Run any of them on this data set and they find
nothing — **and the zero would be about our generator, not about the method.** Porting
one today would produce a comparison we win meaninglessly, which is worse than not
running it.

It also means something about our own benchmark: **it cannot reward membership
structure at all.** A detector that exploits which cells tend to fire together — ours
or anyone's — has no advantage to demonstrate here, because there is none to find.

The order that makes the comparison possible:

1. **Ask the data whether assemblies exist.** Do the 85 real recordings show recurring
   participant groups, or is participation event-by-event random? The assessor already
   clusters co-active onsets and records which ROIs took part; the membership-overlap
   statistic across events is a small addition, not a new instrument. **This is a real
   result about the preparation either way**, and it is cheap.
2. **If they recur, plant them.** The generator gains an assembly structure —
   participants drawn from a small number of recurring groups rather than uniformly.
3. **Then port PCA/ICA assembly detection** (Lopes-dos-Santos, Ribeiro & Tort 2013,
   *J. Neurosci. Methods*): Marchenko–Pastur for the number of assemblies, ICA for the
   patterns, and an activation time course per assembly that thresholds into events.
   It is the right first port — a genuinely different principle from all six of ours,
   which are variations on "more coincidence than the local background explains"; it
   emits a **time course**, so our scorer works on it unmodified and its threshold is
   exactly the one declared knob the fair bake-off sweeps; and Marchenko–Pastur picks
   the assembly count without importing a second human judgement the way K did.
4. **Hold the port to the same bar as the six.** They are 1e-9 against a MATLAB
   original; a new port with no oracle is a claim nobody can check, and "we ported it
   wrong" is the first thing a reviewer will say when a literature method loses.

⚠ If step 1 says participation *is* random event-by-event, then the assembly family is
not the right comparison for this preparation at all, and that is the answer — not a
disappointment.

## The queue, in order

1. **Close the seed gap.** Every other number inherits its error bars.
2. **The event-rate ceiling.** The fitted surround is 9.7–18.1 s wide and *is* the
   background estimate, so events arriving faster than that should make the model
   subtract its own signal. One falsifiable prediction, cheap to test.
3. **The width ceiling** — the centre clamps at 64 samples, ~6.4 s.
4. **Drop the raw brightness channel** — one line, closes the last cheap explanation
   for the transfer asymmetry.
5. **A second data set** from DANDI: it cannot score a detector, and it can say whether
   any of this survives statistics that are not ours.
6. **A data set with varying event widths**, or DANDI instead of it, to settle whether
   multi-scale is worth keeping.

## The seam with the website

Exactly one thing crosses: **the app trains and runs whatever is in the
`ARCHITECTURES` registry.** Adding or removing a model is one class and one
`@register` line, and the app picks it up without an edit. So the model track can
change the model freely, and the website track can be built against the registry
rather than against any particular network.

The one model fact the app must encode today: **fit on the busier recordings and
deploy downward.** It is measured, it is free to implement, and it is the difference
between a −0.24 transfer penalty and a +0.12 gain.
