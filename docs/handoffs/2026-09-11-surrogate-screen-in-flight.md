# Handoff — finish the surrogate screen on the workstation

> **Stopped 2026-09-11 at about 11:05 on the Mac, for power**: the work charger could not keep up
> with the run, and the battery reached 18%. Resume on the HP workstation, which has Claude, Dropbox
> and the repos. Not murderboarded — working material for sessions in this tree. Delete this file and
> its pointer in the root `HANDOFF.md` once the report is murderboarded and #530 lands.

## Read first

- [The plan](../proposals/2026-09-10-surrogate-evaluation-overnight.md) — the authority. Scope: measure
  every candidate on `steps_excluded` and `cossart`; **no shortlist**; the verdict rule is designed from
  the measurements afterwards.
- [The review record](../reviews/2026-09-10-surrogate-evaluation-overnight_2026-09-10.md) — why the
  scope is measure-only, and the agenda for the verdict-rule design session.

## State at the stop

**Code** — branch `surrogate-screen-overnight`, commit `47e278e`, **draft PR #530**. It has 12
candidates, 6 controls, the counting statistics, three yardsticks, the destruction measure and the
per-ROI discriminator. On the Mac the full suite gave 3,018 passed, 33 skipped and 1 xfailed; the
pattern-jitter clean room gave 473 passed, with the differential fuzz agreeing and all 16 mutants
caught. ⚠ CI skips the 98 surrogate tests, because CI does not install Elephant.

**Results** — `<darkroom>/bugarach/2026-09-11-surrogate-screen/`, synced by Dropbox:

| part | state |
|---|---|
| `reproduction/` | finished: the leak table, the saturation table, `reproduction.json` |
| `discriminator/` | **finished** for both folders (`steps_excluded` 08:36, `cossart` 10:10); no command-line entry point exists, and none is needed |
| `steps_excluded/` | grid pass finished 10:45, except the cells left with stale `.progress` markers (28 fast, 21 slow) |
| `cossart/` | in progress at the stop; 32 stale `.progress` markers |
| `_cost_probe/`, `_superseded_stale_progress/`, `_superseded_starved/` | the run agent's cost probe and the stale markers it set aside; keep them |
| the reports | **not started** — no report code exists yet |

**`_manifest_mac_2026-09-11.json`** in the run folder lists all 1,607 files with their byte counts, 81 of
them stale `.progress` markers.

## On the workstation, in order

1. **Wait for Dropbox.** Every path in the manifest must exist with the same byte count. Do not start
   before that, or you will redo finished cells or read half-synced ones.
2. **Claim.** Put a block on this machine's local board naming your worktree. Then update the git
   board's darkroom claim (`docs/SESSIONS.md`, block `Mac/surrogate-screen-overnight`) to say the run
   moved to this machine, and land that change.
3. **Set up.**
   - Check out the branch: `git fetch origin && git worktree add <path> surrogate-screen-overnight`.
     Commits there go to #530.
   - Make a venv **outside** the worktree — its `.gitignore` does not cover `.venv` — and install
     everything in `dev` **except PySpike**:
     `pip install -e ".[ui,docs,dl,surrogates]" "pytest>=8" "playwright>=1.40"`, then
     `python -m playwright install chromium` for the render gate.
   - **Skip PySpike.** Nothing in the screen imports it; the two test files that use it
     (`test_sync_detect.py`, `test_synfire_roi.py`) skip without it, and CI already runs that way.
     PyPI ships PySpike 0.9.0 prebuilt only for macOS, so anywhere else `pip` compiles it from
     source, which needs a C compiler plus Cython (Microsoft's C++ Build Tools on Windows;
     `build-essential` and `python3-dev` under WSL). If you want it anyway, install the plain PyPI
     0.9.0 — **never the fork carrying our `max_tau` fix** (PySpike#89, still open upstream).
     `test_pyspike_max_tau_is_still_inert` deliberately asserts the upstream bug is still there, so
     the patched build turns it red, which looks like a regression and isn't one. bugarach's own
     SPIKE-synch is a separate port, bit-exact against cSPIKE, and needs neither.
   - Check that `python -c "from bugarach.paths import darkroom; print(darkroom())"` and
     `python -c "from bugarach import dataset; print(dataset.current('steps_excluded'))"` both resolve.
     If they do not — likely under WSL — set `BUGARACH_DARKROOM` to the `darkroom/bugarach` folder, and
     `BUGARACH_DATA_ROOT` if needed.
   - Run the full suite, and get it green before touching data.
4. **Finish the grid.** `tools/build_surrogate_screen.py` resumes by itself: finished cells are kept,
   and `--force` redoes them. First read how it treats a leftover `.progress` marker. If it does not
   redo those cells, move the markers aside into `_superseded_stale_progress/`, as the run agent did.
   Then run it with the settings each folder's `meta.json` records under `settings`:
   - `--role steps_excluded` — K 19, cell 1,500 s, hard stop 3,600 s, 4 GB per cell.
   - `--role cossart` — K 40, cell 7,500 s, hard stop 11,000 s, 5 destruction draws.

   Size `--jobs` to this machine and watch memory: JointISI at *J* = 1 frame builds multi-gigabyte
   tables. A cell that blows its caps is recorded as intractable, and the grid carries on.
5. **Write the reports**, per the plan's section "The report":
   - per-folder reports and a cross-folder summary in the run folder, each opening with an executive
     summary; no shortlist;
   - the choices the verdict rule must make, each beside its measurement;
   - numbered figures, the first ones synthetic (a surrogate and its leak, what each candidate does to
     one ROI, the window anatomy), all inline SVG;
   - time axes from a pure-Python port of `_time_axis_hook`, in `src/bugarach/time_axis.py`, with a
     test against it;
   - the builder at `tools/build_surrogate_report.py`, defaulting to the darkroom;
   - the render gate run from stamped copies of `downLow/tools/render_check.py` and
     `draughtsman/tools/edge_collisions.py` placed in the run folder's `tools/`, so their screenshots
     land there; the builder refuses a page with no SVG; `python -m playwright install chromium` first
     if needed;
   - DANDI:000219 cited wherever Cossart data appear.

   Commit the report code to `surrogate-screen-overnight`. Nothing derived from a real recording goes
   into git.
6. **Owed afterwards:**
   - CI: change `.github/workflows/ci.yml` to install `.[ui,dl,surrogates]`.
   - Add the sixth Elephant defect to
     [its todo](../todo/2026-09-11-elephant-surrogate-defects-are-not-filed-upstream.md): in ISI-dither
     mode without the square root, JointISI writes its smoothed histogram into an integer array, so
     sparse regions fall back to uniform dither.
   - Murderboard the report, then take #530 out of draft and land it.
   - Release the darkroom claim, and delete this handoff and its root pointer.

## Traps from today

- **A watchdog that finds the run's processes by path must exclude itself.** The Mac's throttle
  matched its own scratchpad path, throttled itself, and slept for 40 minutes while new workers
  drained the battery.
- **The run draws 60–90 W on a laptop.** Wall power is the reason for moving to the workstation.
- **The repo's hook blocks writing source files through shell heredocs**; use the file-writing tools.
- **Known departures from the plan, both measured.** The interval-jitter bin is rounded to whole
  frames, so at *J* = 1 frame interval jitter moves nothing. The window-shuffle window is √2·*J*
  rounded to an even number of frames.
