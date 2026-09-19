GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 2: citation and reference review, "DOI or Die"

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`. I reviewed its built text, the alt text and any HTML comments (there are none). I did not edit anything. My only intermediates are in `...\scratchpad\mb2\role02\`.

**Verdict:** the report has no fabricated bibliographic metadata. Every published work it names exists, is by the authors given, and has the year given. Every internal document it cites exists and says what the report says it does, with one exception: forks.md §14 does not resolve on main (F5). No private correspondence is quoted.

The weaknesses are these:
- **An omission found by tracing forward:** the Kreuz lab has already published threshold detection on SPIKE-synchronization (F1).
- **One method description that doesn't match its origin:** the 2003 root of binned SCE reshuffles intervals, it does not circularly shift (F2).
- **No reference list at all** (F3).
- Several low-severity problems with how sources are placed or paraphrased.

## Findings
Each finding gives: where · what is wrong · severity · suggested fix · whether I checked it against a source.

**F1 · §3, the SPIKE-synch sentence · MEDIUM · verified: yes**
- **Issue:** The sentence "SPIKE-synch puts a detection step on Kreuz and colleagues' SPIKE-synchronization measure (2015)" sits under "what is this project's", so a reader takes the detection step to be ours.
- **What the source says:** the report's own cited source, docs/detector_history.md (2026-08-29 block), says "Not novel either": the Kreuz lab has published detection on this profile.
- **What I checked:** Cecchini et al. 2021, *PLoS Comput Biol* 17(5):e1008963, doi:10.1371/journal.pcbi.1008963. It exists and its last author is Kreuz (CNR-ISC, Sesto Fiorentino). Its Methods use SPIKE-Synchronization to keep only spikes that coincide with at least three quarters of the other spike trains, which is a threshold detection step on the measure.
- **Fix:** add something like "the Kreuz lab has itself published threshold detection on that profile (Cecchini et al. 2021); the layer here is an implementation, not a new method".
- **Not checked:** that it is the same two-knob detector. That rests on detector_history and the April 2026 Kreuz correspondence. If it matters, cite that as "personal communication" and do not quote it.

**F2 · §3, "binned SCE follows Cossart, Aronov and Yuste (2003)" · LOW–MEDIUM · verified: yes (I read the 2003 Methods from the open-access PDF)**
- **Issue:** The sentence comes right after "does the same count", which means counting against circularly shifted copies. The 2003 paper tested per-frame counts of coactive cells against interval-reshuffled surrogates, which is a different null:
  - 1,000 reshuffles per movie;
  - the threshold is the count exceeded in only 5% of surrogate histograms.

  The circular-shift null is the later Cossart-lab form (Bocchio 2020, Dard 2022, CICADA). By detector_history's account, binned SCE came here through CICADA's ideas.
- **Fix:** "descends from Cossart, Aronov & Yuste (2003), who tested coactive counts against interval-reshuffled surrogates; the circular-shift null is the Cossart lab's later form (CICADA), through which it reached this project."
- **Where the backward trace stopped:** the 2003 paper credits its surrogate method to Mao et al. 2001, *Neuron* 32:883–898, doi:10.1016/S0896-6273(01)00518-9. The publisher returned 403, so the lineage is verified one step short of the root.
- **Lab:** the 2003 paper is from the Yuste lab at Columbia (last author Yuste). The report does not call it Cossart-lab work, which is correct.

**F3 · the whole page · LOW–MEDIUM · verified: yes (metadata below)**
- **Issue:** Citations are author and year only, CICADA has no citation, and there is no reference list. That is thin for a public report written for new readers. I verified the metadata for a list:
  - Cossart R, Aronov D, Yuste R (2003) *Nature* 423:283–288, doi:10.1038/nature01614.
  - Kreuz T, Mulansky M, Bozanic N (2015) *J Neurophysiol* 113(9):3432–3445, doi:10.1152/jn.00848.2014. The year 2015 is correct. Its abstract calls SPIKE-synchronization "an improved and simplified extension of event synchronization", which traces back to Quian Quiroga, Kreuz & Grassberger 2002, *Phys Rev E* 66:041904.
  - Zaheer M, Kottur S, Ravanbakhsh S, Póczos B, Salakhutdinov R, Smola AJ (2017) Deep Sets, NeurIPS 30:3391–3401, arXiv:1703.06114.
  - The CICADA software: Denis, Dard, Quiroli, Cossart, Picardo, Zenodo doi:10.5281/zenodo.10041434.
  - The CICADA framework paper: Hamon M, Lebert J, … Dard RF (2026), bioRxiv doi:10.64898/2026.07.03.736318. Its last and corresponding author is Dard at EPFL; Cossart and Picardo (INMED) are co-authors. The preprint itself cites the software as "Cossart Lab / CICADA, 2019", so "the Cossart lab's CICADA" is right.
  - Optional: Cecchini 2021 (F1) and Finn & Johnson 1968 (F13).

**F4 · §3, the chorus sentence · LOW · verified: yes (chorus.py docstring and the Deep Sets PDF)**
- **Issue:** The text reads "pool the cells' votes three ways (the Deep Sets construction…)". Deep Sets gives the shape: one shared encoder per element, then a symmetric pool. Its main form sums, and it notes that any commutative pool keeps the result independent of order. The three statistics chorus uses (mean vote, spread, mean of the loudest 4) are this project's choice. The code also credits PointNet (Qi et al. 2017); the report drops it.
- **Fix:** move the citation onto "shared encoder and symmetric pool", add PointNet, then name the three statistics as ours.

**F5 · §5, "(docs/forks.md §14)" · LOW–MEDIUM · verified: yes**
- **Issue:** origin/main's forks.md stops at §13 (checked at c93a526). §14 exists only on the tune-bench-comparison and replicate-run branches. Every other branch-only citation in the report names its branch; this one doesn't.
- **Fix:** add ", on branch tune-bench-comparison".
- The number is right: §14 reports 64% of LoCo's and 70% of CoactDetect's calls kept on three real TTX baselines, so 30–36% lost.

**F6 · the "Why this report exists" paragraph · LOW · verified: yes (rehearsal results.json)**
- **Issue:** "put two learned models slightly ahead" is true only under the budget (chorus_norm +0.011, chorus_gain_norm +0.016). Chosen on F1 alone, only chorus_norm led (+0.012); chorus_gain_norm trailed (−0.021). §6 qualifies this; the opening does not.
- **Fix:** add "under its false-alarm budget".

**F7 · §6, how the rehearsal is used · LOW–MEDIUM · verified: yes**
- **Issue 1:** The shakedown README says "nothing should quote it as a comparison", and HANDOFF-workstation-tuning says "nothing quotes them". The report paraphrases the notes correctly, then quotes the margins anyway.
- **Issue 2:** The report's list of reasons the rehearsal is not a result leaves out the one reason that bears on CoactDetect: nothing stopped a context window wider than the planted spacing, so some CoactDetect choices sat at 240 s and contaminated their own null. That weakened the coded side of exactly the margin being quoted.
- **Fix:** add that reason. Say the margin is quoted only as the reason for the replicate, and cite docs/goals/README.md, which already uses the +0.011 margin that way.

**F8 · §3, "rate+context compares the population's event rate with its recent past" · LOW · verified: yes (code)**
- **Issue:** src/bugarach/detectors/rate.py (lines 10–11 and 205ff) uses a centred context window, as detector_history also says ("centred sliding-window counts"). The context includes the future, so "recent past" is wrong.
- **Fix:** "…with the rate over the surrounding minute".
- This is a content point for the accuracy role as well.

**F9 · §10, "pinned 12 ROIs to their lowest recorded value" · LOW · verified: yes**
- **Issue:** The sources (HANDOFF-workstation-tuning lines 839–846 and CLAUDE.md) say those ROIs report the frame minimum, a constant fill (the "frame floor"). That is not the ROI's own lowest value.
- **Fix:** "pinned 12 ROIs to the frame's floor value".
- Two neighbouring claims check out: 0.03% is 83 of 264,075 events (per the de-pinned handoff), and "item 3 of the decisions" is correct.

**F10 · §5 and §8, goal 1's values and its crowded-recording check · LOW · verified: yes**
- **Issue:** These claims carry no citation, though all of them hold:
  - **The reference values** (2 s / 120 s / α 10⁻⁵ / 8 s / 1 s) match meta.json's `coded_base`. Its source field reads "branch opt-every-knob-run @ 6fe09ab (HANDOFF-coded-detectors.md)".
  - **"Held back for the viewer and one analysis"** matches the bench.py OPERATING_POINTS comment and a row on the goal 1 page (coded-detector-optimization.md).
  - **"8 s merge can fuse 6 s events"** matches the goal 1 page, though that correction is about LoCo's winner.
- **Fix:** add a pointer to those sources.

**F11 · the Figure 2 caption · LOW, placeholder · verified: no, cannot be verified yet**
- **Issue:** The caption says "This slot holds … drawings … (<darkroom>/bugarach/2026-09-19-comparison-architectures/)". That folder does not exist in the darkroom yet, and no board claim for it is on main's SESSIONS.md. Under my checklist a reserved slot is flagged as not yet verified.
- **Fix:** "will hold … to be placed at …", and re-check once it lands.

**F12 · "The comparison decides which detectors the project keeps (goal 2 … docs/goals/README.md)" · LOW–MEDIUM · verified: yes**
- **Issue:** The cited page defines goal 2 as "a fair comparison". It says "None of this is final", that the project is "still troubleshooting and figuring out what models/detectors to keep", and that no result under the program is final. The report gives goal 2 a decisive role its source doesn't.
- **Fix:** "feeds the decision of which detectors to keep, which the program says is not yet final".

**F13 · §3, "designed here and independently resemble radar CFAR" (constant false alarm rate) · LOW · verified: partly**
- **What holds:** authorship and independence match detector_history. That rests on Tony's account (the 2026-08-29/30 blocks) and a commit timeline that predates the 2026-08-22 discovery of the CFAR literature.
- **What the report doesn't cite:** the CFAR root. That is Finn & Johnson 1968, *RCA Review* 29(3):414–464, which detector_history records as read in full; I did not re-read it.
- **Residuals the source carries:** rate+context's priority is unexamined (the body of Cotterill 2016 is unread; §7 item 1), and nobody has searched for a coactivity detector with a rate-local surrogate null (§7 item 5).
- **Fix:** cite Finn & Johnson, and never upgrade "designed here" to "new".

## Checked and correct
- **The fold-defect todo:** found by a review of an earlier report. The rehearsal had the defect (held-out folds 3 and 4 both fitted recordings 1000–1009). The fix is round-robin dealing plus a replay check, and the replicate's meta.json has `fold_check.distinct: true`.
- **The 1.6 margin:** the bench's ratio for binned CoactDetect (7.0 against 4.4), carried over (HANDOFF lines 325–334; meta `budget_margin` 1.6).
- **The eight constants:** within their intervals except participation, in both folders.
- **FOUNDATIONS §9:** under TTX, the fast stream falls to a median 0.46 of baseline while the slow stream rises to 2.50, so they move in opposite directions.
- **Goals README decisions 2 and 4:** baseline only, fast stream first, both dated 2026-09-17.
- **"Declarations differ in exactly two entries":** I diffed both meta.json files. Inside `declaration`, only `recording_seeds` and `replicate` differ. The other differences are the budgets derived from those seeds and the launch record (`started`), which is not part of the declaration.
- **"Code differs only in the replicate option":** `git diff e8764aa..9ba49bc` touches only the handoff, and `9ba49bc..7a95e8a` touches only the tool and its test.
- The chorus models exist only on replicate-run and tune-bench-comparison.
- "WSMIP064 writes its own report": the SESSIONS.md block says so.
- The quiet and busy rates (0.0052 and 0.019) are the 25th and 75th percentiles (bench.py lines 635–641).
- The rehearsal's gated margins, +0.011 and +0.016, match its results.json.

## Private correspondence
None. I scanned the raw HTML for quoted speech, "personal communication", Tony, comments and alt text. Kreuz appears only by name, as the author of a published measure.

## Problems in the sources themselves (not the report)
- The shelf's `lit/DL/README.md` lists Deep Sets' second author as "Kumar". It is Satwik Kottur, per the PDF header and NeurIPS.
- HANDOFF-workstation-tuning.md (tune-bench-comparison, around line 899) swaps the rehearsal margins. It says "+0.011 ungated and +0.012 gated", but its own t values and results.json give 0.0122 ungated and 0.0112 gated. The report follows results.json and is correct.
- The shelf's `lit/coordination/README.md` line 279 says CICADA has "no method paper". Its own line 384, which lists Hamon 2026, supersedes that.

## Left open (⚠)
- **Mao et al. 2001:** not read (403 from the publisher), so the SCE lineage is verified one step short of its root.
- **Cecchini 2021:** I read its Methods only through the fetched page. That it is the same detector as ours is not verified by me.
- **Literatures I searched:** calcium-imaging SCE lineage, spike-train synchrony (2002 → 2015 → 2021), set-function machine learning (Deep Sets and PointNet), and the CICADA software and preprint record.
- **Not searched:** the radar primaries (I relied on detector_history's read-in-full record), the burst-detector literature (for rate+context priority), pooling with several aggregators in graph learning (for the three-statistic pool), and nested cross-validation methodology.
- **Nobody asked:** I did not ask Tony whether anyone has written to the CICADA authors (Dard or Cossart) about the locust port. The only correspondence on record is Kreuz's, April 2026, and the report correctly does not quote it.

Sources:
- [Cossart, Aronov & Yuste 2003, Nature](https://www.nature.com/articles/nature01614), with the open-access PDF at [Columbia](https://blogs.cuit.columbia.edu/rmy5/files/2017/06/cossart.nature.03.pdf)
- [Kreuz, Mulansky & Bozanic 2015 (PubMed 25744888)](https://pubmed.ncbi.nlm.nih.gov/25744888/) and [the J Neurophysiol article](https://journals.physiology.org/doi/full/10.1152/jn.00848.2014)
- [Deep Sets, NeurIPS 2017](https://papers.nips.cc/paper/6931-deep-sets)
- [Cecchini et al. 2021, PLoS Comput Biol](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008963)
- [CICADA software record, Zenodo](https://zenodo.org/records/10041434)
- Crossref records for doi:10.64898/2026.07.03.736318 (Hamon et al. 2026), doi:10.1103/PhysRevE.66.041904 (Quian Quiroga, Kreuz & Grassberger 2002) and doi:10.1016/S0896-6273(01)00518-9 (Mao et al. 2001)
