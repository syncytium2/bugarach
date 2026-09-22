# Murderboard run — `docs/parameter_spec_proposal.md`

- upstream:  syncytium2/murderboard @ f43a07b
- vendored:  050b40a (`docs/doc_review_process.md`)
- freshness: current (`murderboard_freshness.sh --refresh` exit 0)
- artifact:  `docs/parameter_spec_proposal.md` (`9b64065` -> `006b481`)
- roles:     11 of 11 run
- rounds:    1 blind verify round to clean

**Mode.** Single-pass self-review walking every role's checklist in turn, with
agent 10's table produced against the file as it will be read. The deliverable is
a design proposal, not a render — there is no built artifact separate from the
markdown, so "the built file" and the source are the same object.

**Audience matters here.** This is read by Tony *and* by three sessions building
against `simulate_coordination` right now, at least one of which has not followed
today's work. Role 8 was run against that reader, not against a generic stranger.

## Role ledger

| # | Role | Result |
|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 3 findings, ledger below. Every quantity recomputed against the tree; two were wrong and one was imprecise. |
| 2 | Citation & reference validator — "DOI or Die." | No findings, and here is what I checked: the document cites no literature. Its references are internal — three FOUNDATIONS sections and one quotation from Tony — and all four resolve (below). |
| 3 | Consistency auditor — "Cross-Examiner." | No findings, and here is what I checked: the parameter count (25) reconciles with the four background knobs named; the staging list's five steps each correspond to a claim made earlier in the document; "adds two more" for the slow-epoch axis matches the shape+bin pair the existing burst axis needed. Terms `promiscuity probe`, `distractor`, `operating point`, `regime` all exist in `GLOSSARY.md`. |
| 4 | Adversarial reviewer — "Reviewer 2." | 1 finding (F4): the central claim was overstated. Also attacked the migration plan's testability — the `as_kwargs`/`from_kwargs` equality test is a real acceptance criterion with a defined failure, so it survives. |
| 5 | Line editor — "Kill Your Darlings." | No findings, and here is what I checked: every section asserts one thing; the yardstick/ruler metaphor appears once and is not reused; no sentence carries two claims that could be separated. |
| 6 | Methods / domain expert — "RTFM." | 1 finding, folded into F2: the `51–67%` figure was quoted from another session's document rather than computed. Recomputed against `bench.make_recording` vs `bench.make_null_recording` over three seeds per regime. |
| 7 | Reuse auditor — "Reinventing the Wheel." | No findings, and here is what I checked: the proposal adds no analysis code. It proposes reusing `fit_background_shape.py`'s estimator as the fitting stage's core rather than a new one, and explicitly keeps the probe/distractor logic where it already lives in `bench`. |
| 8 | Naive-reader accessibility — "You Lost Me." | No findings, and here is what I checked: read as a session that has not seen today's work. Every term is either defined in place, present in `GLOSSARY.md`, or is a Python identifier that exists in the tree (verified: no named identifier is fictional). The dispersion numbers carry their units and their bin widths. |
| 9 | Density & figure-first — "Show, Don't Tell." | 1 finding, adjudicated as no-change: the "what this unlocks" section is a table, which is the right form; the argument itself is a dependency between stages and could be a diagram, but the audience is three sessions who will act on the text and one human who asked for a written proposal. Recorded rather than acted on. |
| 10 | Build & craft gate — "Ship It." | Table below. |
| 11 | Argument order — "Start With the Problem." | No findings, and here is what I checked: the spine is problem (stated as a number) → the change → what stays out and why → migration → what it unlocks → what the estimator owes → what is still missing → staging → open questions. The cold open is the parameter count, which is the problem, not the design. |

## Claim ledger (role 1)

| Quoted | Source | Recomputed | Verdict |
|---|---|---|---|
| "25 keyword parameters" | `inspect.signature(simulate_coordination)` | 25 | match |
| four background knobs, named | same | `bg_rate_hz`, `bg_rate_shape`, `bg_burst_shape`, `bg_burst_bin_sec` | match |
| "three landed 2026-08-16, hours ago" | `git log -S` | `bg_rate_shape` **2026-08-15**; burst pair 2026-08-16 | **mismatch — F1** |
| "51–67% of realized rate is not background" | another session's plan | **67.2% quiet, 30.6% busy** | **mismatch — F2** |
| "nearly identical totals" (busiest ROI) | status figure | 178 real against 214 generated | **overclaim — F3** |
| var/mean 1.81 / 2.60 / 3.87 / 5.68 | `fit_background_shape.py` | identical | match |
| 57% vs 27% top-three-minute share | status figure | identical | match |
| 28% vs 26% busiest-ROI share | status figure | identical | match |
| FOUNDATIONS §4 "Regions are optional" | `docs/FOUNDATIONS.md:64` | correct section | match |
| FOUNDATIONS §6 "grid_dt is the caller's responsibility" | `docs/FOUNDATIONS.md:95` | correct section | match |
| FOUNDATIONS §9 baseline-only | `docs/FOUNDATIONS.md` | correct section | match |

## Findings

**F1 — landing dates off by a day.** `bg_rate_shape` landed 2026-08-15, not
2026-08-16. Corrected to name both dates. Small, but the sentence's whole job is
to establish *how fast this surface is moving*, and getting the rate wrong in the
argument for slowing the rate is not a detail.

**F2 — a quantity carried from another document rather than computed.** The
`51–67%` figure came from a peer session's plan. Recomputing it against
`make_null_recording` over three seeds gives **67.2%** (quiet) and **30.6%**
(busy) — a range of 31–67%, not 51–67%. The claim it supports survives and gets
stronger at the quiet end. Corrected, with the method stated inline so the next
reader does not have to trust this one either.

**F3 — "nearly identical totals" was not true.** 178 against 214 is 20% apart.
What *is* comparable is the busiest ROI's share of its own recording, 28% against
26%. Rewritten to say that, and to name the totals rather than characterise them.

**F4 — the central claim was overstated (Reviewer 2).** "Adding a background axis
changes no call site" is true for a caller that receives a spec and passes it on;
it is false for a caller that constructs a `BackgroundModel` by naming fields.
The document now says so, and states the narrower claim that actually holds: the
coupling stops being everywhere and becomes countable.

## Role 10 table — checked against the file as it reads

| Row | Check | Result |
|---|---|---|
| identifiers exist | every `bg_*` / `n_roi` / `duration_sec` / `grid_sec` named in prose | pass — all present in the signature |
| proposed identifiers marked | `RecordingSpec`, `BackgroundModel`, `fit_recording_spec` | pass — introduced under "What changes", document is headed **proposal, nothing built** |
| cross-references resolve | 3 FOUNDATIONS sections | pass — §4, §6, §9 all correct |
| code blocks | 2 Python blocks | parse as valid dataclass syntax |
| tables | 2 | render, columns aligned, no empty cells |
| status is unmissable | the word "proposal" and "nothing built" | pass — first line, bold |

**Blind pass, round 1** re-derived the parameter count, the identifier existence
check and the FOUNDATIONS section numbers mechanically against the corrected file,
and produced no new findings.

## Residual ⚠ — for Tony

The document's three open questions are deliberate and unresolved: whether
recording shape (`n_roi`, `duration_sec`, `grid_sec`) belongs in the same object
as the fitted models, whether the deprecation window is worth its cost against
cutting the keywords immediately, and whether the bench moves onto a fitted
background inside this change or after it. None is a session's to decide; all
three change what gets built.

---

## Round 2 — same day, after the ground moved

Two PRs landed or opened against the same area between round 1 and delivery, so
the artifact was revised and re-verified. `006b481` -> `96928dc`.

- **PR #46 (merged).** `PlantedEvent` now carries `onsets` — the onset each
  participant actually got — and `observed_span`. The proposal's DL-training row
  claimed a spec makes "targeted to this dataset" checkable; that was true of the
  *distribution* and silent about the *labels*, which were a parametric
  restatement of the request until this landed. Row rewritten to say both.
- **PR #48 (open).** Reverses FOUNDATIONS §6 from "caller's responsibility at
  detection time, warning on fallback" to a refusal at the load boundary. The
  proposal cited §6 for the `grid_sec` bullet. Round 1 verified that citation
  against `main` and it was correct then and is correct now — #48 has not merged
  — but shipping a proposal that would be wrong on someone else's merge is a
  defect with a delay on it. The bullet now states §6 as it stands, names the
  reversal in flight, and says why it strengthens rather than changes the point.
- **Added, not from either PR:** `grid_sec` and `grid_dt` mean the same physical
  quantity and are not the same knob — the generator's quantizes planted onsets
  at construction. Two sessions are converging on a fitting stage that returns
  this field; the ambiguity was worth naming before they meet in it.

Re-verified mechanically against the revised file: parameter count still 25, all
seven named identifiers exist (`PlantedEvent.onsets` and `observed_span` now
among them), both PR numbers resolve to real PRs in the states the document
claims. **Blind pass produced no new findings.** Roles 1, 3 and 4 re-run in full
because the edits were claims; roles 2, 5–11 unchanged and their round-1 entries
stand — no citation, prose, method, reuse, reader, density, craft or ordering
surface was touched.
