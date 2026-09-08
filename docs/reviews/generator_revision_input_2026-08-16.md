# Murderboard run — docs/generator_revision_input.md
- upstream:  syncytium2/murderboard @ f43a07b
- vendored:  f43a07b
- freshness: current
- artifact:  docs/generator_revision_input.md (98ba6cc -> 64b2163)
- roles:     11 of 11 run
- rounds:    1 blind verify round to clean

Run as a single-pass self-review walking every role's checklist in turn, not a
parallel fan-out. Every role ran; what scaled was how, not which.

**The freshness gate fired first, and its diagnosis was wrong in an instructive
way.** It reported STALE (vendored `b2b2ba2` vs upstream `f43a07b`). The
murderboard was not stale — `origin/main` already carried `f43a07b`. The
*worktree* was: it had been branched from a local `main` **41 commits behind
origin**, so it inherited a vendored copy another session had already refreshed.
The gate caught a stale base from the other direction, which is the outcome its
own warning describes ("vendoring onto a leaf branch leaves every new worktree
inheriting the old copy"). Merging `origin/main` cleared it.

That stale base also invalidated the draft's lead finding — see role 1.

---

## Role ledger

| # | role | findings | outcome |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | **4** | 2 fixed, 1 rewritten, 1 flagged `⚠` |
| 2 | Citation & reference validator — "DOI or Die." | 0 | no findings — checked the only two external references (PR #46, PR #48); both exist and are correctly numbered. No papers, DOIs or named attributions in this document. |
| 3 | Consistency auditor — "Cross-Examiner." | **2** | both fixed |
| 4 | Adversarial reviewer — "Reviewer 2." | **3** | all fixed |
| 5 | Line editor — "Kill Your Darlings." | **1** | fixed |
| 6 | Methods / domain expert — "RTFM." | **1** | fixed |
| 7 | Reuse auditor — "Reinventing the Wheel." | **2** | both fixed |
| 8 | Naive-reader accessibility — "You Lost Me." | **2** | both fixed |
| 9 | Density & figure-first — "Show, Don't Tell." | **1** | fixed |
| 10 | Build & craft gate — "Ship It." | **2** | both fixed |
| 11 | Argument order — "Start With the Problem." | **1** | fixed |

---

## Findings

### Role 1 — Prove It (4)

Claim ledger, every quantity recomputed rather than eyeballed.

| quoted | source | recomputed | verdict |
|---|---|---|---|
| probe events/ROI = 18.0 | `hot_rate_hz × span` | **17.08** | **MISMATCH — fixed** |
| probe share 41% | derived from above | **39.7%** | **MISMATCH — fixed** |
| silent 26.7% shaped / 0.0% with probe | measured, 40 seeds | 26.7 / 0.0 | match |
| 34.5% at 1200 s | measured | 34.5 | match |
| 35% in real windows | `bench.MEASURED_RATE_SHAPE` | present in source | match, **source now named** |
| CV 0.150 / 1.025; spread 1.5× / 6.6× | measured, 30 seeds | as quoted | match |
| ρ +0.04 (p 0.21) / −0.06 (p 0.04) | measured | as quoted | match |
| ±3σ = 2.16 s; realized median 0.80 s | measured, 75 events | as quoted | match |
| 0.80 → 0.90 under fitted background | measured | as quoted | match |
| 17 configs × 3 seeds bit-identical | re-run post-merge | empty diff | match |
| `MEASURED_RATE_SHAPE` 0.275, `MEASURED_BURST_SHAPE` (1.547, 1.388) | `bench.py` | as quoted | match |
| upstream files marked PROVISIONAL | `simulation_plan.md` §6 | **not reachable from here** | **`⚠` flagged** |

1. **The whole draft was measured against a 41-commit-stale generator.** The lead
   finding — "per-ROI rate is homogeneous, build heterogeneity" — was already
   built, fitted and documented on `origin/main`. Re-measured after merging; the
   section was rewritten from "build this" to "the fitted values and the probe
   cancel when both are on."
2. **18.0 probe events/ROI was computed, not measured**, ignoring `ramp_sec`'s
   linear wash-in. True value 17.08; the derived share fell 41% → 39.7%.
3. **The 35% figure cited no source.** Now attributed to
   `bench.MEASURED_RATE_SHAPE` with its own basis (81 windows / 2 643 ROIs).
4. **Two claims about upstream MATLAB files are unverifiable from this repo**
   (they need MATLAB + an interface2 checkout). Restated as quoted from
   `simulation_plan.md` §6 and flagged `⚠`, with the generator team named as the
   party who can check them. **Residual — see below.**

### Role 3 — Cross-Examiner (2)

1. **§1 implied the bench runs a shaped background.** It does not — both knobs
   are off by default. The section read as "something is broken now" when the
   finding is "this bites when the revision turns it on." Rewritten with that
   stated explicitly, which also lowers the urgency honestly.
2. **Terminology against the glossary:** `coactivity`, `stream`, `distractor`,
   `extent` all used in their defined senses; "modality" absent. `n_rate_quantiles`
   was considered for this document and **not used** — it is unlanded vocabulary
   from a paused design conversation and had no business in a handoff.

### Role 4 — Reviewer 2 (3)

1. **The figure was drawn on seed 1 — the maximum of all 40 seeds** (14/33 silent
   against a mean of 8.8). The single most flattering choice for the document's
   own argument, and unreproducible for a reader who ran any other seed. Switched
   to seed 8 (9/33, nearest the mean) and the reason recorded in the tool.
2. **"Negligible" asserted over a p = 0.04 result** with no effect size. Now
   states ρ² = 0.004 — under 0.5% of variance — so the reader can judge rather
   than take the adjective.
3. **"41% of activity from 11% of duration" rested on a computed number.**
   Superseded by finding 1.2; the measured version is quoted and the discrepancy
   is shown rather than hidden.

### Role 5 — Kill Your Darlings (1)

§1 argued the same point three times (probe is flat, probe is severe, probe is a
setting). Collapsed; the severity argument now appears once and the "not an
argument for a weaker probe" concession carries the rest.

### Role 6 — RTFM (1)

**`hot_rate_hz × span` is not how the generator applies the probe.** `ramp_sec`
thins the wash-in linearly, so the naive product overstates by half the ramp.
This is the misused-API class exactly: the prose was self-consistent and the
number was wrong because the method's own parameter was ignored. Fixed by
measuring the generator's output instead of modelling it.

### Role 7 — Reinventing the Wheel (2)

1. **Every quantity came from throwaway scripts**, so nothing in the document was
   re-derivable — while the generator team's own values ship with
   `tools/fit_background_shape.py`. Added `tools/probe_vs_heterogeneity.py`,
   which prints every number §1 quotes and renders the figure.
2. **The tool initially re-derived the render path.** Rewritten to call
   `bugarach.ui.diagnostic.raster_panel`, `bugarach.ui.app._time_axis_hook`, and
   `make_generator_figures._write` — the last of which writes to a temp name and
   moves into place, because writing into Dropbox in place once left 188 MB of
   hash-named orphans. Re-deriving it would have re-derived that bug too.
   Constants come from `bugarach.bench`, never retyped.

### Role 8 — You Lost Me (2)

Audience is the generator team: expert, different project. Read for terms whose
meaning is local to bugarach.

1. **"promiscuity probe" used before definition** — it is this repo's word for
   `hot_window`. Defined at first use.
2. **"participant floor" used undefined** in the closing offer. Glossed.

Checked and clean: `bg_rate_shape` / `bg_burst_shape` / `hot_rate_hz` are the
generator team's own parameter names, so they are the plain language here, not
internal identifiers to be hidden.

### Role 9 — Show, Don't Tell (1)

**§1's finding is visual and was written as prose.** A silent-ROI tail being
filled in is exactly what a raster shows and a percentage does not. Replacement
figure named and built: three rasters, quietest ROI at the bottom — flat + probe,
shaped without probe, shaped + probe. CLAUDE.md's standing rule ("if a finding is
visual, render it before writing about it") makes this blocking, not advisory.

Judged and left as prose, stated per the role's requirement: **§2** (participation
independent of rate) — a scatter of rate against participation is a structureless
cloud, and "the cloud has no slope" is carried better by ρ² than by an image.
**§3–§6** are asks and constraints, not data.

### Role 10 — Ship It (2)

Table, checked against the rendered PNG at each stage.

| panel | render | axes | overlap | legibility |
|---|---|---|---|---|
| flat · probe on | `probe_vs_heterogeneity.png` (2064×1528) | y: identity + count; x suppressed per plot conventions | clear | pass |
| shaped · probe off | same | same | clear | **FAIL round 1 → fixed** |
| shaped · probe on | same | x-axis bottom row only, 60-base ticks (`10m`/`20m`) | clear | pass |

1. **Rotated y-labels clipped at both ends** — the middle panel rendered `14/3`,
   losing a digit off a count. Same class `make_generator_figures` documents at
   196 px rows. Fixed by shortening the labels and moving the explanation into
   the caption, where it is set in document type and cannot be cut.
2. **The caption referred to panels as "Row 2" / "row 3"** — spatial panel
   references, which the process forbids. Now named by their own labels.

Checked and clean: shared y-limits (0–33) across all three panels, same
measurement; the shaded probe span is identified in the caption; time axis uses
60-base ticks per CLAUDE.md; no ink at the page edge.

### Role 11 — Start With the Problem (1)

Spine, one claim per section: §1 two features cancel · §2 a modelling choice
nobody made · §3 the label restates the request · §4 tightness needs samples ·
§5 a negative that does not exist · §6 what must not be re-broken.

**The arc deviated from the default and did not say so.** This is not
problem→cost→method→fix; the fixes belong to the reader. Ordering is now stated
in the opening: live choices first, durable gaps second, constraints last.

---

## Residual ⚠ — for the human

**One, and it is the document's only unverified claim.** §6 quotes
`docs/simulation_plan.md` §6 asserting that `rederive_optima_fast.m` still marks
the coordination-timescale parameters PROVISIONAL, and that `optim_history/README.md`
records the calibrated settings being adopted without the real-data validation.
Both live upstream and need MATLAB plus an interface2 checkout, which this repo
deliberately does not require. Flagged inline, attributed to the doc it came
from rather than asserted, and the generator team is named as able to check it.
If either has been closed since `simulation_plan.md` was written, §6 overstates.
