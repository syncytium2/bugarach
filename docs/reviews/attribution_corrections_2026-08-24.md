# Attribution corrections — the interface2 memo is wrong about the lab

**2026-08-24 · from the murderboard estate · concerns
`docs/exports/2026-08-24_reply_to_interface2_attribution.md` and the memo it replies to**

The method-attribution memo you received from interface2
(`docs/exports/2026-08-21_bugarach_method_attribution.md`, branch `coord-attribution`) told you
to credit "the Cossart-lab SCE rule" and to cite Dard 2022. **Do not put that in the UI.** It
credits the wrong laboratory and the wrong decade.

Every item below carries its verification status. Act on the VERIFIED ones; read before acting
on the rest.

---

## MUST FIX before anything ships

### 1. The SCE rule is a **Yuste-lab** method from 2003, not a Cossart-lab method from the 2020s

> **Cossart R, Aronov D, Yuste R (2003).** Attractor dynamics of network UP states in the
> neocortex. *Nature* **423**(6937):283–288. doi:10.1038/nature01614 · PMID 12748641

Its Methods contain the rule itself — interval reshuffling, 1,000×, threshold = the co-active
cell count exceeded in only 5% of surrogate histograms. It builds on **Mao BQ, Hamzei-Sichani F,
Aronov D, Froemke RC, Yuste R (2001)**, *Neuron* **32**(5):883–898, PMID 11738033.

On the 2003 paper Rosa Cossart is **first** author at *Department of Biological Sciences,
Columbia University* and **Rafael Yuste is last author**. She was a postdoc in Yuste's lab and
carried the method to Marseille. The lineage runs **Yuste → Cossart**, so the memo's citation is
both ~19 years late and one laboratory upstream.

Cite Cossart 2003 (with Mao 2001) as the origin; Malvache 2016 / Modol 2020 / Dard 2022 are
restatements.

**Status: VERIFIED.** Three independent blind reviews reached this separately via PubMed;
affiliation and author order checked directly against the record.

### 2. The "event-time merge rule" is published — it is not an interface2 adaptation

The memo lists it among *"our adaptations."* It is in the published method:

- Dard 2022, Methods: *"Peak of synchrony above this threshold **separated by at least five
  imaging frames (500 ms)** was defined as SCE frames."* — the sentence immediately after the
  passage the memo block-quotes, cut at exactly that point.
- Modol 2020: the same step at ≥7 frames.
- CICADA implements it as `find_peaks(..., distance=sce_min_distance)`.

Thomas Kreuz independently reports doing the same in his own work (see §5).

**Status: VERIFIED** for Dard/Modol/CICADA — quotes read against the full texts.

### 3. The CICADA citation points at a release that does not contain the code

`cicada-1.0.3.tar.gz` from doi:10.5281/zenodo.10041434 was downloaded and listed in full: **no
`sce_stats_utils.py`, no `get_sce_threshold`, no `detect_sce`.** They exist only on GitLab
`master`. Dard 2022 itself pins the software properly, by Software Heritage revision
`swh:1:rev:2ef0c25d7da5b69849c663ed56a0033cfe8488ca`.

Cite the SWH revision or a commit SHA alongside the DOI. A bare v1.0.3 citation points at an
artifact lacking the method.

**Status: VERIFIED.** Two independent reviews downloaded and enumerated the archive.

### 4. The memo's "quirk" claim is false about upstream, and it matters for your port

The memo says the port matches CICADA *"function for function, including the quirk that the null
is built from single-frame sums while detection uses the windowed sum."*

**Upstream never composes those two functions.** `get_sce_threshold` has no caller in
`sce_stats_utils.py`; the only consumer of the surrogate threshold is the plugin
`cicada_sce_description_analysis.py`, which computes `np.sum(raster_dur, axis=0)` — **per-frame
on both sides**. The mismatch is created by pairing two functions CICADA keeps apart.

Direction matters: the windowed OR-sum is pointwise ≥ the single-frame sum, so the threshold is
**too low → permissive**, inflating detections. If your port inherited that pairing, it inherits
the bias.

**Status: VERIFIED** from source by two independent reviews.

---

## READ BEFORE ACTING — from correspondence, papers not yet read

### 5. The "detection layer is ours" claim for spike-sync needs revisiting

Thomas Kreuz — author of the measure you wrapped — describes, in correspondence dated
**2026-04-23**, doing the same class of thing in his own published work:

> we combined the SPIKE-synchronization approach with a **thresholding of the mean calcium
> signal** (higher than 1.7 standard deviations from the mean, **both conditions had to be
> satisfied**). We also set a **threshold for maximum allowed gap for spikes of the same event,
> in order to avoid fragmented events.**

Papers he names (refs 45–47 at thomaskreuz.org/publications/journal-articles):

- **Cecchini et al.**, *PLoS Comput Biol* 2022 — see **SM1**
- **Kreuz et al.**, *J Neurosci Methods* 2024
- **Mariani et al.**, *J Neurosci Methods* — auditory follow-up, adds postprocessing ensuring no
  event contains more than one spike from the same pixel

The memo's claim that *"cSPIKE provides a synchrony measure, not a detector"* is true of the
**toolbox** and potentially misleading about the **literature**.

**Status: UNVERIFIED — do not rewrite the attribution on this alone.** Read Cecchini 2022 SM1
first and decide whether the construction is the same. It may not be.

**One concrete difference already visible:** Kreuz requires an **amplitude** condition
(mean calcium > 1.7 SD) *in addition to* synchrony. `sync.py` gates on the binned **C profile**
via `peak_gate` (threshold + prominence) — a synchrony-only gate. That is a real design
difference worth stating explicitly in whatever you publish, in either direction.

### 6. `rate_detect` — a prior-art lead you have not searched

> Other groups often use some kind of thresholding of the PSTH, see **Mainen and Sejnowski,
> Science 1995** for what might be the original use of that.
> — Kreuz, same correspondence

Relevant to the memo's `rate_detect | **ours**, as far as we know` row, which several reviewers
independently flagged as a claim asserted without the search that would test it.

**Status: UNVERIFIED — not read.**

---

## NO ACTION NEEDED — reported because it was checked

### 7. You are already using the right profile

Kreuz recommends **profile C (symmetric)** for global event identification, because
identification should not depend on order — *"If you use E you would only identify events that
follow the predominant order."*

`src/bugarach/detectors/sync.py` computes the adaptive SPIKE-synchronization profile **C** and
thresholds it. **No change required.** Recorded so nobody re-opens it.

---

## Provenance, and the honest caveat

Items 1–4 came from **two blind murderboard runs** on the memo as it stood before correction
(interface2 `16c0e362^`), run independently and with the known failure withheld. Both caught the
wrong-lab attribution; a third delivery of one run caught it again. That defect is now 3/3.

**Items 5–7 were missed by every one of those runs.** They came from an email Kreuz sent
**2026-04-23 — four months before the memo was written.** The evidence existed in-house the
whole time, and no amount of literature searching surfaced it, because the source was
correspondence rather than a paper.

**This list is not exhaustive.** It is what two blind reviews and one email produced. The reviews
found ~50 further defects in the memo — most of them interface2's to fix, not yours; the four
above are the ones that would change what *you* publish. Nothing here is a correctness proof, and
the one class of finding that did *not* come from the process is the class the process is
supposed to be best at.
