---
status: superseded
filed: 2026-08-21
superseded: 2026-08-24
---

> **Superseded 2026-08-24 — every row here has been closed, and not the way this
> file predicted.** interface2 audited all six and none survived as ours. The SCE
> origin it sends you to fetch, Malvache 2016, is not the root: the root is
> **Cossart, Aronov & Yuste 2003**, which credits Mao 2001, which nobody has
> reached. The RateDetect row it calls "priority unexamined" is cell-averaging
> CFAR, 1968. And the Cotterill body-read it puts first as the cheapest check is
> no longer the cheapest anything. Read
> [the methods are not ours](2026-08-24-the-methods-are-not-ours-and-the-app-says-otherwise.md)
> instead. What still holds is this file's opening distinction — between who wrote
> the code and whose idea the method is — which is why it is kept rather than
> deleted.

# Which detector origins are settled, and which are only assumed

Tony, 2026-08-21, having asked the MATLAB side for SCE's origin story: *"is there
any doubt about the others?"*

**Two different claims get conflated here, and only one of them is settled.**

1. **Who wrote the code.** Settled for all six. Not in doubt anywhere.
2. **Whose idea the method is.** Settled for **one**. Unexamined for four.
   Actively known to be unsettled for one — SCE, which is the one Tony asked
   about, correctly.

The distinction only matters at the two moments it always matters: app copy, and
a manuscript.

## Detector by detector

### CICADA — settled, no doubt
Cossart lab, `cossartlab/cicada`, MIT, upstream copyright carried in the module,
citation in the README's table. Nothing to establish.

### SCE — the real doubt, and MATLAB probably cannot settle it

Two independent findings in this tree already say so.

**The canonical rule reached us second-hand.** From the literature shelf's own
gaps section (`<darkroom>/bugarach/lit/coordination/README.md`):

> *The primary source for the canonical SCE rule is still missing. Malvache et
> al. 2016 (Science) is not open access and was not retrieved; the "onsets within
> 250 ms exceeding 3 SD over 1000 shuffles, minimum 5 cells" formulation reached
> this survey through a secondary description. **Get the primary before quoting
> it.***

**And the construction demonstrably exists elsewhere.** The deep dive found it
inside Mölter's assembly benchmark as a *precondition* rather than a result:
binarise per cell, count coactive cells per frame, keep frames above the 95th
percentile (SVD: 99th) of a per-cell permutation null — recorded there in terms
as *"that is our `sce_detect` / CICADA construction"*.

So SCE's shape appears in at least two other places. **interface2 can say what
interface2 did; it cannot say whether Malvache got there first.** The document
that settles this is Malvache et al. 2016, and nobody here has read it — it is
*Science*, not open access, and the murderboard's `fetch_paper.py` is
deliberately not vendored in this repo. **Fetch by hand.**

Tony's own framing — *"derived from ideas in cicada, but essentially ours"* — is
probably the honest landing place, and it is a lineage claim rather than an
independence claim.

### SPIKE-synch — authorship settled, novelty never claimed
The synchrony **profile** is the Kreuz lab's, cited, BSD, and the README's table
already says "semantics ported". The **detector run on that series** is ours.
Worth knowing before anyone writes it up: dual-threshold hysteresis detection is
ordinary signal-processing practice, so this is ours as an *implementation*
without being a novel method. No doubt; no claim to defend either.

### RateDetect — authorship not in doubt, priority unexamined
Nothing contests that it was written here. But *"threshold the pooled population
rate against a rolling local context"* is a common construction, and Tony's own
caveat — *"unless there's something in the literature with the same name"* — is
the right instinct.

**Cheapest check in the whole list:** `cotterill_2016_burst_detector_comparison.pdf`
is already on the shelf and is a **comparison of burst detectors**, which is
precisely where a rate-threshold method would appear. Its read status is
*"abstract and methods opening read; body not read."* Reading the body is an
hour and needs no fetching.

### LoCo and CoactDetect — authorship not in doubt, and the distinctive part is untested
Circular-shift surrogates over distinct-ROI coactivity are standard — this repo's
own assessor uses them, which is the point rather than a coincidence. What would
be distinctive is the **rate-local rolling null**: LoCo's percentile envelope
rebuilt at anchors from a half-context window, CoactDetect's per-bin test against
a null built inside a rolling window centred on that bin.

Nothing in the tree examines whether that construction is published. No candidate
paper has been identified, so unlike SCE and RateDetect this is a **search**
rather than a fetch, and it is the one where the answer is genuinely unknown
rather than merely unretrieved.

## What this changes about what may be said

Nothing yet, and that is the useful part: **no current claim depends on any of
this**. The scoreboard's rules already forbid "competes with state-of-the-art",
`bakeoff.md` reports a tie rather than a win, and
`2026-08-17-run-a-literature-method-on-our-recordings.md` records that nothing from
the literature has been run here at all — so the positioning is already argued
from absence rather than from priority.

The exposure is **future**: a manuscript or an app sentence that says "our SCE"
or "we developed" without this settled. Establishing it costs one paper fetch,
one body read, and one search — in that order of cheapness.

## Order of work, cheapest first

1. **Read the Cotterill 2016 body.** Already on the shelf. Settles or complicates
   RateDetect. An hour.
2. **Fetch Malvache et al. 2016 by hand.** *Science*, not OA. Settles SCE, which
   is the one actually being asked about.
3. **Search for a rate-local surrogate-null coactivity detector.** Open-ended,
   and the only one where "nobody has done this" is still live.
