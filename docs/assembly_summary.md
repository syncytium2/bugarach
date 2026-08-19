# Cell assemblies: the answer, in one page

**Question.** In our slices, bursts of activity recruit a handful of cells at a time. Are
they the **same** cells each time — recurring cell assemblies — or a fresh draw?

**Answer. No recurring assemblies in the slow stream, and the absence is the result.** Two
instruments agree there. Graph modularity on the spike-time-tiling graph finds **no partition
above its null** — 2 of 83 recordings, and 1 of 79 with optical overlap removed. The
membership test finds participation is **not uniform** — some cells are in most events, many
in few — in 38 of 40 testable slow recordings, and in 47 of 49 fast. Uneven participation with
no modular partition is a **core–periphery** field, not an assembly: a busy core and a long
tail, with no membership that repeats as a unit.

**One limit, stated up front.** Modularity was computed on the **slow stream only**; there is
no fast counterpart. So the fast stream has the positive half of this answer (participation is
uneven) and none of the negative half — nothing has looked for modular structure there. **Drop
the word "assembly"** for the slow stream unless the modularity result is overturned, and do
not *assert* it for fast, where the question has not been asked. ⚠

![A · a real recording's membership table beside a generated one at the same geometry with participants drawn uniformly at random — the question cannot be settled by eye. B · power under the decision rule the corpus is actually scored by, at each real recording's own geometry, one curve per planted group size; the dotted line marks the 5% size of the test, where every curve begins when nothing is planted. C · the verdict before and after optical crosstalk is removed, paired on the fast and slow recordings testable in both stores; the grey bar counts recordings that fell below the testable floor, which is lost power and not a negative.](assembly_closed)

## Why you can believe it

Two objections decide this, and both were tested rather than argued.

**Could the test have failed?** Yes. Scored under the exact rule the recordings are scored
by — two statistics Bonferroni-corrected within each of two nulls, one decision per
recording — and evaluated at **each real recording's own geometry** rather than at a median
slice, the test fires on **5.3%** of fast recordings when nothing is planted (95% interval
3.1–8.9%) and **6.6%** of slow (3.9–11.0%), against a nominal 5%. Plant a four-cell group
recruiting one event in four and it fires on **90%** of fast recordings. So a negative here is a measurement, not a shrug. An earlier power curve had scored
a *looser* test than the one that produced the answer; correcting that is what closed this
question.

**Is it just optical crosstalk?** Partly, and not mostly. Neighbouring cells share signal, so
they co-participate for reasons that are not biology — and **no reshuffle can remove this,
because the artifact is already in the table being reshuffled.** Rebuilding the tables from
the penumbra-subtracted recordings and pairing the verdicts: the departure survives in **22
of 28** fast and **22 of 26** slow. All ten recordings that changed moved the same way, and
they are ten distinct recordings rather than one preparation counted twice (sign test
p ≈ 0.002) — so crosstalk **inflates the effect without accounting for it**.

## What this changes

- **The event generator is right as it stands.** It draws participants uniformly at random,
  which is a faithful model of this preparation. **Do not plant assemblies in it** — an
  earlier version of this work recommended exactly that, and on this evidence it would make
  the benchmark *less* faithful.
- **Do not port an assembly detector to score it on our corpus.** It would lose on membership
  recovery, and it would lose because the tissue has no membership to recover. That is a fact
  about the preparation, not a result about the method.
- **A previously claimed difference between experimental groups is withdrawn.** Planting the
  *same* assembly at each group's median event count reproduces the whole gradient — it was
  detection power, not biology.

## What it does not settle

**The fast stream has no modularity measurement at all**, so its assembly negative is untested
rather than established. Core–periphery is the reading that reconciles two measurements,
**not a fitted model**; nothing here tests it against alternatives. Penumbra subtraction removes an *estimate* of
optical overlap, so a residual is evidence the estimate was incomplete as much as evidence
the coordination is real. Modularity handles overlapping groups badly, so a field of
overlapping assemblies could evade it. And 36 of 85 recordings never reached the test at
all — too few coordinated clusters — and are reported as **undefined, never negative**.

Full detail, every number and every caveat: **the assembly report**, beside this file.
