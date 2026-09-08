# Attribution corrections — the interface2 memo is wrong about the lab

**2026-08-24 · from the murderboard estate · concerns
`docs/exports/2026-08-24_reply_to_interface2_attribution.md` and the memo it replies to**

> **Amended 2026-08-28, before merge.** Items 1–7 are unchanged. A section applying two
> role-2 rules that did not exist when the reviews ran — *trace forward*, *ask what the
> humans hold* — has been added near the end, together with the five residual `⚠` it
> produced. Read that section before quoting this one as settled.

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

## Two rules this review did not have — applied 2026-08-28, before merge

The reviews behind items 1–7 ran against a vendored `doc_review_process.md` that
**predated the re-vendor in #307**. That re-vendor added two rules to role 2, and
both bear on this memo more than on anything else in the estate:

> **Trace FORWARD as well as backward.** For any third-party tool, measure or
> library the deliverable builds on, *"the authors' own later applied papers are a
> required search target, not an optional field — read the tool's publication
> page, not only the paper it was introduced in."*

> **Ask what the humans hold.** Before reporting a claim unattributed or prior art
> not found, *"ask the people involved whether anyone has already asked
> someone."* **"Nobody was asked" is a residual `⚠`**, recorded like an unsearched
> field.

Merging without applying them would ship a review that skipped them silently.
Applied below. **Nothing in items 1–7 changes; two of them get reclassified, and
three gaps that were invisible become named.**

### Forward-tracing, per tool this project wraps

| tool / measure | forward target the rule requires | status |
| --- | --- | --- |
| **CICADA** (Cossart lab) | the tool's own publication page, and the lab's later applied papers using it | **not consulted ⚠** — this memo cites the Zenodo release and GitLab `master` only. Item 3 establishes the release lacks the code; nobody has looked at what the authors published *with* it |
| **cSPIKE / SPIKE-synchronization** (Kreuz) | `thomaskreuz.org/publications/journal-articles` refs 45–47 | **named, none read ⚠** — Cecchini 2022 (PLoS Comput Biol, SM1), Kreuz 2024 (J Neurosci Methods), Mariani (J Neurosci Methods). Item 5 has them |
| **PySpike** | the same author's applied work | **not searched ⚠** — the project has an open finding against this library (`docs/kreuz_note.md`, the inert `max_tau`) and has never asked what its authors did with it downstream |
| **the SCE rule** (Cossart 2003 → Yuste lineage) | later restatements | **done** — Malvache 2016 / Modol 2020 / Dard 2022 are named as restatements in item 1 |

**The reclassification that matters.** Item 5 marks the Kreuz papers *"UNVERIFIED
— do not rewrite the attribution on this alone."* Under the forward-tracing rule
they are not an optional deepening; **they are the required search target for
exactly the claim the memo is adjudicating** — whether this project's detection
layer around someone else's synchrony measure is novel. The memo's own §5 already
found one concrete design difference (Kreuz requires an amplitude condition;
`sync.py` gates on synchrony alone). That difference is an argument for reading
them, not a substitute for it.

Same for item 6: `rate_detect | ours, as far as we know` rests on a search of
nothing. Kreuz volunteered the lead (Mainen & Sejnowski, *Science* 1995, PSTH
thresholding). **Unsearched is a residual `⚠`, not an absence of prior art** — the
rule says so in terms, and the memo's row should not be read as clearance.

### Who has actually been asked

| party | asked? | evidence |
| --- | --- | --- |
| **Thomas Kreuz** — author of the wrapped measure | **yes** | correspondence dated **2026-04-23**, quoted in items 5–7. Quoted and dated, as the rule requires |
| Kreuz, on the PySpike `max_tau` defect | **drafted, not sent** | `docs/kreuz_note.md` is paste-ready and has been waiting on Tony since 2026-08-11 |
| **The Cossart lab / CICADA authors** | **no ⚠** | grepped the estate: no email, no issue, no exchange. The memo makes four claims about their code and their release, including that a published DOI ships without the method (item 3) — and nobody has asked them |
| **interface2**, on the memo's own claims | yes | the reply shipped, `docs/exports/2026-08-24_reply_to_interface2_attribution.md` |

**The cheapest open item in this document is one email to the Cossart lab.** It
would settle item 3 (is the missing `sce_stats_utils.py` in v1.0.3 deliberate or
a packaging slip?) and item 4 (do they consider `get_sce_threshold` composable
with the windowed sum, or is the pairing ours alone?) — two questions this memo
answers by reading their source and inferring intent. Item 4's verdict in
particular, *"upstream never composes those two functions"*, is an inference
about what the authors meant, made without asking them.

### Residual ⚠ after applying both rules

1. CICADA's publication page and the lab's applied papers — **not consulted**.
2. Cecchini 2022 SM1, Kreuz 2024, Mariani — **named, unread**; required, not optional.
3. Mainen & Sejnowski 1995 and the PSTH-threshold literature — **unsearched**;
   `rate_detect`'s "ours" is unsupported, not cleared.
4. PySpike's authors' downstream work — **unsearched**.
5. **The Cossart lab has never been asked anything**, while this memo makes four
   claims about their artifacts and one about their intent.

None of these blocks the four MUST-FIX items: 1–4 are verified from primary
sources and stand. They bound what the memo may be quoted as having established.

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

**And the process has since learned that lesson twice over.** The observation in the
paragraph above — that correspondence beat every literature search — is now a rule in
`doc_review_process.md`, alongside a second one about tracing a wrapped tool's authors
*forward*. Neither existed when these reviews ran. Applying them on 2026-08-28, before
merge, changed none of items 1–7 and produced **five named residual `⚠`** where there had
been silence, the largest being that **nobody has ever asked the Cossart lab anything**
while this memo makes four claims about their artifacts and one about their intent. See
*"Two rules this review did not have"* above.

That is the shape of the thing: this document's own closing caveat became a rule, and the
rule immediately found more that the document had missed. It should be read as bounded by
that section, not as a clearance.
