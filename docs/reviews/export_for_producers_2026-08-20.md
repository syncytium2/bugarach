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

1. ~~**The document is addressed to a team that has not read it yet.**~~ **CLOSED
   2026-08-20 — interface2 is reviewing it.** It is a proposal in front of the producer now
   rather than a file, which is the state its own thesis said it had to reach. **Expect the
   contract to change**: the producer knows things about their pipeline this document
   assumes, and a revision coming back from them is the process working, not a defect in it.
   Whatever returns needs a round 2 appended here.
2. **`width_sec` is asked for and not supplied** by the current export. The document requests
   it; whether it arrives is the producer's call, and is exactly the sort of thing their
   review should answer.
3. **The review was single-pass**, not independent — the standing deviation recorded in
   `assembly_summary_2026-08-19.md`. Note that interface2's review is the independent pass
   this one lacked, and a better one: they can check the document against a pipeline nobody
   here can see.

---

# Round 2 — interface2's review, 2026-08-20

**The producer reviewed the contract and found four things.** This is the round residual #1
said had to happen, and it is worth recording that it worked: their review checked the page
against a pipeline and a decision log this repo cannot see, and found defects an
eleven-role pass here did not.

| finding | severity | outcome |
|---|---|---|
| "If you have both, send both" recommends switching off the raw-bounds check | **blocking** | fixed — advice reversed |
| §4 never says what `width_sec` feeds, and suggests `fwhm`, which breaks it | **blocking** | fixed — states the use and the scale |
| the link to the full contract is unreachable for the reader it addresses | major | fixed — spec rendered beside the page |
| "the current export" is one folder stale | major | fixed — requoted from `2026-08-18_revised_2v_periods` |

## The two that matter

**B1 · the analysis-window advice was backwards, and contradicted its own producer.**
Supplying `analysis_start_sec`/`analysis_end_sec` short-circuits the raw-bounds validation,
so the same corrupted folder passes clean with the columns and is caught without them.
interface2 demonstrated it both ways on this page's own example. Worse, they had **decided
this two days before the page was written** (`a1409d1d`, 2026-08-18: *"RAW-ONLY ALSO
RESTORES THEIR GATE"*), for exactly this reason — so the page recommended the practice its
largest producer had deliberately dropped. **Reading their decision log before writing would
have caught it.** Fixed: raw periods are the default advice, with both reasons stated.

**B2 · `width_sec` is read, and the page implied it was not.** "We carry the string and
never read it" is true of `width_def` and false of `width_sec`, which becomes the per-event
duration CICADA uses as a coincidence window. The page offered `fwhm` as an example rule; on
this project's slow stream `fwhm` runs to a median of 4.7 s and a maximum of 186.9 s against
a 2 s rise interval, so a producer following the page ships a conforming folder and a wrong
answer. Fixed: §4 now says what the number feeds and what scale it has to be on, so "pick
your rule" is an informed choice.

## A claim of mine that did not survive checking

Reading their finding 1, I concluded from `a1409d1d` that bugarach still had the
`NaN`-is-truthy bug they described — `load_folder` does return `has_analysis_window=True`
with `nan..nan` — and added a guard to `io.py`. **The existing test suite refused it**,
correctly: the guard already exists at `detectors/loco.py:268`, which rejects a non-finite
analysis start with a named error, and `bugarach check` reports it as *"loads, but no
detector can run on it"*. The loader is permissive by design and the window resolver is
strict; nothing scores `nan..nan`. My change was reverted. The page now says where the
refusal comes from, since it arrives later than a producer might expect.

## Not fixed, recorded

**The silent-ROI note fires on 59 of 84 recordings.** A note that fires on 70% of a folder
trains the reader to skip it, which inverts its purpose. That is bugarach's checker to
sharpen, not the producer's export to change; the page now says so rather than leaving it to
be learned.

## Residual — updated

1. ~~addressed to a team that has not read it~~ — **closed**; they reviewed it, and this
   round is the result.
2. ~~`width_sec` asked for and not supplied~~ — **closed**; the current export carries
   `width_sec`, `width_def`, `peak_sec` and `amp`.
3. **The silent-ROI note is too noisy to be useful.** ⚠
4. **The review here remains single-pass.** interface2's was the independent pass, and it
   found two blocking defects — which is the argument for making that the norm rather than
   the exception. ⚠
