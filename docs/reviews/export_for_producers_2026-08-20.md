<!-- murderboard run record — process vendored from syncytium2/murderboard @ 729fb06 -->
# Murderboard run — docs/export_for_producers.md

**The problem this document solves.** The import contract exists and is correct, and it is
500 lines addressed to whoever maintains bugarach. The people who have to *satisfy* it are
the MATLAB team, and nothing was addressed to them. A contract nobody on the producing side
has read is a contract in name only — and this project has just spent a session paying for
exactly that: an analysis went around the folder to the raw store, re-derived the producer's
exclusions from a lab workbook, and dropped a recording the lab had never withdrawn while the
producer's own export had it right.

So this is a one-page version, written outward: what to write, then the four things that
actually go wrong, then a validator command and a worked example that has been run.

- upstream:  syncytium2/murderboard @ 729fb06
- vendored:  77b70dc620a8bcccfc72fce2fd316d38da34c204
- freshness: current
- artifact:  docs/learned/export_for_producers.html (b3f7c81ce6bedabcd61bb824f78f93c24686993a)
             source docs/export_for_producers.md (3d95e97be4334f542b8991a782708d85252aefcc)
- roles:     11 of 11 run (single-pass, same deviation recorded in the assembly run record)
- rounds:    2 (stopping reason: **severity floor** — round 2 produced no blocking, no major)

## Findings by severity

| round | blocking | major | minor |
|---|---|---|---|
| 1 — initial | 0 | 3 | 1 |
| 2 — blind, rebuilt page | 0 | 0 | 1 |

## Findings and adjudications

**M1 · MAJOR · a near-miss accusation, caught by checking (role 1).** The validator reports
`0 ROI with no events` on the first recordings of the current export, which is the signature
of dropping silent ROIs — the defect section 2 warns about. The draft was about to tell the
MATLAB team they had it wrong. **Recomputed instead**: distinct ROI count matches
`n_roi_recorded` on every recording checked, and several recordings *do* carry `NA` rows.
They are doing it correctly. **Fixed** — the document says the note is asking for
confirmation rather than reporting a fault, and states that the export passes.

**M2 · MAJOR · the silent-ROI rule is per (roi, stream), and the draft implied per roi
(role 6).** In `20240726_34`, ROIs 10 and 16 have four slow events, no fast ones, and an `NA`
row naming the fast stream. A reader following the draft would have written one `NA` row per
silent ROI and under-declared the per-stream population. **Fixed** — stated explicitly, with
their own data as the example, which also makes the point that their exporter already handles
it.

**M3 · MAJOR · wrong canonical column name (role 1).** The draft named `mouse_id` as the
reserved subject column. The loader's canonical is `subject_id`, with `mouse_id` and
`animal_id` as accepted aliases (`io.py`, `SUBJECT_ALIASES`). For a team writing a *new*
exporter that is the wrong instruction. **Fixed** — `subject_id` named, aliases noted so
nobody rewrites a column that already works.

**m1 · minor · the check output was illustrative, not real (role 1, role 10).** Both the
validator transcript and the worked example were copied from the spec's illustrations.
**Fixed** — the transcript is real output from the current export, and the worked example was
written to disk and run through `bugarach check`, which returns `CONFORMING`. Its transcript
is in the document.

**m2 · minor · no owner named for width (role 4, round 2).** The document says width is the
producer's to define; it does not say who on their side signs it off. **Left** — naming a
person in a contract document dates it, and the spec already assigns it to interface2's
documentation.

## Role ledger

| # | role | findings | what was checked |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 2 major, 1 minor | Every column name against `src/bugarach/io.py`; the ROI counts against the live export; the validator output and worked example by running them. |
| 2 | Citation & reference validator — "DOI or Die." | 0 | No literature cited. The one cross-reference, `export_folder_spec.md`, exists and says what is claimed. |
| 3 | Consistency auditor — "Cross-Examiner." | 0 | Every term cross-checked against the full spec — `t50rise`, `region_idx`, `frame_interval_sec`, `width_def`, `subject_id`. No contradiction; this is a strict subset. |
| 4 | Adversarial reviewer — "Reviewer 2." | 1 minor | The incident in section 3 is stated with its mechanism, not as blame, and the document does not claim the producer erred. |
| 5 | Line editor — "Kill Your Darlings." | 0 | 223 lines for a contract summary. Each of the four warnings states one failure and its consequence. |
| 6 | Methods / domain expert — "RTFM." | 1 major | Read the loader rather than the prose: reserved filenames, `NA` spellings, required columns, per-stream population. |
| 7 | Reuse auditor — "Reinventing the Wheel." | 0 | Renders through the existing `tools/md_to_page.py`; no new builder. Points at the existing `bugarach check` rather than describing a procedure. |
| 8 | Naive-reader accessibility — "You Lost Me." | 0 blocking | Swept for repo-internal vocabulary a producer would not know — `bugarach.*` module paths, `tools/*.py`, FOUNDATIONS section numbers, murmuration, interface2, penumbra. **None present.** |
| 9 | Density & figure-first — "Show, Don't Tell." | 0 | Prose is right here: the payload is tables and file contents, and both are shown as literal text a producer copies. A diagram would add nothing to "write these three files". |
| 10 | Build & craft gate — "Ship It." | 1 minor | Rendered page opens; tables render; code blocks are literal and copyable. Both transcripts are real command output. |
| 11 | Argument order — "Start With the Problem." | 0 | What to write, then what goes wrong, then how to check. A producer who reads only the first screen can already write a conforming folder. |

## Residual ⚠

1. **The document is addressed to a team that has not read it yet.** Its own thesis is that a
   contract nobody on the producing side has read is not a contract; delivering it is the
   step that closes that, and it is not done by writing it. ⚠
2. **`width_sec` is asked for and not supplied** by the current export. The document requests
   it; whether it arrives is the producer's call.
3. **The review was single-pass**, not independent — the standing deviation recorded in
   `assembly_summary_2026-08-19.md`.
