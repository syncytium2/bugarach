# Goals — one page per thing we are trying to achieve

**Why this folder exists.** By 2026-09-14 the work toward a label-free detector was spread across two
handoffs, several proposals and review records, a long tail of todos, a draft branch and two darkroom
run folders. Every piece was findable, but nothing said what the goal was, what was settled, what was
dropped and what was waiting on a decision, so sessions and Tony both lost the thread. A long-lived
goal branch was considered and rejected: sessions start from `main`, the briefing and
[`INDEX.md`](../INDEX.md) read `main`, and a branch holds commits, not a summary.

**A goal page holds**, in this order: the goal in a paragraph; where it stands; what is settled, with
strength and source; what was tried and dropped, and why; what is waiting on Tony; open work a session
can do without a ruling; where the work lives; how the page stays true.

**How it differs from its neighbours.** [`MILESTONES.md`](../MILESTONES.md) is the whole project's
established record, one row per result. [`INDEX.md`](../INDEX.md) is keywords to files. A handoff is one
session's state at a stop and is deleted or archived when spent. A goal page lives as long as the goal
does and is the first thing a session reads when it picks that goal up.

**Conventions**

- A result, ruling or dropped approach toward a goal **updates its page in the same PR**.
- A session working toward a goal puts `Goal: <page name>` on its board claim and names its branches
  `<prefix>/<slug>`, so `git branch --list '<prefix>/*'` shows what is in flight.
- No tree counts. Every restated number links to the file that owns it, and the linked file wins.
- When a goal is reached or stopped, the page says which at the top and stays as the record.

| goal | page | branch prefix |
|---|---|---|
| A coordinated-event detector that learns without labels | [`unsupervised-learning.md`](unsupervised-learning.md) | `unsup/` |
