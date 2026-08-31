# A document that stopped claiming a winner, and the four places it still spoke like one

[`docs/performance_table.md`](../performance_table.md) replaces a ranking rule with a
table. The rule was removed because the question it answered was not being asked and,
tested, it could not be answered: tier membership moved with the seed block while the
argmax stood still.

**The review's main result is that removing an ordering is not the same as ceasing to
assert one, and the draft asserted in four places.**

The sharpest was arithmetic. The draft's caption read *"both flips happen where the gap is
under 0.004"*. One of the two flips has a gap of **0.0411** on one side — the claim is
true of the smaller side of each pair and false as stated. Corrected to *"each flip has a
gap under 0.004 on at least one side"*, with both pairs quoted so a reader can check
rather than take it. **A document arguing that a difference was too small to believe must
not overstate how small it was.**

The second was that the table in the draft had been **retyped rather than pasted**, and it
drifted: `3.48` where the code prints `3.47`, `0.47` where it prints `0.48`, and `locust`
where the code prints `sixth`. The prose quoting 3.48 drifted with it. The block is now
verbatim output of the command in §6 and a test asserts the two agree.

That last drift was the useful one. The code prints **`sixth`** because the viewer's title
map has said so since the detector was renamed to *locust* in 2026-08-24 — a rename made
specifically so a modified port would not carry the upstream's name in a public UI. The
placeholder is on the bake-off figure's axis too. The document now prints what the code
prints and flags it, because a document that silently renames what the code emits is one a
reader cannot check against the code. Filed:
[the title map still calls locust "sixth"](../todo/2026-08-30-the-title-map-still-calls-locust-sixth.md).

The third: **the figure had been dropped in the rewrite.** This repo's standing rule is to
render a visual finding rather than describe it, and "the top four overlap" is exactly
that. Restored — reusing the existing bake-off Panel A rather than drawing a new one,
since that panel was built for this defect and its own generator says so.

The fourth: **"fold" was used throughout and never defined**, having lost its definition
when the ordering sections went.

## What would validate this, and what it generalises to

The table's numbers rest on a bake-off of **8 seeds in 4 folds**, which is thin. A 24-seed
re-run is the thing that would firm up every row, and it re-quotes every published number,
so it is a decision rather than a chore.

The generalisable lesson is about deletion. Removing a claim leaves its supporting
apparatus behind — a caption tuned to the old argument, a table retyped when it was
pinned, a term defined in a section that no longer exists. **Three of the four findings
here are not errors in the new document; they are residue of the old one.** A rewrite that
removes a conclusion should be reviewed as a new draft, not as a diff.

---

# Appendix — run record

- upstream:  syncytium2/murderboard @ 564b944
- copy:      vendored @ 564b944
- freshness: **current** (gate exit 0)
- artifact:  `docs/performance_table.md` (`d6030d1` → `e79c40c`)
- roles:     11 of 11 run
- rounds:    1 review round + 1 blind re-read; **stopped on severity floor** — no blocking
  or major findings survived.

## Role ledger

| # | role | findings | what it checked |
|---|---|---|---|
| 1 | Claim & data verifier | **3** | Every quantity recomputed. Caught the `under 0.004` overstatement, and `3.48`/`0.47` drift from retyping the table. Demšar and Benavoli figures read out of the PDFs, not recalled: CD formula, the 0.94-vs-0.046 power pair, and `sqrt(m(m+1)/6)` = 5.10 at m=12, checked by arithmetic. |
| 2 | Citation & reference validator | 1 | Two citations, both fetched and read as PDFs rather than recalled — Demšar JMLR 7:1–30 (2006) and Benavoli, Corani & Mangili JMLR 17:1–10 (2016); both say what is attributed to them. ⚠ **Run single-pass, not as a separate agent** — see residuals. |
| 3 | Consistency auditor | **2** | The doc's table now matches the code's output verbatim (checked mechanically). Detector names against the glossary: proper names used, `corpus`/`modality` absent. Found `locust` in the doc against `sixth` in the code. |
| 4 | Adversarial reviewer | 1 | Pressed the central claim — *is "no ordering" a dodge?* No: the seed-block flip is measured and the fold ranges are printed, so a reader can reach their own verdict. Pressed the gates — each can fail, and one does (rate+context). Escalated the 0.004 overstatement from minor to major. |
| 5 | Line editor | 2 | Tightened §3; removed a hedge that had survived from the ranking draft. |
| 6 | Methods / domain expert | 1 | Verified the rejection of Friedman+Nemenyi is stated for the right reason — pool dependence, not power in general — and that the recommended fallback (Wilcoxon/sign + Holm) is what the cited paper actually recommends. |
| 7 | Reuse auditor | **1** | The figure: reuse `make_bakeoff_figures.py` Panel A rather than draw a new one. `performance.py` imports the bench's own ceilings so the table and the calibration refuse the same behaviour. |
| 8 | Naive-reader accessibility | **1** | "fold" undefined after the rewrite. Figure alt text describes what is visible, not what it means. |
| 9 | Density & figure-first | **1** | Figure dropped in the rewrite; restored with a caption naming what to look at, including that the bars still descend and thereby invite the ordering the table declines. |
| 10 | Build & craft gate | 0 findings | All internal links and the image path resolve; retired-vocabulary scan clean; the doc's table asserted identical to `render()` output. **No render step** — the artifact is Markdown and the one figure is pre-existing and current against `bakeoff.json`. |
| 11 | Argument order | 0 findings | Spine: why there is no ranking → the table → what a gate is → the broken column → what was rejected → reproduce → open. Problem first, and the cold open is the seed flip. |

## Residual ⚠

1. **Role 2 ran single-pass, not as a separate agent.** The process requires a separate one
   for any deliverable attributing a method, and this document attributes two. Both papers
   were fetched and read rather than recalled, which is the substance of the rule, but the
   blindness it asks for was not supplied — this session is directed not to spawn
   subagents.
2. **The bake-off is 8 seeds.** Every number in the table inherits that.
3. **`distr` ships broken and reported.**
4. **No probe ceilings for the learned models**, so four rows read `none` on the one gate
   that needs no ground truth.

## What this run does not warrant

This review found and fixed 11 defects. **It is not a correctness proof.** The stopping
condition measures how quickly a reviewer stopped finding things, not whether anything
remains — and that reviewer was one pass walking eleven checklists rather than eleven
independent ones, which is the condition under which reviewers look in the same wrong
place.
