<!-- murderboard run record — process vendored from syncytium2/murderboard @ 8bf89e5 -->
# Murderboard run — docs/learned/assembly_summary.html (+ companion assembly_report.html)
- upstream:  syncytium2/murderboard @ 8bf89e5
- vendored:  d388811e7cf1cfad8d8fa6bb11e0feb91da060d6 (docs/doc_review_process.md, re-vendored to 8bf89e5 during this run)
- freshness: current — **but it was STALE at call-up and this run stopped to fix it**
- artifact:  docs/learned/assembly_summary.html (a5f19f4 -> d7b0f8deba16899762513cadd0cdc3c76f21bf9c)
             docs/learned/assembly_report.html  (439a215 -> 21cdd037f82b42bc456fcecfd9064e9f09a278e0)
             docs/learned/assembly_closed.png   (33cbd50 -> d4a5aeaec011a48d7e225737a4d69f328c4261ed)
- roles:     11 of 11 run
- rounds:    3 (stopping reason: **severity floor reached** — round 3 blind produced no blocking and no major)

## Two deviations from the process, stated rather than hidden

**1. The freshness gate fired, and this run stopped for it.** The vendored murderboard was at
57445b4 against upstream 8bf89e5. Upstream had replaced *"iterate until a blind pass produces
no new findings"* — a rule that does not terminate — with **stop on severity, cap at 3 rounds,
report findings-by-severity per round**. All five vendored files were refreshed and landed
before the review ran, including `.claude/hooks/require-commit-before-message.sh`, which was
stamped 783501e — two versions behind and unnoticed. This run then followed the new rule.

**2. Roles were run single-pass, not as parallel subagents.** The process prescribes parallel
subagents for a substantial deliverable. This session carries a standing instruction not to
spawn agents unless asked, so all 11 roles were walked in turn by the main thread instead.
**This is a weaker mode for a deliverable of this size** — no independent reviewer, and the
blind passes were blind only in discipline, not in construction. The findings below are real
and were verified against sources, but a reader should discount the *independence* of the
review accordingly. ⚠

## Findings by severity, per round

| round | blocking | major | minor | note |
|---|---|---|---|---|
| 1 — initial | 1 | 4 | 2 | full 11-role pass on the first build |
| 2 — blind, new render | 0 | 1 | 0 | axis units on the rebuilt figure |
| 3 — blind, new render | 0 | 0 | 3 | recorded as residual, not fixed |

Blocking went 1 -> 0 -> 0 and major 4 -> 1 -> 0: converged, and stopped by the severity floor
rather than the round cap.

## Role ledger

| # | role | findings | what was checked |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | **1 blocking, 3 major** | Every quantity recomputed from source, not eyeballed — see the claim ledger below. |
| 2 | Citation & reference validator — "DOI or Die." | 0 new | Eight references carried unchanged from the 2026-08-18 report, which validated them; the Colwell & Winkler 1984 chapter remains flagged `⚠` as cited at one remove. No new citation was added by this revision, so none was introduced unverified. |
| 3 | Consistency auditor — "Cross-Examiner." | 1 major | Summary and report cross-checked on every shared quantity (47/49, 38/40, 22/28, 22/26, 5.3%, 6.6%, 2/83, 1/79, p values) — all agree after fixes. Summary originally quoted one false-positive rate beside a two-stream result. |
| 4 | Adversarial reviewer — "Reviewer 2." | **1 blocking** | The "can the alarm ring?" check is the spine of this deliverable and passes: the test's size is measured, not assumed. But the *negative* half rests on a modularity result that covers only one stream — see B1. |
| 5 | Line editor — "Kill Your Darlings." | 0 | Read for undefined jargon and one-assertion-per-sentence. "Penumbra", "curveball", "margins", "core–periphery", "recruitment" are each defined at first use. |
| 6 | Methods / domain expert — "RTFM." | 1 minor | Exact binomial McNemar (not the chi-square approximation) is correct at these discordant counts. Curveball and the Bonferroni-within-null rule are used as `bugarach.assembly` defines them. Checked whether the combined sign test double-counts preparations — it does not. |
| 7 | Reuse auditor — "Reinventing the Wheel." | 0 | The new figure imports `membership` and `panel` from `make_membership_example` rather than redrawing matrices; `assembly_power.py` imports the statistics, both nulls and `AssemblyResult` from the package rather than copying them, which is what makes the power curve describe the shipped instrument. `_binom_two_sided` is hand-rolled deliberately — this repo does not depend on SciPy. |
| 8 | Naive-reader accessibility — "You Lost Me." | 0 blocking | Both documents open on the answer, define ROI/cell, stream, event and null before using them. No section introduces three or more undefined terms. |
| 9 | Density & figure-first — "Show, Don't Tell." | 1 minor | The summary is one page carrying the figure; the report is deliberately prose-dense because it is the reference document, and its one figure carries the three claims that need showing. No prose block was found that should have been a picture instead. |
| 10 | Build & craft gate — "Ship It." | 1 major, 2 minor | Table below, against the **rebuilt** render each round. |
| 11 | Argument order — "Start With the Problem." | 0 | This revision *is* an argument-order fix: the answer now leads, the two objections that decide it come next, the withdrawals follow, the caveats last. Verified the summary and report open on the same sentence. |

### Role 10 table — checked against `docs/learned/assembly_closed.png` (round 3 render)

| panel | axes named + units | lettered | every mark identified | overlap / run-off | verdict |
|---|---|---|---|---|---|
| A · real | yes — "cells, ordered by participation (1–34)" | A | filled vs empty tile, ordered columns | none | pass |
| A · control | yes, same axis | A | same grammar, distinct colour | none | pass |
| B · power | yes — fraction (0–1) both axes | B | 5 curves in legend; guide line labelled on-figure | none | pass |
| C · crosstalk | yes — counts; categories named | C | 3 named categories, ordered original → subtracted → lost | none | pass |

## The claim ledger (role 1)

| quantity | quoted | source | recomputed | verdict |
|---|---|---|---|---|
| testable fast / slow at K=3 | 49 / 40 | `assessment_real.json` | 49 / 40 | match |
| fires, fast / slow | 47/49, 38/40 | same | 47/49, 38/40 | match |
| size of test, fast | 5.3% (3.1–8.9) | `power_fast/assembly_power.json` | 13/244 = 0.0533 | match |
| size of test, slow | 6.6% (3.9–11.0) | `power_slow/...` | 13/197 = 0.0660 | match |
| 4-cell at 1 in 4, fast | 0.90 | same | 0.90 | match |
| crosstalk pairs, fast / slow | 28 / 26 | `pensub_cmp_*_k3.json` | 28 / 26 | match |
| fires after subtraction | 22 / 22 | same | 22 / 22 | match |
| McNemar fast / slow | 0.031 / 0.125 | same | 0.0312 / 0.125 | match |
| combined sign test | p ≈ 0.002 | 10 discordant, one direction | 2·0.5^10 = 0.00195 | match |
| discordant are distinct recordings | 10 distinct | both JSONs | intersection empty, 10 distinct dates | match |
| events retained by pensub | 65% fast, 58% slow | both stores | 110597/171264 = 64.6%; 57302/98904 = 57.9% | match |
| clusters/min, fast | 0.35 → 0.05 | run logs | 0.35 → 0.05 | match |
| firing rate at K=4/6/8 | ">85%" | run logs | fast 89/88/93%, slow 91/93/100% | match |
| recordings in each store | 85 | store listing | 85 `.mat` each (3 CSVs made it look like 88) | **corrected** |
| **modularity, unsubtracted** | **3%** | connectivity handoff | **2 of 83 = 2.4%** | **MISMATCH — fixed** |
| **modularity, pensub** | **1%** | connectivity handoff | **1 of 79 = 1.3%** | **imprecise — fixed** |
| **modularity stream** | **unstated** | `eval_modularity_null_slow.csv` | **slow only; no fast file exists** | **MISMATCH — fixed** |

## Findings and adjudications

**B1 · BLOCKING · the negative covered only one stream (role 1, role 4).** The headline table
presented graph modularity without naming its stream and paired it with a two-stream membership
result. Only `eval_modularity_null_slow.csv` exists — there is **no fast modularity
measurement anywhere in the connectivity project's output**. So for the fast stream the
report asserted an absence nothing had looked for, which is precisely the failure the
"can the alarm ring?" rule exists to catch, inverted: not a test without power, but a
conclusion without a test. FOUNDATIONS §9 forbids it in terms.
**Fixed** — the table gained a stream column, and both documents now state that the slow
stream has both halves of the answer and the fast stream has only the positive half, with the
fast-stream assembly question recorded as **untested rather than settled**.

**M1 · MAJOR · "3% of ROI recordings" was wrong twice (role 1).** Recomputed from the CSV it is
**2 of 83 = 2.4%**; the handoff rounds it to 3%. And "ROI" there names the *unsubtracted
dataset*, not a kind of recording — the report had read a dataset label as a unit of analysis.
**Fixed**, and both documents now cite the CSV rather than the handoff, with the rounding
disagreement stated.

**M2 · MAJOR · the penumbra-subtracted modularity figure was a bare "1%" (role 1).** Recomputed:
**1 of 79 = 1.3%**. **Fixed.**

**M3 · MAJOR · the summary quoted one false-positive rate for a two-stream result (role 3).**
5.3% is the fast figure; slow is 6.6%. **Fixed** — both are named.

**M4 · MAJOR · the figure's guide line was unexplained (role 10).** An unlabelled dotted line
carrying the claim that the curves start at the size of the test. **Fixed** — labelled
on-figure and in both captions.

**M5 · MAJOR · panel B's axis was a fraction labelled as a count (role 10, round 2).**
**Fixed** — "fraction of recordings where the test fires".

**m1 · minor · the combined sign test needed its unit stated (role 6).** Ten discordant
recordings across two streams could read as one preparation counted twice. Verified they are
ten distinct recordings on ten distinct dates, none discordant in both streams. **Fixed** by
stating it.

**m2 · minor · the store count (role 1).** Both stores hold 85 `.mat` recordings; the
directory listing shows 88 entries because three are CSVs. **Fixed** in the report's
reproduction caveat and on the session board.

## Residual ⚠ — for the human, not fixed

1. **The fast stream's assembly negative is untested**, not established. Closing it needs
   modularity run on the fast stream. This is the one open item that limits the headline.
2. **Core–periphery is an interpretation, not a fitted model.** Nothing here fits it or tests
   it against alternatives.
3. **Penumbra subtraction is itself a model** — a surviving departure is evidence its estimate
   was incomplete as much as evidence the coordination is real.
4. **Modularity handles overlapping groups badly**, so overlapping assemblies could evade it
   even in the slow stream.
5. **The fast/slow kinetic boundary is undefined** in every document in this project.
6. **The review was single-pass, not independent** — see deviation 2 above.
7. **Minors surviving round 3, recorded rather than fixed** (per the process's stopping rule):
   panel A's two matrices share the letter "A" rather than being A1/A2; panel A illustrates a
   fast-stream recording only; panel C shares one y-axis between two "fires" counts and a
   "lost testability" count.

---


# Round 4 — the fast-stream modularity run, reviewed

Appended 2026-08-19, after the deliverable changed materially: the open item this record
named as residual #1 ("the fast stream's assembly negative is untested") was closed by
running the instrument, and both documents were rewritten around the result.

- upstream:  syncytium2/murderboard @ 729fb06
- vendored:  77b70dc620a8bcccfc72fce2fd316d38da34c204 — **re-vendored again during this round**
- freshness: current
- artifact:  docs/learned/assembly_report.html   (a8662c6024b4efdf0b967a6139420c2964f0e6ad)
             docs/learned/assembly_summary.html  (74c3be49f11bfd5928f3ad77aebf66b4ca4f9f69)
             docs/learned/assembly_modularity.png (d5f6ac81b82bda31ea65c86f64e1fe32d5dbed40)
             docs/learned/assembly_closed.png     (62a6e1354356e4ffcb7afd9356298839a7462495)
- roles:     11 of 11 re-run (single-pass, same deviation as rounds 1–3)
- stopping:  **severity floor** — the last blind pass produced no blocking and no major

## The gate fired again, and it paid for itself twice

At call-up the vendored process was **8bf89e5 against upstream 729fb06**. The two commits in
between are the murderboard PRs this project's own handoff had listed as *open, waiting on a
person* — and both landed rules that immediately found defects here:

- **"The sources a deliverable did NOT consult are part of the check."** Applied, it found the
  blocking item below within minutes. Without it, roles keep verifying claims against the
  sources a document *names*, which is how the previous three rounds passed.
- **"Name the chart type the image RESEMBLES before reading its axis labels."** Applied to the
  new modularity figure, it identified the strip panel as reading like a **spike raster** —
  the same idiom that already cost this project one figure.

## Findings by severity, this round

| round | blocking | major | minor | note |
|---|---|---|---|---|
| 4a — initial, on the new result | 1 | 4 | 2 | includes the lab-exclusion blocker |
| 4b — blind, rebuilt render | 0 | 2 | 1 | figure defects only |
| 4c — blind, rebuilt render | 0 | 0 | 2 | recorded as residual |

## Findings and adjudications

**B2 · BLOCKING · every number was computed over recordings the lab had withdrawn (role 1).**
`indiegroups_db4.xlsx`, sheet `indiegroups`, column **`exclude`**, marks six (date, mouse)
rows unusable. Two recordings in the store — `20250731_149` and `20250731_151`, "6 minute ttx
treatment, too short" — fall on one of them, and were inside the membership tallies, both
modularity runs, the crosstalk pairing **and the geometry the power curve was computed at**.
One of them was one of the ten discordant recordings the crosstalk claim rested on. No part of
this analysis had ever opened that workbook.
**Fixed** — `tools/lab_excluded.py` derives the list from the workbook,
`bugarach.assembly.load_excluded` reads it, and the power, crosstalk and modularity tools all
take `--exclude-file`. Three tests lock it, including that a withdrawn recording is dropped
*before* pairing. Every conclusion survived; the counts moved. Filed as
`docs/todo/2026-08-19-lab-exclusions-were-never-consulted.md`, because the assembly work is
only where it was noticed — every deliverable in this repo that counts recordings takes the
store as its universe.

**M6 · MAJOR · the modularity denominator counted untested recordings as negatives (role 1).**
`above_null_Q` is `Q_obs > q_hi`, and a recording too sparse for Louvain to score has no
`Q_obs` — so the comparison is false and it entered the CSV as a `0`, reading as "tested, not
modular". One fast and four slow recordings, all with 3–5 active cells. This is the same
**undefined is not negative** rule the report applies to its own membership test.
**Fixed** — excluded and reported; the published handoff's "ROI 3%" becomes 2 of 77.

**M7 · MAJOR · the roster underneath the published slow result is quarantined (role 6).**
`if2_dead_roi_keep` hardcodes `2R/2026-07-13/`, which the R team moved to `2R/QUARANTINE/`
("plausible WRONG answers"), so the pipeline could not run without restoring a known-bad
input. Successor chain: 2026-08-10 (also superseded — zero high K+ rows, disabling the
safeguard that rescues 176 ROIs) then 2026-08-15.
**Fixed for this run** — an additive `IF2_DROI_CSV` override, default untouched, and slow
re-run on the current roster as a check. It changed **nothing**: same 83 recordings, same
active-cell counts, same verdict on every one. A check that could have failed and did not.
Repointing the default is the connectivity project's call and is offered, not taken. ⚠

**M8 · MAJOR · the strip panel read as a spike raster (role 10, new rule).** Two rows of marks
on a horizontal axis, in a field where that means time-by-cell.
**Fixed** — a per-row median diamond, which no raster carries.

**M9 · MAJOR · the median marker was the same colour as its dots (role 10, round 4b).**
Present and unreadable. **Fixed** — white fill, thick stream-coloured edge.

**M10 · MAJOR · panel B invented a phantom category (role 10, round 4b).** A text annotation
placed at a numeric x on a categorical axis added a "0.5" tick and shifted the bars; the
per-bar colours also collapsed to one. **Fixed** — guide named in the axis label, explicit
categorical colour mapping.

**m3 · minor · the strip was coloured by the sign of z, not by the test's verdict (role 1).**
About fifteen marks were highlighted against a stated count of three, because the threshold is
the 95th percentile and not zero. **Fixed** — coloured by `above_null_Q`.

**m4 · minor · the slow stream's size of test is elevated (role 4).** 17 of 187 = **9.1%**,
interval 5.8–14.1, which does not cover the nominal 5%; an earlier run of the same design gave
6.6%. **Adjudicated: stated, not fixed.** Both estimates are reported, the slow negative is
described as the less precise of the two, and the direction is unaffected — 36 of 38 against a
null of at most 14%.

**m5 · minor · the fast McNemar crossed 0.05 (role 3).** Dropping the withdrawn recording took
the fast crosstalk attenuation from p = 0.031 to **0.063**. **Stated** — neither stream reaches
significance alone now, and both documents say so; the claim rests on the combined
nine-recording sign test (p = 0.004) and the consistency of its direction.

## Residual — updated

Residual #1 from rounds 1–3 (**"the fast stream's assembly negative is untested"**) is
**CLOSED**: 3 of 78 fast recordings above null, 3.8%, against ~5% by chance. The rest stand,
with these changes:

1. ~~The fast stream is untested~~ — **closed this round.**
2. **Modularity cannot see overlapping groups**, in either stream. Now the main route by which
   the negative could still be wrong. ⚠
3. **The penumbra-subtracted modularity run covers slow only** (1 of 69 above null). ⚠
4. **Core–periphery is an interpretation, not a fitted model.** ⚠
5. **Penumbra subtraction is itself a model.** ⚠
6. **The slow stream's test may be anti-conservative at its own geometry.** ⚠
7. **Whether the lab's exclusion should bite at all** — its reason concerns a treatment period
   and this analysis is baseline-only. Tony's call; both readings recorded. ⚠
8. **The exclusion match is by date, not slice**, because the workbook carries no slice id. ⚠
9. **The fast/slow kinetic boundary is undefined** in every document in this project. ⚠
10. **The review remains single-pass, not independent.** ⚠

---

# Round 5 — the modularity instrument moved into this repo

Appended 2026-08-19. The deliverable changed again: the modularity half of the answer is no
longer computed by an unmaintained MATLAB pipeline, and both documents were rewritten around
the in-repo instrument.

- upstream:  syncytium2/murderboard @ 729fb06
- vendored:  77b70dc620a8bcccfc72fce2fd316d38da34c204
- freshness: current
- artifact:  docs/learned/assembly_report.html   (b1e47a5a428fef922af450fb0adec8cfc7949190)
             docs/learned/assembly_summary.html  (8341adc76fa3e695257f639c7f6345e9218d0884)
             docs/learned/assembly_modularity.png (5dc753a4b7401b71429e1d13f8dc90ed12e137a3)
- roles:     11 of 11 re-run (single-pass, same deviation as earlier rounds)
- stopping:  **severity floor** — the last blind pass produced no blocking and no major

## Findings by severity, this round

| round | blocking | major | minor | note |
|---|---|---|---|---|
| 5a — initial, on the ported result | 0 | 3 | 1 | two were defects in my own new code |
| 5b — blind, rebuilt render | 0 | 1 | 1 | the attribution error below |
| 5c — blind, rebuilt render | 0 | 0 | 1 | recorded as residual |

## Findings and adjudications

**M11 · MAJOR · the port analysed cells the producer had rejected (role 1, new rule).**
Applying *"the sources a deliverable did NOT consult are part of the check"* to my own work:
the MATLAB applies the R team's dead-ROI roster before computing and `tools/modularity_null.py`
did not. The signature was unmistakable — `n_active` higher on 10 recordings and **never
lower**. **Fixed** — the roster's verdicts are vendored to
`docs/learned/dead_roi_verdicts.csv` and consumed by the tool (consumed, not recomputed: the
rule needs drug and high-K rows FOUNDATIONS §9 keeps out of this repo's reach).

**M12 · MAJOR · I then blamed the wrong thing, and checking caught it (role 1, round 5b).**
Having found the roster gap I attributed the `n_active` difference to it. Applying the roster
changed **nothing** — every count identical. The reason is structural: the rejection rule is
`base_empty AND drug_empty AND hik_empty`, so a rejected cell is silent in baseline by
definition, and this measurement already drops cells with no events. Verified: **all 66
rejected ROIs have zero baseline events.** The real cause is the window — bugarach scores
1740–1800 s where interface2 caps at 1200 s, so more cells clear "at least one event", which
is exactly *higher, never lower*. **Fixed** — the report now names the window, states the
roster as a demonstrated no-op, and keeps the roster wired because it is the producer's
selection and a future store may not have the same property.

**M13 · MAJOR · a NaN corrupted a median in my own figure tool (role 10).** Three recordings
are scored but have no finite z, because their surrogates had zero spread. They were being
sorted into the strip, and NaN in the sort put the *minimum* where the median belonged —
the figure reported −13.48 against a true −3.45. **Fixed** — the rate's denominator and the
plottable set are now two populations, and the tool reports how many it could not draw.

**m6 · minor · the figure tool's NA check was case-sensitive (role 10).** It tested for
`"NaN"` and the port writes lowercase `nan`, so an untestable recording would have entered
the denominator as a number. **Fixed** — a finite-float check, and the explicit `defined`
column preferred where present.

**m7 · minor · the corpus-level agreement is not re-checked by CI (role 10).** It needs the
store. Only the fixture comparison runs on CI. **Stated, not fixed** — the fixture is what
certifies the coefficient; the corpus run is evidence, recorded here and in the report.

## What this round did NOT find

Role 2 (citations): the two references added — Cutts & Eglen 2014 for the coefficient,
Blondel 2008 and Newman 2004 for the modularity — are real, correctly attributed, and are
the works the methods actually come from. Role 4: the claim "does not depend on which
windowing convention is used" is supported by the 98.7% agreement rather than asserted, and
the two disagreements are named individually. Role 11: the new material sits inside the
existing argument order — instrument, then validation, then result — and does not reopen the
lead.

## Residual — updated

The ten from round 4 stand, with one closed and two added:

- **CLOSED:** ~~the modularity half depends on an unmaintained pipeline~~ — ported, validated
  two ways, and running here.
- **NEW:** the corpus-level agreement is not exercised by CI (m7). ⚠
- **NEW:** the port is a **port, not a clean-room** — the MATLAB driver was read while chasing
  the quarantined roster, so only the coefficient is independently derived. The module says
  so and the fixture only certifies the part that can be certified. ⚠
