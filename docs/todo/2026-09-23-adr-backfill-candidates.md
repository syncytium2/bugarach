---
status: open
opened: 2026-09-23
area: records
---

# ADR backfill: the rulings from the 25-day gap, written up as they are leaned on

Tony, 2026-09-23: *"let's restart the adr habit and backfill as needed."* No ADR was written
between ADR-0005 (2026-08-29) and ADR-0006 (2026-09-23), and the rulings of that period are
spread across bench comments, handoffs, todos, goal pages and the ruling queue
([`adr/README.md`](../adr/README.md) says how that happened).

**As needed means this:** a session that is about to build on one of these, or finds it
disputed, writes its ADR first, in the same PR. Nobody backfills the list for its own sake.
Tick an item off by linking the ADR that now holds it.

Candidates, newest first, each with where it lives today:

- [ ] **Calcium events do not "fire"** (2026-09-23): the glossary and `writing_conventions.md`,
  mechanized as sapper SAP017 (#766).
- [ ] **The combined stream is every fast and slow onset of a ROI in one train, labels kept,
  nothing deduplicated** (2026-09-22): `src/bugarach/combined.py`, the combined goal page.
- [ ] **The probe basis is background, end to end** (2026-09-22): the ruling queue, item 1b.
- [ ] **The jitter constant: the benches carry the measurement** (2026-09-22): the ruling queue,
  item 2.
- [ ] **SPIKE-synch flat across the background axis is a result, not a reason to move the axis**
  (2026-09-22): the overnight handoff, `docs/handoffs/2026-09-22-overnight.md`.
- [ ] **One default dataset, confirmed by Tony every session** (2026-09-21): CLAUDE.md and
  `bugarach.dataset`.
- [ ] **A known contamination stops the work** (2026-09-17): CLAUDE.md and
  `dataset.refuse_if_contaminated`.
- [ ] **No long-lived goal branch; sessions start from `main`** (2026-09-14): CLAUDE.md.
- [ ] **Performance is a table, not a ranking** (2026-08-30): `docs/performance_table.md`.

The run-record naming decisions ([`run_records.md`](../run_records.md)) amend ADR-0005 and are
still waiting on Tony. When they are ruled, they land as an ADR that supersedes or extends 0005,
not as edits to it.
