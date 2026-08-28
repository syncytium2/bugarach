# Murderboard run — docs/handoffs/2026-08-28-what-351-changes-under-the-deploy.md

- upstream:  syncytium2/murderboard @ 3593c44
- copy:      vendored @ 3593c44
- freshness: current
- artifact:  `docs/handoffs/2026-08-28-what-351-changes-under-the-deploy.md` (`0894e0e` -> `54ba9cc`)
- roles:     11 of 11 run
- rounds:    2 (stopping reason: **severity floor** — round 2 produced no blocking and no major findings)

## What was at stake, and what the review caught

A coordination handoff is read by exactly one person, once, at the moment they are
about to publish a public page. Everything in it is load-bearing in a way an
explainer is not: a wrong number here is a number somebody acts on and cannot
easily check, because the whole reason they are reading it is that they did not do
the work.

The review caught two things that would have been acted on.

**A test count that was simply wrong — and had already shipped.** The draft said
the suite passes at 1,442. Recomputing rather than eyeballing (role 1's rule, in
the terms it uses) gave **1,485 passed, 16 skipped, 1 xfailed** at `1b82160`. The
1,442 was not a stale figure, it was never right: the run behind it reported *1
failed, 1421 passed, 15 skipped*. It had already gone into PR #351's body and its
commit message, where a later reader would take it at face value. The corrected
handoff now carries an explicit retraction section, because the wrong number is in
merged history and history is not being rewritten to remove it.

**An overclaim about the fix's own effectiveness.** The draft said the yield swap
removed the background-throttling penalty. What is measured is narrower: the
*timer*-yield count went to zero, so the *timer* clamp no longer applies. Whether
Chrome throttles `MessageChannel` tasks in a hidden tab by some other route was
never measured — and could not be, because Chromium under automation refuses to
throttle three different ways. Role 4's "can the alarm ring?" discipline is what
turns that from a passing claim into a residual `⚠`: the check that would have
caught a remaining penalty does not exist, so the absence of one is silence, not
evidence. The handoff now says so and names the ten-second experiment on the live
page that would settle it.

Both are the same species — a claim that reads as verified because a number is
attached to it — and both were invisible to every check that only asks whether
the prose is coherent.

## What would validate this, and how it generalises

The handoff's own residual `⚠` is the validation step: start a locust sweep on the
deployed page in an ordinary browser, switch tabs for a minute, come back. That
one observation retires the unmeasured half of the claim.

More generally: **this run's two real findings were both quantitative, and both
came from recomputing rather than reading.** The doc's prose was internally
consistent in both places — that is precisely why consistency checking could not
find them. Where a handoff quotes a number produced by a run, the number has to be
re-derived from the tree at writing time, not carried forward from the message
that first reported it.

## Method note, stated rather than hidden

This was a **single-pass self-review walking all eleven role checklists in turn**,
not the parallel subagent fan-out the process prescribes for a substantial
deliverable. This session is configured not to spawn subagents. The process's
carve-out — that role 2 must run as a separate agent whenever a deliverable
attributes a method or claims novelty — **does not fire here**: the handoff
attributes nothing and claims nothing as novel; its one attribution-adjacent
sentence reports that a *CICADA attribution fix* is already live, which is a fact
about a deploy, not an attribution. Recorded so a reader can weigh the coverage
rather than assume it.

## Appendix — role ledger

| # | role | findings | note |
| --- | --- | --- | --- |
| 1 | Claim & data verifier — "Prove It." | 4 | the 1,442 error (blocking); "two of seventeen yields in the sweep" wrong, actually four; Chrome clamp figures unverifiable in-session, flagged ⚠; every sha, count and path re-derived from the tree — see claim ledger below |
| 2 | Citation & reference validator — "DOI or Die." | 0 | nothing to check: the artifact cites no literature and attributes no method. Its only external references are Chrome and Playwright behaviours, handled by roles 1 and 6. The separate-agent carve-out does not fire (see method note) |
| 3 | Consistency auditor — "Cross-Examiner." | 2 | tree sha `7a0c221` already stale at review time → restated as "when written" plus an instruction to re-run the staleness tool; checked the doc against `DEPLOY_HOLD.md` for contradiction — none, the two answer different questions; no banned glossary term ("modality") present |
| 4 | Adversarial reviewer — "Reviewer 2." | 3 | the MessageChannel overclaim (major, → ⚠); "nothing a reader sees is different" was false for a password-manager user; the "no tool registers a dialog handler" null result had no stated power — now says how it was grepped and shows the same grep firing on a script that has one |
| 5 | Line editor — "Kill Your Darlings." | 2 | "the riskiest line in it" promoted from a buried aside to the cold open; provenance boilerplate moved off the top |
| 6 | Methods / domain expert — "RTFM." | 1 | the `MessageChannel`-vs-timer distinction is correct as to *timer* clamping and does not license the broader claim; co-filed with role 4, fixed once |
| 7 | Reuse auditor — "Reinventing the Wheel." | 0 | nothing to check: the artifact is prose. The code it describes introduces two helpers (`yieldToUI`, `noAutofill`); confirmed the page had no prior equivalent of either, so neither duplicates existing project code |
| 8 | Naive-reader accessibility — "You Lost Me." | 2 | "armed" used before definition → defined at first use; "locust" undefined for a cold session → glossed at first mention rather than in a trailing footnote |
| 9 | Density & figure-first — "Show, Don't Tell." | 1 | the throttling numbers were a prose paragraph doing a table's job → replaced with a three-row table (sweep · yields · in front · at clamp · after 5 min hidden). No other section warrants a figure: the artifact is a checklist for one reader, not an argument needing illustration |
| 10 | Build & craft gate — "Ship It." | 0 | Markdown, no render. Table run instead: all 5 relative links resolve from `docs/handoffs/` (the dead-link trap this directory's README documents); all 5 shas exist in the tree; both fingerprints recorded; file re-checked after the last edit |
| 11 | Argument order — "Start With the Problem." | 1 | the draft opened on provenance and a quote, reaching what actually changes in paragraph four → restructured so the first sentence is the change and the risk, with the mandate and the hold relationship after it |

### Claim ledger (role 1)

| quoted | source | recomputed | verdict |
| --- | --- | --- | --- |
| suite "1,442" | PR #351 body | 1,485 passed / 16 skipped / 1 xfailed at `1b82160` | **mismatch — corrected, and retracted in-doc** |
| "two of seventeen yields in the sweep" | draft | 2 in `sweepDetector` + 2 in `runTune` = 4 of 17 | **mismatch — corrected** |
| 17 yield sites | `grep -c "await yieldToUI();"` | 17 | match |
| 50 inputs stamped | `grep -c '<input '` | 50 | match |
| 4 runtime inputs wrapped | `grep -c 'noAutofill(document.createElement("input"))'` | 4 | match |
| LoCo 20 settings: 25 yields, 10.1 s | instrumented run 2026-08-27 | 25 / 10.1 s | match |
| 25 → 0 timer yields after the swap | instrumented run | 0 | match |
| three viewer commits pending | `git log 0ed939d..origin/main -- docs/site/raster_viewer.html` | `f7c0edb`, `173accd`, `53b1d62` | match |
| live at `0ed939d`, version `acac81b2` | deploy record, PR #346 | same | match |
| no dialog handler in `tools/`, `tests/` | broadened grep, power-checked | 0 hits; same grep finds 2 in a script that has one | match |
| Chrome clamp ≥1 s, ≥1/min after ~5 min | Chrome documented behaviour | not re-verified in-session | **unverifiable here — flagged ⚠** |

### Residual ⚠ the human must weigh

1. **Chrome's clamp figures** are quoted from documented behaviour and were not
   re-verified against Chrome's documentation in this session.
2. **`MessageChannel` throttling in a hidden tab is unmeasured.** The swap
   provably removes the timer clamp; it is not proven to remove all background
   penalty. The handoff names the experiment that settles it, and that experiment
   is only available once the page is deployed.

## Correction, 2026-08-28 — the gloss this review approved was wrong

The gloss role 8 asked for, and this record signed off, described *locust* as
**"this project's port of the CICADA detector"**. PR #360 merged minutes later and
established the opposite in terms: locust is *derived from the Cossart lab's
CICADA and **is not** CICADA* — it is fed this project's own detected events and
paints each cell active for the rise interval where the original paints the whole
transient. Saying locust IS CICADA's method beside this project's benchmark
numbers is the precise defect #360 removed from the public front page, because a
reader who joins that to locust's 85 firings on the decoy block concludes CICADA
is promiscuous.

**Why the review missed it.** Role 3 checks the artifact against companion docs as
they stand, and `README.md`, `src/bugarach/ui/app.py` and interface2's methods doc
already carried the correct phrasing — four places against one. The review
consulted none of them, because it treated the word as a convenience gloss for a
cold reader rather than as a claim about another lab's work. That is the finding:
**a one-line definition of someone else's tool is an attribution claim and
inherits role 2's zero-tolerance rule**, whatever else the document is about.
Role 8 asked for a gloss; role 2 was never pointed at the gloss it got.

Corrected in the handoff, matching the substance of the comment at
`src/bugarach/ui/app.py:132-139`. No other claim in this record is affected.

## What this run does not warrant

This review found and fixed 16 defects across 11 roles. **It is not a correctness
proof.** The convergence above measures how quickly a reviewer stopped finding
things, not whether anything remains — and this run had a single reviewer walking
eleven checklists, so a blind spot shared across those checklists would not have
been caught by any of them.
