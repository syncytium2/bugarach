---
status: open
filed: 2026-08-25
---

# A flat guard gain across the neighbour gap is what self-masking relief looks like

**This is a question about `forks.md` §4a's conclusion, raised by a review of something else.
It is not an edit, and §4a should not be changed on the strength of it without a measurement.**
§4a has already been corrected twice and its current form is the careful one; this is the
objection that survived a murderboard, recorded so it can be settled rather than rediscovered.

## The conclusion at issue

§4a concludes the guard interval is **not doing guard-cell work** — that it is "a threshold
knob that happens to be spelled in seconds". The evidence is that its recall gain is **flat
across the neighbour gap**: CoactDetect at a 5 s guard gains +0.045 where a neighbour sits
within 15–30 s, and +0.046 where the nearest is beyond 60 s. Where there is nothing to unmask,
it helps just as much.

## The objection

**Guard cells relieve two maskings, and §5.1 of `detector_history.md` names both:**

- **self-masking** — the event's own energy sits in the reference that judges it;
- **mutual masking** — a *neighbouring* event sits in the reference too.

A gap-stratified test measures the second. **Self-masking relief is gap-independent by
construction** — every event self-masks, whether or not it has a neighbour. So a gain that is
flat across the gap is the signature of guard-cell work with **no mutual-masking component**,
which is not the same thing as no guard-cell work at all.

The same objection reaches §4a's second leg. The sparse bench is described as the place "where
the effect can only be an artifact" because a second planted event can never enter the context
— but §5.1 says in terms that *"the test bin's own events sit in the null pool that judges
them"*. Self-masking is present on the sparse bench. A guard raising recall there is what the
mechanism predicts, not evidence against it.

## Two more things in §4a's own table that bear on it

- **It is non-monotonic, and the middle cell is never discussed.** CoactDetect reads 0.711 at a
  15–30 s gap, **0.882** at 30–60 s, and 0.855 with no neighbour at all. A neighbour at 30–60 s
  leaves recall *better* than no neighbour does. Under a pure crowding story that cannot happen,
  so either the strata differ in something besides the gap, or the effect is inside the noise —
  and if it is inside the noise, the ±0.001 flatness claim goes with it.
- **The seed count moved the sign once already.** §4a's first version, on 4 seeds, reported
  "−0.021 to +0.021 with no direction". At 8 seeds it is a consistent positive. A measurement
  whose sign depends on 4 versus 8 seeds needs its spread published beside it before three
  decimals are quoted from it.

## The better structural argument, which nobody has used

If the conclusion survives, there is a sharper reason for it than pool shrinkage — and unlike
pool shrinkage it applies to LoCo specifically and is checkable from the source:

**LoCo's guard excises around the *anchor*, not around the bin under test.** Thresholds are
computed at anchors every `thr_step_sec` (15 s FAST, 30 s SLOW) and each bin takes its nearest
anchor's value. At the 5 s guard §4a measured, the excised band is ±2.5 s of the anchor, so most
bins in a 15 s step keep their own events in the reference entirely. LoCo's guard cannot relieve
self-masking for the bins it does not cover — which would also explain the thing §4a finds
strangest, that LoCo's gain is *worse* than flat (+0.014 crowded against +0.025 isolated).

## And the mechanism §4a states does not fit one of its two detectors

§4a explains the gain as *"a fixed 99.9th percentile of a smaller sample underestimates the
tail"*. That is LoCo's estimator. **CoactDetect has no percentile**: its bar is a Gaussian tail
on the mean and sd of `n_surrogates` counts, and `n_surrogates` is unchanged by a guard — only
the span the events are drawn from changes. Whatever moves CoactDetect's +0.045, it is not a
shrinking sample. §4a applies one mechanism to two estimators.

## What would settle it

A guard sweep scored on **isolated events only**, against a no-guard control, with the seed
spread published. If the gain persists on events that have no neighbour and cannot be mutually
masked, the remaining candidates are self-masking relief and a lowered bar — and those separate
cleanly by looking at the threshold itself rather than at recall: a lowered bar moves the
threshold on *every* anchor, including anchors with no event anywhere near them. §4a already
did a version of this ("over 891 candidate bins the mean null falls 3.689 → 3.645") for a
different claim; the same instrument answers this one.

Run record: [`loco_coact_as_cfar_2026-08-25`](../reviews/loco_coact_as_cfar_2026-08-25.md) §E2.

---

# MEASURED, 2026-08-25 — the bar does not fall everywhere. It rises where the guard excised nothing.

`tools/probe_guard_where_it_lands.py`. The question above asks *how much* the bar moves; the
instrument built to settle it asks **where**. Both detectors expose their own bar per bin —
LoCo the rolling threshold envelope, CoactDetect the surrogate null mean — so run each at
guard 0 and guard *g* on the same recording and the same seed, and split the bins by whether
the excised band actually held any events.

The two hypotheses make opposite predictions about the **empty** column: a threshold knob
lowers the bar there too, self-masking relief leaves it alone. **Neither is what happens.**

4 seeds, `baseline_quiet`, shipped operating points. `d` is bar(guard) − bar(0), and the
spread is across seeds, not across bins — bins within a seed are not independent.
**flip** = every seed individually shows empty > 0 and occupied < 0.

| recording | detector | guard | n empty | d empty ± sd / bar | n occupied | d occupied ± sd / bar | flip |
|---|---|---|---|---|---|---|---|
| crowded | LoCo | 5 s | 1128 | **+0.0569** ± 0.0170 on 2.81 | 1746 | **−0.0360** ± 0.0189 on 2.89 | **yes** |
| crowded | LoCo | 20 s | 73 | **+0.1849** ± 0.1209 on 2.64 | 2798 | **−0.0090** ± 0.0023 on 2.87 | **yes** |
| crowded | CoactDetect | 5 s | 8372 | **+0.0388** ± 0.0016 on 0.44 | 13204 | **−0.0259** ± 0.0021 on 0.51 | **yes** |
| crowded | CoactDetect | 20 s | 534 | **+0.1591** ± 0.0174 on 0.32 | 21042 | **−0.0050** ± 0.0026 on 0.49 | **yes** |
| bench | CoactDetect | 5 s | 1904 | +0.0329 ± 0.0029 on 0.44 | 3456 | −0.0173 ± 0.0055 on 1.04 | **yes** |
| bench | LoCo | 5 s | 259 | +0.0405 ± 0.0265 on 2.90 | 453 | −0.0093 ± 0.0440 on 3.75 | no |
| bench | LoCo | 20 s | 20 | +0.2250 ± 0.2836 on 2.98 | 690 | +0.0075 ± 0.0289 on 3.45 | no |
| bench | CoactDetect | 20 s | 129 | +0.1665 ± 0.0572 on 0.34 | 5231 | −0.0023 ± 0.0048 on 0.84 | no |

**On the crowded recording — the one §4a's headline numbers come from — every detector, at
both guard sizes, in every seed: the bar RISES where the guard excised nothing and FALLS
where it excised events.** The signs are opposite, not merely different in size.

## What that settles, and what it does not

**§4a's stated mechanism is refuted.** *"Excising a span shrinks the null pool, and a fixed
99.9th percentile of a smaller sample underestimates the tail"* — so *"every anchor gets an
easier threshold"* — predicts the bar falls at **every** anchor. It does not. Where the
excised band held nothing the bar **rises**, by +0.04 to +0.06 at a 5 s guard, which for
CoactDetect is about +9% of the bar. The arithmetic makes sense: the retained span is
compacted onto a shorter line, so the same events sit at higher density and land in the test
bin more often. Shortening the reference pushes the bar **up**.

**The bar falls only where the guard removed events, which is self-masking relief.** That is
what this file argued, and it explains §4a's observation rather than contradicting it:
self-masking relief is gap-independent by construction, so the recall gain it produces is
flat across the neighbour gap — exactly what §4a measured and correctly reported.

**And §4a's sparse-bench leg is not the artifact it was read as.** The bench rows show the
same opposite-sign pattern for CoactDetect. §5.1 says the test bin's own events sit in the
null pool that judges it, so self-masking is present on the sparse bench and a gain there is
what the mechanism predicts.

**What is NOT shown, and must not be claimed:**

- **This measures the bar, not recall.** That the bar falls at occupied anchors does not
  demonstrate it is what produces §4a's +0.045. That link is one further step, unrun.
- **The effects are small against the bar they move** — −1.2% for LoCo crowded, −5% for
  CoactDetect crowded.
- **Two bench rows are inside seed noise** and are marked so: bench LoCo at 5 s has a
  standard deviation larger than its occupied mean, on 453 anchors.
- **At a 20 s guard the occupied effect collapses** (−0.009, −0.005) while the empty effect
  grows. A guard that wide excises so much that compaction dominates — an argument against
  large guards, and against reading §4a's 20 s LoCo numbers as the same phenomenon as its 5 s
  ones.
- 4 seeds, simulated recordings, `baseline_quiet` only.

## Two things the instrument needed, recorded so nobody rediscovers them

**LoCo's guard excises around the ANCHOR, not the bin under test**, and a bin can sit up to
`thr_step_sec / 2` — 7.5 s at the shipped FAST setting — from the anchor whose threshold it
inherits. Scoring occupancy at the bin asks about a stretch of time the guard never touched.
The first run of this probe did exactly that and reported LoCo as showing no relief at all:
+0.0074 empty against +0.0098 occupied, both positive, no signal. Scoring at the anchor
turned the same data into +0.0405 against −0.0093.

**The probe has a `--selftest` that runs guard 0 against guard 0 and requires every delta to
be exactly zero.** It is the only thing standing between this measurement and a report of RNG
drift with a mechanism attached — which is the failure §4a itself was corrected for twice. It
passes on 6,072 bins.

## What is still Tony's call

**`docs/forks.md` §4a is not edited by this.** Its conclusion needs amending — the guard is
doing guard-cell work, of the self-masking kind — but §4a has been corrected twice already,
and rewriting it on the strength of a probe written by the session that raised the objection
is the shape of error this repo keeps catching. The measurement is here; the ruling is not
this file's to make.

If it is accepted, the consequence reaches
[`censoring is the instrument the guard was not`](2026-08-23-censoring-is-the-instrument-the-guard-was-not.md),
whose title is a claim this undercuts, and
[`CFAR variants are a knob axis`](2026-08-25-cfar-variants-are-a-knob-axis-not-new-detectors.md),
whose item B is ranked on it.
