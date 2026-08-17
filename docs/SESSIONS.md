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
- **Status:** ACTIVE
- **Started:** 2026-08-15
- **Writes:** `<darkroom>/bugarach/roi_rate_distribution.{html,png}` — that pair only
- **Claims:** the two `roi_rate_distribution.*` names. No claim on the rest of
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
