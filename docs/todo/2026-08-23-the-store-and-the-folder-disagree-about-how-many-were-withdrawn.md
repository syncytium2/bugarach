---
status: open
filed: 2026-08-23
---

# One withdrawn recording, or two? Two records disagree, and the README needs one number

Found by the murderboard on `README.md`, which had to explain why the bake-off says
eighty-five recordings and the export folder holds eighty-four.

**The measured answer is one.** `docs/todo/2026-08-20-six-tools-still-read-stores.md`
tabulates it directly: *recordings surveyed — on the store 85, on the folder 84.*
That table was produced by running both.

**FOUNDATIONS says two.** Its regime paragraph describes the `.mat` store as
carrying every recording ever processed, *"including two the lab withdrew."*

Both cannot be right about the same pair of sources, and FOUNDATIONS is the canonical
document — so if it is wrong here it is wrong in the file that wins over every other.
The likelier reading is that the two sentences are about different stores (the plain
`revised_2v` against the rescued variant the bake-off actually measured, which the
provenance in `docs/learned/generator_spec.json` names), in which case neither is
wrong and both are underspecified.

## Why it is worth ten minutes

The README now tells an outside reader that 85 and 84 are different populations
rather than a typo — which is the right thing to say and is exactly the sentence that
wants a number. It currently declines to give one and points here instead. A
portfolio artifact should not have to hedge an off-by-one about its own data set.

## What settling it looks like

Count the recordings in each store under `$BUGARACH_DATA_ROOT` and in the approved
export folder, name which store each figure refers to, and make the two documents say
the same thing. Then the README's clause becomes "the one recording the lab withdrew"
— or two — and the hedge comes out.
