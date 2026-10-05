---
status: open
filed: 2026-09-26
---

# Keep the darkroom's top level short, without anyone remembering to

**What happened.** On 2026-09-26 `<darkroom>/bugarach/` had 179 items at its top level, and
Tony found it "extremely crowded". Dropbox sorts by name, so the dated folders put the oldest
first and today's work at the bottom. The orchestrator moved the 134 items last modified before
2026-09-19 into `archive/2026-08/` and `archive/2026-09/`, and wrote `archive/INDEX.md`, which
maps each old path to its new one. That left 46 items. The PR that did it repointed 121 links in
67 live files. It left verbatim review reports, generated HTML and JSON run records as they were;
`archive/INDEX.md` resolves their old paths.

**What is not done.** Nothing stops the pile from growing back, and a week of this project makes
about 40 top-level items.

- A tool, `tools/archive_darkroom.py --older-than 7d`, that does the move and appends to
  `archive/INDEX.md`. It must not move the name-written tool destinations (`detect/`, `runs/`,
  `detector_history*`, `leaderboard.html`, `README.md`), anything under a live DARKROOM claim
  in `docs/SESSIONS.md`, or anything a local board says is being written.
- A trigger. Either the briefing prints one line when the top level passes about 50 items (it
  must stay within the briefing's byte budget, and the darkroom is not mounted in cloud
  containers), or the orchestrator runs the tool when it wraps up a night.

**Viewing tip, already true.** Sorting the folder by Modified, newest first, puts today's work at
the top in the Dropbox app and on the web. Dropbox remembers the choice.
