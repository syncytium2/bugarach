# Murderboard run — Aim 0 of the synthetic-validation goal

**The problem.** Tony asked whether an analytical prediction could replace brute-force
simulation of the toolset, then asked for two blind replications of that theory, whether
assembled participation converges to random as sources multiply, and how an order indicator
compares with Kreuz's synfire measure. The answers went onto the goal page
([`goals/synthetic-validation.md`](../goals/synthetic-validation.md), *Aim 0*) with four figures,
the scripts and records in [`learned/synthetic_validation/`](../learned/synthetic_validation/README.md),
and new glossary entries. This run murderboarded that work: one review round and three blind
verify rounds, 11 roles each.

- upstream:  syncytium2/murderboard @ 682c31b
- copy:      vendored @ 682c31b (re-vendored for this run, PR #909)
- freshness: current
- artifact:  `docs/goals/synthetic-validation.md` (lines 16 through *Tried and dropped*, and the plan item *Aim 0: predict first, simulate to check*), its four figures, `docs/learned/synthetic_validation/*`, the new `docs/GLOSSARY.md` entries (the revised jitter entry and *Synthetic-validation vocabulary*). Page fingerprint (git hash-object) 68b1cbf5 at the first round, 8a209144 after the follow-up pass.
- roles:     11 of 11 run (inline fallback: general-purpose agents in every round, as no role agent was registered)
- reports:   synthetic-validation-aim0-2026-10-23-round4-roles/ (round 4, blind 3, the last); also synthetic-validation-aim0-2026-10-23-round1-roles/ (round 1, review), -round2-roles/ (blind 1) and -round3-roles/ (blind 2)
- rounds:    4 (1 review + 3 blind verify rounds, the cap)

Mode: standard
Execution: subagents — one per role, all eleven spawned in each round

## Findings by round

Counts are rows the roles themselves rated blocking, or major or high, found by searching the
reports for those labels; they are approximate (roles use different scales, and role 8 rates
whole sections blocking under its rule of three undefined terms).

| round | reports | blocking | major or high | what the blocking findings were | fixed in |
|---|---|---|---|---|---|
| 1, review | `…-round1-roles/` | about 9 | about 31 | an August claim stated as explained; undefined-term sections (role 8) | 905c0eda and before |
| 2, blind 1 | `…-round2-roles/` | about 8 | about 38 | a latency template reads as jitter to the population tools; missing run-record link; undefined-term sections | 905c0eda |
| 3, blind 2 | `…-round3-roles/` | about 1, plus role 8's sections | about 21 | "the assessor cannot measure jitter" refuted by Figure 1 D at 0.01 Hz; undefined-term sections | 320e6963 |
| 4, blind 3 | `…-round4-roles/` | about 10 (1 by role 4, the rest role 8's sections) | about 17 | the "about 3 templates" detection claim was never simulated; undefined-term sections | follow-up pass, this PR |

**Stopping reason:** the round cap. Round 4 still carried a blocking finding (role 4, finding 1)
and majors, so a follow-up pass fixed them without a further blind round:
- **Order detection:** power is now simulated on both sides at 5–25 events (`order_limit.py`,
  `power`), and the lab's 1–8 events per baseline window are taken from `windows.csv`.
- **Lab regime:** the lab's background (0.0096 Hz, so 0.01 Hz is the lab-like arm) and its
  participation (7–12 of 33) are stated beside the jitter gap.
- **Sign test:** done per condition (12 of 16 and 9 of 16).
- **Direct answers:** "Not replace, but aim it" answers Tony's first question; membership
  converges "only at fixed E", and detection outlasts the variance.
- **Figure 1:** the jitter panels are no longer offset sideways, and every observed assessor
  jitter is drawn.
- **Figure 3 B:** the labels no longer collide with the data.
- **Prior art:** moved to the folder README, with the corrected minimum-contrast, Kreuz 2022,
  Cecchini 2021 and Grün, Abeles & Diesmann 2008 attributions and an unsearched replay
  literature.
- **Plan:** rewritten in plain words.

Round 4's role 8 blocking rows (sections with three or more undefined terms) were addressed by
glosses and by moving the citation-dense paragraph off the page. They were not re-verified by a
blind round.

**Calibration.** This review found and fixed the defects in the reports listed above (at least
about 40 rated blocking or major across the four rounds). It is not a correctness proof: every
reviewer was a Claude agent with the same model as the author, no human reviewed it, and the
follow-up pass after round 4 was checked only by its author.

## Role ledger

Every role, every round, returned a GRANT line with **MISMATCH**: spawned as general-purpose
agents, they held editing, shell and messaging tools beyond their grants. Each report states which
tools it used; none edited a tracked file. Scratch lived under `_scratch/` (untracked).

| role | name | grant, as each round's report declared it (the same in rounds 1–4) |
|---|---|---|
| 1 | Prove It | GRANT 1 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent (and others its report lists) |
| 2 | DOI or Die | GRANT 2 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent (and others its report lists) |
| 3 | Cross-Examiner | GRANT 3 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent (and others its report lists) |
| 4 | Reviewer 2 | GRANT 4 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent (and others its report lists) |
| 5 | Kill Your Darlings | GRANT 5 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent (and others its report lists) |
| 6 | RTFM | GRANT 6 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent (and others its report lists) |
| 7 | Reinventing the Wheel | GRANT 7 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent (and others its report lists) |
| 8 | You Lost Me | GRANT 8 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent (and others its report lists) |
| 9 | Show, Don't Tell | GRANT 9 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent (and others its report lists) |
| 10 | Ship It | GRANT 10 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent (and others its report lists) |
| 11 | Start With the Problem | GRANT 11 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent (and others its report lists) |

**Blindness.** Rounds 2–4 were told not to open earlier reports or other scratch. In round 4,
role 5 reported that one search's exclusion pattern failed and returned two lines from round 3
reports; it marked its two findings on those phrases as tainted. Role 7 reported a search that
listed (but did not open) earlier scratch file names.

**Archive edits.** The four folders were renamed from `synthetic-validation-aim0_2026-10-23-…` to hyphen-only names, because `murderboard_roster.sh` strips underscores before resolving a `reports:` path (a tool bug, not fixed here). Reports are verbatim apart from these:
- Round 1: SAP004 punctuation, a slash after "Dropbox" written as a comma.
- Round 2: quote marks in `02-doi-or-die.md` line 34, changed for `check_quotes`.
- Round 3: SAP004 punctuation in the GRANT lines of `02-doi-or-die.md` and `10-ship-it.md`.
- Round 4: the quoted page sentence in `02-doi-or-die.md` line 15 reworded for `check_quotes`; slash-separated tool lists in the GRANT lines of `01-prove-it.md`,
  `03-cross-examiner.md` and `04-reviewer-2.md` written with commas.
- All rounds: the harness's two-space indent removed.

## Residual ⚠

- **Nobody has asked Kreuz (or Mulansky)** whether a fast sort or an analytical null for the
  Synfire Indicator exists, nor the Grün lab about the joint fit (goal page, *Waiting on Tony*).
- **Unsearched literatures:** quadrat-variance ecology, physics counting statistics, composite and
  Palm likelihood for cluster processes, and hippocampal replay and sequence rank-order methods.
- **Unopened sources:** Thomas 1949, Neyman & Scott, Kish 1965, Kruskal 1958, Greiner 1909, the
  Baik papers, Grün's 1996 thesis and Cecchini 2021. Louis et al. 2010 and Pazienti et al. 2008
  were read as abstracts only.
- **Review agents' numbers not kept in the repository:** the surrogate dependence (about 0.5–1 %
  of the pair count), the PySpike cross-event coincidence tests, the 9 % frame-tie loss, and the
  frame-rounding bias.
- **Declined, with reason:**
  - A residual-panel version of Figure 2 and a g_n schematic (roles 8 and 9). The page states
    the residuals in numbers, and the plan's item 8 re-plots on dimensionless axes.
  - An exact analytic baseline for Figure 3 A (role 6). The caption states the shared-baseline
    error.
  - Making the repo copy of the figures opt-in (role 7). The figures sit beside the goal page.
  - Raising every figure's text to 13–14 pt (role 10).
- **Left as is:** one small text-on-point overlap in Figure 2 F and G. The assessor's Aim 1a run
  used 120 surrogates, not the shipped 1000; the record says so.
