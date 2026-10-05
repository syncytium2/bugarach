---
status: open
filed: 2026-09-20
---

# Why the merge-gap page's review would not converge, and the four things that can be done about it

waiting: Tony — options A to D below are a ruling, not a task. Nothing here re-runs, re-decides or
rewrites anything until he picks.

**The one-sentence answer: the page cannot carry a directional verdict at this sample size, because
the two sides of its comparison are not the same kind of object and the gap it calls "tuned" is a
boundary set by a constant nobody has signed.** Those are properties of the measurement, not of the
writing, so a third review round would find a third crop of the same shape.

**Working material, not murderboarded** — same standing as the handoffs and `docs/run_records.md`.
It restates numbers that other files own; where it disagrees with them, they win.

**The artifact:** `docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/net_merge_gap.html`, landed
with [#671](https://github.com/syncytium2/bugarach/pull/671). **The record:**
[`docs/reviews/net-merge-gap-2026-09-19.md`](../reviews/net-merge-gap-2026-09-19.md), delivered
unconverged after two blind rounds. **Asked for** by the orchestration session on 2026-09-20: read
both rounds' findings as a set and say what property keeps regenerating blocking findings — explicitly
**not** a third round, which the process's own escalation rule forbids here.

Abbreviations, all as the report uses them: **F1**, the harmonic mean of recall and precision;
**merge gap**, how close two of a detector's calls may be before they are combined into one;
**the budget**, the shared per-fold cap on false alarms; **the crowded check**, the refusal rule that
rejects a setting losing more than 0.02 mean F1 on crowded recordings; **refit**, one trained model
scored on an outer fold; **draw**, one sample of recordings (this run's, and the replicate's).

## 1. The three generators

The 11 blocking findings of round 1 and the 10 of round 2 are not 21 independent defects. They are
three recurring shapes, and the first two are properties of the measurement.

### Generator 1 — the two sides cannot be scored on the same terms, so every accounting choice is a new defect

CoactDetect contributes **one deterministic value per outer fold**, with no seeds and no refits. Each
net contributes **five refits per fold**, some of which fail to train. Every finding below is that
single asymmetry surfacing in a different column:

| the finding | round, role | what it says |
|---|---|---|
| the set-aside is one-sided by construction | R1 role 4 blocking; R2 role 4 M2 | dropping refits under 0.2 F1 can only move a **net's** margin upward — CoactDetect has no refits to drop. Every set-aside column in Table 1 is at or above the column beside it, in all 16 rows |
| the budget bound one side only | R1, record item 6 | CoactDetect's F1 under the budget equals its F1 alone in **every fold of both draws**, while 44 of the nets' 160 budget-chosen refits are over budget on the fold they were scored on |
| the crowded check bound the two sides at different times | R2 role 3, finding 4 | it runs inside this selection for the nets; for CoactDetect it ran back in goal 1, which refused 16 s — which is why its grid stops at 8 s and had nothing left to refuse here |
| the crowded cost was charged against the wrong reference | R1 role 6 blocking, then **again** R2 role 4 B1 | the reported cost is each net against its **own** 2 s. Head to head on the same recordings the tuned chorus nets *beat* CoactDetect by 0.016 to 0.056 F1 while `tube` loses 0.142 |
| the gaps match by name, not by operation | R2 role 4 M6 and the page's own §7 | a net merges runs of frames above its threshold; CoactDetect merges significant sliding windows 2 s wide. The same nominal gap starts fusing real events at different separations |

Five findings, one property. The reviewers are not finding new mistakes each round; they are reaching
the next accounting choice that had not yet been examined for the asymmetry. **Patching a column
cannot retire this, because the generator is the asymmetry and not any column.** That it recurred
across rounds — role 6 found the wrong-reference shape in round 1 and role 4 found it again in round
2, in a different column — is the direct evidence.

### Generator 2 — "tuned" names an operation that did not happen

Held-out F1 is largest at the **widest gap in the grid in all 64 fold-rows**. The chosen gap is
therefore not an optimum the nets found; it is the point where the crowded check stopped them
(record item 2; the page's §2 and §7 now say so).

What stops them is **a 0.02 F1 allowance that the project lead has not signed**, and its residuals in
the record are unresolved:

- one refusal turned on **0.0009 F1**, against a quantity that moves as much as **0.045 F1** between
  the inner fits the check is enforced on and the outer refits that produce the reported number;
- **two accepted choices fail that same check** when re-measured on the outer refits, by 0.063 and
  0.024 F1 against the 0.02 limit;
- **no sensitivity at any other allowance has been run.**

So every number on the page is a function of an unsigned constant. Reviewers keep flagging claims
built on it, correctly, and no round can fix that from inside the page.

### Generator 3 — the verdict is hand-written prose over computed numbers, and only some sentences are guarded

This one is ordinary, and it is the only one of the three that patching does retire. The page has a
`claim()` guard; the recurring defect is assertions that bypass it. Round 2's role 4 says it in terms:

- **B2** — "it does gain" asserted the outcome of a measurement the same sentence admits was never
  made; hardcoded in `tools/build_net_merge_gap_page.py` at about line 751.
- **B4** — "the nets that end ahead were already ahead" was contradicted by the numbers two sentences
  earlier; hardcoded in `alone_text()` at about line 549, *"while the numbers beside it are computed,
  so no guard catches it."*
- **B3** and R2 role 3 finding 2 — "each net gains 0.008 to 0.014 F1" was a range computed over the
  chorus nets only.
- **R1 role 5 F1** — "the better chorus net" named two different nets.

**All four were applied.** The shipped page no longer contains any of those sentences; that was
checked against the built artifact on `main`, not against the diff.

### Why the count did not fall, mechanically

Each repair **discloses another asymmetry**, which adds qualifying clauses, which grows the page. That
shows up in the one role that got measurably worse: **You Lost Me went from 3 blocking findings to 5**,
and its round-2 blocking rows are the lede, §1 and §2 — exactly the sections the repairs expanded. The
page becomes more honest and harder to read on the same edit.

## 2. Two corrections to the record itself

**The 11 → 10 comparison is not flat; normalised, it is worse.** Round 1 ran all 11 roles; round 2
re-ran 5. Per role run, blocking went from 1.0 to 2.0, and both structurally loaded roles rose —
Reviewer 2 from 3 to 4, You Lost Me from 3 to 5. The escalation decision was right, and the record
understates its own case. The record's stopping rule should compare like with like, or say plainly
that the two rounds ran different rosters.

**A round-2 role is claimed in the ledger but has no archived report.** The appendix says
*"roles 1, 3, 4, 8, 10"* and the round-2 ledger carries a row for *1 Prove It* (15 findings), but
`docs/reviews/net-merge-gap-2026-09-19-round2-roles/` holds only `03`, `04`, `08` and `10`. This is
not [the roster gate's path-resolution defect](2026-09-19-the-roster-gate-cannot-find-an-archive-named-by-the-skill.md),
which is a separate open item: here the path resolves and the file is absent.

## 3. What the page should stop claiming

Two sentences, and neither change costs a number.

1. **The title, "The nets' merge gap, tuned."** The page's own §2 and §7 say every chosen gap is a
   boundary the check imposed and *"neither is an optimum."* The title asserts the one thing the page
   spends two sections denying, and it is the only sentence most readers will carry.
2. **§3's heading, "Under the budget, the answer holds."** Its own body corrects it four sentences
   later — *"Read the heading as selected under the budget rather than scored under it."* A heading
   that needs a retraction inside its own section should instead be the fact that follows it: **every
   net gains and every net stays behind**.

## 4. The four options

| | what it is | what it buys | what it gives up / costs |
|---|---|---|---|
| **A. Demote verdict to measurement** | retitle; drop "the answer holds"; state the asymmetry as the result rather than as a limits bullet | a page that is defensible today, with nothing left to run; retires generator 3's remaining surface and neutralises generator 2's framing | the weekend's headline stops being *"CoactDetect still wins under the budget"* and becomes *"the gap is worth about one noise unit and the comparison has no neutral accounting"*. About an hour of work |
| **B. Measure and sign** | run CoactDetect on the crowded recordings **with no merging at all** — the cheapest check, never run — and sweep the crowded allowance | the only option that adds knowledge: it says whether CoactDetect's 8 s is bought on the same terms the nets' gaps are, which is the comparison the record names as missing | compute time, plus **a ruling on the allowance — see the gating note below**. It does **not** make the set-aside even-handed: generator 1 survives it intact |
| **C. Land with flags** | leave the page as it is; it is already on `main` with its residual list | costs nothing; precedent exists (065/chorus-collapse landed with flags on Tony's call) | the residuals stay open and resurface on the next page that reuses these selection rules — and the title keeps asserting "tuned" |
| **D. Narrow the scope** | split the two selections into separate pages, or drop the replicate from the main narrative | targets generator 3's surface growth directly; the cheapest way to make the cold-reader role converge | does nothing about generators 1 and 2; a reader loses the two-draw comparison in one place |

**A and B are independent.** A is honest framing; B is new evidence. They can be taken together, in
either order, or A alone.

### The gating note on B, which matters for which option is cheapest

Option B splits into a half that is gated on the unsigned 0.02 F1 allowance and a half that is not,
and the distinction decides whether B can start today:

- **Measuring CoactDetect with no merging is *not* gated.** It selects nothing. CoactDetect's gap
  stays fixed at the 8 s it ran with; the measurement reports what that 8 s costs it on the crowded
  recordings, against its own no-merge score — the same quantity already reported for the nets. No
  merge gap is re-decided, so the allowance is never applied.
- **Using that number to adjudicate *is* gated.** The moment the page says CoactDetect's 8 s "would
  have been refused" or "passes on the same terms", it is applying the 0.02 constant, and that is the
  decision Tony is already holding.
- **The sensitivity sweep is the input to the signature, not a consequence of it.** Running the
  selection at several allowances and showing whether the chosen gaps and the verdict move is exactly
  the evidence that would let the constant be signed. It precedes the ruling rather than waiting on it.

So B can begin with the descriptive half and the sweep, and stops at the point where a verdict would
be stated. If Tony signs the allowance, B and the wider merge-gap residuals unblock together.

## Closes when

Tony has picked among A, B, C and D; the two sentences in §3 are resolved one way or the other; and
the record's two corrections in §2 are either applied to
[`docs/reviews/net-merge-gap-2026-09-19.md`](../reviews/net-merge-gap-2026-09-19.md) or explicitly
declined.
