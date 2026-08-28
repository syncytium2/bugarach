---
status: open
filed: 2026-08-28
---

# Numbers derive from a store and cannot drift; claims are hand-copied and do

> **Open, not `waiting-on-tony`, and the status is the finding's own subject.**
> This ends in a decision only Tony can take, so the status looks wrong — but a
> `waiting-on-tony` item prints its action line in **every** session briefing, and
> the briefing has no room. Marked that way it took CI to **9,124B against a
> 9,000B budget**, degrading the whole thing to TERSE: the FOUNDATIONS extract
> stops arriving, which is a worse outcome than this file being one click less
> prominent.
>
> [`2026-08-27-the-bakeoff-reference-is-thread-count-bound.md`](2026-08-27-the-bakeoff-reference-is-thread-count-bound.md)
> made the same choice for the same reason two days ago and said so in its own
> header. **Twice is a property of the block, not an accident** — and it is a small
> instance of what this file is about: the briefing is a hand-maintained budget
> where the thing that matters (does the fact arrive?) is not derivable from the
> thing being edited (how long is my sentence?).

> **Not murderboarded** — a structural observation about this repo, every count
> reproducible by the greps quoted below.

## The observation, in two numbers

`docs/learned/learned_detector.src.html` contains:

- **122** `{{N:store:path}}` number tokens
- **0** references to `ADR-0002` or `FOUNDATIONS`

Every **number** on that page is resolved from a JSON store at build time and cannot
go stale. Every **claim** on it is prose someone typed. `tools/build_learned_report.py`
says why the numbers work that way, in its own source:

> *"a superseding notice carrying its own stale transcription of the newer result would
> be the exact failure this substitution exists to stop"*

That reasoning was never extended to sentences.

## The root elements exist. Nothing derives from them.

ADR-0002 records, accepted by Tony on 2026-08-24, that the sixth detector is called
**locust** and what it is a port of. FOUNDATIONS is canonical and cites it. And yet:

- **14+ files** outside `reviews/`, `todo/`, `handoffs/` and built HTML carry a claim
  about locust or CICADA (`grep -rl CICADA docs tools src README.md`).
- `tools/build_site.py` mentions ADR-0002 **4 times, all in comments** — it does not
  read it.
- `learned_detector.src.html` cites it **0 times**.

So an ADR is a decision filed where nothing consults it at build time, and FOUNDATIONS
is canonical but **byte-budgeted** — §9 is printed in every session briefing, which caps
what it can hold and forces it to be a list of signposts rather than a store of
assertions. On 2026-08-28 a 1,292-byte addition to §9 had to be cut to 201 bytes for
exactly that reason.

## What it cost on one day

The claim *"locust is CICADA's method"* changed **four times on 2026-08-28**:

1. It was on the public front page, in bold, beside this project's own benchmark numbers.
2. **#360** removed it after an eleven-role murderboard.
3. **#363** caught the same claim reasserted in a handoff **six minutes later**.
4. The unmerged `learned-detector-page` branch still carried it and would have been the
   third landing.

And then the *replacement* — reviewed, murderboarded — turned out to be wrong too: it
said the port *"replaces CICADA's active-duration model"*, putting the change in the
algorithm. It is not there. The exporter sets the duration and declares it in
`width_def`; the algorithm is untouched (`export_folder_spec.md`, width section).

**Review caught the wrong claim about the laboratory and could not catch the wrong claim
about the mechanism**, because nobody in that loop knew the export step existed. Eleven
roles do not substitute for a single derivable source.

## The shape of a fix, if it is wanted

A **claims store**, addressed by the token machinery that already exists:

```json
{ "locust": { "origin": "A partial port of an older version of the Cossart lab's
   implementation. Skips the per-cell transient-detection stage; the duration it
   receives is set by the exporter, not by the port." } }
```

Pages write `{{CLAIM:locust.origin}}`. They cannot disagree, because there is one
string. Changing your mind is one edit and a rebuild.

`build_learned_report.py` already loads arbitrary JSON stores by letter, so the plumbing
exists and this is a store and a token prefix, not a new system.

**What it does not solve, and should be said plainly wherever it lands:** a token keeps
a *sentence* current, not a *judgement*. *"A tie at the top"* is a claim about numbers
that no substitution can re-evaluate. This closes transcription drift, which is what bit
four times in one day; it does not close staleness of reasoning.

**Also worth deciding at the same time:** ADR-0003 does not exist while **nine files cite
it**, because PR #298 was closed unmerged
([`2026-08-26-nine-files-name-an-adr-that-does-not-exist.md`](2026-08-26-nine-files-name-an-adr-that-does-not-exist.md)).
A root element with a hole in its numbering is part of why it does not feel like one.
