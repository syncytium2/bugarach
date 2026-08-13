---
status: open
filed: 2026-08-13
---

# A fixed scoring tolerance reads SCE as a broken detector

Found while checking that the single-stream fix actually let all three
Slice-based detectors run on simulator output (2026-08-13). They run — but the
scores do not mean what they look like:

```
gt    43.3   63.7  106.0  152.7  183.1  201.9  223.0  254.9
loco  43.2   63.4  106.0  152.6  183.0  201.3  223.0  254.3   recall 0.93
sce   40.0  100.0  150.0  180.0  200.0  220.0  250.0  290.0   recall 0.00
```

SCE found the same events. It reported them at **0.00 recall** because
`score_detections` matches within `tol_sec=1.5` and SCE's onsets are bin
left-edges on its default `bin_width_sec=10.0` grid — so every detection lands
up to 10 s early and nothing ever matches. Fourteen detections, all of them
tracking planted events, all scored as false alarms.

## Why this is not an SCE bug

SCE is a **binned** detector, parity-tested against its MATLAB original. A 10 s
bin edge is the honest answer at its resolution. The mismatch is between that
resolution and a tolerance chosen for the onset-resolution detectors, and the
detectors genuinely disagree about what an event's time *is* — the same
disagreement `docs/todo/2026-08-12-port-coordination-benchmark.md` names for
`width_kind` (`tightness` / `episode_span` / `half_prominence`).

## Why it has to be settled before the bench

This is stage 3 of [`docs/simulation_plan.md`](../simulation_plan.md) — the
ROC/sensitivity bench across all six. Run today, that bench would publish SCE at
zero recall and near-total false-alarm rate, and the number would be an artifact
of the scorer. It is precisely the plan's **stranded validation** trap: numbers
checked against a benchmark whose terms did not fit them.

It also cuts the other way. A tolerance widened to 10 s for everyone makes LoCo
look no better than a detector firing on the right minute, and inflates every
detector's hit rate against a dense background. One tolerance cannot be fair to
both.

## Options

1. **Per-detector tolerance, declared by the detector.** Each port states its own
   temporal resolution (bin width, grid dt, or ~0 for onset-resolution
   detectors) and the scorer uses `max(tol_sec, resolution)`. Honest, and it
   makes the resolution a first-class property instead of a default buried in a
   signature.
2. **Score on interval overlap rather than nearest onset** — a detection matches
   if its span intersects the planted event's ±3σ window (`PlantedEvent.span`
   already exists). Sidesteps the point-time question entirely; changes the
   scorer's contract and the greedy-nearest rule with it.
3. **Report at several tolerances** and let the curve show it. Most informative,
   most work, and the least likely to be read correctly by anyone but the author.

Option 1 is the smallest change that stops the bench from lying. Option 2 is
probably the better instrument and worth considering before stage 3 hardens.

Whichever: the bench must **fail** if a detector's declared resolution is
coarser than the tolerance it is being scored at, rather than quietly returning
zero.
