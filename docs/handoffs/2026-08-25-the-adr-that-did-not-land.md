> ## Moved off the root 2026-08-26. Its one in-flight PR closed, so the signal is spent.
>
> **[PR #298](https://github.com/syncytium2/bugarach/pull/298) was closed without merging**
> at 03:08 UTC, with no comment anywhere saying why. ADR-0003 therefore does not exist on
> `main`; the branch `parity-was-the-inheritance` survives on `origin` at `016df3b`, but
> nothing points at it. This handoff named that PR as the only thing in flight, so the root
> is clear again.
>
> **Do not read the closure as the decision.** The timeline says `closed by syncytium2`,
> and that account is both Tony and every session in this tree, so it does not distinguish
> a deliberate decline from a tidy-up on the way out — it closed one minute after #311
> merged, while another session was shutting down, and the PR was `MERGEABLE`, `CLEAN` and
> 3/3 green at the time.
>
> **The body below is unedited except for relative link paths**, which had to be rewritten
> because the file moved out of the repo root. That is a mechanical consequence of the
> move, not a correction to the record. Two of its claims are now false, and are corrected
> here rather than in place:
>
> - *"It resolves the moment #298 merges."* It did not merge. The handoff named the other
>   branch too — *"if he declines it, the nine references need rewriting instead, and that
>   is a bigger job than the merge"* — and that is the branch we are on.
> - *"What the evening session should do: ask Tony to look at #298."* Overtaken by the
>   closure, whatever the closure meant.
>
> **What is now owed:** nine files on `main` name ADR-0003 as though it exists. Filed as
> [nine files name an ADR that does not exist](../todo/2026-08-26-nine-files-name-an-adr-that-does-not-exist.md),
> `waiting-on-tony` — reopening #298, rehoming the decision in `forks.md` §13, or rewriting
> the citations are all fine, and picking is Tony's, not a session's.
>
> **What retired this file was a test, not a person.** `tests/test_handoff_is_honest.py`
> went red within minutes of #298 closing, and named what closed. That guard shipped in
> #305 hours before it was needed. It is the first time this repo's in-flight signal has
> been retired by something other than somebody happening to notice.

---

# Handoff — 2026-08-25 afternoon, for the evening session

**This file at the root means something is in flight.** One thing is, and it is the
first section. Everything else here is orientation, and when that one thing lands
this file leaves the root — spent, or moved to
[`docs/handoffs/`](README.md) if any of it is still worth reading.

---

## ⚠ In flight: PR #298 is open and `main` already depends on it

**[PR #298](https://github.com/syncytium2/bugarach/pull/298) — ADR-0003, "Parity was
the inheritance, not a standing contract".** It is complete, green, and held open on
purpose because it edits `FOUNDATIONS.md` §2 and Tony had not looked.

**Then I built on it before it landed.** `main` **names ADR-0003 in files that ship
ahead of it** — `src/bugarach/assess.py`, `docs/forks.md` §13, both assess test
modules, and the two-scorers todo. A session reading any of them goes looking for
`docs/adr/0003-*` and finds `0001` and `0002`.

*(This said "nine references" when it was written and the number has already moved —
the set grows every time someone writes about the decision. Naming the files instead
is the version that stays true, and the count was a small instance of exactly the
stale-status defect this handoff spends a section on.)*

Nothing is broken at runtime and no test fails. It is a documentation
inconsistency, it is mine, and it resolves the moment #298 merges.

**What the evening session should do:** ask Tony to look at #298, or ask whether to
merge it. **Do not merge it unasked** — it changes a canonical document, which is
the one class of change this repo reserves for him. If he declines it, the nine
references need rewriting instead, and that is a bigger job than the merge.

The decision it records is not in doubt; he stated it three times in conversation
and the last statement is quoted in the ADR:

> *"We are modifying the six detectors at will to improve performance. We are no
> longer concerned about matching MATLAB performance. Consider the MATLAB versions
> stale."*

---

## Where the pipeline is

`docs/RESET.md` §7 is the order of work. It is on the unmerged `the-reset` branch —
read it there, or from the worktree.

| | | |
|---|---|---|
| 0 | the assessor becomes a pair | ✅ landed 2026-08-24 |
| 1 | the null test — plant nothing, expect zero | ✅ **it leaked; corrected 2026-08-25** |
| 2 | the background axis becomes a reported curve | ✅ **nothing is flat** |
| 3 | fresh assessment + **K decision** | ⛔ Tony |
| 4 | mechanism changes | ⛔ Tony — a second gate turned up, below |
| 5 | the re-fit, then regenerate `docs/learned/` in one pass | after 3 and 4 |
| 6 | the treatment contrast | last |

**Steps 1 and 2 both came back with findings rather than clean bills, and step 1's
is now fixed in code.**

## Two decisions waiting, and they are in the briefing

1. **How does the promiscuity probe enter the score?**
   [`todo/2026-08-25-two-scorers-two-winners-and-nothing-decides.md`](../todo/2026-08-25-two-scorers-two-winners-and-nothing-decides.md).
   Two rules are live in the tree and they pick **opposite winners** for the rate
   detector — multiplicative wins 1 of 7 background points with the probe excluded
   and 5 of 7 with it included. `BenchResult.precision` excludes it;
   `tools/probe_rate_mechanism.py` includes it while its docstring claims to mirror
   `bench.evaluate`. **This blocks the re-fit**, because a campaign is a
   maximisation over a score and two scores give two different sets of shipped
   settings.
2. **K on the approved folder** — RESET §7 item 3, and everything downstream waits
   on it. It is now read off the *corrected* excess, whose curve against K is much
   flatter than the one it replaced (a 19% fall from K=3 to K=6 where the old
   number fell 75%), so the choice matters less than it did and is better posed.

The third, the assessor's excess, **was decided today and is implemented** — do not
re-ask it. The Kreuz letter is still unsent and still only Tony can send it.

## What landed today (2026-08-24 → 25), newest first

| PR | |
|---|---|
| #303 | the excess is selection-corrected, in both implementations |
| #302 | the two routes agree — `rate` 1613/1613 exact |
| #301 | two scorers, two winners; the re-fit is blocked behind it |
| #298 | **OPEN** — ADR-0003, parity retired to a baseline |
| #295 | decision 1 drawn with both options measured |
| #294 | the background is an axis, and the ranking does not survive it |
| #293 | three rasters with the assessor's calls above them |
| #291 | the null test — plant nothing, expect zero |
| #290 | MAHDCE in the glossary, marked as Tony's coinage |
| #289 | SPIKE-synch off in the browser, off-not-gone |
| #288 | the 52% headline withdrawn |

**The site is deployed and current** at `bugarach.tonydefazio.com`, built from
`3fc69bc`, audited on the far side. It went out twice — the second time because
#303 changed the viewer minutes after the first.

## Things I found and did not fix

- **`coact` disagrees with itself 11% of the time on the same data**, at a different
  surrogate seed. A property of the detector, not of any route: a single `coact`
  event list is about a tenth arbitrary, and nothing downstream reports it. Measured
  by `tools/sampling_floor.py`. Bigger than anything the route comparison found.
- **Disabling SPIKE-synch cost the route comparison an anchor.** `rate` and `sync`
  are the only detectors drawing no random numbers — the only two where *"agrees
  exactly"* is a meaningful claim. One is thinner than two.
- **Four of six operating points are inherited defaults**, not measured optima
  (`bench.OPERATING_POINTS`, read the `source` fields), so the bake-off ranking
  partly tracks calibration status rather than detector quality.
- **`docs/learned/` is a calibration behind** and now also predates the corrected
  excess. RESET §5 wants it regenerated **in one pass**; a half-regenerated folder
  mixes two calibrations with nothing saying which is which.

## A pattern worth carrying into the evening

Every diagnostic this week returned the same shape: **an instrument that gives two
answers depending on a convention nobody chose.** The null's selection rule, the
background axis, the promiscuity scorer, and `coact` against itself. Four
instruments, four unchosen conventions, and only the first is now settled.

That suggests the re-fit's real prerequisite is settling conventions rather than
fixing mechanisms — which is not what RESET §7's ordering assumes, and may be worth
saying to Tony.

## Housekeeping for whoever picks this up

- **70 open todos**, most written before the reset. Read as history, not a queue.
  Two are `waiting-on-tony` and the session briefing names them at startup.
- **PRs #304, #292, #270, #53, #50** are open besides #298; none is webapp work.
  #270 is red and stale from 2026-08-24 and wants a rebase.
- Board: `../bugarach-worktrees/SESSIONS.md`. Every block opened for this work is
  closed and every shared resource released — the viewer, the darkroom, the deploy,
  port 5096.
- Suite on `main`: **1,356 collected**, sapper clear.

---

## Amended 2026-08-25 evening — the channel this file depends on was broken

This handoff was written to be read at session start. **It could not have been.**

`tools/session_briefing.sh` is the only code that reads `HANDOFF.md`, and it was
emitting 17,568B — a `SessionStart` hook that size is not trimmed, it is spilled to
a file and replaced by a ~2KB preview. The in-flight alarm sat at byte **17,569**,
dead last. Six alarms were behind the cut, including the two `waiting-on-tony` items
this file asks Tony to settle.

Fixed and on `main`: **#306** reorders so the alarms lead, budgets the bulk at 9,000B
and prints a size canary (17,439B → 8,068B); **#307** re-vendored a stale murderboard;
**#309** is the write-up, [`docs/handoffs/2026-08-25-the-session-hooks.md`](2026-08-25-the-session-hooks.md),
which carries four open items nobody owns.

Three things in this file were also amended rather than left standing:

- The ADR-0003 mention in the null-leak todo is **not** a relative link. `docs/adr/0003-*`
  is not on `main` until #298 lands, so a link there renders as a dead click — this
  handoff was about to add a tenth reference to that ADR and make it the only broken one.
- The open-PR list above omitted #304, which was open when this was written. That is the
  same stale-status defect the file's own body catalogues.
- **This file is now machine-checked.** `tests/test_handoff_is_honest.py` asserts that a
  root handoff names the PR it claims is in flight, and that at least one of them is still
  open. When #298 closes, that test goes red and says so — which is the retirement
  mechanism `docs/handoffs/README.md` was missing when its predecessor sat here for four
  days saying *"nothing is half-done"*.
