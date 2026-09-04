# Milestones — what has been established, and how strongly

**This answers *"where are we?"*.** [`INDEX.md`](INDEX.md) answers *"where is X?"*,
[`RESET.md`](RESET.md) answers *"what may we claim?"*, [`FOUNDATIONS.md`](FOUNDATIONS.md) is
canonical truth, [`adr/`](adr/) holds the decisions themselves, and
[`handoffs/README.md`](handoffs/README.md) says what happened in each handoff.

⚠ **This file is a pointer, never an authority.** Where a row cites an ADR or a doc, that
document owns the claim and the row is the index entry. If they disagree, the document wins.

**Why it carries no counts.** [`RESET.md`](RESET.md) declines to hold open-PR, worktree or
claim counts because *"those were wrong within the hour it took to draft this"* — and it is
right. Every row here is pinned to an **immutable commit** instead, so a row can go
incomplete but cannot silently change its mind.

**How to read it.** Read the two right-hand columns before the claim. `strength` says how hard
the evidence is; `status` says whether it still stands. A row is not a license to quote until
both say so.

| strength | means |
|---|---|
| `built` | the capability exists and is tested |
| `measured` | a number produced by running something, reproducible from the doc |
| `decided` | a human made the call, and it is recorded |
| ⚠ `evidence` | the measurement exists; **the decision it informs has not been made** |

| status | means |
|---|---|
| `current` | stands today |
| `held` | real, and deliberately not to be quoted or promoted yet |
| `inert` | built, and cannot fire |
| `open` | not settled; blocks something the row names |
| `superseded by <row>` | a better result lives in the row it names |

**How to add to it.** A milestone row lands in the **same change as the work it describes**.
[`tools/check_milestones.py`](../tools/check_milestones.py) refuses a row whose commit is not
an ancestor of the base ref, whose path does not exist, whose `strength` or `status` is outside
the legends above, whose `superseded` does not name a successor, or **whose ⚠ `evidence` row
asserts its own subject is settled**. `--selftest` proves each rule can still fire, in both
directions where it has two. It runs under `pytest` via
[`tests/test_milestones_resolve.py`](../tests/test_milestones_resolve.py).

**Why the strength column exists.** On 2026-08-29 the commit that measured K across another
lab's export folder said in its own message *"CHOOSING K IS STILL NOT DONE… this file is the
evidence for that decision, not the decision"*, and noted **two defensible peaks** (K=12 and
K=16). Within forty-two hours, four documents and a pull-request title called K=12 *"the
decided K"* — one of them an incident report about decisions being ignored. A row marked
⚠ `evidence` cannot make that trip without failing a check.

---

## Open — nothing here is a milestone yet

First, because it is what a session starting now most needs. **Six items; four stop forward
motion, two block promotion.**

| what | owner | blocks |
|---|---|---|
| **How does the promiscuity probe enter the score?** Two rules are live and pick opposite winners for the rate detector | **Tony** — waiting since 2026-08-25 | the re-fit, RESET §7 step 5 |
| **Run a MAHICE review on the approved folder** — nobody has annotated a sample, so no K is set and no events are confirmed. Expert attention, not compute | **Tony** | quoting any transfer figure |
| **Run-record naming** | **Tony** | the run store |
| **Plant the promiscuity probe in the browser's generator** so the gate can fire | next session | the app's campaign inherits the ungated defect |
| `bench-background-is-not-flat` — merges cleanly; three `test_background_curve` tests go red by design | **Tony** | what `main` says about its own bench |
| The 24-seed bake-off — held; the input data may be revised | **Tony** | promoting any new bake-off number |

---

## A. The ports

| milestone | what it established | strength | commit | doc | status |
|---|---|---|---|---|---|
| Six MATLAB implementations reimplemented in Python | rate+context, CoactDetect, LoCo, binned SCE, locust, SPIKE-synch — each with parity fixtures against MATLAB output. ⚠ **Only `locust` is a port of another lab's published method**; three are Tony's own designs and binned SCE is not a port. The README and `CITATION.cff` are wrong the other way, and it is filed | measured | `c93c42b` | `docs/detector_history.md` | current — authorship correction open |
| Clean-room method | `find_peaks_halfprom` implemented from a spec alone, adversarially validated; the MathWorks-derived port removed | built | `af34d9c` | `docs/clean_room/WORKFLOW.md` | current — one spec accepted |
| Parity is not a standing contract | parity was how the ports were inherited; it does not bind them forever | decided | `128709b` | `docs/adr/0003-parity-was-the-inheritance-not-the-contract.md` | current |

## B. The instrument — generator, bench, scoring

| milestone | what it established | strength | commit | doc | status |
|---|---|---|---|---|---|
| Simulator with planted ground truth | coordinated events at known times with known participants — the only truth anywhere in this project | built | `6ad1438` | `src/bugarach/simulate.py` | current |
| Generator set by real recordings | 85 recordings measured; the generator stops being an opinion | measured | `fff2fb0` | `docs/learned/generator_spec.json` | superseded by the difficulty-axis row — RESET §5 records that it holds the store-derived axis the export-folder rule closed |
| Calibrate from baseline only | treatments are what the instruments are pointed at; taking coordination properties from them assumes the answer (Tony's call) | decided | `c3fa58a` | `docs/FOUNDATIONS.md` | current |
| Difficulty axis from the approved export folder | re-derived from the folder, not the `.mat` store; exposed locust's FAST percentile as a notch too loose | measured | `114cf29` | `docs/FOUNDATIONS.md` | current — supersedes the store-derived 0.0038–0.0175 mHz/ROI |
| Background is an axis, not a point | **nothing is flat across it, and the ranking does not survive it** | measured | `c7786f2` | `tests/test_background_curve.py` | current |
| The promiscuity probe | a dense block with nothing planted; a detector firing into it is counting rate, not coordination | built | `230f7e4` | `src/bugarach/bench.py` | current |

## C. The learned models

| milestone | what it established | strength | commit | doc | status |
|---|---|---|---|---|---|
| Learned-detector framework | models train off the page and ship as objects, not as a change to what serves | built | `fb6091e` | `docs/model_track.md` | current |
| Twelve detectors, one bake-off | six hand-written and six learned, scored on the same folds with the same seeds | measured | `20432a9` | `docs/learned/bakeoff.json` | held — eight seeds, and computed before the difficulty-axis correction (RESET §5) |
| Detectors and models are objects in a folder | and every run records the code that produced it | decided | `ced0da4` | `docs/adr/0005-detectors-and-models-are-objects-in-a-folder.md` | current |
| No ranking; a table of performance | a scoreboard implies an ordering the spreads do not support | decided | `41b1aff` | `docs/performance_table.md` | current |
| The 24-seed run | top-four spread collapses 0.043 → 0.011 ΔF1; **locust crosses its promiscuity ceiling**, 30.62/min against 25 | measured | `1684dd9` | `docs/learned/bakeoff_24seed.md` | held — do not promote; the input data may be revised |

## D. The data contract

| milestone | what it established | strength | commit | doc | status |
|---|---|---|---|---|---|
| The export folder is the input | the store is closed; a withdrawn recording is simply absent | decided | `954a489` | `docs/export_folder_spec.md` | current — revision 9 |
| The dead-ROI verdict is the exporter's | it needs every treatment of an ROI at once, which baseline-only puts out of reach here | decided | `2d536f4` | `docs/todo/2026-08-15-zero-event-rois-are-not-dead-rois.md` | current |
| One file declares which folder is current | `dataset.current()` reads it; prose had been the only thing stopping a session going to the store, and prose did not hold | built | `4297033` | `current_export.toml` | current |

## E. Cross-lab — the Cossart export folder

| milestone | what it established | strength | commit | doc | status |
|---|---|---|---|---|---|
| bugarach reads another lab's data | DANDI:000219 (Dard, Picardo & Cossart; CC-BY-4.0) becomes a conforming export folder, **59/59 passing `check`** — the first non-lab producer, and the first test of the contract's optional-field promise. ⚠ the raster is **binarised**: `time_sec` is a rising edge, not a t50rise, and there is no peak or amplitude, so cross-lab coincidence is unavailable and transfer must run through a simulated field | measured | `25ca1a6` | `tools/import_dandi.py` | current |
| Their folder assessed | 59/59 recordings, 1000 surrogates, K scanned 3–24; median 566 ROIs against our 32; coactivity excess (dimensionless) 93.28 at K=3, rising to 150.26 at K=8, dipping, peaking 154.04 at K=16 by pooled median | measured | `80b8db6` | `docs/learned/assessment_cossart.json` | current |
| **Which K for their folder** | **The question changed shape, and the old form is answered.** It asked which absolute K to pick off that scan — 12 as the commit reports it, 16 by pooled median. K is now **a percentage of each recording's ROI population, set by a person during MAHICE** (`assess.k_from_fraction`, `annotate.MahiceSession`), so there is no integer to choose and none to transplant. That mechanism answers the ⚠ this row used to carry: an absolute K cannot survive *median 566 ROIs against our 32*, which is exactly why a fraction can. **What is open is that nobody has run a review**, so no percentage is set and no events are confirmed for the approved folder | decided | `a1850d0` | `docs/GLOSSARY.md` | superseded by the row above — the scan numbers stand as measurement |
| Fit on one corpus, score on another | `--score-spec`; the seam is mutation-tested both ways. **The only cross-lab transfer path in the project** — the app has no equivalent | built | `f3c22bf` | `tools/fair_bakeoff.py` | current, and on the retired-tool side of Tony's 2026-08-28 ruling |
| Transfer run at K=12 | CoactDetect carries across for free (ΔF1 0.001); the learned models score best on that field and are the only ones that cannot travel; rate+context fails with perfect recall. Figures are in the doc | measured | `cc2489d` | `docs/learned/cossart_transfer/README.md` | held — **and one of its four reasons has changed rather than cleared**: K=12 is not a choice awaiting a ruling, it is an absolute count from before K became a percentage, so this run was scored at a floor that does not correspond to any percentage until a review sets one. The other three stand: the spec is `--unreviewed`, the background is inherited from this lab, and the doc's own header says a data revision supersedes K=12 |
| Transfer run at k=3 and k=8 | the same ordering at a lower level — the sensitivity evidence | measured | `31b2a2e` | `docs/learned/cossart_transfer/README.md` | superseded by the K=12 row |

## F. Attribution

| milestone | what it established | strength | commit | doc | status |
|---|---|---|---|---|---|
| The sixth detector is called locust | it is a *modified* port of a living lab's named software, and the name was on a public page | decided | `fe3f7d0` | `docs/adr/0002-the-sixth-detector-is-called-locust.md` | current |
| locust is not CICADA | the derivation chain is validated **only at its last link**; it came from their code, and the citation is correct | decided | `90f1b1d` | `docs/handoffs/2026-08-28-locust-is-not-cicada-and-four-things-i-got-wrong.md` | current |
| locust is held out of the public build | the public build ships without it, name and all, in both viewers | decided | `7287db1` | `docs/RESET.md` | current |
| Kreuz endorsed the PySpike patch | he reproduced the bug himself and asked for the PR | decided | `2293d5b` | `docs/todo/2026-08-11-file-pyspike-max-tau-issue.md` | open — the PR has not been filed |

## G. The public artifact

| milestone | what it established | strength | commit | doc | status |
|---|---|---|---|---|---|
| The site is live | a stranger can open a URL and run these detectors without installing anything | built | `c06c5fa` | `docs/site/` | current |
| The page runs the pipeline | assess, detect, sweep and score, in the browser | built | `765fce6` | `docs/site/raster_viewer.html` | current |
| One front end | the webapp was for comparing methods; one viewer does it | decided | `ff971bc` | `docs/RESET.md` | current |
| The app's sweep gained the third refusal | a promiscuous winner is refused rather than silently accepted | built | `c769420` | `docs/handoffs/2026-08-28-the-gate-is-in-the-app-and-inert.md` | inert — no recording the page generates carries the probe it gates on |

## H. The machinery that keeps it honest

| milestone | what it established | strength | commit | doc | status |
|---|---|---|---|---|---|
| Sapper | incidents become checks that fire by themselves — **12 rules**, each proven fireable by `--selftest`. SAP011 is a reserved id, not a rule; counting the ids by grep gives 13 and is wrong | built | `065f6f6` | `tools/sapper.py` | current |
| The murderboard | document deliverables get an eleven-role adversarial review before they are handed over | built | `f284bd0` | `docs/doc_review_process.md` | current |
| The briefing reaches the session | it had been spilling at 17,568B with most of it reaching nobody; a size canary is now its first line | built | `8810566` | `docs/handoffs/2026-08-25-the-session-hooks.md` | current |
| CI installs torch | it had been declared for ten days and never installed | decided | `77f286d` | `docs/adr/0004-ci-installs-torch-from-the-cpu-wheel-index.md` | current |
| An index of where things are | every finding has an address, keyed on the words you would grep for | built | `81cc134` | `docs/INDEX.md` | current — ⚠ an index inherits the errors of what it indexes; its line 41 carried a wrong claim inside a read-this-first flag |
