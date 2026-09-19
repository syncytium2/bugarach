---
status: open
filed: 2026-09-19
---

# The run-status mirror calls a finished run STALE

`tools/mirror_run_status.py` decides from one number, the age of `progress.json`: past 900 s it
writes *"⚠ STALE — the run may have stopped"*. A run that has **finished** also stops writing, so it
gets the same line. Seen on WSMIP065 on 2026-09-19: the replicate ended at 07:48:04 with 1,968 jobs
and 0 errors, and the last mirror pass at 08:15 wrote STALE into
`<darkroom>/bugarach/2026-09-18-replicate-run-status/STATUS.txt`, which is what a reader on a phone
opens first.

**The file already says which it is.** The tuning tool's `progress.json` carries `running`,
`queued`, `remaining_fits_known` and per-stage `done`/`total`. `running == 0 and queued == 0` with
every stage complete is finished; the same with work outstanding is stopped. The mirror should read
those fields when they are present and say FINISHED, STOPPED WITH WORK LEFT, or (fields absent)
fall back to the age rule it has now.

Until then: delete the scheduled task **before** the run's last copy goes stale, or write a line
beside `STATUS.txt` saying the run finished.
