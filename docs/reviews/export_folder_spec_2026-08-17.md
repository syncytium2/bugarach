# Murderboard run — docs/export_folder_spec.md (revision 2)

- upstream:  syncytium2/murderboard @ `783501e`
- vendored:  `783501e` (freshness gate: `--refresh --verbose` → exit 0, via remote)
- freshness: current
- artifact:  `docs/export_folder_spec.md` (`8f934d0` → `50b4507`)
- roles:     11 of 11 run
- rounds:    2 blind verify rounds to clean
- mode:      single-pass self-review, every role walked in turn

**Mode, stated rather than buried.** The process prefers parallel subagents for a
substantial deliverable; this session runs with the Agent tool disabled, so the
roles were walked in one pass instead — the mode the process permits for small
deliverables, applied here to a larger one. What that costs is independence: the
same context that wrote the draft reviewed it. What it did not cost is coverage —
every role ran, and the mechanical roles were answered by *running things* rather
than by reasoning about the source, which is the substitution the process actually
warns about. Four defects came out of it, three of them in code.

## Role ledger

| # | Role | Findings | Notes |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 0 | Claim ledger recomputed against `src/bugarach/io.py`: three reserved names vs `RESERVED` ✔; `slice_id` = file stem ✔; `stream` column optional, defaults to `events` ✔; empty field == `NA` vs `NO_EVENT` ✔; "at least one required" vs the `FileNotFoundError` ✔; **1.67× recomputed** (5 ROIs ÷ 3 counted) and pinned by `test_na_time_declares_a_recorded_roi_with_no_events`. |
| 2 | Citation & reference validator — "DOI or Die." | 0 | No findings, and here is what I checked: the document carries no bibliographic references or named attributions. Its only pointers are internal (`docs/export_folder_spec.md` self-reference, the output-contract section) and resolve within the repo. No lit-cache fetch needed. |
| 3 | Consistency auditor — "Cross-Examiner." | 2 | **F-3a (fixed)** the folder diagram showed two reserved names while the prose immediately below named three — a reader matching one to the other finds a mismatch; the prose now says `metric_dictionary.csv` is not shown and why. **F-3b (fixed)** `roi` was "unique within the recording", but an ROI id repeats on every one of its event rows; reworded to say the same string identifies one ROI and no other. Glossary checked: the document is ROI-centric throughout, matching `GLOSSARY.md`; "modality" absent. |
| 4 | Adversarial reviewer — "Reviewer 2." | 1 | **F-4a (fixed)** "a per-ROI rate is events divided by ROIs" — a *rate* needs a time base; that expression is a count per ROI. Restated as "every per-ROI quantity divides by that population". Attacked and let stand: the spec's own admission that a producer omitting silent ROIs is conformant-but-lossy and "nothing downstream can tell" — that is the honest limit, stated rather than hidden. Can the alarm ring? The `NA` claim is testable and fails loudly when broken: deleting the `NA` rows changes `n_rois` in the round-trip test. |
| 5 | Line editor — "Kill Your Darlings." | 1 | **F-5a (fixed)** "five ROIs recorded with two quiet, **divided** over three" — an edit from F-4a left ungrammatical wording; now "counted over three". |
| 6 | Methods / domain expert — "RTFM." | 1 | Grounded in the `csv` module docs rather than memory: `open(newline="")` is the documented requirement for `csv` readers and is used ✔. **F-6a (fixed, code)** `regions.csv` with a label in the `region_idx` column raised a bare `int()` traceback from inside the reader; it now names the row and says which column holds the name. Noted, not filed: duplicate `roi`+`time` rows are accepted silently — the contract makes no claim either way, and de-duplicating would be a decision about the producer's data. |
| 7 | Reuse auditor — "Reinventing the Wheel." | 0 | No findings, and here is what I checked: `load_folder` delegates to `load_events_csv` → `_read_event_rows`/`_assemble` rather than re-parsing; `io.py` is the only CSV reader in `src/` (`grep DictReader\|csv.reader`); `spec.py` was checked and is `RecordingSpec` for simulation, unrelated to the folder contract. No duplication to collapse. |
| 8 | Naive-reader accessibility — "You Lost Me." | 0 | No findings, and here is what I checked, section by section as a stranger: the three facts arrive before any filename; `stream`, `roi`, `region_idx` and `label` are each defined where first used; the folder diagram precedes the per-file tables. No internal code identifiers leak into producer-facing text — `Slice.roi_set_declared` appeared in an earlier draft and left with the roster it belonged to. Sentence case throughout; lists are formatted as lists. |
| 9 | Density & figure-first — "Show, Don't Tell." | 0 | No findings, and here is what I checked: 2,374 words across 12 sections; the one thing a reader must picture — the folder's shape — **is** a figure (the ASCII tree at the top), placed before the prose that depends on it. Prose is right for the rest: this is a normative contract, and its payload is rules a producer must satisfy, which a diagram cannot state. No table here would be better as a chart. |
| 10 | Build & craft gate — "Ship It." | 0 | Non-rendering Markdown, so the table below is the render check, run against the file rather than reasoned about. |
| 11 | Argument order — "Start With the Problem." | 0 | No findings, and here is what I checked. Spine, one claim per section: (1) bugarach needs three facts (2) the folder is the whole input (3) rev 2 changed the shape and why (4) here is the folder (5) a recording file holds roi+time+stream (6) **a silent ROI has no rows, and that breaks the denominator** (7) `NA` fixes it (8) regions carry treatment timing (9) `slices.csv` carries the interval (10) here is what comes back out (11) the rules that make it universal. Arc used: *what is needed → what it costs to get it wrong → the fix → the rules*. The problem in §6 arrives immediately after the file that has it and immediately before the fix, which is the order that makes it legible. |

### Role 10 — mechanical table

| Check | Result |
|---|---|
| Fenced code block balanced | ✔ 1 open, 1 close |
| Markdown tables well-formed | ✔ 4 tables, header/separator/body column counts equal |
| Heading nesting | ✔ `#` → `##` → `###` → `####`, no level skipped |
| Internal links resolve | ✔ `FOUNDATIONS.md`, `GLOSSARY.md` present in `docs/` |
| Reserved names in prose == `RESERVED` in code | ✔ `slices.csv`, `regions.csv`, `metric_dictionary.csv` |
| Every claimed behaviour has a test | ✔ 22 tests in `tests/test_io.py`; 446 pass, 1 skipped |
| Sapper | ✔ clear (`tools/sapper.py --all`) |
| Artifact changed by the fixes | ✔ `8f934d0` → `50b4507` |

## Findings and adjudication

Three of the four code defects in this change were found by *running* the reader,
not reading it — recorded because that is the pattern worth keeping.

| ID | Severity | Finding | Adjudication |
|---|---|---|---|
| F-6a | **blocking (code)** | A label in `region_idx` raised a bare `int()` traceback | **Fixed** — names the row, says `label` holds the name. Test added. |
| F-10a | **blocking (code)** | `metric_dictionary.csv` was read as a recording called "metric_dictionary" and failed on its columns | **Fixed** — reserved. Test added. |
| F-3c | **blocking (code)** | A `slice_id` in `regions.csv`/`slices.csv` matching no recording file bought nothing and said nothing — one typo silently costs a recording its windows or its interval | **Fixed** — warns from the actionable side (a recording the table failed to reach), staying silent when a batch table legitimately covers more recordings than the folder holds. Two tests added. |
| F-4a | medium | "a per-ROI rate is events divided by ROIs" — a rate needs a time base | **Fixed** (wording) |
| F-3a | low | Folder diagram showed 2 reserved names, prose named 3 | **Fixed** |
| F-3b | low | `roi` described as "unique within the recording" while repeating per event | **Fixed** |
| F-5a | low | Ungrammatical wording introduced by the F-4a fix — caught by the blind pass, not by re-reading the finding list | **Fixed** |

## Verify passes

- **Round 1 (blind)** — re-read the corrected file with no reference to the finding
  list. Produced F-3a, F-3b, F-5a. F-5a is the case the process predicts: a fix
  created a new defect, and only a pass that was not looking at the fix saw it.
- **Round 2 (blind)** — re-read the changed region again. No new findings. Role 10
  re-run in full against the new file; tests and sapper re-run after the last edit.

## Residual ⚠

- **⚠ `n_roi | how many cells took part`** in the output-contract section says
  "cells" where the glossary says ROI, and an ROI is not necessarily a cell. This is
  rev-1 text in a section this revision does not otherwise touch, so it is flagged
  rather than silently rewritten. Worth a one-line fix in whatever next edits the
  output contract.
- **⚠ `region_idx` is documented as "1-based, chronological"; the reader only
  requires an integer.** It sorts by the value and never checks that the values are
  1-based or contiguous, so a producer sending `0,1,2` or `5,7,9` gets correct
  ordering and no complaint. Harmless today — the ordering is all that is used —
  but the document states a convention stricter than anything enforces, so a later
  reader may assume the check exists.
- **⚠ "newline-only endings"** is likewise stricter than the reader: the `csv`
  module accepts CRLF, so a Windows-authored file works despite the sentence. Not
  worth loosening the document over, recorded so nobody treats it as a validated
  constraint.
