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
- **Open items leave for `docs/todo/` when the handoff moves here.** This is the rule
  the one above needs in order to be workable, and it was missing.
  `2026-08-25-the-session-hooks.md` arrived carrying four numbered open items. Two were
  fixed within a day, and closing them meant adding twenty-one lines **inside the body**
  of a file whose rule says not to — because a `DONE` marker for item 2 of 4 cannot go in
  the header. The session that did it was right and the rule was wrong: a dated record
  and a live queue are different objects, and that file was being both. Its own closing
  commit named the cost — *"nothing rereads a handoff's own open list"* — and by then
  item 1's reproduce command had quietly stopped reproducing and item 4's byte counts had
  drifted from 14KB to 15KB, with nothing in either case to notice.
  **A todo gets reread**: the session briefing counts `docs/todo/` at every start and
  reads `waiting-on-tony` out loud. A handoff is read once, by whoever was told to.
  Leave a pointer in the handoff so the record still says what was owed.
- **A reproduce block retires with the defect it reproduces.** Commands in a handoff are
  offered as demonstrations of something being wrong; once it is fixed they demonstrate
  the opposite, and a reader who runs one and gets a pass concludes the page is wrong
  about everything else. Strike the line, or say what it does now and why.
- **Rewrite the relative link paths, and only those.** A handoff is written at the
  repo root, so it links `docs/todo/x.md`. From here that resolves to
  `docs/handoffs/docs/todo/x.md` and every one of them is dead. Rewriting
  `](docs/` to `](../` (and `](docs/handoffs/` to `](`) is a mechanical consequence
  of the move, not a correction to the record, so it does not breach the rule above
  — and skipping it is how an archived handoff becomes a wall of dead links.
  `2026-08-20-difficulty-axis-and-synfire.md` sat here with three of them from the
  day this directory was created until 2026-08-26, because the rule said "do not
  edit" and nothing distinguished the two kinds of edit. Say in the header that
  paths were rewritten, so a reader knows the body is otherwise untouched.
- **Retiring the root file is checked, not remembered.** `tests/test_handoff_is_honest.py`
  fails when every PR a root `HANDOFF.md` names has closed. That is what moved the
  2026-08-25 handoff here the same night its PR closed, instead of four days later.

| handoff | written | what it carries |
| --- | --- | --- |
| [the difficulty axis moved, and three guards fired](2026-08-20-difficulty-axis-and-synfire.md) | 2026-08-20 | `bench.REGIMES` re-derived from the export folder; the retune it exposed; three synfire defects, two of which reached published numbers; three open items nobody owns |
| [one hook delivered, one went silent, one waves everything through](2026-08-25-the-session-hooks.md) | 2026-08-25 | the briefing was spilled at 17,568B and 88% of it reached no session — fixed in #306, with the size test fifteen green tests did not have; the board guard that cannot fail in the primary checkout; nothing retiring a spent root `HANDOFF.md`; four open items |
| [the ADR that did not land](2026-08-25-the-adr-that-did-not-land.md) | 2026-08-25 | pipeline state against RESET §7; the promiscuity-scorer and K decisions; four findings nobody fixed, `coact` disagreeing with itself 11% among them. Its in-flight PR #298 was **closed unmerged**, leaving nine files citing an ADR that does not exist — the first handoff retired by a test rather than by someone noticing |
| [the guards that could not fail](2026-08-27-the-guards-that-could-not-fail.md) | 2026-08-27 | four checks that reported success while looking at nothing: a size canary printed where a spill discards it, a board gate matching by substring, a liveness test that skipped in the only place it promised to shout, and the census built to fix the first — which measured nothing on Linux and said all checks pass. Closes items 1–3 of the hook audit, and explains what *"send it upstream"* actually costs. **Written straight into this directory**: it was never a root signal, because nothing in it was half-done. ⚠ **Its "guards" are checks, not guard cells** — for the CFAR sense see the row below |
| [guards, in one place](2026-08-28-guards.md) | 2026-08-28 | everything about `guard_sec` for the spun-off guards session: a knob axis on three detectors, not a tube variant and not a `clamp`; the chronology in which the headline reverses twice — `a15f5e3` said the prediction held, `27e6c8f` says the gain is not flat and `forks.md` §4a is false in the tail; the `C / (C − guard)` inflation that was cancelling the effect it measured; five open decisions, three of them Tony's; and the live deferral whose file **is not on `main`**. **Written straight into this directory**: an assembly, not a signal, and nothing in it is half-done |
