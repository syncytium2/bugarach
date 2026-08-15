# Murderboard run — `site/index.html` (the driving-idea paragraphs)

- upstream:  syncytium2/murderboard @ b2b2ba2
- vendored:  6a6a960 (`docs/doc_review_process.md`)
- freshness: current (`murderboard_freshness.sh --refresh` exit 0)
- artifact:  `site/index.html` (`28a37df` -> `c7e9e4a`)
- roles:     11 of 11 run
- rounds:    1 blind verify round to clean

A second review of this page on the same day; the landing-page run is
`index_2026-08-15.md` and is not superseded by this one. This run covers only the
two paragraphs stating the project's driving idea, added under the real-recording
figure at Tony's instruction.

**Mode.** Two paragraphs added to an existing page — the process's *small doc*
branch: a single-pass self-review walking every role's checklist in turn, with
agent 10's table produced in full against the render. Every quantity was checked
by opening its source, not by recall.

**What was reviewed.** The built page, rendered headless at 900 px and read as an
image — not the generator. `tools/build_site.py` was reviewed separately under
roles 6 and 7. The last action before delivery was the rebuild.

## Role ledger

| # | Role | Result |
|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 3 findings — unreproducible TTX figures, a half-told stream claim, and two pipeline stages described as if they existed. Claim ledger below. |
| 2 | Citation & reference validator — "DOI or Die." | No findings, and here is what I checked: the draft carries no citations, DOIs, or named attributions. Its one attributable claim (coordination persists under TTX) is sourced to this repo's own FOUNDATIONS §9 and the commit that added it, not to literature, so there is no bibliographic metadata to verify and nothing was reasoned from a half-remembered paper. |
| 3 | Consistency auditor — "Cross-Examiner." | 1 finding — the draft said "TTX does not silence the field", where FOUNDATIONS §9 binds every such claim to name its stream and rules both "TTX abolishes coordination" and its converse out as premises. Also checked against GLOSSARY: "stream" used on the stream axis, "modality" absent, no collision with "detector axis". Page-internal counts ("six detectors", "two of these ports") reconcile with the rest of the page. |
| 4 | Adversarial reviewer — "Reviewer 2." | 2 findings — a result derived from real treatment recordings promoted to the public front page (escalated; see residual 1), and a capability claim with no implementation behind it. *Can the alarm ring?* applied to "a model would call that noise": no such model exists, so the sentence is a design premise and cannot be read as a measured result — the page now says so. |
| 5 | Line editor — "Kill Your Darlings." | 2 findings — "with nothing you can argue with" asserted nothing checkable; "score that as noise" mixed a scoring metaphor into a sentence whose point is confidence. Both rewritten. |
| 6 | Methods / domain expert — "RTFM." | 1 finding — FOUNDATIONS §9 records that the 92–100% run's settings and windowing differ from the MATLAB campaign it agrees with, so quoting the number bare quotes a differently-parameterized instrument than the one that produced the published campaign. Resolved by removing the number rather than caveating it on a landing page. |
| 7 | Reuse auditor — "Reinventing the Wheel." | No findings, and here is what I checked: the change adds prose to an existing HTML template string in `tools/build_site.py`. It introduces no analysis code, no new computation, and no re-implementation of anything in `src/bugarach/`; the build path is unchanged and still opens no data store. |
| 8 | Naive-reader accessibility — "You Lost Me." | 1 blocking row, now cleared — the draft's first block introduced *TTX*, *the field*, *preparation* and *slow stream* undefined, ahead of the paragraph that establishes what an ROI is. Three or more undefined terms in one block is blocking by this role's contract. TTX and stream are now glossed where they appear. Residual 3 below. |
| 9 | Density & figure-first — "Show, Don't Tell." | 1 finding, partially resolved — the draft was a single 167-word block, the largest on the page. Split into 94 and 95 words, against the page's existing 59–80. The four-stage pipeline it describes is still prose that wants a picture; the replacement figure is named in residual 2. |
| 10 | Build & craft gate — "Ship It." | Table below, against the rebuilt render. No overlap, no overflow, no horizontal scroll. |
| 11 | Argument order — "Start With the Problem." | 1 finding, adjudicated as a **stated deviation** — the paragraphs assert the method before the page reaches "What it cost to get this wrong". Placement directly under the data figure is Tony's instruction, so the arc is *picture → why it is built this way → what it shows → what getting it wrong cost → the evidence*. The paragraphs were made self-orienting instead of moved. |

## Claim ledger (role 1)

| Quoted | Source | Recomputed / checked | Verdict |
|---|---|---|---|
| "39 slices that carry both a baseline and a TTX window" | FOUNDATIONS §9 | "39 archived baseline+TTX slices" | match — removed anyway, see next row |
| "92–100% of them" | FOUNDATIONS §9 | "detect coordination in 92–100% of them under TTX" | match, but **not reproducible** — no committed script produces it (`tools/` has none, and none exists anywhere in history); the site's own build opens no data store. Removed. |
| "two of these ports" | FOUNDATIONS §9 | `sce_detect` and `loco_detect` — two | match — removed with its sentence |
| "slow stream at or above its own baseline" | FOUNDATIONS §9 | "SLOW at or above baseline (SCE 1.24, LoCo 1.28)" | match but **incomplete** — §9 also records FAST at median 0.46 of its own baseline |
| "TTX does not silence the field" | FOUNDATIONS §9 | §9 rules the bare converse out and requires the stream be named | **mismatch** — rewritten to name both streams and their opposite directions |
| "measure the coordination parameters of its baseline" | `src/bugarach/` | no estimator exists; `simulate_coordination` takes hand-set scalars and the measurement was an upstream MATLAB script | **overclaim** — reframed as the plan |
| "the finished instrument" | repo, all branches | no trained model exists in the tree or its history | **overclaim** — now "the training half is the plan, not yet the practice" |

## Role 10 table — checked against the rebuilt render (`site/index.html`, `c7e9e4a`)

| Row | Check | Result |
|---|---|---|
| build currency | built file newer than the last fix and than every embedded input | pass — the rebuild was the last action before delivery |
| horizontal overflow | `scrollWidth > clientWidth` on the rendered page | pass — false |
| text-block geometry | every `<p>` box measured against both figure boxes | pass — largest new block 158 px, clear of both |
| largest text block | words per block | 95, down from 167; page range now 8–95 |
| figure integrity | both figures present, captions clear of their images | pass |
| typography | sentence case, no ALL-CAPS emphasis in prose | pass |
| internal identifiers | no code identifiers in audience-facing text | pass |
| presence | every element the template implies is visible in the render | pass |

**Blind pass, round 1** produced no new defects on the rebuilt file. It did note
that nothing on the page illustrates a recording carrying two streams — carried
forward as residual 3 rather than closed.

## Residual ⚠ — for Tony, not for a session

**⚠ 1 — The page now states a treatment result, and FOUNDATIONS §5 reserves that
call for you.** The paragraph says TTX leaves coordination intact in the slow
stream while reducing it in the fast one. That is a finding derived from paired
baseline+treatment real recordings, and §5 says the released-by-name exception
"is a list of one, not a category… A treatment slice, or a baseline paired with
one, is not covered — those are the results," and that releasing anything else
real "needs Tony, in words."

Two things cut against calling it a violation: the same claim and its numbers are
**already committed in public** in `docs/FOUNDATIONS.md` §9, and the site states
no numbers. What changes is prominence — a line in a foundations doc versus the
second thing a stranger reads on the project's front page. That is a judgement
about unpublished results, so this draft states the finding qualitatively and the
quantities came out. **On your word the 39 slices, the 92–100% and the per-stream
ratios go back in**; the sentence is stronger with them.

**⚠ 2 — The pipeline should be a picture and is not one yet.** Named replacement:
one horizontal schematic — *recording → measure baseline parameters → confirm →
simulate → (tune the detectors ‖ train the model) → analyse the full dataset,
treatments included* — with the treatment entering only at the final box, which is
the whole argument in one image. Filed rather than built, to keep this change to
the text that was asked for.

**⚠ 3 — Minor, naive reader.** "Stream" is glossed in passing ("the two event
streams these recordings carry") but never defined, and the figure above shows one
raster per panel, so nothing on the page shows that a recording carries two.
Resolved for free if the schematic in ⚠ 2 lands; otherwise it wants a clause.
