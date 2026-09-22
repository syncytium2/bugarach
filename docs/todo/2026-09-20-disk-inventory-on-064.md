---
status: open
filed: 2026-09-20
---

# What is on WSMIP064's disk after the weekend runs, and what could go — measured, nothing deleted

waiting: Tony — this is a proposal. **Nothing here has been deleted**, and nothing should be until he
says so. A workstation's disk is not something a session reclaims on its own judgement (orchestration
session, 2026-09-20).

**Measured on WSMIP064 on 2026-09-20**, not estimated. The other workstation's numbers will differ.

## First, a correction: the board's estimate was too high by about twentyfold

The machine-local board's `matched-merge-gaps` block says the leftover scratch is *"about 30 GB of
re-decoded arrays the tool regenerates"*. Measured, the three folders it names hold **1.44 GB**, and
**everything** under `%USERPROFILE%\runs\` — all 20 folders — comes to **3.14 GB**. The estimate was
written from the shape of the work rather than from the disk.

The reclaimable space is almost all somewhere else: **two stale virtual environments, 8.60 GB**.

For context, drive C: has **79.3 GB free** of about 951 GB, so nothing here is urgent.

## The inventory

| what | size | files | last written | is there another copy? | what regenerates it |
|---|---|---|---|---|---|
| `%USERPROFILE%\venvs\cuda121-probe` | **4.46 GB** | 18,035 | 2026-09-17 | no, and none is needed | `uv venv` + `pip install`; it was the torch 2.5.1+cu121 stopgap for the **old** driver, unneeded since the 582.78 update |
| `%USERPROFILE%\venvs\bugarach-cuda` | **4.14 GB** | 19,559 | 2026-09-17 | no, and none is needed | same; superseded by the per-worktree `.venv` |
| `runs\fair-comparison-2026-09-18` | 1.22 GB | 8,000 | 2026-09-19 | **yes — verified**, see below | only by re-running the 12-hour GPU run |
| `runs\replicate-2026-09-18` | 1.21 GB | 7,807 | 2026-09-19 | **yes** — it *is* an unpacked copy of the darkroom's `fits.zip`/`scores.zip` (board's own note) | unpacking those archives again |
| `runs\tune-gpu-shakedown` | 0.42 GB | 8,148 | 2026-09-18 | summary only, in `docs/learned/tuned_vs_coact/shakedown_home_spec/` | only by re-running the 13 h 53 min shakedown |
| `runs\fair-comparison-2026-09-18-gaps` | 0.13 GB | 3,878 | 2026-09-19 | no — ⚠ **do not delete**, see item 2 | a serial `select`/`--pairs` loop; 6 rounds for one allowance on one draw |
| `runs\replicate-2026-09-18-gaps` | 0.10 GB | 3,468 | 2026-09-19 | no — ⚠ **do not delete**, see item 2 | same |
| `runs\gpu-weekend-*` (6 folders) | 0.04 GB | ~1,050 | 2026-09-18 | no | timing probes; the board already calls them safe to delete |
| `runs\tune-*`, `gpu-correctness*`, `cpu-check-*` (9 folders) | 0.02 GB | ~1,050 | 2026-09-17 | no | smoke and correctness probes from the setup days |
| loose files in `runs\` (logs, launch wrappers) | 0.08 GB | 30 | — | the launch wrappers are the only record of how the tasks were invoked | — |

### The one "another copy" claim that needed checking, and does hold

`runs\fair-comparison-2026-09-18` is the weekend run's own output and cannot be regenerated cheaply,
so *"the darkroom has it"* is the whole basis for removing it. Checked rather than assumed:

```
fits.tar.gz      3,876 files
scores.tar.gz    3,715 files
results/ loose     411 files
                 -----
                 8,002 files   against 8,000 in the local folder
```

So the darkroom's `2026-09-18-fair-comparison-run/results/` accounts for every local file, with two
extra, in 98.3 MB compressed against 1.22 GB on disk. The replicate's archive is the same shape
(99.9 MB, `fits.zip` + `scores.zip`).

## What is proposed, in the order the space is actually there

1. **The two virtual environments — 8.60 GB, and the only large item.** Both were superseded by the
   2026-09-17 driver update and the board has called them unneeded since 2026-09-18. Nothing reads
   them. **This is the whole reclaim; the rest is rounding.**
2. **The `-gaps` scratch and the probe folders — 0.29 GB.** Re-decoded arrays and smoke runs; the
   tools regenerate them.
   ⚠ **Amended 2026-09-22 — do NOT delete the two `-gaps` folders, and "the tools regenerate them"
   is the part that was wrong.** The crowded-allowance top-up
   (`docs/learned/runs/2026-09-21-crowded-allowance-sweep/`) wrote into
   `fair-comparison-2026-09-18-gaps\crowded\` and `replicate-2026-09-18-gaps\crowded\`, and every
   strict row in that record reproduces from them. Regenerating is not one command: once a fit's
   crowded file is partial the plain `crowded` stage refuses it outright, so the only route is a
   serial `select` → `crowded --pairs` → `select` loop that took **six rounds and 20 minutes** for
   one allowance on one draw. Reclaiming 0.29 GB would cost that back, and the record says so.
   The probe and `-gaps-smoke` folders are still fine to delete.
3. **`runs\replicate-2026-09-18` — 1.21 GB.** An unpacked copy of darkroom archives, by the board's
   own description. Unpack again if needed.
4. **`runs\fair-comparison-2026-09-18` — 1.22 GB.** Covered by the darkroom, verified above. This is
   the one worth a moment's thought: it is the weekend's primary output, and the only remaining copy
   would be the Dropbox one.
5. **Keep `runs\tune-gpu-shakedown`** unless Tony says otherwise. Only its summary is in the repo, it
   is not in the darkroom, and 0.42 GB is not worth the asymmetry.
6. **Keep the loose launch wrappers.** They are the record of how the scheduled tasks were actually
   invoked — including the quoted-comma workaround that
   the launcher fix ([#676](https://github.com/syncytium2/bugarach/pull/676),
   on `tune-bench-comparison`) retired.

## Closes when

Tony has said which of items 1 to 4 may go, and they have gone — or he has said to leave the disk
alone, in which case this file records what is there and why it was kept.
