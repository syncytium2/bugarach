# Recombination nulls — reading log

**What this is.** The literature deep dive filed in
[`todo/2026-09-12-literature-deep-dive-on-recombination-nulls.md`](../todo/2026-09-12-literature-deep-dive-on-recombination-nulls.md),
done 2026-09-12. It asks whether anyone has built a null — or training negatives — by recombining units
that were never recorded together, which is what the ROI swap does
([proposal](../proposals/2026-09-12-the-roi-swap-null.md),
[plan](../todo/2026-09-12-evidence-before-more-effort-on-the-roi-swap.md)).

**How it was done.** Six readers ran in parallel, one per field. Each resolved every identifier from
Crossref, OpenAlex, PubMed or Europe PMC (none from memory), fetched full text, and read the relevant
sections. Every row below says whether it was **read** (full text of the relevant sections), **abstract
only**, or **metadata only**. The PDFs are on the shelf at `<darkroom>/bugarach/lit/`: spike-train
ancestors in `surrogates/`, calcium-imaging detectors in `coordination/`, learning with negatives in `ml/`,
and pseudopopulations, hyperscanning, fMRI, ecology and genomics in the new `recombination/`. Each folder's
README has a row per file. Papers with no publisher PDF are in [`lit_needed.md`](../lit_needed.md).

**Status: working material for this repo's sessions, not murderboarded.** If any of it goes into a
document for outside readers, that document goes through `/murderboard` first. Page numbers are the
readers' and have not been re-checked by a second pass.

---

## The answers

### Has recombination been used as a null? Yes, widely — and where a false positive is documented, it has the same cause

**Evidence: read, many sources.** The names are the **shuffle predictor** or **shuffle corrector** and the
**shift predictor** (Perkel, Gerstein & Moore 1967, p. 436; Gerstein & Perkel 1972, pp. 463–464), **trial
shuffling** (Louis, Borgelt & Grün 2010; Grün 2009), **session permutation** (Harris 2021), **pseudo-pairs**
and **surrogate dyads** (Burgess 2013; Holroyd 2022), **inter-subject surrogates** (Iatsenko et al. 2013;
Ticcinelli et al. 2017), **participant shuffling** (Moulder et al. 2018) and **pseudopopulations**
(Meyers 2013). "Chimeric surrogate" found nothing, again.

**The documented false positive is the ROI swap's largest objection, one level down.** When the units of one
trial, session or person share a state that the recombination breaks, the null rejects with no
coordination present:

| field | the shared state | what was measured | source |
|---|---|---|---|
| spike trains | per-trial excitability or response latency | shuffle-corrected peaks with no synchrony; the covariogram integral equals the spike-count covariance | Brody 1999a, eq. 3.6 and rules of thumb p. 1548 — read |
| spike trains | rate profiles covarying across trials | trial shuffling **24% false positives at α = 1%** | Louis, Borgelt & Grün 2010, Fig. 17.6, p. 377 — read |
| spike trains | shared excitability in a real V1 pair | synchrony at p < 10⁻⁵ attributed **entirely** to excitability once modelled | Ventura, Cai & Kass 2005b, pp. 2935–2937 — read |
| decoding | a subject's decline across sequential sessions; different strategies across subjects | named as what breaks session permutation | Harris 2021, Methods — read (preprint) |
| decoding | a subject-level offset shared by its neurons | false-positive rates about 46–96% | Saravanan, Berman & Sober 2020, §3.1 — read (preprint) |
| hyperscanning | a condition that changes each person's own rhythmicity | spurious hyper-connections in ~20% (theta) and 22% (alpha) of connections under family-wise control — "not Type-1 errors" | Burgess 2013, p. 13 — read |
| ecology | site heterogeneity in species richness | 188 of 218 significant datasets stayed significant after everything except richness variation was randomised | Fayle 2020, p. 16 — read (preprint) |

**The converse failure is documented too.** Structure locked to a common clock — a stimulus, a task, a
protocol — survives recombination, so the null keeps it and cannot see it (Amarasingham et al. 2012, §2.6;
Simony et al. 2016; Zamm et al. 2024). For slices: bleaching from time zero and start-up transients would
be carried by donors into the null.

**What a rejection means.** Recombination tests that **all pairings are equally likely** (Amarasingham et
al. 2012, p. 521), which bundles independence of units with exchangeability of the records. With a hidden
variable **common** to the units of a record, rejection is correct about global dependence and says
nothing about synchrony, and no distribution-free test of conditional independence exists (Albert et al.
2016, §5 — read).

**Closest precedents to the ROI swap itself** — all read:
- **Louis, Gerstein, Grün & Diesmann 2010**, *Front Comput Neurosci* 4:127 (pp. 9–10; already shelved as
  `surrogates/louis_2010_operational_time_dither.pdf`), paired two V1 neurons from **different sessions** as a known
  negative. Simple dithers still found significant coincidences, because both had stimulus-locked rate
  transients.
- **Harris 2021** is the only cross-session **significance** null found. It needs at least 5 sessions and
  statistically independent sessions recorded under identical conditions.
- **Kingsbury et al. 2019** used **calcium imaging** in mouse dmPFC with partners from separate sessions,
  but matched the epochs on behaviour rather than swapping freely.
- **Moulder et al. 2018** ran participant shuffling (swap-type) against data sliding (circular-shift-type)
  on the same real data. Participant shuffling was rejected more often.

**None of the calcium-imaging assembly or event detectors read uses a cross-recording null.** Mölter 2018,
Russo & Durstewitz 2017, Romano 2015/2017, Peyrache 2010 and CICADA all stay inside one recording. Malvache
2016's supplement, where its null is, was not obtained.

### Has recombination been used for negatives? Across recordings, yes — and every group that measured it found the model learned recording identity

**Evidence: read, seven independent groups.**

| study | negatives or classes drawn across | what the model learned | fix |
|---|---|---|---|
| Hyvärinen & Morioka 2016, TCL (MEG) | sessions and subjects | "tends to mainly learn" inter-subject and inter-session differences (p. 7) | a separate output layer per session |
| van den Oord, Li & Vinyals 2018, CPC (speech) | other sequences, mixed speakers | speaker linearly decodable at 97.4% of 251; **other-sequence mixed-speaker negatives — the ROI swap's structure — gave the worst phone accuracy, 57.3% against 64.6–65.5%** (Table 2, p. 5) | same-speaker negatives, later the default (Rivière et al. 2020) |
| Cheng et al. 2020 (EEG, ECG) | subjects | linear probe identifies the subject at **88.6%**; random encoder 55.9% (Table 2, p. 6) | same-subject negatives brought it to 68.4%; an adversary to 73.0% |
| Banville et al. 2021 (clinical EEG) | recordings | embeddings clustered by channel count and measurement date (p. 18, Fig. 6) | suggested: negatives within cohort |
| Arora et al. 2025, NuCLR (Neuropixels, 2-photon) | probe insertions | neurons clustered by probe identity (p. 5); **on small datasets, including a 2-photon calcium set, still by subject or session** (p. 20) | negatives within one insertion |
| Yèche et al. 2021, NCL (ICU) | patients | between-patient variance exceeds within-patient (p. 2) | neighbourhood within one patient |
| Zhu et al. 2026, CONCORD (single cell) | datasets | latent space separates by dataset (p. 2) | a dataset-aware sampler |

⚠ **Not found:** real units recombined across recordings as negatives for a *coordination* detector. The
nearest training task is the **Population Transformer** (Chau et al. 2025, p. 4): replace 10% of channels
with a random channel at a random time, **always within one subject**. It does not test whether swapped
channels can be spotted from single-channel statistics. Jude et al. 2022 replaces a train with a
rate-matched **synthetic** neuron (p. 4).

⚠ **Permutation-contrastive learning is not a precedent**, although the todo seeded it as one. Hyvärinen &
Morioka 2017 pair the whole vector x(t) with the whole vector x(t*) (p. 4, eq. 11), which keeps cross-channel
structure. It is the analogue of a whole-population time shift.

### How identifiable is the recording? Near ceiling at population level; weak for single units under a standard protocol

**Evidence: read.**
- **Population or session level, near ceiling:** subject from contrastive EEG features, 88.6% (Cheng); speaker
  97.4% (CPC); hospital system from a chest X-ray, 99.95–99.98% (Zech et al. 2018); a person from 30 s of MEG,
  95–96% of 158, and above chance even from empty-room hardware noise (da Silva Castanheira et al. 2021);
  subject from resting fMRI connectivity, 93–99%, with per-node variance alone at 48–87% (Finn et al. 2015,
  Europe PMC text). **Calcium imaging:** CalM's per-session embeddings classify the mouse at 0.930 (Xu et al.
  2026, App. F, Table 20).
- **Single units, weak:** CalM's per-**neuron** embeddings classify the mouse at 0.224, against about 0.125
  chance for 8 mice (chance is this log's arithmetic). The International Brain Laboratory 2025 could not
  decode lab identity from per-neuron features under its standardized protocol (Fig. 7, p. 18).
- **Dataset-level calcium signatures exist**: per-spike calcium kernels "varied substantially across
  datasets, even for data from the same indicator" (Rupprecht et al. 2021, CASCADE, already shelved).
- Abstract only: EEG foundation models carry subject variance at 13–89× a random baseline (Lin, Wu & Jung
  2026) and dataset membership at AUROC 1.000 (Zare et al. 2026).

**Not found:** anyone measuring whether a single calcium-imaging ROI, or a pair of population windows, can
be traced to its slice. That is the plan's slice-identity stage, and it would be new.

### When are units from different preparations exchangeable? Only when nothing they share differs between preparations — which is the thing in question

**Evidence: read.**
- **Definition.** Exchangeable means the joint distribution is unchanged by the permutation; equal dependence
  among all units is allowed (Winkler et al. 2014, p. 383; Abney 2015, Appendix). Operationally, a believer in
  the null "could not pick out the real spike train from a lineup" (Amarasingham et al. 2012, §2.4). **So a
  classifier that picks swapped ROIs out of a recording is, by definition, evidence against the swap's
  exchangeability.**
- **The sharpest formal result.** Free permutation fails exactly when the data and the tested contrast carry
  the same dependence structure (Winkler et al. 2015, Europe PMC text; Abney 2015). For the ROI swap,
  "recorded together or not" **is** the preparation block by construction, so any within-preparation
  similarity that is not coordination reaches significance.
- **Where it holds.** Centred statistics whose expectation is built per record — the sum of per-record
  products, not the product of averages (Grün, Diesmann & Aertsen 2010, eq. 10.11) — and either no common
  record-level variable, or one modelled explicitly (Brody 1999b's subtraction; Ventura et al. 2005b). With
  unshared per-unit variation the centred test keeps its level (Albert et al. 2016, Fig. 8C).
- **How practitioners get it.** Every pseudopopulation read conditions on a shared clock — stimulus,
  condition, location bin (Kafashan et al. 2021, p. 14; Meyers 2013, pp. 5–6; Courellis et al. 2024).
  Spontaneous slice activity has no shared clock, so the ROI swap is the unconditional version. Hyperscanning
  stratifies donors by condition and counterbalance (Reindl et al. 2021; Moerel et al. 2025, which dropped 6
  real pairs with no matched donor).
- **The trade-off ecology settled.** Too few constraints flag known heterogeneity as association (Gotelli
  2000, Table 4: nulls that do not fix row totals falsely rejected random matrices 49–70% of the time). Too
  many hide the process — the **Narcissus effect**, sampling the null from a pool the process already shaped
  (Colwell & Winkler 1984, pp. 353–355). A donor pool drawn from coordinated recordings is a Narcissus pool.
  At scale every null is rejected, so effect size carries the information (Gotelli & Ulrich 2011, p. 1338).

---

## What this changes in the plan

These are gate changes to
[`todo/2026-09-12-evidence-before-more-effort-on-the-roi-swap.md`](../todo/2026-09-12-evidence-before-more-effort-on-the-roi-swap.md),
by stage. None requires new compute to decide.

**The decision the plan earns — training negatives.** The plan reopens the detector only if "the literature
deep dive has not surfaced a documented failure that applies". **It has.** Cross-recording negatives taught
recording identity in every study that measured it, including one on calcium imaging, and every fix kept
negatives inside a recording — which removes what makes the swap a swap. **Read this condition as not met.**
The significance-null route is unaffected, and is where the precedent is.

**Slice identity.**
- **Expect STOP at the global matching level.** Population-level identity is near ceiling wherever it has been
  measured, and the stage uses pooled per-window features, which are population-level. That keeps the plan's
  instrument check valid: the global level *should* read above 0.60.
- **Add a single-train lineup test.** Using features of one ROI's own train only — rate, interval
  statistics, event width, drift, zero-event status — classify native ROIs against swapped-in donor ROIs within
  a recording. This is Amarasingham's exchangeability definition made operational, and it is what the swap
  actually needs. Single-unit identity is weak in the literature (CalM per-neuron, IBL), so this test can
  plausibly pass where the window-pair test fails. **Proposed gate:** the swap is admissible as a
  significance null only at a donor-matching level where this classifier's upper 95% bound over mice is below
  0.60.

**Simulated ground truth.**
- **Split the slice-level covariation arm into the three mechanisms the literature separates**, each with
  its own declared strength and a sweep:
  - **shared gain within a recording**, one multiplicative rate factor for all its ROIs, varying across
    recordings. This is Brody's excitability covariation. Prediction: the swap **rejects**, circular shift
    holds. Sweep it as Louis Fig. 17.5c did, to find where the swap breaks.
  - **donor marginal mismatch with unshared gains**, where recordings differ but each ROI's scale is
    independent. This is Albert's centering control. A correctly centred swap must hold α here; if it does
    not, the defect is centering, not identity.
  - **protocol-locked structure**, the same time course at the same offset in every recording. Prediction:
    the swap keeps it and **misses** it, circular shift destroys it. **Declare before running whether this
    counts as coordination.**
- ⚠ **The shared-rate-increase arm's positive control may be unable to bite for the swap by design.**
  Amarasingham et al. 2012 show shuffle-type nulls flag shared rate changes that **vary across trials**. If
  the simulated `hot_window` sits at the same time in every recording, it is protocol-locked, donors carry it,
  and the swap should not flag it. The plan's rule — "if neither null flags it, the confound was planted too
  weakly" — would then re-declare strength for the wrong reason. **Declare the hot window's timing as random
  per recording** for the shared-rate arm, and put a fixed-time version in the protocol-locked arm.
- **Draw donors at several matching tiers inside the simulation** (same mouse, same group, global). If the
  null distribution moves with donor distance, identity is leaking (Winkler 2015; Moerel 2025).
- **The simulator's missing pieces are the documented failure, not a footnote.** The plan lists shared slow
  drift and bleaching under "what the simulation cannot test". The literature says a shared within-recording
  time course is the single best-documented way recombination nulls lie (Perkel p. 428; Harris; Tyrcha et al.
  2013). **A simulated GO without a shared-drift arm should not license the real-data stage.**
- Keep the circular shift as the comparison null. Whole-train dither is what Louis 2010 recommends and what
  Stella et al. 2022 found most robust, so the existing `rigid_shift` reference is well chosen.

**Real-data concordance.**
- Harris's minimum of 5 sessions and the permutation floor matter when donors are confined to a group: with
  n records the smallest attainable p is about 1/n! (Yuan & Shou, bioRxiv).
- Permute donor membership fully rather than drawing one swap (Holroyd 2022, Box 4).
- Aggregate by recording, never by pair (Chen et al. 2016; Nastase et al. 2019).

---

## Corrections to what was on file

| was on file | what reading found |
|---|---|
| Cunningham & Yu 2014 as a candidate source for "pseudopopulations remove noise correlations" (the proposal; `lit_needed.md`) | **It does not say that.** "pseudo", "shuffl" and "noise correlation" do not appear in the body of the PMC author manuscript. Cite Averbeck, Latham & Pouget 2006 (p. 359, p. 362), Latham & Nirenberg 2005 or Kobak et al. 2016 instead |
| Permutation-contrastive learning as a within-recording ROI-swap analogue (the todo's seed) | It shuffles whole population snapshots in time; see the negatives section |
| Perkel, Gerstein & Moore 1967 Part II — metadata only | **Read** from a Europe PMC scan of the published pages. The route that worked is `europepmc.org/articles/<PMCID>?pdf=render`, which the ask list said was exhausted |
| Louis, Borgelt & Grün 2010, chapter 17 — paywalled ask | **Read** from the G-Node course portal copy, now shelved |
| Hyperscanning pseudo-pairs — "not read, a reviewer's search result" | **Read** — Burgess 2013 and five others |
| CICADA's surrogate — unknown, uncredited in `detectors/cicada.py` | An independent per-cell **circular shift** within the recording (upstream `sce_stats_utils.py`: 100 surrogates, 95th percentile; Dard et al. 2022 used 300 at the 99th). Cite the software as Zenodo 10.5281/zenodo.10041434 and the framework as Hamon et al. 2026, bioRxiv 10.64898/2026.07.03.736318. DeepCINAC is a different tool |
| Chen et al. 2016 blamed the subject-wise bootstrap (the todo's seed) | The subject-wise bootstrap was their best one-group method; the element-wise methods and circular-shift time-series randomisation inflated |
| Hindriks 2016 and Liégeois 2017 as between-subject surrogate nulls (the todo's seed) | Both use within-subject surrogates |
| "Narcissus effect (Colwell & Winkin 1984)" (the todo's seed) | Colwell & **Winkler** 1984 |
| Holroyd 2022, "Interpersonal synchrony: a mere by-product of shared sensory input?" (the todo's seed) | No such title. The paper is *Interbrain synchrony: on wavy ground*, *Trends Neurosci* 45:346–357 |
| König 1994 as the shift-predictor procedure; Grün et al. 1999's "multiple shift" as a surrogate | Abstracts only: König 1994 fits Gabor functions to correlograms; the multiple-shift method is a coincidence **detector**. Both unverified beyond the abstract |
| ⚠ Unresolved, recorded rather than settled | Hatsopoulos et al. 2003 (p. 26) say the shift predictor can **over**estimate expected synchrony under slow rate covariation. Amarasingham 2012 and Louis 2010 document the shuffle giving false **positives**, which means underestimating it. The two may describe different covariation (within-session drift versus trial-level states); not traced |

`detectors/cicada.py`'s credit and the ROI-swap proposal's literature section are **not** edited in this
change. Both corrections are recorded here for whoever next touches those files.

---

## Reading log

One row per paper read or tried. **Status** uses read / abstract only / metadata only / grep only.
Question codes: **null** (precedent as a null), **neg** (precedent as negatives), **id** (identity), **ex**
(exchangeability).

### Spike-train surrogates

| paper | qs | what it says, and where | status |
|---|---|---|---|
| Perkel, Gerstein & Moore 1967, *Biophys J* 7:419–440 | null, ex | Shuffle interstimulus segments; destroys everything except stimulus-locked relations (p. 436). Shared slow rate swing biases near-zero lag, below the square of the fractional swing for Poisson cells (p. 428) | read |
| Gerstein & Perkel 1972, *Biophys J* 12:453–473 | null, ex | Shuffle and shift controls differ only under serial dependence, most likely a shared long-term trend (pp. 463–464) | read |
| Aertsen, Gerstein, Habib & Palm 1989, *J Neurophysiol* 61:900–917 | null | JPSTH presented as superior to the shift predictor | abstract only |
| Brody 1999a, *Neural Comput* 11:1537–1551 | null, id, ex | Latency covariation broadens the shuffle corrector (p. 1541); excitability covariation leaves V = cov(ζ₁,ζ₂)Z₁⋆Z₂ (eq. 3.3); integral = count covariance (eq. 3.6); rules of thumb (p. 1548) | read in full |
| Brody 1999b, *Neural Comput* 11:1527–1535 | null, ex | Per-trial excitability estimate and subtraction; latency search conclusive only when negative (pp. 1528–1534) | read in full |
| Brody 1998, *J Neurophysiol* 80:3345–3351 | null | Slow resting-potential covariation (tens of seconds) produces correlogram peaks 25–200 ms wide | abstract only |
| Ventura, Cai & Kass 2005b, *J Neurophysiol* 94:2928–2939 | null, id, ex | Shared excitability explains a V1 synchrony effect entirely; trials not exchangeable, no nonparametric bootstrap (p. 2932) | read |
| Ventura, Cai & Kass 2005a, *J Neurophysiol* 94:2940–2947 | null | Companion bootstrap test | grep only |
| Kass & Ventura 2006, *Neural Comput* 18:2583–2591 | id, ex | State-driven count correlation grows with the counting window | read (main result) |
| Kass, Ventura & Brown 2005, *J Neurophysiol* 94:8–25 | ex | Arbitrary shuffles do not necessarily meet their goals (p. 13) | read (two passages) |
| Harrison, Amarasingham & Kass 2013, in *Spike Timing* (CRC) | null, ex | Trial shuffling as the exchangeable-model test; cannot separate timescales; broken by slow gain, misalignment, SNR drift (§4.4.3) | read (§4.4–4.5) |
| Albert, Bouret, Fromont & Reynaud-Bouret 2016, *Neural Comput* 28 | null, ex | Level holds only for centred statistics; common hidden variable makes rejection correct but not synchrony (§5) | read (abstract, intro, §4.2, §5) |
| Amarasingham, Harrison, Hatsopoulos & Geman 2012, *J Neurophysiol* 107:517–531 | null, ex | Shuffle flags shared slow rates, "the wrong null hypothesis" for a timescale question (§2.1, p. 519); all pairings equally likely (p. 521); lineup definition (§2.4); false positive with no injected synchrony (Fig. 3A); false negative for repeated fast structure (§2.6) | read |
| Amarasingham et al. 2011 supplement, arXiv:1111.4296 | ex | Trial shuffling also tests that trials are iid (§2.1) | read |
| Amarasingham, Geman & Harrison 2015, *PNAS* 112:6455–6460 | ex | Rate covariation versus coordination not identifiable unless timescales are distinct (p. 6459) | read |
| Harrison & Geman 2009, *Neural Comput* 21:1244–1258 | ex | Surrogates exchangeable given coarse-window counts; rejection means structure faster than the window (pp. 1248–1252) | read |
| Louis, Borgelt & Grün 2010, ch. 17 of *Analysis of Parallel Spike Trains*, pp. 359–382 | null, ex | Shift predictor is a special case of trial shuffling (pp. 363, 380); 24% false positives at α = 1% (Fig. 17.6, p. 377); regular spiking amplifies (p. 376); recommends whole-train dither | read (§17.2–17.5) |
| Louis, Gerstein, Grün & Diesmann 2010, *Front Comput Neurosci* 4:127 | null, ex | Cross-session pair as a known negative still significant under simple dithers, from stimulus-locked transients (pp. 9–10) | read |
| Grün, Diesmann & Aertsen 2010, ch. 10 of the same book | null, ex | Coherent rate states cause false positives; sum of per-trial products (eq. 10.11) | read (§10.4.2) |
| Grün 2009, *J Neurophysiol* 101:1126–1140 | null, ex | Cross-trial rate covariation "the most effective generator of false positives"; trial shuffling inappropriate under it | read (PMC text) |
| Grün, Riehle & Diesmann 2003, *Biol Cybern* 88:335–351 | null, ex | Cross-trial nonstationarity induces apparent rate covariation, with implications for the shuffle predictor | abstract only |
| Grün, Borgelt, Gerstein, Louis & Diesmann 2010, *BMC Neurosci* 11(Suppl 1):O15 | null | Trial-ID shuffling has the tallest false-positive bars in Fig. 1a; the text does not say which data type each bar is | read |
| Pipa, Wheeler, Singer & Nikolić 2008, *J Comput Neurosci* 25:64–88 | null | Trial shuffling "might lead to false positives" (§4.4, p. 81) | read (passage) |
| Stella, Bouss, Palm & Grün 2022, *eNeuro* 9(3) | null | Excluded spike exchange across trials because it does not keep the rate profile (p. 18); trial shuffling not tested | read |
| Hatsopoulos, Geman, Amarasingham & Bienenstock 2003, *Neurocomputing* 52–54:25–29 | null | Shift predictor can overestimate expected synchrony under slow rate covariation (p. 26) — see the unresolved correction | read (passage) |
| Staude, Rotter & Grün 2008, *Neural Comput* 20:1973–1999 | ex | Rate covariation and spike coordination statistically separable | abstract only |
| Ben-Shaul, Bergman, Ritov & Abeles 2001, *J Neurosci Methods* 111:99–110 | null | Trial-to-trial variability produces apparent correlation | abstract only |
| Vinci, Ventura, Smith & Kass 2016, *Neural Comput* 28:849–881 | id, ex | Count correlation is an attenuated version of rate correlation; trial variation dominates in V4 | abstract only |
| Larry & Joshua 2023, *J Neurophysiol* 129:843–861 | null | Shuffling "can be extended to neurons recorded at different times", matched on behaviour; cannot then be compared with real correlations | read (bioRxiv) |
| Yuan & Shou, *eLife* (bioRxiv 10.1101/2023.03.13.531689) | null, ex | Trial-swapping permutation valid if either variable's replicates are exchangeable; floor 1/n! | read (bioRxiv) |
| König 1994; Grün et al. 1999; Pazienti et al. 2007, 2008; Stella et al. 2019 | — | See corrections; within-train methods | abstract or metadata only |

### Calcium-imaging and assembly detectors

| paper | qs | what it says, and where | status |
|---|---|---|---|
| Mölter, Avitan & Goodhill 2018, *BMC Biol* 16:143 | null | Every null within one dataset; Marčenko–Pastur overestimates assembly count under calcium autocorrelation (pp. 9–10) | read |
| Russo & Durstewitz 2017, *eLife* 6:e19428 | null, ex | ISI shuffling flags spurious peaks under step-like rate change; Marčenko–Pastur PCA assigns units falsely (Appendix 1) | read |
| Romano et al. 2017, *PLoS Comput Biol* 13:e1005526 | null | Surrogate assemblies regroup ROIs within the dataset (p. 7) | read |
| Romano et al. 2015, *Neuron* 85:1070–1085 | null | Inter-activation-interval shuffling and neuron-index permutation, within the experiment | read (Europe PMC text) |
| Malvache et al. 2016, *Science* 353:1280–1283 | null | SCE threshold per recording; null in the supplement | main text read; supplement not obtained |
| Peyrache et al. 2010, *J Comput Neurosci* 29:309–325 | null, ex | Row and cell-identity permutations within recording; PRE-sleep epoch controls structural correlations (p. 311) | read |
| Lopes-dos-Santos et al. 2011, *PLoS ONE* 6:e20996 | null | Marčenko–Pastur null credited to Peyrache | read |
| Dard et al. 2022, *eLife* 11:e78116; Bocchio et al. 2020, *Nat Commun* 11 | null | CICADA-style per-cell circular shift, 300 at 99th and 1000 at 99th | read (Methods) |
| CICADA `sce_stats_utils.py` (gitlab.com/cossartlab/cicada) | null | Roll each cell's raster by a random offset, pool per-frame active counts, take the percentile | read |
| Rupprecht et al. 2021, CASCADE, *Nat Neurosci* 24:1324–1337 | id | Calcium kernels vary across datasets with the same indicator (Ext. Data Fig. 1) | read (passages) |

### Pseudopopulations and noise correlations

| paper | qs | what it says, and where | status |
|---|---|---|---|
| Harris 2021, bioRxiv 10.1101/2020.11.29.402719 | null, ex, id | Session permutation; independence and identical conditions required; shared decline and different strategies break it; at least 5 sessions | read (preprint) |
| Averbeck, Latham & Pouget 2006, *Nat Rev Neurosci* 7:358–366 | null, ex | I_shuffled by shuffling trials (p. 359); pitfalls of using it in place of I (p. 362) | read |
| Cunningham & Yu 2014, *Nat Neurosci* 17:1500–1509 | null | No pseudopopulation or shuffle claim; non-biological covariation "can seriously confound" ("Data preprocessing") | read (PMC author manuscript) |
| Kohn, Coen-Cagli, Kanitscheider & Pouget 2016, *Annu Rev Neurosci* 39:237–256 | null, ex | Shuffled versus true information can reverse with population size; simultaneous recording "critical" | read (PMC author manuscript) |
| Moreno-Bote et al. 2014, *Nat Neurosci* 17:1410–1417 | null, ex | Decoding "must be done on simultaneously recorded neurons" (Discussion) | read (PMC author manuscript) |
| Latham & Nirenberg 2005, *J Neurosci* 25:5195–5206 | null, ex | Shuffled distribution uses "a response distribution that never occurred" | read (that section) |
| Kafashan et al. 2021, *Nat Commun* 12:473 | null, ex | Shuffle conditioned on stimulus direction (p. 14) | read |
| Meyers 2013, *Front Neuroinform* 7:8; Meyers et al. 2008, *J Neurophysiol* 100:1407–1419 | null, ex | Pseudo-populations defined, condition-matched; nonstationary neurons removed before pooling | read |
| Kobak et al. 2016, *eLife* 5:e10989 | null, ex | Noise covariance cannot be estimated across sessions | read (Methods) |
| Posani 2026, bioRxiv 10.64898/2026.03.16.711920 | null, ex | Pooling can change geometry; one session may drive decoding (p. 7) | read |
| Saravanan, Berman & Sober 2020, arXiv:2007.07797 | ex, id | Shared subject offset gives 46–96% false positives (§3.1) | read |
| Aarts et al. 2014, *Nat Neurosci* 17:491–496 | ex, id | Nested data in 53% of 314 papers; Type I error up to 80% | abstract only |
| Tyrcha, Roudi, Marsili & Hertz 2013, *J Stat Mech* P03005 | ex, id | Shared nonstationary input mimics coupling | read |
| Sorochynskyi, Deny, Marre & Ferrari 2021, *PLoS Comput Biol* 17:e1008501 | null | Stitched sequential recordings miss large transients (p. 9) | read |
| International Brain Laboratory 2025, *eLife* 13:RP100840 | id | Lab not decodable from per-neuron features (Fig. 7, p. 18) | read |
| Xu, Zhang, Qian & Zhang 2026, CalM, arXiv:2604.04958 | id | Mouse from session embeddings 0.930, from neuron embeddings 0.224 (Table 20) | read |
| Safaie et al. 2023, *Nature* 623:765–771; Gallego et al. 2020, *Nat Neurosci* 23:260–270 | id, ex | Cross-animal and cross-day dynamics compare only after alignment | read |
| Stefanini et al. 2020, *Neuron* 107:703–716; Leavitt et al. 2017, *PNAS*; Mozumder & Constantinidis 2023; Mozumder et al. 2025; Nogueira et al. 2020; Ebitz & Hayden 2021; Courellis et al. 2024; Deitch et al. 2021; Zhang et al. 2026 | null, ex, id | Simultaneous versus pseudo decoding gaps inconsistent in sign and size; pseudopopulations disrupt correlation structure; all condition on a shared clock | read (relevant sections) |
| Anderson, Sanderson & Sheinberg 2007; Franco et al. 2004 | null | Little or no synergy from simultaneous recording in IT | abstract only |

### Learning with negatives

The table in the answer on negatives covers TCL, CPC, Cheng, Banville, NuCLR, NCL and CONCORD, all read.
The rest:

| paper | qs | what it says, and where | status |
|---|---|---|---|
| Hyvärinen & Morioka 2017, PCL, AISTATS | neg, ex | Negative pairs whole vectors at a random time (p. 4, eq. 11) | read |
| Chau et al. 2025, Population Transformer, ICLR | neg | Within-subject channel swap (p. 4) | read |
| Jude, Perich, Miller & Hennig 2022, arXiv:2205.09829 | neg, ex | Rate-matched synthetic replacement neuron (p. 4) | read |
| Schneider, Lee & Mathis 2023, CEBRA, *Nature* 617:360–368 | neg, id, ex | Uniform sampling across a factor makes the model invariant to it (p. 11); no session-decoding measurement | read (sampling, multi-session) |
| Kiyasseh, Zhu & Clifton 2021, CLOCS, ICML | neg, id | Other patients as negatives, deliberately patient-specific | read |
| Pandarinath et al. 2018, LFADS; Ye et al. 2023, NDT2; Azabou et al. 2023, POYO | id, ex | Per-session parameters or tokens; POYO's session embeddings group by lab and animal (Fig. 5D) | read |
| Le & Shlizerman 2022, STNDT; Azabou et al. 2021, MYOW; Kostas et al. 2021, BENDR; Mohsenvand et al. 2020, SeqCLR; Ye & Pandarinath 2021, NDT | neg | Negatives within a session, sequence or batch; SeqCLR's "channel recombination" is re-referencing | read or grep |
| Rivière et al. 2020; Liu, Tang & Goldwater 2023 | neg | Same-speaker negatives as the default | read (method sections) |
| Zech et al. 2018, *PLoS Med*; Geirhos et al. 2020, *Nat Mach Intell*; Doersch, Gupta & Efros 2015 | neg, id | Hospital identity learned; shortcut learning; chromatic aberration solved a pretext task | read |
| Minderer et al. 2020; Chen, Luo & Li 2021; Lin, Wu & Jung 2026; Zare et al. 2026 | neg, id | Shortcut features suppress others; EEG foundation models carry identity | abstract only |
| Gutmann & Hyvärinen 2012, NCE, *JMLR* 13:307–361 | neg, ex | Noise must cover the data's support (Theorem 1, p. 311); noise "too different" teaches little (p. 313) | read |
| Lopez-Paz & Oquab 2017, C2ST, ICLR | neg, ex | Rejects P = Q on any axis; raw-pixel tests separate GAN images by checkerboard artefacts (§5, p. 7) | read |

### Hyperscanning and physiology

| paper | qs | what it says, and where | status |
|---|---|---|---|
| Burgess 2013, *Front Hum Neurosci* 7:881 | null, ex | 45 pseudo-pairs; spurious hyper-connections from condition-driven rhythmicity (p. 13); circular correlation and mutual information robust | read |
| Holroyd 2022, *Trends Neurosci* 45:346–357 | null, ex | Randomly paired dyads show eyes-closed alpha synchrony; permute membership fully (Box 4) | read (author manuscript) |
| Hamilton, PsyArXiv 10.31234/osf.io/rc9wp (*Neuron* 2021) | null, ex | Pseudo-pairs valid only if matched on experienced events (pp. 4–5) | read (preprint) |
| Zamm et al. 2024, *SCAN* | null, ex | Chance depends on the target; co-produced stimuli let true pairs beat surrogates | read (Europe PMC text) |
| Reindl et al. 2021, bioRxiv (*NeuroImage* 2022) | null, ex | Participant ID exchangeable within condition × channel, stated (4.7.3) | read (preprint) |
| Gugnowska et al. 2022, *Cereb Cortex* | null, ex, id | Cross-dyad surrogates matched on condition; trials equalised by deletion or duplication; individual temporal fingerprint | read (Europe PMC text) |
| Moerel et al. 2025, *PLoS Biol* | null, ex | Stratified pseudo-pairs; 6 unmatched pairs dropped (pp. 6–10) | read |
| Zimmermann, Schultz-Nielsen, Dumas & Konvalinka 2024, *Imaging Neurosci* 2 | null, ex | Short epochs and power differences look like inter-brain synchrony (4.3) | read (Europe PMC text; supplement not read) |
| Kingsbury et al. 2019, *Cell* 178:429–446 | null, ex | Calcium imaging; cross-session partners; behaviour-matched epochs show no correlation | read (PMC author manuscript) |
| Moulder, Boker, Ramseyer & Tschacher 2018, *Psychol Methods* 23:757–773 | null, ex | Participant shuffling versus data sliding; the former rejected more often on real data | read (PMC author manuscript) |
| Iatsenko et al. 2013, *Phil Trans R Soc A* 371:20110622 | null, ex | Inter-subject surrogates can make the threshold lenient (p. 7) | read |
| Ticcinelli et al. 2017, *Front Physiol* 8:749 | null, ex | Independence "by definition"; donors pooled across spectrally different groups | read |
| da Silva Castanheira et al. 2021, *Nat Commun* 12:5713 | id | 95–96% of 158 people from 30 s MEG | read (pp. 1–3) |
| Prichard & Theiler 1994, *PRL* 73:951–954; Pereda et al. 2005; Sheppard et al. 2012 | ex | Physics surrogates stay within one recording | read |
| Shahbazi, Ewald, Ziehe & Nolte 2010, IFMBE Proc. 28:207–210 | null, ex | Shift unmixed sources and remix — keeps shared instantaneous mixing | abstract only |
| Ayrolles 2021; Nguyen 2021; Kayhan 2022; Marriott Haresign 2022; Liu 2022; Pérez 2017, 2021; Dumas 2010; Hakim 2023; Czeszumski 2020 | null, ex | Fake-pair options within or between condition; random-mother pairs not generally beaten; surrogates within a dyad; band-selection double dipping | read (sections) or skimmed |
| Lancaster et al. 2018, *Physics Reports* 748:1–60; Theiler et al. 1992; Andrzejak et al. 2003; Barnes et al. 2024; Toledo et al. 2002 | — | Whether the surrogate reviews cover inter-subject surrogates is unverified | metadata or abstract only |

### fMRI, ecology and genomics

| paper | qs | what it says, and where | status |
|---|---|---|---|
| Finn et al. 2015, *Nat Neurosci* 18:1664–1671 | id, ex | 117 and 119 of 126 identified at rest; per-node variance alone 48–87%; motion alone 2.4% | read (Europe PMC text) |
| Amico & Goñi 2018, *Sci Rep* 8:8254; Bari et al. 2019 | id | Identity small on large shared structure; site effects survive harmonisation | read |
| Simony et al. 2016, *Nat Commun* 7:12141 | null, ex | Inter-subject correlation filters intrinsic and non-neuronal correlation; not significant at rest | read |
| Nastase, Gazzola, Hasson & Keysers 2019, *SCAN* 14:667–685 | null, ex | Pair-wise bootstrap violates exchangeability; stimulus-locked physiology creates correlation | read (Europe PMC text) |
| Chen et al. 2016, *NeuroImage* 142:248–259, and corrigendum | ex, null | Exchangeability by subject not element; circular shift "similarly inflated" on real data | read (PMC text, no figures) |
| Winkler et al. 2014, *NeuroImage* 92:381–397; Winkler et al. 2015, *NeuroImage* 123:253–268 | ex | Exchangeability blocks; free shuffling fails when data and contrast share the dependence | read |
| Hindriks et al. 2016; Liégeois et al. 2017; Ahrends et al. 2022 | ex, id | Surrogate nulls narrower than the question; models fit across subjects learn the subject | read |
| Hasson et al. 2004, *Science* 303:1634–1640 | null | Cross-subject correlation under a shared movie | abstract only |
| Gotelli 2000, *Ecology* 81:2606–2621 | null, ex | Row-free nulls 49–70% false rejection (Table 4) | read |
| Ulrich & Gotelli 2007b; Gotelli & Ulrich 2011, 2012; Fayle 2020; Molina & Stone 2020; Colwell & Winkler 1984 | ex | Scale rejects every null; smuggling; heterogeneity reported as association; Narcissus effect; test with graded assumption violations | read (partial) |
| Connor & Simberloff 1979; Diamond & Gilpin 1982; Miklós & Podani 2004; Ulrich & Gotelli 2007a; Fayle & Manica 2010, 2011; Wilson 1995; Peres-Neto et al. 2001 | ex | Origin of the fixed-total swap and its critiques | abstract or metadata only |
| Abney 2015, *Genet Epidemiol* 39:249–258 | ex | Confounding from shared covariance structure even for an independent predictor; naive permutation 3.7× nominal | read |
| Churchill & Doerge 1994, *Genetics* 138:963–971; Price et al. 2006, *Nat Genet* 38:904–909 | ex, id | Permutation thresholds valid under equal relatedness; stratification as the confound | abstract only |

---

## Searches, and what was not searched

Each reader recorded its queries; the counts here are theirs. Crossref and OpenAlex resolved every seed.
Forward-citation traces ran on Brody 1999a (343 citing works), Albert 2016 (18), Amarasingham 2012, Louis
2010, Mölter 2018, Elsayed & Cunningham 2017, Harris 2021, Burgess 2013, Shahbazi 2010, Cheng 2020, Banville
2021, Chen 2016, Winkler 2015 and Colwell & Winkler 1984. OpenAlex rate limits cut some traces short.

**Searched and found nothing** — searched absences, not proofs:
- "chimeric surrogate" and "chimeric surrogates" in neural synchrony and EEG connectivity;
- inter-subject or cross-subject surrogate connectivity in EEG or MEG;
- calcium-imaging synchrony or assembly nulls built from cells of different slices or animals;
- "shuffled across sessions" and shift predictors from different sessions or animals;
- pseudo-pair confounds from session date, time of day or rig.

**Not searched** — residuals, never absences:
- the full texts of slice calcium-imaging assembly papers from the Yuste, Ikegaya and Bonifazi labs, and
  Cossart, Aronov & Yuste 2003;
- Okun et al. 2012 (a model conditioned on population rate, likely relevant);
- speech models after CPC, fMRI and MEG foundation models, and NDT3;
- single-cell contrastive methods beyond CONCORD, and site harmonisation such as ComBat;
- EEG fingerprinting beyond one MEG paper;
- the bodies of most forward-citation hits.

**Correspondence.** Asking the Grün group whether a cross-session surrogate has been tried is still the
cheapest outstanding check, and whether to write is Tony's call.
