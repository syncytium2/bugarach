# Goal: a document about the detectors that an outside reader can judge

> **The goal page for this work — start here.** The tree calls the same goal *the detector review*,
> *the plain-language page*, *the review document* and *the document for external review*; they are
> one goal. This page holds the goal, what is settled about it, what was tried and dropped, and what
> is waiting on Tony, with a link beside every line. **The linked file wins** where the two disagree,
> and a line found wrong is fixed in the same change as whatever you were doing.
>
> **Working material, not murderboarded** — same standing as [`pipeline.md`](../pipeline.md). The
> *document* is murderboarded; this page about it is not. No tree counts; measured numbers are content
> and carry their source. How the page stays true is at the bottom; the convention is in
> [`README.md`](README.md).
>
> **Written 2026-09-16** against `origin/main` at `a7fe2f8` and the open branches.

---

## The goal

Everything this project knows about its detectors is true and scattered: where each one came from is
in one document, what the simulator imitates is in another, what the numbers are is in a third, and
the rule that picked each operating point is in a tool's docstring. An outside reader — a colleague,
a reviewer, someone deciding whether to trust the instrument — cannot assemble that, and should not
have to. Tony, 2026-09-16:

> this will be reviewed by people judging the project. this looks like unfinished business

The goal is **one document** that takes such a reader from what a coordinated event is, through every
detector and how each one decides, through the simulator and the grading and the tuning that produced
the operating points, to held-out results and the detectors running on real recordings — with the
weaknesses stated rather than smoothed. It is a portfolio artifact in the sense of FOUNDATIONS §8,
which is why it gets the murderboard and why a claim that overstates costs more here than a bug.

Abbreviations used below: **F1**, the harmonic mean of recall and precision; **TTX**, tetrodotoxin;
*senktide* is the other treatment condition. A **blind round** is a review pass run without telling
the roles what the previous round found.

## Where it stands

**Two documents exist, both built, both in the darkroom, and neither has finished review.** They are
on branch `detector-review-doc`, [PR #587](https://github.com/syncytium2/bugarach/pull/587) ⚠ **open
and unmerged, so none of it is on `main`**.

- **The formal review** — every hand-written and learned detector with a figure of it deciding,
  surrogates, the simulator, grading and tuning, held-out results, the detectors on real TTX and
  senktide recordings, and strengths and weaknesses. Three blind murderboard rounds ran, eleven roles
  each. **It hit the round cap and was delivered unconverged**, with ten open items listed in its run
  record — so the review is evidence that the roles ran, not a proof that the document is right.
- **The plain-language page** — the same subject for a reader who is not already steeped in it:
  twenty figures, about eight thousand words, the six hand-written programs. **Tony is reading it and
  sending notes one at a time**, and each note is filed with its diagnosis and applied in the same
  turn. That notes file, not this page, is the live state of the plain document. The four neural
  networks were cut out of it onto a separate page at his instruction and are held back unreviewed.

**The numbers in both predate three merges** — locust's per-event widths, binned SCE's scoring, and
the retune of all six operating points. Merging `main` in and regenerating is the first thing the
document needs, before anything else is written into it.

**The overnight search over every declared setting is meant to land in this document** as a
measurement — *every declared setting was searched, and here is what beat the shipped point on
recordings the search did not see*. That is the answer to *it looks unfinished*. The sibling goal
page is [`coded-detector-optimization.md`](coded-detector-optimization.md), and its handoff says how
to phrase the result without turning a finding into an adoption.

## What is settled

**Strength** follows [`MILESTONES.md`](../MILESTONES.md): *measured* is a number from a run, *decided*
is a ruling, *argued* is reasoning nobody has measured.

| finding | strength | source |
|---|---|---|
| **The document is darkroom-only, and that is a rule, not a preference.** It embeds real treatment recordings, so under FOUNDATIONS §5 it is written to `<darkroom>/bugarach/2026-09-15-detector-review/` and never to the repo: no repo copy of those figures, no web link. Every sentence that describes a real recording lives beside it in `real_prose.json`, which stays out of the tree — and the page cannot build without it | decided | [FOUNDATIONS §5](../FOUNDATIONS.md); [PR #587](https://github.com/syncytium2/bugarach/pull/587) |
| **Every number in the prose is a token filled from the stage that drew the matching figure**, so a figure and the sentence about it cannot drift apart silently | built | `tools/make_detector_review.py` ⚠ **on the branch, not on `main`** |
| **Section numbers are computed from the template, never typed.** A restructure that leaves a stale cross-reference is the failure this prevents | built | same |
| **Captions do not follow their figures, and that cost the document twice.** A figure was replaced and its caption survived, reading plausibly and describing data that were no longer there. Captions that state a fact are now written from that figure's own measured tokens, which is the only form the build can check | measured, twice, the hard way | `HANDOFF-detector-review.md` on the branch ⚠ **not on `main`** |
| **The review changed the findings, not only the wording.** The bench never planted events in its busy block, so a detector that goes blind there lost nothing; a new stage plants them, and detectors that judge chance from nearby time lose most of those events while the ratio tube models lose all of them | measured, and the stage is built | [PR #587](https://github.com/syncytium2/bugarach/pull/587) |
| **Binned SCE was being scored over the wrong stretch**, found by reading the document rather than the code: scored over each call's own bin, tuned binned SCE goes from F1 0.45 to 0.70. Filed as a decision because the detector's contract is parity-locked — and it then landed | measured, then landed | [PR #593](https://github.com/syncytium2/bugarach/pull/593); [the todo](../todo/2026-09-15-binned-sce-calls-are-scored-over-the-wrong-stretch.md) |
| **The murderboard ran completely**: all eleven roles accounted for with `--require-mode --require-reports`, and public copies of all three rounds' role reports are kept with the treatment-recording lines removed | built, checked | `docs/reviews/detector_review_2026-09-15.md` and `docs/reviews/detector-review-2026-09-15/` ⚠ **on the branch, not on `main`** |
| **Writing the document is how two defects in the instrument were found.** Both findings above came from assembling the explanation, not from testing the code. That is an argument for the document existing at all, and it belongs in the case for doing this again | argued, from two instances | this page |

### What the document draws on, and how current each piece is

| document | what it covers | state |
|---|---|---|
| [`detector_history.md`](../detector_history.md) | where each of the six came from — authorship against method priority, the radar lineage, what the interface2 commit prose actually means | the strongest piece; murderboarded more than once, current to 2026-09-14. ⚠ Read its revision blocks first |
| [`generator.md`](../generator.md) | the simulator — what it imitates and how well | murderboarded 2026-08-14 |
| [`benchmark_explainer.md`](../benchmark_explainer.md) | the bench in pictures, for a person | ⚠ **never reviewed**, and it argues from the flat background field, superseded 2026-09-06 |
| [`performance_table.md`](../performance_table.md) | the numbers, and its refusal to rank them | murderboarded 2026-08-30; ⚠ its first section's evidence is superseded, same flat field |
| [`simulation_plan.md`](../simulation_plan.md) | the design of the simulator and the training sets | a plan, explicitly not what was built |
| the operating-point rule | how a stored setting was chosen | **written down nowhere in prose** — it lives in [`tools/retune_operating_points.py`](../../tools/retune_operating_points.py)'s docstring and in [`bench.py`](../../src/bugarach/bench.py)'s `source` strings |

**Three of those argue from a background field this project has replaced**, headers added and numbers
never re-derived: [the todo](../todo/2026-09-08-three-documents-argue-from-the-flat-field.md). A
document assembled from them inherits it.

## Tried and dropped — do not re-propose without new evidence

- **A repo copy of the real-recording figures.** Refused by FOUNDATIONS §5, whose released-by-name
  exception is *"a list of one, not a category"*. The report links such a figure by name instead of
  embedding it.
- **Keeping the four neural networks in the main plain-language page.** Cut out onto their own page
  on Tony's instruction, and held back unreviewed. They are the other goal's subject
  ([`learned-model-family.md`](learned-model-family.md)).
- **Batching the plain-language review notes.** Tony asked for them applied as they arrive — *"start
  with that feedback for the next revision"* — so each note is filed with its diagnosis and fixed in
  the same turn rather than queued.

## Waiting on Tony

| decision | why it gates the goal | filed |
|---|---|---|
| **Whether the document shows the bake-off's selection rounds or the retune's figure.** The rounds come from the ungated path he called stale on 2026-08-28; the retune's figure is gated and current | It is the document's own account of how a setting was chosen, so it cannot show both | `HANDOFF-detector-optimization.md` on branch `detector-review-doc` ⚠ **not on `main`** |
| **The plain-language notes still in flight.** The loop is his to end | The page is finished when he stops sending notes | `docs/reviews/detector_review_plain_notes.md` ⚠ **not on `main`** |
| **The decisions in [`coded-detector-optimization.md`](coded-detector-optimization.md)** — binned SCE's threshold, locust's anchor, rate+context — each changes a number this document prints | A document published ahead of them prints a value that is about to move | that page |

## Open work a session can do without a ruling

1. **Merge `main` into the branch and regenerate.** The document's numbers predate locust's per-event
   widths, binned SCE's scoring and the retune of all six operating points.
2. **Add the overnight search result**, phrased as a measurement rather than an adoption.
3. **Murderboard it again before it goes out** — it is a document deliverable with figures, so
   CLAUDE.md requires it, and the last run was delivered unconverged with ten items open.
4. **Work the ten open items** from the run record rather than treating the round cap as a pass.
5. **Release the darkroom claim.** [`SESSIONS.md`](../SESSIONS.md) on `main` still reads **ACTIVE** on
   `bugarach/2026-09-15-detector-review/`. The release exists — on the unmerged branch. Until that
   branch lands, every session on every machine reads a folder held by a session that is gone.
6. **Re-derive the three flat-field documents** the review draws on, or say inside the document which
   of their claims it is not using.

## Where the work lives

| what | where |
|---|---|
| The builder, the template, and the shared mechanism figure | `tools/make_detector_review.py`, `tools/detector_review_template.html`, `tools/make_mechanism_figure.py` ⚠ **on branch `detector-review-doc`, not on `main`** |
| The plain-language builder | `tools/make_plain_detector_review.py`, rebuilt with `--from-review <the review folder> --stages page` ⚠ **not on `main`** |
| The murderboard record and all three rounds' role reports | `docs/reviews/detector_review_2026-09-15.md`, `docs/reviews/detector-review-2026-09-15/` ⚠ **not on `main`** |
| The live note-by-note state of the plain page | `docs/reviews/detector_review_plain_notes.md` ⚠ **not on `main`** — read it before touching the page |
| The built pages | `<darkroom>/bugarach/2026-09-15-detector-review/` and `<darkroom>/bugarach/2026-09-15-detector-review-plain/` — resolve with `bugarach.paths.darkroom()` |
| The session's own working notes, including what not to relearn | `HANDOFF-detector-review.md` on the branch ⚠ **not on `main`** |
| The argument about what optimization can honestly claim | `HANDOFF-detector-optimization.md` on the branch ⚠ **not on `main`** |
| The review process itself | [`doc_review_process.md`](../doc_review_process.md), and the vendored `/murderboard` skill |

## Keeping this page true

- **A result toward this goal updates this page in the same PR.** A decision moves from *Waiting on
  Tony* to *What is settled* with its date. A dropped approach moves to *Tried and dropped* with its
  reason.
- **A session working on this goal says so on its board claim** (`Goal: detector-review-document`) and
  names its branch `review/<slug>`. Branches stay short-lived and land on `main`; the page, not a
  branch, is what holds the goal together.
- **Every ⚠ branch-only marker above is a debt**, and this goal carries more of them than any other:
  the document, its builder, its review record and its release of a shared claim all sit on one
  unmerged branch. A session reading `main` sees an ACTIVE claim on an empty-looking folder and
  concludes the work was never done. That happened on 2026-09-16 and is why this page exists.
