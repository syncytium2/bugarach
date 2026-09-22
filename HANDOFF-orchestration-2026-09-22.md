# Handoff: where the program stands after 2026-09-22, and what to pick up

> ⚠ **This file covers the orchestration thread — the ruling queue, the producer exchange and
> the day's corrections.** The other root handoffs are other threads and are NOT superseded by
> it. Delete only your own file.

**Written 2026-09-22 by a cloud session** (claude.ai/code, container `vm`) at Tony's request,
with compaction imminent. That session had **no export folder, no venv, no GPU and no darkroom
mount**: everything below is a read of the tree, the darkroom over the Dropbox connector, and
GitHub. Nothing was measured on this machine.

> **Not murderboarded** — working material for a session in this tree, on the same footing as
> the slow-bench handoff. Nothing here is for an outside reader.
>
> **Corrected 2026-09-22, evening, by a later cloud session** after Tony reviewed it and closed the
> sessions it named. Every correction is marked *(corrected)* in place; the rest is as written.

---

## Read these three first

1. [`docs/decisions_pending.md`](docs/decisions_pending.md) — **the ruling queue**, ten items,
   what each blocks and what to do absent a ruling. It is the page the briefing's one
   `waiting-on-tony` entry points at.
2. [`docs/goals/README.md`](docs/goals/README.md) — four goals now; goal 4 was added today.
3. [`docs/handoffs/2026-09-21-slow-bench.md`](docs/handoffs/2026-09-21-slow-bench.md), the
   *Current state* section at the top — WSMIP064's own account of the slow thread, written at the
   end of its run. *(corrected: retired from the root on 2026-09-22, nothing in it being in
   flight; its header says where each open item went.)*

## The one thing on the critical path

**Item 2, the jitter constant. It is ready to rule and it has no remaining preconditions.**

`tools/measure_jitter_correlogram.py` (#718) measured onset jitter without bins: **fast 0.106 s
[0.091, 0.120], slow 0.135 s [0.126, 0.149]**, against bench constants of **0.36 s and 0.30 s**.
Both old values tracked bin ÷ √12 — the instrument was measuring its own coincidence bin, and the
2026-09-17 re-measure "confirmed" it with the same instrument at the same bin. The measurement is
on `main`; **no constant moved with it**, which is why it is a ruling and not a change.

Tony asked, correctly, what else the simulations absorb and whether it was measured as carelessly.
That audit is done — [`docs/todo/2026-09-22-what-else-came-from-the-clustering-instrument.md`](docs/todo/2026-09-22-what-else-came-from-the-clustering-instrument.md):

- **Well measured:** `rate_shape` (ML Gamma over 81 windows / 2,643 ROIs, and it predicts the 35%
  silent-ROI figure it was never fitted to), the rate percentiles, `n_roi`.
- **Same instrument as the jitter:** `participation` — but **it was swept across five bins and
  held** (fast 0.19 at every bin, slow 0.37–0.38 from 0.5 s to 3 s). The recruitment constant
  survives the test the timing constant failed.
- **Residuals, follow-ups not blockers:** the flat range stops at 3 s where the bins run to 5;
  participation has no null counterpart while the jitter has one (`jit_excess`) that the bench
  does not use; the burst shapes are fitted per scale and multiplied, so the coarse end is short
  (variance/mean 4.44 simulated against 5.69 real at 300 s); and the simulators' long-lag level
  is ≈0.75 excess at 5–10 s against about 0.1 in real data, which nobody has looked at.

**The session that will act on it is idle on WSMIP064** — VS Code, title *"Sweep timing and burst
configuration"*, blocked since this morning with the choice in its own status line: adopt
0.106/0.135, keep 0.36/0.30, or ask the producer about same-frame artefacts first. Its checkout
was at `964e3ab`, well behind; **it must pull before it commits.**
*(corrected: that session has since been archived. Whoever acts on the ruling starts fresh from
`main`.)*

## The meeting has happened, which unblocks two filed items

Several documents say "after the 2026-09-22 meeting". **That meeting was the morning of
2026-09-22**, so these are live now, not pending:

- **Bench participation 0.18 → 0.19** — [`docs/todo/2026-09-21-bench-participation-to-0-19-after-the-meeting.md`](docs/todo/2026-09-21-bench-participation-to-0-19-after-the-meeting.md).
  Schedule it in the same overnight pass as the jitter: both move the same bench.
- **The one stream-aware bench** — [`docs/todo/2026-09-21-one-stream-aware-bench.md`](docs/todo/2026-09-21-one-stream-aware-bench.md),
  which deletes `bench_slow.py` and the stopgap measurement tool. Goal 4 would otherwise add a
  **third** copy of the scoring path, so this wants doing before that starts.

*(corrected)* **Two things this section did not say.** First, **what the meeting decided is not
recorded anywhere in the tree.** The 0.19 todo was held *so the meeting could discuss it*, and a
meeting having happened is not the same as its approving the change, so confirm with Tony before
moving the constant. Second, **the two items touch the same files**: the constant changes edit
`bench.py` and `bench_slow.py`, and the one-bench rewrite replaces both. Do the constant changes
first, in the files as they stand, and let the rewrite carry the new values across; the other order
makes the rewrite's tests pin values about to change. Tying 0.19 to the jitter's overnight pass
also holds a change that needs no ruling behind one that does, so it need not wait for item 2.

A relative date in a document goes stale silently. If you find more of them, fix them where you
find them.

## What landed today, in order

| PR | what |
|---|---|
| #706 | the slow bench's clobber list — six places a slow run would overwrite a fast result |
| #720, #722 | **the ruling queue** and its one `waiting-on-tony` entry |
| #723 | **goal 4**: fast and slow as one stream, with the membership question that precedes it |
| #725 | the pinning screen had run three times; the pointer file said it never had |
| #726 | the ask went to interface2 as a GitHub issue |
| #728 | ⚠ **superseded the same day** — CoactDetect onsets as bin edges. Wrong for the run it was about |
| #730 | the producer answered in four hours: the frames pin, the ROIs do not |
| #731 | the bench-constants audit, and its own correction |
| #732 | what the full-cohort rasters actually show |

## The producer exchange — closed, and what it leaves

[syncytium2/interface2#1](https://github.com/syncytium2/interface2/issues/1) is **closed**. They
ran the geometric test (`tools/check_roi_pinning.m`, 4,000 frames per slice) on the three DI
candidates: **`20250926_237` shows no pinned frames; `20260629_314` pins in 44 and `20260630_325`
in one, and in both the flooded patch lies where no ROI or penumbra sits.** The frames pin, the
ROIs do not. Their caveat travels with it: that test undercounts (2 of 4 census ROIs on the
known-pinned control), so what carries the conclusion is two tests sharing no code agreeing. The
answer is in `current_export.toml`'s note and the `MILESTONES.md` row — **the pointer file, because
leaving a correction out of it is what cost a week the first time.**

**Ours and untouched:** group and imaging day are perfectly aliased in this corpus — 84 recordings
across 48 dates, no date holding two groups. They said plainly they have not checked it and it is
not theirs to check. Also ours: **nothing in this tree reads `moco_pinned_excluded.tsv`**, and the
shared-gap question for our surrogate is untested — clipping removes the events but leaves the
hole, so a whole-trace circular shift can still manufacture coincidence at the offset.

## Cheapest unblock on the board

**Item 4, the fireflies export contract.** Another team is frozen: they set no axis ranges until
it is agreed. Accept their A, B and D as proposed, keep the per-cohort file as canonical (windows
are ours, their own scope stop), and adopt the `measure_version` column **before** the
`core_span_sec` change rather than after. Two answers are needed from Tony and nobody else:

1. **Zero width** — 443 calls have `core_span_sec == 0` while `amplitude` computes as if the width
   were one frame. Which is the rule?
2. **NA** — 609 calls have `amplitude` NA, 326 with `core_span_sec` NA too. No core, too small to
   measure, or something else?

The proposal is `FORMAT_CHANGE_from_fireflies.md` in
`<darkroom>/bugarach/2026-09-21-full-cohort-default/`.

## The raster finding, and three misreadings to not repeat

Tony saw that detections on the DI senktide rasters did not line up with the events or with each
other. Measured against the run's own files
([`docs/todo/2026-09-22-what-the-full-cohort-rasters-show.md`](docs/todo/2026-09-22-what-the-full-cohort-rasters-show.md)):

- **CoactDetect ran sliding there and its onsets sit on member events** (median 0.00 s).
- **Binned SCE floats by a median 3.5 s** — its 10 s bin edge — and **locust by +0.5 s fast and
  +1.1 s slow**, peak versus half-rise. Neither was in that figure.
- The two lanes disagree because **chorus fires where coact does not** (19 calls against 12 on one
  panel), not because either is drawn wrong.
- **The page's x-axis is minutes from senktide onset and does not say so.** That unlabelled origin
  produced three wrong readings in twenty minutes: that a screengrab was the whole recording, that
  a panel rendered empty, and that the drawn marks did not match the file. Label the origin.

## The fleet, and how to see it

`ListAgents` is empty from a cloud session — it only reaches this machine. Use
`mcp__Claude_Code_Remote__list_sessions` with `mine: true` to see the whole fleet; it shows each
session's `post_turn_summary`, which is where the blocked ones announce themselves. **It does not
record which machine a session is on** — that has to come from a run record or the board, and
assuming it is how this session put the jitter session on the wrong workstation for an hour.

*(corrected)* **As of 2026-09-22 evening, Tony has closed the sessions this paragraph listed.** The
jitter session and the cloud session blocked on the dataset default are archived. The paragraph
answered that session's question for it (*"yes, confirmed 2026-09-21"*), which the dataset rule
forbids: the default is confirmed **by Tony, in each session**, and never relayed from another one.
**One result is still not in the repo:** the crowded-allowance sweep on WSMIP064 (*"sweep complete;
4 rows need top-up pass; findings doc unwritten"*, session titled *"Handoff from machine 064"*).
Until that session pushes its output and a findings note, the sweep exists only on that machine;
the tooling it needs is [#682](https://github.com/syncytium2/bugarach/pull/682).

## Housekeeping a new session inherits

- **The machine-local board** is over budget: this container's raw dump reached 12.5 KB against
  8,000 B. *(corrected: that board was in the writing session's own cloud container, which is gone.
  The machine-local board is per machine, so this item describes nothing a new session will find.
  The point about archiving still holds for any board that does grow.)* Archiving finished blocks under `## Archive` makes the file navigable but **does not
  shrink the pre-trim dump** — the dump is measured on the file, and nothing is deleted. If size
  is the goal, the archive has to be a separate file.
- **`docs/SESSIONS.md` is 207 KB across 121 blocks, 92 of them DONE or RELEASED.** Same caveat.
  Worth a pass, not as a five-minute job.
- **Machine identity on the board has nine spellings** for four machines — `Mac` (66 blocks),
  `Tonys-MacBook-Pro` (21), `065` (13), `mac` (4), `WSMIP065`/`WSMIP064`/`WSMIP-win` (2 each),
  `vm`, and one literal `<machine>` placeholder. interface2's `tools/session_identity.sh` is the
  solved version (machine = the box normalised, session = the branch, address = `065/branch`) and
  is **not vendored here**. It stalls because it has no answer for the Mac or a cloud container,
  which is 91 of those 119 blocks. That naming decision is Tony's and unmade.
- **Branch `claude/sleepy-noether-xyvx59`** is this session's, one commit, already merged as #706.
  Safe to delete. *(corrected: already gone from the remote.)*

## What this session did not do

No code. No measurement. No darkroom write. No murderboard run — every document it produced is
working material in this tree, and the one artifact that went outside (interface2#1) was
claim-checked by hand against named files rather than through the roster.
