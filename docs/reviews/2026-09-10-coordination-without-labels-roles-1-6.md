# Murderboard on the label-free detector — roles 1-6

> **Recovered from the harness archive on 2026-09-12, not re-run and not edited.**
> Working material, the same standing as a handoff — **not murderboarded**, and nothing
> here is for an outside reader. Paths and recording identifiers are scrubbed
> (`<repo>`, `<darkroom>`, `<recording>`); nothing else in the reports is changed.
>
> ⚠ **Each report below is the role's FINAL message, which is the authoritative one.**
> Do not grep these transcripts for a grant line: the string `GRANT n ok — <tools>`
> appears inside every compiled agent file, and that file is quoted verbatim in the
> transcript, so a naive scan returns the declaration the role was *given* rather than
> the one it *made*. Role 4 is the live example — a whole-transcript grep finds both
> `GRANT 4 ok` and `GRANT 4 MISMATCH`, and MISMATCH is what role 4 actually declared.


The eleven role reports behind [`2026-09-10-coordination-without-labels_2026-09-10.md`](2026-09-10-coordination-without-labels_2026-09-10.md), the murderboard that stopped the first self-supervised detector. That run record **summarised** these and said so; the reports themselves were never archived, and this file is them.

---

## Role 1 prove it — `murderboard-prove-it`

*Recovered from `agent-afcbe65b658970426.jsonl`; 15,135 characters.*

GRANT 1 ok — Read, Grep, Glob, Bash

## What I checked

Every quantitative and factual claim in `<repo>/docs/proposals/2026-09-10-coordination-without-labels.html`, recomputed against: the two export folders resolved by `bugarach.dataset` (`..._STEPS_EXCLUDED_SENKTIDE`, `..._STEPS_EXCLUDED_TTX`), `current_export.toml`, `docs/FOUNDATIONS.md` §9, `docs/GLOSSARY.md`, `docs/performance_table.md`, `docs/learned/bakeoff.json`, `docs/detector_history.md`, the two named todos, `src/bugarach/learn/nets/*`, `src/bugarach/detectors/*`, `src/bugarach/simulate.py`, `src/bugarach/score.py`, `docs/export_folder_spec.md`, and the SVG geometry of the figure. The artifact is untracked and has no prior version and no generator, so the regeneration-diff check is N/A — recorded rather than skipped.

## Claim ledger — corpus table (the only "measured" block)

| quoted | source | recomputed | verdict |
|---|---|---|---|
| senktide 29 rec | export folder | 29 | match |
| senktide 9.5 h | regions.csv baseline windows | 9.5333 h | match |
| senktide 950 traces | distinct ROI/rec summed | 950 | match |
| senktide ROIs 17–32–55 | per-rec distinct ROI | 17 / 32 / 55 | match |
| senktide 18,011 fast / 6,772 slow | in-window onsets | 18,011 / 6,772 | match |
| TTX 38 rec | export folder | 38 | match |
| TTX 12.6 h | regions.csv | 12.6167 h | match |
| TTX 1,169 traces | distinct ROI/rec | 1,169 | match |
| **TTX ROIs 10–32–61** | per-rec distinct ROI | **10 – 31 – 61** | **MISMATCH** |
| TTX 19,685 / 16,072 | in-window onsets | 19,685 / 16,072 | match |
| both 67 / 22.1 h / 2,119 / 37,696 / 22,844 | sum | 67 / 22.15 h / 2,119 / 37,696 / 22,844 | match |
| "averaging just under 20 minutes" | — | 19.84 min | match |
| senktide ~2.7 fast per slow | — | 2.660 | match |
| TTX ~1.2 | — | 1.225 | match |

Both ROI-count definitions (distinct ROI in the event file, and `slices.csv:n_roi_recorded`) give **31** for TTX; they agree everywhere and neither yields 32. The `regions.csv` NA→`start_sec` fallback the brief mentions never fires in either cohort — zero NA in `analysis_start_sec`/`analysis_end_sec`.

## Findings

| # | Location | Issue | Sev | Suggested fix | Verified? |
|---|---|---|---|---|---|
| 1 | "Where we are" h2 "Ten detectors…", lede "six written by hand, four learned", "Five of the six architectures", "the ten detectors are not ten approaches" | **The detector arithmetic is wrong and self-contradicting.** `nets.ARCHITECTURES` holds **six** learned architectures (`bakeoff.json` `registered: [tiny, trace, tube, tube_guard, tube_ratio, tube_ratio_guard]`, `registered_but_not_run: []`), plus six hand-written = **twelve**. The doc says "four learned" and "ten detectors" in the lede and heading, then says "five of the six architectures" and lists all six in its own code excerpt. | blocking | "six written by hand, six learned"; heading "Twelve detectors, and structurally one idea"; "the twelve detectors are not twelve approaches" | yes |
| 2 | Masthead chip "nothing measured"; §"Three questions" — "Nothing in it has been measured"; Limits — "The only measured numbers in this document are the corpus counts" | **False as written.** The doc also quotes measured F1 (0.125, 0.681), a measured bake-off design (8 seeds/4 folds), measured artifact figures (74–82%), and measured TTX effects (0.46 / 2.50). | blocking | "Nothing *proposed* here has been measured. The measured numbers quoted are the corpus counts, the bake-off scores, and the preparation facts cited from our foundations — all of them from prior work, none of them from this design." | yes |
| 3 | Corpus table, TTX row | ROIs/recording median is **31**, not 32 (senktide's median is 32 — looks copied). | blocking | `10 – 31 – 61` | yes |
| 4 | "The critical choice" — "Our six hand-written detectors use a circular shift null" and "All six compute a version of the same statistic: observed coincidence, against coincidence estimated from nearby data" | **Only four of six use a circular-shift null.** `rate.py` computes `excess = rate − context` with no surrogate at all; `sync.py` is a SPIKE-synchronization profile with hysteresis thresholding and its docstring says **"Deterministic — no RNG."** `sync` also has no local-background comparison, so "all six" fails twice. This matters to the argument: the wrap-splice objection does not apply to two of them. | blocking | "Four of our six hand-written detectors (CoactDetect, LoCo, binned SCE, locust) use a circular shift null; rate+context compares against a surrounding window and SPIKE-synchronization uses no null at all." | yes |
| 5 | Warn box — "Split by recording, stratified by group" | **Subject is not the recording.** `slices.csv:mouse_id` — in the folder this proposal already reads — shows **67 recordings from 36 mice**; 22 mice contribute 2–3 recordings, and 5 mice appear in *both* cohorts. Splitting by recording puts two slices from the same animal in train and test, which is the same leak the doc names one sentence earlier. | major | Add: "Split by **animal**, not by recording — `mouse_id` in `slices.csv` shows 67 recordings from 36 mice, 22 of them contributing more than one." | yes |
| 6 | Warn box — "we do not currently have an explanation for the gap" (2.7 vs 1.2) | **The explanation is in a column already loaded.** Broken out by `group_id`: senktide DI 3.76 / OVX 3.00 / ORX 1.75 / MALE 1.47; TTX DI **0.88** / MALE 1.04 / ORX 1.74 / OVX 2.81. Within-cohort spread exceeds the between-cohort gap; ORX is 1.75 vs 1.74. The cohorts differ in group composition (senktide DI 6 / OVX 8 of 29; TTX DI 11 of 38). FOUNDATIONS §9: *"a pooled across-group number hides sign changes and is not admissible on its own."* The 2.7/1.2 pair is exactly such a number. | major | Replace with the per-group breakdown, and state that the pooled ratio is not admissible alone per FOUNDATIONS §9 | yes |
| 7 | "The corpus" — the folder described only as artifact-removed | **Four recordings with a known, unflagged cross-cell contaminant are in the training corpus and unmentioned.** `current_export.toml` (`steps_excluded`): non-rigid motion correction pinned 12 ROIs to the frame floor across `<recording>`, `<recording>`, `<recording>`, `<recording>` — "Not flagged in any column. Producer's own caveat." All four are in these cohorts (senktide: `<recording>`; TTX: the other three). A frame-floor-pinned ROI is a cross-cell artifact of precisely the kind the dither objective is said to reward. | major | Name the caveat beside the field-step one, and say whether those four are in or out | yes |
| 8 | Limits — "retracted as unsupported — it rested on web searches, not on papers read" | **Understates the retraction, and reverses whose evidence is whose.** The *original* claim rested on web searches; the *retraction* rests on three papers read in full — DOSED (Chambon 2019), cnn-ripple (Navas-Olive 2022), SEED (Tapia-Rivas 2024) — and concludes *"Learned event detection over physiological time series is a genre, not a gap, and no architecture-novelty claim survives."* As written the reader is told the question is open; it is closed. This also weakens the doc's own ask #1. | major | State the finding and cite the three papers; reframe ask #1 as "is this *construction* known", not "has this been done" | yes |
| 9 | "Where we are" — "Two of the four learned variants fire on a single cell" | Wrong count (**two of six**, per the todo's own opening line), and it drops the correction the source added the same day. Measured: `tube_ratio` 5.7% and `tube_ratio_guard` 6.5% of calls on one ROI or none, against a **96% chance rate** — the todo says explicitly *"Read this as a comparison, not as an indictment. Both ratio variants are still 15× better than dart-throwing."* | major | "Two of the six learned variants land on one ROI or none about ten times more often than the two subtract variants (5.7%/6.5% against 0.3%/0.8%, chance 96%)." | yes |
| 10 | Footer — "Hansen 1973" | **Wrong year for GO-CFAR.** `detector_history.md` §4's attribution table — the row marked **read in full**, with volume and pages — gives **Hansen & Sawyers, *IEEE T-AES* AES-16(1), Jan 1980, 115–118**, as does `docs/learned/cfar_scope.html`. "Hansen 1973" survives only in two prose recaps. A wrong citation year in a public-facing footer. | major | "Finn & Johnson 1968; Hansen & Sawyers 1980; Rohling 1983" | yes |
| 11 | Limits — "Not a claim about any drug. Nothing here says what tetrodotoxin or senktide does"; footer — "No … unpublished results from collaborating laboratories appear in this document" | **Both are contradicted by the document's own text.** It states TTX's effect on coordination by stream (0.46 / 2.50), and that senktide raises event frequency and the fluorescence baseline. Per FOUNDATIONS §9 those figures are the MATLAB campaign's (`darkroom/constellation/coordBA_uniform_*`, `oxc_ttx_persistence.csv`) and *"treatment effects themselves are fireflies' and must not be re-derived here."* | major | Soften to "no *new* claim about any drug — the TTX and senktide facts below are cited from the lab's own campaign, not measured here", and fix the footer sentence to match | yes |
| 12 | "Where we are" — "`tiny` … is the one that does not train — it scores 0.125" | `trace` scores **0.118**, lower, and the source todo says *"two of the six learned files are degenerate (`trace` and `tiny`)"*. `tiny` is not "the one". | major | "the two that do not train — `tiny` at 0.125 and `trace` at 0.118, against a best of 0.681" | yes |
| 13 | Open questions — "one to two thousand parameters" | `bakeoff.json` `n_params`: tube family **1,149**; trace **2,065**; tiny **2,393**. Two of six exceed two thousand. | minor | "roughly 1,100 to 2,400 parameters" | yes |
| 14 | "The dither width is a declared, interpretable parameter" — "the same quantity as the jitter our simulator uses" | *J* is a half-width of a bounded symmetric distribution; `PlantedEvent.jitter_sec` is documented as **"SD of participant onset jitter"**. `score.tol_sec` *is* a half-width, so the tolerance half of the sentence holds and the jitter half does not. | minor | Drop the jitter equivalence, or say "related to (not equal to) the simulator's jitter SD" | yes |
| 15 | "Where we are" — "traces three of them to the radar … literature" | The closing audit maps **three CFAR analogues across two detectors** — `rate_detect` = CA-CFAR, and LoCo's `maxlt` = GO-CFAR *and* its percentile-of-pool = OS-CFAR kin. CoactDetect's row carries no attribution. "Three of them" reads as three detectors. | minor | "traces three CFAR constructions onto two of them" | yes |
| 16 | "For the producer team" — "every surviving row reads zero" | True of `on_field_step` (0 on all 229,221 rows). `field_step_id` is **empty on all 229,221 rows**, not zero. | minor | "one reads zero on every surviving row and the other is empty on every row" | yes |
| 17 | Not stated anywhere | **41 event rows carry `time_sec = NA`** (senktide 7, TTX 34), with `width_sec`, `peak_sec`, `amp` also NA on the same rows. Immaterial to the table (all counts above already exclude them) but a loader that coerces rather than skips will crash or silently mis-window them, and the doc says the proposal "reads the folder exactly as specified today". | minor | Add to the producer notes, or state that the 41 timeless rows are dropped | yes |
| 18 | "The problem" — "a third of them not at all in a given window" | 35% (senktide) / 21% (TTX) / 27.5% pooled zero-onset ROIs in baseline windows. FOUNDATIONS §9 says "roughly 35% with no events in a baseline window" — so "a third" matches senktide and the foundations, and overstates the pooled corpus. | minor | "a fifth to a third, depending on cohort" | yes |
| 19 | Figure caption — "background onsets drawn from a gamma-distributed per-cell rate, seed 7" | The SVG is hand-authored; no generator for it exists in the tree. The provenance claim cannot be checked by a reader or by me. | minor | Either ship the generator or drop the seed/distribution claim and say "hand-drawn schematic" | **no** |
| 20 | "The corpus" — "makes 74–82% of cells appear to fire at once" | Not a range — `current_export.toml` gives **74% fast and 82% slow**, two per-stream figures. | minor | "74% of cells in the fast stream and 82% in the slow" | yes |

## Claims that verified clean (recomputed, not eyeballed)

- Code excerpt, all three lines: `frac = x.sum(dim=1, keepdim=True) / max(n, 1)` = `trace.py:40`; `bright = pooled.sum(dim=1, keepdim=True) / max(n, 1)` = `tube.py:262` (`tube.py:143` adds a trailing `# space invariant`); `h = self.roi(x.reshape(b * n, 1, t))` = `tiny.py:47`. The comment labels match each `@register` note.
- **0.125 / 0.681** — `performance_table.md` §2, tiny and tube. Not affected by the flat-field supersession, which is scoped to §1; `bakeoff.json`'s spec carries the fitted `bg_rate_shape` and `bg_burst_shape`.
- **"eight seeds over four held-out folds"** — `bakeoff.json`: `folds: 4`, 8 seeds, `seeds_per_fold: 2`. **"one training run per fold"** — `train_seed: 0`.
- **`sce_detect` raises `NotImplementedError` for `surrogate_model="jitter"`** — `src/bugarach/detectors/sce.py:124-125`, exactly as described.
- **`participation_mask` has exactly one consumer** — `tests/test_simulate.py:64` is the only call. (Caveat: the underlying `PlantedEvent.rois` record *is* read by `tools/probe_crowded_background.py`, `tools/make_learned_figures.py` and `tests/test_bench.py`, so "which cells it recruited … has exactly one consumer" is true of the method and not of the record. Sub-minor; the argument survives either way.)
- **"participation count is written as `NA` on every learned call"** — `tools/run_learned_on_folder.py:250` writes `n_roi=None`.
- **"10 to 61 cells"**, **"22 hours"**, **fields/duration/event-count framing** ("tens of cells, twenty minutes, a few thousand events" — median 32 ROI, 19.8 min baseline, 3,421 events/recording whole).
- **TTX fast 0.46 / slow 2.5**, **senktide raising frequency and baseline**, **K's definition as a person-set percentage**, **"moves the headline by an order of magnitude"**, **"no arithmetic chooses it"** — all verbatim-accurate against FOUNDATIONS §9 and GLOSSARY.
- **"The contract does not mention field steps"** — confirmed, `docs/export_folder_spec.md` has zero hits for `field_step`/"field step". **"Our own loader also drops both columns silently"** — confirmed in `current_export.toml`.
- **"our simulator draws fresh participants for every event"** — `rng.choice(nR, size=np_, replace=False)` per event, `simulate.py:676` and `:705`.
- **Figure geometry is exact**: 67 marks in each panel, identical per-row counts across the two (per-cell rates preserved), 14 rows, seven distinct cells in the column under the down-triangle, and the maximum within-row displacement is 17.0 px = 1.59 s — exactly half the lane span rect. The only cosmetic note: row 1 carries a background onset at x=388.7 abutting its coordinated mark at x=391.9 (3.2 px apart at 2.6 px width), so the column reads as eight marks over seven cells.

---

## Role 2 citations — `murderboard-doi-or-die`

*Recovered from `agent-a3a5d83bc88508e39.jsonl`; 20,689 characters.*

I have what I need. Here is my report.

---

**GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch**

Artifact: `<repo>/docs/proposals/2026-09-10-coordination-without-labels.html`

## Part 1 — Attribution audit: exists / says what is claimed / is the origin

| # | attribution | exists | says what is claimed | is the origin |
|---|---|---|---|---|
| 1 | CICADA, Cossart lab, MIT, © 2019 | **yes** — `gitlab.com/cossartlab/cicada`, MIT on the repo, `Copyright (c) 2019 Cossart Lab` in the upstream notice carried at `src/bugarach/detectors/cicada.py:46`; repo created 2019-08-29 | **yes** for the software and licence | **no** — for the SCE rule the root is Cossart, Aronov & Yuste 2003, *Nature* 423:283–288 (**Yuste's** lab), which itself credits Mao et al. 2001, *Neuron* 32:883–898 (unreached by anyone here) |
| 2 | Kreuz lab's SPIKE-synchronization | **yes** — Kreuz, Mulansky & Bozanic 2015, *J Neurophysiol* 113(9):3432–3445 | **yes**; Kreuz is first and corresponding author, ISC-CNR Florence, so "Kreuz lab" survives the last-author-plus-affiliation test | **one step short** — the coincidence criterion descends from event synchronization, Quian Quiroga, **Kreuz** & **Grassberger** 2002, *Phys Rev E* 66:041904 (Grassberger's group, Jülich). SPIKE-synchronization as named is Kreuz's. I stopped at 2002 |
| 3 | Finn & Johnson 1968, cell-averaging CFAR | **yes** — *RCA Review* 29(3), Sept 1968, 414–464 | **yes**, the CA-CFAR founding paper; on this project's shelf, read in full | **yes** |
| 4 | Hansen 1973, greatest-of CFAR | **yes** — Proc. IEE Int. Radar Conf., IEE Conf. Publ. 105, 325–332 | **yes**, confirmed independently as where GO selection is introduced | **yes** — and the document is *more* right than `detector_history.md` here (see F4) |
| 5 | Rohling 1983, ordered-statistic CFAR | **yes** — *IEEE T-AES* AES-19(4), July 1983, 608–621, doi:10.1109/TAES.1983.309350 | **yes**; the document's hedge "a relative of ordered-statistic CFAR" correctly mirrors the repo's "kin to" | **yes** |

No fabricated or guessed bibliographic metadata found. Every named work resolves.

## Part 2 — Structured finding list

### Attribution findings

**F1 · "three of them to the radar CFAR literature" is wrong · location: "Where we are", ¶1 · severity HIGH · verifiable YES**

The sentence reads *"traces three of them to the radar constant-false-alarm-rate literature — cell-averaging CFAR, greatest-of CFAR, and a relative of ordered-statistic CFAR."* The apposition makes three named CFAR variants map one-to-one onto three detectors. They do not. `GLOSSARY.md:261-263`: *"`rate_detect` is cell-averaging CFAR (Finn & Johnson 1968), `loco_detect`'s `maxlt` is GO-CFAR (Hansen 1973), and its percentile-of-pool is kin to OS-CFAR (Rohling 1983)."* That is **three mechanisms across two detectors** — greatest-of and the order statistic are both LoCo. `detector_history.md:460-469` agrees: CoactDetect is the third detector in the CFAR design space, and its attribution column is `—`.

Fix: *"…traces two of them to the radar constant-false-alarm-rate literature under three named forms — cell-averaging CFAR in one, and both greatest-of selection and a relative of ordered-statistic CFAR in the other. A third sits in the same design space with no separate attribution."*

**F2 · "Two more are ports or adaptations of published work" reinstates a sentence the project already withdrew · same paragraph · severity HIGH · verifiable YES**

`detector_history.md:312-317` withdraws in terms the claim that locust is *"the only one of the six whose idea has a settled external owner"*, because **"the 2026-08-24 audit found published prior art for all six."** The document's accounting is 3 + 2 = 5, leaving binned SCE as the one detector with no stated lineage — when its published root (Cossart, Aronov & Yuste 2003) is the *oldest* attribution the project holds. LoCo and CoactDetect also carry a published family in the repo's own README: Unitary Events, Grün, Diesmann & Aertsen 2002, *Neural Computation* 14(1):43–80 and 81–119.

Fix: say all six have published lineage and give the two the document currently drops.

**F3 · The lineage footer is incomplete against the repo's own citation block · footer · severity MEDIUM · verifiable YES**

`README.md:633-680` lists, for these same detectors: Cossart/Aronov/Yuste 2003; Grün/Diesmann/Aertsen 2002; Amarasingham et al. 2012; Mulansky & Kreuz 2016 (PySpike, whose BSD source the SPIKE-synch port derives from). The footer names only CICADA, Kreuz and the CFAR trio. For an externally circulated document that is an under-acknowledgement, and PySpike's omission is a licence-adjacent one.

**F4 · `Hansen 1973` vs `Hansen & Sawyers 1980` — the document is right and the repo disagrees with itself · severity MEDIUM (about the repo) · verifiable YES**

`GLOSSARY.md:262` and `README.md:648-651` say Hansen 1973 is the origin; `detector_history.md:464` puts **Hansen & Sawyers 1980** in the attribution column with "read in full". I confirmed independently that Hansen 1973 introduces GO selection and Hansen & Sawyers 1980 measures its detectability cost — so `detector_history.md` §4 is citing the analysis where its own column header says origin. The proposal picked correctly. **⚠ Residual: nobody on this project has read Hansen 1973** (README marks it `°`; the shelf at `<darkroom>/bugarach/lit/radar/` holds the 1980 paper, not the 1973 one). The document presents all three CFAR references flat, with no indication that one of them is unread here.

Fix, in the repo: correct the §4 attribution column. Fix, in the document: nothing required, but consider a footnote saying which primaries are held.

**F5 · "adapted from the Cossart lab's CICADA" omits *partial* · "Where we are" and footer · severity LOW-MEDIUM · verifiable YES**

`GLOSSARY.md:82-95` is emphatic: locust is a **partial** port (CICADA's per-cell transient-detection stage is skipped entirely) and a **modified** one, and *"the 1e-9 parity reaches interface2's `generate_sce_cicada`, not the Cossart source"*. The document says "adapted", which is the right verb and does not carry the original's name onto the detector — the ADR-0016 rule is respected. But an external reader learns nothing about what was turned off. One clause fixes it: *"adapted from the SCE stage of the Cossart lab's CICADA — a partial port, since CICADA's own transient detection is not used."*

**F6 · If a CICADA reference is added, do not conflate two licences · severity LOW · verifiable YES**

The GitLab source is MIT (verified). The Zenodo software deposit the README cites — Denis, Dard, Quiroli, Cossart & Picardo, *CICADA* v1.0.3, 20 July 2020, doi:10.5281/zenodo.10041434 — is **CC BY 4.0**, not MIT. Both are upstream's statements; the port derives from the MIT source. Cite the DOI for the software and the GitLab source for the licence, and say which is which. (Separately: `GLOSSARY.md:29` says *"CICADA (Denis et al. 2020)"* — the 2020 **eNeuro** Denis et al. paper is DeepCINAC, not CICADA. The glossary row is ambiguous enough to be read as the wrong paper.)

**F7 · FORWARD TRACE: the closest prior art for the SPIKE-synch detection layer is Kreuz's own later paper, and the document does not say so · severity MEDIUM-HIGH · verifiable YES**

The document writes *"one built on the Kreuz lab's SPIKE-synchronization measure"*, which reads as: measure theirs, detector ours. `detector_history.md:168-169` records the opposite conclusion: *"Not novel either: Kreuz's own lab has published the same two-knob detector on this profile (personal communication, April 2026; Kreuz et al. 2022, J Neurosci Methods 381:109703)."* I confirmed that reference exists. This is the required forward trace — the wrapped tool's authors did the wrapping themselves — and it is already in the tree.

## Part 3 — Novelty. This is the substantive section.

**Verdict: the posture is honest, the effect is not.** The document says *"we would be unsurprised to learn this exact construction has a name."* It has at least four, and I found them in under an hour of searching. A disclaimer that prior art probably exists is not a substitute for the search that finds it, and an external reviewer will read the section as the document telling on itself.

**F8 · CRITICAL · The central construction is called *dithering* and has a 28-year lineage. The document cites nobody. · "The proposal", ¶1 · verifiable YES**

Louis S, Gerstein GL, **Grün S**, Diesmann M (2010), *Surrogate Spike Train Generation Through Dithering in Operational Time*, **Front Comput Neurosci 4:127**, doi:10.3389/fncom.2010.00127. Verified from the paper itself, not from a search summary. It defines dithering as *"randomly shifting individual spikes"* by *"adding a random number drawn from the uniform distribution"*, for the purpose of testing *"whether observed spike synchrony exceeds what would be expected from firing rates and interval statistics alone."* That is the proposal's construction verbatim and the proposal's stated rationale verbatim, including the word.

Origin traced backward from that paper: **Date A, Bienenstock E, Geman S (1998), *On the Temporal Resolution of Neural Activity*, Technical Report, Division of Applied Mathematics, Brown University.** *Where I stopped and why:* that is a 1998 university technical report; I could not locate an open copy, so the root is confirmed by citation from Louis et al. 2010 but not read. Intermediate applications the same paper credits: Nadasdy et al. 1999; Hatsopoulos et al. 2003; **Shmiel et al. 2006**, which is where *teetering* comes from.

Statistical framing: **Amarasingham A, Harrison MT, Hatsopoulos NG, Geman S (2012), *Conditional modeling and the jitter method of spike resampling*, J Neurophysiol 107(2):517–531, doi:10.1152/jn.00633.2011** — which **bugarach's own README already cites**, at line 651, for LoCo and CoactDetect's null. The citation the proposal needed was in the repo the whole time.

**F9 · HIGH · The "we changed our minds mid-design" argument is the published argument for jitter over shift · "It dissolves a confound…" · verifiable YES**

Amarasingham et al. 2012's entire contribution is that jitter is a *conditional* inference: coarse rate structure — including drift — is preserved by construction, so the test isolates fine timing. The document derives this from scratch, presents it as the reason it abandoned the circular shift, and asks reviewers to check it. It is checked, published, and fourteen years old.

**F10 · CRITICAL, and it is a design defect rather than a citation problem · "Under a dither with small J, the drift survives identically in both classes and therefore carries no gradient at all" and the open question "Does the objective admit a trivial solution?" · verifiable YES**

**Stella A, Bouss P, Palm G, Grün S (2022), *Comparing Surrogates to Evaluate Precisely Timed Higher-Order Spike Correlations*, eNeuro 9(3):ENEURO.0505-21.2022**, doi:10.1523/ENEURO.0505-21.2022. A systematic comparison of six surrogate methods — uniform dithering, uniform dithering with dead-time, joint-ISI dithering, ISI dithering, trial shifting, window shuffling. Two of its measured results land directly on this proposal:

1. **The "quantization onto the imaging grid" worry is not a candidate — it is measured, with a magnitude.** Uniform dithering followed by binning and clipping loses **up to 10% of spikes** relative to the original, because dithering produces more Poisson-like ISIs, shorter intervals collapse into single bins, and the significance threshold drops. Stella et al. report this as a false-positive generator. The proposal's discriminator would have a 10% count difference to key on, and re-quantization is exactly the step the proposal identifies and then leaves open.

2. **The stated rate-invariance guarantee is false at rate transitions.** Stella et al.: dithering *"convolves firing rates with the dither window, smoothing sharp transitions."* So a sharp rate step is smoothed in the dithered class and not in the real one. The document's claim that drift *"survives identically in both classes"* holds for slow modulation and **fails wherever the rate changes on a timescale near J** — which, given the document's own statement that one of the corpus drugs *"is known to raise both event frequency and the fluorescence baseline over time"*, is a live case. This is the answer to the document's own review question #2, *"does the surrogate leak?"*, and the answer is yes, in a way the document currently claims is structurally impossible.

3. **The first open question already has a third, published answer.** The document poses per-onset dither versus per-cell rigid displacement as an unresolved dichotomy. Louis et al. 2010 exists precisely because that dichotomy is false: **joint-ISI dithering** and **dithering in operational time** conserve both firing rate and ISI statistics, which is what the document says neither of its two options can do. Stella et al. then benchmark them against each other.

**F11 · HIGH · "The optimal discriminator computes a monotone function of the likelihood ratio" is a named theorem, stated as an original observation · "The proposal", ¶3 · verifiable YES**

This is noise-contrastive estimation: **Gutmann M, Hyvärinen A (2010), AISTATS, PMLR 9:297–304**, and **(2012), JMLR 13:307–361**. The optimal NCE discriminator equals the Bayes posterior and recovers the density ratio between the data and the noise distribution. Same statement as the GAN discriminator optimum (Goodfellow et al. 2014, Prop. 1). The claim is *correct* — it is the load-bearing theoretical justification in the document — and it is a citation, not a derivation. Leaving it uncited makes the strongest paragraph in the proposal look like hand-waving to exactly the reviewer who would recognise it.

**F12 · MEDIUM · The objective itself has a name in statistics: the classifier two-sample test · verifiable YES**

**Lopez-Paz D, Oquab M (2017), *Revisiting Classifier Two-Sample Tests*, ICLR, arXiv:1610.06545.** Train a classifier to separate two samples; its held-out accuracy is the test statistic; chance accuracy is the null. Applied to a recording and its surrogate, that is this proposal's training objective and — notably — also its proposed negative control (*"a model that still separates them"* is a C2ST rejecting the null). The document's control is a C2ST under the null and should be described as one; that framing brings a ready-made significance test rather than an eyeballed "flat".

**F13 · MEDIUM · "Localization comes free" is a decade-old benchmarked recipe, named but uncited · "From a window label to a detector" · verifiable YES**

Weak clip-level label + MIL pooling → frame-level event times is the standard formulation of **weakly-supervised sound event detection** (DCASE). Attention pooling as the permutation-invariant aggregator: **Ilse M, Tomczak JM, Welling M (2018), *Attention-based Deep Multiple Instance Learning*, ICML, PMLR 80:2127–2136** — which also gives the proposal's "attention weights are a participation readout" claim its precedent, since instance attention as an interpretability readout is that paper's headline. On the specific choice the document leaves open — smooth maximum versus alternatives — **Wang Y, Li J, Metze F (2019), *A comparison of five multiple instance learning pooling functions for sound event detection with weak labeling*, ICASSP** compares max, average, exponential-softmax, linear-softmax and attention pooling on exactly the localization question. The proposal treats this as a design choice to be made; there is measured evidence.

Permutation-equivariance over the cell axis is **Zaheer et al. (2017), *Deep Sets*, NeurIPS**. Low severity, but it is the standard citation for the property the document claims "by construction".

**F14 · NO FINDING — the assembly-detection disclaimer is accurate · "What we are not claiming", last bullet · verifiable YES**

I checked this because the brief asked whether the assembly literature already does something equivalent. It does not. **Lopes-dos-Santos V, Ribeiro S, Tort ABL (2013), *J Neurosci Methods* 220(2):149–166** (PCA/ICA assembly detection) and **Russo E, Durstewitz D (2017), *eLife* 6:e19428** (CAD) both detect *recurring membership patterns* by pairwise significance testing and agglomeration; neither is trained, neither uses a discriminative surrogate objective, and neither scores event timing. That matches the project's own deep dive (`docs/todo/2026-08-17-literature-deep-dive-handoff.md`: *"across the assembly literature the metric is membership, never event timing"*). The document's bullet — including its reason, that the simulator draws fresh participants per event so there are no recurring assemblies to find — is correct as written.

**F15 · Overall framing · severity HIGH · verifiable NO (a judgment)**

Not overclaiming — the document claims nothing. **Underclaiming in a way that will cost it credibility**, because a reviewer who recognises dithering, NCE and weakly-supervised MIL will conclude the drafter did not look, which is what the document itself admits. Recommended rewrite of "Not novelty" from a disclaimer into a *positioning* section: everything mechanical here is old — the surrogate (Date 1998 → Louis 2010), the inference (Amarasingham 2012), the objective (Gutmann & Hyvärinen 2010; Lopez-Paz & Oquab 2017), the localization (Ilse 2018, DCASE). What may be new is narrow and worth stating on its own: **using the discriminator as the detector rather than as a test statistic, at the level of the coordinated population event, in calcium imaging, calibrated to a stated false-alarm rate on real recordings.** That claim is small enough to survive and specific enough to be checked, and it is stronger than the current bullet.

## Part 4 — Residual ⚠ flags (required by my checklist)

**⚠ R1 · Literatures searched, and the ones I did not.** Searched: spike-train surrogate methodology (dithering/jittering/teetering; Grün, Diesmann, Gerstein, Amarasingham lines); contrastive and self-supervised learning on neural population data; classifier two-sample testing and noise-contrastive estimation; weakly-supervised sound event detection and multiple-instance learning; calcium-imaging assembly detection; surrogate-data testing for nonlinearity. **Not searched:** the **self-supervised anomaly-detection** literature, where "train a discriminator against a deliberately corrupted copy of the input" is a standard recipe (CutPaste, Deep SVDD and successors) — that is the field most likely to hold a near-identical construction under a different name, and I did not search it. Also unsearched, and already flagged in `README.md:686-690` as never searched by anyone here: genomics peak calling, seismological STA/LTA, changepoint detection, adaptive image thresholding. **An unsearched field is a residual ⚠, not an absence of prior art.**

**⚠ R2 · Nobody was asked, as far as I can tell.** This is the cheapest check in the review and I cannot run it. The project has a live correspondence channel with **Thomas Kreuz** (`docs/kreuz_note.md`; the April 2026 exchange recorded in `docs/todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md`), and **Sonja Grün's** group is the authority on dither surrogates and wrote the paper (F10) that answers this proposal's two open questions. Before this goes out for external critique: one email to Grün, one to Kreuz. If either has already been asked, that answer is citable evidence — cite and date it, and per `CLAUDE.md` paraphrase rather than quote, since this repo is public.

**⚠ R3 · Hansen 1973 is cited by this project and read by nobody in it.** See F4.

**⚠ R4 · The 1998 root of dithering (Date, Bienenstock & Geman) is confirmed by citation, not read.** No open copy located. Verified to one step short of the root.

## Marginal note, flagged as outside my lane

*"Four more are small neural networks"* and the heading *"Ten detectors"* do not reconcile with the tree or with the document's own next paragraph. `src/bugarach/learn/nets/` contains **six** architectures — `tiny.py`, `trace.py`, `tube.py`, `tube_guard.py`, `tube_ratio.py`, `tube_ratio_guard.py` — and the document itself then says *"Five of the six architectures…"* and *"The sixth, `tiny`…"*. So it appears the counts should be six learned and twelve total, with "the four learned variants" (the tube family) correct where it stands. Arithmetic, not attribution — passing it to whoever owns numeric consistency because it sits inside the sentence carrying F1.

---

## Role 3 consistency — `murderboard-cross-examiner`

*Recovered from `agent-a4445e5eac161e0e2.jsonl`; 15,177 characters.*

GRANT 3 ok — Read, Grep, Glob

## Cross-Examiner — consistency findings

Surface examined: the full HTML artifact (prose, table, SVG figure and caption, footer) against `docs/GLOSSARY.md`, `docs/FOUNDATIONS.md`, `docs/model_track.md`, `docs/performance_table.md`, `docs/detector_history.md` §4, `current_export.toml`, `src/bugarach/learn/nets/`, `src/bugarach/emit.py`, `src/bugarach/score.py`, `src/bugarach/simulate.py`, `src/bugarach/detectors/sce.py`.

### Arithmetic that checks out (stated so the clean part leaves a trace)
Every corpus row reconciles: 29+38=67, 9.5+12.6=22.1, 950+1169=2119, 18,011+19,685=37,696, 6,772+16,072=22,844. Ratios follow from the table: 18011/6772 = 2.66 ≈ "2.7", 19685/16072 = 1.22 ≈ "1.2". 22.1 h / 67 = 19.8 min ≈ "just under 20 minutes". "10 to 61 cells" matches the ROIs/recording column. Cohort counts match `current_export.toml` (`senktide` 29, `ttx` 38). Figure: 14 rows drawn in each panel, 7 marks in 7 distinct rows at the aligned column, 67 marks per panel in both, axis 0–60 s with 15s/30s/45s/1m ticks — caption's "fourteen cells", "one minute", "seven cells participate" all hold.

### Findings

| # | Location | Issue | Sev | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| 1 | §"Where we are", heading + para 2 vs the code block below it | **"Four more are small neural networks" is contradicted two sentences later by its own listing of six.** `src/bugarach/learn/nets/` registers exactly six architectures (`trace, tiny, tube, tube_guard, tube_ratio, tube_ratio_guard`, one `@register` each) and `performance_table.md` §2 prints all six as detector rows. The doc then says "five of the six architectures" and "the sixth, `tiny`" — so it counts six and four in the same section. | **critical** | Pin one basis: "six written by hand, six learned" and "twelve detectors". Where "four" is meant, say "the four `tube` variants". | yes |
| 2 | Lede ("six written by hand, four learned"), h2 "Ten detectors, and structurally one idea", and "the ten detectors are not ten approaches … measured ten ways" | **The "ten" figure is wrong three times over** and it is the section's organising claim. Twelve detectors exist. | **critical** | "Twelve detectors … measured twelve ways", heading likewise. | yes |
| 3 | §"Where we are", bullet "Two of the **four learned variants** fire on a single cell" | Same word "four" now names a *different* population (the tube family) than the lede's "four learned" (all learned detectors). Two of six architectures are log-ratio; two of four tube variants are. | high | "Two of the four `tube` variants — the log-ratio pair —". | yes |
| 4 | §"Limits", "Not a claim about any drug… Nothing here says what tetrodotoxin or senktide does" vs §"Train on the baseline windows" and §"It dissolves a confound" | **Direct self-contradiction.** The document does state what both drugs do: TTX "is not a silencing control — events persist… fast stream falling to about half… slow stream at roughly two and a half times baseline", and senktide "raises both event frequency and the fluorescence baseline over time". Both are restatements of FOUNDATIONS §9 / another project's results, which the Limits bullet says "are not ours to state". | **critical** | Either drop the Limits bullet's absolute form ("we state two facts about the preparation, both cited to FOUNDATIONS §9 and not measured here"), or replace the two passages with citations that do not restate the effect sizes. | yes |
| 5 | Chip "nothing measured" vs byline "Corpus figures measured…" vs §Limits "The only measured numbers in this document are the corpus counts" | **The third statement is false and the first contradicts the second.** Measured numbers also appearing: F1 0.125 and 0.681, "eight seeds over four held-out folds", "74–82% of cells", the 0.46/2.50 stream ratios, "10 to 61 cells", "a third of them not at all". | high | Chip → "nothing measured *here*"; Limits bullet → "the only numbers measured *for this document* are the corpus counts; the rest are quoted from internal records and flagged where they are". | yes |
| 6 | §"Train on the baseline windows…" final para: "that contrast is, at present, a question no code in our project computes" | **Contradicts FOUNDATIONS §9**, which records the contrast as already computed *with these ports*: "Confirmed with these ports (2026-08-14): `sce_detect` and `loco_detect` over the 39 archived baseline+TTX slices detect coordination in 92–100% of them under TTX, with SLOW at or above baseline (SCE 1.24, LoCo 1.28)." | high | "…a contrast this project has run on an archived slice set (FOUNDATIONS §9) but does not compute over the current export folder." | yes |
| 7 | §"The critical choice": "Our **six** hand-written detectors use a **circular shift** null"; and §"It dissolves a confound": "their null destroys all cross-cell structure" | **Four of six, not six.** Per GLOSSARY: CoactDetect (circular-shift null), LoCo (percentile of a circular-shift surrogate pool — `detector_history.md` line 483), locust (per-cell roll), binned SCE (`surrogate_model="circular_shift"`, `sce.py:105`). rate+context tests against a *mean context rate* and SPIKE-synch runs hysteresis on a synchronization profile — neither builds a shift null. | high | "Four of our six hand-written detectors use a circular-shift null (CoactDetect, LoCo, locust, binned SCE)." | yes |
| 8 | §"Where we are", first bullet: "The participation count is written as `NA` on every learned call. … A model that summed the cells away never had a participation variable to report." | **The tree does not support the causal framing, and arguably not the fact.** `emit.DETECTOR_FIELDS` (emit.py:100–122) contains only the six hand-written detectors — there is no learned entry, so `events_from` raises on one today. More damaging to the argument: `"rate"` (rate+context, hand-written) carries `n_roi=None`, i.e. a *hand-written* detector also reports no participation. The missing count is therefore not diagnostic of cell-axis collapse. | high | Re-check where a learned call actually writes `NA`, and drop or qualify "This is not an output-format oversight" — rate+context is the counter-example inside the same file. | yes |
| 9 | §"The dither width is a declared, interpretable parameter": "*J* states, **in samples**…" vs §Controls: "*J* is declared **in the same units as the tolerance**" | **Unit contradiction, twice.** The scorer's tolerance is `tol_sec` — seconds (`score.py:106, 211`). So J cannot be both in samples and in the tolerance's units. | high | Pick one: J in samples (FOUNDATIONS §6 permits it) and say "the same *quantity* as the tolerance, expressed in samples", or declare J in seconds. | yes |
| 10 | Same paragraph: "the same quantity as the **jitter** our simulator uses" | `simulate.jitter_sec` is documented as "SD of participant onset jitter" in **seconds** (simulate.py:379, 456). J is defined here as the **half-width of a symmetric distribution**. An SD and a half-width are not the same quantity, and the units differ again. | medium | "…closely related to the simulator's `jitter_sec`, which is an SD in seconds rather than a half-width in samples." | yes |
| 11 | §"The problem", para 1: "tens of cells, twenty minutes, a few thousand events" vs the corpus table | Same population, two values. The table's baseline windows average just under 20 minutes and carry 60,540 onsets across 67 recordings — **≈900 per recording, both streams pooled**, not "a few thousand". | medium | "…a few hundred to a couple of thousand events", or state the basis (whole recording vs baseline window). | yes |
| 12 | §"Ten detectors" para 3: "it scores 0.125 against a **best of 0.681**" | Agrees with `performance_table.md` §2 (`tube` 0.681) but **contradicts `model_track.md`**, whose headline for the same model is "0.668 ± 0.061". One quantity, two published values, and the proposal quotes neither's provenance. | medium | Quote 0.681 with the source ("the bake-off table, 8 seeds × 4 folds") and file the model_track/performance_table disagreement — it is a companion-doc defect, not this document's. | yes |
| 13 | §"Where we are" para 1: "their internal lineage audit traces **three of them** to the radar … CFAR, greatest-of CFAR, and a relative of ordered-statistic CFAR" | The three named CFAR variants map onto **two** detectors in `detector_history.md` §4: rate+context (CA-CFAR), LoCo `maxlt` (GO-CFAR), LoCo's percentile-of-pool (OS-CFAR kin). "Three of them" reads as three detectors. | medium | "…traces three of their mechanisms, across two detectors, to…". | yes |
| 14 | Footer: "the constant-false-alarm-rate family from the radar literature (Finn & Johnson 1968; **Hansen 1973**; Rohling 1983)" | The repo's own primary-source audit — the only place a PDF was read in full — cites **Hansen & Sawyers, *IEEE T-AES* AES-16(1), Jan 1980, 115–118** (`detector_history.md:464`). GLOSSARY still says "Hansen 1973" and is stale on the same point. | medium | Use Hansen & Sawyers 1980; flag the GLOSSARY row for the same fix in this change. | yes |
| 15 | Throughout: "The **corpus**" (eyebrow), "one of the drugs in our corpus", "the whole background range the corpus contains", "Two constraints the corpus forces" | **RETIRED word.** GLOSSARY: *"RETIRED: 'corpus' (Tony, 2026-08-22). … the real recordings the lab approved are the export folder."* The document already uses "the export folder" correctly in the table note and the producer section, so it names one thing two ways. | high | Replace every instance with "the export folder" / "these recordings". Section eyebrow → "The export folder". | yes |
| 16 | §"Where we are": "one adapted from the Cossart lab's **CICADA**" | Names a *bugarach detector* by the upstream tool's name in a public, outward-facing document. GLOSSARY and FOUNDATIONS §7 are explicit: CICADA is the upstream tool, **locust** is the detector here, and "a modified port does not carry the original's name in a public UI". (The footer's attribution sentence is correct and should stay.) | high | "one is **locust**, a modified partial port of the Cossart lab's CICADA; one is **SPIKE-synch**, built on the Kreuz lab's SPIKE-synchronization measure." | yes |
| 17 | Corpus table header: "cell traces" alongside "ROIs / recording"; body text "cells", "cell axis", "cell population" | Two names for the same axis inside one table, and **"cell trace" is a new term with no glossary entry**. The checklist rule is that a new term is added to the glossary in the same change. | medium | Standardise on ROI in the table ("ROI traces"), keep the prose's "cells — regions of interest, ROIs" gloss in the opening, and add the term to GLOSSARY if it is kept. | yes |
| 18 | §"Localization comes free": "fields here range from **10 to 61** cells" | Matches this document's own table, but **contradicts GLOSSARY's K entry**, which says "fair across recordings running **10 to 51** ROIs". One of the two is stale against the current export. | medium | Reconcile against the folder and fix whichever is wrong **in the same change** (the glossary row, most likely). | yes |
| 19 | §Controls, the K paragraph | Consistent with GLOSSARY's single K definition (a percentage, set by a person during review, moves the headline by an order of magnitude) — **no defect**, recorded so the check leaves a trace. One gap: the document describes MAHICE (machine proposes, person judges) in three places without ever naming it, while GLOSSARY requires outward-facing text to spell it out on first use *if used*. | low | Optional: name it once — "machine-assisted human identification of coordinated events (MAHICE, this project's own coinage)". | yes |
| 20 | §"The corpus" opening: "a brightness step makes **74–82%** of cells appear to fire at once" | Presented as a range; `current_export.toml` gives **two per-stream numbers**, 74% fast and 82% slow. FOUNDATIONS §9 requires a claim to name the stream. | medium | "…makes 74% of cells fire at once in the fast stream and 82% in the slow." | yes |
| 21 | Corpus section + table vs `current_export.toml` | **Counting basis never pinned.** The 67 is a subset of an 84-recording export (`steps_excluded`); 17 recordings of that export are in neither cohort and the document never says so. The bare number also collides with two unrelated 67s and 85s in the tree — FOUNDATIONS §9's "67 of 85 slices" (dead-ROI verdicts, `.mat` store) and `model_track.md`'s "the 85 real recordings". | high | Add one sentence under the table: "These 67 are the senktide-first and TTX-first views of the 84-recording `STEPS_EXCLUDED` export; 17 recordings fall in neither cohort." Then every N in the document reconciles to that roster. | yes |
| 22 | §Falsification, bullet 2: "If performance collapses **when artifact-removed data is used**, the model learned the artifact" | **Inverted relative to the corpus section**, which states the training data *already* has artifacts removed. As written there is no baseline to collapse from. (The paired `PRE_ARTIFACT_KILLER` export makes the intended test possible — the sentence just has it backwards.) | medium | "If performance is markedly higher on the artifact-*retaining* export than on the artifact-removed one, the model learned the artifact." | yes |
| 23 | Figure caption: "**Schematic, not data.** … gamma-distributed per-cell rate, **seed 7**" | The caption asserts a reproducible draw but names no generator, script or module, so nothing in the tree can reproduce the panel; and "not data" sits oddly beside a specific seed. No other figure claim is unverifiable — 14 ROI, 7 participants, one minute all check against the SVG. | low | Either name the generating tool, or drop "seed 7" and "gamma-distributed" and let "schematic" stand alone. | no (nothing to check it against) |
| 24 | Figure SVG, raster rects | The stylesheet defines `.mk rect{fill:var(--mark)}` but **no element carries `class="mk"`** — the 134 raster rects have no fill and fall back to black, so in dark mode the raster disappears against `--ground:#0F1413`. This also makes the caption's claim that "the raster carries one ink" untrue of the file as written. Noted here only because it breaks figure↔caption agreement; **rendering verification is role 10's**. | medium | Add `class="mk"` to both `<g>` wrappers. | yes |

### The one thing to fix first
Findings 1–3 and 21 are the same defect in two populations: the document never pins a canonical counting basis. Fixing it is two declarations — **twelve detectors = six hand-written + six learned architectures (four of them `tube` variants)**, and **67 recordings = the senktide-first (29) and TTX-first (38) views of the 84-recording `STEPS_EXCLUDED` export, counted over baseline windows only** — after which every remaining N in the document reconciles.

Files: artifact at `<repo>/docs/proposals/2026-09-10-coordination-without-labels.html`; the two companion rows that are themselves stale and should be fixed in the same change are the "10 to 51 ROIs" line in `<repo>/docs/GLOSSARY.md` and the "Hansen 1973" attribution in the same file.

---

## Role 4 hostile reviewer — `murderboard-reviewer-2`

*Recovered from `agent-a42ba5df1d4cbaa6c.jsonl`; 50,203 characters.*

GRANT 4 MISMATCH — missing Grep, Glob; holds Read, Bash

(No forbidden editing tools. I substituted `rg`/`grep`/`find` through Bash, so no check was skipped; the gap is in the grant, not in the coverage.)

---

# Reviewer 2 — adversarial findings

Ordered by severity. Every numeric claim below I derived myself and the derivation is reproducible from the commands in this transcript.

---

## BLOCKING — "a lone cell carries no discriminative signal at all" is false, and the document's own optimality claim is what makes it false

**Location:** "The proposal" section — *"a lone cell bursting carries **no discriminative signal at all**… The failure mode is not penalised after the fact; it is absent from the gradient."*

**Issue.** Real onsets carry a hard minimum inter-onset interval — an event extractor cannot emit two onsets of one cell inside one calcium transient's rise-and-decay. Per-onset dithering has no such floor, so the dithered class contains within-cell intervals whose probability under the real class is **exactly zero**. That is a *support* difference, not a distribution difference: the likelihood ratio on such a window is infinite, and a Bayes-optimal discriminator classifies it perfectly using one cell and no cross-cell information whatsoever.

So the two central claims destroy each other. If the discriminator really "computes a monotone function of the likelihood ratio," it will find the impossible interval **first**, because nothing else on offer has infinite odds. The document's optimality argument is not neutral toward the lone-cell argument — it is the proof against it.

I put numbers on it, with a refractory floor of 1 s, a 0.1 s grid (`simulate.py` `grid_sec` default), 32 ROIs, and the corpus table's own implied rate of 0.0158 Hz/cell:

| burstiness | J=0.5 s | J=1.0 s | J=2.0 s |
|---|---|---|---|
| none (pure renewal, hard floor only) | 0.058 | 0.122 | 0.182 |
| mild (15%) | 0.383 | 0.682 | 0.787 |
| moderate (35%) | 0.703 | 0.890 | 0.973 |

— probability that a single 60 s training window contains at least one within-cell impossible interval. Even in the assumption-free case with **no bursting at all**, 12% of windows at J=1 s are perfectly separable on within-cell evidence, and 9.3% of cells carry a certificate somewhere in a 20-minute recording. The document's chosen illustration is "a lone cell **bursting**" — the worst case it could have picked.

The document already knows the mechanism. It is the first item under *Questions we have not resolved*: *"Displacing every onset independently destroys each cell's own interval structure… which means the model could win on within-cell statistics."* That sentence and the no-discriminative-signal sentence cannot both stand, they are ~1,400 words apart, and neither cross-references the other. A reader who stops at the proposal section — which is where the benefit is *sold* — carries away a claim the document itself retracts in an appendix.

There is a third instance of the same knowledge, filed under the wrong heading: the corpus warn-note says *"A discriminator can memorize an individual cell's interval signature"* and treats it as a **fold-splitting hygiene** problem. It is not. It is the objective's global optimum.

**Severity:** blocking.

**Suggested fix.** Strike the "no discriminative signal at all" claim and the "absent from the gradient" sentence; they are unsupportable in the per-onset form. Replace with the honest version: *per-onset dither introduces a within-cell support violation that dominates the objective, so the lone-cell property is a claim about the per-cell-rigid variant only, and the per-onset variant is disqualified by it.* Promote the interval question out of the open list into the design, since it decides whether the construction works at all. Then state the refractory floor τ as a declared parameter and require J ≪ τ, or use rigid per-cell displacement and accept the boundary problem. Additionally: move the "memorize an interval signature" sentence out of the fold-splitting note and into the objective's own failure analysis.

**Verifiable against a source:** yes — `src/bugarach/simulate.py` (grid quantization, `min_sep_sec`), `src/bugarach/learn/encode.py` (binary frame raster), and the corpus table's own rate. The refractory value itself needs the producer.

---

## BLOCKING — the negative control is near-blind to the leak that dominates the objective, and the document instructs the reader to read its silence as a pass

**Location:** "Controls" — *"dither it once, and use that as the positive against a further-dithered negative… A model that still separates them is reading something about the surrogate construction"*, and the falsification entry *"The control is not flat… fatal."*

**Issue.** The control puts **one dither on the positive**. Every leak that arises *from* dithering is therefore already present in the control's positive class, and the control can only see the *increment* the second dither adds — not the level. For any leak that saturates, that increment is near zero.

Measured on the same synthetic corpus (J = 1.0 s, moderate burstiness):

| | P(window has impossible within-cell ISI) | share of onsets in the outer-J band |
|---|---|---|
| real — 0 dithers | **0.000** | 0.0157 |
| 1 dither — control POSITIVE | **0.932** | 0.0144 |
| 2 dithers — control NEGATIVE | **0.953** | 0.0135 |

The training objective faces `0.000 vs 0.932` — a support difference, perfect separability. The control faces `0.932 vs 0.953` — two points apart, deep in saturation. **The control is flat precisely because the leak is total.** Under the document's stated rule, that flatness is read as clearing the design.

This is the "a check that cannot fail — and the danger is that it PASSES" pattern in its pure form: a verification step whose reference class already contains the defect it was written to detect. The document then compounds it by making the control load-bearing twice over — it is *"the only thing standing between the design and a confident artifact detector"* and it also sets the operating threshold α.

Two further defects in the same construction:

- **It can fail for a correct reason (false-fatal).** Two independent dithers compose to an effective kernel of width √2·J, so the control's classes are not equally smeared. Genuine coordination living between J and √2·J is still partially present in the positive and further reduced in the negative — a *real* signal. The document pre-commits to calling any non-flat result "fatal to the approach rather than something to tune around," so a working design gets killed by its own control. The control's two outcomes each have two readings, and the document assigns exactly one to each.
- **It is near-blind to the artifact the falsification list calls fatal.** A whole-field brightness step is smeared by J in the positive and √2·J in the negative — largely gone from both — so the control is close to flat on field steps, while the deployed model meets them undithered.

**Severity:** blocking.

**Suggested fix.** State what the control has power against and what it does not, per leak, before building it. Add a control that is not saturated: a *fully independent* per-cell surrogate (rigid circular shift or Poisson resampling at matched rate) as the positive, so the comparison is against a class with zero dither-induced structure rather than one already full of it. Add a direct diagnostic that does not go through a learned model at all — count sub-refractory within-cell intervals and outer-J onset density in the real and dithered classes, and require the *level* to be zero rather than the increment to be small. Withdraw the pre-commitment that a non-flat control is fatal until the √2·J asymmetry is corrected (dither the negative from the positive with an independent draw of width J, and match the positive's total smear).

**Verifiable against a source:** yes for the arithmetic and the saturation numbers; the magnitude on real recordings needs the export folder.

---

## BLOCKING — the design trains quiet and deploys busy, which is the direction this project has already measured as harmful, and the document does not mention it

**Location:** "Train on the baseline windows, deploy on the treated ones."

**Issue.** `docs/model_track.md` states as a measured result: *"It transfers worse than two of the six from a quiet background to a busy one, which is a negative result about its own central claim. **Fit busy, deploy quiet.**"* And, as the one model fact the app must encode: *"fit on the busier recordings and deploy downward… the difference between a **−0.24 transfer penalty and a +0.12 gain**."*

The proposal's central deployment plan is baseline → treated. Under TTX, by the document's own paragraph two lines earlier, the slow stream runs at **~2.5× baseline**. That is quiet → busy: the measured-bad direction, worth ~0.36 F1 in the project's own numbers, and the proposal never names it.

The proposal does not have to abandon the design — the FOUNDATIONS §9 constraint is real and binding — but it cannot present the constraint as costless (*"it turns out to be the right experimental design anyway"*) while the tree holds a measurement saying it costs a third of the score. This is the strongest measured result the project has about a learned detector, and it points against the proposal's headline design choice.

**Severity:** blocking.

**Suggested fix.** Add a paragraph naming the transfer asymmetry, citing `model_track.md`, stating the direction the design forces and what it is expected to cost. Then either (a) argue why a dither objective should be immune to the transfer penalty that the centre-surround model showed — and make that a falsification entry with a stated test — or (b) accept it and state that the baseline-to-treatment contrast carries a transfer confound that must be bounded before any treatment number is read. Note also that the fast stream falls to 0.46× baseline, so the two streams transfer in *opposite* directions and a single pooled statement is not available.

**Verifiable against a source:** yes — `docs/model_track.md` lines 17-18 and 109-111, `docs/FOUNDATIONS.md` §9.

---

## BLOCKING — "provably no coordination" contradicts the document's own drift argument, so α is not a false-alarm rate

**Location:** "The control also sets the threshold" — *"real recordings, real fields, real per-cell rates, **provably no coordination**. That is a measured false-alarm rate on real data across the whole background range the corpus contains."*

**Issue.** Three separate overclaims in two sentences, and the first is refuted by the document's own selling point.

- **"Provably no coordination" is false and the document argues so itself.** The whole case for dither over circular shift is that *"the drift survives identically in both classes"* — i.e. dithering deliberately **preserves** shared cross-cell modulation coarser than J. A dithered recording therefore has no coordination *finer than J* and retains all of it coarser than J. The control's positives are not coordination-free; they are band-limited. So the number calibrated on them is not a false-alarm rate, it is a rate of firing on coarse co-modulation — which the document elsewhere insists is a real and different phenomenon. Both claims cannot stand.
- Even at fine timescales, "provably" is wrong. Dithering multiplies the cross-spectrum by the kernel's transfer function, which for a uniform kernel is a sinc — it has zeros at isolated frequencies and **nonzero sidelobes between them**. Fine-timescale coordination is attenuated, not nulled.
- **"across the whole background range the corpus contains"** — the corpus is baseline windows only, by the design's own constraint. The deployment regime (treated windows, slow stream at ~2.5× baseline) is by construction *outside* the calibrated range. α is calibrated on a range that excludes where it will be used.

**Severity:** blocking.

**Suggested fix.** Replace "provably no coordination" with *"no coordination at timescales finer than J; coordination coarser than J is retained by construction."* Rename α from a false-alarm rate to *"rate of firing on a surrogate retaining only coarse co-modulation."* Delete "across the whole background range the corpus contains" or qualify it to "across the baseline background range," and add an explicit statement that α is not calibrated for the deployment regime.

**Verifiable against a source:** no — this is internal to the document plus standard properties of the dither kernel.

---

## MAJOR — "Dithering creates no wrap and leaves nothing of that kind to find" is false; it trades one splice per recording for two edge artifacts per window

**Location:** "A circular shift has a splice…" — *"Dithering creates no wrap and leaves nothing of that kind to find."*

**Issue.** The document rejects circular shift because wrapping creates **one anomalous interval per cell per recording**, and a network has the capacity to find it. Correct. But per-onset dither creates a boundary artifact at **both ends of every training window**, in every cell, in every example:

- Onsets within J of a boundary are displaced across it. If dropped, the dithered class has a systematic **onset-density deficit** in the outer-J band that the real class does not. Measured above: outer-J onset share falls 0.0157 → 0.0144 in one dither, an 8% relative deficit at a fixed, known location.
- If clipped instead — which is what `src/bugarach/learn/encode.py` does today, `idx = np.clip(((v - t0) / dt).astype(np.int64), 0, n_frame - 1)` — you get a **pile-up on exactly frame 0 and frame n−1**. That is another support violation: real recordings essentially never place onsets on the boundary frame, dithered ones do with probability rising in J. Infinite likelihood ratio, again with zero cross-cell content. At J=2 s, 40% of windows carry a pile-up; at J=5 s, 74%.

The circular shift's splice is one event per cell per ~20 minutes. The dither's edges are two bands per cell per **window**. By the document's own capacity argument, this is worse, not better — and it is offered as one of the three reasons the design exists.

**Severity:** major.

**Suggested fix.** Strike "leaves nothing of that kind to find." State the boundary problem explicitly and specify the mitigation: dither over a context window strictly wider than the scored window and score only the interior (a J-margin crop on both sides), so no scored frame is within J of a place events can leave from. Then say the clip-vs-drop choice out loud — the current encoder clips, which is the worse of the two, and must not be reused unchanged. Note also that the *first* open question ("per-cell rigid displacement… reintroduces a boundary problem") treats the boundary problem as unique to the rigid variant; it is not.

**Verifiable against a source:** yes — `src/bugarach/learn/encode.py` line 119.

---

## MAJOR — "exactly the quantity all six hand-written detectors approximate" is hand-waving, and the document contradicts it three sections later

**Location:** "The proposal" — *"the optimal discriminator… computes a monotone function of the likelihood ratio between the real recording and the rate-matched null: which is to say, an estimate of **exactly the quantity all six hand-written detectors approximate**, learned rather than specified."*

**Issue.** The first half is textbook and fine: for a balanced binary discrimination the Bayes-optimal D satisfies D/(1−D) = p/q. The second half — the equivalence — does not survive contact.

- **Different null, therefore different ratio.** The six use a circular shift. The proposal uses a dither. LR(p ‖ q_shift) ≠ LR(p ‖ q_dither). The document *knows* this and says so as a virtue three sections later: *"This is a sharper question than the six hand-written detectors ask: their null destroys all cross-cell structure, so they cannot separate 'these cells fired together' from 'these cells were both busy this minute.'"* If the dither null asks a sharper question, the ratio is not the quantity the six approximate. The document cannot claim both the equivalence and the improvement.
- **Different object.** The six emit a *local, per-time* contrast. The Bayes optimum here is a *window-level* scalar. The document itself needs multiple-instance learning to bridge the two, which concedes they are not the same thing.
- **Dither is not an independence null.** Circular shift produces per-cell independence; dither does not — it band-limits the joint. So the dither LR is a contrast between "coordination at all timescales" and "coordination coarser than J," not "coordination vs chance." A genuinely broad recruitment (say 3 s) with J = 0.5 s is **invisible to this detector by construction**, and the document never states that ceiling.
- **Optimality is vacuous at the stated capacity.** The Bayes optimum is attained in the infinite-capacity, infinite-data limit. The document elsewhere reassures on data sufficiency by pointing at models of "one to two thousand parameters." A 1–2k parameter model is not the Bayes optimum, so the statement licenses nothing about the artifact being proposed. Invoking optimality to justify the design and small capacity to justify the corpus size are load-bearing in opposite directions.

**Severity:** major.

**Suggested fix.** Keep the likelihood-ratio statement, drop "exactly" and drop the equivalence. Say instead: *"the Bayes-optimal discriminator for this task is a monotone function of the likelihood ratio between the recording and its dither — a different null from the six detectors' circular shift, and therefore a different quantity. It is band-limited: coordination coarser than J is present in both classes and cannot be detected."* Add the timescale ceiling to the *Limits* section, where "cannot see coordination broader than J" belongs. Remove the appeal to optimality wherever it is used to argue about what a 1–2k parameter model will do.

**Verifiable against a source:** no — internal, plus standard discriminator theory.

---

## MAJOR — "the drift survives identically in both classes" is not right, and the failure is exactly at burst edges

**Location:** *"Under a dither with small J, the drift survives **identically in both classes** and therefore carries no gradient at all."*

**Issue.** Dithering convolves the point-process intensity with the dither kernel: E[λ_dith] = (λ ∗ k_J). Slow drift — minutes — is preserved to O((J²/2)·λ″) and the argument is fine *to first order*. "Identically" is not fine, and the error term is not negligible where the document needs it least:

- Any curvature in the rate **at the J scale** is attenuated. A burst with a sharp onset has exactly that curvature: the real class has a step, the dithered class has a ramp of width ~2J. That is a discriminative feature, it is entirely **within-cell**, and it is a second independent counterexample to the lone-cell claim — again on the document's own chosen example, "a lone cell bursting."
- The reviewer prompt's instinct is right: dithering *does* change local event density at burst edges. That is not a second-order nuisance; it is the same first-order smoothing that destroys the coordinated column, applied to a single cell's envelope.

**Severity:** major.

**Suggested fix.** Replace "identically" with the correct statement and its condition: *"drift on timescales ≫ J is preserved to O(J²λ″); structure with curvature at the J scale — including the edges of a single cell's burst — is attenuated in the dithered class and is discriminative without any cross-cell information."* Then either add a falsification test (train on single-cell windows only; the objective must be at chance) or state the leak in *Limits*. A single-cell-only training run is the cheapest possible probe of the whole lone-cell claim and it should be built **before** the encoder, alongside the negative control.

**Verifiable against a source:** no — analysis.

---

## MAJOR — the grid-quantization open question is aimed at a non-issue, while the real quantization defect goes unmentioned

**Location:** *"Does the objective admit a trivial solution we have not thought of?"* — *"quantization onto the imaging grid is one candidate, since displaced events must be re-quantized and the original ones were already on-grid."*

**Issue.** Asked to work out whether a discriminator can win on quantization residue alone: **no, not in the form the document fears**, and the document is spending its most prominent open question on it.

`encode.py` floors every onset to a frame and sets a **binary** cell — *"Several onsets in one frame stay 1 — distinct activity, never a spike count."* Both classes land on integer frames. Sub-frame phase, which is the only thing quantization residue could live in, is destroyed by the encoder for real and dithered alike. There is no residue in the representation the model sees. If J is drawn as an integer number of frames the question does not even arise.

But there **is** a re-quantization defect, and it is not the one asked about. Because the raster is binary, re-quantization changes the number of ones per row: two onsets sharing a frame in the real class become two ones after displacement, and two separated onsets can collide into one. So the document's flat assertion that *"Every cell keeps its own firing rate, its own number of events"* is **false at the representation the model actually consumes**. It is true in the event list and false in the raster. At corpus rates the effect is small — collisions are rare at 0.016 Hz on a 0.1 s grid — but it is a per-row marginal difference with zero cross-cell content, and the document states count preservation as a structural guarantee rather than an approximation.

**Severity:** major (the misaimed question wastes the review it is asking for; the count claim is an unqualified guarantee that is not one).

**Suggested fix.** Rewrite the open question to name what actually leaks — within-cell interval support, window-edge density, burst-edge curvature — and demote grid residue to a sentence saying why the binary frame encoding makes it moot. Qualify the count claim: *"each cell keeps its event count exactly in the event list, and up to frame collisions in the binary raster."* Draw J as an integer number of frames and say so.

**Verifiable against a source:** yes — `src/bugarach/learn/encode.py` docstring and lines 116-120.

---

## MAJOR — "This detector needs no K" trades one declared number for four undeclared ones, and K was the *adaptive* one

**Location:** *"this detector needs no **K**… That trades a number nobody can choose for one anybody can state."*

**Issue.** The trade is stated as one-for-one. It is one-for-four, and the document supplies every one of the replacements itself:

1. **J** — its own open question says it does not have a principled way to choose it, and asks whether it should be swept.
2. **α** — a declared false-alarm rate is only as good as the control it is declared on, and that control is in trouble above.
3. **The dither scheme** — per-onset vs per-cell-rigid is the document's *first* unresolved question, and it *"changes what 'together' means at the margin."* A parameter that changes what the detector means is not a minor knob.
4. **The MIL smooth-max temperature.** Never named. A smooth maximum over per-frame scores is a soft OR whose sharpness controls how much concentrated evidence is needed to raise the window score — which is a **soft coactivity floor**. K has not been removed; it has been made continuous, hidden inside a softmax, and left undeclared. This is the strongest form of the objection: the document's own architecture reintroduces the quantity it advertises eliminating.

And the direction of the trade is worse than stated. GLOSSARY records K as set *relative to each recording's ROI count* — it **adapts to field size**. Fields here range 10 to 61 cells, a 6× span the document highlights as a reason for permutation-equivariance. J adapts to nothing. Trading an adaptive parameter for a fixed one is not obviously a gain and is asserted as one.

Separately, the three-way identification is unearned: *"It is the same quantity as the tolerance our scorer already uses… and the same quantity as the jitter our simulator uses."* Those are three different things that share units — a match tolerance, a Gaussian jitter SD (`jitter_sec`, default 0.05 s), and a uniform dither half-width. The simulator's default jitter SD is 0.05 s against a `grid_sec` of 0.1 s, i.e. **quantization already dominates the planted jitter**, so "the same quantity" does not survive even inside `simulate.py`.

**Severity:** major.

**Suggested fix.** Rewrite the claim as: *"K is replaced by J, α, the dither scheme, and the pooling temperature. J and α are declarable and sweepable; the other two are open."* Name the MIL temperature explicitly as a soft coactivity floor and add it to the open questions. Drop the three-way identification or replace it with the precise relation (e.g. "J should be set commensurate with the scorer's match tolerance," with the reason). Address the field-size adaptivity K had and J does not.

**Verifiable against a source:** yes — `docs/GLOSSARY.md` lines 127-145 and 195-205, `src/bugarach/simulate.py` lines 379-380.

---

## MAJOR — "Ten detectors" is twelve, and the section's whole argument is a count

**Location:** "Ten detectors, and structurally one idea"; *"Four more are small neural networks"*; *"the ten detectors are not ten approaches."*

**Issue.** `docs/MILESTONES.md` records the bake-off as **"Twelve detectors, one bake-off — six hand-written and six learned"** (`20432a9`, `docs/learned/bakeoff.json`). The document says ten, and four learned — while its own code block lists **six** architectures and its own next paragraph says *"Five of the six architectures"* and *"The sixth, `tiny`."* And *"Two of the four learned variants fire on a single cell"* should be two of six.

This is not a typo I would leave to the consistency checker, because the count *is* the argument: a section headed "structurally one idea" is claiming that N detectors collapse to one, and it has the wrong N and contradicts itself inside three paragraphs.

**Severity:** major.

**Suggested fix.** Twelve detectors, six hand-written and six learned. Reconcile "four" with the six-item code block throughout, including "two of the four learned variants."

**Verifiable against a source:** yes — `docs/MILESTONES.md` line 93; `src/bugarach/learn/nets/` contains six modules.

---

## MAJOR — the warn-note discloses the seed limitation and conceals the supersession, which is worse than no note

**Location:** the warn-note under "Ten detectors" — *"The scores come from an internal bake-off at eight seeds over four held-out folds… Every learned number in this project is one training run per fold, so none of them carries a seed error bar."*

**Issue.** Three problems, and the third is the one that matters.

- **The note contradicts itself.** "Eight seeds" and "one training run per fold, no seed error bar" cannot both describe the same numbers. `docs/RESET.md` records `0.681 ± 0.049 … four folds, **one training run per fold and no seed replication anywhere**`. MILESTONES' "eight seeds" refers to the bake-off's data seeds. The note conflates data seeds with training seeds — precisely the distinction RESET exists to protect.
- **The 0.681 is quoted without its retraction.** RESET, on that exact number: *"⚠ **And both numbers were computed at a calibration that has since been superseded** — see part 5. They are the best published figures and they are not current ones."* The proposal quotes 0.681 and 0.125 with a caveat about seeds and **no caveat about the superseded calibration**. A note that discloses one limitation and omits a larger one reads as full disclosure and is not — it is more damaging than no note, because it buys the reader's trust with the smaller admission.
- **This makes the proposal a fourth document arguing from a superseded measurement.** `docs/todo/2026-09-08-three-documents-argue-from-the-flat-field.md` exists for exactly this failure, and its stated lesson is CLAUDE.md's: *"grep the tree for the same shape before closing it out… that was one `grep` and nobody ran it."* The grep was not run here either. This is an external-facing document, which is the case the todo's own header says must be murderboarded first.

**Severity:** major.

**Suggested fix.** Add the supersession to the warn-note in the same sentence as the seed limitation, citing RESET §5. Resolve eight-seeds-vs-one-run-per-fold — the correct phrasing is "eight data seeds, one training run per fold, no training-seed replication." Add a row to `docs/todo/2026-09-08-three-documents-argue-from-the-flat-field.md`, since this is now the fifth site. Consider whether the 0.681/0.125 pair is needed at all: the argument of that section (five of six architectures collapse the cell axis) is carried by the code block and needs no score.

**Verifiable against a source:** yes — `docs/RESET.md` lines 196-200; `docs/MILESTONES.md` line 93; `docs/todo/2026-09-08-three-documents-argue-from-the-flat-field.md`.

---

## MAJOR — "Two of the four learned variants fire on a single cell" overstates its own source, which revised itself specifically to prevent that reading

**Location:** *"**Two of the four learned variants fire on a single cell.** Found by eye on a rendered raster in September 2026."*

**Issue.** The source is `docs/todo/2026-09-08-the-ratio-tube-cannot-count-cells.md`, and it says something narrower and more careful:

- The measured lone-call fractions are **5.7% and 6.5%**, against a chance rate of 96%, i.e. ratios of 0.06 and 0.07.
- The source's own instruction: *"**Read this as a comparison, not as an indictment.** Both ratio variants are still 15× better than dart-throwing; what they are is **ten times worse than the two subtract variants**."*
- The source carries a same-day revision whose entire purpose was to add the chance correction, because *"A raw lone percentage is not comparable across detectors."* Without the correction, an earlier draft *"put a red flag on locust, whose 12% is against a chance of 98%."*

The proposal drops the rate, drops the denominator, drops the differential framing, and states the bare extreme as a categorical behaviour. It is the exact error its source revised itself to stop, reintroduced one document downstream, in the copy that goes outside.

"Found by eye on a rendered raster" is also not the evidence. The by-eye observation was the *prompt*; the finding rests on two measured lines (a planted-k ladder and a chance-corrected tally).

**Severity:** major.

**Suggested fix.** *"Two of the six learned variants place 6–7% of their calls on one ROI or none, against a 96% chance rate — roughly ten times the rate of the two subtract variants, which differ by one kernel operation. The mechanism is that a log-ratio reports contrast and discards magnitude."* Attribute the evidence to the ladder and the chance-corrected tally, not to the eye. Note that the source is marked *"Not murderboarded… If any of it reaches an outside reader, murderboard that artifact first"* — this is that reader.

**Verifiable against a source:** yes — `docs/todo/2026-09-08-the-ratio-tube-cannot-count-cells.md`, tables at lines 32-37 and 55-60, revision note at 47-53.

---

## MAJOR — a falsification criterion that cannot be executed on the stated corpus

**Location:** falsification list — *"**It fires on field steps and little else.**… If performance collapses when artifact-removed data is used, the model learned the artifact. **fatal**"*

**Issue.** The test requires two versions of the data, with and without artifacts. The document states there is only one: the export is artifact-removed by the producer, *"every surviving row reads zero,"* and the loader *"drops both columns silently."* There is no artifact-bearing arm to compare against, and obtaining one means reading something other than the export folder — which the project's export contract forbids (*"The export folder is the input. The store is closed."*). So the criterion has no executable form on the corpus the proposal declares.

This matters more than a normal untestable claim, because the objective is stated to *actively reward* finding whole-field artifacts. The proposal has named its most dangerous failure mode and attached to it a test it cannot run.

Related, and I would escalate it from a note to a precondition: the producer section reports that the two field-step flag columns are undefined in the contract and dropped by the loader. On a design whose objective rewards the artifact, silently dropping the only column that could verify removal is not a courtesy note to the producer — it is a live single point of failure.

**Severity:** major.

**Suggested fix.** Replace with a criterion that can be run on one corpus: **plant** synthetic whole-field steps into the real recordings at known times and measure whether the per-frame score fires on them; require the score at planted steps to be indistinguishable from background. Move the flag-column issue from the producer notes into the design as a precondition — define the columns in `export_folder_spec.md`, stop dropping them, and refuse to train on a folder whose field-step flags are absent or nonzero.

**Verifiable against a source:** yes for the loader-drop and the contract gap; the "74–82% of cells" figure needs its own source check (Prove It's lane).

---

## MODERATE — "Localization comes free" is the MIL assumption presented as a derivation, and the document rates it "redesign" elsewhere

**Location:** *"Localization comes free, and that is not obvious"* — *"the only way the model can win the window task is to concentrate its evidence on the few moments that actually betray the real recording."*

**Issue.** "The only way" is false whenever the discriminative signal is **diffuse**, and every leak identified above is diffuse: an impossible interval anywhere in the row, a density deficit in two edge bands, a burst-edge ramp, a per-row count shift. A smooth max is won just as well by raising the floor everywhere as by a spike at one frame. The MIL premise holds only if the *sole* discriminative structure is localized to coordinated moments — which is the thing under dispute.

The document then rates "It does not localize" as a falsification with verdict **redesign**, i.e. it knows this is contingent. A property whose failure triggers a redesign is not one that "comes free"; it is a load-bearing assumption. Section title and falsification list disagree.

The same paragraph also introduces the smooth max's temperature without naming it — see the K finding.

**Severity:** moderate.

**Suggested fix.** Retitle to "Localization, if the multiple-instance assumption holds," and state the assumption in terms: *"this requires that the only discriminative structure is localized; any diffuse leak wins the window task without concentrating, and the per-frame head is then not a detector."* Cross-reference the leaks. Name the pooling temperature.

**Verifiable against a source:** no — internal.

---

## MODERATE — "unbounded negatives" is the augmentation-is-not-data trap, and the document rebuts it two sections earlier

**Location:** *"Is twenty-two hours enough?"* — *"every epoch can draw fresh surrogates, so the effective negative set is unbounded. The positives are not."*

**Issue.** Fresh dithers are deterministic functions of the same 67 recordings with fresh noise. The information available about the true coordination distribution is bounded by the positives and does not grow with the number of surrogate draws; resampling the null adds variance reduction, not sample size. This is a well-known trap and the document presents it as reassurance.

The document also contradicts it. Its own corpus warn-note says the unit of independence is the **recording** — *"the same recording appearing in training and test leaks and the number means nothing"* — which is the correct accounting, and it is 67, not unbounded. It cannot claim recording-level dependence for the split and draw-level independence for capacity.

And the effective n is smaller than 67 once the design's own constraints are applied: folds stratified by experimental group (FOUNDATIONS §9: effects run in **opposite directions** by group), separated by cohort (senktide 2.7 fast:slow, TTX 1.2 — the document flags that a pooled slow-stream model *"would be learning mostly from one cohort"*), and split by recording. The document never computes what is left. The comparison point in the tree is unfavourable: `docs/conditioned_run.md` records that a related question needs *"eight folds at twelve seeds — 96 recordings, not a finer cut of"* what exists.

The parameter-count reassurance is also imported from the wrong model. *"one to two thousand parameters"* describes the current tube (1,149). The proposal replaces it with a per-cell temporal encoder plus attention pooling over cells, whose parameter count is never stated and is certainly larger. Using the old architecture's mass to argue the new architecture's data sufficiency is a non-sequitur.

**Severity:** moderate.

**Suggested fix.** Strike "unbounded." Say: *"the effective sample size is the number of independent recordings — 67 before stratification, fewer after — and resampling the surrogate reduces variance without adding information."* State the proposed encoder's parameter count. Compute and state the per-fold recording count under the group-and-cohort stratification the document itself requires, and compare against `conditioned_run.md`'s eight-folds-at-twelve-seeds figure.

**Verifiable against a source:** yes — `docs/FOUNDATIONS.md` §9 (group-dependence), `docs/conditioned_run.md` line 226, `src/bugarach/learn/nets/tube.py` (parameter count).

---

## MODERATE — the corpus is pooled across the design factor FOUNDATIONS §9 says may not be pooled

**Location:** the corpus table and the warn-note beneath it.

**Issue.** FOUNDATIONS §9, in terms: *"**Group-dependence is not optional.** Effects run in opposite directions by group (ORX up, male unchanged, diestrus down under TTX), so a pooled across-group number hides sign changes and is not admissible on its own."*

The corpus table breaks down by cohort only. Experimental group appears exactly once in the document, as a **fold-stratification** requirement — *"folds must be stratified or one can come out entirely single-group."* Stratifying folds is not reporting by group. Nothing in the design says the deployed baseline-to-treatment contrast will be reported per group, and that contrast is the proposal's stated scientific payoff (*"a question no code in our project computes"*). Under §9 a pooled version of it is inadmissible on its own.

Per my own checklist I should not accept an unavailability claim without checking: the group variable **is** available — §9 names the groups and cites the campaign files (`darkroom/constellation/coordBA_uniform_<detector>_{ttx,senktide}`, `oxc_ttx_persistence.csv`). So this is not a data gap, it is an omitted breakdown.

**Severity:** moderate.

**Suggested fix.** Add group as a column to the corpus table (recordings and baseline time per group per cohort), and state in the design that any baseline-to-treatment contrast is reported **per group and per stream**, never pooled, citing §9. Note that the fast and slow streams also move in opposite directions (0.46× and 2.50×), so "stream" is a second non-poolable factor.

**Verifiable against a source:** yes — `docs/FOUNDATIONS.md` §9 lines 303-321 and 370-372.

---

## MODERATE — attention weights asserted as a participation measurement, validated against a baseline that is chance by construction

**Location:** *"The attention weights are a participation readout. A detection can finally name the cells it meant."* And the falsification entry, *"no better than the cell's own rate would predict."*

**Issue.** Two separate problems.

- Attention weights are the model's internal allocation, not a measurement of participation, and there is a substantial literature against reading them as explanations. The body states it flatly; only the falsification list hedges. The proposal's most attractive secondary benefit is asserted where it is sold and hedged where fewer people read.
- The stated baseline is **chance by construction on this generator**. `simulate.py` draws participants uniformly — `rois = np.sort(rng.choice(nR, size=np_, replace=False))` at lines 676 and 705 — so a cell's rate carries **zero** information about whether it participated. "Better than the cell's own rate would predict" is therefore "better than chance," which is a floor, not a bar. On real recordings participation is plausibly rate-dependent, so a model that clears this bar on simulation has demonstrated nothing about the case that matters. `docs/model_track.md` makes the adjacent point: *"it cannot reward membership structure at all."*

**Severity:** moderate.

**Suggested fix.** Downgrade the body claim to *"the attention weights are a candidate participation readout, to be validated, not an explanation."* Restate the falsification baseline honestly — *"the simulator draws participants uniformly, so the rate baseline is chance; clearing it is a floor"* — and add a stronger check: hold out the planted membership, and require the attention weights to recover it at a stated precision/recall against a **rate-matched permutation** null, not against rate itself.

**Verifiable against a source:** yes — `src/bugarach/simulate.py` lines 676, 705; `docs/model_track.md` lines 46-60.

---

## MINOR — the figure visually asserts the count-preservation the analysis contradicts, while being labeled "not data"

**Location:** the two-raster figure and its caption.

**Issue.** I read the marks rather than the caption. The figure is internally clean — 67 marks in both panels, 14 rows in both, **no row's mark count changes**, implied J ≈ ±1.6 s, coordinated column 0.35 s wide on 7 distinct rows (8 marks; one cell fires twice inside the column, consistent with the caption's "seven cells"). Axis and lane conventions are followed: one x-axis on the bottom panel, the down-pointing triangle in a lane above the raster it describes, nothing drawn on the raster.

But the exact cleanliness is the problem. A dither drawn with no boundary loss and no re-quantization collision is what makes the counts match — and count preservation is precisely the structural guarantee the text asserts (*"Every cell keeps its own firing rate, its own number of events"*) and that the raster encoder does not deliver. The figure is doing evidentiary work for a contested claim while being labeled "Schematic, not data," which is where a reader's guard is lowest.

Two smaller things visible only in the marks: panel A's smallest within-cell interval is **0.187 s**, below any plausible calcium refractory and under two frames at a 0.1 s grid — so the schematic's "real" recording already contains intervals real data cannot produce, and cannot illustrate the interval argument in either direction. And the implied J (±1.6 s) is **4.5× the coordinated event's own width** (0.35 s), a ratio the text never states and which bears directly on how much drift a "small J" actually smooths.

**Severity:** minor (as an image defect) — but it is the visual half of the blocking count/ISI findings.

**Suggested fix.** Either redraw with the boundary handling and grid re-quantization the design actually uses, so the figure shows the edge deficit rather than concealing it, or add one sentence to the caption: *"drawn with an idealized dither — no boundary loss, no re-quantization; the encoder's binary frame raster does not preserve counts exactly."* State J and the event width as numbers in the caption so the reader can see the 4.5× ratio. Raise panel A's minimum within-cell interval above the refractory floor.

**Verifiable against a source:** yes — I re-derived every number above from the SVG `rect` coordinates and the figure's own axis calibration (x = 64 at t = 0, 10.667 px/s).

---

## MINOR — "Nothing in it has been measured" is false several times over

**Location:** masthead chip *"nothing measured"*; *"Nothing in it has been measured"*; *Limits* — *"The only measured numbers in this document are the corpus counts."*

**Issue.** The document also quotes 0.681, 0.125, 74–82%, 0.46, 2.50, 2.7, 1.2, 10–61 cells, and 15/24 of the corpus table. The intent is clearly "nothing about *this proposal* has been measured," but the sentence as written is false, and the *Limits* entry states the false version as a positive claim about the document's own contents. In a document whose entire pitch is that it is honest about what it does not know, an inaccurate honesty claim is expensive.

**Severity:** minor.

**Suggested fix.** *"Nothing about this design has been measured; no code exists. The measured numbers quoted here come from the corpus, from FOUNDATIONS §9, and from internal bake-offs, and each is sourced where it appears."*

**Verifiable against a source:** no — internal.

---

## MINOR — unsupported provenance on the `jitter` slot

**Location:** *"The binned-SCE detector's signature accepts `surrogate_model="jitter"` and raises `NotImplementedError` — **an option inherited from the MATLAB original that was contemplated and never built**."*

**Issue.** The slot is real — `src/bugarach/detectors/sce.py` lines 124-125 raise exactly that. The *provenance* half is not supported by anything at the site: the code carries no comment about the MATLAB original and no note about what was contemplated. As written it implies the MATLAB authors considered a dither null, which would be a (weak) independent endorsement of the design — so the unsupported half is the half that carries rhetorical weight.

**Severity:** minor.

**Suggested fix.** Either cite where the inheritance is recorded, or reduce to what the code shows: *"the binned-SCE port accepts `surrogate_model="jitter"` and raises `NotImplementedError` — a slot with nothing in it."*

**Verifiable against a source:** yes for the slot; no for the provenance, which is what makes it a finding.

---

## Two things claimed as benefits that are restatements of assumptions

Filed together because they share a shape, and my checklist asks for them by name.

- **"Why the rate-invariance is structural rather than hoped-for."** True *as stated* — the classes share per-cell rates by construction — but it is invariance to a quantity the surrogate was defined to hold fixed. It says nothing about invariance to anything the dither does not preserve: local density, burst envelope, ISI distribution, edge density. The document then extends the guarantee to the failure that motivates the whole proposal (lone-cell firing), and that extension is exactly where it breaks. The honest form is: *"the model cannot key on total rate. It can key on anything else the dither changes, and the list of those things is the risk register above."*

- **"It dissolves a confound that the circular shift creates."** The dissolution is the *definition* of the dither, not a discovery about it: a kernel of width J removes structure finer than J and leaves the rest. Stating that drift survives is restating "small J." The benefit is real, but so is its inseparable cost — the detector is blind to coordination coarser than J — and only the benefit is stated. A property and its dual should appear in the same paragraph.

---

## What I checked and found clean

The corpus table's arithmetic is internally consistent (29+38=67; 950+1,169=2,119; 18,011+19,685=37,696; 6,772+16,072=22,844; 9.5+12.6=22.1 h) and both cohort ratios reproduce (2.66 and 1.23 against the stated 2.7 and 1.2). The FOUNDATIONS §9 handling is correct and unusually careful — TTX is stated as **not** a silencing control, the split by stream is given with both magnitudes, and treatment effects are explicitly disclaimed as another project's. The lineage attributions (CICADA/Cossart, SPIKE-synch/Kreuz, CFAR/radar), the BSD-3 statement, and the no-private-correspondence note are all present and correct. The figure follows the raster conventions exactly. The novelty disclaimer and the retraction of the earlier prior-art claim are handled better than most published methods sections manage.

**Files that matter to these findings:**
- `<repo>/docs/proposals/2026-09-10-coordination-without-labels.html`
- `<repo>/src/bugarach/learn/encode.py` — the binary raster and `np.clip(..., 0, n_frame - 1)` at line 119
- `<repo>/src/bugarach/simulate.py` — lines 379-381 (`jitter_sec`/`grid_sec`/`min_sep_sec`), 676 and 705 (uniform participant draw)
- `<repo>/docs/model_track.md` — the transfer asymmetry
- `<repo>/docs/RESET.md` — 0.681 and its supersession
- `<repo>/docs/MILESTONES.md` — twelve detectors
- `<repo>/docs/todo/2026-09-08-the-ratio-tube-cannot-count-cells.md` — the chance-corrected lone-call rates
- `<repo>/docs/todo/2026-09-08-three-documents-argue-from-the-flat-field.md` — the ledger this document should join

**One sentence for the main thread, if only one fix lands:** the negative control was built so that both of its classes already contain the leak that dominates the training objective (0.932 vs 0.953, where the real objective faces 0.000 vs 0.932), and the document tells the reader to treat that control's flatness as clearing the design.

---

## Role 5 line edit — `murderboard-kill-your-darlings`

*Recovered from `agent-abe5f4f7e6ad0f178.jsonl`; 34,077 characters.*

GRANT 5 MISMATCH — missing Bash; holds Read, Grep, Glob

**Run findings (about the run, not the artifact).** Two, both belonging in the ledger:

1. `murderboard_prose.sh` **was not run**. I hold no Bash, so I cannot execute it. I also could not find it: `Glob **/murderboard_prose.sh` returns nothing in either tree. My checklist says "not run is a failure, not a clean result" — so this is declared, not glossed. I substituted Grep for the mechanical half (banned constructions, ordinal back-references, British spellings) and counted blocks by hand; those results are below and are hand-counts, not tool output.
2. The banned-construction list I ran is the **house list in `doc_review_process.md` role 5**, verbatim, plus the two project rules in the task brief.

**Mechanical pass — banned constructions.** One hit: `robustness` (line 691). No hits for *not just X but Y*, *it's not about A it's about B*, *it's worth noting*, delve, leverage, seamless, crucial, landscape, tapestry, or *"In today's ___"*. **British spellings, three** — `docs/writing_conventions.md` requires American English: `behaviour` (258), `penalised` (316), `labelled` (337, inside the SVG `aria-label`, so it reaches a screen reader).

**Passage test — the honest result.** No block is grossly longer than its point. Longest is 122 words (the two-constraints note, 651–661); median is around 70. What the test *does* find here is a repeated **throat-clearing opener**: five blocks announce what they are about to say before saying it. Those are listed below. The payload-at-the-end pattern shows up twice (633–638, 645–649) and the fix is promotion, not trimming.

---

## Findings

### Internal contradictions (highest severity — these are the ones a hostile reviewer will lead with)

| # | Location (quoted) | Issue | Sev | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| 1 | L672 "a control that manufactures data with provably **no cross-cell structure**"; L685 "**provably no coordination**" | Contradicted by the document's own drift argument, L535: "the drift survives **identically in both classes**." Shared slow modulation is cross-cell structure and it survives dithering. "Provably" is the strongest word in the document and it is attached to the one claim the document elsewhere refutes. The control is sound; the description of it is not. | **high** | "…a control that manufactures data with **no cross-cell alignment finer than *J*** — the timescale the detector is defined on." And L685: "real per-cell rates, and no alignment on the timescale the model is trained to see." | yes — internal |
| 2 | L292 "very nearly **its own interval statistics**" vs L793 "Displacing every onset independently **destroys each cell's own interval structure**" | Flat contradiction between the proposal and the open-questions section. The Open section is right; the proposal paragraph oversells. | **high** | L291–293: "Every cell keeps its own firing rate and its own number of events. Its interval statistics are perturbed — by how much is an open question, below." | yes — analytic |
| 3 | L292 "What the dither destroys, **and the only thing it destroys**" | Absolute claim, contradicted twice: by the interval-structure point above, and by L810–812 (re-quantization onto the imaging grid). | **high** | "What the dither destroys is the precise alignment of events across cells at timescales finer than *J*. Whether it destroys anything else is the question we most want checked." | yes — internal |
| 4 | L274 "an internal bake-off at **eight seeds** over four held-out folds" vs L277 "Every learned number in this project is **one training run per fold**, so none of them carries a seed error bar" | Eight seeds and one run per fold cannot both be true. One of these numbers is wrong and the caveat is the load-bearing one. | **high** | Resolve against the bake-off record, then state one. If it is genuinely one run per fold, delete "at eight seeds". | yes — against the bake-off record |
| 5 | L299 "an estimate of **exactly the quantity** all six hand-written detectors approximate" vs L537–540 "**their null destroys all cross-cell structure**, so they cannot separate 'these cells fired together' from 'these cells were both busy this minute'" | The proposal's headline claim (we learn the same quantity, better) is retracted three sections later (we learn a *different, sharper* quantity because their null is different). The second is the interesting claim; the first weakens it. | **high** | "…an estimate of the quantity the six hand-written detectors approximate — against a **different null**, which is the whole point, and which we come back to below." | yes — internal |
| 6 | L750 "**Not a claim about any drug.** Nothing here says what tetrodotoxin or senktide does." vs L640–643 "tetrodotoxin **is not a silencing control** — events persist under it and so does coordination… the fast stream falling to about half of its own baseline and the slow stream running at roughly two and a half times baseline" | The document does say what tetrodotoxin does, in numbers, and then denies having done so. Given the project's own foundations on this preparation, the denial is the part that is wrong. | **high** | Rewrite the Limits bullet: "**Not a finding about any drug.** The tetrodotoxin numbers above are the lab's, quoted to establish why we cannot train inside a treated window. Nothing here is our measurement of what either drug does, and treatment effects belong to a different project in this ecosystem." | yes — internal + against project foundations |
| 7 | L326 "This is the part **we most want reviewed**" vs L528 "the one **we would most like checked**" | Two different things carry the same superlative, ~200 words apart. A reviewer deciding where to spend attention gets no signal. | med | Keep the superlative at L326 (the surrogate choice, which is the section). At L528 write: "This is the reason we changed our minds mid-design." | yes — internal |
| 8 | L553 heading "**Localization comes free**" vs L722–724 "It does not localize. The window-level task is won, but the per-frame score does not concentrate… The multiple-instance assumption fails. `redesign`" | The heading asserts as settled what the Falsification section lists as an untested assumption whose failure forces a redesign. "Free" also hides the cost: an architecture change and an unproven assumption. | **high** | Heading: "**Where the event times come from, if the assumption holds**". Body opener: "The objective produces a label per *window*, but a detector must emit event times. The bridge is multiple-instance learning, and it is an assumption we have not tested." | yes — internal |

### Project style rules (CLAUDE.md rule 1: never refer back by a bare enumerated label)

| # | Location (quoted) | Issue | Sev | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| 9 | L804 "**The second** is more useful scientifically and more expensive." | Unambiguous violation. The reader must scroll back two sentences and count. | **high** | "Training a family at several fixed values is more useful scientifically, and more expensive." | yes — against CLAUDE.md |
| 10 | L224 "Our answer to **the third problem** so far has been to keep a person in the loop" | Violation — indexes into the bullet list above. | **high** | "Our answer to **the missing ground truth** so far has been to keep a person in the loop". | yes |
| 11 | L256 "**The sixth**, `tiny`, keeps the cell axis" | Violation. The code comment two lines up already names it correctly — "the exception". | **high** | "**The exception**, `tiny`, keeps the cell axis and is the one that does not train". | yes |
| 12 | L207 "Three things make it hard, and only **the first** is obvious." | Indexes an item the reader has not seen yet. | med | "Three things make it hard, and only **the timescale** is obvious." | yes |
| 13 | L313 "**A second property** falls out" | Ordinal back-reference to a "first property" that was never labeled (rate-invariance, in the panel above). | med | "Rate-invariance is not the only property that falls out. A lone cell bursting carries **no discriminative signal at all** — and that matters for the single-cell failure above." | yes |
| 14 | L771 "**Reasons are above.**" | Not an ordinal, but the same defect the rule exists to prevent: a pointer where a name belongs, in the one section written for readers who may not have read the rest. | med | "The reasons are the wrap splice, the declared timescale, and the drift confound — above." | yes |

### Naming, not indexing (rule 2) and units

| # | Location (quoted) | Issue | Sev | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| 15 | L661 "A slow-stream model trained on the pooled baselines would be learning mostly from **one cohort**." | Names neither cohort, when the table two inches above makes it computable (16,072 slow onsets vs 6,772). Consequence stated as a label. | **high** | "…would be learning mostly from the **tetrodotoxin** cohort, which contributes 16,072 of the 22,844 slow onsets." | yes — from the table |
| 16 | L268 "Found by eye on a rendered raster **in September 2026**." | Date as content, in a document dated 10 September 2026 — the date encodes nothing the reader can use. | med | "Found by eye on a rendered raster while preparing this proposal." | yes |
| 17 | L258 "it scores **0.125** against a best of **0.681**" | Bare numbers, no metric named, no "dimensionless". The provenance note calls them "the scores"; the reader never learns of what. | med | "it scores **F1 0.125** against a best of 0.681 (F1, dimensionless)". | yes — against the bake-off |
| 18 | L605–606 table headers `ROIs / recording`, `baseline onsets, fast`, `slow` | Units and structure live in the footnote, which the conventions forbid: `17 – 32 – 55` is unreadable as min–median–max without scrolling, and the `slow` column has lost its subject. | med | Headers: `ROIs / recording (min–med–max)`, `baseline onsets, fast (count)`, `baseline onsets, slow (count)`, `baseline time (h)`. | yes — against writing_conventions |
| 19 | L776 "The current export ships **two per-event columns** flagging them" | The columns have names in the export; the document withholds them, in the one section addressed to the people who own them. | med | Name both columns explicitly. | yes — against the export folder spec |

### Undefined jargon (the general-scientific reader)

| # | Location (quoted) | Issue | Sev | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| 20 | L186 "Does the **surrogate** leak?" | First use is in the opening ask, 100 lines before the definition at L288. The second of three things the document is asking for is unreadable on first pass. | **high** | "**Does the fake data leak?** The design trains a model to tell a real recording from a manufactured copy of it (a *surrogate*, defined below). The entire design rests on that copy being statistically identical to the original in every respect but one." | yes |
| 21 | L212 "'By chance' needs a **null**." | The bullet explains why a fixed threshold fails but never says what a null *is*. A methods-literate reader supplies it; a general reader does not. | **high** | "**'By chance' needs a null** — a model of what the data would look like with the coordination removed and everything else left alone." | yes |
| 22 | L270 "so **one onset** against a near-empty surround"; also the figure and the table | "Onset" is the document's unit of data and is never defined. L202 describes the thing ("the moments its calcium signal rises") without attaching the word. | **high** | L201–202: "…and, for each, the moments its calcium signal rises — its **onsets**." | yes |
| 23 | L627 "*Fast* and *slow* are the two **event streams** the producer exports" | Circular: defines a stream as a stream. First substantive use is L641 "splitting by stream", which then carries the paper's sharpest empirical claim. | **high** | "*Fast* and *slow* are two independent event detections run over the same fluorescence trace, separating rapid calcium transients from slow ones. Every recording carries both." | yes — against `docs/GLOSSARY.md` |
| 24 | L567 "**attention pooling** over cells at each frame" | Undefined, and it is the mechanism the participation claim rests on. L573 then relies on the reader already knowing what "attention weights" are. | **high** | "…then **attention pooling over cells** at each frame: a learned weighted average whose weights say how much each cell contributed. Those weights are the participation readout." | yes |
| 25 | L568 "This is **permutation-equivariant** by construction" | Explained by contrast with row-sorting, but never stated. | med | "The result does not depend on the order the cells are listed in — it is permutation-equivariant by construction, which is stronger than…" | yes |
| 26 | L238 "**cell-averaging** CFAR, greatest-of CFAR" | "Cell" in the radar literature means a range bin; "cell" everywhere else in this document means a neuron. Same word, two referents, one sentence apart from "Six detectors… their internal lineage audit". A careful general reader will read "cell-averaging" as averaging over neurons, which is nearly the opposite of what it means. | **high** | Add a clause: "…the radar constant-false-alarm-rate literature, where *cell* means a range bin rather than a neuron — cell-averaging CFAR, greatest-of CFAR…" | yes |
| 27 | L744 "**Contrastive** training against surrogate data is an old idea in several fields" | New jargon in the last third, plus "several fields" is vague where a name or two would cost four words. | low | "Training a model to tell real data from manufactured data — contrastive learning — is old in speech, vision and genomics, and we would be unsurprised…" | yes |
| 28 | L203 "Drawn, it is a **raster**." | Names the word without describing the picture (one row per cell, one mark per onset, time across). The figure caption at L499 assumes the layout. | med | "Drawn — one row per cell, one mark per onset, time running across — it is a **raster**." | yes |
| 29 | L186 "a **negative** distribution being exactly as hard as the **positive**" | ML class jargon at first use, and "as hard as" is vague — hard for whom, at what? | med | "…rests on the manufactured examples being **statistically identical** to the real ones in every respect but one." | yes |

### Sentences doing two jobs

| # | Location (quoted) | Issue | Sev | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| 30 | L236–239 "They differ in thresholding rule, in how the null is built, and in speed, **and** their internal lineage audit traces three of them to the radar…" | Two unrelated jobs (how they differ; where they came from) welded with a bare "and". | med | "They differ in thresholding rule, in how the null is built, and in speed. Three trace to the radar constant-false-alarm-rate literature…" | yes |
| 31 | L640–643 "tetrodotoxin is not a silencing control — events persist under it and so does coordination, splitting by stream, with the fast stream falling to about half… and the slow stream running at roughly two and a half times baseline in the lab's own campaign." | Three jobs in one sentence, and the two numbers — the load-bearing part — arrive last and subordinated. | med | "In this preparation **tetrodotoxin is not a silencing control**. Events persist under it, and so does coordination. The two streams move in opposite directions: in the lab's own campaign the fast stream fell to about half its baseline while the slow stream ran at roughly two and a half times." | yes |
| 32 | L688–691 "a detector that divides by its surround cannot fire in a *hot* window by arithmetic, so scoring zero there restates the arithmetic instead of measuring **robustness**, and the corresponding quiet-field test does not exist." | Three jobs, plus the one banned word in the document. | med | "A detector that divides by its surround cannot fire in a hot window; that is arithmetic, not a property we measured. Scoring zero there tells us nothing. The quiet-field test that would tell us something does not exist." | yes |
| 33 | L592–595 "Both are views on an export from which whole-field brightness artifacts have already been removed by the producer — a real contaminant here, since a brightness step makes 74–82% of cells appear to fire at once and is precisely the signature a coordination detector exists to find." | Two jobs, and "views on an export" is imprecise — the cohorts are subsets, not views. | med | "Both are drawn from an export the producer has already cleaned of whole-field brightness artifacts. That cleaning matters here: a brightness step makes 74–82% of cells appear to fire at once, which is exactly the signature a coordination detector exists to find." | yes |
| 34 | L296–300 "And the optimal discriminator for this task computes a monotone function of the likelihood ratio between the real recording and the rate-matched null**: which is to say,** an estimate of…" | Colon followed by "which is to say" — the punctuation cannot carry both. Also the claim is stated without its conditions (it holds for a Bayes-optimal classifier under a proper loss, not for the network you will actually train). | med | "The Bayes-optimal discriminator for this task computes a monotone function of the likelihood ratio between the real recording and the rate-matched null. A trained network is an approximation to it, with the usual caveats about capacity and loss." | yes — standard result |
| 35 | L776–779 "The current export ships two per-event columns flagging **them**, but our folder specification does not define **those columns**, so a future export has no stated obligation to carry **them** and no definition to carry **them** under." | Four pronouns, two referents (field steps, columns), one sentence. | med | Split into two sentences and name the columns (see finding 19). | yes |

### Throat-clearing, previews, and payload-at-the-end

| # | Location (quoted) | Issue | Sev | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| 36 | L179 "**We are asking for three specific things:**" | Third announcement of the same fact in nine lines: eyebrow "What we are asking for", heading "Three questions", then this. Preview of a list that starts on the next line. | med | Delete the sentence; end the paragraph at "Nothing in it has been measured." The `<ol>` needs no introduction. | yes |
| 37 | L243–245 "And here is the thing we noticed while preparing this proposal, which is really what prompted it. Look at what each network does to the cell axis in its first lines:" | Pure drumroll — 22 words that assert nothing and delay the code block that is the evidence. | med | "Four more are small neural networks. Look at what each does to the cell axis in its first lines:" | yes |
| 38 | L633–635 "This is a constraint we impose on ourselves and it turns out to be the right experimental design anyway." | Preview. The payload is the paragraph's last sentence ("Training a model on tetrodotoxin data and then asking whether tetrodotoxin changes coordination assumes the answer"), which is the sharpest sentence in the section and arrives fourth. | med | Promote: "Training a model on tetrodotoxin data and then asking whether tetrodotoxin changes coordination assumes the answer. Our project's foundations forbid it, and it is the right experimental design anyway." | yes |
| 39 | L639 "The constraint is sharper here than it sounds." | Preview of the sentence that follows it. | med | Delete; open with "In this preparation tetrodotoxin is not a silencing control." | yes |
| 40 | L528 "This is the reason we changed our minds mid-design, and the one we would most like checked." | Preview + duplicate superlative (see finding 7). The paragraph's real opener is "Real recordings drift". | med | "Real recordings drift, and that is why we changed our minds mid-design." | yes |
| 41 | L219 "**This is the crux.**" | Restates the emphasis the previous sentence already carried. | low | Delete. | yes |
| 42 | L681–682 heading "The control also sets the threshold, at a stated false-alarm rate" → body "**Which** is the part we did not expect." | A relative-pronoun fragment whose antecedent is a *heading*. Grammatically dangling; breaks for anyone reading headings as navigation, and for a screen reader. | med | "We did not expect this part. Calibrate the operating point so the model fires at a declared rate α on this control…" | yes |
| 43 | L178 "circulated before it is built **rather than after**" | "Rather than after" adds nothing to "before". | low | "…circulated before it is built." | yes |
| 44 | L647–649 "…rather than something the model was fitted to **— and that contrast is, at present, a question no code in our project computes.**" | Em-dash pivot to a closing flourish that introduces a new fact at the point where the paragraph has stopped doing work. | low | Promote it to its own sentence at the head of the paragraph, or cut. | yes |

### Redundancy across sections (lede / asking-for / not-claiming)

| # | Location (quoted) | Issue | Sev | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| 45 | "nothing measured" (chip L161), "everything else is a proposal" (L169), "Nothing in it has been measured" (L179), "Treat all of it as internal working material" (L278), "**Not a result.** Nothing here is measured. No code exists." (L746) | The same fact asserted five times in five registers. By the fifth, it reads as anxiety rather than discipline. | **high** | Keep the two chips (they are the at-a-glance surface) and the Limits bullet (which adds "The only measured numbers are the corpus counts"). Delete L179's sentence and L169's "everything else is a proposal". | yes |
| 46 | L181–185 "**Has this been done?** We have not established that any part of this is novel and we are not claiming it is. Our own prior-art pass… was retracted internally as too shallow to stand on." vs L741–745 "**Not novelty.** We have not established that this is new. An earlier internal claim… was retracted as unsupported — it rested on web searches, not on papers read." | Near-duplicate paragraphs, ~560 lines apart, with the second strictly more informative. | **high** | Cut the opener to the ask alone: "**Has this been done?** If the construction below is a known method under a name we failed to search, that is the most useful thing you can tell us. Our own prior-art pass was retracted as too shallow — see *What we are not claiming*." Let Limits carry the retraction detail. | yes |
| 47 | L190–191 "With no labels, a negative control is the only thing that can catch the model being wrong." vs L669 heading "With no labels, only a negative control can catch you" vs L670–672 | The same sentence three times, twice as a near-verbatim repeat. | med | In the opener, drop the general claim and keep only the ask: "**Is the control sufficient?** We propose one, below. We would like to know what it misses." | yes |
| 48 | L224–228 "keep a person in the loop… That does not go away under anything proposed here"; L702–706 "This does **not** remove the person from the loop, and we are not claiming it does"; L748–749 "**Not a replacement for the person.**" | Three statements. Only the middle one earns its place — it immediately follows the K claim, which is the sentence that could be misread. | med | Keep the Controls note. Shorten the problem-section note to "…the machine proposes candidates, a person judges them, and neither half is the instrument alone. What is proposed here changes only the machine half." Delete the Limits bullet. | yes |
| 49 | L168–169 "Corpus figures measured from the export folder on the date of drafting"; L623 "Measured from the export folder on 10 September 2026"; L833 "Corpus figures measured 10 September 2026 and current as of that date" | Same provenance three times. | med | Keep the table footnote (where the numbers are) and delete the other two. | yes |
| 50 | L166–167 byline vs L825–827 footer, both opening "bugarach — a browser-based viewer and Python port of six neural-coordination detectors…" | Near-verbatim repeat of the project description at both ends of the document. | low | Keep the footer version (it adds the audience and the licence); cut the byline to the drafting note. | yes |

### Ambiguity and precision

| # | Location (quoted) | Issue | Sev | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| 51 | "**we**" throughout — L156 "detectors we have", L529 "we changed our minds", L643 "the lab's own campaign", L764 "For the producer team" | Three distinct parties are implied — the authors, the producer team, the lab — and none is ever introduced. The document is addressed to outsiders and has no author line. A reader cannot tell whether "we" includes the producer team it later addresses in the second person. | **high** | Add one sentence to the byline: "*We* here means the bugarach team — the Python port and viewer. The MATLAB producer team, addressed directly near the end, and the lab that ran the experiments are separate groups." | yes |
| 52 | L243 "**Four more** are small neural networks" + L268 "Two of **the four** learned variants" vs the code block naming **six** architectures (`trace`, four `tube*`, `tiny`) and L254 "Five of **the six** architectures" and L235 "**Ten** detectors" | The counts do not reconcile on the page. Ten = six hand-written + four learned, but six architectures are shown, and the document never says that `trace` and `tiny` sit outside the four. A reader doing the arithmetic — which the section invites — gets 6 + 6 = 12. | **high** | State the exclusion once: "Four more are small neural networks, plus two that are not deployed: `trace`, registered as the control that gives up distinctness, and `tiny`, which does not train. All six share an architecture family, so look at what each does to the cell axis:" | yes — against the repo |
| 53 | L654 "effects in this preparation run in opposite directions by **experimental group**, so folds must be stratified" — while the section otherwise says "**cohort**" | Two words, unclear whether one referent. If group = cohort (senktide / TTX), use one word; if not, the constraint is undefined. | **high** | Pick one term and define it once at L592. If they differ, say what a group is. | yes — against project docs |
| 54 | L592 "two cohorts, split by which drug each slice **received first**" | "First" implies each slice received both drugs in sequence — a fact with direct consequences for what "baseline window" means, stated only by implication. | **high** | "…two cohorts, split by which drug each slice received first; every slice receives both, in one order or the other. The baseline window is the pre-drug stretch of each recording." | yes — against the export folder |
| 55 | L816 "**The models in question** are small — one to two thousand parameters" | Ambiguous: the proposed model does not exist and has no parameter count. Presumably the existing learned detectors, used as a size estimate. | med | "The existing learned detectors are small — one to two thousand parameters — and we would start in that range." | yes — against the repo |
| 56 | L213–215 "Cells here fire at rates spanning more than an order of magnitude, **a third of them not at all in a given window**, and the background moves" | Three-item list whose middle item has no verb and a different subject, so the grammar breaks; and the "a third" figure is stated as flatly as the sourced numbers elsewhere while appearing in no table. | med | "Cells here fire at rates spanning more than an order of magnitude, and about a third are silent in any given window. The background also moves over the course of a recording." Then source the third, or hedge it explicitly. | yes — against the export folder |
| 57 | L266 "A model that summed the cells away **in its second line** never had a participation variable to report." | Overspecific and inconsistent with the code block: the `tube` variants collapse *after* a max-pool, not in line two. | med | "A model that sums the cells away before its first temporal filter never had a participation variable to report." | yes — against the repo |
| 58 | L269 "**The log-ratio variants**" vs L688 "the **ratio** variants" vs the code block's `tube_ratio`, `tube_ratio_guard` | Three names for one thing. | low | Use "the ratio variants" throughout, and name them once: "the ratio variants (`tube_ratio`, `tube_ratio_guard`)". | yes |
| 59 | L316 "The failure mode is not penalised after the fact; **it is absent from the gradient.**" | Overclaim by a hair: the expected gradient contribution is zero; the realized one on a finite batch is not. In a document this careful, the hard version invites a cheap objection. | low | "…it carries no expected gradient." | yes — analytic |
| 60 | L221 "fitted on synthetic data that we generated **and therefore already understand**" | Non-sequitur as written — generating data does not confer understanding. The meaning is that the ground truth is held. | low | "…fitted on synthetic data whose ground truth we hold by construction." | yes |
| 61 | L758 "Running one against it today would produce **a win that means nothing.**" | A win for whom is not stated; the reader must infer that our detectors would flatter themselves. | low | "Running one against it today would flatter our detectors for a reason that has nothing to do with detection." | yes |
| 62 | L156–158 "asks one question: is there more coincidence here than the local background explains." | A question rendered as a statement with no question mark, while L209–212 punctuate the same construction differently. | low | "…asks one question: *is there more coincidence here than the local background predicts?*" | yes |
| 63 | L159 "**This** describes how, and where we think it breaks." | Bare "this" with no antecedent noun. Also: the lede promises a different question and never states it, so the reader must reach L287 to learn what the proposal is. | med | "We want to ask a different one — *can a model tell this recording from a copy of itself with the cross-cell timing destroyed?* — and to ask it of real recordings nobody can label. This proposal describes how, and where we think it breaks." | yes |
| 64 | L188 "We know **two ways** that fails and we expect there are more." | Vagueness posing as concision. The two ways are the wrap splice and the drift confound, five sections away, and are never labeled as the pair this sentence promised. | med | "We know two ways it fails — a circular shift leaves a splice to find, and it destroys the slow drift that both classes should share — and we expect there are more." | yes — internal |
| 65 | L684 "**real** recordings, **real** fields, **real** per-cell rates" | Tricolon carried by rhythm; the three items are one point (nothing about the background is synthetic). | low | "real recordings, with whatever fields and per-cell rates they actually have". | yes |
| 66 | L651–661, the "Two constraints" note | Two distinct constraints and their explanations run together in a single unbroken block with only bold run-ins to separate them — 122 words, the longest block in the document, and the one place where length and formatting compound. | med | Split into two `<p>` elements inside the note, one per constraint. (Boundary: whether the note *renders* as one block is agent 10's; that it *reads* as one is mine.) | yes |

### Headings

| # | Location (quoted) | Issue | Sev | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| 67 | L324 "**The negative distribution is the model**" | Aphoristic, and opaque to a general reader who has not yet met "negative distribution" (which is nowhere defined — see finding 29). A heading is navigation and must stand alone. | med | "**What the surrogate destroys is what the detector will mean**" | yes |
| 68 | L527 "**It** dissolves a confound that the circular shift creates" | The heading's subject is a pronoun with no antecedent inside the heading; in a table of contents or a screen-reader heading list it is meaningless. | med | "**A dither dissolves a confound the circular shift creates**" — or, better, name the confound: "**The circular shift makes slow drift look like coordination**" | yes |
| 69 | L519 "**The dither width is a declared, interpretable parameter**" | Restates a category ("interpretable parameter") where the section states a fact. | low | "***J* states, in samples, how close counts as together**" | yes |
| 70 | L669 "With no labels, only a negative control can catch **you**" | Second person appears once in the document, here. Who is "you" — the reader, or the authors? | low | "…only a negative control can catch the mistake." | yes |

---

**What I checked and did not flag.** MAHICE does not appear in the artifact (grepped; the brief listed it). `dither`, `K` and `tolerance` are each defined at or near first use and read cleanly. The Falsification section is the strongest block in the document — every bullet names a concrete observation and a consequence, and none of them hedges. The figure caption correctly states the project's raster rule and the down-triangle convention; the SVG's lane placement matches it (its only defect is the British `labelled` in the `aria-label`, finding under mechanical pass).

**One boundary note.** Findings 1–6 are internal contradictions I verified against the document itself, so they are line-editor findings. Where they also require checking an external record — the eight-seeds/one-run conflict (finding 4), the "a third of them" figure (56), the drug-order claim (54) — I have marked them verifiable and they belong to the claim-support role as well.

**Artifact reviewed:** `<repo>/docs/proposals/2026-09-10-coordination-without-labels.html`
**Rules applied from:** `<repo>/docs/writing_conventions.md`, `<repo>/CLAUDE.md`, `<repo>/docs/GLOSSARY.md`

---

## Role 6 methods expert — `murderboard-rtfm`

*Recovered from `agent-a7150c643c4319050.jsonl`; 28,633 characters.*

GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

**What I checked:** the built artifact at `<repo>/docs/proposals/2026-09-10-coordination-without-labels.html`; the repo sources it rests on (`docs/GLOSSARY.md`, `src/bugarach/detectors/_shared.py`, `src/bugarach/learn/encode.py`, `src/bugarach/score.py`, `src/bugarach/simulate.py`, `src/bugarach/detectors/sce.py`); the surrogate-data, NCE/density-ratio, MIL, set-encoder and attention-interpretability literatures; and — because the decisive question was empirical — **the actual corpus**, resolved through `bugarach.dataset`. Four findings below are measured on the exact 18,011 fast / 6,772 slow baseline onsets in the document's own table.

---

## Findings

### 1. The dead-time leak — the surrogate is separable per-cell, and I measured it
**Location:** "The proposal" — *"Every cell keeps its own firing rate, its own number of events, and very nearly its own interval statistics. What the dither destroys, and the only thing it destroys, is the precise alignment of events across cells."*
**Severity: CRITICAL.** **Verifiable: yes — measured.**

The document's question 2 is "does the surrogate leak?" It does, and it is measurable before any code is written. In the senktide baseline windows, within-cell onset intervals have a **hard floor**: 0.40 s in the fast stream, 3.20 s in the slow (p0.1 = 0.60 s and 3.43 s). Independent per-onset dither violates that floor; real data never does.

Cutting those baselines into 60 s windows and dithering each:

| stream | J | real windows with a sub-floor within-cell interval | dithered windows | AUC of that one scalar |
|---|---|---|---|---|
| fast | 1.6 s | **0.0 %** (0 of 543) | 29.5 % | 0.647 |
| fast | 2.5 s | **0.0 %** | 38.3 % | 0.692 |
| slow | 2.5 s | **0.0 %** | 16.9 % | 0.585 |

That statistic is a *certificate*: any window containing a sub-floor interval is a surrogate with probability 1 on this corpus, using **no cross-cell information at all**. AUC 0.692 comes from one hand-picked count with zero fitting; a network with capacity does better, and the objective rewards it for doing so. Note the document's own best learned detector scores 0.681.

This is the named failure of this exact surrogate. Stella, Bouss, Palm & Grün (2022, *eNeuro* 9(3) ENEURO.0505-21.2022) tabulate uniform dithering as destroying dead time, ISI, autocorrelation and CV, and conclude *"UD fails as an appropriate surrogate because it leads to a loss of spikes in the context of binning and clipping, and thus to a large number of FP patterns."* Louis, Gerstein, Grün & Diesmann (2010, *Front. Comput. Neurosci.* 4:127): *"spike dithering alters the original data in two undesirable ways; it smoothes the rate profile and distorts the inter-spike interval (ISI) distribution toward that of a Poisson process."*

**Fix:** state the measured floors; adopt a dead-time-respecting surrogate — dither-with-dead-time (UDD), joint-ISI dithering (Gerstein 2004; Louis et al. 2010), or Harrison & Geman's **pattern jitter** (2009, *Neural Computation* 21:1244–1258), which preserves every spike's recent history exactly and so leaves *no* within-cell gradient by construction; add the sub-floor-interval count to the falsification list as a pre-registered probe.

Reproduce:
```
cd <repo>/
BUGARACH_DATA_OK=1 python3 -c '...'   # baseline windows, per-ROI diff, floors 0.40 / 3.20 s
```

---

### 2. The variant proposed is the one the literature singles out as invalid
**Location:** "The proposal" — *"each event time is independently displaced by a small random amount — a dither, drawn from a symmetric distribution of half-width J"*.
**Severity: CRITICAL. Verifiable: yes.**

This is **spike-centered (basic) jitter**. The literature distinguishes it from **interval / window jitter**, where a partition of time is fixed in advance and each spike is resampled within its own window, conditioning on the per-window count. Platkiewicz, Stark & Amarasingham (2017, *Neural Computation* 29(3):783–803), *"Spike-Centered Jitter Can Mistake Temporal Structure"*, construct explicit examples in which spike-centered jitter hallucinates temporal structure with exaggerated false-positive rates, and resolve the matter by re-emphasising the distinction from interval jitter. Amarasingham, Harrison, Hatsopoulos & Geman (2012, *J. Neurophysiol.* 107:517–531) give the conditional-inference framing: **what the resampling conditions on is the null hypothesis** — which is the document's own thesis, already worked out.

The document proposes exactly this variant, names neither variant, and cites neither literature. Against its question 1 ("has this been done?"): yes, this is the jitter/dither surrogate literature, roughly 25 years old, with a settled taxonomy.

**Fix:** name the variant against the taxonomy; switch to window/interval jitter (which also removes the edge problem below); cite it.

---

### 3. The positive class is mostly negative, which is what makes the leak fatal rather than untidy
**Location:** "Localization comes free" — *"the only way the model can win the window task is to concentrate its evidence on the few moments that actually betray the real recording."*
**Severity: HIGH. Verifiable: partly (window length and event rate are computable; the ceiling is analytic).**

Most baseline windows contain no coordinated event. For those, real and dithered are drawn from near-identical distributions, the true likelihood ratio is ≈1, and the bag label is *wrong* in the MIL sense. Bag-level AUC is bounded by the total-variation distance between the two window distributions, which is small precisely because most windows are eventless. So the legitimate gradient is thin and intermittent — while the dead-time leak is present in 29–38 % of windows at precision 1.0. That asymmetry is the mechanism by which the optimizer chooses the artifact.

The document also **never states the training window length**, which sets the events-per-bag base rate, the logsumexp bag-size offset, and the edge fraction 2J/W.

**Fix:** state W; estimate from the six detectors' own SCE rate on baseline what fraction of windows should contain an event; state the expected bag-level ceiling; consider reporting AUC conditioned on event presence.

---

### 4. Dither has a boundary problem too — charged only to the alternative
**Location:** "Open" — *"Displacing each cell rigidly ... reintroduces a boundary problem"*; and the wrap-splice section.
**Severity: HIGH. Verifiable: yes.**

If the dither is applied inside a training window, onsets within J of an edge are pushed out (or clamped/reflected), so the surrogate has a different onset density in the outer 2J/W of **every** window — a cue at a known location, which a conv net finds immediately, and which is the same class of defect as the wrap splice the document rejects circular shift for. Clamping is worse than dropping: it piles mass on the edge frames. The document does not say where in the pipeline the dither is applied relative to windowing, and the answer changes the design.

**Fix:** state it; prefer count-conditioned window jitter; if per-onset dither is kept, dither the whole recording *before* cutting windows and discard the outermost J at each recording end.

---

### 5. The wrap-splice objection is overstated, repairable, and the literature recommends the family being discarded
**Location:** "A circular shift has a splice, and the splice is easier to find than coordination."
**Severity: HIGH. Verifiable: yes.**

Real in kind and recognised (the shift family is tabulated in Louis, Borgelt & Grün 2010, *Analysis of Parallel Spike Trains* ch. 17, and in Stella et al. 2022) — but stated far above its magnitude. Circular shift preserves the *circular* ISI multiset exactly; the only anomaly is that the recording's two edge gaps merge into one interval whose expected length exceeds a typical ISI by roughly (1+CV²). With ~18 fast onsets per cell per baseline window that is one mildly-long interval per cell — **strictly weaker evidence than the floor violation the proposed replacement introduces in every cell**. It is also repairable without leaving the family: shift without wrapping and discard the remainder.

And Stella et al. (2022) *recommend* the shift family over dithering on five criteria, including that it "reproduces exactly the most relevant statistical features of a spike train." So the document rejects the family the current systematic comparison recommends, in favour of the one it criticises, on the weaker of its own two arguments.

**Fix:** restate the splice objection with its magnitude; acknowledge the no-wrap repair; **lead with drift**, which is the legitimate half; cite Stella et al. as the contrary recommendation you are knowingly departing from.

---

### 6. "The drift survives identically in both classes" — and the paper that fixes this is the one you want
**Location:** "It dissolves a confound that the circular shift creates."
**Severity: HIGH. Verifiable: yes.**

Uniform dithering convolves the rate profile with the dither kernel: λ_D = λ ∗ U[−J,J], i.e. λ_D(t) ≈ λ(t) + (J²/6)·λ″(t). Louis et al. (2010) state it directly — it "smoothes the rate profile", increasing rates in convex regions and decreasing them in concave ones. Drift survives *smoothed*, not *identically*, with residual proportional to rate curvature. For minute-scale drift and J of order a second the residual is genuinely negligible and the argument survives in substance — but this document's whole premise is that an optimal discriminator finds *any* difference, so an exact claim is the wrong register.

The consequence actually missed: **"structure finer than J" is not a synonym for "cross-cell alignment."** It is everything with rate curvature at scale J — per-cell structure included, which is finding 1. And keeping the cell axis (the architecture change the document also proposes) is exactly what gives the model the capacity to exploit it; the old collapse-the-cells architecture could not.

The published fix for the document's stated central problem is **dithering in operational time** (Louis et al. 2010), τ(t)=∫λ, which gives "perfect conservation of the rate profile" under non-stationarity while preserving ISI statistics. It is uncited.

**Fix:** soften to second order in J·curvature; separate "finer than J" from "across cells"; cite and consider operational-time dithering.

---

### 7. One J cannot serve both streams, and the document never says which stream it dithers
**Severity: HIGH. Verifiable: yes — measured.**

At J = 2.5 s: **50.4 %** of fast within-cell ISIs are below 2J and 15.2 % below J — the fast stream's interval structure is largely inside the dither's reach. At the same J, **4.1 %** of slow ISIs are below 2J and **0.00 %** below J. The same parameter is destructive on one stream and inert on the other. The document says "the recording" throughout and never names a stream, though `docs/GLOSSARY.md` makes the stream axis a first-class distinction and the corpus table itself reports fast and slow separately.

**Fix:** say which stream (or both, and how they are dithered jointly); state J per stream; report the fraction of each stream's ISIs inside 2J at the chosen J.

---

### 8. J is claimed to be "the same quantity" as two things it is not, 50× apart
**Location:** "The dither width is a declared, interpretable parameter" — *"the same quantity as the tolerance our scorer already uses ... and the same quantity as the jitter our simulator uses"*.
**Severity: HIGH. Verifiable: yes.**

Three different objects:
- `src/bugarach/score.py:60` — `TOL_SEC = 2.5`, a **greedy-match scoring window**, whose own docstring warns *"⚠ This is a scoring window, not a claim about timing accuracy"*, widened 1.5 → 2.5 on 2026-08-28 for bench-ranking reasons.
- `src/bugarach/simulate.py:379` — `jitter_sec: float = 0.05`, the **SD of a Gaussian** displacement of participant onsets.
- J — the **half-width of a uniform** kernel.

2.5 s versus 0.05 s is a factor of 50, and an SD is not a half-width. The document's strongest argument for dither is that J is "set, stated, and can be swept" — and it never states it, while mis-identifying it with two incompatible quantities. It matters: findings 1 and 7 both scale steeply with J.

**Fix:** give J a number, in seconds and frames (verified: `frame_interval_sec` = 0.1 for all 29 senktide recordings); drop the identity claims or reduce them to "of the same order as".

---

### 9. The likelihood-ratio claim is unconditioned, and contradicted four sections later
**Location:** "The proposal" — *"the optimal discriminator for this task computes a monotone function of the likelihood ratio between the real recording and the rate-matched null: which is to say, an estimate of exactly the quantity all six hand-written detectors approximate."*
**Severity: HIGH. Verifiable: yes.**

The first clause is right in the population limit under conditions the document does not state: (i) a **strictly proper composite loss** (cross-entropy or equivalent) — an arbitrary loss gives no such guarantee; (ii) the **class prior** enters, so the logit equals log LR only at balanced classes, otherwise logit = log LR + log(π/(1−π)); (iii) **unlimited capacity and infinite data** — this is a statement about the Bayes-optimal classifier and says nothing about a 1–2k-parameter net on 22 h; (iv) **common support**. This is standard noise-contrastive / density-ratio estimation (Gutmann & Hyvärinen 2010 AISTATS, 2012 *JMLR* 13:307–361; Sugiyama, Suzuki & Kanamori 2012), and "train a classifier, read its separability as the statistic" has a name — the **classifier two-sample test** (Lopez-Paz & Oquab, ICLR 2017), which carries the sample-splitting caveat any reported number will need.

The second clause is wrong twice. The six detectors compute a per-bin z/p against a circular-shift null (`docs/GLOSSARY.md:23`, *"circular-shift null, per-bin z/p"*) — a tail probability, not a likelihood ratio. And it is a *different* null, as the document itself argues later: *"their null destroys all cross-cell structure, so they cannot separate 'these cells fired together' from 'these cells were both busy this minute'"* and *"This is a sharper question than the six hand-written detectors ask."* Both cannot be true.

**Fix:** state the four conditions; delete "exactly the quantity all six approximate" and use the honest version the document already writes later.

---

### 10. The likelihood-ratio argument and the MIL argument recommend different pooling operators
**Location:** "make the window-level score a smooth maximum over a per-frame score."
**Severity: HIGH. Verifiable: yes.**

If the window score is a log-LR and frames are conditionally independent, the window log-LR is the **sum** of per-frame log-LRs — mean/sum pooling. Under the standard MIL assumption ("positive iff at least one instance is positive"), **max** is right. Logsumexp is neither; it interpolates, at a temperature the document does not name. Three consequences it does not state:

- **Bag-size offset.** For a flat bag, LSE ≈ log n_frames + mean, so the window logit carries a log(window length) term. A model trained at one window length is miscalibrated at another — and this couples directly to the false-alarm calibration, whose control window must therefore match deployment.
- **The known MIL failure mode.** With LSE and a low witness rate, the cheapest way to satisfy the bag loss is to raise *every* frame slightly rather than a few sharply. That is precisely the document's "it does not localize" falsifier, arriving by a mechanism it does not name. Mitigations: top-k pooling, a sparsity/entropy penalty on frame scores, or noisy-OR.
- **Which one.** The document must say max vs LSE vs mean, and at what temperature, because the answer determines what "coordinated event" means operationally.

References: Maron & Lozano-Pérez (1998, NIPS); Ramon & De Raedt (2000) for LSE as a soft max in MIL; Pinheiro & Collobert (CVPR 2015) for LSE pooling in weakly-supervised localization; Ilse, Tomczak & Welling (ICML 2018).

---

### 11. "The attention weights are a participation readout" is contradicted by the paper the architecture comes from
**Location:** "The attention weights are a participation readout. A detection can finally name the cells it meant."
**Severity: HIGH. Verifiable: yes.**

Ilse, Tomczak & Welling (ICML 2018) — the attention-MIL paper this follows — themselves note that instance-level accuracy of such methods is low and that MIL methods disagree at the instance level. The interpretability literature is blunter: Jain & Wallace (NAACL 2019), *"Attention is not Explanation"*, show learned attention is frequently uncorrelated with gradient-based importance and that very different attention distributions yield equivalent predictions; also Serrano & Smith (ACL 2019); Wiegreffe & Pinter (EMNLP 2019) push back only by narrowing what "explanation" may mean.

The document hedges in the falsification list but states it flatly in the body, and grades the falsifier "partial" — i.e. it already assumes the claim is more likely true than not. Since the participation readout is one of two headline benefits over the current detectors, it should be a hypothesis with a pre-registered test.

**Fix:** downgrade to "we would test whether"; keep the held-out participation check (that decision — keeping the simulator's recruitment array out of training — is methodologically correct and worth defending); include the rate-matched baseline the falsifier already names; consider intrinsically-attributable pooling (additive MIL) if attribution is load-bearing.

---

### 12. Softmax attention pooling reintroduces the magnitude-blindness diagnosed two sections earlier
**Location:** "attention pooling over cells at each frame" vs *"The log-ratio variants report contrast and discard magnitude, so one onset against a near-empty surround looks like five onsets against a surround five times larger."*
**Severity: MEDIUM-HIGH. Verifiable: yes.**

A softmax-normalized pool is scale-free in the cell axis: weights sum to 1 whether 1 of 30 cells is active or all 30 are. Coordination is intrinsically about *how many* cells participate, over fields of 10–61 cells. Normalized pooling cannot distinguish "seven of fourteen" from "one of one" without an explicit count — the same defect, in a new place. Deep Sets (Zaheer et al., NeurIPS 2017) draws exactly this sum-vs-mean distinction; Set Transformer (Lee et al., ICML 2019) adds PMA.

Two riders. **Terminology:** attention pooling over cells makes the pooled per-frame output permutation-**invariant**; only the per-cell branch and the weights are permutation-**equivariant**. The document says the pooled arrangement "is permutation-equivariant by construction" — worth getting right for outside methodologists. **And it partly undercuts "this detector needs no K":** naming participants from a normalized weight vector requires a cut on the attention distribution, which is a coactivity floor by another name.

**Fix:** pool with an explicit magnitude path (sum-pooling, or concatenate n·mean and n); fix invariant/equivariant; acknowledge the threshold on attention.

---

### 13. The CFAR analogy is the wrong one — this is a constant *corpus-average* false-alarm rate
**Location:** "The control also sets the threshold, at a stated false-alarm rate."
**Severity: HIGH. Verifiable: yes.**

`docs/GLOSSARY.md` defines CFAR as *"set the threshold from an estimate of the **local** background so the false-alarm probability stays put **as the background moves**."* A threshold fitted once on a pooled corpus delivers constant α *averaged over the corpus's background mixture* — it says nothing about α on a quiet field or a hot one individually. "It inherits whatever backgrounds the recordings actually have" describes the pooling, not a per-recording guarantee, and the section reads as though the pooled measurement delivered the adaptive property that CFAR exists to provide.

**The unit of α is also unstated.** Per frame, per window, per minute, per recording? A 20-minute baseline at 0.1 s is ~12,000 frames, so α = 10⁻³ per frame is ~12 false detections per recording. And the rate a reader cares about is measured *after* `decode()`, which merges runs within `merge_gap_frames` and drops runs below `min_width_frames` (`src/bugarach/learn/encode.py:164`) — so the calibration must fix those too.

**Fix:** say "constant corpus-average false-alarm rate", or make it genuinely CFAR by calibrating per recording against that recording's own dithered control (the construction already supports this and it is strictly better); state α's unit and the decode settings; report α stratified by background decile, which this corpus supports.

---

### 14. The control tests a slightly different contrast than the objective — and is also the instrument that catches finding 1
**Location:** "take a real recording, dither it once, and use that as the positive against a further-dithered negative."
**Severity: MEDIUM. Verifiable: yes.**

Two independent uniform ±J displacements compose to a **triangular** kernel of half-width 2J. So the control contrasts dither(J) against a triangular-2J smoothing — not a like-for-like repeat of the training contrast. A model keying on kernel *shape* or total smoothing width separates the control while nothing cross-cell remains, which would read as fatal when it is an artifact of the control.

Worth saying loudly, though, because it is the best thing in the document: **the control as proposed would catch the dead-time leak**, and treating a non-flat result as fatal rather than tunable is the correct posture. Build it first, as stated.

**Fix:** state the composed kernel; prefer a matched control (dither the *original* twice independently, so both sides are dither(J) of one source); note that a non-flat control is the expected signature of a within-cell leak and name the sub-floor-interval statistic as the first thing to check when it happens.

---

### 15. "Dithering one cell in isolation changes nothing about that cell's own statistics" — measurably false, and it is the reason given for believing the single-cell bug disappears
**Location:** "The proposal" — the lone-cell paragraph.
**Severity: MEDIUM (corollary of finding 1, but a separately load-bearing claim). Verifiable: yes — measured.**

Dithering one cell in isolation moves its interval distribution below the dead-time floor, from never (0 of 543 real 60 s windows) to routinely. A *bursting* cell is the worst case, because bursts are where the short intervals live: median fast within-cell ISI is 4.9 s, and 28 % of fast ISIs sit inside 2J at J = 1.6 s. So a lone bursting cell carries a **large** discriminative signal — the opposite of the claim — and the single-cell failure the design was meant to eliminate by construction is reinforced by the objective instead.

**Fix:** withdraw it, or restore it by adopting pattern jitter, under which it becomes true by construction. That is the single strongest argument for making the switch.

---

### 16. The quantization open question is answerable, and it is the wrong worry
**Location:** "Open" — *"quantization onto the imaging grid is one candidate, since displaced events must be re-quantized and the original ones were already on-grid."*
**Severity: MEDIUM. Verifiable: yes — measured.**

Both are on-grid: every `time_sec` in the export is a multiple of 0.1 s and `frame_interval_sec` is 0.1 across all 29 senktide recordings, so a continuous dither rounded to the grid leaves no sub-grid signature. The real effect is the one Stella et al. name — **binning and clipping**. `src/bugarach/learn/encode.py:52` writes a binary raster where *"Several onsets in one frame stay 1"*, so two onsets dithered into one frame merge and the surrogate silently loses an onset the positive kept. Measured: real data has essentially no such collisions (2 in 96,733 fast onsets across whole recordings), so any collision at all is near-diagnostic of a surrogate.

**Fix:** replace the open question with the measured answer and the clipping mechanism; it points at the same repair as finding 1.

---

### 17. Simulated validation is broken by the simulator's own dead time
**Location:** "can be scored head-to-head against the six on simulated data"; and the "does not localize" falsifier, scored on simulation.
**Severity: MEDIUM. Verifiable: yes.**

`src/bugarach/simulate.py:381` sets `min_sep_sec: float = 15.0`, and `_place_renewal` (`:292`) builds intervals as `min_sep + Gamma(shape, scale)` — so simulated cells carry a **hard, exact 15 s floor**, versus 0.40 s in the real fast stream. Any dither can push a pair below it, so a dither-trained discriminator evaluated on simulation is *more* trivially separable per-cell than on real data. Every localization or control number computed there will be optimistic in a way that does not transfer. This is the validation-must-exercise-the-shipped-configuration problem in its data form: the simulator's regularity is not the corpus's.

**Fix:** state it; if simulation is used for the control, raise the generator's interval CV or use a dead-time-respecting surrogate so the floor cannot be violated.

---

### 18. Prior art, against question 1
**Severity: LOW (a request, not a defect). Verifiable: yes.**

The construction is a **classifier two-sample test** (Lopez-Paz & Oquab, ICLR 2017) against a **jitter/dither surrogate null** (Date, Bienenstock & Geman's teetering; Gerstein 2004; Harrison & Geman 2009; Amarasingham et al. 2012; Louis et al. 2010; Stella et al. 2022), estimated by **noise-contrastive / density-ratio estimation** (Gutmann & Hyvärinen 2010, 2012; Sugiyama, Suzuki & Kanamori 2012), localized by **multiple-instance learning** (Maron & Lozano-Pérez 1998; Pinheiro & Collobert 2015; Ilse et al. 2018) over a **permutation-invariant set encoder** (Zaheer et al. 2017; Lee et al. 2019). None is the whole thing; each is a name the document says it failed to search, and each carries conditions currently omitted.

Also worth adding to the "not a comparison with" list: Elsayed & Cunningham (2017, *Nat. Neurosci.* 20:1310) is the canonical statement of this document's own thesis — that surrogates preserving a specified feature set can only test whether structure exceeds what that feature set implies. "The negative distribution is the model" has a citation.

---

## What checked out

- **Corpus numbers are exact.** 29 senktide recordings, 18,011 fast and 6,772 slow baseline onsets, 9.53 h of baseline against the stated "9.5 h" — all reproduced from the export folder.
- **Keeping the simulator's participation array out of training** and using it only as a held-out check is the right call and well argued.
- **Train-on-baseline / deploy-on-treated** is sound and the reasoning for it is correct.
- **Split by recording, stratified by group** is correctly identified — and note the document half-saw finding 1 there (*"a discriminator can memorize an individual cell's interval signature"*) without following it to the surrogate.
- **Building the control before the encoder**, and treating a non-flat result as fatal, is the strongest methodological decision in the document.

---

Sources:
- [Spike-Centered Jitter Can Mistake Temporal Structure — PubMed](https://pubmed.ncbi.nlm.nih.gov/28095192/)
- [A Rate and History-Preserving Resampling Algorithm for Neural Spike Trains — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3065177/)
- [Surrogate Spike Train Generation Through Dithering in Operational Time — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2972681/)
- [Comparing Surrogates to Evaluate Precisely Timed Higher-Order Spike Correlations — PMC (eNeuro)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9186111/)
- [Generation and Selection of Surrogate Methods for Correlation Analysis — Springer](https://link.springer.com/chapter/10.1007/978-1-4419-5675-0_17)
- [Revisiting Classifier Two-Sample Tests — arXiv](https://arxiv.org/abs/1610.06545)
- [Attention-based Deep Multiple Instance Learning — PMLR](https://proceedings.mlr.press/v80/ilse18a.html)
- [Attention is not Explanation — ACL Anthology](https://aclanthology.org/N19-1357/)
- [Attention is not not Explanation — ACL Anthology](https://aclanthology.org/D19-1002/)
- [Structure in neural population recordings: an expected byproduct of simpler phenomena? — Nature Neuroscience](https://www.nature.com/articles/nn.4617)

---
