GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

**Grounding.** I read these in full as text, from the shelf at `<darkroom>/bugarach/lit/radar/`:
- Hansen & Sawyers 1980
- Rohling 1983 (the attribution passages on pp. 609 and 613, and the reference list)
- Gandhi & Kassam 1988 (§I, §III.B and the reference list)
- the IEE Conf. Publ. 105 contents listing
- the IEEE Xplore profile page for Hansen

I also read the `maxlt` code in `src/bugarach/detectors/loco.py:501–518` in the worktree.

**Answers to the four questions:**
- **(a) Definition: correct.** Greatest-of takes the larger of the leading and lagging reference-window estimates. That matches Rohling eq. (7), Gandhi & Kassam eq. (22) and the 1980 paper's Fig. 1 and eq. (3). Eq. (3), F_z = F_y², is the distribution of the larger of two independent half-window sums.
- **(b) Is "Split" the same as greatest-of? Yes, but only on the 1980 paper's word.** The paper says of the greatest-of processor in its Fig. 1: *"The detection performance of this processor was derived as follows [2]"*, where [2] is the memo. Its curves were *"prepared from [2]"*, and it compares [2]'s exact loss with the loss from the 1973 rule, which only makes sense if both describe the same processor. The memo's author is a co-author of the 1980 paper. The memo's title alone would not settle it: a split window can also be combined by taking the smaller estimate, or by testing each half separately.
- **(c) Terms: correct.** "Cell averaging LOG/CFAR receiver" is the exact title of Hansen & Ward 1972 (AES-8(5), pp. 648–652; 1980 ref. [4] and the Xplore profile). The Hansen & Zottl 1971 description matches its title ("The Detection Performance of the Siebert and Dicke-Fix CFAR Radar Detectors", AES-7(4)).
- **(d) "Derives greatest-of's detection performance from" the memo: accurate, but wider than the source.** Details in finding 3.

---

### Findings

**1. The Rohling 1983 bullet** (detector_history §4, "What the papers we hold say")
- **Issue:** It says Rohling "credits greatest-of to the 1980 paper and to Moore & Lawrence 1980". Rohling actually gives them different roles. p. 613: *"Moore et al. [3] proposed a different estimation method. The CAGO CFAR applies the maximum of two arithmetic means…"*, and separately *"Hansen et al. [2] have investigated CAGO CFAR"*. So Rohling names a third proposer, in 1980. That is impossible given the 1972 memo and the 1973 paper, and it bears directly on the passage's origin question. The current wording hides who "proposed" and who "investigated".
- **Severity:** major
- **Fix:** "Rohling 1983 says Moore & Lawrence 1980 *'proposed'* greatest-of and that Hansen & Sawyers 1980 *'investigated'* its losses. He cites neither the 1973 paper nor the memo."
- **Verifiable:** yes (Rohling pp. 609, 613)

**2. The Gandhi & Kassam 1988 bullet** (same list)
- **Issue:** The quote stops before the clause that ties Hansen [9] to greatest-of: *"in this procedure the noise power is estimated by the greatest of (GO) the sums in the leading and lagging windows"*. §III.B is also more explicit than anything quoted: *"A modified detection scheme proposed and analyzed in [9, 10], known as the 'greatest of' (GO) CFAR"*. As written, a reader cannot tell that this bullet is the source of "usually credited". Separately, their reference for [9] names the venue *"Proceedings of the IEEE 1973 International Radar Conference, London"*, not IEE Conf. Publ. 105. So the one source for pages 325–332 also gets the venue wrong.
- **Severity:** minor
- **Fix:** Extend the quote through "leading and lagging windows", add the "proposed and analyzed in [9, 10]" sentence, and note the venue mismatch next to the page range.
- **Verifiable:** yes (Gandhi & Kassam pp. 428, 431, 444)

**3. The memo bullet: "The same paragraph cites an earlier analysis … The 1980 paper derives greatest-of's detection performance from it"**
- **Issue, part 1:** "Same paragraph" is wrong. §I paragraph 1 cites only [1], the 1973 paper. The memo, [2], is cited in paragraph 2: *"the loss calculated from [1] is somewhat larger than predicted from an exact analysis contained in [2]"*.
- **Issue, part 2:** "Derives greatest-of's detection performance" is wider than the source. The paper credits [2] only with the exact analysis for a square-law detector and a Swerling case 1 target. Its results for a non-fluctuating target and for envelope and log detectors are its own Monte Carlo simulations.
- **Severity:** minor
- **Fix:** "The next paragraph cites … The 1980 paper takes its exact greatest-of analysis (square-law detector, Swerling case 1 target) from it. Its other results are its own simulations."
- **Verifiable:** yes

**4. "What we do not know: what the 1972 memo contains"** (detector_history §4)
- **Issue:** This conflicts with the bullet above it, which says the 1980 paper derives greatest-of's performance from the memo. We do know part of what the memo contains: an exact loss analysis of the "Split" detector, which the 1980 paper treats as greatest-of. The 1973 bullet is already hedged ("beyond its author's one-sentence description"); this one needs the same hedge.
- **Severity:** minor
- **Fix:** "what the 1972 memo contains beyond the exact greatest-of analysis the 1980 paper takes from it, and whether its 'Split' detector covered any other way of combining the two halves."
- **Verifiable:** yes

**5. README: "a 1972 internal memo cited in the 1980 paper already analysed the same split detector"**
- **Issue:** "The same split detector" has nothing to refer back to: the README never uses the word "split" before this. It also states the match with greatest-of as settled fact, when we only have it through the 1980 paper's citation (see (b)). An outside reader with a radar background will stop at "same".
- **Severity:** major
- **Fix:** "…and a 1972 internal Hughes memo by Sawyers, which the 1980 paper cites as the source of its exact greatest-of analysis, predates the 1973 paper."
- **Verifiable:** yes

**6. README: "LoCo's `maxlt` is greatest-of CFAR. Its detectability cost is measured in Hansen & Sawyers (1980)"**
- **Issue:** Grammatically "Its" refers to `maxlt`, so the sentence says LoCo's cost was measured. The 1980 figure (0.1–0.3 dB of signal-to-noise loss, square-law detector, Swerling case 1 target) is greatest-of's cost in radar. The shelf README's own ⚠ says *"The magnitude does not transfer."* This wording predates the change but sits inside the rewritten bullet.
- **Severity:** major
- **Fix:** "Greatest-of's detectability cost in radar is measured in…"
- **Verifiable:** yes (the 1980 paper's §IV; shelf README)

**7. What the 1980 paper says about origin is left out** (detector_history §4)
- **Issue:** The Acknowledgment says: *"The results reported in this paper are derived from independent work performed by the two authors"*. David Shanks is thanked for telling each author about the other's work. So Hansen at Raytheon and Sawyers at Hughes worked on it independently. That bears directly on the open question "introduced greatest-of, or analysed a technique already in use". Relatedly, "it was not published" rests on "internal memo" plus the conclusion's *"previously unpublished results"*, which describes the position as of 1980.
- **Severity:** minor
- **Fix:** Add a bullet quoting the Acknowledgment, and write "unpublished as of 1980, per the paper".
- **Verifiable:** yes

**8. "beyond its author's one-sentence description"** (What we do not know)
- **Issue:** The 1980 paper says more than one sentence about the 1973 paper. It adds *"This rule is based on a simplified analysis and simulation results of limited accuracy"*, and says its loss came out larger than the exact analysis. So we know the 1973 paper held a simplified analysis plus simulation, and that it overstated the loss.
- **Severity:** minor
- **Fix:** Add both facts to the first bullet and drop "one-sentence".
- **Verifiable:** yes

**9. Table row "LoCo, `maxlt`", analogue column "greatest-of (CAGO-CFAR)"; README "is greatest-of CFAR"**
- **Issue:** CAGO means cell-averaging greatest-of, which names the cell-averaging estimator. The `maxlt` paragraph says LoCo matches only the **combination rule**, and its estimator is a surrogate-pool percentile, not a mean. The table cell and the README claim more than the paragraph does. This text predates the change, but the row was edited.
- **Severity:** minor
- **Fix:** "greatest-of (GO) selection". In the README: "uses greatest-of selection".
- **Verifiable:** yes (Rohling eq. 7; loco.py)

**10. The "`maxlt` is greatest-of selection" paragraph: consistency with the method**
- **Issue:** The paragraph is consistent with the new passage and correct about clutter edges; Gandhi & Kassam's *"clutter transition"* supports it. It misses one invariant. In greatest-of CFAR, the scaling factor T is re-solved for the max statistic so the design false-alarm rate holds (the 1980 paper solves eq. (7) for T; Rohling's Table I gives separate values for CA and CAGO). `loco.py:514–518` takes the max of two per-half thresholds, each already set at the nominal percentile, and does not recalibrate. So the combined bar's null exceedance rate is below the nominal percentile. "The rule is the same; the thing being combined is not" is true, but the constant-false-alarm calibration does not carry over either. This is outside the diff.
- **Severity:** minor
- **Fix:** Add one sentence saying the max is taken after thresholding, with no recalibration, so the nominal percentile is conservative and is not the false-alarm rate.
- **Verifiable:** yes (code plus the two papers)

---

**Checked with no finding:**
- The inline ⚠ flag at detector_history.md:204.
- The GLOSSARY CFAR paragraph's description of the method.
- The contents listing matches the stated author, title, venue and dates (23–25 October 1973), and gives no page numbers.
- "Twenty months" from 15 Feb 1972 to 23 Oct 1973 is correct.
- Neither Hansen & Zottl 1971 nor Hansen & Ward 1972 is on the shelf.

**Not verified:** "IEEE Xplore does not index this IEE volume". A web search could neither confirm nor refute it.

Files:
- <worktree>\docs\detector_history.md
- <worktree>\README.md
- <worktree>\docs\GLOSSARY.md
- <worktree>\src\bugarach\detectors\loco.py
- <darkroom>\bugarach\lit\radar\hansen_sawyers_1980_go_cfar_loss.pdf
- <darkroom>\bugarach\lit\radar\rohling_1983_os_cfar.pdf
- <darkroom>\bugarach\lit\radar\gandhi_kassam_1988_cfar_nonhomogeneous.pdf

Sources (web; nothing load-bearing rests on them):
- [Semantic Scholar entry for Hansen 1973](https://www.semanticscholar.org/paper/Constant-false-alarm-rate-processing-in-search-Hansen/b9f381e35d0cc467d022f6661a4b477f0ba78d8f)
- [IET Digital Library, adaptive censored greatest-of CFAR](https://digital-library.theiet.org/doi/10.1049/ip-f-2.1992.0032)
