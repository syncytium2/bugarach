# Handoff — 2026-08-25 afternoon, for the evening session

**This file at the root means something is in flight.** One thing is, and it is the
first section. Everything else here is orientation, and when that one thing lands
this file leaves the root — spent, or moved to
[`docs/handoffs/`](docs/handoffs/README.md) if any of it is still worth reading.

---

## ⚠ In flight: PR #298 is open and `main` already depends on it

**[PR #298](https://github.com/syncytium2/bugarach/pull/298) — ADR-0003, "Parity was
the inheritance, not a standing contract".** It is complete, green, and held open on
purpose because it edits `FOUNDATIONS.md` §2 and Tony had not looked.

**Then I built on it before it landed.** `main` now carries **nine references to
ADR-0003 in a file that does not exist on `main`** — `src/bugarach/assess.py`,
`docs/forks.md` §13, both assess test modules, and the two-scorers todo. A session
reading any of them goes looking for `docs/adr/0003-*` and finds `0001` and `0002`.

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
   [`todo/2026-08-25-two-scorers-two-winners-and-nothing-decides.md`](docs/todo/2026-08-25-two-scorers-two-winners-and-nothing-decides.md).
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

- **71 open todos**, most written before the reset. Read as history, not a queue.
- **PRs #292, #270, #53, #50** are open and none is webapp work; #270 is red and
  stale from 2026-08-24 and wants a rebase.
- Board: `../bugarach-worktrees/SESSIONS.md`. Every block I opened today is closed
  and every shared resource released — the viewer, the darkroom, the deploy, port
  5096.
- Suite on `main`: **1,333 passed, 13 skipped, no xfail.** sapper clear.
