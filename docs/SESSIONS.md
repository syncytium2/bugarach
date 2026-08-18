# Cross-machine session board — bugarach

**In git, therefore it reaches every session on every machine.** This is the half of the
session board that has to travel. The protocol is
[`docs/session_protocol.md`](session_protocol.md) (vendored from interface2); this file is
its Tier-2 ledger.

Companion, **outside git**: `../bugarach-worktrees/SESSIONS.md` — only what genuinely
cannot travel (live process ids, that box's free disk, local scratch paths).

---

## Which board does this go on?

One test, and it is **not** "is this about my machine?":

> **Can a session on another machine see, reach, or damage the thing you are claiming?**
> **Yes → here, in git. No → the machine-local board.**

The trap is shared storage. A Dropbox or network mount is visible from *every* machine, so a
claim on it is cross-machine even though it feels local.

| goes HERE (git) | stays MACHINE-LOCAL |
|---|---|
| claims on `BUGARACH_DATA_ROOT` stores, the Dropbox darkroom, any `interface2` checkout | live process ids, `pytest -n` jobs |
| exclusive-write claims of any kind | that box's free disk, local scratch |
| "I am regenerating the MATLAB parity fixtures" (needs MATLAB + interface2) | which MATLAB release is installed where |
| messages to another session | — |

**bugarach-specific shared resources worth claiming before writing:**

- `tests/fixtures/ref_*.json` — regenerating these needs MATLAB + an interface2 checkout;
  two sessions regenerating at once will produce conflicting oracles.
- the Dropbox **darkroom** (`<dropbox>/darkroom/constellation/`) — shared across every
  machine and every project that mounts it. Claim before writing.
- any `interface2` worktree you `addpath` — another session may be mid-edit on that branch.

---

## Protocol for a block

- **Add a block at startup** — address (`<machine>/<branch>`), task, which external paths you
  will write, status.
- **Mark it DONE on exit**, and release any exclusive claim explicitly.
- **Scan the board before writing any shared external output.** If an ACTIVE block claims it,
  use a different namespace or wait.

Template:

```
### <machine>/<branch> — <task>
- **Status:** ACTIVE | DONE
- **Started:** YYYY-MM-DD
- **Writes:** <external paths, or "repo only">
- **Claims:** <exclusive-write claims, or "none">
- **Notes:** <anything another session must know>
```

---

## Active

### Mac/windows-abut — the window boundary was drawing a gap that is not in the data
- **Status:** ACTIVE 2026-08-18 — redeploying after the fix
- **Writes:** the PUBLIC SITE. Nothing to the darkroom, nothing under `$BUGARACH_DATA_ROOT`.
- **Claims:** the site deploy, taken from released. Same standing note as the block below —
  check what `bugarach-worktrees/deploy-site` is checked out at first; it is a detached HEAD.
- **Why:** the raster left a 1px unpainted column at every region boundary. Measured, not
  guessed. On a time axis that reads as time nobody declared, and regions are contiguous by
  contract — `region_windows` halts on a gap because in these stores one is a data defect.

### Mac/explain-k-and-input — figures for K and the model input, and the two tracks split
- **Status:** DONE 2026-08-18 — session ended, nothing in flight
- **Started:** 2026-08-18
- **Writes:** `<darkroom>/bugarach/` — `webapp_spec.html`, `model_track.html`,
  `overnight_spec.html`, `overnight_spec_review.html` at the **top level**; the report
  and its two new figures in `2026-08-17-coordination-report/`; and that folder's
  `README.md`. **Claim released — the writing has stopped.**
- **Notes for whoever picks this up:**
  - **The cell-assembly question is handed off**, deliberately as a todo rather than a
    `HANDOFF.md`, because it is a *new* piece of work and not an interrupted one:
    [`docs/todo/2026-08-18-do-real-slices-have-recurring-assemblies.md`](todo/2026-08-18-do-real-slices-have-recurring-assemblies.md).
    It is self-contained — the question, why it is cheap, why the answer is useful in
    both directions, and the one thing that must not happen (porting an assembly
    detector first and reporting its score).
  - **Read `docs/model_track.md` before touching the model** and `docs/webapp_spec.md`
    before touching the app. They are separate on Tony's instruction and neither blocks
    the other; the only seam is the `ARCHITECTURES` registry.
  - **Nothing in `docs/overnight_spec.md` is approved.** It carries its own refusal
    block. Do not run it.
  - **Three corrections landed today that were inherited, not invented** — "K=4 halves
    the event rate" (it is a quarter, and it had spread to six places), PySpike credited
    with a detector that is ours, and "no literature model has been run" when CICADA is
    exactly that. All three survived earlier reviews. Assume the next one is in a
    sentence nobody has divided.

### Mac/viewer-colours+simulator — deploying the site after the viewer work
- **Status:** DONE 2026-08-18 — **claim released**, deploy finished and verified
- **Started:** 2026-08-18
- **Writes:** **the PUBLIC SITE** — `npx wrangler deploy` from `origin/main`. Nothing to the
  darkroom, nothing under `$BUGARACH_DATA_ROOT`.
- **Claims:** the site deploy, taken from released. Last deploy wins and there is no
  per-page ownership, so coordinate here before deploying.
- **Why now:** the live site was serving `19a7812` and `main` had moved twelve commits past
  it. Not because nobody deployed — because the deploy ran from
  `bugarach-worktrees/deploy-site`, which is a **detached HEAD pinned at that commit**. That
  worktree holds the only `node_modules` and the only wrangler login on this Mac, so it is
  where deploys happen, and it does not follow `main`. **Check what it is checked out at
  before deploying, every time**, or you will republish whatever it was pinned to. This
  session fast-forwarded it to `origin/main`; it will drift again.
- **Deployed:** version `f9df77ef-24c3-4703-bea7-3aa7aff00b93`, live page now stamps `4c7c18f`.
  `npm run deploy` needs `python` on PATH and this Mac only has `python3`, so it must be run
  as `PATH=<repo>/.venv/bin:$PATH npm run deploy`. Do **not** "fix" `package.json` to say
  `python3` — the Windows box has `python` and not `python3`, and that is the box the deploy
  doc was written on.
- **⚠ Found on the live page, not fixable from this repo:** Cloudflare injects its Web
  Analytics beacon into the served HTML, so the viewer — the page that promises it makes no
  network calls — makes two before the reader clicks anything. Needs a dashboard toggle.
  `docs/todo/2026-08-18-cloudflare-injects-a-beacon-into-the-page-that-promises-none.md`.
- **Publishing:** the only build inputs that changed since the live version are
  `docs/site/raster_viewer.html` and `tools/build_site.py` (PR #85 — window colours, the
  browser simulator, the accordion sidebar). Everything else that landed since goes to
  `docs/learned/`, which the build does not publish.

### Mac/spec-to-dropbox — put the overnight spec where Tony can find it
- **Status:** DONE 2026-08-18 — **claim released**, writing has stopped
- **Started:** 2026-08-18
- **Writes:** `<darkroom>/bugarach/` — `overnight_spec.html` at the **top level**, not in a
  dated subfolder, plus one line in that folder's `README.md`.
- **Claims:** those two paths only. No dated subfolder, nothing in `<darkroom>/constellation/`.
- **Notes:** third time a deliverable has been published and not found. The first two went
  into dated subfolders; this one goes at the top level because the folder's own index is
  the only thing a person reads first. The spec is **NOT APPROVED** and the page says so
  above the fold.
- **Done:** `overnight_spec.html` and `overnight_spec_review.html` at the top level, and
  the folder README now opens with them rather than with the report. Rendered through the
  new `tools/md_to_page.py`, which puts a markdown document in the reports' own look —
  because the last thing that was found and then not read was a `.md` sitting in a folder
  of JSON.

### Mac/import-contract+viewer — the import contract, its validator, and the public reader
- **Status:** DONE 2026-08-17 (session ended)
- **Started:** 2026-08-17
- **Writes:** **the PUBLIC SITE** — deployed `bugarach.tonydefazio.com` three times today
  (`npx wrangler deploy` from `main`; last version `9ea78b47`, and the live page now matches
  `main`). Nothing written to the darkroom. Nothing written under `$BUGARACH_DATA_ROOT`.
- **Claims:** released. While active this held the site deploy — coordinate before deploying,
  since the last deploy wins and there is no per-page ownership.
- **Reads (no claim needed, recorded so the next session knows):**
  `<data>/exports/bugarach/2026-08-17_revised_2v` and `..._v2` — interface2's export folders,
  written by their `generate_export_folder.m`. Read-only here.

- **What landed (main):** the folder contract at revision 3, `bugarach check`, `bugarach view
  --raster-only`, and a client-side raster viewer on the public site. PRs #70, #72, #73, #75,
  #76, #77, #78. Closed as superseded: #68 (wrong contract shape), #51 (landed via #72).

- **Notes another session must know:**
  - **The windowing default is an open scientific decision**, filed at
    `docs/todo/2026-08-17-windowing-convention-is-not-optional.md`. A folder with no
    `analysis_*` columns gets this project's wash-in delay, caps, and the `"hi" in label`
    substring exemption — which is why `histamine` would be spared and `elevated potassium`
    trimmed. Three options are costed there. **Do not "fix" it by relaxing the guards in
    `region_windows`:** they halt on real data defects, and that halt is what caught a bad
    export instead of quietly scoring it.
  - **`bugarach check` now runs `effective_region_windows`, and that is load-bearing.** Before
    2026-08-17 it called `load_folder` and no detector, so a folder that halted 83 of 85
    detectors and a good one were indistinguishable to it. Both teams cited the green result
    as evidence. If you add a check, ask what it would fail on.
  - **The viewer page reaches nothing, and that is tested.** `tests/test_site_viewer.py` fails
    on any network primitive and on building markup from a value. It is not decoration: a
    `regions.csv` label ran script on the deployed page on 2026-08-17 before the second rule
    existed.
  - **An analysis-window editor is version 2** (Tony, 2026-08-17). The contract carries
    `analysis_start_sec`/`analysis_end_sec` and the detectors honour them; nothing edits them.
### Mac/sota-landscape — the landscape report, four upgrades, and the site's competitor links
- **Status:** DONE 2026-08-17 — session ended, everything merged (PRs #69, #71, #74)
- **Started:** 2026-08-17
- **Writes:** repo, plus **two small writes to `<darkroom>/bugarach/lit/coordination/`**
  — see the honesty note below.
- **Claims:** none held. Released.
- **✅ DEPLOYED 2026-08-17 by `Mac/import-contract+viewer`** (block above), so the warning
  below is discharged: `landscape.html` and the competitor links are live, verified by
  fetching them. Recorded rather than deleted, because the reason it was true is the
  standing one — **nothing redeploys on merge**, and the next person to change
  `build_site.py` inherits exactly this note.

  **Re-deployed later the same day** from `origin/main` at `19a7812`, version
  `98e82444` — that block's deploy predated two more merges, so `index.html` and
  `diagnostic.html` went up again on top of it. Nothing was wrong with the earlier
  deploy; `main` had simply moved. Two details neither of us wrote down and the next
  person will want:
  - **Cloudflare drops the `.html`.** `/landscape.html` 307s to `/landscape`. The
    relative `href="landscape.html"` in `index.html` is still the right thing to
    write — it works in a browser through the redirect and works from `file://`
    directly — but a link check that treats a 307 as a failure will cry wolf.
  - **Only `deploy-site` can deploy.** It is the one worktree with `node_modules` and
    an authenticated wrangler; the rest have neither. Point it at `origin/main`
    (`git checkout --detach origin/main`) before building, or you ship whatever
    commit it was parked on — it was 40 PRs stale when I found it.
- **⚠ THE LIVE SITE WAS BEHIND `main` (resolved above).** `tools/build_site.py` gained a
  "Where this sits" section linking DOSED, cnn-ripple and CICADA, and it now publishes
  `landscape.html` into `site/`. **Nothing redeploys on merge** — someone must run
  `npm run deploy` (see `docs/deploy.md`; needs node + a wrangler login). Until then
  `bugarach.tonydefazio.com` has neither the competitor links nor the landscape page,
  and the build refuses to run without `docs/learned/landscape.html` present.
- **Honesty note — I wrote to the darkroom after releasing the claim on it.** The
  `lit-adjacent-fields` block below was marked DONE and its claim released; the
  murderboard that ran afterwards found the shelf README overstating its own read
  status ("ten read in full" — it is nine), and I corrected the README and its DOSED
  entry **without re-taking the claim**. Two lines in one file, no other session was
  active on it, and the alternative was leaving a known-wrong count on a shelf whose
  entire purpose is honest read status. Recording it because a claim that is released
  and then written to is worth less than one that says so.
- **Notes:** Section 3 of the coordination report is **corrected at source** — the
  novelty claim is withdrawn, three groups already train networks that emit population
  events with times. New companion page `docs/learned/landscape.html` positions the work
  and links every competitor; `docs/learned/next_stage.md` sequences the four upgrades.
  Review records: `docs/reviews/landscape_2026-08-17.md` (11/11 roles, 2 blind rounds)
  and `docs/reviews/coordination_report_section3_2026-08-17.md` (11/11, 1 round).

  ⚠ **The two pages must publish together.** `coordination_report.html` links to
  `landscape.html` relatively, and that link carries its retraction. Copying the report
  anywhere without the landscape page beside it points the correction at nothing.

  **A measurement fell out of the reading and it is the useful part.** Scoring tolerance
  is fixed at 1.5 s everywhere and had never been varied. Sweeping it: the published
  ranking of the six is stable at every tolerance from 0.1 s to 3 s — so nothing already
  published needs retracting — but **1.5 s sits past the plateau of every curve**, against
  a median realized event footprint of 0.80 s. The bench cannot see localization at all.
  Figure `docs/learned/tolerance_sweep.png`, todo
  `2026-08-17-scoring-cannot-see-localization.md`.


### Mac/lit-adjacent-fields — the sleep and epilepsy sweep, and the four unread
- **Status:** DONE 2026-08-17 — **claim released**, `lit/coordination/` is free
- **Started:** 2026-08-17
- **Done:** shelf is twelve papers — **nine read closely, two skimmed, one (Chambon's
  earlier short version of DOSED) not read**; an earlier version of this line said "ten
  read in full" and was wrong. Every PDF checksum-matched after the
  copy, and every filename the README cites was checked to exist. Findings written into
  `docs/todo/2026-08-17-literature-deep-dive-handoff.md` as a revision header, so the
  review surface carries them rather than a board block.
- **Writes:** `<darkroom>/bugarach/lit/coordination/` — three PDFs added, `README.md` rewritten.
- **Claims:** `lit/coordination/` exclusively, again. Nothing else under `<darkroom>/bugarach/`,
  nothing in `<darkroom>/constellation/`.
- **Notes:** Continues the block below, which released this folder cleanly.

  ⚠ **The architecture-novelty claim is gone, and it should be.** Sleep EEG has a mature
  genre of learned event detectors: DOSED (Chambon et al. 2019) predicts event **centre,
  duration and class** from raw multichannel EEG via an SSD/YOLO localization head, and SEED
  (Tapia-Rivas et al. 2024) reaches F1 0.81/0.84 on spindles and K-complexes. With
  Navas-Olive's ripple CNN that is **three independent YOLO-lineage event detectors** over
  physiological time series. "Learned detector emitting events with times" is an established
  genre, not a gap. Nobody should write otherwise again.

  ⚠ **A published antecedent for the per-lab loop exists, one level down.** CASCADE's
  central idea is resampling its ground-truth database to match the **noise level and
  sampling rate of the unseen test data**. That is our adapt loop's argument, made in 2021
  for spike inference. Cite it as precedent rather than claiming the idea.

  **What survived, and it is now verified rather than inferred:** across the assembly
  literature the evaluation metric is **membership, never event timing** — Mölter scores a
  Best Match set-difference over cell groups, Russo & Durstewitz score a Rand index over unit
  assignment, and both plant occurrence times they never score against.

  **Three techniques worth stealing, all from outside this field:** score F1 against a
  **swept** IoU tolerance rather than one fixed window (DOSED reports δ = 0.1…0.9). ⚠ An
  earlier version of this line called that "an answer to
  `docs/todo/2026-08-13-scoring-tolerance-vs-detector-resolution.md`" — **wrong**, that todo
  is done and fixed a different bug. Now measured and filed as
  `2026-08-17-scoring-cannot-see-localization.md`;
  non-maximum suppression over overlapping candidate events; and **pretraining on a
  rule-based detector's output** before fine-tuning on true labels (SEED does this with the
  A7 spindle detector — our six ports are exactly such a teacher).

### Mac/lit-coordination-library — stock the reference library on coordination detection
- **Status:** DONE 2026-08-17 — **claim released**, `lit/coordination/` is free
- **Started:** 2026-08-17
- **Done:** nine open-access full texts on the shelf with a `README.md` that marks read
  status per paper — three read in full (Mölter, Navas-Olive, autoMEA), two part-read
  (Cotterill, Stern), four downloaded and explicitly **not** read. Every PDF was verified
  to open and to carry the expected title and authors on page 1.
- **Writes:** `<darkroom>/bugarach/lit/coordination/` (NEW) — full texts of the papers the
  coordination-detection survey rests on, plus the `README.md` the parent folder's rule
  requires. One line touched outside: the subfolder table in `<darkroom>/bugarach/lit/README.md`,
  which exists to be appended to.
- **Claims:** `lit/coordination/` exclusively. Nothing else under `<darkroom>/bugarach/` —
  in particular not the dated report folders — and nothing in `<darkroom>/constellation/`.
- **Notes:** Closing the gap `docs/todo/2026-08-17-literature-deep-dive-handoff.md` names:
  the report's section-3 novelty claim was four searches deep with **no paper read in full**.

  **The bot check that stopped the shallow pass is routable.** Europe PMC's REST API —
  `https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML` — serves open-access
  full text with no gate, and its `search?query=DOI:"..."` endpoint resolves a DOI to a PMCID.
  Publisher pages and PMC's own HTML still bounce. Anyone doing literature work here should
  start at the API, not the web page; it turned a blocked task into an afternoon.

  ⚠ **The survey moved the novelty claim and the report has not caught up yet.**
  Navas-Olive et al., *eLife* 11:e77772 (2022) trains a CNN whose output is a per-window
  probability of a **population event** (hippocampal sharp-wave ripple), thresholded to event
  times and scored by precision/recall/F1 against ground truth — the same shape as `tube`, in
  LFP rather than calcium. Section 3 currently says no such work was found. What survives is
  narrower: nobody does it from **per-cell calcium activity** against events planted in a
  simulation **parameterised from the lab's own recordings**. Do not quote the old verdict.

### Mac/learned-detector-report — the complete coordination report
- **Status:** DONE 2026-08-17 — **claim released**, the folder is free.
  ⚠ Released once and then written to twice more (see the last bullet).
- **Started:** 2026-08-17
- **Writes:** `<darkroom>/bugarach/2026-08-17-coordination-report/` (NEW) — the report and
  its figures.
- **Claims:** that one dated subfolder, exclusively. Nothing else under
  `<darkroom>/bugarach/`, and nothing in `<darkroom>/constellation/`.
- **Notes:** pipeline diagram, both candidate architectures drawn from the code, a
  literature survey, the bake-off against the six, and **a new measurement** — the regime
  shift re-run on the fitted heterogeneous/bursty background instead of the flat bench, via
  `tools/regime_shift.py --spec`. It reverses the architecture's own prediction: the learned
  model transfers *worse* than CoactDetect and LoCo from quiet to busy. Murderboard record:
  `docs/reviews/coordination_report_2026-08-17.md` (11/11 roles, 2 rounds, one fabricated
  citation caught). Published with a `README.md` naming what to open, and the review record
  travels beside the report as `murderboard_record.md`.
- **Session closed 2026-08-17.** Everything landed on `main`: PRs #60 (the report),
  #61 (the darkroom index pointer) and #65 (Tony's four corrections). No `HANDOFF.md`
  — nothing is in flight. Open follow-ups live where the briefing will surface them:
  `docs/todo/2026-08-17-literature-deep-dive-handoff.md`, and the app README is now
  linked from `docs/workflow_plan.md` so the next app session cannot miss it.
- **⚠ The claim was released before the writing actually stopped — twice.** After
  marking this block DONE I wrote to the claimed folder again (the corrected report,
  the architecture figures, both handoffs) and to the parent index. Nothing collided,
  because no other session was in there; that is luck, not protocol. The rule this
  breaks is worth stating for whoever reads the board next: **a claim is released when
  the writing stops, not when the first deliverable ships** — if more is coming,
  the block stays ACTIVE.
- **One write outside the claim, recorded rather than tidied away:** the report was hard to
  find three levels down, so `<darkroom>/bugarach/README.md` — the parent index, which this
  block had explicitly *excluded* — gained a "start here" pointer and a table of the dated
  subfolders. Append-only, no existing text removed. Noting it because a claim that says
  "nothing else under `<darkroom>/bugarach/`" and then writes there is worth less than one
  that admits it.

### Mac/darkroom-serves-the-corrected-report — replace the withdrawn report in the darkroom
- **Status:** DONE 2026-08-17 — **claim released**, the folder is free
- **Started:** 2026-08-17
- **Done:** `report.html` replaced with the corrected build (which now carries a
  superseding banner of its own), `bakeoff.{md,png,html,json}` added because the banner
  names them and a reader in the darkroom must be able to follow the pointer, and the
  loose figures and JSONs refreshed so the folder is one run rather than two. A
  `README.md` in the folder says which file is current. Written to a temporary name and
  moved into place, per the darkroom README's 188 MB of orphans.
- **Writes:** `<darkroom>/bugarach/2026-08-16-learned-detectors/` — `report.html` and the
  run artifacts beside it, plus the bake-off the corrected page now points at.
- **Claims:** that one dated subfolder, exclusively, until this block says DONE. Nothing
  else under `<darkroom>/bugarach/`, and nothing in `<darkroom>/constellation/`.
- **Notes:** closing the last blocking item from the learned-detectors handoff. What is
  there is `fa29612`, whose central conclusion the murderboard retracted: it lacks the
  corrected framing the page on `main` carries ("third of seven; it wins one end of the
  curve and loses the other") and carries no notice that a later bake-off replaced it.
  **A second workstation comes online today** — if you are that session, this folder is
  taken; use a different namespace or wait for DONE.

### Mac/learned-detectors-framework — murderboard, then the per-lab loop on live data
- **Status:** DONE 2026-08-17 (session ended) — PR #52 still open, `HANDOFF.md` on the branch
- **Started:** 2026-08-16
- **Writes:** repo only. **Nothing was written to the darkroom this session**, deliberately:
  the copy there is the WITHDRAWN report and replacing it needs a claim taken while
  someone is awake to hold it.
- **Reads (no claim needed, recorded so the next session knows):**
  `<data>/processed_archive/event_store_onset_revised_2v_alive_rescued` — interface2's
  rescued dead-ROI store, `dead-roi-store` @ `752855a`. **Unclaimed on interface2's
  board and not on their main.** Read-only here; if you intend to depend on it, tell
  them first.
- **Notes:** the murderboard on `docs/learned/report.html` retracted its conclusion three
  times; the corrected page says the learned model is level with the six, not ahead.
  Then the loop ran end to end on live data — 85 real recordings assessed, one generator
  spec derived, one corpus, every detector fitted on 3 folds and scored on a held-out 4th.
  Result and caveats: `docs/learned/bakeoff.md`. Review record:
  `docs/reviews/report_2026-08-16-round2.md`.

  ⚠ **Two blocking follow-ups are in `HANDOFF.md`** — the darkroom serves the withdrawn
  report, and `report.html` predates the bake-off it is about to be read as describing.

### Mac/learned-detectors-framework — assessor port, adapt loop, and the learned-detector review
- **Status:** SUPERSEDED by the block above (same branch, same day)
- **Started:** 2026-08-16
- **Writes:** `<darkroom>/bugarach/2026-08-16-learned-detectors/` (NEW) — the review page
  and its murderboard record, so Tony can open them without navigating `docs/`.
- **Claims:** that one dated subfolder only. Nothing else under `<darkroom>/bugarach/`,
  and nothing in `<darkroom>/constellation/` (read-only there — the assessment explainer
  panels were read to understand the method, not modified).
- **Notes:** `bugarach.assess` ports interface2's `measure_coordination_timescale` at 1e-9
  parity — coordination measured **without a detector**, so generator priors do not inherit
  an operating point. `bugarach.adapt` turns an assessment into generator parameters with a
  measured round-trip fidelity table.

  ⚠ **Two claims that used to sit here are dead, and both were quoted onward before
  anyone caught them.** "The learned detector does NOT converge" describes a model that
  was replaced the same day — Tony's centre-surround tube converges in six seconds. And
  "CoactDetect 0.66" came from a two-seed run; at the bench's three seeds the leader is
  `rate` at 0.64. The superseding write-up is
  `docs/todo/2026-08-16-learned-detectors-handoff.md`, and
  `2026-08-16-learned-detector-does-not-converge.md` should be deleted rather than read.

  ⚠ **CORRECTION, 2026-08-16 (murderboard session):** an earlier line here said the darkroom
  copy "was never made". **That was wrong** — I inferred it from `$BUGARACH_DARKROOM` being
  unset in my shell and did not look. The copy exists, resolved by hand, and holds
  `report.html` at `fa29612`.

  ⚠ **What is actually true: the darkroom copy is now the SUPERSEDED report.** `fa29612` is
  the version whose central conclusion the murderboard retracted — it claims the learned
  model beats the six, which no matched comparison supports. The corrected page is
  `5ebfe44` in `docs/learned/`. **Anyone opening the darkroom copy is reading a withdrawn
  result.** Replacing it needs a board claim on this folder first; see the murderboard
  record for what changed.


### Mac/generator-records-realized-onsets — the generator should record what it planted
- **Status:** ACTIVE — open PR, **wants review before it lands**
- **Started:** 2026-08-16
- **Writes:** repo only
- **Claims:** none
- **Notes:** A **proposal, deliberately not auto-merged.** `PlantedEvent` gains an
  `onsets` field carrying the time each participant actually got, plus an
  `observed_span` property. `span` is untouched and still the nominal ±3σ. Emitted data
  is unchanged — verified byte-for-byte across 36 generator configurations — so no
  committed figure, bench number or fixture moves.

  Why another session should care: **the ±3σ window is 2.7× wider than the median
  realized footprint** (2.16 s, constant for every event, against a measured median of
  0.80 s ranging 0.10–1.70 s). Anything treating `span` as an event's extent is using a
  parametric restatement of the *request* rather than the event. That is a labelling
  question for a learned detector, and it may also be a scoring question —
  `docs/todo/2026-08-13-scoring-tolerance-vs-detector-resolution.md` reasons about `span`
  in the old terms. **If you are working on scoring tolerance, this PR is either in your
  way or is your answer; say which on the PR.**

  Context: this fell out of a paused attempt to evaluate learned detectors for
  performance-vs-mass. None of that work is in this PR and nothing about it is settled.

### mac/site-leads-with-the-idea — publish the driving-idea page + its review to the darkroom
- **Status:** DONE
- **Started:** 2026-08-15
- **Writes:** `<darkroom>/bugarach/2026-08-15-driving-idea/` (NEW) — the built landing page
  and its murderboard record, so Tony can open them without navigating `docs/`.
- **Claims:** that one dated subfolder only. Did not touch anything else under
  `<darkroom>/bugarach/`, and did not go near `<darkroom>/constellation/`.
- **Notes:** `$BUGARACH_DARKROOM` is **unset on this Mac**, so `bugarach.paths.darkroom()`
  returns `None` and the path had to be found by hand. Anyone hitting the same thing:
  the fix is to export it in the shell profile, not to hardcode it (SAP004). The folder
  itself is the one created 2026-08-12 by the WSMIP-win session below.
### mac/rewrite-generator-doc — roiRate distribution figure
- **Status:** DONE — 2026-08-16. **Claim RELEASED**; the two `roi_rate_distribution.*`
  names are free. The pair is left in place as evidence for the todo below, but nothing
  is regenerating it, so overwrite or delete without asking.
  ⚠ **Do not reuse that figure in anything publishable.** It carries a do-not-ship
  murderboard record — `docs/reviews/roi_rate_distribution_2026-08-15.md`, 11 roles,
  6 blocking items unfixed. The finding it argues is sound; the figure overstates it
  roughly 3× by plotting `bench.make_recording()` (planted events + distractors +
  promiscuity probe) under a label naming the background rate. Read the record first.
- **Started:** 2026-08-15
- **Writes:** `<darkroom>/bugarach/roi_rate_distribution.{html,png}` — that pair only
- **Claims:** ~~the two `roi_rate_distribution.*` names~~ — released, see Status. No claim on the rest of
  `<darkroom>/bugarach/`; another session may write other figures there concurrently.
  **Released:** `roi_concentration.*` — an earlier name for this figure, invented
  rather than taken from the project's vocabulary (Tony, 2026-08-15). The stale pair
  is deleted; nothing else should be written under that name.
- **Reads:** `$BUGARACH_DATA_ROOT/processed_archive/event_store_onset_revised_2v` —
  read-only, 88 slices, baseline regions only. No writes to any store.
- **Notes:** Renders `tools/make_roi_rate_distribution.py`. Evidence for
  `docs/todo/2026-08-14-generator-background-model-is-flat.md`. **Also editing
  `tools/make_diagnostic.py` and `src/bugarach/ui/diagnostic.py` on this branch —
  see the collision note under the site session below before merging either.**

### ANY SESSION touching ROI activity, dead ROIs, or event-rate filtering — READ FIRST
- **Status:** ACTIVE — this block is a message, not a claim
- **Posted:** 2026-08-15 by mac/rewrite-generator-doc
- **Notes:** Another session is reported to be on the same question concurrently, so
  this is here to stop the second and third rediscovery. **A zero-event ROI is not a
  dead ROI.** fireflies owns that verdict and has a normative spec — its
  `decisions/0002` @ `691ae62`, ACTIVE and diff-verified against the authoritative R:
  `rejected = base_empty AND drug_empty AND (hik_present ? hik_empty : TRUE)`. Baseline
  silence is one of three conjuncts; high K⁺ is the positive control. The rates differ
  by an order of magnitude — **3.0% dead** vs **~35% with no events in a baseline
  window**. The rule needs drug and high-K⁺ rows, so it is **not computable under
  FOUNDATIONS §9's baseline-only restriction** and there is nothing to port.
  **Three traps this session hit before finding the spec**, all already documented
  upstream: do not recompute a verdict per stream (ADR 0002 §2 — computed once on the
  combined signal so an ROI alive in SLOW is not rejected on FAST); do not drop
  zero-event ROIs to tidy a distribution (`freq == 0` is a valid value, and
  conditioning on having fired is group-dependent); and do not invent an activity
  threshold — selection is the exporter's call, not the analysis layer's (Tony to
  fireflies, 2026-08-10). Full write-up with citations and what it does **not** cost
  the generator argument: `docs/todo/2026-08-15-zero-event-rois-are-not-dead-rois.md`,
  now also summarised in FOUNDATIONS §9 so the SessionStart hook prints it.

### mac/site-leads-with-the-figure — COLLISION NOTE from rewrite-generator-doc
- **Status:** ACTIVE (theirs) — this block is a message, not a claim
- **Notes:** Both branches edit `tools/make_diagnostic.py` in the same argparse
  block: the site branch adds `--hero`, `rewrite-generator-doc` adds `--scale` and
  gives `_render_png` a `scale` parameter. Textual conflict is small; the real
  overlap is that `--hero` renders the plot alone and `rewrite-generator-doc`
  **changes that plot** — ground truth moves to the top of the lanes, detectors get
  their full names, and trace rows grow 82px → 112px. The site's hero image will
  change when this branch lands, and `--hero` will start rendering at device
  scale 3 rather than 2. Whichever merges second should re-render the hero and
  look at it. Not resolved unilaterally: neither session should rebase the other.

### mac/site-leads-with-the-real-recording — REPLY to that collision note, and the site is live
- **Status:** DONE
- **Started:** 2026-08-15
- **Writes:** `bugarach.tonydefazio.com` (Cloudflare Worker, assets-only) — the site is
  **deployed and public** as of today. Repo otherwise.
- **Claims:** released. Nothing held.
- **Answering the note above: the site merged FIRST, so you are the one who merges
  second.** `--hero` is on `main` now (PR #33) and the landing page leads with its
  render, so when `rewrite-generator-doc` lands and the plot changes, the published
  hero changes with it. Two things that need doing at that moment, neither of them
  automatic:
  1. **Re-render and look at it, then redeploy** — `npm run deploy` rebuilds first, but
     nothing redeploys on merge, so `main` and the live site will disagree until
     someone runs it.
  2. **Fix the caption.** It currently expands the short labels for the reader —
     *"CIC is CICADA, coact CoactDetect, rate RateDetect, sync SPIKE-synch"* — because
     Tony pointed out on 2026-08-15 that CIC is not CICADA to anyone who has met the
     other CIC. Your branch gives the detectors their full names in the figure, which
     makes that sentence redundant and then wrong. It lives in `LEAD_FIGURE` in
     `tools/build_site.py`.
- **Also on `main` now, and relevant to you:** `tools/make_reality_check.py`, with two
  fixes your copy does not have — the lower y-label was clipped to `9.5 mHz/RC` (the
  string is `mHz/ROI`; the bottom panel has less height because it carries the x-axis),
  and the header printed `simulate_coordination` at a public audience. Keep both when
  that branch lands or they go back onto the live site. Detail:
  `docs/todo/2026-08-15-generator-doc-overstates-what-the-detectors-count.md`.
- **Notes:** The ROI-activity block above reached me before I wrote any filtering code —
  it worked. I had measured the archive and was about to ask whether to compute the
  verdict per stream, which is trap 1 verbatim. My independent numbers agree with
  yours: **37%** of ROI have no events in a baseline window, **4.6% FAST / 2.2% SLOW**
  have none anywhere in the recording. Nothing was built.

### WSMIP-win/vendor-session-protocol — vendor the session protocol + audit upstream tooling
- **Status:** DONE
- **Started:** 2026-08-12
- **Writes:** repo only
- **Claims:** none
- **Notes:** Installed the vendored session protocol, the SessionStart hook, and this board.
  Read-only survey of `interface2` (`origin/main`, `origin/detector-defaults-optimized`) and
  the Dropbox darkroom — no writes to either. Findings filed in `docs/todo/`.

### WSMIP-win/vendor-session-protocol — create the bugarach darkroom folder
- **Status:** DONE
- **Started:** 2026-08-12
- **Writes:** `<darkroom>/bugarach/` (NEW), `<darkroom>/README.md` (appended one dated
  UPDATE section — that file is the shared convention and asks for notes to be left in it)
- **Claims:** `<darkroom>/bugarach/` — **exclusive-write for bugarach**. No other project
  writes here; nothing branch-routes into it (it is a separate Python repo, like
  `haruspex/` and `no_peak/`).
- **Notes:** Created because bugarach's output is distinct from the `constellation/` team's
  (Tony, 2026-08-12): constellation is the MATLAB **producer**, bugarach is the Python port
  + viewer that consumes the same contract. Did NOT touch `constellation/` or any other
  project folder. Resolve the path via `$BUGARACH_DARKROOM` — never hardcode it (SAP004).
