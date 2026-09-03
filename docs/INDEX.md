# Index — the words you would search for, and where the answer is

**This exists because the information was already here and had no address.** On
2026-08-30 a session spent several turns re-deriving that the Cossart/DANDI transfer
machinery exists, and began designing around a constraint that `tools/import_dandi.py`
had already solved. Nothing was missing. It was unfindable.

**How to use it:** find the row whose *keywords* match what you would have typed into
`grep`, not the row whose filename looks right. The keyword column carries the words
that do **not** appear in the path — that is the whole point of the file.

⚠ **This index is a pointer, never an answer.** Where it summarises, it can be stale;
the linked file wins. If you find it wrong, fix the row in the same commit as whatever
you were doing.

⚠ **A row may only point at something that exists on `main`.** This repo runs 14
worktrees and several open PRs at once, and the first version of this file cited a todo
that existed only on an unmerged branch — dead for every reader on `main`, and the link
test could not see it because the pointer was a bare code span rather than a markdown
link. **Land the thing first, then index it.** Both the rule and the gap are now
enforced by `tests/test_index_resolves.py`, which reads code spans too.

---

## The loop — what the product actually does, end to end

| you want | keywords | go to |
|---|---|---|
| **the pipeline, all of it, in order** | loop, workflow, pipeline, the stages, end to end, what the app does, what happens, the product, per-lab loop, what are we building | [`RESET.md`](RESET.md) **§2** — Tony's own statement of the loop, quoted verbatim, with the four places reality differs marked. **§7** is the order of work and which steps are blocked; **§3** is the built/not-built table |
| ⚠ **not** the loop | app plan, build order, folder reader, the writers, batch | [`workflow_plan.md`](workflow_plan.md) is the **app-build** plan for the two ENDS — reading a folder, writing `detections.csv`. It does not mention the human-identification step at all. A session on 2026-09-03 read it as the pipeline, reported the centrepiece missing, and Tony had to type his own loop out from memory to correct it |
| **the centrepiece — a person's verdicts on the machine's candidates** | human in the loop, machine assisted, identification, confirm, reject, annotate, verdict, judgement, who decided, agreement | [`src/bugarach/annotate.py`](../src/bugarach/annotate.py) — records the verdict **and the view it was made in**. `assess` proposes, this disposes; browser UI in `docs/site/raster_viewer.html` |
| **K, and what "blocked on K" means** | K, min_rois, floor, how many ROIs, coactivity floor, blocked, who chose K | `assess` reports a **scan** and names no winner. `derive_spec --k-from-annotations` estimates K from labelled calls (`annotate.derive_k`), and `assess --for-annotation` is the proposal pass it needs. ⚠ Propose **below** the floor being estimated or the answer is the assumption returning — [the trap](todo/2026-08-28-derive-k-from-confirmed-events.md) |
| the question the loop opens with and never answers | contrast, before and after, baseline vs drug, paired, does it change, publish | ⚠ **nothing computes it.** No function in `src/` puts two regions side by side — [`the question nothing computes`](todo/2026-08-23-the-treatment-contrast-is-the-question-nothing-computes.md) |

## The data

| you want | keywords | go to |
|---|---|---|
| which recordings analysis reads, right now | current, canonical, which folder, corpus, "where is the data" | [`current_export.toml`](../current_export.toml) — declares it; `dataset.current()` resolves it. **Never hardcode a folder** |
| a second or third corpus | role, pensub, cossart, alternate | `current_export.toml` has **three roles**: `default`, `pensub`, `cossart`. `dataset.current("cossart")` |
| what a folder is allowed to contain | contract, columns, producer, optional fields, silent ROI | [`export_folder_spec.md`](export_folder_spec.md) |
| why analysis must not read the `.mat` store | store is closed, exclusions, withdrawn recordings, dead ROI | `CLAUDE.md` "The export folder is the input"; sapper **SAP007** |
| the tour of where things live on disk | data root, darkroom, mount | [`where_the_data_are.md`](where_the_data_are.md) |

## Another lab's data — DANDI / Cossart

| you want | keywords | go to |
|---|---|---|
| import another lab's published data | DANDI, 000219, Cossart, other lab, outside producer, NWB, binarised, mouse pup, CA1 | [`tools/import_dandi.py`](../tools/import_dandi.py) — its docstring is the reference, including what the source does **not** carry |
| what their corpus looks like statistically | assessment, their numbers, K scan | `docs/learned/assessment_cossart.json` (ours: `docs/learned/assessment_real.json`) |
| **does a detector tuned here work on their data** | transfer, generalisation, cross-lab, out-of-corpus, fit-here-score-there | `fair_bakeoff.py --score-spec`. ⚠ **Read this first:** transfer works by deriving a *generator spec* from their statistics and scoring on simulation from it — **not** by scoring on their raster. Their data is a **binary raster with no coordination ground truth**, so recall/precision are not directly computable on it |
| why their timing cannot be compared to ours | landmark, t50rise, rising edge, half-rise, offset | `tools/import_dandi.py` — *"cross-lab timing comparisons carry a caveat"*. Rankings and rates transfer; coincidence-to-a-tolerance does not |
| the executable spec for import and transfer | what does it actually promise, contract test | `tests/test_import_dandi.py`, `tests/test_fair_bakeoff_transfer.py` |
| **which K for their corpus, and why the answer is a curve** | K=12, K=16, argmax, coact_excess peak, per-slice median, aggregator | [`tools/make_k_scan_figure.py`](../tools/make_k_scan_figure.py). ⚠ **The argmax depends on the aggregation** — pooled median says 16, pooled mean and mean per-slice rank say 12, and only the second pair survives resampling. `80b8db6`'s *"per-slice median argmax is K=12"* is **false**; choosing K is still Tony's, on the `MILESTONES.md` Open list |
| **numbers from the transfer work that were later retracted** | superseded, corrected, K=3 vs K=12, sample size | `docs/handoffs/2026-08-29-the-transfer-experiment-and-two-things-i-corrected-myself-on.md` — ⚠ **read before quoting any transfer figure**; a session that finds this index will not otherwise learn which numbers were withdrawn |

## The bench, the simulation, the scoring

| you want | keywords | go to |
|---|---|---|
| the synthetic recording every detector is scored on | bench recording, planted events, hot window, distractors, regimes | `bench.BENCH_RECORDING`, `bench.REGIMES` in [`src/bugarach/bench.py`](../src/bugarach/bench.py) |
| how a recording is generated | simulate, generator, background shape, participation, jitter, min_sep | [`src/bugarach/simulate.py`](../src/bugarach/simulate.py); [`generator.md`](generator.md) |
| what counts as a hit | tolerance, matching, TOL_SEC, edge gap | [`src/bugarach/score.py`](../src/bugarach/score.py) |
| **the four ways a detector can be wrong** | false negative, false positive, promiscuity, probe, distractor, coincidence-not-coordination | `BenchResult`: `recall` / `by_frac` (misses, by participation level), `precision` (fired where nothing was planted), `hot_fa` (**fired in a block with nothing planted**), `distractor_hits` (**fired on a real coincidence that is not coordination**) |
| how an operating point gets chosen | calibration, sweep, knob, campaign, grid, gate | `bench.pick_operating_point`, `bench.OPERATING_POINTS`, `bench.MAX_PROBE_PER_MIN`. The probe is a **gate at selection time, deliberately not a term in F1** |
| platform-independent speed | realtime, normalised, machine-dependent | `BenchResult.detect_x_realtime` — prefer it to raw seconds |

## The detectors

| you want | keywords | go to |
|---|---|---|
| **who wrote which one, and which are ports** | authorship, provenance, lineage, port, original, credit, CFAR, radar | [`detector_history.md`](detector_history.md). **Read its revision blocks top-down — they correct each other.** Only `locust` is a port |
| what each detector actually does | mechanism, algorithm, how it works | [`src/bugarach/detectors/`](../src/bugarach/detectors/) — one file each, docstring first |
| why coact and loco look like one detector | shared, circular shift, surrogate, _shared.py, duplicate | `src/bugarach/detectors/_shared.py` shares the **null**, not the detector. They differ in thresholding principle, params, speed and false-alarm rate |
| the learned models | network, torch, tube, center-surround, DL, training | [`src/bugarach/learn/`](../src/bugarach/learn/), architectures in `src/bugarach/learn/nets/` |
| head-to-head numbers | bake-off, comparison, scoreboard, ranking, F1 table | `docs/learned/bakeoff.json` is the data; `docs/learned/bakeoff.md` is the page. ⚠ The page's table is **typed by hand** and has gone stale |

## The site

| you want | keywords | go to |
|---|---|---|
| what the public site is | pages, nav, publish, deploy | `tools/build_site.py` — `PAGES`, `STATUS`, `PUBLISHED` declared once |
| why a page refuses to build | stale, degraded, staleness gate | `_page_is_current()` rebuilds and byte-compares. A stale page is a build failure, not a warning |
| which detectors the site hides | withheld, excluded, locust, five vs six | `_withheld_from_the_viewer()` reads the viewer's `WITHHELD` set. **README documents six, the site shows five, and both are right** |

## Process — how work is done here

| you want | keywords | go to |
|---|---|---|
| **where are we, what is established, how strongly** | milestone, achievement, status, what is done, what is settled, evidence vs decided, strength, superseded, held, inert | [`MILESTONES.md`](MILESTONES.md) — every row pinned to a commit and a doc, with a `strength` column separating **measured** from **decided** from ⚠ **evidence** (the measurement exists; the decision it informs does not). Read `strength` and `status` before quoting a row |
| what is in flight right now | handoff, in progress, resume | root `HANDOFF.md`. **No file at root == nothing in flight** |
| what another session is touching | board, claim, collision, concurrent, parallel | [`SESSIONS.md`](SESSIONS.md) (cross-machine) **and** `../bugarach-worktrees/SESSIONS.md` (this machine). Two boards, different questions |
| rules that fire by themselves | sapper, lint, gate, hook, SAP0.. | [`../tools/sapper.py`](../tools/sapper.py); disputes in [`sapper_feedback/`](sapper_feedback/) |
| reviewing a document before it ships | murderboard, adversarial, roles, anti-slop | [`doc_review_process.md`](doc_review_process.md) |
| **quoting someone's email, or anything a person said in private** | correspondence, personal communication, private mail, quote a letter, permission, is this public, de-identify, attribution leak | **Cite it; do not quote it.** `CLAUDE.md` §*Other people's words* — paraphrase plus `<name>, personal communication, <date>`. **This repo is public**, it has leaked a private letter twice, and asking afterwards is not asking. Mechanized both at the commit and in CI: [`tools/check_quotes.py`](../tools/check_quotes.py). Where the letters themselves should live is open: [`todo/2026-09-02-correspondence-has-nowhere-private-to-live.md`](todo/2026-09-02-correspondence-has-nowhere-private-to-live.md) |
| **draw a figure — how this repo renders one** | figure, plot, chart, PNG, holoviews, bokeh, panel, playwright, screenshot | copy the shape of any `tools/make_*_figure.py`: `measure()` → `build()` (holoviews panels) → `header_html()` → save HTML, screenshot it with Playwright chromium. Destination **defaults to `bugarach.paths.darkroom()`**, `--also` takes the repo copy (SAP006 blocks a required `--out`). Conventions — no titles, identity in the y-label, nothing drawn on a raster — are in `CLAUDE.md` |
| an algorithm implemented from a spec alone | clean room, spec, adversarial validation | [`clean_room/`](clean_room/) |
| a decision already made | ADR, ruling, settled | [`adr/`](adr/) |
| open work | todo, backlog, next | `docs/todo/` — 148 files, `status:` in frontmatter. **A record, not a queue** |
| **a question asked and how it was answered** | decision log, misread, quote, ruling | ⚠ **`docs/decisions.md` is owed and not written.** Specified in [`handoffs/2026-08-30-the-session-end-hook.md`](handoffs/2026-08-30-the-session-end-hook.md) §"Also still owed" — question asked, answer verbatim, how it was interpreted |

## Known traps — things that fail quietly

| trap | keywords | where |
|---|---|---|
| a worktree's tests run against the **primary checkout's** `src` | worktree, PYTHONPATH, fails toward green, wrong src, `test_architectures_are_files`, `test_a_broken_architecture_is_loud`, `test_the_server_hands_out_the_page_with_the_shim`, "3 failed", "already failing on main", stashing did not clear it | [`handoffs/2026-08-28-the-worktree-src-fix-nobody-has-chosen.md`](handoffs/2026-08-28-the-worktree-src-fix-nobody-has-chosen.md). Use `PYTHONPATH=$PWD/src`. **Those three tests fail in every worktree whatever the branch holds, and stashing cannot tell you so** — [the todo](todo/2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md), §2026-09-02 |
| running a **subset** of tests and reading it as green | partial, subset, passed | Full suite, always. Cost two sessions on 2026-08-30 |
| the session briefing reads a **stale checkout** | briefing wrong, out of date, behind | `git pull` first. A 64-commit-behind primary reported wrong PRs, suite size and board counts |
| numbers typed into prose by hand | transcribed, stale table, retype | `docs/learned/bakeoff.md` and `README.md`'s tables. Filed: `docs/todo/2026-08-28-the-bakeoff-page-transcribes-what-a-token-could-substitute.md` |
| "team" in **interface2** commit prose | other team, their detector, another lab | It means **a parallel session**, not another laboratory. `detector_history.md` 2026-08-30 |
| three seeds is inside the noise on this bench | seeds, flaky, noise, reproducible | 12+ seeds. At 3 the background-axis winner flips between blocks |
| **a settings file you tuned is ignored by `bugarach detect`** | settings, tuned, --settings, write-only, detector_settings.csv, apply, load back | `detect_folder()` takes no settings argument and `emit.read_detector_settings` has no caller — the run uses stock `OPERATING_POINTS` and says nothing. [`todo/2026-09-02-the-settings-loop-does-not-close.md`](todo/2026-09-02-the-settings-loop-does-not-close.md) |

---

## What is deliberately not here

Anything that changes weekly — counts, current numbers, who holds what. Those go
stale and an index that lies is worse than none. **Rows point at the file that owns
the answer, and the file is the authority.**
