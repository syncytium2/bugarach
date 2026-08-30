---
status: open
filed: 2026-08-27
---

# `pick_threshold` holds out its validation set; `fair_bakeoff` hands it back the training recordings

> Found by the murderboard on the learned-detector page
> ([`docs/reviews/learned_detector_2026-08-27.md`](../reviews/learned_detector_2026-08-27.md)),
> confirmed by two roles independently, one of which ran the seed arithmetic.

**The headline F1 is not inflated by this and the comparison against the six is not
invalidated.** The scored fold is genuinely untouched. What is wrong is narrower and
worth fixing anyway: a fairness guarantee the code states, and states carefully, is
not delivered at the call site.

## The seam

`src/bugarach/learn/train.py` is written correctly. `pick_threshold` draws
`TRAIN_SEED_BLOCK + 500_000 + …`, disjoint from the training seeds, and **asserts** it
— the docstring calls the separation *"explicit and asserted rather than assumed."*

`tools/fair_bakeoff.py:180` then passes a maker that throws the seed away:

```python
mk = lambda seed, _t=tuple(tr_seeds): rec(_t[seed % len(_t)])
```

Fold 0, run:

```
train() asks for  [10000..10005]   -> recordings [1006, 1007, 1002, 1003, 1004, 1005]
pick_threshold    [510000..510003] -> recordings [1002, 1003, 1004, 1005]
validation recordings also in the training set: 4 of 4
validation recordings in the held-out fold:     0
```

The assertion passes because it tests **seed integers**, and the modulo indirection
makes those meaningless. `tools/ablate_tube.py:82` has the same line. Note
`tools/make_architecture_figures.py:92` passes the seed through and does **not** have
this, so two tools that look alike behave differently.

## Why it matters even though the score is safe

The six have one knob and nothing to overfit beyond it. The learned model picks its
operating point on recordings its 1,149 weights were just fitted to, which is a
stronger in-sample condition than the sentence *"chosen on held-out data"* describes.
On a public page that sentence is one of the fairness guarantees, and it was there
because the code appeared to support it.

## Two repairs, and the cheap one is not obviously right

**(a) Give the threshold its own recordings.** Reserve one or two of the six training
recordings as a threshold set, or map validation seeds onto recordings outside
`tr_seeds`. Preserves the claim; changes published numbers, because every learned
operating point moves.

**(b) Say what the code does.** *"chosen on the training folds, never on the fold
being scored."* Free, honest, and it is what the page now says.

The page took (b) as an interim. **(a) is the one that makes the guarantee true**, and
it should be decided together with the re-fit rather than bolted on — it is the same
class of change as
[revise the bench recording before the re-fit](2026-08-23-revise-the-bench-recording-before-the-refit.md).

## The general shape, worth a line somewhere durable

**An assertion that checks an index rather than the thing the index resolves to is
not a check.** `pick_threshold`'s guard is well written, well documented, and was
satisfied on every run while the property it guards was false. Whatever replaces it
should assert on the *recordings*, not the seeds — the identity that actually matters
survives the indirection and the integer does not.
