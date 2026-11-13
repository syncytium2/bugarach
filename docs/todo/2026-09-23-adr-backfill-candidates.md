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
- [x] **One default dataset, confirmed by Tony every session** (2026-09-21): written up, and its
  confirmation half retired, in
  [ADR-0018](../adr/0018-the-dataset-is-reported-not-confirmed.md) (2026-10-14).
- [ ] **A known contamination stops the work** (2026-09-17): CLAUDE.md and
  `dataset.refuse_if_contaminated`.
- [ ] **No long-lived goal branch; sessions start from `main`** (2026-09-14): CLAUDE.md.
- [ ] **Performance is a table, not a ranking** (2026-08-30): `docs/performance_table.md`.

## Audit of 2026-11-11 (Tony: *"and perfect ADR hygiene"*)

Every ADR file on any branch was listed and each status line read.

**Written that day:** [ADR-0020](../adr/0020-one-route-from-a-folder-to-calls-per-stream.md) (the
ruling of the day) and [ADR-0021](../adr/0021-the-toolset-is-validated-on-synthetic-data-first-with-coded-detectors.md)
(the 2026-10-22/23 synthetic-validation rulings, backfilled because ADR-0020's route leans on
them).

**Found, and what was done:**

- **0012 and 0013 exist only on branches** (#848, #855), Proposed since 2026-09-28. The index
  recorded that inside ADR-0014's title cell. They now have their own paragraph under the index,
  with the command that lists every number taken on any branch. **Both were ruled the same day**: 0012
  declined, 0013 accepted as amended, and both files are now on `main` with index rows.
- **ADR-0019 is Accepted and not implemented**: every bench still plants 6 decoys per recording.
  A dated note in the ADR says so and points at the work. No decision changed.
- **ADR-0005's status line is not in the template's form** (`- **Status:** accepted 2026-08-29`,
  no `## Status` heading). Left alone: an accepted ADR is not edited for form.
- **ADR-0010 says "Accepted, once Tony had ruled on all eight open points"**, and its ruling 2
  (the realistic bench is the default) was carried out on 2026-10-07. Consistent.

**Rulings since the gap that settle how work is done and have no ADR.** Same rule as above: the
session that next builds on one writes it first.

- [ ] **Fast is the producer's event set minus the event matched to each slow event; no event is
  in both streams** (2026-10-07): a working rule *"for now"*, in
  `docs/goals/combined-stream-coordination.md`. It becomes an ADR when the producer states it,
  not before: until then it is an assumption, and an ADR would harden it.
- [ ] **A baseline window shorter than 15 minutes is not measured** (2026-09-17):
  `bench.MIN_BASELINE_SEC`, goals README decision 2.
- [ ] **No ranking in the detector document; numbers already recorded stay as records of their
  date** (2026-10-20): cited by ADR-0019 decision 3 and by the synthetic-validation handoff, and
  held nowhere as a record of its own.
- [ ] **Times written for Tony are Michigan local time** (2026-09-25): CLAUDE.md.
- [ ] **Output file names come from the estate's naming tool** (2026-10-12): CLAUDE.md.
- [ ] **The darkroom's top level holds the last week** (2026-09-26): CLAUDE.md.
- [ ] **01-lit is the master literature library** (2026-10-29): pull request #920, not merged.
- [ ] **The dissertation chapters are a test of the collaboration, with no committee**
  (2026-10-29): pull request #919's branch only.

The run-record naming decisions ([`run_records.md`](../run_records.md)) amend ADR-0005 and are
still waiting on Tony. When they are ruled, they land as an ADR that supersedes or extends 0005,
not as edits to it.
