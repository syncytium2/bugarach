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
