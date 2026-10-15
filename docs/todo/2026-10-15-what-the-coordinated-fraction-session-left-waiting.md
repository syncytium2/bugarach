---
status: open
filed: 2026-10-15
---

# What the coordinated-fraction session left waiting: two armory merges, one PR, one question

Written at the end of session "065 bugarach coord" (2026-10-14 into 2026-10-15). Nothing in it
is half-done code. Every item waits on something outside this repository, or on Tony.

## 1. The coordinated fraction under treatment: PR #896

`tools/measure_coordination_under_treatment.py` and its test, set to auto-merge on green. If CI
went red, the branch is `coordinated-fraction-under-treatment`. The run on the two cleared 2026
pilots is done. Its results, one-page PDF (Figure 1) and README are in
`<darkroom>/bugarach/2026-10-14-coordinated-fraction-under-treatment/`. The finding, as stated
there: coordination does not collapse under APV+CNQX(+GZ). The event rate does. The fast stream
leans down (median ratio 0.61–0.76) and the slow stream holds (0.93–1.21), on six recordings per
pilot.

## 2. Rename the page once armory's several-pilot naming form merges

The PDF is named `coordinated-fraction_before-after_pilots-20260811-20260917_4x_win20min_20261014.pdf`,
by Tony's choice, because the scheme could not name a page holding two pilots. Armory built the
form on `syncytium2/armory` branch `names-for-several-studies` (commit `d65ed6e3`). **Unmerged:
Tony's call, in the armory session.** Once it is on armory's `main`:

1. Re-vendor `tools/naming/` from armory `main`, stamp and all.
2. Make `--page` build its file name with `artifact_name.build(..., source="pilot-20260917, pilot-20260811", ...)`,
   not take it as an argument.
3. Rename the darkroom file to
   `pilots-20260811-20260917_before-after_roi_fast-slow-combined_win20min_20261014.pdf`,
   and update the folder's README.

## 3. Vendor armory's session-naming hook, then close PR #892

The hook that blocks `SendMessage` from a session nobody has renamed was drafted here in PR #892
(draft, auto-merge off) and handed to armory, which ported it: `syncytium2/armory` branch
`sessions-are-named-before-they-message` (commit `13a215d7`). **Unmerged: Tony's call.** Tony has
already said yes to the bugarach half (2026-10-14, "do 2 when available"). Once it is on armory's
`main`:

1. Copy `.claude/hooks/require-a-name-before-message.py` with a provenance stamp on line 1.
2. Wire it into `.claude/settings.json`: PreToolUse on SendMessage, and `--session-start` on
   both SessionStart matchers.
3. Point `tests/test_session_names.py` (from #892) at the vendored file. Close #892.

Its escape is `ESTATE_ALLOW_UNNAMED=1`, not #892's `BUGARACH_ALLOW_UNNAMED`.

## 4. Armory's sapper work: nothing to do here until it reports

The 19 open sapper and board-guard findings went to the armory session on the Mac
([the handoff](2026-10-14-hand-the-open-sapper-issues-to-armory.md)). It said it would wait for
Tony's approval before writing in bugarach.

## 5. Questions only Tony can answer

- **Delete the six per-stream PNGs** in that darkroom folder's `4x/` and `3x/`? Tony asked for
  "pdf only (no png)" and has not said whether that means removing the ones already there.
- **The TTX coordinated-fraction run on the default dataset is stopped** by its declared
  contamination (the pinning census undercount,
  [todo](2026-10-05-the-pinning-census-undercounts-on-the-default-folder.md)). It waits for the
  producer's corrected export. It does not become a caveat.

## Two things this session learned that the next one should not relearn

- **Session handles.** A session nobody has renamed is addressed by its auto title, which
  changes. After Tony renamed this one in VS Code, the Mac reached it by the bare name. Item 3
  makes that a hook.
- **A pilot's README can be stale.** The 2026 pilot READMEs said "not cleared for analysis"
  after Tony had hand-reviewed every recording. The producer fixed them on 2026-10-14. When a
  folder's own text and a ruling disagree, search for the ruling (`git log --grep`, the INDEX)
  before stopping. The record of the review was one raster-tool flag, `--hand-reviewed`.
