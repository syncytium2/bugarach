# Murderboard run — docs/methods/coordination_pipeline_methods.md

- upstream:  syncytium2/murderboard @ 08f5ddb
- vendored:  08f5ddb
- freshness: current (`tools/murderboard_freshness.sh` exit 0)
- artifact:  `docs/methods/coordination_pipeline_methods.md` (blob b64ffa26 at f6f0c26 → 53adfbd3 final), built to `.docx` (the deliverable) and `.html`
- roles:     11 of 11 run (named agents)
- reports:   docs/reviews/coordination-pipeline-methods-2026-09-22-roles/
- rounds:    3 (round 1 on f6f0c26; blind round 2 on 464d995; blind round 3 on ee7bd62), capped at 3; fixes from round 3 applied without a fourth review

Round 2 and round 3 reports are in `docs/reviews/coordination-pipeline-methods-2026-09-22-roles-r2/` and
`docs/reviews/coordination-pipeline-methods-2026-09-22-roles-r3/`, eleven files each, written verbatim as they
arrived. Personal absolute paths were redacted to placeholders (sapper SAP004). A quoted citation string that sat
beside the words "personal communication" was paraphrased wherever it occurred (`tools/check_quotes.py`). No
private correspondence was quoted anywhere.

## What was asked, and what was delivered

Tony, 2026-09-21: a methods section for the current coordination pipeline, written as manuscript methods —
precise, unambiguous and as brief as possible — covering the detected events, the synthetic data, coded-detector
optimization, model training, the benchmark and its derivation, the scoring parameters, each detector's knobs, the
analysis of recorded data, and the width and amplitude measure, murderboarded in full.

Delivered:
- the section, with one figure and four tables;
- its build (`.docx` rendered through Microsoft Word, 16 pages, and `.html`);
- a cover memo for Tony (`docs/methods/coordination_pipeline_methods_cover_memo.md`) holding everything that is
  not manuscript text: five code defects, the design choices a referee will attack, open decisions, questions for
  the producer, the ordering rationale, and stale notes found in passing;
- the recorded-data run's settings file, committed beside the section (`recorded_data_detector_settings.csv`),
  because the stored operating points do not hold the settings the run used.

## Grants — what each reviewer declared it held

Round 1:
- GRANT 1 ok — Read, Grep, Glob, Bash
- GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
- GRANT 3 ok — Read, Grep, Glob
- GRANT 4 ok — Read, Grep, Glob, Bash
- GRANT 5 ok — Read, Grep, Glob
- GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
- GRANT 7 ok — Read, Grep, Glob, Bash
- GRANT 8 ok — Read, Grep, Glob
- GRANT 9 ok — Read, Grep, Glob, Bash
- GRANT 10 ok — Read, Grep, Glob, Bash
- GRANT 11 ok — Read, Grep, Glob

Rounds 2 and 3 declared the same grants for every role (each report's first line); some roles also named the
hand-back channel, which is not an editing tool. No role reported a MISMATCH.

## Role ledger — all eleven, three rounds

Highest severity each role raised in each round, with the finding that set it.

| # | Role | Round 1 | Round 2 (blind) | Round 3 (blind) |
|---|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | **blocking**: the Table 1 caption said the search left four detectors alone; it had proposed changes for three | major: minimum cells was said not to be searched, but it was; width counts pooled both streams; the pinning history was out of date | major: the "1.6× senktide, busier than any condition" claim was stale (28 recorded windows are busier); the quiet/busy percentiles cover only 80 recordings; three analyzed recordings are still under pinning review |
| 2 | Citation & reference validator — "DOI or Die." | major: binned SCE misattributed to Cossart 2003; the SPIKE-synch cap misattributed to Kreuz 2015; no citation for CICADA | high: the detection step overstated as "the same form" as Cecchini 2021; the Bouckaert & Frank claim misattributed | high: citations the README asks for (CoactDetect, LoCo) missing; the CFAR contrast wrong; the profile threshold originates in Kreuz 2017; all 17 references verified |
| 3 | Consistency auditor — "Cross-Examiner." | medium: tables numbered out of order; artifact counts pooled both streams | medium: "the same event detection" contradicted by the counts; planted-interval statistics contradicted the figure | medium: Table 4 cited before Table 3; width counts contradicted the memo; glossary conflicts |
| 4 | Adversarial reviewer — "Reviewer 2." | **blocking**: the close-events limit was reported, not applied; distractors are indistinguishable from planted events | **blocking**: the objective penalizes detecting 6-cell events; no statistics plan | major (no blocking): distractors break the 120 s spacing rule; the elevated-rate test counts calls; amplitude largely tracks 1/width; stage 2 was run but discarded |
| 5 | Line editor — "Kill Your Darlings." | high: "seed" and "participation" each carried two meanings; merge-gap contradiction | high: "event" in three senses; modes undefined; the "in each" merge claim false | high: "Each also requires…" false; one-parameter-per-detector retune false; archive and recording counts ambiguous |
| 6 | Methods / domain expert — "RTFM." | major: Table 1 caption false; the search rule could not reproduce the LoCo setting; the Gaussian p misread as a false-alarm rate | high: binned SCE width measured over the wrong interval; locust's global threshold confounds treatment | major: SCE width defect quantified (27% of core groups change); SPIKE-synch wrongly listed as absolute in cells |
| 7 | Reuse auditor — "Reinventing the Wheel." | high: SCE call stretch rebuilt instead of reused; LoCo/locust window membership wrong | high: the same two, plus Table 4's settings recorded nowhere in the tree | high: both confirmed and quantified; new defect, `measure_calls` overwrites `n_roi` |
| 8 | Naive-reader accessibility — "You Lost Me." | **blocking**: 7 of 9 sections; "coordinated event" and "call" undefined | **blocking**: binned and sliding modes undefined; treatments defined 8 pages late | **blocking** (2 sections): undefined Table 4 terms (greatest-of, guard normalization, update step) and coded-detector terms (grid point, interior events) |
| 9 | Density & figure-first — "Show, Don't Tell." | major: the benchmark is a layout described in prose; asked for Figure 1 | high: Table 3 failed as a table; figure text about 5 pt | moderate: detector bullets could be a table; constant column in the limits table |
| 10 | Build & craft gate — "Ship It." | **FAIL**: the .docx was never rendered; tables out of order | **FAIL**: build one edit stale; figure text illegible; mid-word breaks | **FAIL** (one craft defect): mid-word breaks in Tables 2 and 4; everything else passed |
| 11 | Argument order — "Start With the Problem." | major: scoring before the detectors it scores; tables out of order | major: modes undefined; the PI's "knobs" item had no home | major: learned-detector section depended on the next section's design |

## Adjudication

**Accepted and fixed after round 3** (the final revision, 53adfbd3):
- all text errors: the senktide comparison, the 80-recording basis, the pinning review, the SPIKE-synch limitation,
  stage 2's result, the gains of the rejected proposals, the inadmissible reference, and distractor placement;
- all undefined terms: null, surrogates, guard, greatest-of, guard pieces, the search span and groups, inner fits,
  the threshold recordings, and contrast;
- table order: the parameter table moved into *Coded detectors* as Table 3, and the limits became Table 4 with
  the constant close-events column moved to the caption;
- dead rows dropped: LoCo's update step, which has no effect in sliding mode, and the detection-mode rows;
- citations: the CFAR contrast corrected; Kreuz 2017 given as the profile threshold's origin; the personal
  communication dropped because the published record carries the claim; CICADA's 2026 framework paper, Mao 2001
  and Hansen & Sawyers 1980 added; cSPIKE named as software;
- the learned-detector design paragraph moved to the head of its section, with defaults and search ranges (the
  learned half of the PI's "knobs");
- the rotated panel letters dropped from Figure 1; American spelling throughout;
- build: column widths that stop mid-word breaks, lead-ins kept with their lists, captions kept whole.

**Moved to the cover memo** rather than the text:
- the five code defects;
- design choices whose remedy is in the pipeline: distractor design, the elevated-rate metric, treatment-rate
  sensitivity, the missing time control and statistics plan, and amplitude's dependence on width;
- the width counts (a result, and they include binned SCE's defective measurement);
- code identifiers;
- the pinning question for the producer.

**Declined, with reason:**
- *Rename "amplitude"* (roles 5 and 8, all three rounds): it is Tony's definition. The memo carries the
  recommendation and round 3's evidence that it largely duplicates width.
- *Cite Grün 2002 and Amarasingham 2012 for CoactDetect and LoCo* (role 2, round 3): nobody here has read them,
  and a citation attaches a content claim. It goes to Tony as a decision.
- *Add a Figure 2 or a coded-detector summary table* (roles 8 and 9): declined under the brevity brief; Table 3
  now carries the knobs.
- *Reorder to the PI's list* (role 11): dependency order is kept, and the memo explains why.

**Residual ⚠ (not resolved by this run):**
- the pinning review of three analyzed recordings (memo §0);
- five code defects that stop results for the detectors named (memo §1);
- the MATLAB, PySpike and cSPIKE versions;
- nobody has asked CICADA's authors how they want the software cited;
- the Mao 2001 and Finn 1967 traces stop one step short.

## Process findings (about the run)

- **The prose tool is missing.** Role 5's checklist names `tools/murderboard_prose.sh`, which does not exist here.
  Role 5 ran its checks by hand in all three rounds and said so, so its mechanical results are approximate.
- **A commit hook crashed on a Windows console.** `tools/sapper.py` raised `UnicodeEncodeError` printing an arrow
  under cp1252. With `PYTHONIOENCODING=utf-8` it ran clean. This is an environment defect worth a sapper fix.
- **The quotation check's compliant citation form** accepts a month and year, or an ISO date, after the citation
  but not a day-month-year date, so a correctly dated citation reads as a violation. The check was not edited.
- **`murderboard_roster.sh` strips underscores from the declared reports path** (its `reports_decl` removes
  `[*`_|>]` to unwrap markdown), so a folder named with underscores can never be found. The three report folders
  were renamed to hyphens (`coordination-pipeline-methods-2026-09-22-roles*`). The vendored tool was not edited;
  this belongs upstream.
- **Round 2 reviewed a build one edit behind its commit.** Rounds 1 and 2 caught it; round 3's build was verified
  byte-identical to its commit.
