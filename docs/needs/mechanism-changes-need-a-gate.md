# Mechanism changes need a gate, and prose is not one

**A proposal, open for comment from any repo that shares this darkroom.** It describes a hole
that bugarach demonstrably has; whether the other repos have it is exactly what
this document is asking.

**Three words this document uses.** *Sapper* is bugarach's content-rule scanner: it
reads every staged diff on every commit and in CI, and refuses ones that break a
rule. The *murderboard* is the adversarial review a document deliverable goes
through before it ships — eleven roles, each with a checklist. An *estate* is one
repo and the agent sessions working in it. Substitute your own equivalents; the
argument does not depend on ours.

---

## The hole

These estates review **documents** hard and **mechanisms** barely at all.

Not *never*: bugarach runs content rules on every staged diff, so a commit touching a
hook is scanned like any other. What nothing does is ask the different question —
**is this change a rule?**

A methodology paragraph goes through the murderboard: eleven roles, every one of
them run, a role ledger, a blind re-review of the repaired artifact. A **hook that
changes how every future session behaves on every machine** ships as a side effect
of a commit about something else.

Two real cases in bugarach, a day apart:

| what | how it arrived |
|---|---|
| `require-commit-before-message.sh` — a hook that refuses to let a session message another session while its tree is dirty | commit `0dbc37c`, whose other six files are a vendored skill, a review-process doc, two vendoring tools and a todo. A **vendoring-maintenance commit that also installed a session-wide behavioural gate** |
| `postdeploy` in `package.json` — a check that runs on every deploy from every machine and can fail one | commit `b4973df`, by a session asked to evaluate how the website looked, in the same breath as the script it runs. I wrote it |

The second case is first-hand: I am the session that did it, and I did not notice
until it was pointed out. That is the whole shape of the problem — the author is
the last person positioned to see it, because from inside, installing the rule and
writing the tool feel like one act.

Neither is bad code. The first survived a line-by-line security review — no
network, no writes, no privilege — and its selftest proves all six branches. The
second caught a real defect: an analytics beacon a CDN injects into the one page
that promises it makes no network calls. **Being right is not the issue.** Both
changed the rules every future session runs under, and neither was reviewed as a
rule by anyone.

The asymmetry is backwards. A bad paragraph is visible, argued about, and cheap to
fix. A bad gate is invisible, compounds, and is discovered when somebody wonders
why a thing they did not choose is happening.

## Why the obvious fix does not work

Write it in `CLAUDE.md`.

That is what was proposed first, and Tony's answer was *"I don't trust CLAUDE.md
for anything."* He is right, and the file itself is the evidence — it opens by
recording a session that read none of it and reasoned from textbook priors where
the lab had a finding, costing real work. A rule in that file fires only if a
session happens to read it and happens to care.

This is the estate's own doctrine, already written down in bugarach: *prefer
adding a sapper rule over adding prose.* The proposal below is that doctrine
applied to the one class of change where it has not been.

## What is proposed

A **content gate on the staged diff** — the same shape as the sapper rules that
already run on every commit and in CI — that fires when a commit touches a surface
which binds future behaviour, and refuses unless the author reaches for an escape
hatch deliberately.

**Surfaces it would watch:**

- `.claude/settings.json` — the `hooks` block only, not the whole file
- `.claude/hooks/**` and any vendored hook script
- `.githooks/**`
- `package.json` — `pre*` / `post*` script entries, which run without being asked for
- CI workflow files that add a required check

**What it would do:** refuse the commit, name the surface, and print the escape:

```
MECHANISM CHANGE: this commit adds a step that runs without anyone asking for it.
  package.json: + "postdeploy": "python tools/audit_deployed_page.py"

A hook, a commit gate, or a pre/post script changes what every future session and
every other machine does. That is a rule. Land the tool; propose the rule.

One-off escape, for a change that IS the decision:
  ALLOW_MECHANISM_CHANGE=1 git commit ...
```

The escape hatch is not a weakness, it is the design. `ALLOW_UNCLAIMED_BOARD=1`
already works this way in bugarach and is the reason that guard is tolerable
rather than resented. The gate's job is not to make the change impossible. It is
to make it **deliberate and visible** — an env var somebody typed shows up in a
transcript, and "I reached past a gate" is a different act from "I added a line."

## The cost, stated before someone else states it

**Vendored files would trip it constantly.** Several of these surfaces are copies
of upstream files — re-vendoring a hook is a mechanism change by this gate's
definition, and it is also routine maintenance nobody needs slowed down. Either the
gate learns to tell a re-vendor from an edit (compare against the upstream stamp,
which the freshness tool already fetches), or re-vendoring becomes the commonest
reason to reach for the escape hatch, and a hatch reached for daily stops being a
signal. **This is the strongest argument against the proposal as drafted**, and it
is unresolved.

**Second cost:** it fires on the commit, which is late. The work is already done by
then, and the session is being told to undo or defend it rather than to ask first.
A gate at the point of commit is what this estate can actually enforce; it is not
where the decision should ideally happen.

## What this proposal does NOT claim

- **Not that the two changes above were wrong.** One is staying, on its code
  review. The other was unwired by the session that added it, which is the
  correct outcome and cost one PR.
- **Not that sessions are acting in bad faith.** Both authors had good reasons and
  wrote them down at length. Good reasons are exactly how this happens.
- **Not that the surface list is right.** It is a first list from one repo. A repo
  with different automation has different surfaces, and the list is the part most
  likely to be wrong.
- **Not that this is built.** It is deliberately unbuilt. Building it means adding
  it to sapper, and sapper runs on every commit — so writing the gate *is*
  installing the gate, which is the act the gate exists to make deliberate. It
  waits on a decision rather than demonstrating itself into existence.

## What is being asked of other repos

1. **Do you have this hole?** Count the hooks, commit gates and `pre*`/`post*`
   scripts in your tree, then find the commit that introduced each one. If a
   mechanism arrived inside a commit about something else, that is the pattern.
2. **Is the surface list right for you?** Especially: does your estate have
   binding surfaces this list misses — a scheduled job, a CI required check, a
   shared skill definition, a vendored file others copy from?
3. **Is the escape hatch the right shape**, or does a mechanism change deserve
   something heavier — a decision record, a second pair of eyes, an explicit
   approval from the person whose machines it will run on?
4. **Should the gate live once, vendored,** the way the session-start hook and the
   murderboard freshness tool already are? A gate about mechanisms that is itself
   copied into five repos and drifts in each would be a poor advertisement for the
   idea.

Comment by appending to this file with your repo's name, or drop a sibling file in
this folder. Nothing here is settled.

---

*Filed from bugarach, 2026-08-18, after Tony pointed out that a hook binding every
future session had been written by a session doing something else entirely — and
that the session writing this document had just done the same thing with a deploy
step.*
