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
| [the guards that could not fail](2026-08-27-the-guards-that-could-not-fail.md) | 2026-08-27 | four checks that reported success while looking at nothing: a size canary printed where a spill discards it, a board gate matching by substring, a liveness test that skipped in the only place it promised to shout, and the census built to fix the first — which measured nothing on Linux and said all checks pass. Closes items 1–3 of the hook audit, and explains what *"send it upstream"* actually costs. **Written straight into this directory**: it was never a root signal, because nothing in it was half-done. ⚠ **Its "guards" are checks, not guard cells** — for the CFAR sense see the bottom row |
| [what #351 changes under the deploy](2026-08-28-what-351-changes-under-the-deploy.md) | 2026-08-28 | for whoever lifts the [deploy hold](../DEPLOY_HOLD.md). `53b1d62` is not a content change: it swaps how all seventeen long loops schedule themselves — only four in the sweep — adds the page's first `beforeunload` prompt, and stamps fifty inputs against autofill. Carries the measured background cost that motivated the swap (a 20-setting LoCo sweep: 10 s in front, ~25 min if left in a hidden tab), the residual `⚠` that the swap's full effect **cannot** be measured under automation and needs one look at the live page, two traps that bite any deploy session regardless, and a retraction of a wrong test count already merged into PR #351's message. **Also carries the combined-viewer drive**, which closes the gap [deploy notes 2](2026-08-28-deploy-notes-2.md) named: all three queued viewer commits built, served and walked together on `a74395b` — clean, and two of the three turn out to be lab-gated and ship inert to a public reader, while the third's only ungated hunk leaves the simulated folder hash-identical. **Written straight into this directory** — nothing in it is half-done |
| [the bench moved under the deploy](2026-08-28-the-bench-moved-under-the-deploy.md) | 2026-08-28 | the **third** deploy note, and the only one about a change that is *not* queued: the bench's background stopped being flat and the scoring tolerance moved 1.5 → 2.5 s, so every published F1 predates both — and `hero.png` is rendered from `src/bugarach`, so the front page's figure moves with no viewer commit to explain it. Carries the paired 12-seed deltas, the coact grid re-fit, why the regime budget did **not** need expanding (rate's swing was the tolerance, 0.103 → 0.003), and the bug the note itself found: the published figure was still scoring at 1.5 s while the bench scored at 2.5. Branch is **red on purpose** — three tests encode a finding about the background axis that Tony has not ruled on, and re-baselining them would delete it |
| [the winner stopped changing](2026-08-28-the-winner-stopped-changing.md) | 2026-08-28 | those three tests, as a result instead of a chore. The bench's background-rate axis used to reorder the detectors — one moved four places — and on the fitted background coact leads across it. Measured rather than argued: own-range 0.185 → 0.136, between-detector spread 0.117 → 0.098, so **the axis still discriminates** and the reordering was living in a crowded low-F1 tail the *flat* field manufactured at the busy end. Carries what a rewrite must keep (a single F1 without its background is still not a result), three options in the order to try them, and the seed-count caveat that makes "wins everywhere" vs "nearly everywhere" noise at n=6 |
| [deploy notes 2 — the live page is wrong about another lab](2026-08-28-deploy-notes-2.md) | 2026-08-28 | **the companion to the row above**, covering the other queued commits. The public page tells readers `locust` **is** CICADA's method and, four sentences later, that no method from the literature has been run here; both are bold and they cannot both hold. The fix `ed5e02e` is queued behind the deploy hold, whose own text says an actively misleading page is a reason to lift deliberately rather than route around — raised for a person, not acted on. Also: **three sessions have edited `raster_viewer.html` since the last deploy** and nobody has driven the combination |
| [locust is not CICADA, and four things this session got wrong](2026-08-28-locust-is-not-cicada-and-four-things-i-got-wrong.md) | 2026-08-28 | the derivation chain is validated only at its last link — `gen_ref_cicada.m` builds the 1e-9 fixture from interface2's own port, so nothing compares anything to the Cossart source, and interface2 **parked** that port for over-detecting. Established that it came from their **code** (`sce_stats_utils.py`, both functions verified) and that the citation is correct. Carries the live page still saying `locust` **is** CICADA's method, four self-corrections in one session with the pattern they share, the data rules Tony gave, and the hazard that **a worktree's `pytest` imports the primary checkout's `src`** — which had already put two wrong test counts into PR messages |
| [guards, in one place](2026-08-28-guards.md) | 2026-08-28 | everything about `guard_sec` for the spun-off guards session: a knob axis on three detectors, not a tube variant and not a `clamp`; the chronology in which the headline reverses twice — `a15f5e3` said the prediction held, `27e6c8f` says the gain is not flat and `forks.md` §4a is false in the tail; the `C / (C − guard)` inflation that was cancelling the effect it measured; and five open decisions, three of them Tony's. Its deferral lived on an unmerged branch when it was drafted, for no reason but an unarmed auto-merge; **#304 landed the same day** and the page links it. **Written straight into this directory**: an assembly, not a signal, and nothing in it is half-done |
