---
status: done
filed: 2026-09-12
closed: 2026-09-12
---

# Literature deep dive: has anyone built a null by recombining units that were never recorded together?

> **Done 2026-09-12 — [reading log](../learned/recombination_nulls_reading_log.md).** Each of the four
> questions has at least two read sources, which is this todo's stop rule. In short:
> - **As a null: yes, widely.** It is the shuffle predictor, session permutation, pseudo-pairs and
>   inter-subject surrogates. The documented false positives share one cause, units of a record sharing a
>   state:
>   Brody 1999; Louis, Borgelt & Grün 2010 (24% at α = 1%); Ventura et al. 2005; Harris 2021; Burgess 2013.
> - **As negatives: yes, across recordings.** All seven studies that measured it found the model learned
>   recording identity, and each fixed it by keeping negatives within a recording. No one found uses real
>   units recombined across recordings as negatives for a coordination detector.
> - **Identity:** near ceiling at population level, weak for single units under a standard protocol.
> - **Exchangeability:** fails exactly when the tested contrast and a nuisance share the block structure
>   (Winkler 2015; Abney 2015), and "recorded together" is that block.
>
> **What it changes:** gate changes to the justification plan are in the reading log. The largest is that
> the plan's condition for reopening training negatives is **not met**.
>
> **Still open, and not this todo's:**
> - the papers in [`lit_needed.md`](../lit_needed.md) under the deep-dive heading;
> - whether to write to the Grün group (Tony's call);
> - the CICADA credit in `detectors/cicada.py`.
>
> The table below is kept as filed; the reading log's corrections section says which rows moved.

**Why this exists.** Tony's ROI-swap idea — replace ROIs in a recording with real trains from other
recordings, so coordination is destroyed while every train stays real — was written up and reviewed
three times and marked **not recommended as designed**
([proposal](../proposals/2026-09-12-the-roi-swap-null.md),
[record](../reviews/2026-09-12-the-roi-swap-null_2026-09-12.md)). That verdict was about the design and
this cohort. It was **not** a finding that the idea lacks precedent, and the search behind the
proposal's literature section was thin: four web searches and three shelf PDFs. Tony, 2026-09-12:
*"we need some evidence in our system that this is a valuable approach."* This search is half of that
evidence; [the justification plan](2026-09-12-evidence-before-more-effort-on-the-roi-swap.md) is the
other half, and its gates change depending on what this finds.

**What is established so far, and how strongly** — do not re-derive these, and do not upgrade them
without reading:

| claim | status |
|---|---|
| Recombining non-simultaneous trials is a conditional-inference null; its rejection means "all pairings are not equally likely", not "timing is precise" | **read** — Amarasingham, Harrison, Hatsopoulos & Geman 2012, `surrogates/amarasingham_2012_jitter_method.pdf` |
| The same paper shows shuffle-correction flags coordination "because of slow, common rate fluctuations alone" and recommends jitter for fine timescales | **read** — same paper |
| Stella, Bouss, Palm & Grün 2022 compare six surrogates and none is cross-session or cross-preparation | **read** — full-text search of `surrogates/stella_2022_comparing_surrogates.pdf` |
| Pipa et al. 2008 credit whole-train shifting to Grün et al. 1999 and cite König 1994 for the shift-predictor procedure | **read** — `surrogates/pipa_2008_neuroxidence.pdf` |
| The shift predictor goes back to Perkel, Gerstein & Moore 1967, Part II | **metadata only** — not held; open ask in `lit_needed.md` |
| Pooling neurons across sessions (pseudopopulations) removes noise correlations | **not read** — a search result and a reviewer's candidate citation (Cunningham & Yu 2014); `elsayed_cunningham_2017_byproduct.pdf` was checked and does **not** support it |
| Hyperscanning uses "pseudo-pairs" of people who never interacted as a routine null | **not read** — a reviewer's search result |
| No one has used cross-recording recombination as negatives for a self-supervised coordination detector | **unknown** — nothing found, and the likeliest fields were never searched |

## Four questions, in order of what they decide

- **Precedent as a null.** Has recombining units never recorded together — across trials, sessions,
  animals, subjects, slices — been used as the null for synchrony, coordination or assembly detection?
  Under what name? What failure modes were documented, and under what conditions does it give false
  positives?
- **Precedent as negatives.** Has such recombination been used to generate negatives for
  self-supervised, contrastive or discriminative learning of population structure — in neural,
  physiological, or any multichannel time-series data? What did the negatives teach the model that was
  not intended?
- **The identity confound.** How identifiable is session, animal or preparation identity from
  population activity? This is the ROI swap's largest objection, and multi-session modelling work has
  almost certainly measured it, whether or not it framed it that way.
- **Exchangeability.** What does a recombination null condition on, and what exchangeability does it
  assume? When is "units from different preparations are exchangeable" defensible?

## Where to look, with seeds

⚠ **Every seed marked *verify* is cited from memory or from a search snippet and has not been checked.**
Resolve the DOI and read the paper before using it; never paste a seed into a document.

**Check the shelf first** — `<darkroom>/bugarach/lit/`. Several shelved papers were never read for
this question:

- `coordination/molter_2018_assembly_benchmark.pdf`, `coordination/russo_2017_cad_multiscale_assemblies.pdf`,
  `coordination/romano_2017_promax_toolbox.pdf`, `coordination/malvache_2016_awake_reactivations.pdf` —
  for precedent as a null: which nulls do they use, and does any recombine across recordings?
- `surrogates/harrison_geman_2009_pattern_jitter.pdf`, `surrogates/amarasingham_2015_ambiguity_nonidentifiability.pdf`,
  `surrogates/elsayed_cunningham_2017_byproduct.pdf` — for exchangeability.
- `ml/gutmann_hyvarinen_2012_nce.pdf`, `ml/lopezpaz_oquab_2017_c2st.pdf` — for precedent as negatives
  and for exchangeability; both are marked unrecorded in the shelf README.
- CICADA, which `detectors/cicada.py` ports from the Cossart lab and which the surrogate thread left
  uncredited: which surrogate does it use?

**Spike-train surrogates — precedent as a null.**
- Perkel, Gerstein & Moore 1967, Part II — open ask.
- Aertsen, Gerstein et al. 1989, the joint peri-stimulus time histogram and its shuffle predictor —
  *verify*.
- **Brody 1999, "Correlations without synchrony", *Neural Computation*** — *verify*. From its title and
  the search snippet, it shows covariation in latency or excitability across trials producing
  shuffle-predictor peaks that are not synchrony. **That is the trial-level analogue of preparation
  identity, and may be the single most relevant paper on precedent as a null.**
- Grün et al. 1999, the multiple-shift method — open ask.
- Louis, Borgelt & Grün 2010, chapter 17 — open ask. The surrogate-screen handoff records an open copy
  on the G-Node advanced-course portal.
- Stella, Quaglio, Torre & Grün 2019, 3d-SPADE, and the INM-6 `SPADE_surrogates` harness, which
  accompanies a 2021 paper by Stella et al. — open ask.

**Pseudopopulations and noise correlations — precedent as a null, and the identity confound.**
- Cunningham & Yu 2014 — open ask.
- Averbeck, Latham & Pouget 2006, *Nat Rev Neurosci* — *verify*.
- The information-limiting-correlations paper found by search at
  `pmc.ncbi.nlm.nih.gov/articles/PMC7817840/` — read it, and resolve its authors.

**Self-supervised and multi-session models — precedent as negatives, and the identity confound.** The
field most likely to hold precedent as negatives, and never searched.
- CEBRA, Schneider, Lee & Mathis 2023, *Nature* — *verify*. Contrastive embeddings of neural data: what
  are its negatives, and does it report session leakage?
- MYOW, Azabou et al. 2021 — *verify*.
- Neural Data Transformers, LFADS, and multi-session pretraining such as POYO — *verify*. How do they
  handle session identity, and is session decodable from their embeddings? That is the identity
  confound, measured.
- Shortcut learning, Geirhos et al. 2020 — *verify* — for the general failure of negatives that differ
  from positives on a nuisance axis.

**Hyperscanning — precedent as a null.** Pseudo-pair and surrogate-dyad controls for inter-brain
synchrony. A reviewer named Burgess 2013, *Front Hum Neurosci* — *verify*. What critiques exist of what a
pseudo-pair null fails to control?

**EEG/MEG connectivity — precedent as a null, and exchangeability.** Surrogates built to control volume
conduction, for example the Springer chapter "Constructing surrogate data to control for artifacts of
volume conduction for functional connectivity measures" found by search — *verify*. ⚠ Four searches for
"chimeric surrogate" in connectivity found nothing; record that as a searched absence, not a proof.

**fMRI — precedent as a null, and the identity confound.** Null models for functional connectivity and
between-subject surrogates. Subject identity is reported to be decodable from resting-state
connectivity ("connectome fingerprinting" — *verify*), which would be the identity confound answered at
another scale.

**Ecology and genomics — exchangeability.** **Swap algorithms for presence-absence matrices** —
Gotelli's null-model work, *verify* — preserve row and column totals while scrambling co-occurrence.
That is structurally close to an ROI swap, and the field has argued for decades about what
fixed-marginal nulls wrongly flag. Permutation across individuals in genomics is the same idea.

## How to do it

- **Shelf first, then publisher routes.** `docs/INDEX.md` row 124 records what works: biomedcentral
  `/counter/pdf/<doi>.pdf`, Springer `/content/pdf/<doi>.pdf`, ane.pl. PMC returns a bot-check, and
  Europe PMC's `fullTextPDF` returns 0 bytes. A paper reachable only through PMC is a Tony ask, not a
  dead end.
- **Shelve what you fetch in the same change**, with a topic README entry saying what it was read for.
- **Trace back and forward.** Back until the citations stop — this repo has twice stopped one paper
  short (Gerstein before Date 1998; Pipa before Grün 1999). Forward to what the same authors did next.
- **Record every search and every field not searched.** An unsearched field is a residual, never an
  absence.
- **Correspondence.** Asking the Grün group whether a cross-session surrogate has been tried is the
  cheapest outstanding check, and **whether to write is Tony's call**. Any reply is cited, never quoted
  (CLAUDE.md, *Other people's words*).

## What done looks like

- **A reading log**, one row per paper: what it says on each of the four questions, the page or section,
  and whether the row was *read* or is *metadata only*.
- **An answer to each question** with its evidence strength, in the read / metadata / not-read
  vocabulary of the table above.
- **Consequences for the justification plan, stated as gate changes.** For example: if Brody 1999 shows
  shuffle nulls false-positive under trial-level covariation, the plan's simulated-ground-truth stage must
  add a slice-level covariation arm; if multi-session models report session identity as highly decodable,
  the plan's slice-identity stage should expect STOP.
- **Every unreachable paper** added to `lit_needed.md`.

**Stop when** each question has at least two read sources, or a recorded, exhausted search across every
field listed above, whichever comes first. If the synthesis becomes a document for anyone outside this
repo's sessions, it is a document deliverable and goes through `/murderboard` first.

**Not in scope:** the stopped surrogate screen's family-size decision, and PR #531.
