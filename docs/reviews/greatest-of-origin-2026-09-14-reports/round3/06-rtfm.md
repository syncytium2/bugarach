GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

**Role 6 (Methods / domain expert), blind pass.** I found nothing blocking and nothing major. Every quotation and bibliographic detail I checked matches its source, and the README's description of `maxlt` matches the code. There are six minor findings.

## What I checked, against sources

- **`maxlt` in `src/bugarach/detectors/loco.py`, lines 514–518.** The code computes one threshold from the trailing half `[a − ctx/2, a]` and one from the leading half `[a, a + ctx/2]`, then keeps the larger. The README's wording ("the larger of two local thresholds, one from the trailing and one from the leading half-window") is accurate. Calling that greatest-of selection is also accurate.
- **Hansen & Sawyers 1980 (shelf PDF).**
  - Both quotations and the acknowledgment match word for word.
  - The memo's title and date (15 Feb 1972) match. Their loss curves "were prepared from [2]", and Section II says the performance of the greatest-of processor "was derived as follows [2]". That supports calling the memo a greatest-of treatment.
  - "Computed" is fair: the loss is exact for a square-law detector and a Swerling 1 target, plus Monte Carlo for other cases.
  - The DOI resolves on Crossref to the right paper: AES-16(1), 115–118.
- **Rohling 1983.**
  - Both quotations match.
  - His equation 7 defines the greatest-of statistic as the maximum of two arithmetic means, which matches `cfar_scope.html`'s "greater of the two half-means".
  - His reference list has no 1973 Hansen paper.
  - He cites Moore & Lawrence as "Presented at the IEEE International Radar Conference" (1980).
- **Gandhi & Kassam 1988.** Both quotations match. Their reference [9] gives pages 325–332 and calls the venue "IEEE 1973 International Radar Conference, London".
- **Patent 4,318,101.**
  - The "proposed another CFAR processor for the Weibull clutter in general" quotation matches (the patent's "solely" is dropped, which is fine), as do the Goldstein contrast and "paged 1-8".
  - Filed 1980-03-11, granted 1982-03-02.
  - The word "greatest" does not appear anywhere, and nothing describes a larger-of or leading/lagging split.
- **IEE contents notice.** It lists "GREGERS HANSEN, V.", Proc. IEE 120(11), p. 1391, ISBN 0 85296 114 6.
- **IEEE author profile.** Hansen & Zottl is AES-7(4), 1971; Hansen & Ward is AES-8(5), 1972.
- **Other shelf papers.** Finn & Johnson 1968 analyses clutter-edge effects but has no greatest-of rule. Weinberg 2017 cites Hansen & Sawyers only in a list.
- **Not checked:** the HathiTrust record number and its second ISBN. That is a bibliographic question, not a methods one.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verifiable against a source |
|---|---|---|---|---|---|
| 1 | `detector_history.md` §4 table, row "LoCo, `maxlt`" (source cell); `cfar_scope.html` map row; README sentence on Hansen & Sawyers | **`maxlt` is not the cell-averaging form, so the cited loss analysis is not the one for `maxlt`.** Each half's estimate in `maxlt` is a 99.9th percentile of a surrogate pool, not a mean. The scale is also not re-set for the max, whereas a greatest-of radar detector re-chooses its scale factor T for the max statistic at a fixed false-alarm rate (Rohling Table I: T_CAGO is smaller than T_CA). Hansen & Sawyers analyse mean-based halves of equal size (L/2 each); `maxlt`'s halves become unequal where they are clamped at a region boundary. In radar, greatest-of over order-statistic halves is its own named variant, OSGO-CFAR (Elias-Fusté, de Mercado & de los Reyes, IEEE T-AES AES-26(1), 1990, 197–202). The README's "in radar" and §5's "does not transfer" note limit the damage, but the table puts Hansen & Sawyers next to `maxlt` with no caveat. | minor | Keep Hansen & Sawyers, but say in the source cell that its analysis assumes cell-averaged halves. Optionally note that the order-statistic analogue is OSGO. This names an analysis, not an origin, so it stays within Tony's brief. | yes |
| 2 | `detector_history.md` §4 table, "loss analysis of the cell-averaging form" | **Ambiguous wording.** It can be read as a loss analysis of cell-averaging CFAR itself. Hansen & Sawyers compute the *extra* loss of greatest-of *over* plain cell-averaging. | minor | Change to "added loss of cell-averaging greatest-of over plain cell-averaging: Hansen & Sawyers…", matching the README. | yes |
| 3 | §4.1, patent bullet: "averages the reference cells on both sides of the cell under test" | **True but incomplete, in a way that could mislead.** The processor the patent attributes to the Hansen report works in the log domain and fits Weibull clutter. Over the ±H cells (H = 12 to 16, centre cell excluded) it averages the logarithms of the amplitudes, and a second calculator averages their squares. Together these estimate both Weibull parameters. "Averages the reference cells" suggests a plain cell-averaging detector, and a reader may conclude the 1973 paper had no greatest-of rule. | minor | Change to: "averages the logarithms of the reference-cell amplitudes, and their squares, over both sides of the cell under test (excluding it), to estimate the two Weibull parameters". Keep "does not mention greatest-of selection". | yes |
| 4 | `detector_history.md` §7 item 2: "All four primaries are read." (kept just before the new ⚠) | **Contradicts the revised §4.** §4 now says "Four of the table's papers are held and read in full" and no longer treats Hansen & Sawyers as greatest-of's primary. Leaving "all four primaries" in place says again that the primary for greatest-of was read. | minor | Change to "All four of the table's papers are read", or fold the sentence into the ⚠. | yes |
| 5 | Unchanged lines next to the change: `cfar_scope.html` line 329 and `detector_history.md` line 690–691 ("Hansen & Sawyers measured…") | **Inconsistent with the corrected README.** Hansen & Sawyers mostly calculated the loss exactly, from Sawyers' memo, and used Monte Carlo only for the extra cases. The README now correctly says "computed"; these two lines still say "measured". | minor | Change "measured" to "computed" in both places. | yes |
| 6 | §4.1, "What the sources we hold say" | **The list leaves out two shelf papers that say nothing on the question.** Finn & Johnson 1968 treats clutter edges without a greatest-of rule. Weinberg 2017 cites Hansen & Sawyers with no origin statement. Since the brief is to describe the search, showing that these were checked and are silent makes the "not established" conclusion more complete. | minor | Add one line: "Finn & Johnson 1968 and Weinberg 2017, also on the shelf, say nothing about where greatest-of began." | yes |

**Relevant files** (repo-relative): `src/bugarach/detectors/loco.py`, `docs/detector_history.md`, `README.md`, `docs/GLOSSARY.md`, `docs/learned/cfar_scope.html`; the shelf PDFs are under `<darkroom>/bugarach/lit/radar/`.

Sources:
- [Crossref record, doi:10.1109/TAES.1980.308885](https://api.crossref.org/works/10.1109/TAES.1980.308885)
- [Elias-Fusté et al., "Analysis of some modified ordered statistic CFAR: OSGO and OSSO CFAR" (ResearchGate listing)](https://www.researchgate.net/publication/3001792_Analysis_of_some_modified_ordered_statistic_CFAR_OSGO_and_OSSO_CFAR)
