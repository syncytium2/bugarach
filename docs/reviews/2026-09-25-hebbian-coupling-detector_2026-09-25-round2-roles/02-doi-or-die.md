GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
(I also hold SubagentHandback. I have no Edit, Write or NotebookEdit. No repository file was modified. The only thing written to disk was fetch scratch under `.../scratchpad/mb2/`.)

# Role 2: citation and reference check of `docs/proposals/2026-09-25-hebbian-coupling-detector.md`

## Bottom line
- **No fabricated bibliographic metadata.** All 7 DOIs resolve on Crossref, and title, authors, journal, volume, issue and pages match what is written.
- **Two attributions misplace their support** (F1, F2).
- **One unreached source is missing from the ⚠ line**, and it is the one the paper itself names as its full treatment (F3).
- **One named method has no citation** (F7).
- **One reference is never cited in the body** (F6).

## Metadata checks (Crossref API, 2026-09-25)

| reference | result |
|---|---|
| von der Malsburg & Schneider 1986 | 10.1007/BF00337113, *A neural cocktail-party processor*, Ch. von der Malsburg and W. Schneider, *Biol Cybern* 54(1):29–40. OK. Closed access: OpenAlex and Semantic Scholar both show no open-access copy. |
| Ahn, Bagrow & Lehmann 2010 | 10.1038/nature09182, *Nature* 466(7307):761–764. OK. |
| Cutts & Eglen 2014 | 10.1523/JNEUROSCI.2767-14.2014, *J Neurosci* 34(43):14288–14303. OK. PMC4205553. |
| Kempter, Gerstner & van Hemmen 1999 | 10.1103/PhysRevE.59.4498, *Phys Rev E* 59(4):4498–4514. OK. |
| Sejnowski 1977 | 10.1007/BF00275079, *J Math Biol* 4(4):303–321. OK. |
| Stark & Abeles 2009 | 10.1016/j.jneumeth.2008.12.029, *J Neurosci Methods* 179(1):90–100. OK. |
| Aicher, Jacobs & Clauset | arXiv:1404.0431 exists. The published version is 10.1093/comnet/cnu026, *J Complex Networks* 3(2):221–248 (2015; online 2014). See F5. |

## Findings

Each row: location · issue · severity · suggested fix · verified against a source (yes/no)

**F1.** Real-recording stage, "The unit of replication is the mouse: 66 recordings from 36 mice (ADR-0008)"
- **Issue:** ADR-0008 (`docs/adr/0008-the-event-floor-is-set-per-window-from-its-own-null.md`) is about the event floor. It gives the count ("66 recordings from 36 mice", line 33) and says "Group is nested in imaging day" (line 106). It makes no ruling that the mouse is the unit of replication. That phrase appears nowhere else in `docs/` (grep, excluding reviews).
- **Why it matters:** the ADR is cited as authority for a ruling it does not make. Meanwhile the previous bullet, on nesting, actually comes from ADR-0008 and is left uncited.
- **Severity:** medium.
- **Fix:** cite ADR-0008 for the count and for the nesting. Either state the mouse as this page's own position or cite the real source of that ruling.
- **Verified:** yes.

**F2.** "What this does not claim", third bullet: "the first stability test reproduces and the second does not (its CLAIMS item 5)"
- **Issue:** clamor `CLAIMS.md` item 5 only says the *second* (single-block, p. 36) test does not reproduce. That the first one reproduces is recorded in `clamor/README.md:63` and `lit/malsburg-1986-implementation.md:247`, not in item 5.
- **Issue, same bullet:** "Equation 8's step size re-locks streams the dynamics had separated (item 2)" drops item 2's condition. Item 2 says this happens *under the E correction*, and that the step size "cannot cause the uncorrected one-step failure".
- **Severity:** low.
- **Fix:** cite README / implementation.md for the first test. Restore the "under the E correction" condition.
- **Verified:** yes, against clamor at c25c7e5.

**F3.** Method detail, "The source", and the References ⚠ line
- **Issue:** the backward trace stops at the 1981 report and leaves out Schneider's 1986 Göttingen doctoral thesis. Per clamor's reading of the paper (`lit/malsburg-1986.md`), the paper's Discussion names that thesis as the complete treatment. clamor has an unconfirmed interlibrary-loan request for it (`clamor:docs/ill-schneider-1986.md`: two failed ILLiad submissions on 2026-09-05, an email on 2026-09-06, OCLC 46202873, a subito fallback after 2026-09-30).
- **Why it matters:** this is the one source likely to settle the step-size and row/column questions this page sweeps around. It is also already-asked correspondence, which the "What is asked" item on writing to von der Malsburg should mention.
- **Severity:** medium.
- **Fix:** add to "Not reached": *Schneider W. (1986), doctoral thesis, Univ. Göttingen, ILL requested by clamor 2026-09-06, unconfirmed.* Mention the ILL in the "What is asked" correspondence item.
- **Verified:** yes, against the clamor record. The thesis itself was not seen.

**F4.** "⚠ Neither the 1986 PDF nor the 1981 report was reachable during review", and the 1981 entry in References
- **Issue, 1986 PDF:** "not reachable" is true on this machine, but the PDF is **held**. clamor `lit/malsburg-1986.md` says "Status: HELD, 2026-09-05", gitignored, on Tony's machine. Under `docs/lit_needed.md` the proper move is to ask Tony for it, not to settle for the transcription.
- **Issue, 1981 report:** it is the author's own deposit at `web-archive.southampton.ac.uk/cogprints.org/1380/1/vdM_correlation.pdf`. clamor verified it live earlier. Today it returns 403 (a bot check) to curl and WebFetch, so a person with a browser can get it.
- **Issue, metadata:** the 1981 entry gives only title and year. Full details: Internal Report 81-2, Max-Planck-Institut für Biophysikalische Chemie, Göttingen. Reprinted in Domany, van Hemmen & Schulten (eds.), *Models of Neural Networks II* (Springer, 1994), pp. 95–119, doi:10.1007/978-1-4612-4320-5_2. Checked on Crossref.
- **Issue, shelf:** neither paper, nor any other cited paper, is listed in `docs/lit_needed.md`.
- **Severity:** medium.
- **Fix:**
  - Change the wording to "held by Tony (clamor/lit), not read in this review".
  - Complete the 1981 entry.
  - Add the 1986 PDF, the 1981 report and the Schneider thesis to `lit_needed.md`.
- **Verified:** yes (metadata, HTTP status, clamor record).

**F5.** References, the Aicher entry; body "(Aicher, Jacobs & Clauset 2015)"
- **Issue:** the entry gives the arXiv number with no year and no journal. The body's year 2015 belongs to the journal version.
- **Issue, origin:** the model first appeared in Aicher, Jacobs & Clauset 2013, *Adapting the stochastic block model to edge-weighted networks*, arXiv:1305.5782 (ICML workshop).
- **Issue, content:** "handles signed weights" is plausible, because the model takes any exponential-family weight distribution, which includes the Normal. But I found no sentence in the paper that says signed weights are handled; I could not extract the PDF text.
- **Severity:** low.
- **Fix:** cite *J Complex Networks* 3(2):221–248 (2015), doi:10.1093/comnet/cnu026, and optionally the 2013 origin. Phrase it as "real-valued weights via a Normal edge distribution" unless someone confirms it from the text.
- **Verified:** partly: metadata yes, the signed-weight claim no.

**F6.** References, the Stark & Abeles 2009 entry
- **Issue:** it is cited nowhere in the body.
- **Issue, description:** the note calls it "a cross-correlogram statistic with a hollowed window". In the paper the partially hollowed Gaussian kernel builds the *baseline predictor* (the correlogram convolved with a hollowed kernel), which is then subtracted. It is not the statistic's own window. The resemblance to "positive centre, negative flanks" is only through that subtraction. Checked against the ScienceDirect listing and secondary descriptions (σ 10 ms, hollow fraction 60%), not the full text.
- **Severity:** low.
- **Fix:** cite it where the kernel is introduced ("The idea" or "Why this rule"). Reword to "a correlogram baseline from a partially hollowed kernel; the correlogram minus that baseline has the kernel's centre-minus-flanks shape".
- **Verified:** partly: metadata yes, full text no.

**F7.** Readout 2, "the fixed-margin (curveball) null"
- **Issue:** the curveball algorithm is named without a citation. The repo's own `docs/assembly_report.md` (lines 103 and 445–449) cites Strona et al. 2014 and Carstens 2015 (*Phys Rev E* 91:042812) for it.
- **Severity:** low.
- **Fix:** add both references, copied from the assembly report's list, after checking them.
- **Verified:** yes, that the repo citations exist. Their metadata was not re-checked in this review.

**F8.** Method detail, "Rate neutrality is in the mean": "…(Kempter et al. 1999). Before the clamp that is exact, not approximate."
- **What checks out:** Kempter et al. Sec. III.B (text extracted from the paper) derives the window-driven drift as W̃(0)·ν_in·ν_out, with W̃(0) = ∫W(s)ds. A zero-integral window therefore removes rate-product drift. So "Its kernel averages to zero … That principle is Kempter…" is supported.
- **Issue:** the derivation rests on two stated approximations: no input–output correlations beyond the rates, and rates changing slowly compared with the window width. Placed next to "(Kempter et al. 1999)", "exact" reads as that paper's result. It is exact only for independent *stationary* trains. For independent trains with rates that change within ±m frames, the expected update is Σ_k Co(k)·Σ_t λ_i(t)λ_j(t+k), which is not zero in general.
- **Also:** Kempter's window is asymmetric (pre before post), and the page applies the principle to a symmetric kernel. The principle carries over; say that it is being carried over.
- **Severity:** medium.
- **Fix:** "exact in expectation for independent trains whose rates are constant over ±m frames (the slow-rate condition of Kempter et al. 1999); slow drift is what the simulation stage measures."
- **Verified:** yes. I read the Kempter text from an earlier round's scratch extraction (`scratchpad/mb/k.txt`; title page and Sec. III checked) and did not re-download it.

**F9.** "Why this rule", first bullet, and the title "von der Malsburg–Schneider plasticity rule"
- **Issue:** the rule's mechanism, synaptic modulation, comes from von der Malsburg 1981. What the 1986 pair add is the concrete equations 7–8. The body says this ("It applies the synaptic modulation of von der Malsburg's 1981 correlation theory").
- **Issue, labs:** "Which lab" is von der Malsburg's group: Abteilung Neurobiologie, MPI für Biophysikalische Chemie, Göttingen, taken from clamor's reading of the title page. The page asks about writing to "von der Malsburg or his group", which fits that. The page names no other labs, so there is nothing to misattribute.
- **Severity:** informational.
- **Fix:** optionally say "the 1981 rule in the 1986 paper's equations 7–8".
- **Verified:** partly: the 1981 abstract via Springer and search, yes; the 1981 text, no.

**F10.** Method detail: the `malsburg1986.py` transcription claims (equation 7 cosine and `INTERPOLATED`, equation 8 form, subliminal rule on p. 33, s₀ = 0.012, s_d = 0.8, q₀ = 0.01, clamp at 0.0216, "p. 35 implies about 0.01/12", modulo wrap)
- **Result:** every claim matches clamor at c25c7e5: `malsburg1986.py` lines 79–97 and 207–285, and CLAIMS item 2.
- **Arithmetic:** 0.012 + 0.01 = 0.022 > S_MAX = 0.0216, and s₀s_d/2 = 0.0048. Both correct.
- **Caveat:** every page citation here comes second-hand through clamor's quotes, and the page says so.
- **Severity:** none.
- **Verified:** yes, against the transcription only.

**F11.** "Tony chose a stamped copy over a dependency on 2026-09-25, in the session that wrote this page"
- **Issue:** this is a named attribution with no durable record. No ADR exists; the list ends at 0009, and the page defers the ADR to the first copying commit.
- **Severity:** low.
- **Fix:** fine as long as the ADR follows. Meanwhile, point to where the ruling is written down, or date it and mark it "recorded here only".
- **Verified:** no.

**F12.** Abbreviations: "Stream: the fast or slow class … (FOUNDATIONS §3)"
- **Issue:** FOUNDATIONS §3 says FAST/SLOW is "a convention of this project's stores, **not** of bugarach", and that streams are generic. ADR-0008 line 30 refers to "all three streams". So §3 supports "stream", not "fast or slow" as its definition.
- **Severity:** low. This belongs to the domain-accuracy role; I am filing it once here.
- **Fix:** "a class of calcium event (on this project's stores, fast or slow; FOUNDATIONS §3)".
- **Verified:** yes.

**F13. Checked internal attributions, all consistent**
- FOUNDATIONS §9: baseline only; background-rate intervals; group-dependence mandatory.
- `decisions_pending.md` item 2: σ = 0.106 s fast and 0.135 s slow, ruled 2026-09-22.
- The goal page's rows on recording identity and "Waiting on Tony: quiet → busy".
- The open-risks todo item 1: modularity cannot see overlapping groups.
- `assembly_report.md` line 26: core–periphery given as an interpretation.
- ADR-0007.
- clamor's open licence item concerns copied tooling (clamor README line 97 onward). Both repositories are BSD-3.
- clamor's "letter still to write" (CLAIMS item 6).
- **Not checked:** the "200 surrogate draws" count and "2 s tile, never stored" (left to the numbers role).
- **Verified:** yes.

## Forward trace, and prior art for the "rule as detector" framing

**FT1. Fast weights.** The fast-weights literature traces itself to von der Malsburg 1981 as its origin. Examples: Irie, Schmidhuber et al., arXiv:2211.09440 and arXiv:2508.08435, both of which list von der Malsburg 1981 and Hinton & Plaut 1987 as the start of fast synaptic modulation. So the page's "Not searched: fast weights" is a real and relevant residual, not a formality.
- **Severity:** ⚠ residual.
- **Verified:** from search summaries only; the papers were not read.

**FT2. STDP as a pattern detector.**
- **Gap:** an adjacent literature the page neither cites nor lists as unsearched: plasticity rules used *as unsupervised detectors* of repeating coincidence structure in spike trains. The root is Masquelier, Guyonneau & Thorpe 2008, *PLoS ONE* 3:e1377, doi:10.1371/journal.pone.0001377 (DOI checked on Crossref); follow-ups are in that lineage.
- **Difference from this page:** those learn a detector *neuron's* input weights, whereas the page learns a pairwise coupling matrix. It is still the closest prior art I found for the "plasticity rule as detector" framing.
- **Severity:** medium, as a residual ⚠.
- **Fix:** name it under "Not searched", or cite it as related and state the difference.
- **Verified:** metadata only.

**FT3. von der Malsburg's own later work.**
- von der Malsburg & Buhmann 1992, *Biol Cybern* 67:233–242 (per clamor, closed access).
- The dynamic-link line of work.

I found no later paper by the von der Malsburg group that applies synaptic modulation to *recorded* data. The search was shallow (two web queries), so this is not a clearance.
- **Verified:** no.

## Literatures searched, and not
- **Searched:**
  - Crossref, Semantic Scholar, OpenAlex and Europe PMC, for metadata and open-access status.
  - Web search on the 1981 report's publication history.
  - Stark & Abeles's hollowed kernel.
  - The WSBM (the weighted stochastic block model).
  - STDP/Hebbian rules as pattern or assembly detectors.
  - von der Malsburg synaptic modulation applied to recordings.
  - The fast-weights history.
  - Internal: bugarach `docs/`, clamor `CLAIMS.md`, `lit/`, README and `docs/ill-schneider-1986.md`.
- **Not searched:**
  - Oscillator-synchronization physics.
  - Mexican-hat / symmetric learning-window theory beyond Kempter.
  - Assembly detection from calcium imaging using Hebbian or plasticity-based methods, beyond one generic query.
  - Signed-network community detection beyond the WSBM.
  - The fast-weights ML literature itself (only its history, which confirms the link).
- **Full texts actually read:** Kempter 1999 (extracted text). Cutts & Eglen was checked through a WebFetch summary of PMC: the paper does not address empty trains, so "STTC is undefined for them" is the page's own inference, which is correct from P_A = 0/0 and is not attributed to the paper. Everything else was checked against abstracts or metadata only.

## Residual ⚠
1. The 1986 paper was verified only against clamor's transcription.
2. The 1981 report was not read; the Cogprints copy returns 403 to automated fetches.
3. The Schneider thesis was not reached; the ILL request is unconfirmed.
4. **Nobody was asked:** I could not ask whether anyone has corresponded with von der Malsburg or FIAS. The clamor record shows the letter unwritten, and the ILL email of 2026-09-06 is the only correspondence on record. The page rightly asks Tony this; it stays ⚠ until he answers.
5. The fields in "Not searched" above.

## Files
- `docs/proposals/2026-09-25-hebbian-coupling-detector.md`
- `clamor:clamor/malsburg1986.py`
- `clamor:CLAIMS.md`
- `clamor:README.md`
- `clamor:lit/malsburg-1986.md`
- `clamor:lit/malsburg-1986-implementation.md`
- `clamor:docs/ill-schneider-1986.md`
- `docs/adr/0008-the-event-floor-is-set-per-window-from-its-own-null.md`
- `docs/FOUNDATIONS.md`
- `docs/assembly_report.md`
- `docs/lit_needed.md`

## Sources
- [Correlation Theory, Springer reprint](https://link.springer.com/chapter/10.1007/978-1-4612-4320-5_2)
- [arXiv:1404.0431](https://arxiv.org/abs/1404.0431)
- [WSBM code page](https://aaronclauset.github.io/wsbm/)
- [Cutts & Eglen, PMC4205553](https://pmc.ncbi.nlm.nih.gov/articles/PMC4205553/)
- [Stark & Abeles, ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0165027009000053)
- [Irie et al., arXiv:2211.09440](https://arxiv.org/pdf/2211.09440)
- [arXiv:2508.08435](https://arxiv.org/pdf/2508.08435)
- [Masquelier et al. 2008, doi:10.1371/journal.pone.0001377](https://doi.org/10.1371/journal.pone.0001377)
