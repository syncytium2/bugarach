# Changelog

## 0.1.0 — 2026-08-23

The first version this repository has carried. `pyproject.toml` said `0.0.1` from the
first commit on 2026-08-10 and never moved; there were no tags. This one is cut from
`main` after 286 merged pull requests, and every count below was read off the tree on the
day it was written rather than recalled.

### What bugarach is at 0.1.0

**Six coordination detectors** over calcium-imaging event data — `cicada`, `coact`,
`loco`, `rate`, `sce`, `sync` (`src/bugarach/detectors/`) — ported from the MATLAB
originals and validated against them, split on the two axes the glossary insists on:
stream (fast/slow) and detector.

**The export folder is the input, and the store is closed.** Analysis reads an export
folder per `docs/export_folder_spec.md` and nothing else — no `.mat` store, no lab
workbook, no roster. Which recordings are analysable and which ROIs are alive are the
producer's calls, already applied. A few legacy tools still reach for the old stores;
that is migration debt, recorded as such.

**A browser viewer and a CLI.** `bugarach` (`src/bugarach/cli.py`) for the command line;
`src/bugarach/ui/` renders detector lanes, the ROI raster and per-detector traces, with
the minutes-friendly time axes and compact labelling the plot conventions require.

**Tests: 1194 passing, 12 skipped.** They include the adversarial clean-room harness for
`find_peaks_halfprom` — an independently derived implementation, hand-built hostile
vectors, and a differential fuzzer — wired into the ordinary suite so validation reruns
with plain `pytest`.

**Rules that fire by themselves rather than being remembered.** `tools/sapper.py` carries
seven content rules (SAP001–SAP007) run by the pre-commit hook and CI, each with a
selftest proving it can still fire. `tools/guard_branch.sh` refuses a commit on `main`.
`tools/guard_local_board.sh` refuses a commit from an unclaimed worktree.
`tools/merge_when_green.sh` refuses to merge a pull request whose checks have not passed
— failing closed when it finds *no* checks, which is the condition that produced the bug
it exists for.

### Landed in the days before this tag

- **The merge gate reaps its own worktree** (#240, #241). It blocks until the pull request
  lands, so it is the only process awake when a worktree becomes garbage; it now removes
  the one it is standing in, verified merged and clean, and reports the ignored files it
  destroys. Both of those pull requests were landed by the reaper, from inside the
  worktree it then deleted.
- **A handoff for interface2** (#259) — `docs/reaper_handoff.md`, the rule and its decision
  function written to be implemented rather than vendored, since that repo is on GitLab
  and has no pull-request merges to hang a reaper off.
- **The worktree lifetime measurement was corrected** (#259). "Median ten minutes" was the
  median of the short mode; the true median is 37 minutes over 27 worktrees and the
  distribution is bimodal. Raw data and reduction committed at
  `docs/reviews/reaper_handoff_2026-08-23_worktree_lifetimes.csv`.
- **Murderboard re-vendored** to `fae0eca` (#256), after its freshness gate refused a
  review as stale — and one vendored file was found to have been edited in place, which
  the gate structurally cannot detect.

### Known open

`docs/todo/` carries the open items, including the two this release did not close: the
worktree sweep still reads no session board and **must not be `--apply`ed**, and the
vendor freshness gate still compares stamps rather than file bodies.
