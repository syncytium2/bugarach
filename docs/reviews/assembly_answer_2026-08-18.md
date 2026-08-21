# Murderboard run — `<darkroom>/bugarach/assembly_answer.{html,png}`

> **Superseded 2026-08-18, later the same day.** The artifact this run reviewed has been
> replaced: the group workbook arrived, ⚠1 below is resolved, and the figure now leads
> with the group split rather than the pooled result. Two things this run recorded are
> now known to have been wrong in the reviewed version — it included a slice the lab
> marks `exclude`, and it reported a pooled number FOUNDATIONS §9 does not admit. Neither
> was caught by any of the eleven roles, because none of them knew the workbook existed.
> **That is a finding about this review, not just about the figure**, and it belongs in
> the upstream murderboard change alongside the point that this record leads with a
> ledger instead of a picture.
- upstream:  syncytium2/murderboard @ 57445b4
- vendored:  57445b4 (re-vendored during this run — see *Preflight*)
- freshness: current
- artifact:  `<darkroom>/bugarach/assembly_answer.html` (`46a75af` -> `8106659`)
             `<darkroom>/bugarach/assembly_answer.png`  (`a34b11e` -> `fa76b9c`)
- roles:     11 of 11 run
- rounds:    2 blind verify rounds to clean (round 2 produced no new findings)

**Mode.** Single-pass self-review walking all 11 role checklists in turn, not an
11-subagent fan-out. The process permits this for a figure-and-caption deliverable;
this session additionally operates under an instruction not to spawn subagents
unrequested. Stated here because a dropped role and a clean role are
indistinguishable in a report, and the mode is what makes the difference checkable.

**Preflight.** `murderboard_freshness.sh --refresh` exited **1 — STALE** (vendored
`783501e`, upstream `57445b4`) and the review stopped there. All four vendored files
were re-copied and re-stamped, then landed on this branch toward `main` rather than
left on a leaf. What changed upstream between the two shas is **nothing this repo
vendors** — the diff is upstream's own harness (a no-heredoc hook, `settings.json`) —
so the review rules were byte-identical and the branch diff is four stamp lines. The
gate was still right to refuse: it cannot know that, and neither could I before
looking.

## What is being reviewed

The figure answering `docs/todo/2026-08-18-do-real-slices-have-recurring-assemblies.md`
against the real corpus. Generator: `tools/make_assembly_figure.py`. Inputs: two
`assess_archive.py --assemblies` runs over
`event_store_onset_revised_2v_alive_rescued` (85 `.mat` slices), one per stream.
Both the generator (roles 6–7) and the built render (everything else) were reviewed.

## Role ledger

| # | Role | Findings | Note |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 3 | claim ledger below; all quantities recomputed from the run JSONs |
| 2 | Citation & reference validator — "DOI or Die." | 0 | **Nothing to check, and here is what I checked:** the caption carries no bibliographic references. Its only citations are internal — `FOUNDATIONS §9` and figure `roi_rate_distribution`. Both verified to exist and to say what is claimed (§9's last bullet is "Group-dependence is not optional"). Marchenko–Pastur and the Lopes-dos-Santos/Peyrache line are named in `bugarach.assembly`'s docstring, not in the deliverable, so they are out of scope here and remain unverified against the papers — see residual ⚠3. |
| 3 | Consistency auditor — "Cross-Examiner." | 2 | figure↔caption counts reconciled; category order consistent |
| 4 | Adversarial reviewer — "Reviewer 2." | 5 | the substantive haul, including the independence defect |
| 5 | Line editor — "Kill Your Darlings." | 2 | |
| 6 | Methods / domain expert — "RTFM." | 2 | curveball invariants, Fisher's independence assumption |
| 7 | Reuse auditor — "Reinventing the Wheel." | 2 | one fixed, one filed |
| 8 | Naive-reader accessibility — "You Lost Me." | 2 blocking | per-panel verdict below |
| 9 | Density & figure-first — "Show, Don't Tell." | 1 | with a stated deviation |
| 10 | Build & craft gate — "Ship It." | 4 | table below, against the NEW render |
| 11 | Argument order — "Start With the Problem." | 1 | |

## Role 1 — claim ledger

Every quantity recomputed from `asm_fast/assessment_real.json`,
`asm_slow/assessment_real.json`, and the control run. No value was eyeballed.

| Quoted | Source | Recomputed | Verdict |
|---|---|---|---|
| 85 baseline recordings | store listing | 86 entries, 85 `.mat` + `dead_roi_manifest.csv`; tool reports `n_files` 85, all 85 assessed | match |
| FAST 28/49 reject both, K=3 | fast run rows | 49 testable, 28 `structure-beyond-rate` | match |
| SLOW 30/40 reject both, K=3 | slow run rows | 40 testable, 30 | match |
| control 1/40 | control run | 40 testable, 1 | match |
| alpha/2 threshold | `bugarach.assembly.AssemblyResult.verdict` | 0.05/2 = 0.025 | match |
| fewer than four clusters → no null | `bugarach.assembly.MIN_EVENTS` | 4 | match |
| 1/1001 resolution floor | `pvalues_*` return `(1+ge)/(1+n_surr)`, n=1000 | 9.99e-4 | match |
| 19/31 and 21/26 preparations | slice-id date prefixes | recomputed | match |

**F1.1 (fixed).** "This corpus has strongly heterogeneous ROI rates" was asserted in
the caption with no source in this deliverable. The claim is true and *measured* —
but elsewhere (figure `roi_rate_distribution`;
`docs/todo/2026-08-14-generator-background-model-is-flat.md`). A self-describing
explanation is still a claim. **Fix:** attributed in the caption to the figure that
measured it.

**F1.2 (fixed).** "One point per recording" over-counted: panel A plots only
*testable* recordings (49 of 85 FAST). **Fix:** "one point per *testable*
recording", with the excluded count and its reason stated.

**F1.3 (fixed).** The geometry the power curve was sized on was wrong, and the error
was in this deliverable's lineage rather than its caption. The curve assumed 21
clusters (spec `duration_sec` 3525 s x 0.35/min); a *testable* slice carries a median
of **38** clusters in a **1200 s** baseline window. `clusters_permin` is a median over
all 85 slices, most of the way down it being slices too thin to test. **Fix:** the
control's cluster count is now matched to the testable slices (38, not 7), and the
correction is recorded in the commit and the todo. Consequence worth stating: the
power curve was *conservative* for the slices it applies to, but it was not
describing them.

## Role 3 — consistency

**F3.1 (fixed).** Panels were referred to as "Left"/"Right". Role 10 forbids spatial
words. **Fix:** lettered A/B, carried in the y-axis labels so the repo's no-titles
plot convention is not broken, and the caption now says A and B.

**F3.2 (fixed).** The headline claimed "at every coactivity floor". Defensible but
thin at K=8 FAST, where `structure-beyond-rate` is 7 of 14 — the largest block by
one slice. **Fix:** the headline no longer generalizes across K; it states the K=3
result and panel B shows the rest without a claim attached.

Checked and clean: figure↔caption counts agree (B's K3 bars total 49 and 40);
category order is identical across all eight bars; no glossary term is reused for a
new concept; "modality" does not appear; "stream" is used in the glossary's sense.

## Role 4 — adversarial

**F4.1 (fixed, and the most serious).** *"Independent methods agree" — is it really
independence?* Two separate failures of independence, both live:
- **The two nulls are nested, not independent.** Uniform participation is the
  stronger assumption; the margin null is strictly weaker. "Rejects both" was
  presented in a way a reader could take as two agreeing tests. **Fix:** the caption
  states they are nested and that rejecting both is one conclusion, not two.
- **The slices are not independent.** 85 slices come from **48 dates**, up to three
  per preparation. Fisher's combination assumes independence, so the pooled p is
  anti-conservative — and the earlier PR text quoted it (`p=3.99e-25`). **Fix:** the
  figure does not quote a pooled p at all; it reports counts by **preparation**
  alongside slices (19/31 FAST, 21/26 SLOW), and `assess_archive.py` now prints the
  pooled value with both violated assumptions attached and "quote the tally, not
  this".

**F4.2 (fixed).** Overreach in the headline. The test shows co-participation
structured beyond per-cell rate; that does not establish a *discrete recurring
group*, which is what "assembly" implies to a reader. **Fix:** headline states what
was measured, and a closing line says structure "does not by itself make it one
discrete recurring group".

**F4.3 (fixed).** Undefined quantity: the p-values' surrogate count was nowhere, and
dozens of points sit exactly on the axis edge where they read as identical values.
**Fix:** both axes name "1000 surrogates" and the caption explains the 1/1001 floor.

**F4.4 (no change — the check passes).** *"Can the alarm ring?"* This is the one the
role exists for, and the deliverable satisfies it rather than needing a fix. The
failure the claim denies is constructible and was constructed: 40 generated
recordings, participants drawn by `rng.choice`, matched on ROI count and cluster
count, run through the identical code path. The number moves — 1/40 against 28/49.
The instrument also has a *positive* control on the other side, in
`tests/test_assembly.py`, and one null is known-blind at saturation and documented as
such.

**F4.5 (fixed).** *Read the picture, not the caption.* Panel A overplots hard: many
slices share the floor exactly, so no reader can count 28 from the image, and a
reader trying to would conclude the caption disagrees with the figure. **Fix:** the
caption assigns the jobs explicitly — A shows the separation, B carries the counts.

## Role 5 — line editing

**F5.1 (fixed).** "Dotted lines are alpha/2, the threshold each null is *actually*
read at" — filler intensifier removed.

**F5.2 (fixed).** The caption opened by asserting an answer with no statement of the
question, so the first sentence did two jobs badly. **Fix:** it opens with the
question, then answers it. (Overlaps role 11; filed once, here.)

## Role 6 — methods

**F6.1 (no change, verified).** Curveball randomization obeys its invariant: row
sums and every column sum are conserved. Verified two ways — by construction in
`_trade` (membership moves only between two events and only among ROIs exactly one of
them holds) and by `tests/test_assembly.py::test_trade_conserves_both_margins`
asserting exact equality of both margin vectors after 400 trades. Chain is burned in
and advanced one sweep between surrogates (sequential sampling); empirical size is
nominal at 0.05, so mixing is adequate at these sizes.

**F6.2 (fixed).** Fisher's combination requires independent tests; see F4.1. The
method was applied correctly and to an input that does not satisfy it.

Also checked: the control path uses `n_surrogates=50` for the *assessor* while the
real runs used 1000. This does **not** validate a different tool — membership comes
from the observed clustering only, and the assessor's surrogate ensemble feeds the
coactivity null, which this figure does not read. The assembly test itself runs at
the production 1000 in both. Documented in the code at the call site.

## Role 7 — reuse

**F7.1 (fixed).** `_xy` re-derived the verdict's min-of-two-statistics reduction
locally. If `verdict` changed, the axes would put points on the significant side of a
line that no longer called them significant. **Fix:** the coupling is documented at
the reduction and the threshold is taken from `bugarach.assembly`'s alpha rather than
a second literal.

**F7.2 (filed, not fixed — ⚠2).** `_render_png` is now duplicated in three tools
(`make_roi_rate_distribution.py`, `assembly_power.py`, `make_assembly_figure.py`).
Refactoring three tools mid-review would put untested edits into two deliverables
this review did not cover — role 4's scope rule cuts against it. Filed as a todo.

Confirmed reused rather than re-derived: the statistics, both nulls, the verdict and
the generator all come from the package; nothing in this tool re-implements them.

## Role 8 — naive reader, per panel

| Panel | Terms first used here | Defined on the figure? | Cold reader can follow? |
|---|---|---|---|
| A | K, "both margins fixed", "uniform participation", per-cell rate, surrogate, alpha/2, resolution floor | **now yes** — K defined in the standfirst; both nulls glossed in plain words; floor explained | yes |
| B | the four verdicts, "testable" | **now yes** — all four keyed in their own colours; "testable" defined by the undefined-vs-negative sentence | yes |

**F8.1 (fixed, was blocking).** Panel A introduced four-plus undefined terms,
including **K**, which appeared as bare "K=3". Per the role's rule that is a blocking
row named by panel, not a line in a list. **Fix:** K is defined in the second line;
each null is glossed in plain language where it is first named.

**F8.2 (fixed, was blocking).** **Panel B's four colours were never explained at
all** — `show_legend=False` and no key in the caption. The panel carrying every count
in the deliverable was unreadable. **Fix:** all four verdicts named in the caption in
their own bar colours.

## Role 9 — density and figure-first

**F9.1 (partially fixed; deviation stated).** The caption runs ~250 words, above any
reasonable convention for a figure caption, and the role's rule is that a caption
says what the figure shows and why it matters. **Deviation, stated as the role
requires:** the caveats are kept on the face of the figure rather than relocated. The
role's own "relocate, don't delete" rule requires a *named* destination where the
reader still meets them, and this artifact ships as a standalone darkroom figure with
no deck, notes pane, or surrounding document — the only alternative destination is
this run record, which its readers will not open. Trading a rigor defect for a craft
one is the worse trade by the role's own text. Wording was tightened; the caveats
stay.

Measured: figure occupies roughly 62% of the render's height and its full width; no
panel is under half the canvas; no empty side margins. Prose share ~38% by height,
concentrated in one block above the panels.

## Role 10 — build and craft gate

Checked against the **new** render, `assembly_answer.png` `fa76b9c`, modified
14:03:09, **newer than** its generator (14:02:41) and both input JSONs.

| Row | A (scatter) | B (stacked bars) |
|---|---|---|
| Build current | yes — newer than last fix and all inputs | yes |
| Nothing overlaps / runs off page | clear; tick labels clear of axis titles | clear; rotated category labels clear |
| Everything the source implies is present | 3 series + 2 threshold lines, all present | 4 stacked categories x 8 cells, all present |
| Axis named with units | x "p · uniform participation, 1000 surrogates"; y "A · p · both margins fixed, 1000 surrogates" — p is dimensionless, resolution named | x "coactivity floor K · stream"; y "B · slices with a testable answer" |
| Panels lettered, not spatial | **A** in y label | **B** in y label |
| Every colour/marker identified | circles/squares/diamonds named in their colours | all four verdicts keyed in their colours |
| Category colours contrast | black / blue / orange — distinct | green / orange / purple / mid-grey — all legible as text and as fill |
| Shared y-limits where same measurement | n/a — different quantities per panel | n/a |
| No vertical lines annotating a histogram | n/a (scatter) | n/a (bars, not a histogram) |
| One glyph per concept | consistent: circle=FAST, square=SLOW, diamond=control | one colour per verdict throughout |
| Rendered box | ~38% of render width, ~62% height | ~38% width, ~62% height |

**F10.1 (fixed).** Panels referred to by spatial words — see F3.1.
**F10.2 (fixed).** Panel B's x-axis was unlabeled (`xlabel=""`), and its categories
("K3 fast") were not self-describing with K undefined. **Fix:** axis named.
**F10.3 (fixed).** Panel B's colours unexplained — see F8.2.
**F10.4 (fixed, blind pass round 1 — a regression from F8.2's fix).** Keying the
verdicts in their own colours rendered "neither" in `#b9b9b9` on white: legible as a
bar fill, illegible as text. The fix for a missing legend created an unreadable one —
the exact failure mode the process's step-4 sub-checks (a) and (c) describe. **Fix:**
both the fill and the key word moved together to `#7d7d7d`.

## Role 11 — argument order

Spine of the caption, one claim per line:

1. The question, and its answer stated as what was measured.
2. Corpus, streams, and the parameter the answer is quoted at.
3. A: how to read the two axes, and what the control establishes.
4. B: the counts, by verdict.
5. The three things that qualify the counts.
6. What the result is not, and where the rest lives.

**Arc used**, as the role requires naming: *question → answer → how the evidence is
laid out → the evidence → what qualifies it → what it does not show*. This is a
deliberate deviation from the default problem-first arc: the artifact is a
single-figure result, and its reader arrives from the todo that already states the
problem.

**F11.1 (fixed).** The pre-review caption opened on the assertion with the question
nowhere on the figure — the reader met an answer to a question they had not been
shown. Fixed with F5.2.

## Verify passes

- **Round 1, blind.** Two new findings, both first-class: F10.4 (the illegible key
  the earlier fix created) and F4.5 (panel A's overplotting makes its counts
  unreadable). Neither was on the original list; the blind pass is what surfaced
  them, and F10.4 existed only because of a round-0 fix.
- **Round 1, follow-up** against the original list: F1.1 fixed · F1.2 fixed · F1.3
  fixed · F3.1 fixed · F3.2 fixed · F4.1 fixed · F4.2 fixed · F4.3 fixed · F4.4 no
  change needed · F5.1 fixed · F5.2 fixed · F6.1 no change needed · F6.2 fixed ·
  F7.1 fixed · F7.2 deferred (⚠2) · F8.1 fixed · F8.2 fixed · F9.1 deviation stated ·
  F10.1–3 fixed · F11.1 fixed. Nothing **moved**; nothing silently downgraded.
- **Round 2, blind.** No new findings. Role 10's table above is round 2's, against
  the shipped render.

## Residual ⚠ — for the human

- **⚠1 — no group split, and the number is not admissible without one.**
  FOUNDATIONS §9 says a pooled across-group figure can hide a sign change and is not
  admissible alone. Slice group does not travel with the store, so it cannot be done
  here. **Needs:** the slice→group mapping from whoever holds it. Until then every
  count in this figure is pooled and labelled as pooled.
- **⚠2 — `_render_png` duplicated across three figure tools** (F7.2). Filed rather
  than fixed, to avoid untested edits to two deliverables outside this review.
- **⚠3 — the assembly literature is cited in code, unread.** `bugarach.assembly`
  names Marchenko–Pastur and the Lopes-dos-Santos/Peyrache line as the classical
  instrument. Neither paper was fetched (the lit tool is deliberately not vendored
  here). The figure makes no claim resting on them, so this is not a defect in the
  deliverable — but before any write-up leans on the eigenvalue statistic as "the
  standard method", the papers need reading.
- **⚠4 — "structured" is not "discrete assemblies".** The measurement supports the
  former. Establishing the latter needs a different analysis — clustering the
  membership matrix and showing the groups are stable — which nothing here does.
