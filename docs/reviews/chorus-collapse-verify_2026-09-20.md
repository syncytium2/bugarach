# The blind round the chorus-collapse page never got

## What was at stake

[PR #667](https://github.com/syncytium2/bugarach/pull/667) landed the chorus-collapse diagnosis on
`main` at Tony's call, carrying four flags. The heaviest said the round-2 repairs — a rebuilt
Figure 1, a new Figure 4, a merged Figure 5, a census and replays measured away from the
recording's ends, and rewritten sections 1 to 6 — **had been applied and rebuilt, and no reviewer
had seen them.** That page is public. This is the blind round it was owed.

The question was not "is the diagnosis right". It is right, and this round says so more firmly than
the last one could: role 1 re-derived `collapse_table.json` from the raw run archives without
calling the builder — **1,938 rows, zero differences** — re-ran every permutation test with an
independent generator at up to 200,000 shuffles, and rebuilt the nets in torch to re-measure the
untrained controls from first principles. Every count, every p-value, every median, every replay
number and every architectural statement reproduced. The page also rebuilds byte-for-byte, and I
confirmed it does so on **Python 3.11, 3.13 and 3.14** — all three CI legs — so the two
cross-version determinism bugs that bit this page before are genuinely closed rather than dormant.

The question was whether the repairs hold. **Three of six do not**, and the round found more
blocking findings than either round before it.

## The verdict, in one table

| round-2 repair | verdict |
|---|---|
| Figure 1 rebuilt as a matched pair (same fold pair, differing only in seed) | **holds** — role 1 verified the pairing and that the shown recording was held out from both fits |
| The census and replays measured on the interior (400 frames trimmed) | **holds as a measurement** — role 6 derived the receptive field independently (318 frames needed, 400 used) |
| Figure 5 merged | **holds** |
| The #596 vote-response test replacing the scale-free separation measure | **does not hold** |
| The selection split by rule (Table 2) | **does not hold for the budgeted column** |
| The replicate report's reading "corrected" on this page | **does not hold, and is new damage** |

### The three that failed, and why each is a different kind of failure

**The Figure 4 substitution narrowed a defect instead of removing it.** Round 2 replaced the
separation measure because role 4 had shown *an untrained plain chorus passes it* — a test that
could not fail. The replacement can fail. It still under-detects: role 4 measured the head's input
directly on the census recording for all 231 collapsed fits and found **6 chorus_norm and 13
chorus_gain_norm fits that pass the deafness test while their votes are, in fact, constant** — a
2.5× and 1.7× undercount. Role 1, attacking from a different direction, found the untrained
comparator the page sets its medians against (0.02–0.03) is the **lowest of the grid's four encoder
shapes by 14×**; for 4×4 and 8×4 an *untrained* net reads 0.45–0.51, at or above the collapsed
median. It also contradicts this project's own `field_size_candidates/README.md` at the very commit
§8 cites, which records 0.22–0.51 for the same quantity. Two roles, two attacks, one repair.

**Table 2's budgeted column is wrong under the page's own definition.** Roles 1 and 4 reached this
independently, and role 1 settled it from the raw score files: the two chorus_norm refits the page
counts as collapsed under the false-alarm budget have `n_detected = 0` at that rule's threshold.
They **call nothing**. The page quotes the sibling report's footnote verbatim — *"made one call per
recording **or called nothing** on the held-out fold"* — and then uses only the first half. The
table note is worse than the cell: it tells the reader the same collapsed refit counts under both
rules, when the real reason is that the two rules threshold the same trained model differently.

**The correction of the sibling report is a straw man, and round 2 introduced it.** Roles 2 and 4
independently read `tuned_vs_coact/replicate1/report.html` and found it already says the overlap
comes from *"shared configurations and training seeds"* — the same explanation §2 reaches. There is
nothing to correct. This is a public repository correcting its own public sibling for a sentence
that sibling does not contain.

## Underneath the repairs: the finding that is not a wording fix

Role 4's B1 is the one that cannot be patched. The page says, as its headline mechanism, *"**The
signal stops in the head**"*. `census.json` stores only `min_share_varying` — the **minimum across
the eight head layers**. It records neither which layer nor the head's **input**. So the artifact
cannot distinguish a signal that died inside the head from one that never reached it. Role 4
measured it directly and found the distinction is real: in **10 of 153 chorus_norm and 32 of 75
chorus_gain_norm** collapsed fits the head's input is already constant, and in 12 and 8 more the
only silent layer is the last one, with seven of eight awake — which contradicts *"a collapsed fit's
head is never woken"* in the answer box.

The builder's own module docstring promises both missing measurements: it says `census` records
*"how many units of **each** head layer … pass anything that varies"* and *"how well **the head's
input** and the output separate event frames"*. Neither field was ever stored. Closing this needs a
re-run of the census with those fields on a GPU — not an edit.

## Why this round stopped instead of repairing

`doc_review_process.md` says to stop when a blind round produces no blocking and no major findings,
**or after three blind rounds**, and separately: *"If severity is NOT falling across rounds, stop and
escalate to the human. A flat or rising blocking count after two rounds does not mean review harder;
it means the artifact has a structural problem that patching will not retire, and continuing to
patch converts a fixable draft into a long tail of edits nobody has reviewed together."*

Blocking went **3 → 4 → 6**. It is rising. So this round applied **no fixes at all**, and the
artifact's fingerprint is deliberately unchanged: `0aa79699bd888f0d1203cfa0cd9b597f0940879d`, the
same file round 2 rebuilt. Applying 59 major findings to a page whose central artifact cannot
support its central sentence is exactly the long tail that rule exists to prevent.

**This review found defects. It is not a correctness proof.** The convergence table measures how
quickly reviewers stopped finding things, not whether anything remains — and here they did not stop.

## Convergence

| round | artifact reviewed | blocking | major | minor | outcome |
|---|---|---|---|---|---|
| 1 (first pass) | 5cafecea | 3 | 52 | 111 | repaired and rebuilt (56e5c49) |
| 2 (blind, round 1 of 3) | fe8db88a | 4 | 55 | 110 | repaired and rebuilt; not blind-verified |
| 3 (blind, round 2 of 3) | 0aa79699 | **6** | 59 | 119 | **no repair applied; escalated** |

Stopping reason: **severity rising.** Blocking 3 → 4 → 6 (7 reported; roles 9 and 10 found the same
Table 3 defect). Counts are per role as each report states them and are not deduplicated across
roles, except the blocking column, which is deduplicated because it drives the stop decision.

## What Tony has to decide

Three of these are cheap and unambiguous; the fourth is a run.

1. **The wrong numbers.** "Counted 1 working fit as dead" is **5** (1 chorus_norm, 4
   chorus_gain_norm), and the same rule misses 3 collapsed chorus_gain_norm fits — recomputed by
   roles 1 and 6 and again by me. Correcting it *strengthens* the page's case for measuring
   variation rather than sign. Table 2's budgeted column is wrong. Three bounds round inward and
   are literally false as printed ("at least 0.82" against a true minimum of 0.81986).
2. **The straw man.** Withdraw the claim to correct the sibling report, or restate it as what §2
   actually adds to it.
3. **Table 3 is unreadable.** Its `outcome` column — the trains / does-not-train verdict the table
   exists for — is clipped by 211 px at every desktop width, with the scroll hint suppressed above
   700 px. Confirmed by roles 9 and 10 and measured again here. The content column is fixed, so
   widening the browser never helps.
4. **The mechanism sentence needs a census re-run**, or it needs narrowing to what the stored data
   support. This is the only item that costs GPU time, and it is the one that decides whether the
   page's headline can stay as written.

Two more, outside this claim's scope and named rather than touched:

- **`docs/goals/learned-model-family.md` states 112.6 and 40.4** where this page and the todo state
  111.5 and 39.6 (role 3). The page's numbers are the ones the tested builder computes. `docs/goals/`
  belongs to #664, so it is flagged here, not edited.
  **CLOSED 2026-09-20 by #678**, which moved the goal page to 111.5 / 39.6. The estimator the goal
  page had used pooled each configuration's rate across the two draws and squared it; the product of
  each draw's own rate is the unbiased one. The reading did not change.
- **Prior art sits under the page's novelty claim** (role 2, verified against the arXiv API here):
  Kosson et al. 2024 (arXiv:2410.23922) already reports that large initial updates permanently
  deactivate units and that warm-up prevents it. The delta is real — the *form* of the failure here
  is a head silent at initialisation that is never woken — but *"That it prevents this collapse is
  this page's result"* overstates it as written. Lu et al. (arXiv:1903.06733) predicts the
  encoder-shape direction in Table 1.
  **CLOSED 2026-09-20 — ruled ADJACENT, NOT THE SAME, and the novelty sentence is withdrawn.** Both
  papers were read, not searched. Kosson's dead-unit result is an appendix on a small image network
  where large updates **kill units that were alive**, counted at the end of training, and his remedy
  is a leaky rectified-linear unit — which works because a ReLU has an exact zero region to be stuck
  in. A GELU has none, so that repair is unavailable here and no layer of this head is dead in his
  sense, only silent. This page's head is already silent **before the first step**, in every replayed
  fit, working and collapsed alike. Lu et al. turned out to be the **closer** neighbour: *born dead*
  is dead-before-training, their theorem sends a gradient method (Adam named) to a constant function,
  and their depth-up / width-down ordering matches Table 1 in all four comparisons at lr 0.03
  (recomputed: 69→90% and 46→81% with depth, 69→46% and 90→81% with width). But their theory is
  ReLU-only and forbids the recovery this page demonstrates. The page now cites both, states the
  difference, and says what is left — which is narrower than the sentence it replaced.

## What generalises beyond this page

**A repair that narrows a defect reads exactly like a repair that removes one.** Round 2 fixed a test
that could not fail; nobody asked whether the replacement could fail *enough*. The check that caught
it was role 4 constructing the failing case and running it — not reading the test.

**A stored summary statistic quietly decides which claims are checkable.** `census.json` stores a
minimum across eight layers. Every claim about *which* layer, and every claim about what reaches the
head, became unfalsifiable the moment that choice was made — and the builder's docstring says the
richer fields were intended. Worth a habit: when a page's headline sentence names a mechanism, check
that the artifact can distinguish that mechanism from its neighbours.

---

## Appendix: the run

Mode: standard
- upstream:  syncytium2/murderboard @ 08f5ddb
- copy:      vendored @ 08f5ddb
- freshness: current
- artifact:  docs/learned/chorus_collapse/index.html (0aa79699bd888f0d1203cfa0cd9b597f0940879d -> 0aa79699bd888f0d1203cfa0cd9b597f0940879d, unchanged — no repair applied, see *Why this round stopped*)
- roles:     11 of 11 run (named agents)
- reports:   chorus-collapse-verify-2026-09-20-roles/
- rounds:    1 blind round in this pass (the run's third overall, blind round 2 of 3); severity rising (blocking 3 -> 4 -> 6); escalated without repair

**No model gate ran.** `murderboard_model_gate.sh` is not vendored in this repo. The run was on
Claude Opus 5, the process file's "known good" model, and was commissioned by a scheduled task that
asked for this specific review. Recorded because an absent gate that nobody mentions is
indistinguishable from a gate that passed.

**Blindness, and three nicks in it.** Every role was given the artifact and its sources and told not
to read `docs/reviews/`. Three disclosed accidental exposure and none opened a file: role 3's numeral
grep printed **one line** of a round-1 report in its results (a number it had already derived
independently); roles 2 and 7 saw round-1 **filenames** in `grep -l` listings. Carried here verbatim
rather than smoothed over — a blind round whose nicks are unrecorded cannot be audited.

**One edit to one archived report.** Role 2 wrote three MCP server names slash-separated; sapper
SAP004 reads that as a personal path and blocked the commit. The separators became commas, the file
says so in place, and the dispute is filed in
[`docs/sapper_feedback/2026-09-20-sap004-matches-a-list-of-names.md`](../sapper_feedback/2026-09-20-sap004-matches-a-list-of-names.md).
Nothing else in any report was altered; paths inside them are written as `<worktrees>`, `<darkroom>`
and `<scratch>`, as in the previous round's archive.

### Role ledger (blind, round 2 of 3)

| # | role | grant, as the reviewer declared it | findings | heaviest |
|---|---|---|---|---|
| 1 | Prove It | GRANT 1 ok — Read, Grep, Glob, Bash | 9, plus a full claim ledger; `collapse_table.json` re-derived from the raw archives with 0 differences in 1,938 rows; nets rebuilt in torch; every p-value re-run at up to 200k shuffles | major: Table 2's budgeted column counts refits that called nothing; "1 working fit as dead" is 5; the untrained comparator is the lowest of four encoder shapes and contradicts the project's own README |
| 2 | DOI or Die | GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 9; all 8 references fetched as PDFs, all 8 exist, resolve and support their sentence | major: Kosson et al. 2024 is uncited prior art for the novelty claim; the born-dead literature predicts Table 1's shape effect |
| 3 | Cross-Examiner | GRANT 3 ok — Read, Grep, Glob | 14; every population reconciled to one counting basis | major: `docs/goals/learned-model-family.md` states 112.6/40.4 against this page's 111.5/39.6 |
| 4 | Reviewer 2 | GRANT 4 ok — Read, Grep, Glob, Bash | 19; re-ran forward passes for all 231 collapsed fits plus 8 working | **blocking: "the signal stops in the head" is false for 10 chorus_norm and 32 chorus_gain_norm fits; the warm-up result was never scored on calls and its checkpoints were discarded** |
| 5 | Kill Your Darlings | GRANT 5 ok — Read, Grep, Glob | 35 (tool not vendored; banned-construction list searched by hand, zero hits) | major: the twin "recovered" counts sit outside their stated denominator; "8 distinct" vs "7 distinct"; "plain chorus" never defined |
| 6 | RTFM | GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 16; all four cited papers fetched; the 400-frame trim derived independently | major: the warm-up's 6-of-7 and its 1.4-of-7 null are different metrics; the Adam framing compares lr to the wrong quantity; "1 working fit" is 5 |
| 7 | Reinventing the Wheel | GRANT 7 ok — Read, Grep, Glob, Bash | 13, plus a 16-row duplication table; collapse counts reproduced under both keyings | major: nothing binds the four duplicated algorithms to their canonical versions; the vote copy omits the `input_gain` branch |
| 8 | You Lost Me | GRANT 8 ok — Read, Grep, Glob | 26, plus a per-section table and a false-friend check on every figure | **blocking: six undefined terms in the architecture paragraph; "the false-alarm budget" never defined though §3 turns on it; Figure 1's caption precedes its definitions** |
| 9 | Show, Don't Tell | GRANT 9 ok — Read, Grep, Glob, Bash | 19, plus a measured density table (page 11,916 px, 30.2% figure) | **blocking: Table 3's `outcome` column is clipped and there is no affordance** |
| 10 | Ship It | GRANT 10 ok — Read, Grep, Glob, Bash | 13, one row per figure and table, rendered at 1440/1920/390 px with greyscale and CVD simulation; rebuild byte-identical; `pytest` 3 passed; SAP004 clean | **blocking: the same Table 3 clipping, confirmed at two widths**; major: Figure 6 separates three series by colour alone and two collapse under deuteranopia; Figure 4 has no on-figure legend |
| 11 | Start With the Problem | GRANT 11 ok — Read, Grep, Glob | 10, plus a section-by-section ordering map | major: the stake is never assembled and its only early appearance is a negation; the n behind the central claim is withheld until Limits; the open decision is stated but never located |

Roles 2 and 7 each also named **SubagentHandback**, the channel a subagent reports back through,
alongside their granted tools — role 7 inside its `GRANT` line, where it made the declared set differ
from the granted one and the grants gate refused the report until this note existed. It is the
delivery mechanism every subagent holds, not a reviewing tool the process grants, and neither
reviewer reached anything outside its grant. Recorded here once rather than edited out of the
ledger, because the gate's question — *did every role state what it held* — deserves a true answer
and not a tidied one. Both reports carry the parenthetical verbatim in the archive.

### Adjudication

**Everything below is adjudicated `flag`, not `fix`.** That is the round's outcome, not an oversight:
severity rose, so the process stops rather than patches, and a repair pass here would create a fourth
layer of unreviewed text over an artifact that needs a data re-run. The ranked list Tony acts on is
*What Tony has to decide*, above. Every finding is preserved verbatim in the role archive.

Two findings were **confirmed by more than one role independently**, which is why they head the list:
the Table 2 budgeted column (roles 1 and 4, from different evidence) and the straw-man correction of
the sibling report (roles 2 and 4). Three more I recomputed myself rather than relaying: the sign-rule
count of 5, the 211 px Table 3 clipping, and the census's missing fields.

### Checks

- `bash tools/murderboard_roster.sh check --require-reports docs/reviews/chorus-collapse-verify_2026-09-20.md`
- `python tools/murderboard_agents.py --process docs/doc_review_process.md verify docs/reviews/chorus-collapse-verify_2026-09-20.md`
- Cross-version rebuild: byte-identical on Python 3.11, 3.13 and 3.14 (the three CI legs).
