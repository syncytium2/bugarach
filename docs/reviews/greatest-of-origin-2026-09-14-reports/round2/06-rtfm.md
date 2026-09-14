GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

**Sources I read before reviewing:** the `loco.py` source in the worktree (`_detect_stream`, `_threshold_pool`, and the `loco_detect` defaults). I ran `pdftotext -layout` on five shelf PDFs: Hansen & Sawyers 1980, Rohling 1983, Gandhi & Kassam 1988, the IEE Conf. Publ. 105 contents notice, and Hansen's IEEE author profile. I also read the US 4,318,101 page. I searched the web once, to confirm the OSGO-CFAR reference below.

## Findings

**1. The `maxlt` row in the `detector_history.md` §4 table labels it "greatest-of (CAGO-CFAR)"**
- **Issue:** "CAGO" means cell-averaging greatest-of: the larger of two arithmetic means (or sums), then multiplied by a scale factor. Rohling eq. 7 is *"the maximum of two arithmetic means"*, and Gandhi & Kassam eq. 22 is Z = max(Y₁, Y₂), the larger of two sums.
  - `maxlt` does not do that. Each half, `_threshold_pool`, returns the 99.9th percentile of a circular-shift surrogate null. The code then takes `thr_a[ai] = max(tl, tr)` and compares `s_obs > thr_bin` directly, with no scale factor.
  - So what it selects between are two high order statistics, not two means. The same table says so two rows down ("99.9th percentile … kin to ordered-statistic"). In radar terms this is greatest-of selection over order-statistic halves, which has its own name: OSGO-CFAR (Elias-Fusté, de Mercado & Davó, IEEE T-AES 26(1), 1990, 197–202).
  - This matters more now that Hansen & Sawyers is the only source in that cell. Their 0.1–0.3 dB loss is exact only for cell-averaging with GO, a square-law detector and a Swerling 1 target. Beside a "CAGO" label, a reader will assume that figure applies to LoCo.
- **Severity:** major
- **Fix:** Write "greatest-of selection (GO)", and optionally "over order-statistic halves; cf. OSGO". Or at least drop the "CA" prefix. Say the 1980 loss analysis covers the cell-averaging form.
- **Verifiable against a source:** yes (`loco.py` lines 506–518; Rohling p. 609 eq. 7; Gandhi & Kassam eq. 22; the Elias-Fusté citation via web search).

**2. README, LoCo/CoactDetect bullet: `maxlt` "takes the larger of its trailing and leading background estimates"**
- **Issue:** Each side's value is a finished threshold (the 99.9th percentile of that half-window's shuffled coactivity), not an estimate of background level. In CFAR usage a background estimate is the Z that gets scaled by T to make a threshold. LoCo has no such scaling step, so calling these "background estimates" misdescribes both LoCo and the CFAR mapping.
- **Severity:** minor
- **Fix:** "takes the larger of two local thresholds, a high percentile of shuffled coactivity in the trailing half-window and in the leading half-window, which is greatest-of selection…"
- **Verifiable against a source:** yes (`loco.py` `_threshold_pool`, and `fire = (s_obs > thr_bin)`).

**3. README: "Greatest-of's detectability cost in radar is **measured** in Hansen & Sawyers (1980)"**
- **Issue:** The paper computes the cost; it does not measure it. The curves come from an exact analysis in the Sawyers memo (square-law detector, Swerling 1 target), backed by Monte Carlo simulation with importance sampling. They give the *additional* loss relative to basic cell-averaging CFAR in homogeneous noise. "Measured" suggests an empirical result.
- **Severity:** minor
- **Fix:** "the additional detectability loss of greatest-of selection over cell-averaging is computed in…"
- **Verifiable against a source:** yes (Hansen & Sawyers §§I–III).

**4. §4 "What we do not know", the first two bullets**
- **Issue:** The list leaves open "whether the 1973 paper introduced greatest-of selection or analyzed a technique already in use" and "who proposed it: Rohling credits Moore & Lawrence…". But the section's own first bullet already reports two dated facts that limit both questions:
  - Sawyers' exact analysis of the detection performance of cell-averaging CFAR with greatest-of selection is dated 15 February 1972. That is 20 months before the October 1973 paper, by a different author at a different company, and the 1980 acknowledgment says the two lines of work were independent.
  - So Moore & Lawrence (1980) cannot be the first proposal of greatest-of in the sources held. Rohling's "proposed" is not a priority claim.
  - Stating those dates does not name an origin, so it stays within Tony's brief. Leaving them unconnected presents two readings as equally open when the held sources already rule one out as first.
- **Severity:** minor
- **Fix:** Add one factual sentence, not an origin claim. For example: "The held sources already date a written analysis of greatest-of selection to February 1972 (Sawyers, independently of Hansen), before both the 1973 paper and Moore & Lawrence 1980." Reword the "who proposed it" bullet so it does not present Moore & Lawrence 1980 as a live candidate for first proposal.
- **Verifiable against a source:** yes (Hansen & Sawyers p. 115, Introduction and §II "derived as follows [2]"; reference [2]; Acknowledgment).

## Checked and found accurate

- **Hansen & Sawyers quotes:** *"a simple rule for determining the detectability loss"*, *"based on a simplified analysis and simulation results of limited accuracy"*, the memo title and date, *"prepared from [2]"*, and *"are derived from independent work performed by the two authors"* all match the PDF. The inference "so the 1973 paper treated greatest-of" follows. "Detectability loss" is used in the paper's own sense.
- **"Split" mean-level detector:** the doc only quotes the memo title and draws no inference from the word. That is consistent with Rohling's "split neighborhood" wording for cell-averaging and CAGO.
- **Rohling quotes:** *"Moore et al. [3] proposed a different estimation method. The CAGO CFAR applies the maximum of two arithmetic means"* and *"Hansen et al. [2] have investigated CAGO CFAR"* match. [3] is Moore & Lawrence at the 1980 IEEE International Radar Conference. His reference list ([1]–[12]) does not include the 1973 paper.
- **Gandhi & Kassam:** the quoted sentence matches, [9] is Hansen 1973 at pp. 325–332, and the venue is given as "IEEE 1973 International Radar Conference, London". They also say greatest-of was "proposed and analyzed in [9, 10]", which agrees with "credit Hansen".
- **US 4,318,101:** Nippon Electric; priority 1979-03-14, filed 1980-03-11, granted 1982-03-02. The quote is accurate but leaves out the word "solely" ("Hansen solely proposed another CFAR processor…"). "Paged 1-8" is correct. The patent describes Hansen's processor as transforming Weibull clutter to an exponential variate, so "covered more than greatest-of" holds.
- **IEE contents notice:** *Proc. IEE* 120(11), p. 1391; the GREGERS HANSEN title is listed; ISBN 0 85296 114 6; 23–25 October 1973, London. All match.
- **Author profile:** papers with Zottl (1971) and Ward (1972) are listed, then nothing until 1974. Matches.
- **`GLOSSARY.md` GO/OS bullet and `cfar_scope.html` GO entry:** "greater of the two half-means" is the correct radar definition of GO-CFAR. "`maxlt` is greatest-of" is correct as a statement about the selection rule. The problem is only the "CA" qualifier in finding 1.

## Relevant files

- `<worktree>\src\bugarach\detectors\loco.py`
- `<worktree>\docs\detector_history.md`
- `<worktree>\README.md`
- `<worktree>\docs\GLOSSARY.md`
- `<worktree>\docs\learned\cfar_scope.html`
- Shelf: `<darkroom>\bugarach\lit\radar\`

Sources:
- [Analysis of some modified ordered statistic CFAR: OSGO and OSSO CFAR (ResearchGate)](https://www.researchgate.net/publication/3001792_Analysis_of_some_modified_ordered_statistic_CFAR_OSGO_and_OSSO_CFAR)
