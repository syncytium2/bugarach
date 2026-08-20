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

### ANY SESSION touching the export contract — interface2 is reviewing it RIGHT NOW
- **Status:** ACTIVE — this block is a message, not a claim
- **Posted:** 2026-08-20
- **Notes:** `docs/export_for_producers.md` — the one-page contract addressed to the
  producer, rendered to `<darkroom>/bugarach/export_for_producers.html` — is **with
  interface2 for review**. Do not revise it unilaterally while that is open: a producer
  reading one version while this repo edits another is how a contract stops being one.
  **Expect it to come back changed**, and expect the change to be right — they know things
  about their pipeline the document assumes. Whatever returns needs a round appended to
  `docs/reviews/export_for_producers_2026-08-20.md`.
  The full spec `docs/export_folder_spec.md` is **not** what was sent, and its revision 6
  stands regardless: the folder is the whole input, selection is the producer's, and no
  exclusion filter goes in this repo.

### Mac/contract-trusts-the-folder — a dedicated home for the source exports
- **Status:** ACTIVE
- **Started:** 2026-08-20
- **Writes:** `<dropbox>/data/bugarach/` — **creating it.** A COPY of the three export
  folders now under `<dropbox>/data/exports/bugarach/` (30 MB of CSV). The originals
  stay exactly where they are, because interface2's `generate_export_folder.m` writes
  there and moving its target would break their next export silently.
- **Claims:** `<dropbox>/data/bugarach/` for the duration. Nothing in `darkroom/` —
  **source data does not belong there**, that folder is review artefacts and figures.
  Nothing under any store path, nothing written to `exports/`.
- **Notes:** Tony, 2026-08-20, after two recordings the lab had marked unusable
  reached published numbers. The exporter had honoured the flag and said so in its
  `PROVENANCE.md`; the numbers came from analyses that opened `.mat` stores and never
  read the folder at all. This gives the exported corpus one address so a tool has no
  excuse, and a repo-wide gate follows.
### Mac/darkroom-corrected-synfire — the corrected synfire numbers, in their own folder
- **Status:** DONE 2026-08-20 — **written, claim released**
- **Started:** 2026-08-19
- **Writes:** `<darkroom>/bugarach/2026-08-19-synfire-roi-corrected/` — **one new subfolder.**
  Both `--keep-silent-rois` (pre-fix) and corrected runs of each stream, both figures, and
  a README saying which is which. **Plus ONE new file at the root of `bugarach/`**:
  `synfire_README.md`, a signpost beside the synfire session's two JSONs — see below.
- **Claims:** ~~that ONE subfolder~~ — **released.** Written and not being regenerated. It
  holds `README.md`, `v2_analysis_window/` and `periods_raw_baseline/` (pre-fix and
  corrected, both streams, all seeded), and both figures.
- **Tony's decision, 2026-08-20: both sets stay, side by side, with a README.** The two
  root files are NOT superseded and NOT deleted. The only thing added beside them is
  `synfire_README.md`, because a reader opening `bugarach/` would otherwise see the old
  JSONs with nothing to say a corrected set exists one folder down. It adds a signpost and
  changes no result.
- **DOES NOT TOUCH** `<darkroom>/bugarach/synfire_{fast,slow}_relabel.json` at the root
  (2026-08-19 19:51). Those are the synfire session's output and carry the **pre-fix**
  numbers — the ones the handoff and `docs/todo/2026-08-19-synfire-measured-and-what-it-cost.md`
  quote. Overwriting them would silently restate a published result, which is a decision
  and not a cleanup. **Whoever owns that todo should decide whether the root files are
  superseded**; until then both are on disk and the new README says how they differ.
- **Reads:** BOTH export folders, read-only —
  `exports/bugarach/2026-08-17_revised_2v_v2` and `..._2026-08-18_revised_2v_periods`.
- **A windowing trap found on the way in, which anyone comparing synfire numbers must know.**
  The two exports do not score the same window. `2026-08-17_revised_2v_v2` carries
  `analysis_start_sec`/`analysis_end_sec`, so the scan uses the producer's analysis window;
  `2026-08-18_revised_2v_periods` carries **no `analysis_*` columns at all** (deliberately,
  per the windowing decision), so the scan falls back to the raw baseline period. The root
  `synfire_*_relabel.json` files were built from the **v2** export. A first pass here used
  the periods export, which made the corrected numbers non-comparable to the ones they
  correct — on the slow stream one shared recording differs by 0.377 in the indicator from
  windowing alone, larger than anything the ROI fix does. Everything published in this
  subfolder is therefore run on **both** exports, and the README says which is which.
- **THREE defects, not one, and two of them reached published numbers.** PR #152 carries
  the first; the follow-ups on `roi-and-synfire` carry the rest.
  1. PySpike returns `(e=1, m=1)` — a *perfectly ordered* pair — for two EMPTY trains, and
     the scan fed it every ROI: 1941 of 5260 (ROI, stream) pairs, 37%. Note that "empty
     here" is not "dead". Only **122** are silent across the whole recording — matching the
     export's own `PROVENANCE.md` exactly — and the other **1819** fire outside the
     baseline window.
  2. **Nothing reproduced.** The seed was `abs(hash(slice_id))`, and Python salts string
     hashing per process, so every run drew different surrogates while the docstring
     promised otherwise. Now `zlib.crc32`; a rerun is field-for-field identical, asserted
     in subprocesses with hash randomisation forced on. **The synfire session's published
     files predate this, so they are not re-derivable** — not wrong, but not reproducible.
  3. `20240723_22` slow — 3 events across 3 trains — has no surrogate spread and was
     reported as the corpus maximum: 0.774 **before** the ROI fix and 1.000 after. Rows now
     carry `defined` and summaries exclude them. Honest maxima 0.414 and 0.625.
- **What the fix does to the answer.** The tally moves +3 / -1 / -2 / +1 across the four
  (export x stream) combinations — no consistent direction, every flip a recording on the
  alpha=0.05 line, and the conclusion untouched. Two effects ARE consistent across both
  exports and are the quotable ones: the upper tail of the indicator (p90 |change| 0.04
  fast / 0.09 slow, against medians of 0.03 / 0.08), and `rho(indicator, spikes)` weakening
  from -0.74/-0.39 to -0.57/-0.19 — which is the synfire handoff's **third reason** for not
  quoting the slow group result.

### Mac/deploy-record — the webapp merge train landed, and the site now serves it
- **Status:** DONE 2026-08-19 — deployed and verified; **claim released.**
- **Started:** 2026-08-19
- **Writes:** **the PUBLIC SITE** — `bugarach.tonydefazio.com`. Nothing to the darkroom,
  nothing under `$BUGARACH_DATA_ROOT`.
- **Claims:** the site deploy, taken from released and **released again on the way out**.

**What landed.** PRs **#128 → #129 → #130 → #131**, `main` @ `19a320b`. The browser now
runs **five of the six** detectors — rate, SCE, coact, LoCo, sync — leaving CICADA. On
merged `main`: 655 passed, 1 skipped, including all **97** browser parity tests, which
actually ran here because this Mac has chromium (CI still skips them; PR #148 is fixing
that). #133 was left alone — another session owns it.

**They were a stack, and that has a trap.** #129 was based on #128's branch, #130 on
#129's, #131 on #130's. **GitHub does not retarget a stacked PR when its base merges**, so
every one after the first needed `gh pr edit <n> --base main` or it would have merged into
a feature branch while reporting success. Worth knowing before the next stack.

**Deployed, and the live page was checked rather than assumed.** `tools/build_site.py` ran
from `19a320b`; the publish gate passed and `site/viewer.html` is **byte-identical** to
`docs/site/raster_viewer.html` — copied, not transformed. Tony ran `npx wrangler deploy`
and `tools/audit_deployed_page.py`, and **the served page fetched nothing but itself** —
the privacy promise holds as served, not merely as written. That audit is the only check
positioned to see what Cloudflare adds after the upload, which is how the injected Web
Analytics beacon was caught; it fires on the live URL in chromium, and `curl` cannot
replace it because the injection was UA-gated.

**Separately confirmed on the live page: five detectors are being offered** — RateDetect,
SCE, LoCo, CoactDetect, SPIKE-synch. The audit proves the page is quiet; it says nothing
about *which* page shipped, and those are different questions. So `main` and
`bugarach.tonydefazio.com` now agree.

**⚠ A standing instruction on this board is now obsolete.** Two blocks below say deploys
run from `bugarach-worktrees/deploy-site` and warn to *"check what it is checked out at
before deploying, every time"*, because it was a **detached HEAD** that did not follow
`main`. That worktree was merged and clean and this session removed it in the Phase-0
sweep. **Deploys now run from the primary checkout, which does follow `main`** — which is
the safer arrangement and removes the republish-the-wrong-commit hazard the warning
existed for. `docs/deploy.md` never mentioned the pinned worktree, so nothing there needs
changing; the warning lived only here.

**Also swept**, so nobody hunts for them: worktrees `detector-table`, `webapp-loco`,
`webapp-coact`, `webapp-sce`, `contract-check` and `deploy-site` removed — all merged,
clean, and unclaimed on either board — and those four remote branches deleted.
`preview-everything` was **pushed to origin first**; it had four commits on no remote, and
its worktree and two uncommitted files were left untouched, because discarding another
session's work is not a sweep.

### Mac/modularity-on-fast — run the connectivity project's modularity instrument on the FAST stream
- **Status:** DONE 2026-08-19 — **claim released**
- **Started:** 2026-08-19
- **Writes:** `<darkroom>/murmuration/bugarach-fast-modularity/` — **one new subfolder**,
  holding `eval_modularity_null_{fast,slow}.csv`. **Nothing at the root of `murmuration/` is
  written**, so the connectivity project's own `eval_modularity_null_slow.csv` is untouched.
  (The original plan was to drop the fast CSV at their root under their naming convention;
  changed on finding that the slow re-check has to be written too, and overwriting their slow
  file is not mine to do.) Also `<darkroom>/bugarach/` for the bugarach-side copies.
- **Claims:** ~~that ONE subfolder~~ — **released**. Both CSVs are written and nothing is
  regenerating them. `murmuration/` is the connectivity project's output folder, not
  bugarach's, so the claim was deliberately a new namespace inside it rather than any existing
  name; their `eval_modularity_null_slow.csv` was never touched and still carries its July
  timestamp.
- **Reads:** `$IF2_DATA_ROOT/processed_archive/event_store_onset_revised_2v` — read-only, the
  same 85 recordings the slow run used.
- **interface2:** branches `bct-modularity-fast` **from** `bct-connectivity-cont`, in its own
  worktree. **Does not edit `bct-connectivity-cont`.** The change generalizes
  `eval_modularity_null.m` to take a channel argument, **defaulting to `slow` so their
  behaviour is unchanged**, and is offered back rather than pushed into their branch.
- **Notes:** closes the open item from PR #135 — the assembly negative was established for
  slow only because modularity had never been run on fast. The script hardcodes `slow` with
  a stated reason ("the rate-independent marker", ADR 0011) and the connectivity handoff
  treats FAST as a negative control — but **both of those are about the GROUP comparison**
  (GDX vs intact), which fails rate-, node- and Δt-matching on fast. `above_null_Q` is a
  WITHIN-slice test of Q against that slice's own jitter surrogates, which hold node count,
  event counts and sparsity fixed, so the matching objection does not reach it. Run and
  reported on that basis; if the connectivity project disagrees, the file is one CSV and
  deleting it costs nothing.
- **A blocker found on the way in, which belongs to interface2 rather than here.** The
  connectivity pipeline's dead-ROI roster path is hardcoded to `2R/2026-07-13/`, and the R
  team moved that entire vintage to `2R/QUARANTINE/` — unnormalised treatment labels, 33% of
  rows beyond treat1, described as loading cleanly and producing plausible WRONG answers. So
  **`eval_modularity_null` cannot currently run at all without restoring a quarantined
  input**, and the published `eval_modularity_null_slow.csv` was built from it. The successor
  chain is 2026-08-10 (itself superseded — zero high K+ rows, silently disabling the
  depolarization safeguard that rescues 176 ROIs) then **2026-08-15**, current. This run adds
  an additive `IF2_DROI_CSV` full-path override, leaves the stale default alone, and uses the
  current roster — and re-runs SLOW on it too, so the fast answer is compared against a slow
  number computed the same way rather than against the quarantined-roster one.
- **RESULT, for anyone who needs it without reading the report:** no modular structure above
  null in **either** stream — 3 of 78 fast recordings (3.8%), 2 of 77 slow (2.6%), against the
  ~5% the 95th-percentile threshold gives by chance. Re-running slow on the current roster
  reproduced the published file exactly, so **`eval_modularity_null_slow.csv` stands** despite
  its roster having been quarantined since.
- **FOR THE CONNECTIVITY PROJECT — a branch is waiting, not merged.** interface2
  `bct-modularity-fast` (GitLab, pushed 2026-08-19) makes the channel an argument with the
  default unmoved, and adds an `IF2_DROI_CSV` override because **your default dead-ROI roster
  path now points into `2R/QUARANTINE/`** — the pipeline cannot run clean without it. Opening
  the MR is yours; so is deciding whether to repoint the default.
- **A finding that reaches every deliverable in this repo, not just this one:** the lab's
  `exclude` column in `indiegroups_db4.xlsx` had never been read by anything here, and two
  withdrawn recordings were inside every published assembly number. See
  `docs/todo/2026-08-19-lab-exclusions-were-never-consulted.md`.

### Mac/close-the-assembly-question — the three steps that close the assembly negative
- **Status:** DONE 2026-08-19 — **claim released**, merged as PR #135
- **Started:** 2026-08-19
- **Writes:** `<darkroom>/bugarach/` — `assembly_closed.{html,png}`, `assembly_summary.html`,
  `assembly_report.html` (**overwrites** the 2026-08-18 report, deliberately: it is the same
  document reframed to lead with the negative, per its own handoff). Nothing in
  `<darkroom>/constellation/`, nothing in `murmuration/`, nothing under `$BUGARACH_DATA_ROOT`.
- **Claims:** ~~those four names in `<darkroom>/bugarach/`~~ — **released**; all four are
  written and nothing is regenerating them. No claim was ever held on the rest of the folder.
- **Reads:** `$BUGARACH_DATA_ROOT/processed_archive/event_store_onset_revised_2v` (88) and
  `..._onset_pensub_revised_2v` (85, a strict subset) — **read-only**, both streams, baseline
  regions only. No writes to any store.
- **Notes:** `BUGARACH_DATA_ROOT` was **unset** in this session's environment and had to be
  located; it resolves to `~/Library/CloudStorage/Dropbox-<org>/<person>/data` on this box.
  The crosstalk comparison reads `.mat` on **both** sides because no export folder exists for
  the penumbra-subtracted recordings — so its tallies (49/40 testable) differ slightly from
  the export-folder run's (48/38), which honours the producer's analysis window. That is a
  windowing difference, not a measurement one, and it is stated in the report.
- **Left open for whoever picks this up:** the **fast stream has no modularity measurement**
  (`eval_modularity_null_slow.csv` has no fast counterpart), so the assembly negative is
  established for slow only. The murderboard caught the report asserting it for both. Full
  list of residual flags: `docs/reviews/assembly_summary_2026-08-19.md`.

### Mac/dt-required-at-load — FOUNDATIONS §6 reversed: dt is required, not defaulted
- **Status:** DONE 2026-08-18 — merged. Opened 2026-08-16 and sat three days, during
  which `main` said the opposite of the decision and every session read the old rule.
  Brought up to date with `main` and landed by a later session at Tony's direction.
- **Started:** 2026-08-16
- **Writes:** repo only
- **Claims:** none
- **Notes:** **Read this before writing anything that loads data.** FOUNDATIONS §6 used
  to say `grid_dt` is the caller's responsibility at detection time and that omitting it
  falls back to 0.1 s with a warning. Tony, 2026-08-16: *"we cannot allow data loading
  without the user specifying a dt."* §6 now requires it at the **load boundary**, and
  refusing beats defaulting — a warning fires after the number already exists.

  Doc-only so far; the code still falls back. The gap is
  `docs/todo/2026-08-16-dt-must-be-required-at-load.md`. Until it closes,
  `GridDtNotSetWarning` still fires and still must not be silenced. **The six ports keep
  their seconds-valued MATLAB parameters — parity is untouched by this.**

### Mac/— — lit folder in the darkroom
- **Status:** DONE
- **Started:** 2026-08-16
- **Writes:** `<darkroom>/bugarach/lit/` (NEW), `<darkroom>/bugarach/lit/DL/` (NEW)
- **Claims:** none — new namespace, nothing else writes there
- **Notes:** A reference library for papers a bugarach design decision actually rests on,
  each entry naming the decision. Seeded with Deep Sets (Zaheer 2017) and PointNet (Qi
  2017), which bear on set-structured input and the distinct-ROI rule. Undated on purpose
  — everything else in `bugarach/` is a dated review artifact; a citation does not expire.
  Rule in `lit/README.md`: a PDF with no index entry is indistinguishable from one someone
  downloaded and forgot. Fetch by hand — murderboard's `fetch_paper.py` is deliberately
  not vendored (SAP004, personal paths).
### Mac/windowing-design — the windowing decision, written down because two sessions collided
- **Status:** DONE 2026-08-18 — nothing held, nothing claimed
- **Writes:** repo only — ONE new file,
  `docs/todo/2026-08-18-windowing-default-and-the-three-delta-interface.md`.
  **`docs/export_folder_spec.md` was deliberately NOT touched**, because another session
  was cleaning it up at the same time and a design note is not worth a conflict in the
  document it describes.
- **⚠ READ THAT TODO BEFORE EDITING THE EXPORT SPEC.** Tony decided the windowing default
  on 2026-08-18 and it settles `2026-08-17-windowing-convention-is-not-optional.md`, which
  had been open since the contract shipped: with no `analysis_*` columns bugarach applies
  **no protocol at all** and uses the full-length baseline, rather than this project's
  wash-in delay, caps and `"hi"`-substring exemption. A three-delta interface lets a user
  state windows they did not send. None of it is built.
- **For the spec cleanup specifically:** the todo says which 22 lines of the current spec
  are mine and should be cut to their normative core without asking, gives the 260→444-line
  growth table, and proposes splitting the revision-header stack into a `CHANGES` section.
- **Also recorded there, and nowhere else in this repo:** interface2 replied to the export
  request on 2026-08-17 (revised 2026-08-18) on their unmerged `bugarach-export-folder`
  branch, with four spec corrections we have not applied — including that our `baseline`
  overwrite mechanism is wrong and `chelerythrine` does not contain `hi`. Their todo still
  cites spec revision 2; we are on 4.
- **Landed separately:** PR #123, the guards on `supplied_region_windows`. A producer
  supplying `analysis_*` was routed past every check on region bounds; a window of
  −100,499 s passed `bugarach check` and reached the detectors. Universal checks only —
  FOUNDATIONS §4 forbids applying this project's HALT guards to a conforming folder, and a
  test asserts the non-contiguous, non-zero-based folder still loads.

### Mac/park-infra-ideas — two infrastructure ideas parked in the darkroom
- **Status:** DONE 2026-08-18 — **claim released**
- **Writes:** `<darkroom>/ideas/` — **created it**. Two files, plus a README.
- **Claims:** `<darkroom>/ideas/` only. Nothing in `bugarach/`, `constellation/`, `needs/`.
- **Notes:** parked rather than built, at Tony's direction — the repo keeps a todo
  pointing at them so they are findable without being work in flight.

### Mac/needs-mechanism-gate — a cross-repo proposal in a NEW shared darkroom folder
- **Status:** DONE 2026-08-18 — **claim released**, both files written
- **Writes:** `<darkroom>/needs/` — **created it**. One file:
  `mechanism-changes-need-a-gate.md`, plus a `README.md` saying what the folder is for.
  Nothing in `<darkroom>/bugarach/`, nothing in `<darkroom>/constellation/`, nothing
  under `$BUGARACH_DATA_ROOT`.
- **Claims:** `<darkroom>/needs/` for the duration. It is a **new top-level folder in a
  mount every repo on every machine can see**, which is a wider claim than a file inside
  our own folder — if another estate is also inventing a cross-repo review convention,
  this is where the collision happens. `0-REVIEW/` was checked first and is slice
  submissions, not process proposals, so this does not duplicate it.
- **Notes:** the document invites other repos to comment, so treat it as shared and
  append rather than overwrite — the folder README says so too. Tony asked for it by
  name after rejecting CLAUDE.md as the vehicle for the same rule.
- **Done:** `needs/README.md` and `needs/mechanism-changes-need-a-gate.md`. The
  proposal went through the murderboard first (11/11 roles, 2 blind rounds); its
  headline claim did not survive role 1 and was replaced with one the commit history
  actually shows. Run record in `docs/reviews/`.

### Mac/assembly-membership — synfire order measured; the assembly half is closed elsewhere
- **Status:** DONE 2026-08-19 — claims released. `HANDOFF.md` on `main` covers the live
  half (synfire). The assembly half was **closed by another session** — its record is
  `docs/assembly_report.md` + `docs/reviews/assembly_summary_2026-08-19.md`, and the
  numbers this block once carried are superseded.
- **Wrote (darkroom, claim released):** `synfire_fast_relabel.json`,
  `synfire_slow_relabel.json`, alongside the earlier `assembly_*` files.
- **The one thing worth carrying to any new measure here:** the standing per-ROI
  circular-shift null answered the wrong question for BOTH measures attempted this week.
  It calls 60% of order-free generated recordings synfire-significant, because it destroys
  the coordinated events and so is beaten by any recording that has them. Run the
  order-free generated control before believing a number, and prefer an event-preserving
  null.
  answer and the three steps that close it. Delete that file when they are done.
- **Started:** 2026-08-18
- **Writes:** `<darkroom>/bugarach/assembly_answer.{png,html,json}` (NEW). Nothing else
  under `<darkroom>/bugarach/`, nothing in `<darkroom>/constellation/`.
- **What the next session should know.** The corpus-level result stands: co-participation
  beyond per-ROI rate in 27 of 48 fast recordings and 27 of 38 slow, against a measured
  2.5% control rate. The **group difference is withdrawn** — identical planted assemblies
  at each group's own event count reproduce it, so it was detection power. Do not restate
  it without matching on coordinated-event count first.
- **Two open leads, both filed as todos:** spatial adjacency is unchecked and is the most
  likely alternative explanation for the surviving result; and synfire order is a distinct
  question from assemblies with a cheaper port than PCA/ICA, blocked only on papers Tony
  is fetching.
- **Claims:** RELEASED. Held `assembly_answer.*`, `assembly_membership.*` and
  `assembly_report.html` while writing them; all are written and nothing is pending on
  those names. Regenerate with the four commands in the report's own reproduce block. The earlier `assembly_power.*` claim from this machine is
  released.
- **The report is in the darkroom**, not only in the repo: `assembly_report.html`, one
  self-contained file with both figures embedded. It landed there late — the builder
  required `--out` and had no darkroom default, unlike every figure tool here, so the
  first build reached `docs/learned/` alone and Tony had to ask where it was. The
  builder now defaults to the darkroom and takes `--also` for the repo copy.
- **Reads (no claim taken, recorded so the next session knows):**
  `<dropbox>/data/processed_archive/event_store_onset_revised_2v_alive_rescued` — 86 files,
  85 slices with a named baseline region. Interface2's rescued dead-ROI store, still
  unclaimed on their board. **Read-only here**; nothing was written to it.
- **Notes:** the answer is yes, in both streams. At K=3, FAST rejects both nulls in 28 of
  49 testable slices and SLOW in 30 of 40, against 0 expected from generated recordings
  whose participants are drawn by `rng.choice`. Consequences for other work: the generator
  plants no recurring groups and so cannot reward membership structure, and PCA/ICA
  assembly detection is now a defensible literature port rather than a rigged comparison.

  Two limits that ride with the number. Slices with fewer than four clusters have no
  permutation null and are reported **undefined, never negative** — 36 of 85 at K=3 in
  FAST. And the combination is **pooled across groups**: slice group does not travel with
  the store, and FOUNDATIONS §9 says a pooled across-group number is not admissible on
  its own. Splitting it needs the group of each slice from whoever holds that mapping.

### Mac/assembly-power — can this corpus see an assembly at all, before anyone measures one
- **Status:** DONE 2026-08-18 — **claim released**, figure written and verified
- **Started:** 2026-08-18
- **Writes:** `<darkroom>/bugarach/assembly_power.{png,html,json}` (NEW). Nothing else
  under `<darkroom>/bugarach/`, nothing in `<darkroom>/constellation/`.
- **Claims:** released. Held the three `assembly_power.*` files by that name while writing;
  they are now written and nothing further is pending on them. Rerun
  `tools/assembly_power.py` to regenerate — it reads no store, so any machine can.
- **Notes:** the open assembly question asks whether the same cells recur across events in
  the 85 baseline recordings. This answers the prior question — what an answer could
  possibly mean — by planting assemblies of known strength at the median slice geometry
  the derived spec already records, and measuring how often the test finds them. No real
  recording is read and `BUGARACH_DATA_ROOT` is not needed, so it reruns on a bare clone.

  Two results bind the measurement that follows. **The double-margin null goes blind
  exactly where the signal is purest** — at full strength the non-members never fire, the
  whole assembly sits in the column sums the null holds fixed, and power falls back to
  chance. It cannot be run alone, which is what the todo (and its first correction) had
  wrong. **And the corpus is far better powered than its pair counts suggest**: across a
  group of twenty slices, a four-to-six cell assembly taking part in one event in ten is
  found every time, and eight cells at one event in seven. The thin-looking 0.33
  observations per pair is the wrong intuition, because an assembly concentrates counts
  rather than spreading them.
### Mac/windows-abut — the window boundary was drawing a gap that is not in the data
- **Status:** DONE 2026-08-18 — **claim released**, deploy finished and verified
- **Writes:** the PUBLIC SITE. Nothing to the darkroom, nothing under `$BUGARACH_DATA_ROOT`.
- **Claims:** the site deploy, taken from released. Same standing note as the block below —
  check what `bugarach-worktrees/deploy-site` is checked out at first; it is a detached HEAD.
- **Why:** the raster left a 1px unpainted column at every region boundary. Measured, not
  guessed. On a time axis that reads as time nobody declared, and regions are contiguous by
  contract — `region_windows` halts on a gap because in these stores one is a data defect.
- **Deployed:** version `1667b04e-8455-4b5b-a01d-23c2422c131f`, live page stamps `b773abf`.
  Re-scanned the live canvas: no unpainted column between bands. The `postdeploy` audit added
  in PR #95 ran by itself and passed — first deploy it has guarded.

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
