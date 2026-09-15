# Handoff — the detector review for outside readers (session 065, 2026-09-15)

> Its own thread. The root `HANDOFF.md` is a different thread; neither supersedes the other.
> When this thread is finished, delete this file (or move it to `docs/handoffs/` if anything
> below is still worth reading). Not murderboarded; working notes.

## Update, later on 2026-09-15: Tony rejected the review; a plain-language rebuild is in the darkroom

Tony's verdict on `detector_review.html`: he had asked for figures and sixth-grade text for a
reader with no background, and did not get it. Specifically: no figure showed *how* a detector
works; the networks were shown only as bell curves; Figure 2B made no sense to a naive reader;
jargon ("shipped"); citations without live links; and the one that matters most — on real
recordings some calls look like nothing, and some clear stripes are missed by most tools. He
asked that the old shift-versus-scramble deck figure (`constellation/coord_explainer/`, from
`coord_explainers_with_arc-td.pptx`) be combined with Figure 2, and said **do not murderboard**.

- **Delivered:** `<darkroom>/bugarach/2026-09-15-detector-review-plain/detector_review_plain.html`
  (21 figures, about 6,300 words), plus its PNGs, `real_prose.json` and `_work/`.
- **Builder:** `tools/make_plain_detector_review.py` (+ `tools/svgfig.py`,
  `tools/plain_detector_review_template.html`, `tests/test_svgfig.py`). It reads the first review's
  darkroom `measurements/` and reuses its four real-recording figures:
  `--from-review <darkroom>/bugarach/2026-09-15-detector-review --stages all`.
- **What the close-ups found** (numbers in the darkroom only): nearly all clear stripes that three or
  fewer detectors called sit outside the analysis windows, where the window-scoped detectors never
  run; inside windows most detectors call almost every clear stripe (binned SCE is the low one, partly
  the scoring todo below). Calls on nothing come from busy stretches (locust, SPIKE-synch, binned SCE,
  rate+context call through) and from 3-cell lineups in quiet recordings. A "clear stripe" needs a
  local stand-out rule, or busy stretches fill with chance "stripes" — the first cut without it was
  misleading.
- **Direction flag:** the deck slide says a scramble inflates the bar (bursty cells); the old Figure 2
  says a shuffle lowers it (the lab's evenly firing brief events). Both are right; the new Figure 5
  shows both directions.
- **Darkroom claim** `WSMIP065/detector-review-plain` is RELEASED in the same push as this update.

## State when the first session ended

- **PR [#587](https://github.com/syncytium2/bugarach/pull/587)** (`detector-review-doc`), auto-merge ON.
  - First CI run **failed on all three Pythons**: `tests/test_session_briefing.py`. The briefing was
    **9179B against a 9150B budget**. The cause was this PR's new todo (listed in the briefing).
  - Fixed in `dc6a411` by shortening the todo's title. **That did not fix it**: the re-run failed at the
    same 9179B. The waiting-on-Tony section is capped, so a shorter title just lets the section fill
    back up. The todo adds a third waiting entry (about 100B on this machine: main 9016B with the
    missing-board warning, the branch 8917B without it). The fix is a decision, not a trim — either
    Tony rules on the todo, or it leaves `waiting-on-tony`. Do not raise the budget.
  - **First job next session:** `gh pr checks 587`.
    - If the briefing is still over budget, shorten the todo title or its first line further. Do NOT
      raise the budget; see CLAUDE.md on `hook_spill_census.sh`.
    - If anything else fails, read `gh run view <id> --log-failed`.
- **Local Windows full suite:** 3021 passed, 19 failed, 31 errors. The visible failures are
  environment-bound: `test_site_pages_render` (Playwright), `test_session_briefing` (bash) and
  `test_paths::test_windows_path_is_translated_for_wsl`. Only the tail was captured, so this is not
  proven for all 19. **CI on Linux is the check that counts.**
- **Darkroom delivered:** `<darkroom>/bugarach/2026-09-15-detector-review/`.
  - `detector_review.html`: sha256 `de97953b…`, stamped from commit 510aafd.
  - 19 figure PNGs.
  - `real_prose.json`: the sentences about treatment recordings, kept out of the repo (FOUNDATIONS §5).
    The page cannot build without it.
  - `measurements/`: the `_work` JSONs.
  - `reviews/round{1,2,3}/`: verbatim role reports, plus `followup-prior-findings.md`.
- **Boards:** the git-board darkroom claim is RELEASED inside #587. The local board block
  `065/detector-review-doc` is marked DONE. Remove the worktree after merge.

## What landed (on the branch)

- **`tools/make_detector_review.py`.** Stages: models, real, problem, surrogate_data (needs the
  Elephant venv), surrogates, mechanism, learned, generator, sweeps, shipped, blockrecall,
  sce_rescore, optimization, performance, page.
  - **Rebuild the page:**
    `PYTHONPATH=src .venv/Scripts/python.exe tools/make_detector_review.py --out <dir> --bakeoff <run dir> --stages page`
    The output directory must hold `real_prose.json` and `_work/`.
  - **Where the inputs live:** the bake-off run dir is not in the repo. Its JSONs came from three
    `tools/fair_bakeoff.py` runs per background, and the session scratchpad copy is ephemeral. The
    darkroom `measurements/` holds the derived numbers only.
  - **Regenerating a scratch build:** copy `measurements/*.json` into `<out>/_work/` and
    `real_prose.json` into `<out>/`, then run `--stages page`. That needs the fig PNGs, so rerun the
    figure stages, or copy the PNGs into `_work/` too.
- `tools/detector_review_template.html`: the prose, with `{{token}}` and `{{PROSE:key}}` placeholders.
- `docs/reviews/detector_review_2026-09-15.md`: the run record. The roster and grants gates pass.
- `docs/reviews/detector-review-2026-09-15/round{1,2,3}/`: public copies of the reports.
- `docs/todo/2026-09-15-binned-sce-calls-are-scored-over-the-wrong-stretch.md`: waiting on Tony.
- `docs/GLOSSARY.md`: reader-facing synonyms block.

## The murderboard ended UNCONVERGED (round cap, 3 rounds)

The round-3 fixes were applied and rendered, but never reviewed blind. If Tony wants the page to go
outside, run a **round 4 (blind, all 11 roles)** on the shipped build first. This is his call, since
it exceeds the process cap.

## Decisions waiting on Tony (in the run record's ⚠ list)

1. **Release of fresh bake-off numbers** (MILESTONES "24-seed bake-off — held").
2. **binned SCE scoring mismatch** (the todo).
   - The problem: `sce_detect` width = event spread from the bin edge.
   - The cost: tuned F1 0.45 scored as-is, 0.70 scored over the full bin.
   - The choice: change what the scorer is given, or change the detector plus its parity fixtures.
3. **Whether "locust held out of the public build" covers outward documents.**
4. **Contacting the CICADA authors.** Their repo is now superseded by `cossartlab/cicada_analysis`,
   which also detects from event times; locust has never been compared with CICADA's output.

## Follow-ups a session can do without Tony

- **INDEX.md row** for `tools/make_detector_review.py`, *after* #587 merges. A row may only point at `main`.
- **Stale project text found by the review:**
  - the GLOSSARY `locust` entry says producer durations, but the shipped setting is a fixed 1 s;
    watch SAP013 when rewording;
  - `detector_history.md` reads Cossart 2003 as a pooled histogram; it was a per-surrogate maximum;
  - the `detect_folder.ONSET_FIELD` comment about locust's anchor is stale;
  - the `bench.TOLERANCE_GRID` docstring still says 1.5 s;
  - the `bench.MEASURED_BURST_SHAPE` table disagrees with Figure 10D/E;
  - `make_mechanism_figure.py` keeps an old window filter that `_overlapping` replaced.
- **Vendored gate bug.** `tools/murderboard_roster.sh` strips `_` from the `reports:` path before
  resolving it, which is why the report dir uses hyphens. Report it upstream (syncytium2/murderboard);
  don't edit the vendored copy.
- **Reuse debt noted by role 7** (optional):
  - `_page_layout` monkeypatches `make_group_raster_summary`; better to add `names=`/`raster_px=` kwargs
    to `build_page`;
  - Figure 2D's bars are a sketch, not a shipped detector's rule;
  - the `_real_members` picker duplicates `make_intro_figures`.

## Traps met this session

- **Harness output files are 0 bytes.** Extract reports from
  `~/.claude/projects/<proj>/<session>/subagents/agent-<id>.jsonl` instead (a scratch
  `extract_report.py` did this).
- **The no-heredoc hook blocks writing source through bash heredocs.** Use the Write or Edit tools.
- **Editor file state goes stale after `sed`.** Re-read a file before using Edit on it.
- **`check_quotes` fires on quoted page text that sits beside a personal-communication citation.**
  Keep such lines out of public copies rather than editing the check.
- **Windows PYTHONPATH needs `;`, not `:`,** for multiple entries.
