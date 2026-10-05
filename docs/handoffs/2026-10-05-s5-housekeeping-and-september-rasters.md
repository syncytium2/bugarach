# 2026-10-05: brief S5 housekeeping, the default folder stopped, and the September rasters

> **Session `d2dfd7e2`** on WSMIP064, Claude Code, 2026-10-05. Its work came from the orchestrator's
> briefs, with Tony ruling in the session. Written at close, on Tony's word that all sessions end
> for the day. **Nothing is in flight**: no branch is half-done, no run is going, and nothing is
> unpushed. Working material, not murderboarded.

## Waiting on Tony

- **The contamination stop on the default folder.** `dataset.default()` refuses
  `senktide_ttx`. The stop clears only when interface2's corrected pinning export becomes the
  default, with the stop's note and test removed in the same change (#858;
  [todo](../todo/2026-10-05-the-pinning-census-undercounts-on-the-default-folder.md)).
- **Two drafts for Tony to post** (ADR-0007), both in that todo: the outcome-stated request for
  the corrected pinning export, and the comment closing interface2#2. `20260707_346` was checked
  absent against the folder itself.
- **Open PRs that need his decision.** All were brought up to `main` on 2026-10-05 and were green
  then.
  - #856, the local-rate threshold for count (sliding).
  - #853, the floor-sensitivity check. On hold by his word since 2026-09-28; do not merge.
  - #851 and #848: #851 is stacked on #848, and #848 carries ADR-0012.
  - #855, ADR-0013, simulating treatment periods on the bench.
  - #854, so that two calls never share an onset.
  - #835, the one-page methods section.
  - #637, the reaper.
  - **#596 conflicts with `main`** in model code (`chorus.py` was added on both sides, plus
    `line.py`, `tube.py` and `fair_bakeoff.py`) and is 616 commits behind. Rebuild it or close it?
  - **#587 still has auto-merge armed** from an earlier session. It was deliberately not updated,
    so that it cannot merge unattended. Should it merge?
- **Three root handoffs left in place**, as he chose: coded-detectors, detector-review and
  slow-comodulation. Two others moved here (#859).

## What landed

- **#858:** the default folder stopped on Tony's ruling. The census flagged 4 pinned ROIs on
  `20260629_312` where his review called 9; `_309` ROI 16 is over-cut; and `_309`, `_316` and
  `_235` have not been reviewed ROI by ROI.
- **#859:** two spent root handoffs retired to this directory.
- **#860, #862:** `make_group_raster_summary.py`.
  - `--all-groups` puts every group on one page, rows in DI, OVX, MALE, ORX order.
  - Every page is numbered as a figure, in the order fast, slow, combined.
  - The combined page no longer drops the "no field-step scan" warning.
- **#861:** the darkroom claim for the September rasters, released by this PR.
- **The September APV+CNQX → gabazine rasters**, in `<darkroom>/bugarach/2026-10-05-apv-cnqx-gz-sept-rasters/{4x,3x}/`,
  with a README. They are drawn from interface2's eval folders as rebuilt at 4:25 PM EDT: six
  recordings, dead ROIs removed, Tony's review blanking, and his long analysis windows (2 min
  delay on APV+CNQX and gabazine, none on high K⁺). Both folders pass `bugarach check`. Every
  window was checked against the rule before drawing: 0 mismatches out of 23 per folder.

## Worth knowing next time

- **`bugarach check` on native Windows dies printing ⚠** (cp1252). Set `PYTHONIOENCODING=utf-8`.
  The check itself is fine.
- **The local board guard reads a block's id from after the LAST `/` in its heading**, anywhere on
  the line. A slash in the description, such as `docs/handoffs/`, hides the block from the guard
  and blocks the commit. Keep slashes out of headings until `tools/guard_local_board.sh`'s
  `claims_heading` is fixed.
- **`tests/test_session_briefing.py` times out on this machine**, on unchanged `main` too: the
  briefing script runs past the test's 30 s. CI is unaffected.
- **Before reporting on a folder, read every `bugarach check` warning.** On the first September
  render, "NO ANALYSIS WINDOWS" was printed and not passed on, and Tony had to ask why no solution
  delay showed.
- **The producer rebuilt the eval folders in place four times in one afternoon.** For about ten
  minutes one of them was empty. Re-run the check on every rebuild, and look at the file list
  before trusting a read.
