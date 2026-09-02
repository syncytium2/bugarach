---
status: done
kind: new-rule-request
raised: 2026-09-02
resolved: 2026-09-02
about: quoted private correspondence reaching the public tree — twice now
outcome: built, but NOT as a sapper rule — tools/check_quotes.py
---

# A private letter reached this public repo twice, and prose is what was supposed to stop it

## RESOLVED 2026-09-02 — built as `tools/check_quotes.py`, deliberately not as a sapper rule

Tony answered the three questions below: **his own speech is out of scope**, **clearance is
*"ask me. this is rare"*** — so there is no marker and no allowlist a session can reach for
— and it should **gate the commit as well as scan the tree**.

**It is not a sapper rule, and that is the finding.** The property spans lines: in the file
as published, the marker sentence and its block quote are **seven lines apart** with a
paragraph between them. Sapper matches per line by design, and neither line is suspicious
alone — `> "` matches 14 places in this tree that are the repo quoting itself. So the check
lives in [`tools/check_quotes.py`](../../tools/check_quotes.py), which reads whole files,
and is wired the way sapper is: `--selftest`, `--all`, `--staged`, into
`.githooks/pre-commit` and into pytest.

**It gates the commit and not only CI because on a public repo a push IS publication** — by
the time CI runs, the branch is world-readable.

### Two defects in my own first draft, both of which would have made it useless

1. **`WINDOW = 3`, tuned on the tree as it stands — which no longer contains the quotes.**
   Measuring false positives against a corpus with the true positive deleted is survivorship
   bias, and the result did exactly what you would expect: **zero findings on the real file.**
   The value is now set from the incident and the false positives measured afterwards.
2. **The Tony exemption matched his name anywhere.** The sentence introducing the leaked
   quotes was *"…replied to Tony by email in April"* — he is the **recipient**. A bare name
   match read the letter's audience as its author and silenced the one case that mattered.
   It now matches attribution shapes only.

**Both were caught by replaying the actual pre-redaction file, not by the fixtures** — the
fixtures passed throughout, because I wrote them to agree with the design. That replay is
now a permanent test, `test_it_fires_on_the_file_that_actually_leaked`, so a future change
to the window or the exemption that stops catching the real case goes red.

### One thing the check itself taught

The first version fired on `docs/detector_history.md`, where a **correctly formatted
citation** — the parenthesised *(personal communication, April 2026)* this rule asks people
to write — sat above a block quote of interface2's written audit. **A check that punishes
the behaviour it is trying to produce teaches people to stop citing**, which is worse than
the leak. The compliant citation form is now carved out explicitly.

**Green on `main` at the time of writing, and it fires on the April file as published.**
The questions below stand as the record of what had to be decided first.

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
