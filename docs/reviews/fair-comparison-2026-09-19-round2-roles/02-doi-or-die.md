<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round2/. -->

GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 2, DOI or Die: round-2 check of the fair-comparison report

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html`. Its `git hash-object` is `16ac70467ce5…`, which matches the blob hash you gave (16ac704). The worktree HEAD is `c261f9c`.

**Scratch files:** in `%USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\r2-role-2\`:
- `report.txt`: the page text
- `cossart2003.pdf` and `c.txt`: the full text of Cossart, Aronov & Yuste 2003
- `bf2004.pdf` and `bf.txt`: the full text of Bouckaert & Frank 2004

I edited nothing.

**How the pass ran.** I did the blind pass first. Only afterwards did I read the round-1 role-2 report (`docs/reviews/fair-comparison-2026-09-19-roles/02-doi-or-die.md`). The status of each round-1 item is at the end.

**Bottom line.** Every outside work the page names exists, and its metadata checks out. The problems are about what is credited to whom, and about what is left out:
- The page credits the nets' architecture to "this project", while the nets' own source code calls it a known design.
- It labels the tuned binned SCE "the rule of Cossart 2003", although the tuned version differs from that rule in the surrogate, the threshold and the merge.
- "Denis and colleagues 2020" without a DOI points a reader at a different tool.
- The SPIKE-synch attribution describes a coincidence window that the budget-constrained choices switched off.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against a source? |
|---|---|---|---|---|---|
| 1 | Table 1, "where it comes from" for chorus_norm and chorus_gain_norm (and, by the same logic, line_length): "this project" | The coded rows in this column name their lineage, so a reader takes "this project" as a claim of origin. The nets' own source says otherwise. `…\tune-bench-comparison\src\bugarach\learn\nets\chorus.py` lines 33–37: *"it is not a new idea — a shared per-element encoder, a symmetric pool, a decoder on the pool is the Deep Sets shape (Zaheer and colleagues, 2017; Qi and colleagues, PointNet, 2017)"*. `line.py` is also a per-ROI encoder, then a mean over ROIs, then a decoder. That is the same shape by chorus.py's own definition (my inference; line.py itself does not say it). Round 1 raised this as #7, and it is still there. | **major** (a novelty-shaped claim that contradicts the project's own code, and it survived round 1) | "built here; a Deep Sets network (Zaheer M., Kottur S., Ravanbakhsh S., Póczos B., Salakhutdinov R., Smola A. (2017), *Deep Sets*, NIPS 30; Qi C.R., Su H., Mo K., Guibas L.J. (2017), *PointNet*, CVPR 652–660)". Keep "this project" for tube only if nobody objects (see residuals). | yes: the source file; Deep Sets on the NeurIPS proceedings page; PointNet on the CVF open-access listing |
| 2 | Table 1, binned SCE: "thresholds the count against circularly shifted copies (synchronous calcium events, SCE) … the rule of Cossart, Aronov and Yuste 2003" | **I read the 2003 Methods in full.** They say: "we used **interval reshuffling** … Reshuffling was carried out 1,000 times … threshold … exceeded in a single frame in only 5% of these histograms" (P < 0.05, a whole-movie criterion), citing Mao et al. 2001 (ref 12). The run's chosen SCE differs from that rule (`configs/sce/*.json`, via `selections/*/outer*/sce.json`):<br>• it uses a circular shift, not interval reshuffling<br>• 200 surrogates, not 1,000<br>• a threshold at the **70th percentile in 3 of 4 folds on F1 alone** (90th–95th otherwise), not P < 0.05<br>• 2 s bins, a minimum of 3 ROIs and a **30 s merge**<br>Next to a headline of "0.771, first on paper", "the rule of" invites reading 0.771 as the 2003 rule's score. The name "SCE" is not in the 2003 paper, which says "peaks of synchronous activity". The acronym belongs to the Cossart lab's later usage (Malvache et al. 2016, *Science* 353:1280–1283), which I have from a search summary only. The project's record says binned SCE reached this project "based on ideas in CICADA" (`docs/detector_history.md`, 2026-08-29 block). | **major** | "descends from the rule of Cossart, Aronov & Yuste 2003 (*Nature* 423:283–288, doi:10.1038/nature01614). That rule resampled by interval reshuffling at P < 0.05. The circular-shift form follows Bocchio et al. 2020 and Dard et al. 2022. The tuned variant here (70th–95th percentile, 30 s merge) is not that rule." | yes: the 2003 full text; the run's config files |
| 3 | Table 1, SPIKE-synch: "a coincidence window set by the local gaps between each ROI's events … built on Kreuz, Mulansky and Bozanic 2015" | (a) **Under the budget, all 4 folds chose `tau_mode="fixed"`, `tau_max` 0.25 s** (`configs/sync/2365e6cda5c80ee4.json`). GLOSSARY lines 55–62 call that "ordinary fixed-window coincidence": the Kreuz ISI-adaptive window is switched off. So the row's description, and the credit attached to it, fit only the F1-alone choices. Those are ISI-adaptive, with this project's τ cap at 0.5 or 1.0 s.<br>(b) **Root:** SPIKY's own abstract calls SPIKE-synchronization "an improved and simplified extension of event synchronization": Quian Quiroga R., Kreuz T., Grassberger P. (2002), *Phys Rev E* 66:041904. The README carries this and the page does not.<br>(c) **Forward:** Kreuz's own lab published a detection step on the profile. Cecchini G. … Kreuz T. (2021), *PLoS Comput Biol* 17(5):e1008963. The last author is Kreuz, at ISC-CNR, Sesto Fiorentino. They filter to spikes coincident with at least three quarters of the other trains. The README section the page sends readers to does not cite it; `detector_history.md` does. | minor–moderate | "built on SPIKE-synchronization (Kreuz, Mulansky & Bozanic 2015, *J Neurophysiol* 113:3432–3445, an extension of Quian Quiroga, Kreuz & Grassberger 2002). The Kreuz lab's own detection step on the profile is Cecchini et al. 2021. Under the budget, the search chose a fixed 0.25 s window instead of the adaptive one." | yes: config files; SPIKY abstract (arXiv 1410.6910); Cecchini methods and authors via PMC8159272; QKG metadata |
| 4 | Table 1, CoactDetect: "designed here; excess-coincidence testing (Grün and colleagues 2002)" | (a) The README marks Grün, Diesmann & Aertsen 2002 with °, meaning *carried, not read here*. It says the shift-based null "is nearer" Amarasingham, Harrison, Hatsopoulos & Geman 2012, *J Neurophysiol* 107:517–531. The row itself describes the shift null ("against the same recording shifted in time") and credits only Grün. Unitary Events takes its expectation from firing rates, not from shifting (Elephant's UE documentation is a secondary source; the Grün paper returned 403).<br>(b) The project's record puts CoactDetect in the cell-averaging CFAR family (constant false alarm rate; `detector_history.md` §6.7). §4.3 of the page introduces a "guard of 1 s", which is radar's guard-cell idea (§5.1 there), with no lineage. rate+context gets Finn & Johnson for the same local-context structure; CoactDetect gets nothing. | minor–moderate | "designed here; excess-coincidence testing (Grün, Diesmann & Aertsen 2002, *Neural Comput* 14:43–80 and 81–119) against a time-shift null (nearest published form: Amarasingham et al. 2012). Its local context and guard are the cell-averaging CFAR structure (see rate+context)." | Grün 2002 and Amarasingham 2012 metadata: yes. Grün text: **no** (403, paywalled) |
| 5 | Table 1, locust: "a modified port of CICADA (Denis and colleagues 2020)" | (a) "Denis et al. 2020" without a DOI takes most readers to **DeepCINAC**, which is a different tool: Denis, Dard, Quiroli, Cossart & Picardo 2020, *eNeuro* 7(4). The Zenodo CICADA record even lists "Published in eNeuro 7(4)". The repo's reading log says "DeepCINAC is a different tool", and the 2026-09-16 role-2 review flagged this exact string as a misattribution. The Zenodo record does list Denis et al. as authors, 2020-07-20, v1.0.3, doi:10.5281/zenodo.10041434 (record created 2023-10-26). So the citation holds only if the DOI is given.<br>(b) **Forward:** the CICADA framework paper is Hamon M. et al. 2026, bioRxiv doi:10.64898/2026.07.03.736318, posted 2026-07-08. Its corresponding and last author is Robin F. Dard at EPFL; Cossart and Picardo are co-authors. **Which lab:** the 2020 software is from INMED (Cossart and Picardo); the 2026 framework paper is led from EPFL.<br>(c) "port of CICADA" leaves out "by way of interface2". The 1e-9 parity reaches interface2's `generate_sce_cicada`, not CICADA (`detector_history.md` §6.3). | minor–moderate | "a modified port, by way of interface2, of CICADA's SCE step (software: Denis et al., Zenodo doi:10.5281/zenodo.10041434; framework: Hamon et al. 2026, bioRxiv doi:10.64898/2026.07.03.736318)" | yes: Zenodo record; bioRxiv API; GitLab API (MIT licence, cossartlab namespace) |
| 6 | Table 1, rate+context: "the structure of Finn and Johnson 1968" | The metadata is correct: Finn H.M., Johnson R.S. (1968), RCA Review 29(3):414–464. The repo read it in full. It is the canonical source, but not established as the bottom: Hansen 1973's reference list cites earlier cell-averaging work (Hall 1962–63, Hansen 1965, Finn 1967), none of it read. | low | Optional: "after the cell-averaging structure of Finn & Johnson 1968". | metadata yes (search listing and CiNii); text not re-read by me |
| 7 | §6, t correction | **Checked:**<br>• Nadeau & Bengio, *Machine Learning* 52:239–281 (2003): correct.<br>• Bouckaert & Frank 2004, read in full. They define the "corrected repeated k-fold cv test", which scales the variance by (1/(k·r) + n2/n1). At k = 4, r = 1 and n2/n1 = 1/3 the factor on t is √(0.25/0.583) = **0.655**, so the page's 0.65 checks. They call these tests "heuristic".<br>• Bengio & Grandvalet prove there is "no **universal unbiased estimator of the variance** of K-fold CV". "No exact correction exists" is a loose paraphrase of that.<br>**The gap:** only Nadeau & Bengio gets full metadata. The other two appear as name and year only, and the README the page points to cites none of the three. | low | Add: Bouckaert R.R., Frank E. (2004), PAKDD, LNCS 3056:3–12, doi:10.1007/978-3-540-24775-3_3; Bengio Y., Grandvalet Y. (2004), JMLR 5:1089–1105. Add Nadeau & Bengio's doi:10.1023/A:1024068626366. Reword: "show that no unbiased estimator of k-fold's variance holds for every distribution". | yes: B&F full text; B&G abstract; N&B metadata |
| 8 | Provenance: "The review record for this page is docs/reviews/fair-comparison-2026-09-19.md" | That file does not exist in the tree at c261f9c. Only the role folders exist. | low (a dead pointer if it does not land with the page) | Land the file in the same commit, or drop the line until it exists. | yes |
| 9 | Opening: "An earlier comparison put the best net +0.103 F1 ahead" | Supported by `docs/goals/learned-model-family.md` line 138 (chorus_norm +0.103, t 6.5, untuned; that result lives on branch `tune-learned-vs-coact`). The page gives no pointer, although the builder's comment says "(cited below)". This is round-1 #10, still open. | low | Link the goals page row. | yes |
| 10 | §7: "the project lead's brief for this report asked for exactly that" | A named attribution with no durable record I could find. Searched: `docs/SESSIONS.md`, `docs/goals/*`, both handoffs, the builder. | low | Cite where the brief is recorded, or rephrase so it does not rest on an uncheckable instruction. | **no** |
| 11 | §3: "draughtsman, the project's architecture-diagram tool" | It is a separate BSD-3 repository, `syncytium2/draughtsman`, vendored at `third_party/draughtsman` @ 5705c46. | low | "draughtsman (github.com/syncytium2/draughtsman, a sibling project vendored here)" | yes: gh repo view; vendoring header |
| 12 | §4.1, nested cross-validation | A standard method with no pointer. This is round-1 #8, still open. | optional | Stone 1974 (JRSS B 36:111–) for the idea; Varma & Simon 2006 (BMC Bioinformatics 7:91) for the bias it removes. | not re-verified this pass (round 1 had metadata only) |

**Checked and fine:**
- HANDOFF-slow-comodulation decision 3 says "0.03 % of events".
- `2120516` is on `tune-bench-comparison`. Its `HANDOFF-workstation-tuning.md` lines 839–853 support "every value moved by less than its own bootstrap interval", and its note on participation matches §7.
- The participation text in `meta.json` matches the page word for word.
- `e8764aa` exists and carries `tools/tune_learned_vs_coact.py`.
- PR #660 exists (open, branch `draw-the-comparison-four`) and contains `docs/learned/comparison/comparison.svg`.
- Both evidence tools exist.
- The 1.6 margin is on record (goals page decision 4; `meta.json` `budget_margin`).
- The baseline-only decision is on record (Tony, 2026-09-17: `docs/goals/README.md` lines 28–32).
- LoCo chose the `symmetric` null in all 8 choices, never `maxlt`. So the greatest-of CFAR credit is not owed for this run, and the row is right to leave it out.

**Not checkable from here:** the darkroom did not resolve in this sandbox (`bugarach.paths.darkroom()` returned nothing). So these cited paths are unverified:
- the replicate's report, `2026-09-18-replicate-run-status/`
- the architectures page
- the report's darkroom copy
- `results/`

## Where each trace stopped
- **Binned SCE.** Backward: I read Cossart 2003's Methods in full. They credit the technique to Mao et al. 2001, *Neuron* 32:883–898, which returned 403 on Cell Press, with no open copy found. The trace stops one step short of that root. Forward: Malvache 2016, Bocchio 2020 and Dard 2022 are known to me from search summaries and the repo only.
- **SPIKE-synch.** Backward to Quian Quiroga, Kreuz & Grassberger 2002 (metadata only). Forward to Cecchini et al. 2021 (methods read via PMC). I did not read Kreuz's 2025 review (arXiv 2510.07140).
- **CoactDetect / Unitary Events.** Stopped at metadata and Elephant's documentation. The Grün 2002 full text is paywalled (403). I did not search Grün's surrogate-methods papers (Grün 2009; Louis, Borgelt & Grün 2010), which the GLOSSARY names for whole-train shifting.
- **CICADA.** Zenodo record, GitLab API and the bioRxiv API (Hamon 2026). I did not read the full CICADA code or the framework paper.
- **Finn & Johnson.** Metadata only. The repo's own full read stands. Earlier cell-averaging work (Hall, Hansen 1965, Finn 1967) is unread.
- **Statistics.** Bouckaert & Frank read in full. Nadeau & Bengio and Bengio & Grandvalet from metadata and abstracts; round 1 read Nadeau & Bengio in full.
- **Nets.** Deep Sets and PointNet metadata only. Earlier permutation-invariant work was not traced.

## Literatures searched and not searched
- **Searched:**
  - calcium-imaging synchrony detection: Cossart 2003 full text, the SCE term, CICADA
  - spike-train synchrony measures: SPIKY, event synchronization, Cecchini 2021
  - Unitary Events and excess coincidence
  - radar CFAR (metadata)
  - statistics for comparing learning algorithms
  - set-function networks: Deep Sets, PointNet
- **Not searched (⚠):**
  - per-channel standardization over time in networks (instance normalization, Ulyanov et al. 2016), which is chorus_norm's "standardizes it over time" step
  - permutation-invariant pooling before 2017
  - learned event detectors (DOSED family), which `detector_history.md` §3 says is an established genre
  - surrogate-method reviews for the time-shift null
  - the four CFAR-convergence literatures the README lists as never searched (genomics peak calling, seismology STA/LTA, adaptive image thresholding, changepoint detection)
  - where "SCE" was coined, beyond a search summary

## Questions for the humans (correspondence is a source)
1. Has anyone asked the CICADA authors (Dard, Picardo, Cossart) how they want it cited: the 2020 Zenodo software, or Hamon et al. 2026? If not: ⚠ nobody was asked.
2. Has anyone been asked whether CoactDetect's time-shifted local null is published, for example Grün's group? If not: ⚠.
3. The Kreuz correspondence of April 2026 is on record. If the page adopts the Cecchini point, cite it as "Kreuz, personal communication, April 2026", paraphrased, never quoted, since the repo is public.
4. Where is "the project lead's brief" for this report recorded (finding 10)?
5. Has anyone outside been asked whether the nets' design is new? If not, "this project" for the nets stays ⚠.

## Outside the artifact (the attribution record it points to)
- `docs/learned/tube_self_supervised/README.md:795` reads "Hamon **L**, et al. (2026)". bioRxiv lists the first author as **Hamon, M.** That is wrong metadata in a reference list.
- The README's SPIKE-synch citation block lacks Cecchini et al. 2021, although `detector_history.md` cites it. The page sends readers to both.

## Round-1 role-2 items, re-checked
- **#1 ("ports"):** fixed.
- **#3 (citations):** partly fixed, through the README pointer.
- **#4 (SCE):** partly fixed. "Circularly shifted" is now stated, but not the divergence from 2003's reshuffling (my #2).
- **#7 (Deep Sets):** not fixed (my #1).
- **#8 (nested CV):** not fixed (my #12).
- **#10 (earlier result):** not fixed (my #9).

Sources: [Cossart 2003 PDF (Columbia)](https://blogs.cuit.columbia.edu/rmy5/files/2017/06/cossart.nature.03.pdf) · [CICADA Zenodo](https://zenodo.org/records/10041434) · [CICADA GitLab](https://gitlab.com/cossartlab/cicada) · [Hamon et al. 2026 (bioRxiv)](https://www.biorxiv.org/content/10.64898/2026.07.03.736318v1) · [SPIKY arXiv](https://arxiv.org/abs/1410.6910) · [Cecchini et al. 2021 (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8159272/) · [Event synchronization (Caltech record)](https://authors.library.caltech.edu/records/z5nws-yap77) · [Grün 2002 I (MIT Press)](https://direct.mit.edu/neco/article-abstract/14/1/43/6571/Unitary-Events-in-Multiple-Single-Neuron-Spiking) · [Elephant UE docs](https://elephant.readthedocs.io/en/latest/reference/unitary_event_analysis.html) · [Amarasingham 2012](https://journals.physiology.org/doi/full/10.1152/jn.00633.2011) · [Finn & Johnson (CiNii)](https://cir.nii.ac.jp/crid/1570009750913923200?lang=en) · [Nadeau & Bengio 2003](https://link.springer.com/article/10.1023/A:1024068626366) · [Bouckaert & Frank 2004 PDF](https://ml.cms.waikato.ac.nz/publications/2004/bouckaert-frank.pdf) · [Bengio & Grandvalet 2004](https://www.jmlr.org/papers/volume5/grandvalet04a/grandvalet04a.pdf) · [Deep Sets](https://proceedings.neurips.cc/paper/2017/hash/f22e4747da1aa27e363d86d40ff442fe-Abstract.html) · [PointNet (CVF)](https://openaccess.thecvf.com/content_cvpr_2017/html/Qi_PointNet_Deep_Learning_CVPR_2017_paper.html) · [Mao 2001 (PubMed)](https://pubmed.ncbi.nlm.nih.gov/11738033/) · [Malvache 2016](https://www.science.org/doi/10.1126/science.aaf3319)
