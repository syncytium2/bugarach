# Murderboard run — docs/handoffs/2026-08-28-the-gate-is-in-the-app-and-inert.md

## The problem this run was pointed at

A handoff is the one document whose failure mode is *silent*: a fresh session acts on it,
finds the world does not match, and the cost lands on somebody who was not there to argue.
This one carries eight cued items and a booby-trap warning, so every number in it is an
instruction.

**The review earned its place on the first check.** Three of the draft's factual claims were
wrong, and all three were the kind that read as authoritative:

- **The suite count was stale by 29 tests** — `1,507` was measured in a different worktree
  before other sessions' work merged. Recomputed on the tree being handed over: **1,536
  passed, 16 skipped, 1 xfailed**.
- **"`labSpec()` is consumed only by `api.train(...)`" was false.** It has two readers; the
  second, `paintLabWhat()`, displays which fields were carried. The substantive point (it
  never feeds the sweep) survived, the word *only* did not.
- **A failure reported as observed was not observable.** The draft told the next session
  `test_hooks_installed` fails; `core.hooksPath` is set on this machine and it passes. True
  only of a fresh clone, and now says so.

A fourth came from the blind pass and was **introduced by one of the fixes**: the opening
said the job is *"one job in one file"* while a fix eleven lines later told the reader to add
a parity test in a second file. That is the classic repair regression this process exists to
catch — the fix was right and it contradicted the summary nobody re-read.

## What would validate it, and how it generalises

The claims in this handoff are checkable by construction: every one names a file and a line,
or a PR number, or a command. The reproduce commands were **run**, not quoted — the roster
gate below, the link resolution, the sapper pass, and the suite. What is *not* validated is
the one prediction the document makes on purpose and flags as such: that planting the probe
will be roughly F1-neutral. It is labelled a prediction, with the instruction to measure.

The generalisable part: **a status document written from a worktree quotes that worktree's
world.** Two of the three blocking findings were measurements that were true where they were
taken and false where they would be read. A handoff should recompute its state numbers in the
tree it is handed over from, as its last act before delivery.

## What this run does NOT warrant

This review found and fixed 8 defects. **It is not a correctness proof.** The convergence
table measures how quickly reviewers stopped finding things, not whether anything remains.
In particular, roles 2, 6 and 7 had little to bite on in a document that cites no literature
and introduces no method — their clean rows are evidence they ran, not evidence the document
is sound.

---

# Appendix — header, ledger, findings

- upstream:  syncytium2/murderboard @ f62acb3
- copy:      vendored @ f62acb3
- freshness: current (`murderboard_freshness.sh --refresh --verbose` → exit 0)
- artifact:  `docs/handoffs/2026-08-28-the-gate-is-in-the-app-and-inert.md`
  (`7d11f549` → `9bf67828`)
- roles:     11 of 11 run
- rounds:    3 (1 review + 2 blind); stopping reason **severity floor reached**

⚠ **Stated deviation — the roles ran single-pass, not as parallel subagents.** This session
runs under a standing instruction not to spawn agents unasked. Every role ran and each
produced its output; the mechanism differed. This matters most for **role 2**, which the
process says may *not* collapse into single-pass when a deliverable attributes a method —
because a single pass inherits the drafter's search history. Recorded as a residual `⚠`
below rather than presented as satisfied.

## Convergence

| round | blocking | major | minor |
|---|---|---|---|
| 1 · full review, 11 roles | 2 | 3 | 3 |
| 2 · blind on corrected | 0 | 1 | 1 |
| 3 · blind on corrected | 0 | 0 | 2 |

## Role ledger

| # | role | findings |
|---|---|---|
| 1 | Claim & data verifier — "Prove It." | **3** — stale suite count (1,507→1,536); false "only" on `labSpec()`; `test_hooks_installed` reported as observed when it passes here. Claim ledger below. |
| 2 | Citation & reference validator — "DOI or Die." | **0 findings, and here is what I checked.** The document cites no literature. Every reference is internal: 9 PR numbers (all states checked via `gh`), 3 relative links (all resolve), 6 file:line citations (all opened and quoted verbatim). ⚠ Ran single-pass — see deviation above. |
| 3 | Consistency auditor — "Cross-Examiner." | **2** — "one job in one file" contradicted the parity-test instruction (round 2); "the evidence for step 1" pointed at the numbered list when it meant the unnumbered section above it (round 3). |
| 4 | Adversarial reviewer — "Reviewer 2." | **2** — "nothing upstream of it exists" overstated (the generator exists; the hot block does not); no rationale given for putting the probe ahead of RESET §7's Tony-owned steps. Both fixed. Checked "can the alarm ring?" on the draft's own null claim — *the gate always passes* — and the draft names the mechanism (undefined input), so it is a mechanism statement, not an untested absence. |
| 5 | Line editor — "Kill Your Darlings." | **1** — "and that surprised both of us" reads as private shorthand in a document for a stranger; replaced with the quote and what was actually unchecked. |
| 6 | Methods / domain expert — "RTFM." | **1** — the `simulate.py:693` citation did not contain the behaviour claimed of it: line 693 builds `excl`; the compression is at `:318-326` and the restore at `:363`. Now cited where the behaviour lives, which is also the part being ported. |
| 7 | Reuse auditor — "Reinventing the Wheel." | **1** — the document instructs a port of `simulate.py`'s hot block into JS without naming it as deliberate duplication. Added, with the constraint that forces it (`test_site_viewer.py` bans `fetch(`/`<script src`/`import(`) and the existing `test_webapp_*_parity.py` pattern as the answer. |
| 8 | Naive-reader accessibility — "You Lost Me." | **1** — "promiscuity probe" was used throughout and never defined; a fresh session is exactly the cold reader here. Defined in the opening. Per-section verdict below. |
| 9 | Density & figure-first — "Show, Don't Tell." | **0 findings, and here is what I checked.** Nothing in this handoff is visual — it is state, citations and instructions; there is no distribution, trace or comparison that a figure would carry better. The one structural payload (what is built vs what is missing) is already a table rather than prose. Thresholds are slide conventions and were not applied to a prose handoff; stated rather than silently skipped. |
| 10 | Build & craft gate — "Ship It." | **0 defects.** Table below, checked against the rendered file at each hash. |
| 11 | Argument order — "Start With the Problem." | **1 (major)** — the draft opened with filing metadata ("not at the root, on purpose") before the reader knew what the problem was. Reordered: the state of play leads, the filing note demoted to a block quote. |

### Role 1 — claim ledger

| quoted | source | recomputed | verdict |
|---|---|---|---|
| suite 1,507 passed | `pytest tests/` | **1,536 passed, 16 skipped, 1 xfailed** | **mismatch → fixed** |
| `labSpec()` consumed only by `api.train` | `raster_viewer.html` | 2 readers (`:9871` display, `:9934` train) | **mismatch → fixed** |
| `test_hooks_installed` fails | `pytest` + `git config` | `core.hooksPath=.githooks`, **2 passed** | **mismatch → fixed** |
| #375/#377/#378/#381/#383/#387 landed | `gh pr view` | all **MERGED** | match |
| #292, #53, #50 open | `gh pr view` | all **OPEN** | match |
| `_still_live` is `any(OPEN)` | `test_handoff_is_honest.py:145` | `any(s == "OPEN" ...)` | match |
| site behind 5 commits, 1 serving-relevant (`d999ae4`) | `tools/site_staleness.py` | identical | match |
| `bench.py:703` = `span = BENCH_RECORDING["hot_window"]` | file | identical | match |
| `score.py:242` overlap rule | file | `(fa_ends >= hot[0]) & (fa_times <= hot[1])` | match |
| 31 of 56 additive refused; 0/7, 6/7, 0/7 | `docs/todo/2026-08-25-two-scorers…md:116-137` | identical | match |
| four new tests in tune parity | file | 4 (`:571, :598, :611, :629`) | match |
| lane C `status: open` | file frontmatter | open | match |
| `main` green at `7637a84` | `gh run list` | success | match |

### Role 8 — per-section verdict

| section | terms first used here | defined here | cold reader follows? |
|---|---|---|---|
| opening | promiscuity probe, sweep, operating point, F1 | probe **now defined**; others are repo vocabulary in GLOSSARY | yes |
| the trap | `plant_times`, compressed timeline, `min_sep` | shown with the code and the mechanism spelled out | yes |
| what is done | `hotFa`, `poolScores`, `gateOnProbe`, splice | each row says what it does | yes |
| cued 1–7 | staleness, `hot_fa_per_min`, refit, lane C | each names its file or PR | yes |
| what I got wrong | — | — | yes |

### Role 10 — build & craft table

Markdown, no render step; rows checked against the file at `9bf67828`.

| check | result |
|---|---|
| relative links resolve | 3/3 OK (`../todo/…` ×3) |
| tables well-formed | all rows uniform pipe count |
| fenced code blocks balanced | yes; `python`, `bash`-less fence for the deploy command |
| sapper | clear (`tools/sapper.py --all`) |
| artifact hash changed after fixes | `7d11f549` → `49c1f642` → `eedb1700` → `9bf67828` |
| frontmatter/date consistent with filename | yes, 2026-08-28 |

## Residual ⚠

1. **Role 2 ran single-pass, and the process forbids that for attribution deliverables.** This
   handoff restates an attribution settled elsewhere (locust ← CICADA's coordinated-event
   stage, ADR-0002 / FOUNDATIONS §7) rather than making a new one, so the exposure is low —
   but the rule exists because a single pass inherits the drafter's search history, and this
   run did. Not satisfied; recorded.
2. **The F1-neutrality of planting the probe is unmeasured** and labelled as a prediction in
   the document. It should be measured before and after on the same folder, as the document
   itself instructs.
3. **Nobody was asked.** No correspondence check was run — there may be a prior decision about
   whether the user's simulated folder *should* contain a probe block at all, which is a
   product question this handoff raises and does not settle.
