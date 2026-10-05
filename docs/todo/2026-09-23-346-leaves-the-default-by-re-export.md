---
status: open
opened: 2026-09-23
area: data contract
waiting: the producer's re-export (syncytium2/interface2#2)
---

# `20260707_346` leaves the default folder by re-export, not by a filter here

Tony, 2026-09-23: he is marking `20260707_346` excluded in db4, and does not want it to affect the
study. It has 10 ROIs, the smallest field among the 67 recordings with a senktide or TTX window, and
its first treatment is TTX.

**The route is the producer's**, as the export contract requires (`docs/export_folder_spec.md`;
CLAUDE.md, "The export folder is the input"). Nothing in bugarach filters it. The request is
[syncytium2/interface2#2](https://github.com/syncytium2/interface2/issues/2): a new dated export
of the default folder with 83 recordings, and the TTX subset following.

**`20241004_80` stays in.** It has 9 ROIs and is baseline only. Tony is keeping it as an important
example of kernel success, and it is in neither treatment subset. Nobody should read "the smallest
fields are being removed" into this: one recording leaves, by name, for a reason Tony gave.

**When the folder ships:**

1. Move `default` in `current_export.toml` to it. Tony confirms it at session start; a session
   never does.
2. `tools/check_scored_dataset.py` flags every result scored on the 84-recording folder.
   Re-measure what the scoring design reads: the bench constants (background rates, jitter,
   participation, ROI count), and the chance floor per stream, which link 1 of the scoring design
   needs.
3. Close this todo, and link the folder's name here.
