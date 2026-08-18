# Murderboard run — docs/todo/2026-08-11-file-pyspike-max-tau-issue.md

- upstream:  syncytium2/murderboard @ 783501e
- vendored:  783501e
- freshness: current
- artifact:  docs/todo/2026-08-11-file-pyspike-max-tau-issue.md (a02dd1d -> 9fcb8bc)
- roles:     11 of 11 run
- rounds:    14 blind verify rounds to clean

The deliverable is the "Draft issue text" section, to be posted as a public GitHub
issue on `mariomulansky/PySpike`. Nothing has been posted; Tony gates it.

## How this run deviated, and why

The first pass spawned all 11 roles as parallel subagents. Seven of them
(1, 2, 3, 4, 6, 7, 10) died mid-run on a monthly spend limit; four (5, 8, 9, 11)
returned. The seven that died were re-run in-thread as a single-pass self-review
walking each role's checklist — the fallback the process specifies for scaling
down — and every subsequent round was a full 11-role blind pass by a fresh
reviewer with no knowledge of prior findings. The ledger below reports the
cumulative result across all rounds.

## Role ledger

| # | Role | Findings |
|---|---|---|
| 1 | Prove It | Every quantity recomputed each round, none eyeballed. Caught: the fixture called "real" when it is synthetic (`synth_fastcal_s1.mat`); "2670 distinct event times" when it is 2670 events at 2362 distinct times; "every finite `max_tau` returns the same value" falsified on the report's own trains at 1.269; "mean ISI is 10 s" for 10.11/9.97. All resolved. Final state: both reproducers byte-identical, table 0.3235/0.3133/0.3119 vs 0.3235/0.0696/0.0156, ratio 4.4996, all recomputed. |
| 2 | DOI or Die | Three successive attributions were wrong and all three were caught here. First draft credited the capped window to Kreuz 2015, which calls the measure "parameter- and scale-free" and whose Eq. 19 carries no bound. The correction overshot to "PySpike's own addition", refuted by cSPIKE's `max_dist`. The second correction said "in neither paper", refuted by Kreuz/Satuvuori/Pofahl/**Mulansky** 2017 (New J Phys 19:043028), which introduces τmax in terms — the recipient is a co-author. Final: a seven-row provenance table starting at Quian Quiroga/Kreuz/Grassberger 2002, whose Eq. 4 discussion already sanctions `min{τ, τij}`. All four DOIs verified against Crossref; both verbatim quotes checked character by character. |
| 3 | Cross-Examiner | Caught the summary/body contradiction on synthetic-vs-real; "the diff below" pointing 60 lines up after a reorder; the in-repo inventory undercounting itself twice (five → six → eight sites that call this "0.9.0's" bug); the pinned test carrying its own copy of that inventory, already drifted to three entries. |
| 4 | Reviewer 2 | Ran "can the alarm ring?" on every null. Killed the intent argument: the draft claimed callers "still" compute a doubled `max_tau` as evidence the clamp was meant to survive — 0.7.0 has no `true_max` and no doubling, so the doubling was *created* by the rewrite and discriminates nothing. Also caught the `Reconcile=False` remedy that could not fire, and the over-general "diverge at every cap". |
| 5 | Kill Your Darlings | 23 findings in round one, including the blocking one: the proposed patch capped at twice the intended window and dropped a guard. Later: "gives the uncapped answer, to three digits" refuted by the output block three lines above it. |
| 6 | RTFM | Grounded in all four papers and both implementations. Established that MRTS is a floor and cannot express a cap (the rebuttal that would have killed the report); that the correct bound is `true_max/2`; that the patch restores 0.7.0 exactly at MRTS=0; and that the tie argument had to rest on the bound being positive, not on a fast path that `coincidence_single_profile` does not have. |
| 7 | Reinventing the Wheel | Headline: nothing in the repo *asserted* the bug — it lived in a prose comment, so an upstream fix would have gone unnoticed. Added `test_pyspike_max_tau_is_still_inert`, which pins the behavior and is built to fail the day upstream fixes it (verified: it does). |
| 8 | You Lost Me | Caught "cSPIKE (the lab's MATLAB reference implementation)" — to this recipient "the lab" reads as *ours*, destroying the point; the `cSPIKE-validated` column header that never said whose number it was; and project vocabulary (fast/slow stream, operating point) exported cold. |
| 9 | Show, Don't Tell | Argued the mechanism should be a picture and named it: the ASCII timeline showing the four ISIs, the 13.1 s window returned and the 0.25 s cap sitting inert. Also argued *against* a rendered figure, with reasons recorded in the artifact so a later session does not reopen it. |
| 10 | Ship It | Found the defect no amount of source-reading catches: unescaped `\|` inside code spans in a GFM table cell shredded the cSPIKE provenance row, which rendered as a lone backtick. Every round since renders the body through GitHub's markdown API and inspects the HTML. Final render: 2 tables, 12 rows all correct width, 13 code blocks highlighted, 7 links, 0 stray backslashes. |
| 11 | Start With the Problem | Round one: the draft opened on mechanism and buried its strongest sentence two-thirds in. Reordered to symptom → smallest repro → scale → scope → cause → expected → fix → provenance → environment. No ordering findings in the last three rounds. |

## What changed, in order of consequence

1. **The patch was wrong twice.** First version capped at 2× the intended window
   (inside `get_tau` the parameter named `max_tau` is the already-doubled
   `true_max`). Second version raised `NameError` in `python_backend.py`, which
   imports only numpy and uses the builtin `min`. Both backends now get their own
   diff, and the `.pyx` one applies with `git apply`.
2. **The attribution was wrong three times**, ending at the 2002 founding paper.
3. **The regression is from 0.8.0, not 0.9.0** — and dated from the PyPI release
   (2023-07-14), not the Releases entry, which is three months late because the
   tag went up only after issue #71 asked for it.
4. **Scope was understated**: `get_tau` has 14 call sites, so the directionality
   and spike-train-order APIs are affected too, not just the four SPIKE-Sync
   entry points originally listed.
5. **The intent argument was cut** for being false.
6. **The results table became PySpike-against-PySpike**, retiring the hedge about
   comparing two aggregations and letting the 1 µs row ship.
7. **A regression test now pins the claim** in the repo.

## Residual ⚠ for Tony

- **⚠ Not verified here**: whether upstream's own test suite stays green under
  the patch. The one `max_tau` assertion does — run patched and unpatched, and
  the issue says so. The other 12 test files were not run. `test/` ships in the
  0.9.0 sdist, so this is doable before offering the PR; `test_reconcile.py` is
  the one to watch, given the `Reconcile=False` behavior change the issue
  discloses.
- **⚠ Not verified here**: every "with the patch" number comes from the
  pure-Python backend. No patched *compiled* extension has been run. The `.pyx`
  diff applies cleanly and the two backends agree elsewhere, but the compiled
  path is untested.
- **⚠ Not verified here**: whether SPIKY (the MATLAB GUI) also carries the cap.
  It is not in this tree. The issue claims the cap only for cSPIKE and PySpike,
  both read directly.
- **Before posting**: land the branch and repoint the three `blob/main` links to
  the landed SHA — `main` does not yet carry the pinned test. Unwrap the prose
  when pasting; GitHub turns every newline in an issue body into a line break.
- **After filing**: eight places in this repo call this "PySpike 0.9.0's" bug.
  All eight need the issue URL and the version correction, including the
  methodology narrative, which is the copy an outside reader meets.
