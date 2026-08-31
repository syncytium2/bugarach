---
status: superseded
filed: 2026-08-30
---

# The tie margin does not survive its own test

> **SUPERSEDED the same day — dissolved, not solved.** Tony: *"no ranking just a table of
> performance … no one said we need to declare a winner."* The margin existed to decide
> when one detector beats another; with no ordering there is nothing for it to decide, so
> the question is retired without an answer. **It was never fixed — 0.02 still would not
> have worked.** What replaced it: [the performance table](../performance_table.md).
>
> **Kept because the measurement is still true.** If an ordering is ever wanted again,
> everything below is the evidence about what this bench can and cannot separate, and §5
> of the performance table records why the standard statistical route (Friedman +
> Nemenyi) is the wrong fit for a bench that ships deliberate controls.

> **Not murderboarded** — a finding for sessions in this tree, produced during the
> murderboard of [`docs/ranking_rule.md`](../ranking_rule.md). Every number is
> reproducible in about ten seconds from the command at the bottom.

The ranking rule exists to survive a seed change. Its promise, in its own words: the
result may move, the **tiers** should not. That promise now has a measurement, and it
does not hold at the margin that was chosen.

## What was run

Six hand-written detectors, one background level (0.0190 Hz/ROI, the busy end of the
grid), four folds, and the whole thing done twice — once on seeds 1–12 and once on
seeds 13–24. Then `rank()` on each block, and the two tierings compared.

## What came back

| | seeds 1–12 | seeds 13–24 |
|---|---|---|
| tier 1 | **CoactDetect + LoCo + rate+context** | **rate+context** |
| tier 2 | locust | LoCo |
| tier 3 | SPIKE-synch | CoactDetect |
| tier 4 | binned SCE | locust |
| tier 5 | — | SPIKE-synch |
| tier 6 | — | binned SCE |

A three-detector tier on one block, three separate tiers on the other. The argmax is
`rate+context` in both, so **the ordering was stable and the tiering was not** — the
opposite of what the design predicts.

## How big a margin would it take

| tie margin | tierings agree? |
|---|---|
| 0.02 — **shipped** | no |
| 0.03 | no |
| 0.04 | no |
| 0.05 | no |
| 0.06 | no |
| **0.08** | **yes** |
| 0.10 | yes |

Four times the chosen value.

## It is not thin folds

The obvious objection is three seeds a fold. Doubling it does not help: at **24 seeds
per block, four folds of six**, the tierings still disagree at 0.02, 0.03 and 0.04,
and at 0.05 they still differ over whether locust and SPIKE-synch share a tier. So
this is not a sampling problem that more compute retires.

There is a real consistency check inside that: §1 of the rule document measures the
between-block swing in a single pairwise gap at **0.042**, and a margin has to be
wider than the swing it is meant to absorb. 0.02 is half of it. The margin was set
from the bench's *noise floor* — the smallest difference worth believing — but what
the tiers need is the *between-block spread*, and nobody checked that those were the
same number. They are not, by a factor of about four.

## The three ways out, and they are different claims

1. **Raise the margin** to something the bench supports — 0.08 on this evidence. The
   cost is that almost everything ties: at 0.08 the six collapse to three tiers, and
   the rule stops being able to say much beyond "these three lead".
2. **Restrict the claim to tier 1 versus the rest.** Tier-1 membership is the stable
   part — it agrees from about 0.05 up. The finer distinctions below it are the ones
   that will not hold still. This keeps a useful answer and stops promising a
   resolution the bench cannot deliver.
3. **Keep 0.02 and publish the instability** — quote the full tiering only alongside
   the seed block it came from, the way an F1 must be quoted with its background.
   Honest, and it gives up the property the rule was written for.

Option 2 is the one that keeps a usable rule without overstating it, but the choice
is a claim about what this project is willing to assert, which is why it is Tony's.

## What is NOT in doubt

The rest of the rule is unaffected. The gates fire, the pairing works, the seed floor
refuses, and the two-conjunct tie test still blocks both of the comparisons §5 shows
it blocking. What is in question is only how far down the tiering can be trusted.

## Reproduce

```
PYTHONPATH=$PWD/src python -c "
from bugarach.bench import evaluate_background_curve as ebc
from bugarach.rank import FoldScore, rank
DET=['coact','loco','rate','sce','sync','cicada']; RATE=0.0190
def block(lo,n,nf):
    seeds=list(range(lo,lo+n)); per=n//nf; sc=[]
    for fi in range(nf):
        fold=tuple(seeds[fi*per:(fi+1)*per])
        for d in DET:
            r=ebc(d,'baseline_quiet',fold,rates=(RATE,))[RATE]
            sc.append(FoldScore(detector=d,fold=fi,f1=r.f1,seeds=fold,
                                hot_fa_per_min=r.hot_fa_per_min))
    return sc
for m in (0.02,0.05,0.08):
    a=rank(block(1,12,4),tie_margin=m).tiers; b=rank(block(13,12,4),tie_margin=m).tiers
    print(m,[set(t) for t in a]==[set(t) for t in b],a,b)"
```

## See also

- [`docs/ranking_rule.md`](../ranking_rule.md) §5 — carries this as a blocking ⚠.
- [the ranking brief](../handoffs/2026-08-30-ranking-the-detectors.md) — D4, and the
  reason a margin was wanted in the first place.
