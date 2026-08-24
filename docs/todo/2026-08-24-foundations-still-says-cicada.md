---
status: waiting-on-tony
filed: 2026-08-24
---

# FOUNDATIONS still says CICADA in two places, and one of them should stay

waiting: Two words in `docs/FOUNDATIONS.md` — §6 line 175 and §9 line 257, CICADA
→ locust. **§7 line 197 stays as it is**, because that one is the upstream tool in
a licensing sentence. Exact before/after below; nothing else is asked.

The sixth detector was renamed to `locust` on 2026-08-24
([ADR-0002](../adr/0002-the-sixth-detector-is-called-locust.md)). The glossary,
the README, the viewer and the figures' title maps moved with it.
**`docs/FOUNDATIONS.md` did not, because a session does not edit it** (CLAUDE.md;
[RESET §8](../RESET.md) makes the same point about its own amendments).

So the canonical document and the vocabulary document currently disagree about
what the sixth detector is called, and FOUNDATIONS wins over everything —
including the glossary that changed.

## The exact edit, so this is a decision and not a task

Three occurrences. **Two are our detector and should move; one is the upstream
tool and should not.**

**§6, line 175 — change.** It names our detector's parameter:

> …`GRID_DT_FALLBACK`, `GridDtNotSetWarning` and ~~CICADA's~~ **locust's**
> `imaging_rate_hz = 10.0` are gone.

**§9, line 257 — change.** Same, in the difficulty-axis paragraph:

> …but it exposed that ~~CICADA's~~ **locust's** FAST percentile was a notch too
> loose (7.3 false events/hour…)

**§7, line 197 — LEAVE IT.** This one is the Cossart lab's software in a
licensing sentence, and it is exactly right as written:

> Builds only on permissive upstreams (PySpike BSD semantics, **CICADA** MIT with
> its notice carried in `cicada.py`)…

That is the whole distinction the rename rests on: *CICADA* is the upstream tool
we cite and carry a notice for; *locust* is the detector here. A blanket
find-and-replace would break §7 and quietly weaken the licensing statement.

## Optional, and a separate call

§7 is *Licensing & provenance posture*, and the rename **is** a provenance
decision. A sentence there would put it where a reader looking for licensing
questions would find it:

> The sixth detector is a **modified** port of CICADA — our own events in, rise
> interval rather than transient duration — so it ships under its own name,
> `locust`, with CICADA cited (ADR-0002).

Not proposed as necessary. §7 currently says what we *build on*, and this would
add what we *renamed*; those are adjacent rather than the same, and the ADR
already holds it.

## What is not being asked

Nothing about the identifier. `cicada` remains the module, the function, the
fixtures and the `detector` column in `detections.csv` — see
[the identifier todo](2026-08-24-the-identifier-still-says-cicada.md). FOUNDATIONS
does not mention any of those.
