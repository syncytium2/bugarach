---
status: open
filed: 2026-09-12
---

# Stella 2022 answers a different question than the one the screen is asking

An independent read of `<darkroom>/bugarach/lit/surrogates/stella_2022_comparing_surrogates.pdf`
(Stella, Bouss, Palm & Grün 2022, *eNeuro* 9(3) ENEURO.0505-21.2022), filed because the paper is
being used to reason about which surrogate a self-supervised detector should train against.

## What the paper measures

Six surrogates run through SPADE on macaque motor cortex: uniform dither, dither with dead time,
joint-ISI dither, ISI dither, trial shifting, window shuffling. The criterion throughout is the
**false-positive rate of a significance test**. Their headline is a pattern count over 24 datasets
per monkey — uniform dither 203 and 121, against 14, 10, 10, 7–14 and 11 for the other five.

## Why that does not transfer unchanged

**A conservative null and a clean training contrast are different requirements, and ours is
stronger.** A significance test needs its surrogate not to *under*-produce chance patterns. A
self-supervised detector needs its surrogate to differ from real data in **nothing the encoder can
see** except cross-ROI timing. A surrogate can be perfectly conservative for SPADE and still hand a
discriminator a marginal feature to win on. The five reasons Stella gives for preferring trial
shifting — easy to implement, few parameters, keeps ISIs exactly, as conservative as the others — are
properties of a test procedure, not statements about what a learner can exploit.

**Their diagnosed mechanism is not the one this project found, and both apply here.** The review of
2026-09-10 killed uniform dither for manufacturing within-ROI intervals shorter than any real one.
Stella's account of the same surrogate's failure is that dithering itself deletes nothing — the
binarization step does, once dithered onsets fall in one bin — so the surrogate carries fewer events
than the real data, worse at higher rates, driven by dead time and CV. That is the same root cause
seen from the other end, and it is a **count** difference, which is
[its own todo](2026-09-12-count-preservation-after-encoding-is-the-gate-stella-actually-found.md).

**Trial shifting's guarantee does not survive the move to continuous imaging.** Stella's trials come
from the monkey's task. Continuous baseline recordings have none, so the screen uses pseudo-trials
bounded by silences — which reintroduces exactly the parameter their "fewer parameters" argument was
praising the method for avoiding.

**Their dead-time practice supports this project's τ ruling, in their own terms.** They estimate the
dead time per neuron as its minimum ISI, then cap it at 4 ms, because at low firing rates the minimum
ISI can reach hundreds of milliseconds and stop being a biologically meaningful number. This project's
observed floors are 0.40 s fast and 2.80 s slow. By Stella's own reasoning those are properties of the
event extractor, not of biology — which is the argument for
[τ being the producer's to declare](2026-09-10-the-dead-time-floor-is-the-producers-number.md) rather
than ours to fit.

## What this changes

- **Do not adopt trial shifting on Stella's authority.** This project has its own evidence pointing at
  whole-train shifting, from the per-ROI leak detector, and that is better grounds. See
  [the join](2026-09-12-join-the-leak-results-to-the-destruction-results.md).
- The existing warning stands and is not weakened by this read: their discussion says the five valid
  surrogates reach almost identical significance, while their own results describe a movement-epoch
  pattern found by every surrogate except the one they recommend.

## Closes when

The screen's report states which of its criteria are inherited from Stella and which are this
project's own, and no document cites the paper as settling a surrogate choice for a training
objective.
