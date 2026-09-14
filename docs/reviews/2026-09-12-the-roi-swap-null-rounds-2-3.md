# Murderboard on the ROI-swap proposal — blind verify rounds 2 and 3

> Companion to [roles 1-4](2026-09-12-the-roi-swap-null-roles-1-4.md) and
> [roles 5-11](2026-09-12-the-roi-swap-null-roles-5-11.md), which were round 1. Landed as the reports
> arrived, scrubbed only for absolute paths.
>
> **Every reviewer in these rounds was a fresh agent given the artifact and no finding list** — a
> blind pass, per the process. The grant lines are the reviewers' final declarations.

---

## Round 2 — blind claims pass on revision 2

`murderboard-prove-it`, fresh instance. **GRANT 1 ok — Read, Grep, Glob, Bash.**

Four claims wrong in ways that matter, and three of them are revision 2's own ⚠ caveats and open
questions, which the sources already answer or contradict.

| # | quoted claim | recomputed / correct | verdict | sev |
|---|---|---|---|---|
| 1 | "roughly 39% of the negative class is bit-identical to the positive class"; identical pairs "are coin flips" | `unchanged_share` is a share of **ROIs**; the discriminator's unit is the pooled window pair, identical only when every ROI in the window is unchanged. Windows with no event in any ROI: **146/1669 (8.7%) fast, 207/1669 (12.4%) slow**. `surrogate_discriminator.py` never mentions `unchanged`, so there is no exclusion. | WRONG (unit), ⚠ settleable | high |
| 2 | "If group is perfectly nested in imaging date, this cannot be run… Produce the group-by-date crosstab first." | `slices.csv`: 42 dates, **0 dates with more than one group**, every mouse on one date. By the document's own rule the side quest cannot run on this cohort. | verifiable, not settled | high |
| 3 | four papers "open asks in lit_needed.md"; Cunningham & Yu "has been added" | **None of the four is in the file**, on any branch. | WRONG | high |
| 4 | "every generator leaves about 39%… flat in J" | isi_dither 0.572, joint_isi 0.577, pattern_jitter 0.547, operational_time 0.488 (pooled medians). The quoted three numbers are slow-stream. Not flat in J on fast: trial_shift 0.455-0.461 at J 0.1 falling to 0.381 at J 2.5. The per-stream minimum equals the zero-event share. | WRONG | high |
| 5 | "Those ROIs are empty baselines" | zero-event share 0.379 fast, 0.390 slow — equals the unchanged floor to three decimals | CONFIRMED (now measured) | — |
| 6 | "six of twelve positive controls" unpowered | **seven**: fast J 0.8/1.6/2.5, slow J 2.5/2.8/5.6/11.2 | WRONG | medium |
| 7 | MDA "about 0.543 — below the 0.5386 it was voided on" | exact MDA 0.544, which is **above** 0.5386; power at 0.5386 is 0.70 | WRONG (direction) | medium |
| 8 | "a chimera leak of 0.52 is invisible" | at 1669 pairs power at 0.52 = 0.49; the gate is declared at mouse level where MDA is **0.684** | overstated | medium |
| 9 | "Rate runs down over a recording" | median recording has **more** events in the second half: fast +4.3% (58%), slow +14.7% (71%) | WRONG on this data | medium |
| 10 | "543 windows from 29 recordings" | the senktide cohort, not `steps_excluded`; each displayed row is a range over six | misdescribed | medium |
| 11 | 0.1 s grid alignment as "the signature of a pipeline constant" | all 84 recordings are at 0.1 s, so alignment is no evidence; the run report says the shortest emittable interval "is the producer's number and is not known" | overconfident | medium |
| 12 | "re-quantised from a 0.05 s grid" | no 0.05 s grid on steps_excluded/senktide; cossart varies 0.0926-0.1190 s | hypothetical as fact | medium |
| 13 | "misses a pattern the other **five** find" | "the other **four**" | WRONG | medium |
| 14 | hyperscanning "with its own critique literature" | no paper cited, not marked not-held | UNVERIFIABLE | medium |
| 15 | "the exit criterion requires both" folders | the criterion is only proposed, in an open todo | overstated | medium |
| 16 | rate IQR 0.0052-0.0190 | per-ROI including zeros: p25 **0**, p75 0.0100; nothing reproduces the range | ⚠ settleable | medium |
| 17 | "the Windows workstation has a live session" | board block dated 2026-09-11; the 2026-09-12 handoff records the thread stopped | unsupported | medium |
| 18-28 | "sums over cells" (a mean) · `sd_count` top-weighted only on seed 0 · 0.357/124 are normal approximations (exact 0.386/129) · cossart range selective · duration channel small (75/84 at 1200 s) · Amarasingham calls trial shuffling "another, familiar" example · NCE condition is uniqueness not existence · `trial_shift` adapts rather than is Stella's method · "two sessions" unrecorded · `correction_reach(13)` already computed · "guaranteed" unsourced | — | low |

All of these were applied in revision 3 — see the proposal's revision note.

---

## Round 3 — blind claims pass on revision 3

`murderboard-prove-it`, fresh instance. **GRANT 1 MISMATCH — missing Grep, Glob; held Read, Bash.**
Bash covered the searching, so no check was skipped.

| # | quoted claim | recomputed / correct | verdict | sev |
|---|---|---|---|---|
| 1 | "at **month** resolution, 9 of 22 months contain more than one group" | **14 months, 10 with more than one group.** No count gives 22 or 9. | WRONG | **high** |
| 2 | Tony stopped the thread "with 'do not run anything'" | Tony's recorded answers: **"Need to discuss further before deciding."** and **"Stop here for now."** "do not run anything" is the handoff author's own instruction. | WRONG — words attributed to Tony he did not say | **high** |
| 3 | the run record link | the file does not exist | WRONG (dead link) | high |
| 4 | "twenty-eight more defects, four of them serious" | no round-2 report on disk at the time | UNVERIFIABLE | med-high |
| 5 | "ISI-dither and joint-ISI families 48-58%" | isi_dither 0.552-0.594, joint_isi 0.551-0.595; **48% is operational-time dither** (0.479-0.551). The revision note's correction repeats the error. | WRONG | medium |
| 6 | "The ROI swap inherits this exactly" | untouched share is `(1 - k/N) + (k/N)·p_both`; with independent uniform donors a full chimera has p_both ≈ 0.379² = **0.144** fast, 0.152 slow | WRONG | medium |
| 7 | 8.7%/12.4% "an upper bound on identical pairs" | values confirmed; **the bound is not** — pooled features collapse shifted trains to identical vectors, and an empty real window can gain onsets from a neighbour | WRONG (reasoning) | medium |
| 8 | "A chimera has k+1 contributing mice" | 35 of 44 mice have two or more recordings; **at most** k+1 | WRONG | low-med |
| 9 | cossart "0.039-0.073" | dead_time_dither reaches 0.0750; interval_shuffle control 0.130 | range too narrow | low-med |
| 10 | "75 of 84 baseline windows are exactly 1200 s" | confirmed for **analysis** windows; the export's baseline **periods** are 51/84 at 1200 s, up to 1860 s | confirmed, qualified | low-med |
| 11 | floor 0.379/0.390 "recomputed from the export folder" | 0.3791/0.3897 on `steps_excluded`; **0.3673/0.3707** in the approved periods folder where step events are kept | confirmed on steps_excluded; folder unnamed | low-med |
| 12 | `f` "the pseudo-trial parameter" | `f` is the **dead time** | WRONG label | low |
| 13 | "about 129 mice" | first crossing of 80% power; the repo's `required_pairs` rule gives **141** | confirmed as first crossing | low |
| 14 | drift +4.3% (58%) / +14.7% (71%) | medians confirmed; shares exclude one tied recording per stream (57%/70% over all 84) | confirmed | low |
| 15 | "Pipa credits König (1994)" for the name | Pipa cites König for the *procedure*, not the name | overstated | low |
| 16 | Amarasingham 2015 "is the same point" | related, not the same point | loose | low |
| 17 | "`mouse_folds` exists" | on the screen branch only | confirmed on branch | low |
| 18 | rigid_shift "only candidate surviving contiguously to 1.6 s on fast" | confirmed; **every fast result carries `void=True`** | confirmed, caveat | low |

**Confirmed without qualification** (recomputed): the leak table's eighteen rows, floors, share and
AUC ranges and the AUC identity · 84 recordings, 44 mice, 42 dates, **no date with more than one group,
no mouse on more than one date** · the per-ROI rate table · cossart's nine frame intervals and
`int(3.1999999999999886/0.1) = 31` — and on real onsets **36% of 264,158 land one frame below the
rounded frame** · the 20-seed fast control (flag_rate 0.05, mean 0.49482, only seed 0 flagged) · 126 of
248 and 126 of 126 · all power figures · seven of twelve unpowered · `correction_reach(13,100,99)`
band_reaches False · `surrogate_discriminator.py` has **zero** matches for "unchanged" · tube's 1,149
parameters and mean pooling · all four `lit_needed.md` entries now present · every literature quote
checked against the shelf.

---

## Round 3 — blind hostile pass on revision 3

`murderboard-reviewer-2`, fresh instance. **GRANT 4 MISMATCH — missing Grep, Glob; held Read, Bash.**

### Bottom line

> **The proposal has argued itself out of its experiment without saying so.** What the swap uniquely
> buys is avoiding the splice and edge-loss leaks of within-recording shifting — which the run folder
> measures at per-ROI accuracy 0.495-0.524 for `rigid_shift` on fast and up to 0.633 for
> `circular_shift` on slow. What it costs is every between-preparation difference — slice, day,
> silent-ROI composition — which the document itself calls the largest objection. **No gate tests that
> trade before compute**, the one element that could separate coordination from preparation identity
> (the within-recording anchor) is `circular_shift` with a measured leak and would make the swap
> unnecessary if it worked, and **the two "free" stages cannot kill the design because the cohort's
> structure fixes their outcomes.**

### Fatal as written

**F1 — the swap grid cannot be built on this cohort.** "Each swapped ROI from a different donor
recording" plus "donors only from the target's own fold", with median N = 31.5 ROIs (range 9-61) and
30 of 44 mice contributing two recordings, 9 one, 5 three. Simulated with 5 mouse folds over 50 seeds,
targets (of 84) with sufficient donors:

| k/N | global pool | within-group pool |
|---|---|---|
| 0.25 | 82.8 | 9.3 |
| 0.5 | 39.1 | 0.9 |
| 0.75 | 14.3 | 0.2 |
| 1.0 | 3.7 | 0.0 |

Within-mouse/within-session allow k ≤ 2. The within-group chimera cannot be built at all, and
high-k/N targets are the small-N recordings, so dose is confounded with recording size.

**F2 — the dispersion stage cannot reach STOP**, so its GO carries no information: the tight levels
it needs to separate can swap only one or two ROIs; no swap fraction is specified; the comparison is
unpaired against a population band wide enough (per-recording silent share 0 to 0.917 on fast) that a
chimera turning a 4%-silent recording into a 36%-silent one still lands inside it; and "TOST inside a
percentile band" is not a defined test.

**F3 — the construction-validity stage cannot kill the design either.** Its only STOP is a builder
assertion followed by "fix and re-run" — a repair loop. Its own predicted outcome, discriminator above
chance, has no declared consequence.

**F4 — the "zero-leak anchor" is not zero-leak.** It is the large-lag limit of `circular_shift`, whose
per-ROI accuracy on `steps_excluded` is 0.562 fast (P = 0.005) and 0.633 slow (P = 0.005, not voided),
with interval-extreme features — the splice the proposal itself criticises. And "bath, drift, depth and
rate scale identical by construction" contradicts the document's own measured within-window drift.

**F5 — if the anchor worked, it would replace the swap**, and the document never says so. `rigid_shift`
keeps slice identity and passes the document's own construction-validity threshold (mouse-level MDA
0.684) by a wide margin; the case against it was never measured against those numbers.

**F6 — the planted-artifact control plants coordination.** A whole-field step in binary onset space is
a volley of most cells firing together — the object a coordination detector exists to find. Planted
into held-out *real* windows it cannot move accuracy even if it is what was learned; and on
`steps_excluded`, where steps were removed, it passes trivially.

### Serious

**S1** — the replacement regression inherits the flaw it replaced: any leak that does not move the
four first-order statistics lands in the intercept, and dispersion distance is collinear with dose.
**S2** — "inherits this exactly" is false and the untouched share is itself a leak: silent share by
group (fast, median per recording) is DI 0.037, MALE 0.225, OVX 0.527, ORX 0.656, and `frac_active` is
already a pooled feature. **S3** — the mouse-level binomial throws power away (design effect 1.81 gives
effective n ≈ 921 and MDA ≈ 0.542, not 0.684), and "powered: False" on the positive controls is a
prospective sizing flag, not a failure to detect. **S4** — the day confound applies to the core design,
not only the side quest: 40 of 42 dates carry one mouse. **S5** — the side quest's verdict is argued on
the wrong grounds: group nested in day is group nested in mouse, true of any between-animal design;
what folds cannot fix is **group aligned with calendar era** (DI-only months 2024-09, 2025-07, 2026-03,
2026-06), and a *negative* group result would still be interpretable. **S6** — "whether groups differ at
baseline is open" contradicts the data: silent-ROI share differs about 18-fold between DI and ORX
medians. **S7** — the two temporal statistics called "required" have no gate, and coincidence count is
the coordination signal itself. **S8** — nothing in the plan tests Amarasingham's slow common-fluctuation
warning.

### Moderate

**M1** — the rate-matched arm's rationale is numerically empty: at p ≈ 0.001 per frame the Σpᵢ² term
is 0.1-0.2% of the variance. **M2** — "every gate names a statistic, a threshold and a unit" is false:
seven margins and criteria are left undeclared, which undercuts the pre-registration argument.
**M3** — "no compute, minutes" hides new code (builder, fold wrapper, TOST, mouse-level test, two
temporal statistics). **M4** — duration figures are from analysis windows, not the approved export's
baseline periods.

### Strongest reason not to approve even the free stages

> Their outcomes are fixed by the cohort's structure, not by the data. They would produce a "two gates
> passed" record that reads as validation and becomes the justification for the compute stage — a
> check that cannot fail, and passes. Approve only a revision that carries the donor-feasibility table,
> paired gates, declared margins, and the within-recording-nulls-versus-swap leak/destruction
> comparison.
