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
| Every hand-written detector at a setting this bench chose | [`coded-detector-optimization.md`](coded-detector-optimization.md) | `opt/` |
| A learned architecture that beats the hand-written detectors, separably | [`learned-model-family.md`](learned-model-family.md) | `nets/` |
| A document about the detectors an outside reader can judge | [`detector-review-document.md`](detector-review-document.md) | `review/` |

**Three of these four were written on 2026-09-16, and writing them is what found the problem they
fix.** Asked where four goals stood, two independent searches of `main` reported that the detector
review document did not exist and that detector optimization had nothing in flight. Both were reading
the tree correctly: the work, and the only summary of it, sat together on unmerged branches. A goal
whose account of itself lives on the branch it describes disappears the moment that branch lands — or,
until then, is invisible to every session that starts from `main`, which is every session.

**So a page may point at a branch, and it must say so.** Each of the three carries a ⚠ marker on every
source that is not on `main` yet, and taking a marker off is part of landing the branch it names.
