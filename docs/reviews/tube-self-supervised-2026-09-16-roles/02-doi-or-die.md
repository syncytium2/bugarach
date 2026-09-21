GRANT 2 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch).

The missing tools did not limit the check — `grep` and `find` through Bash covered the same ground, so no check was skipped. I edited nothing. Intermediates (the Dard 2022 JATS XML) are in `<scratchpad>/mb2/role02/`.

# Role 2, citations and references

**Artifact:** `<worktree>/docs/learned/tube_self_supervised/README.md` and its two figures.

**The one-line summary of the surface:** the page contains **zero external citations**. `grep -i "et al\|doi\|arXiv\|CFAR\|Grün"` over the README returns nothing; the same grep over its parent handoff (`docs/handoffs/2026-09-15-rigid-shift-controls-and-tube-training.md`) also returns nothing. Every borrowed construction on the page is uncredited, and the page is in a public repo, written for the lab's lead, showing figures derived from another laboratory's CC-BY data.

## Findings

**1. The Cossart data are used on a public page with no attribution, under a licence that requires it** · **blocking** · verified yes

- **Location:** "including on the Cossart folder at that folder's measured participation" (What holds); "the slow stream and Cossart were not"; "on the lab slow stream and on Cossart that structure is real".
- **Issue:** DANDI:000219 is *"Two photon calcium imaging in the CA1 region of the hippocampus in neonatal mice"*, contributors Dard, Robin; Picardo, Michel; Cossart, Rosa, **licensed CC-BY-4.0** (confirmed against the DANDI record). The publication is Dard et al. 2022, *eLife* 11:e78116, doi:10.7554/eLife.78116 (confirmed: 15 authors, Cossart second-to-last, Picardo last; P5–P12 pups, in vivo two-photon). "The Cossart folder" names neither the first author nor the last author, and CC-BY attribution is a licence term, not a courtesy. The companion `docs/learned/rigid_shift_look/README.md` already carries the full credit in its correction banner; this page, which is the one written to be read, dropped it.
- **Fix:** at first mention write *"the Cossart folder — DANDI:000219 (Dard, Picardo & Cossart; CC-BY-4.0), from Dard et al. 2022,* eLife *11:e78116"*.

**2. The paper behind that dataset already published the report's central design, and the report claims it** · **blocking** · verified yes (Dard 2022 Methods, read in full)

This is the required forward trace, and it lands hard. Dard et al. 2022, Methods, "SCE detection", says in terms:

> SCEs were defined as the imaging frames within which the number of co-active cells exceeded the chance level as estimated using a reshuffling method. Briefly, an independent circular shift was applied to each cell to obtain 300 surrogate raster plots. We computed the 99th percentile of the distribution of the number of co-active cells from these surrogates and used this value as a threshold to define the minimal number of co-active cells in an SCE.

That single paragraph contains all three things the report presents as its own:

| the report's claim | where Dard 2022 already has it |
|---|---|
| "count how many ROIs are lit" — the length sensor, `line`'s reason for existing | "the number of co-active cells" |
| rigid shift as the negative class | "an independent circular shift was applied to each cell" — a per-cell whole-train shift |
| "a threshold read off the surrogate lands in the right place for a model that counts", called *"a useful result on its own"* | "the 99th percentile of the distribution … from these surrogates and used this value as a threshold" |

- **Fix:** the claim that survives is narrow and worth stating on its own — *making this construction differentiable and trainable, and setting the operating point at a stated event rate rather than a fixed tail quantile.* Write the Dard sentence into "What holds" as the precedent, and delete "That is a useful result on its own" or rewrite it as a replication of theirs.

**3. Setting a threshold from a null's own false-alarm rate is CFAR, and this repo has 1,125 lines on the subject** · **blocking** · verified yes

- **Location:** "set per recording so the model fires at most *r* events per 10 minutes on that recording's own rigid shift"; the "≤ 0.5 / ≤ 1 / ≤ 2 events per 10 min" columns in both tables.
- **Issue:** holding the false-alarm rate fixed while the background moves, by estimating the background and setting the threshold from that estimate, is the founding idea of constant false alarm rate detection — **Finn & Johnson (1968)**, *Adaptive Detection Mode with Threshold Control as a Function of Spatially Sampled Clutter-Level Estimate*, *RCA Review* **29**:414–464 (metadata confirmed by search; the repo records this copy as read in full and shelved). `docs/detector_history.md` §4 already maps three of this project's detectors onto CFAR and says *"This tradition is not cited anywhere in either repository"* — that sentence was written as a defect to fix, and this page reproduces the defect on new work.
- **Fix:** one clause — *"this is CFAR's rule (Finn & Johnson 1968), with the surrogate standing in for the reference cells"* — and a link to `docs/detector_history.md` §4.

**4. The architecture is credited to Tony; this repo already published its lineage** · major · verified yes

- **Location:** "**The architecture question has an answer, and it is Tony's.**"
- **Issue:** `docs/learned/learned_detector.src.html` carries a block headed *"The architecture is not unprecedented either"* which credits, for this exact operator: centre–surround as a difference of Gaussians, **Rodieck (1965)** and **Enroth-Cugell & Robson (1966)**; as a detection kernel, **Marr & Hildreth (1980)**; a bank of them with scale as the selected quantity, **Lindeberg (1998)**, octave spacing from **Lowe (2004)**; and — directly on point — **making the widths learnable has a precedent in Pogoncheff, Granley & Beyeler (NeurIPS 2023)**. `line` is that bank with a counting front end. Nothing in this report tells a reader so.
  The design *intent* is genuinely Tony's and the quoted message dates it; the sentence as written claims the mechanism, not the intent, and the mechanism is sixty years old.
- **Fix:** keep the credit for the idea, and add *"the mechanism is not new — see the lineage block in `docs/learned/learned_detector.html`"*. That is a link, not a new literature search.

**5. "One ROI, one vote" is Unitary Events clipping — and somebody already told this lab so, by email** · major · verified yes (repo record; correspondence paraphrase on file)

- **Location:** the report's framing of `line` as "count how many **ROIs** are lit" against `tube`, and Panel B's line-versus-burst separation, "the distinctness the count channel was built for".
- **Issue, two independent precedents:**
  - The same repo's citation block reads: *"LoCo · CoactDetect — Build on Unitary Events, **including the per-cell clipping step this page's model also uses**. Grün, Diesmann & Aertsen (2002), Neural Computation 14(1):43–80 and 81–119."* Clipping the binned train to binary so a bursting cell contributes at most one is precisely `line`'s sigmoid cap.
  - **Correspondence exists and is unused.** `docs/todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md` records that Thomas Kreuz replied to Tony by email in April 2026 and said (paraphrased there, not quoted) that a later paper of theirs adds postprocessing admitting **at most one spike per pixel per event**, which he describes as essential to that method. That is the same cap, from the author of a measure this project already wraps, on record in this tree for three weeks.
- **Fix:** cite Grün, Diesmann & Aertsen 2002 beside the vote cap, and cite the correspondence as *"Kreuz, personal communication, April 2026"* — **paraphrase only**; `CLAUDE.md` and `tools/check_quotes.py` forbid reproducing his sentences here.

**6. Rigid shift's own lineage is absent from the page that trains on it** · major · verified yes

- **Location:** "Rigid shift is the candidate — each ROI's whole onset train moves by one random offset within ±*J*"; "**Rigid shift is a sound teacher.**"
- **Issue:** published as whole-train shifting — **Pipa, Riehle & Grün 2007**, *Neurocomputing* **70**:2064–2068 (confirmed by search: *Validation of task-related excess of spike coincidences based on NeuroXidence*); **Pipa, Wheeler, Singer & Nikolić 2008**, *J Comput Neurosci* **25**:64–88; **Louis, Borgelt & Grün 2010**, *Analysis of Parallel Spike Trains* ch. 17; ranked most robust by **Stella, Bouss, Palm & Grün 2022**, *eNeuro* **9**(3). The companion note now carries this in its correction banner; the report does not inherit it, and the report is the document that leaves the tree.
  The **no-wrap deviation matters more here than it did there**: the published form rolls the train on purpose, and this run drops onsets pushed past the edge (`src/bugarach/surrogates.py`, `rigid_shift`, `edges=True`). Every negative in the label-free training came from the non-published variant.
- **Fix:** one lineage sentence in "The problem", ending *"the published form wraps the train; this run does not."*

**7. The training objective is uncited, and the repo's own source file cites it** · major · verified yes

- **Location:** "The objective is a ranking loss on the mean of the top 1 % of per-frame scores, a real crop against the same crop rigid-shifted."
- **Issue:** two separate borrowed constructions, neither named.
  - *Real against surrogate, read as separability* is the **classifier two-sample test** — `src/bugarach/surrogate_discriminator.py` cites **Friedman 2003** and **Lopez-Paz & Oquab 2017** (ICLR, arXiv:1610.06545) in its own module docstring, and the shelf holds the PDF. Training on the ratio rather than testing it is **noise-contrastive / density-ratio estimation** (Gutmann & Hyvärinen 2010).
  - *The mean of the top 1 % of per-frame scores* is **top-k mean pooling in multiple-instance learning**, the standard aggregation in weakly-supervised event detection — Wang, Li & Metze, *A comparison of five MIL pooling functions for sound event detection with weak labeling* (ICASSP 2019, arXiv:1810.09050); McFee, Salamon & Bello, *Adaptive pooling operators for weakly labeled sound event detection* (2018). That literature also has the measured answer to the report's own open question, "the label-free objective is the bottleneck, and it is untuned": it compares pooling rules head to head and reports which localize.
- **Fix:** name both in the objective sentence, and point "Is the objective worth another attempt?" at the MIL-pooling comparison rather than at a fresh design.

**8. Figure 1, Panel A displays three third parties' methods by name, at poor scores, with no attribution and no caveat** · major · verified yes

- **Location:** `line_sensors_fig.png`, Panel A — the plotted bake-off carries six detectors the README's own table omits: `rate+context` (0.57), `locust` (0.54), `tube_ratio`, `tube_ratio_guard`, `binned SCE` (0.45) and **`SPIKE-synch` (0.27, second from bottom)**.
- **Issue:** on a public page, `SPIKE-synch` names **Kreuz, Mulansky & Bozanic (2015)**, *J Neurophysiol* **113**(9):3432–3445, `locust` is the port of the Cossart lab's **CICADA** (Denis, Dard, Quiroli, Cossart & Picardo 2020), and `binned SCE`'s root is **Cossart, Aronov & Yuste (2003)**, *Nature* **423**:283–288. The repo's own learned_detector report ships the necessary caveat — *"The detection layer built on top of the measure is this project's, not his, and it sits under two open defects — so its score here is not a statement about the measure"* — and two of those defects are still open (`docs/todo/2026-08-11-file-pyspike-max-tau-issue.md`, `docs/todo/2026-08-18-spike-synch-knob-may-not-be-the-knob.md`). A reader of this figure sees a named researcher's measure at the bottom of a leaderboard with none of that.
- **Fix:** either cut the unattributed rows from the figure, or add a credits line under Figure 1 naming the four outside sources and stating that the poor `SPIKE-synch` score is about this project's detection layer, not about the measure.

**9. Elephant produced every negative in the report and is cited only as a directory name** · major · verified yes

- **Location:** "in the Elephant virtual environment (`bugarach-worktrees/surrogate-screen-overnight-venv`, torch 2.14.0)".
- **Issue:** `rigid_shift` calls Elephant's `dither_spike_train` (`src/bugarach/surrogates.py`), so the toolkit generates every training negative and every surrogate threshold on the page. It is cited as a venv name. The citable reference is **Denker, Yegenoglu & Grün (2018)**, *Collaborative HPC-enabled workflows on the HBP Collaboratory using the Elephant framework*, Neuroinformatics 2018, P19, doi:10.12751/incf.ni2018.0019, **RRID:SCR_003833** (confirmed against the project's own docs and bibliography). The report pins `torch 2.14.0` but gives **no Elephant version**, which is the one version number that changes the results.
- **Fix:** write *"Elephant (RRID:SCR_003833) version X.Y.Z; Denker, Yegenoglu & Grün 2018"* and pin the version in the reproduce table.

**10. A sourced number is attributed to a file that does not contain it, and the soft flag is put on the wrong number** · major · verified yes

- **Location:** "Real fast onset jitter is 0.36–1.04 s and the second number is flagged soft in `docs/generator.md`."
- **Issue:** `docs/generator.md` flags **0.36 s** soft, not 1.04 — *"⚠ The least trustworthy number here"*, *"secondary, flagged-soft"*, *"Treat it as an upper bound at the estimator's …"*. The string `1.04` does not appear in `docs/generator.md` at all; the prior round traced 1.04 s to interface2 commit `f76e7b1b`, a **private** repository a reader of this public page cannot reach. So the sentence miscredits which number is soft and cites a public file for a number it does not hold.
- **Fix:** *"Real fast onset jitter is 0.36–1.04 s; the 0.36 s end is flagged soft and treated as an upper bound in `docs/generator.md`, and 1.04 s is a median from interface2 commit `f76e7b1b` in a private repository."*

**11. Two named prior results are cited to directories that contain no prose** · minor · verified yes

- **Location:** "Details and figures: `../rigid_shift_look/controls/`"; "the controls, the aggregate-channel leak test, and the first tube training run — are in `aggregate_leak/`, `../rigid_shift_look/controls/`".
- **Issue:** `docs/learned/rigid_shift_look/controls/` holds two PNGs and two JSON pairs and **no README**; `aggregate_leak/` holds one PNG and two JSON and **no README**. The figures carry no captions, no numbers and no method text. A reader sent there to check the controls — the evidence for the headline claim "Rigid shift is a sound teacher" — arrives at an unlabelled image. The handoff link and `docs/learned/generator_spec.json` both resolve; these two do not resolve to anything readable.
- **Fix:** put a short README in each, or move the controls figures and their numbers into this page where the claim is made.

**12. The companion note this page rests on is under a correction banner, and this page does not say so** · minor · verified yes

- **Location:** the "What holds" links to `../rigid_shift_look/controls/`; "The rigid-shift note stays under its correction banner until this is answered" (What waits on Tony) mentions the banner only in passing, three screens down.
- **Issue:** `docs/learned/rigid_shift_look/README.md` opens with *"⚠ Under correction, 2026-09-15 — read this before anything below. Two of its readings do not hold as written, and the rest of the note has not yet been rewritten."* A reader who follows the link from "What holds" reaches a document whose own first line disowns part of itself, with no warning from here.
- **Fix:** say it at the link, not only at the bottom.

**13. The permutation-invariance claim has an uncited framing, and its companion todo says something different about what a person sees** · minor · verified yes

- **Location:** "⚠ **The wave is not a tilt.** These models are permutation-invariant over ROIs and the encoder sorts rows by rate, so the diagonal a person sees in a raster is a fact about row order, which the model never reads."
- **Issue:** the set-function framing is **Zaheer et al. 2017 (Deep Sets)** and **Lee et al. 2019 (Set Transformer)**, both already named in `docs/reviews/2026-09-10-coordination-without-labels-roles-1-6.md` and cited nowhere here. Separately, `docs/todo/2026-09-15-raster-aspect-ratio-has-psychophysics-behind-it.md` — filed the same day, and named as a companion — holds sourced evidence that what a person reads as a line is governed by **inter-dot spacing and the ratio of competing distances** (Uttal 1973; **Kubovy & Wagemans 1995**, *Psychological Science* **6**:225–234; Field, Hayes & Hess 1993), not by row order alone. The report's parenthetical account of human raster reading is unsourced and is narrower than what the tree already holds.
- **Fix:** cite Zaheer et al. 2017 for the invariance, and link the psychophysics todo rather than asserting what a person sees.

**14. `CoactDetect` and `LoCo` appear as reference detectors with no statement of what they are** · minor · verified yes

- **Location:** the bake-off table; "beside CoactDetect and LoCo at their production operating points"; "Supervised `line` catches 76–77 % of CoactDetect's and LoCo's events".
- **Issue:** an outside reader cannot tell whether these are published methods or in-house ones. `docs/detector_history.md` settles it — both are Tony's, designed for this preparation, and the author's own statement is *"They blindly reconstructed elements of CFAR, I was totally unaware when I designed them"*; the repo maps `CoactDetect` to a per-cell cell-averaging CFAR test and both to Unitary Events. Since `line`'s entire pitch is that it counts distinct ROIs against a rolling background, and that is what `CoactDetect` already does non-differentiably, the relationship between the new model and the row two below it in its own table is the thing a reader most wants and the page never says.
- **Fix:** one sentence — *"CoactDetect and LoCo are this lab's own detectors (`docs/detector_history.md`); `line` is CoactDetect's statistic made differentiable."*

**15. Cross-reference for the mechanical role:** Figure 2's legend shows only `tube` and `tube_guard`, while the text above it says "Four architectures" and the table below it carries `line` and `line_length` rows. The figure appears not to have been regenerated after the `line` arms were added. I flag it only because it breaks the text-to-evidence link; the pixel check belongs to role 10.

## Where the backward traces stopped, and why

- **Count-of-coactive-cells against a shift surrogate:** stopped at **Dard et al. 2022** (read in full, open access). Its own antecedent is the CICADA "SCE description" analysis (**Denis et al. 2020**), whose antecedent this repo traces to **Cossart, Aronov & Yuste 2003**, *Nature* **423**:283–288, which used interval reshuffling rather than a circular shift. **I did not read the 2003 Methods this round** — that credit rests on `docs/detector_history.md`'s own audit, which is one step short of the root.
- **CFAR:** stopped at **Finn & Johnson 1968**, metadata confirmed by search but **not re-read this round**; the repo records the shelf copy as read in full.
- **Rigid shift:** stopped where the prior round stopped — at **Pipa, Riehle & Grün 2007**, closed access, reached only through Harrison & Geman's secondary reading. One step short of the root, and unchanged.
- **Centre–surround:** stopped at **Rodieck 1965 / Enroth-Cugell & Robson 1966**, confirmed by search as the two independent origins of the difference-of-Gaussians model. Neither read.
- **Lab affiliation checked, not inferred:** Dard 2022's senior authors are Cossart and Picardo at INMED, Aix-Marseille. **Pipa's papers cross two laboratories** — the 2007 paper has Grün as last author (Jülich/Riken), the 2008 paper has Nikolić (Frankfurt). Crediting 2008 alone credits the wrong group; the report credits neither.

## Literatures searched, and not searched

- **Searched:** spike-train surrogates (Grün school: Pipa 2007/2008, Louis 2010, Stella 2022); the DANDI record and Dard 2022 full text, forward to CICADA/DeepCINAC; radar CFAR (Finn & Johnson, via the repo's own shelf record and a confirming search); classifier two-sample testing (shelf, plus the repo's source file); weakly-supervised sound event detection and MIL pooling; visual-neuroscience receptive-field modelling (difference of Gaussians); self-supervised/contrastive learning on neural spike data; and the repo's own detector-history and review corpus.
- **Not searched — residual ⚠, each a live place prior art could sit:**
  - **Astronomy and genomics source detection**, where "set the threshold from a permutation or simulated null at a fixed false-alarm rate" is routine and predates the radar framing in some corners.
  - **Point-process / scan-statistic literature** on counting distinct participants in a moving window against a null (Kulldorff-style scan statistics). `line` is a scan statistic with a learned kernel and nobody has checked that field.
  - **Self-supervised learning on calcium imaging specifically** — the search I ran returned spike-sorting and SNN work, not population-event detection, so "no prior art" is **not** established here.
  - **Pipa's own later work after 2008**, still unsearched from the previous round.
  - **Elephant/NEST ecosystem applied papers** that train a model against Elephant surrogates.

## Residual ⚠: what the humans hold

**Somebody was asked, and the answer is on file and unused.** Kreuz replied to Tony by email in April 2026, and one of his points — a one-event-per-unit cap being essential to their published method — bears directly on `line`'s headline sensor (finding 5). That is the cheapest available check and it was already paid for.

**Nobody was asked about the rest.** I found no correspondence with Dard, Picardo or Cossart about the SCE-detection method this report re-derives, and none with Grün's or Pipa's groups about whole-train shifting without wrap on trial-less recordings. Before the page says anything is new, the main thread should ask Tony whether either conversation exists, and cite it dated and paraphrased.

## For the main thread, outside this artifact

`docs/learned/recombination_nulls_reading_log.md` still says rigid shift is what Louis 2010 recommends and what Stella 2022 found most robust; both endorse the **wrapped** or per-trial variant, and this thread runs the unwrapped one. The prior round flagged that line and it is still uncorrected.

Sources:
- [DANDI:000219](https://dandiarchive.org/dandiset/000219)
- [Dard et al. 2022, eLife 11:e78116](https://elifesciences.org/articles/78116) · [JATS XML](https://cdn.elifesciences.org/articles/78116/elife-78116-v2.xml)
- [Cossart, Aronov & Yuste 2003, Nature 423:283–288](https://www.nature.com/articles/nature01614)
- [Stella et al. 2022, eNeuro 9(3)](https://www.eneuro.org/content/9/3/ENEURO.0505-21.2022)
- [Louis, Borgelt & Grün 2010, ch. 17](https://link.springer.com/chapter/10.1007/978-1-4419-5675-0_17)
- [Wang, Li & Metze 2019, MIL pooling functions for SED](https://arxiv.org/pdf/1810.09050)
- [Elephant documentation and citation](https://elephant.readthedocs.io/) · [Elephant bibliography](https://github.com/NeuralEnsemble/elephant/blob/master/doc/bib/elephant.bib)
- [Finn & Johnson 1968 CFAR, secondary confirmation](https://www.radartutorial.eu/01.basics/False%20Alarm%20Rate.en.html)
- [Receptive field / difference-of-Gaussians origins](http://www.scholarpedia.org/article/Receptive_field)
