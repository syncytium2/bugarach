# Handoffs, after they stop being handoffs

**The root is the signal. This directory is the record.**

A session stopping mid-task writes `HANDOFF-<slug>.md` **at the repo root**, so
that `ls HANDOFF*.md` answers *"is anything in flight?"* without opening a file
(CLAUDE.md, "Repo management"). The check only works if the answer is honest, so
a handoff at the root means **work is genuinely in flight** and nothing else.

**When the work lands, the file leaves the root.** Its two jobs come apart at
that moment: the *signal* is spent, and the *content* usually is not — a handoff
is where a session writes down what it learned in the shape another session will
trip over, and that outlives the branch it was describing.

So:

- **Open items retired, nothing durable left** → delete it. That is what the
  handoffs themselves tell you to do, and it is right when the content is
  genuinely spent.
- **Anything still worth reading** → move it here, dated, and update whatever
  pointed at it. Deleting it would be the only lossy option.

## Why this directory exists at all

`HANDOFF-difficulty-axis-and-synfire.md` sat at the root from 2026-08-20 to
2026-08-24 while its own first line said *"Everything below is merged on `main`.
No branch is waiting, nothing is half-done."* For four days the in-flight check
returned a false positive, and the session that wrote it had done nothing wrong —
it had followed the rule as written, which offered **delete or leave**, and its
content was too useful to delete. Three of its items are still open and unowned.

The rule was missing a third option. This is it.

## Convention

- `NNNN-NN-NN-<slug>.md` — the date the handoff was **written**, not the date it
  was moved. The one below keeps its original title line and gains a header
  saying where it came from and when it stopped being live.
- **Do not edit the body.** A handoff is a record of what one session knew at one
  moment; correcting it in place turns a dated account into an undated claim. If
  something in it has since been settled, say so in the header.

| handoff | written | what it carries |
| --- | --- | --- |
| [the difficulty axis moved, and three guards fired](2026-08-20-difficulty-axis-and-synfire.md) | 2026-08-20 | `bench.REGIMES` re-derived from the export folder; the retune it exposed; three synfire defects, two of which reached published numbers; three open items nobody owns |
| [one hook delivered, one went silent, one waves everything through](2026-08-25-the-session-hooks.md) | 2026-08-25 | the briefing was spilled at 17,568B and 88% of it reached no session — fixed in #306, with the size test fifteen green tests did not have; the board guard that cannot fail in the primary checkout; nothing retiring a spent root `HANDOFF.md`; four open items |
