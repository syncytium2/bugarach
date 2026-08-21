---
status: open
filed: 2026-08-18
---

# Synfire order is a different question from assemblies, and it is the cheaper port

The assembly measurement asks **who** takes part in each coordinated event. cSPIKE's
SPIKE-order work asks **in what order** they fire — whether the same units lead and the
same units follow, event after event, summarised as a synfire indicator. These are not
the same property and a recording can have either without the other.

Three questions about the same coordinated events, and this project answers one and a
half of them:

| question | measure | here? |
|---|---|---|
| how much co-firing | SPIKE-synchronization | **yes** — `detectors/sync.py`, ported from cSPIKE and cross-validated to 1e-9 against MATLAB *and* PySpike |
| which cells, repeatedly | assembly membership | **yes** — `bugarach.assembly`, 2026-08-18 |
| in what order, repeatably | SPIKE-order / synfire | **no** |

## Why it is worth doing, and why it is cheap

**The assembly measurement is order-blind by construction.** It collapses each
coordinated cluster to a set of participating ROIs and discards the onsets — even though
`assess._clusters` already gathers each participant's onset and computes their spread.
Any leader/follower structure in this corpus is untouched and has never been looked for.

**We already ported the sibling measure.** `detectors/sync.py` is a cSPIKE port validated
to 1e-9. SPIKE-order is the same lab, the same suite, and the same input representation
this project already produces — plausibly the cheapest published-method comparison
available, and cheaper than the PCA/ICA port
([`2026-08-17-run-a-literature-method-on-our-corpus.md`](2026-08-17-run-a-literature-method-on-our-corpus.md))
that has been the assumed candidate.

**And the benchmark cannot reward it either.** The generator plants each event's onsets
as jitter around a common time with no systematic order, so a synfire measure scores
nothing on our corpus — the same structural gap the assembly work found, on a second
axis. Whatever is decided about planting assemblies in the generator should decide about
planting order at the same time, or the second port hits the same wall as the first.

## What must not happen

The same mistake the assembly work nearly shipped: reporting a synfire score against a
corpus built to contain no order, and reading the zero as a fact about the method. See
[`2026-08-18-do-real-slices-have-recurring-assemblies.md`](2026-08-18-do-real-slices-have-recurring-assemblies.md).

## Papers — fetched 2026-08-19, in the library

Kreuz publishes direct links; all three came from his own site, and the two PDFs are in
`<dropbox>/01-lit/`.

- **Kreuz T, Satuvuori E, Pofahl M, Mulansky M (2017). "Leaders and followers:
  quantifying consistency in spatio-temporal propagation patterns." *New J. Phys.* 19,
  043028.** doi:10.1088/1367-2630/aa68c3 — open access.
  → `01-lit/kreuz 2017 leaders and followers spike-order njp.pdf`.
  This is the SPIKE-order / Spike Train Order source. Verified by opening the PDF: it
  carries the title, both method names and the article number.
- **Mulansky M, Kreuz T (2016). "PySpike — a Python library for analyzing spike train
  synchrony." *SoftwareX* 5, 183.** → `01-lit/mulansky kreuz 2016 pyspike softwarex.pdf`
  (arXiv 1603.03293v2). Already the reference behind the ported synchronization measure.
- **Kreuz T, Satuvuori E, Mulansky M (2017). "SPIKE-order." *Scholarpedia* 12(7):42441**
  — free at <http://www.scholarpedia.org/article/SPIKE-order>. Not downloaded; this is
  the readable overview and the place the **Synfire Indicator** is described.

⚠ **One thing to confirm when reading.** The Synfire Indicator is defined in the
Scholarpedia article; a crude text extraction of the *New J. Phys.* PDF did not surface
the word, which may be an artefact of the extraction rather than the paper. Establish
from the PDF itself which of the two defines the indicator before citing either for it.

**cSPIKE already implements it.** From Kreuz's own cSPIKE page: *"Version 1.3 also
contains the complementary directional method SPIKE-order and Spike Train Order."*
Download: <https://drive.google.com/file/d/1UQrsggj9MKXJqfVYKFuXOo9gws8XXOFE/view>.
So the port is against a MATLAB reference we can run, exactly as the
SPIKE-synchronization port was — which is the argument for it being the cheapest
literature comparison available.

