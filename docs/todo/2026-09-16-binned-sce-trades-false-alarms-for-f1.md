---
status: open
filed: 2026-09-16
---

# Binned SCE: F1 0.525 at 3 false calls an hour, or 0.665 at 42

> **Status `open`, and the decision is Tony's.** Put to him in the session that filed it; the
> briefing has no room for another waiting item
> ([`2026-08-30-the-briefing-has-one-todo-of-headroom.md`](2026-08-30-the-briefing-has-one-todo-of-headroom.md)).

**What was measured** — `tools/retune_operating_points.py`, 2026-09-16, 48 bench recordings per
point, scored over each call's own bins. `retune.json` and Figure 1 are in
`<darkroom>/bugarach/archive/2026-09/2026-09-16-best-parameters/`.

| threshold percentile | mean F1 (quiet, busy) | calls/hour on the empty recording |
|---|---|---|
| 99 (shipped until 2026-09-16) | 0.490 | 1.6 |
| **98 (shipped now)** | 0.525 | 3.4 |
| 95 | 0.597 | 8.2 |
| 85 | 0.661 | 31.2 |
| 75 (the F1 optimum) | 0.665 | 41.8 |

The budget is `bench.MAX_FALSE_POSITIVES_PER_HOUR["sce"] = 6`, set as "measured 3.1 plus slack"
at the old setting — a regression budget, not a principle. 98 is the loosest setting under it.
Going to 75 buys **+0.14 mean F1** for **12 times the false calls** on a recording where nothing
was planted.

**The precedent runs the other way.** On 2026-08-20 Tony moved locust's percentile to cut its
empty-recording false calls 18-fold for "a wash in F1" (FOUNDATIONS §9). This is the same trade
with a real F1 gain on the other side of it.

**Also worth knowing before deciding:** in the dense empty stretch inside an ordinary recording
(the promiscuity probe) binned SCE fires about 6 times a minute at every threshold from 10 to
99.9 — one call per 10 s bin. That promiscuity is structural and no threshold removes it
([`2026-09-08-binned-sce-is-close-to-random-placement-here.md`](2026-09-08-binned-sce-is-close-to-random-placement-here.md)).

**Decision needed:** keep 98, or raise SCE's empty-recording budget deliberately and ship a looser
threshold.
