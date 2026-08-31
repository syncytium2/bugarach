# A ranking rule that promised stability, and the test that says it does not deliver it

> **The artifact this reviews no longer exists.** `docs/ranking_rule.md` became
> [`docs/performance_table.md`](../performance_table.md) hours after this run, when Tony
> ruled that no winner needs declaring. **The blocking finding below was not fixed — the
> ordering it applied to was removed**, which retires the question instead of answering
> it. The record stays exactly as written: it is what the review found, and that finding
> is a large part of why the ordering went.

The document under review, `docs/ranking_rule.md`, exists to
solve one problem: **the detectors cannot be ordered, because the order changes with
the seeds.** Its answer is to emit tiers rather than an order, and to call two
detectors tied unless one wins by more than 0.02 mean F1 on a majority of paired
folds.

**The review's main result is that the answer does not work at that number.**

Tiering the six hand-written detectors on seeds 1–12 and again on seeds 13–24 gives
two different tierings — `{CoactDetect, LoCo, rate+context}` is a single tier on the
first block and splits into three on the second, while the argmax stays put in both.
The rule's whole promise is that the *tiers* survive what the *ordering* does not, and
on its first real test that is exactly backwards. Sweeping the margin, the two
tierings first agree at **0.08**; doubling the seeds per fold does not close the gap.

That is a **blocking** finding and it is **not fixed**, because the margin is decision
D4 and belongs to Tony. It is filed with its evidence and three named options in
[the tie margin does not survive its own test](../todo/2026-08-30-the-tie-margin-does-not-survive-its-own-test.md),
and the rule document now carries it as a blocking flag in §5 and §8. The code still
ships 0.02.

**Second result: the document's opening claim was inherited and does not reproduce.**
The draft opened on the brief's statement that CoactDetect wins all seven background
levels on seeds 1–12 by 0.0011 at the busy end. Re-run on `main`, CoactDetect takes
**three of seven**, and varying the match tolerance does not recover the original.
The brief's numbers were most likely produced on the branch carrying a fitted
background shape. **The underlying finding survives** — the winner still flips between
seed blocks, at two of the seven levels — so §1 was rewritten around numbers this
document produced itself, and the discrepancy is flagged for reconciliation before the
brief's figure is quoted elsewhere.

That correction paid for itself immediately. The re-derived sweep shows **both flips
occur where the gap is under 0.004, and no level whose gap clears 0.02 in both blocks
changes its winner** — an independent check on the tie margin from data the brief never
used, and the reason the margin's *failure* above is a statement about tier
composition rather than about pairwise comparison.

## What would validate this, and what it generalises to

The tier-stability test should run on the **bake-off's** structure, not only on the
background curve: twelve detectors, its own fold split, at twenty-four seeds. That run
is the one that decides whether option 2 in the write-up — restricting the claim to
tier 1 versus the rest — is enough.

The generalisable lesson is about where a threshold's number comes from. **0.02 was
set from the bench's noise floor — the smallest difference worth believing — and then
used to absorb the between-block spread, which is a different quantity.** Nobody
checked that the two were the same, and they differ by about four times. Any
project setting a "these are equivalent" band should ask which of the two it measured.

---

# Appendix — run record

- upstream:  syncytium2/murderboard @ 564b944
- copy:      vendored @ 564b944 (re-vendored during this run — see below)
- freshness: **current** (gate exit 0; it exited **1** at first call and was cleared by #417)
- artifact:  `docs/ranking_rule.md` (`a76b481` → `bf7e14a`)
- roles:     11 of 11 run
- rounds:    2 (1 repair round, 1 blind re-read); **stopped on severity floor for
  fixable findings** — the one blocking finding that remains is not fixable by this
  session and is escalated, not carried as an open round.

**Freshness note.** The gate refused this run: vendored `f62acb3` against upstream
`564b944`. `murderboard_revendor.py --check` showed *"would re-copy (body changed):
none"* — every body byte-identical, only the stamp behind — so no rule was missing,
but the gate is a gate. Cleared by re-vendoring on `main` (#417, merged) rather than
by proceeding past it.

## Role ledger

| # | role | findings | what it checked |
|---|---|---|---|
| 1 | Claim & data verifier | **4** | Every quantity re-computed from `bakeoff.json` and the code. Found the draft presenting inherited and re-derived numbers in one voice; found the background-axis claim not reproducing on `main`; found `distractor_hits` not measuring what its name says; confirmed all twelve bars of the reused figure against per-fold means. |
| 2 | Citation & reference validator | 1 | Only named attribution is the Condorcet paradox (Condorcet, 1785), now stated in text as standard and not claimed as new. ⚠ **Run single-pass, not as a separate agent** — see residuals. |
| 3 | Consistency auditor | **3** | Probe rates 1.25 / 20.5 (BENCH_RECORDING) sat unlabelled beside 0.12 / 2.05 (bake-off) for the same two detectors — a reader would have read a contradiction or a trend. "Three measurements" headed a four-row table. Glossary: prose used code keys where proper names are reserved; "corpus"/"modality" absent (checked mechanically). |
| 4 | Adversarial reviewer | **2** | *Can the alarm ring?* — the seed floor can and does fail (it refuses the shipped bake-off, asserted as a test); the probe gate fires on rate+context; the distractor gate is disarmed and says so. Demanded a test of the central claim, which produced the blocking finding above. |
| 5 | Line editor | 3 | Caption had unbalanced emphasis markers; "hot-window" jargon → "probe-block"; two unnamed detectors in the precision/probe comparison. |
| 6 | Methods / domain expert | 1 | Tier construction is a level decomposition of the beats-DAG; acyclicity argued and checked by search. Found the `None`-means-two-things collision on `max_probe_per_min`, fixed with an explicit sentinel. |
| 7 | Reuse auditor | **1** | The needed figure already exists — `make_bakeoff_figures.py` Panel A, written for this exact defect. Reused rather than rebuilt. `rank.py` imports the bench's own ceilings so ranking and calibration refuse the same behaviour. |
| 8 | Naive-reader accessibility | 2 | "Fold" was used throughout and never defined — now defined in §2. Figure alt text describes what is visible, not what it means. |
| 9 | Density & figure-first | **1** | Five tables and no figure, in a repo whose standing rule is to render a visual finding rather than describe it. Fixed by embedding Panel A with a caption that names what to look at — and notes that its bars descend left-to-right, inviting the ordering the rule declines. |
| 10 | Build & craft gate | 2 | All four internal links and the image path resolve (checked mechanically). Emphasis-balance scan clean apart from bold spanning line breaks. Figure verified current against `bakeoff.json`. **No render step** — the artifact is Markdown. |
| 11 | Argument order | **1** | The draft opened on its own solution. The problem now opens it; the rule/result split moved to §2 where it answers something. |

## Residual ⚠ — for Tony

1. **BLOCKING — the 0.02 tie margin does not make the tiers reproducible.** Not fixed;
   D4 is yours. Three options, with evidence:
   [the tie margin does not survive its own test](../todo/2026-08-30-the-tie-margin-does-not-survive-its-own-test.md).
2. **The brief's background-axis numbers do not reproduce on `main`.** Worth
   reconciling before that figure is quoted anywhere else.
3. **D3 shipped disarmed.** `distractor_hits` counts span coverage, not firing;
   repairing it changes published numbers and is owned elsewhere.
   [Write-up](../todo/2026-08-30-distractor-hits-counts-coverage-not-firing.md).
4. **Role 2 ran single-pass, not as a separate agent.** The process requires a
   separate agent for any deliverable that attributes a method; this session was
   directed not to spawn subagents, so every role was walked in one pass. The
   attribution surface here is one standard term, but the blindness the rule asks for
   was not supplied.
5. **The learned models have no probe ceilings**, so they are ungated on that axis
   while `tube` fires above the ceiling its closest hand-written counterpart is held
   to. Setting them is a measurement, not a default.

## What this run does not warrant

This review found and fixed 12 defects and escalated 5. **It is not a correctness
proof.** The convergence above measures how quickly reviewers stopped finding things,
not whether anything remains — and one round of it was a single reviewer walking
eleven checklists rather than eleven independent ones, which is precisely the
condition under which reviewers look in the same wrong place.
