---
status: open
kind: new-rule-request
raised: 2026-09-02
about: quoted private correspondence reaching the public tree — twice now
---

# A private letter reached this public repo twice, and prose is what was supposed to stop it

CLAUDE.md gained **Other people's words** on 2026-09-02, after the second occurrence.
The first was a PR description on `mariomulansky/PySpike`, live about an hour. The
second was [the April todo](../todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md),
public for **nine days** — four block quotes from a letter Thomas Kreuz wrote to Tony on
2026-04-23. Nobody asked him about either.

**The prose that was supposed to prevent this is what caused it.** The murderboard's
role-2 instruction read *"Where correspondence exists, quote it and date it"*, so a
reviewer doing the right thing by the process doc produced the defect. That line now says
**cite it**, and the sapper argument applies in full: the rule that was carried in prose
got applied by whoever happened to read it, in the direction the prose happened to point.

## What a rule would have to catch

The signature is a **block quote in a tracked file whose provenance is a person, not a
publication**. In both incidents the file itself said so within a few lines:

```
Kreuz ... replied to Tony by email in April.
...
> "for global event identification you should first use ..."
```

A first cut: fire on a markdown block quote (`^>`) within N lines of a
correspondence marker — `by email`, `replied to`, `personal communication`, `his mail`,
`in her mail`, `wrote to (me|Tony)`, `emailed` — anywhere under `docs/**`, `*.md` at the
root, and commit messages via `--staged`.

## Why it is filed rather than written

**The false-positive shape is the whole problem, and it is not obvious which side to err
on.** This tree quotes constantly and legitimately: papers, FOUNDATIONS, the glossary,
Tony's own instructions in conversation, interface2's audit, superseded versions of a
file kept as a block quote for the record — [the April todo now carries three such
quotes](../todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md) in the
very sections that had his removed. A rule loud enough to catch a letter will fire on all
of them.

Three questions a rule-writer has to settle first, and I do not think a session should
settle them alone:

1. **Is Tony's own speech in scope?** This repo quotes him constantly and by design —
   *"please, lets never draw on the raster"* is load-bearing. He is not a third party and
   it is his repo, so presumably not; but the naive matcher cannot tell his voice from a
   correspondent's.
2. **Does a cleared quote need an escape hatch, and what proves clearance?** Kreuz cleared
   the PySpike material on 2026-09-02, so those quotes are legitimately in
   [the filing todo](../todo/2026-08-11-file-pyspike-max-tau-issue.md) today. Some marker
   would have to mean *"asked and answered"* — and a marker a session can add to silence a
   check is a marker a session will add to silence a check.
3. **Where does it fire?** `--staged` catches the next one and is cheap. `--all` would
   have caught this one nine days sooner, which is the actual failure — but it will light
   up the existing tree on day one, and a rule that starts red gets suppressed.

## The cheap half, if the full rule is too blunt

Even a **warn-only** `--all` check, listing every block quote within range of a
correspondence marker, would be worth having. It does not have to be right; it has to
produce a list a person can read in a minute. The nine-day gap existed because **nobody
ever looked**, not because looking was hard — the sweep that found this was a single
`grep` run once the question was asked.
