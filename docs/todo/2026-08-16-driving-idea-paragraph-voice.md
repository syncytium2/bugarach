---
status: open
filed: 2026-08-16
---

# The driving-idea paragraphs say the right thing in the wrong voice

The two paragraphs under the lead figure on the public site now carry the
project's central argument — coordination is not one phenomenon, so a network
trained across all of it is mediocre at each, and the instrument should instead
be fitted to the recordings in front of it.

Tony, 2026-08-16: *"it's better, but the voice and vocabulary are off."* The
argument is settled; the wording is not. Landed as-is because it beats what it
replaced, and filed rather than churned because the fix needs his ear, not
another session's guess.

## One thing that is concretely wrong, not a matter of taste

**"there is no one detector to train" collides with the project's own
vocabulary.** In this repo a *detector* is one of the six ported algorithms
(GLOSSARY: the detector axis), and not one of them is trained — they are
calibrated. Using "detector" for the learned model blurs the term the whole
codebase is organised around, on the page most likely to be a stranger's first
contact with it. Whatever the rewrite does, the network and the six need
different words.

## Candidates for what else is off — guesses, for him to confirm or discard

- **"spends its capacity on a space in which almost nothing transfers"** —
  machine-learning register on a page whose reader is a physiologist.
- **"Stars coordinate and cells coordinate"** — rhetorical symmetry doing work
  that a plain statement of the timescale range would do better.
- **"comes out mediocre at all of it"** — casual.
- **"Worse for a working lab"** — editorialising; the page elsewhere states
  consequences and lets them land.
- **"the instrument gets built for your recordings"** — second person appears
  here and nowhere else on the page.

## Where

`INDEX` in [`tools/build_site.py`](../../tools/build_site.py), the two paragraphs
immediately below `{real}`. Rebuild with `python tools/build_site.py` and read
the rendered page, not the template — the site is a document deliverable, so a
rewrite goes through `/murderboard` before it lands.

Related: [`2026-08-15-draw-the-pipeline-instead-of-describing-it.md`](2026-08-15-draw-the-pipeline-instead-of-describing-it.md).
The second paragraph describes a flow that should be a diagram; if that figure is
built, the paragraph shrinks and part of this problem goes with it.
