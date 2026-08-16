# Murderboard run — docs/workflow_plan.md

- upstream:  syncytium2/murderboard @ f43a07b
- vendored:  f43a07b (refreshed from b2b2ba2 in PR #42, commit 49da5b8, for this run)
- freshness: current
- artifact:  `docs/workflow_plan.md` (19bae3d9 -> 0bdb52a6)
- roles:     11 of 11 run
- rounds:    3 blind verify rounds (each found blocking defects; see below)

## What was reviewed, and the one thing to know about it

The artifact began life as `~/.claude/plans/jazzy-watching-pixel.md` revision 2 —
outside the repo, which FOUNDATIONS §8 forbids for anything that must travel, and
which it could not enter because a personal path in it triggered sapper SAP004.
Revision 3 is `docs/workflow_plan.md`: scrubbed, restructured, and in git.

**The gate fired before the review could start.** `murderboard_freshness.sh`
returned exit 1 — the vendored process sat at `b2b2ba2` against an upstream
`f43a07b`. The delta was entirely British-to-American spelling, thirty lines, no
rule changed, roster still eleven. Proceeding anyway was tempting and is forbidden
in terms. The vendor was refreshed (PR #42) and the gate re-run to exit 0 before
any role was spawned.

## Role ledger — all eleven

| # | Role | Findings | Notes |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | **3 blocking, 6 major, 9 minor** | Full claim ledger, every number recomputed. **Four load-bearing quantities had no source in any repo or its git history.** "51–67% of realized rate is not background" did not reproduce (recomputed 67% quiet / 31% busy). Quarantine count understated 3 vs 16. Contract described as v1.1 when v1.1 is explicitly not frozen. |
| 2 | Citation & reference validator — "DOI or Die." | **3 blocking, 3 major, 4 minor** | 117 identifiers extracted, every path opened. **38 of 49 checkable references verified exactly**, several to the character; nothing fabricated. Defects clustered in one class: line numbers into documents being rewritten concurrently. Found a systemic upstream defect — five decision-record numbers are each used twice in interface2. |
| 3 | Consistency auditor — "Cross-Examiner." | **3 blocking, 8 major, 5 minor** | Caught the plan reproducing, in its own build order, the exact error it corrected seventy lines earlier. Confirmed the SAP004 block with the rule cited. Found `grid_sec`/`grid_dt` conflated — right rule, wrong parameter. Verified the previous revision's self-contradiction fix was complete. |
| 4 | Adversarial reviewer — "Reviewer 2." | **5 blocking, 9 major, 8 minor** | The run's sharpest verdict: *"every guard the plan proposes is weaker than the hazard it is aimed at."* The fitting refusal was a checkbox whose own error message explained how to defeat it. The escape from circularity was renamed, not achieved. The claimed scientific payoff inherited the exact defect it was meant to retire. |
| 5 | Line editor — "Kill Your Darlings." | **4 blocking, 13 major, 15 minor** | Measured **26.7% of the document bolded** — emphasis had become the default typeface. Found four sentences the document itself contradicted elsewhere. |
| 6 | Methods / domain expert — "RTFM." | **4 blocking, 6 major, 9 minor** | Established that the proposed parity target cannot exercise the ported function (provable from column shapes alone). Found production runs the clustering gap **per stream**, 0.5 s and 2.5 s — a fixture at the default would validate half the contract. Found the proposed fitting method is the error the tree's own estimator documents and forbids. |
| 7 | Reuse auditor — "Reinventing the Wheel." | **3 blocking, 10 major, 7 minor** | Found the viewer and the bench feed one detector **different onset fields** — coinciding on synthetic data, diverging on real. Found four screenshot helpers where one carries a fix another still documents as a live hazard. Confirmed the peak-gating claim is supported. |
| 8 | Naive-reader accessibility — "You Lost Me." | **10 blocking, 12 major, 7 minor** | Per-section table: **14 of 18 sections blocking**. Established the run's most useful correlation — the only two sections a cold reader could follow were the only two containing no code identifiers. |
| 9 | Density & figure-first — "Show, Don't Tell." | **4 blocking, 6 major** | 2,533 words, one table, **zero figures**, in a repo whose durable rule is "show the picture — don't describe it". Named seven replacement artifacts and found **four already rendered** in `docs/generator/` and uncited. |
| 10 | Build & craft gate — "Ship It." | **4 fail of 32 rows** (8 N/A, reasons stated) | Not a render, so most canonical rows were N/A — the table ran regardless. **Ran the real commit gate and got `BLOCK SAP004`, exit 1.** Proved the build order collapsed to a single paragraph by actually rendering it. |
| 11 | Argument order — "Start With the Problem." | **2 blocking, 5 major, 3 minor** | Reduced the document to its spine and found it in written order, not argued order: the decision surface buried under 180 lines of execution detail, and the trap the plan itself called "invalidates every other check" placed after every check it invalidates. Prescribed the two-part split now applied. |

## Adjudication — what was fixed, and what the scope change dissolved

Mid-review the project owner narrowed the scope decisively: the app reads **one
self-contained export folder**, does **no region windowing** (an upstream exporter
does it), reads **no data store**, and reads **no event properties** — only onset
times. Output is **universally compatible first**, with the R side free to adapt.

That dissolved a large share of the findings rather than fixing them: everything
about region-window derivation, archive layout, store reading, the metadata
sidecar, the treated-window refusal, and quarantined reference data left scope
entirely.

**Fixed in revision 3:** the two-part restructure; the personal path (gate now
clear); the four unsourced quantities removed; the fitting method changed to the
maximum-likelihood estimator already in the tree, with the dispersion curve
demoted to a reported diagnostic; the parity target moved from the golden files to
synthetic fixtures; the per-stream clustering gap recorded; the recruitment field
corrected to present-and-missing-filled; the extra written column recorded; the
circularity claim restated as a consistency check; the read-before-you-run traps
hoisted above the checks they invalidate; the build order made a real list; the
open decisions collected and surfaced.

**Not applied, deliberately:** figures. Four existing renders and three new ones
were named. The plan is a decision document read once; the figures belong to the
deliverables it produces, where the same gate will demand them. Recorded as a
residual flag rather than silently dropped.

## Residual ⚠ — for the human

1. **⚠ The scientific payoff is a candidate, not a cure.** Porting the yardstick
   produces a candidate replacement for the flagged jitter constant. Both of its
   outputs are bounded by measurement parameters, and its clustering gap sits inside
   the noise band of the statistic being replaced. Retiring the flag needs a
   surrogate null computed for the new statistics and a round-trip test. Stated in
   the plan; not resolved.
2. **⚠ Which mode a generated run reports as.** Nine detector keys in real mode,
   six in surrogate — and the per-event file, the only consumer of the ported
   yardstick, exists in real mode only. Owner's decision.
3. **⚠ Whether the exporter emits `treatment_idx`.** The R side orders baseline
   against first treatment with it. Owner's decision.
4. **⚠ Whether to ask the R side to accept peak-mode keys.** Owner's decision.
5. **⚠ Figures deferred** (above).
6. **⚠ The plan has no per-milestone abort condition.** Raised by the adversarial
   reviewer, not addressed: no stage says what happens if parity fails, if the
   round-trip fails, or if the sources disagree.

## The three blind rounds, and what each layer was

Each round found a different **class** of defect rather than more of the last one,
which is the argument for having run three.

**Round one — wrong about the world.** Four quantities that read as measurements had
no source in any repository; a line citation resolved to a different sentence in
every checkout; a claimed statistic existed in a file the plan did not cite. Every
one arrived by message from another session and was written down unverified.

**Round two — wrong about its own logic.** The plan specified an input contract in
full and scheduled no milestone to read it. A caveat's arithmetic ran backwards. A
guard was introduced to catch a failure it structurally could not see.

**Round three — wrong about the consumer.** The output shape the plan proposed to
match would have been rejected by the analysis it was matching: that side requires
the first period of a recording to be named `baseline`, while the input contract
deliberately asks for its real name, and one figure script silently discards labels
it does not recognise. Tony resolved it by ruling the output must carry nothing
project-specific at all — our analysis adapts, and the private dialect is dropped
rather than reproduced.

Several round-three findings were defects **introduced by round-two fixes** — a new
milestone whose Part II section was missing, a heading scheme half-renamed. That is
the "a repaired deliverable has not been reviewed" rule demonstrating itself, and it
is why the blind pass runs before the follow-up pass rather than instead of it.

## Two process notes worth keeping

**Role conflicts were resolved by recomputing, never by picking the more alarming
reading.** Three arose. Two roles cited different line numbers for the same flag —
both were right, the document carries four instances. One role reported a directory
absent that another had verified present — the second was right; the first's search
missed a path containing a space. A count of writers inside one conditional block
disagreed 3 vs 4 — the higher was right, and the fourth writer turned out to be the
ported function's only consumer, which materially raised the stakes of an open
decision.

**The plan's weakest points were, without exception, the places it trusted a
relayed claim instead of opening a file.** Every fabricated number, every wrong
line citation, and the one attributed request that no source contains, arrived by
message from another session and was written down unverified. The correctly-sourced
material held up: 38 of 49 references verified exactly, several to the character.
