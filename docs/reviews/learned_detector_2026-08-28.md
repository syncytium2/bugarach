# Murderboard run — docs/learned/learned_detector.html (re-review after #356)

Supplements [`learned_detector_2026-08-27.md`](learned_detector_2026-08-27.md), which
reviewed this page over eleven rounds. **This is not that review re-run.** It covers
what changed underneath the page after it was finished, and the page's prose was
written against numbers that have since moved.

## What was at stake

The branch was one merge from landing a page that would have **reintroduced a claim
`main` retired the same day**. Its attribution table said locust *is* *"CICADA's
method, from the Cossart lab, ported and modified"*. PR #360 merged hours earlier for
the express purpose of removing that sentence from a public page, having established
that the 1e-9 parity validates bugarach against **interface2** and says nothing about
CICADA, that the port **skips a whole stage**, and that it **replaces the
active-duration model**. PR #363 shows the same claim recurring in a handoff six
minutes after #360 landed, so this is a defect that reasserts itself.

## What the re-run found, and it is worse than stale numbers

**Three tools still had the defect #356 said it had fixed.** That PR's own commit
message claims *"both call sites"*. There were five. `tools/ablate_tube.py` was on
`main` and was missed; `tools/probe_one_vote.py` and `tools/probe_rate_invariance.py`
were written on this branch **after** the fix landed. Every number this page quoted
from those three stores had its operating point chosen on the recordings the model had
just been fitted to.

**Fixing them reversed a published conclusion.** The scale ablation, before and after:

| variant | before | after |
|---|---|---|
| 4 scales | 0.668 | **0.681** |
| 2 scales | 0.634 | 0.664 |
| 1 scale | **0.670** | 0.649 |

One scale used to beat four, and two scales sat outside both — which the page
correctly flagged as *"no monotone reading predicts"*. It is now cleanly monotone in
scale count. **Neither ordering is a result**: all three differences remain inside the
fold spread, and a grid whose ranking flips when an unrelated defect is fixed is a
grid reporting it cannot resolve the variable. That is what the page now says.

**And the question that prompted the ablation stopped reproducing.** It exists because
a fitted surround ratio sat at 38 against a ceiling of 40. Nothing now fits above
**28.6**, at any scale count, so the ceiling is clear everywhere. The page's claim that
the clamp *"does bind, in the single-scale runs"* — whose scores *"differ as they
must"* — is now false twice over: it binds nowhere, and those two runs are identical.

## What this generalises to

Prose did not catch a five-copy defect; a grep did. **SAP010** now blocks the maker
shape across `tools/**` and `src/bugarach/**`, with a selftest proving it fires. On its
first scan it caught two of my own explanatory comments — the self-describing-string
trap this file has sprung four times before — which is itself evidence the rule reaches
what prose cannot.

---

## Run record

- upstream:  syncytium2/murderboard @ 3593c44
- copy:      vendored @ 3593c44
- freshness: current (`--refresh`, exit 0)
- artifact:  `docs/learned/learned_detector.html` (rebuilt; 47d86a70 after)
- roles:     11 of 11 run
- rounds:    1 blind verify round to clean (the 2026-08-27 record carries 11)
- ⚠ **deviation:** single-pass self-review, not parallel subagents — this session
  operates under a standing instruction not to use the Agent tool unless asked. Role 2
  is the one role the process says may not collapse when a deliverable **attributes a
  method**, and this page does exactly that. **That role's finding here is therefore
  taken from #360's separate, agent-run review rather than re-derived**, which is the
  best available substitute and is not the same thing.

### Role ledger

| # | role | findings | note |
|---|---|---|---|
| 1 | Claim & data verifier | **4** | Three derived stores regenerated after the defect fix (`tube_ablation`, `one_vote`, `rate_invariance`), plus `probe_inclusive` after #356. Recomputed every ranking claim against the new stores: locust 5th published / 7th charged ✓, coact−loco gap 0.025 ✓, tube drop 0.138 against coact's 0.011 ✓. Found the reversed ablation, the no-longer-binding clamp, and the two identical single-scale runs the page said "differ as they must". |
| 2 | Citation & reference validator | **1** | The attribution row asserted locust *is* CICADA's method. Corrected to #360's established wording: a **partial** port of an **older** implementation, one stage skipped, active-duration model replaced, chain checked only at its last link. ⚠ Taken from #360's agent-run review, not independently re-derived — see the deviation note. |
| 3 | Consistency auditor | **2** | Page described `bakeoff.md` as *"still lists locust as CICADA"* — false since #365 renamed it; removed. Confirmed the two surviving CICADA mentions in the built page are correct usages naming the *original* method, which ADR-0002 keeps. |
| 4 | Adversarial reviewer | **1** | Attacked the new monotone ordering: it is not evidence for four scales either. The page now says so, and says why a flipped ranking is itself the finding. |
| 5 | Line editor | **0** | Changed passages read in the page's existing register; ⚠ markers used as the page already uses them. |
| 6 | Methods / domain expert | **1** | Checked whether `make_architecture_figures.py` shares the defect — **it does not**: it generates a fresh recording per seed rather than indexing a fixed set, so the two seed blocks never collide there. `architecture_fitted.json` therefore needed no regeneration on that account. |
| 7 | Reuse auditor | **1** | All three fixed tools now call `learn.train.fold_maker` rather than each re-deriving the split, which is the point of that helper existing. |
| 8 | Naive-reader accessibility | **0** | The attribution row is longer but every term in it is defined in place; no new jargon. |
| 9 | Density & figure-first | **0** | No figure changed. Prose grew in two paragraphs, both caveats, which the process says to relocate rather than delete — they are in the paragraph they qualify. |
| 10 | Build & craft gate | **1** | **Rebuilt** and audited: 0 unresolved `{{` tokens, both CICADA mentions verified as correct usages, hash changed. |
| 11 | Argument order | **0** | Section order untouched; the corrections sit in the paragraphs they qualify. |

### Residual ⚠ for a human

1. **Role 2 was not independently re-derived** — see the deviation note. The wording is
   #360's, which *was* agent-reviewed, but this run supplied no fresh blindness.
2. **Thread pinning touches every trained artifact, not only the ones regenerated here.**
   `architecture_fitted.json` is fitted through `train()` and so is now produced under a
   pinned thread count; it was **not** regenerated, because the defect this run chased
   never applied to it. Whether every trained store should be refreshed under the pin is
   a separate decision, and
   [`2026-08-27-the-fitted-kernels-figure-is-a-different-fit.md`](../todo/2026-08-27-the-fitted-kernels-figure-is-a-different-fit.md)
   is already open on that figure.
3. **The scorer question is still open and still visible on this page.** Under the
   probe-inclusive rule the tube (0.543) now falls **below** CoactDetect (0.640) and LoCo
   (0.615). The page shows both columns and declines to answer, which is correct — but
   the decision still blocks the re-fit.
