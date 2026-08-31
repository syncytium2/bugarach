---
status: waiting-on-tony
filed: 2026-08-31
---

# Two overnight results need a ruling, and the briefing cannot see either of them

waiting: Promote the 24-seed bake-off or leave it beside the 8-seed one; and choose a K for the Cossart assessment. Both are written up with their data.

This file exists because of a gap rather than a finding. The SessionStart briefing lists
items waiting on Tony by grepping **`docs/todo/*.md` only**. Two results produced overnight
carry `status: waiting-on-tony` and live beside the data they describe, under
`docs/learned/` — so neither would have reached a session at startup, which is the one
place they need to appear. This is the pointer that fixes that. Retire it when both are
decided.

## 1. The bake-off at 24 seeds — promote it, or leave it beside the 8-seed run?

[`docs/learned/bakeoff_24seed.md`](../learned/bakeoff_24seed.md)

Ran in 9m36s. The shipped run is 8 seeds and every F1 in the performance table rests on it.
At 24 the **spread across the top four collapses from 0.043 to 0.011**, every fold range
narrows, and the order inside that group rearranges — LoCo fourth to second while tube
falls from first. Nothing about the 8-seed ordering of the leaders survived tripling the
data. **locust also crosses its promiscuity ceiling**, 30.62/min against 25, where at 8
seeds it read 21.48 and passed.

Nothing was promoted, because promotion is not a file copy: `bakeoff.json` is read by 20
modules under `src/`, `tests/` and `tools/` and quoted in about ten documents plus the
public site and several figures. Three options are set out in that file; none was chosen.

**Checked before any of it was trusted:** re-running the 8-seed configuration reproduces
the shipped file exactly — all twelve detectors, including the six PyTorch fits, delta
0.0000.

## 2. The Cossart transfer — which K?

[`docs/learned/cossart_transfer/README.md`](../learned/cossart_transfer/README.md)

Their median recording holds **566 ROIs** against our 32. Carried across unchanged,
**CoactDetect transfers for free** and the learned models find **0 of 120** planted events;
refitted, the learned models are the best detectors on that field by a clear margin. And
**rate+context fails with perfect recall** — 120 of 120 events found, precision 0.09, 1311
detections for 120 events — which is the opposite failure from the learned models and is
invisible in an F1 column.

`derive_spec.py` requires `--k` explicitly and refuses to make that call, so both specs
were produced `--unreviewed` and say *"NOBODY HAS LOOKED"* in their own notes. k=3 and k=8
were run as a sensitivity pair instead of choosing: the ordering survives, the numbers do
not stand alone.

**The gap is the finding.** Our `k_chosen` is 3 of about 34 ROIs, roughly 9%. Three of 566
is 0.5%, and 24 — the top of their scan — is 4%. No K in the scan reproduces our
participation fraction.

## Should the briefing scan more than `docs/todo/`?

Open, and not obviously yes. Widening the grep would have surfaced both of these without
this file, and would also have cost briefing bytes at a moment when the budget has about
680B of headroom — see
[the briefing has one todo of headroom](2026-08-30-the-briefing-has-one-todo-of-headroom.md).
The alternative rule is that anything waiting on a human belongs in `docs/todo/` whatever
else it sits beside, and a result file simply keeps `status: open`. That is a convention
question rather than a code change, which is why it is written here rather than fixed.
