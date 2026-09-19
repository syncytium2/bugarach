<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round3/. -->

GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

Role 2 (DOI or Die), round 3 blind pass. I reviewed the built artifact `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html`. I confirmed `git hash-object` = 5c0ccbb and worktree HEAD = 6eb9b29. I did not open earlier review rounds or any run record, and I edited nothing. My scratch text extraction is at `%USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\r3-role-2\`.

## What I checked

**External references.** I checked every one:
- Zaheer 2017 and Qi 2017 (PointNet)
- Grün, Diesmann & Aertsen 2002; Amarasingham 2012
- Cossart, Aronov & Yuste 2003; CICADA on Zenodo
- Kreuz 2015; Quian Quiroga 2002
- Finn & Johnson 1968; Varma & Simon 2006
- Nadeau & Bengio 2003; Bouckaert & Frank 2004; Bengio & Grandvalet 2004
- draughtsman

**Named attributions inside the repository.** I checked goal 1 and the +0.103 figure, the project lead's decisions, "decision 3" in the handoff, commits e8764aa and 2120516, pull request #660, the scorer's own documentation, the threshold picker's edge flag, and the claim that `build_chorus_norm()` builds plain chorus.

**Where I got the texts:**
- Shelf copies at `<darkroom>/bugarach/lit/`, read with pdftotext: Deep Sets, PointNet, Finn & Johnson, Amarasingham 2012, Pipa 2008, Dard 2022, Bocchio 2020.
- PubMed Central full text of Kreuz 2015.
- Europe PMC for Grün 2002 parts I and II, and for Varma & Simon.
- Publisher pages: PLOS (Cecchini 2021), Zenodo, JMLR, Springer.
- The Waikato PDF of Bouckaert & Frank.

**Correspondence.** The page quotes no third party's private correspondence. That check is clean.

## Findings
Format: location · issue · severity · suggested fix · verified against a source.

1. **Table 1, SPIKE-synch row (and §9, "switched off the window its credit is for")** · The detection layer is presented as ours, sitting on Kreuz's measure. That misses the forward trace. The measure's own lab published a detection step on this profile: Cecchini et al. 2021, *PLoS Comput Biol* 17(5):e1008963. Kreuz is last author, at ISC-CNR. Their step keeps only spikes coincident with at least three quarters of the other trains. The repository already records this, together with Kreuz's April 2026 correspondence, in `docs/detector_history.md:168-169`. The page cites neither. · **major** · Add to the row: "detection layer written here; the measure's authors published the same kind of layer (Cecchini et al. 2021; Kreuz, personal communication, April 2026)". Cite it; do not quote it. · **yes**

2. **Table 1, CoactDetect row: "time-shifted copy, whose nearest published form is Amarasingham 2012"** · Amarasingham 2012 reviews jitter, meaning individual spikes resampled within windows (basic and interval jitter). In the shelf copy, "shift" appears only in one reference title. CoactDetect instead circularly shifts each ROI's whole event train inside a context window (`coact.py` lines 7-8 and 151). Two published forms are nearer:
   - The per-cell independent circular-shift null for coactive-cell counts: Dard et al. 2022, *eLife* 11:e78116 (300 surrogates, 99th percentile); Bocchio et al. 2020, *Nat Commun* 11:4559.
   - Random shifting of whole spike trains to test excess joint-spike events in sliding windows: Pipa, Wheeler, Singer & Nikolić 2008, *J Comput Neurosci* 25:64–88 (NeuroXidence), which is on the shelf and marked unread.

   · **major** · Replace or qualify the Amarasingham claim; name the circular-shift and whole-train-shift sources. · **yes**

3. **Table 1, CoactDetect row: Grün, Diesmann & Aertsen 2002, *Neural Computation* 14:43–80** · That is Part I, which covers stationary data. The rate-local, rolling form is Part II, "Nonstationary data", 14(1):81–119. Its abstract says it analyses overlapping segments "by sliding a window of constant width". Part II is the nearer credit, and the repository README already cites both parts. · moderate · Add Part II. · **yes**

4. **Table 1, CoactDetect row: "its local context and guard are the cell-averaging structure credited under rate+context"** · The guard is misattributed. Finn & Johnson 1968 exclude only the cell under test (the delay line's centre tap). No guard band appears in the shelf text, and `detector_history.md` (around line 625) records this correction. Guard cells are documented as routine by Rohling 1983, *IEEE T-AES* AES-19(4):608–621, Fig. 3(b). · moderate · Credit the local context to Finn & Johnson and the guard to later cell-averaging practice (Rohling 1983). · **yes**

5. **Table 1, "designed here" for CoactDetect, LoCo and rate+context; rate+context's "after the cell-averaging structure of Finn and Johnson 1968"** · Two problems:
   - "After" implies the design was derived from Finn & Johnson. The record says the opposite: the author was unaware of that work, so this is convergence (`detector_history.md:155-161`, the author's recollection, 2026-08-29).
   - The README says four literatures have never been searched: genomics peak calling, seismological STA/LTA, adaptive image thresholding and changepoint detection. It says to read "designed here" as "not found elsewhere yet". The page drops that caveat.

   · moderate · Rewrite as "designed here, independently; later found to match the cell-averaging structure of Finn & Johnson 1968", and add a short note naming the unsearched fields. · yes for the record; ⚠ I did not search those fields either.

6. **Table 1, binned SCE row: "descends from Cossart, Aronov and Yuste 2003 … interval reshuffling at P < 0.05"** · The bibliographic details are correct: *Nature* 423:283–288, Columbia, Yuste last author. The Methods content is second-hand:
   - It was carried from interface2's reading (`docs/todo/2026-08-24-the-methods-are-not-ours-...md:75-80`). No 2003 PDF is on the shelf, and my own fetch hit Nature's login redirect.
   - The 2003 paper credits Mao et al. 2001, *Neuron* 32:883–898, which nobody has reached. So 2003 is the root reached, not established; the page does not say so.
   - The row says the circular-shift null "is not that rule" but never credits the circular shift itself (Dard 2022; Bocchio 2020, both on the shelf and read).

   · moderate · Add the stopping point ("root reached; it credits Mao 2001, not obtained") and cite Dard 2022 and Bocchio 2020 for the circular shift. Shelve the 2003 PDF. · partly: metadata yes, Methods text no (paywall; verified to one step short).

7. **§2, "the scorer's own documentation says to read the order of its rows, not their third decimal place"** · That misquotes the source. `score.py:78-79` says to read the ORDER of the rows, "never the decimal places of one". The page narrows that to the third decimal, while its headline margins (0.007 and 0.010) sit in the second and third decimal. · moderate · Paraphrase it faithfully: "…read the order of its rows, never the decimal places of one". · **yes**

8. **§4.1, "Bouckaert and Frank (2004…) carry it to k-fold cross-validation as a heuristic"** · The paper does not call its own extension a heuristic. It justifies it as "cross-validation is a special case of random subsampling" and names it the "corrected repeated k-fold cv test" (§3.3). "Heuristic" appears only for earlier t-test variants. It is also for repeated (r × k) cross-validation. The metadata (LNCS 3056:3–12) is correct. · minor · "…carry it to repeated k-fold cross-validation, treating k-fold as a special case of random subsampling". Keep the page's own "they are not tests" conclusion as the page's judgement. · **yes**

9. **Table 1, SPIKE-synch: "by default with a coincidence window set by the local gaps"; Quian Quiroga, Kreuz and Grassberger 2002** · The adaptive local-gap window comes from event synchronization. Kreuz 2015 (PMC4455566) says SPIKE-synchronization "builds on the same bivariate and adaptive coincidence detection that was used for event synchronization". §9 credits the window to the 2015 row. The 2002 reference also has no venue. · minor · Credit the window to 2002 and add "Phys Rev E 66:041904". · **yes**

10. **Table 1, the three "Deep Sets shape" rows** · Metadata verified (NIPS 2017 = NeurIPS 30; PointNet, CVPR 2017; PointNet's arXiv version predates Deep Sets'). Two gaps:
    - The chorus nets pool three ways (mean, spread, loudest few). Multi-aggregator pooling is prior art in Corso et al. 2020, *Principal Neighbourhood Aggregation*, NeurIPS 33 (mean, max, min and standard deviation). It is uncited.
    - Neural population decoders that treat units as a set (e.g. POYO, Azabou et al. 2023, on the shelf) were not searched by me.

    · minor · Optionally cite Corso 2020 for the multi-statistic pool. · yes (PNA at abstract level)

11. **Table 1, tube and line_length: "compares … with its own surroundings in time"** · Both are a centre-surround difference of Gaussians, and `tube.py` (around lines 170-185) calls them "two classical results in a network's clothing" (cell-averaging CFAR). The page credits this local-context structure on the coded rows only. · minor · Add "the same local-context comparison credited under rate+context" to those two rows. · **yes**

12. **Table 1, locust row (CICADA, doi:10.5281/zenodo.10041434)** · The DOI resolves:
    - Creators: Denis, Dard, Quiroli, Cossart, Picardo. Version 1.0.3, 2020.
    - Forward trace: the framework paper exists (Hamon et al. 2026, bioRxiv, on the shelf). The shelf's decision is to cite the software, because that paper states no SCE null.
    - The repository's citation ledger (the same 2026-08-24 todo, line 95) says to cite Dard 2022 alongside it. The page does not.
    - Not in the page, for information only: Zenodo lists the record as CC-BY-4.0, while the README says MIT for the GitLab source.

    · minor · Add Dard 2022 (what CICADA's SCE threshold is in the lab's own use). · **yes**

13. **Table 1, rate+context (Finn & Johnson 1968, *RCA Review* 29:414–464)** · The metadata checks out against the shelf copy. Finn & Johnson's own reference list cites Finn 1967 in RCA Review. The repository also lists Hall 1962–63 and Hansen 1965 as cell-averaging citations. So 1968 is the root reached, not a proven origin. · minor · Optional: "the canonical citation; earlier Finn 1967 exists". · **yes**

14. **§4.1, Nadeau & Bengio 2003** · The metadata and DOI are correct, and the √(3/7) = 0.655 factor for J = 4 and n2/n1 = 1/3 is right. The first appearance was the NIPS 12 conference paper of the same title (1999, printed 2000); the journal paper is the restatement. · minor, informational · None required. · **yes**

## Verified clean
- Varma & Simon 2006, *BMC Bioinformatics* 7:91.
- Bengio & Grandvalet 2004, *JMLR* 5:1089–1105.
- The 3.18 critical value at 3 degrees of freedom.
- draughtsman: public, BSD-3-Clause.
- Pull request #660: open, and contains `docs/learned/comparison/comparison.svg`.
- Commit e8764aa, and commit 2120516 on `tune-bench-comparison`; both `HANDOFF-workstation-tuning.md` and `HANDOFF-slow-comodulation-on-the-de-pinned-export.md` exist on that branch.
- `HANDOFF-slow-comodulation-on-the-de-pinned-export.md` decision 3 (`bench.MEASURED_ROLE` still points at the contaminated folder), on main.
- Goal page +0.103 (`docs/goals/learned-model-family.md:62`).
- The project lead's baseline-only decision of 2026-09-17 (`docs/goals/README.md:32`).
- `build_chorus_norm()` builds plain chorus when called directly (`chorus_norm.py` passes `cfg` straight through; `norm=True` lives only in the registry).
- The threshold picker's `at_edge` flag (`train.py:385`).

## Residual ⚠
- **Where the trace stopped:** at Cossart 2003's Methods (paywalled; the quote is carried from interface2, one step short) and at Mao 2001 (not reached). The one LoCo configuration I read (`configs/loco/5382dd2a3f4253be.json`) uses `null_context_mode: "symmetric"`, so the greatest-of credit may not apply to that choice. I did not check every fold's selection.
- **Literatures searched:** the repository shelf (radar/CFAR, spike-train surrogates, calcium coordination, set models in deep learning, ML), PubMed Central, Europe PMC, PLOS, Zenodo, JMLR, Springer.
- **Not searched:** genomics peak calling, seismological STA/LTA, adaptive image thresholding, changepoint detection, and neuroscience decoders that treat units as a set, beyond the shelf.
- **Nobody was asked:** I cannot ask the humans. The main thread should ask the project lead whether there has been any correspondence with the Cossart/Picardo lab about the locust port, or with the Grün or Amarasingham groups about the null. The Kreuz correspondence (April 2026) exists and is not cited on the page (finding 1).
- **Not read in full by me:** Quian Quiroga 2002 (bibliographic check only) and Grün 2002 (abstracts only).
