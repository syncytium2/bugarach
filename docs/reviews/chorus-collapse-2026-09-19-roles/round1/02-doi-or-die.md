GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
(The harness also gave me SubagentHandback, which is only the delivery channel. I hold no Edit, Write or NotebookEdit.)

# Role 2, DOI or Die: round 1 on `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`

## Summary
- **The internal references check out.** The numbers and paths resolve, but the page states two things about PR #596 more strongly than its sources do.
- **The main gap is on the external side.** The mechanism is a known one: units go inactive under a large early learning rate, and warm-up is the standard remedy. The page presents it without saying so, and it never names the optimizer.
- **Nothing is fabricated.** The page cites no external work at all, so the external findings are about what is missing, not about wrong metadata.

## Findings
Each row gives: location · issue · severity · suggested fix · verified against a source.

1. **Whole page: §0 "The answer", §4, §5 "Three follow from the evidence".**
   - **Issue:** The mechanism is presented as this project's own diagnosis, with no word that it is a known failure class and a textbook remedy. The failure class is units going permanently inactive early in training at a large learning rate, leaving the net's output constant. The remedy is learning-rate warm-up. §5 lists warm-up as a repair that "follow[s] from the evidence". A deep-learning reader on a public portfolio page will read that as not knowing the literature.
   - **Severity:** major.
   - **Fix:** Add one sentence in §0 or §4, e.g. "This is a known failure of training at too large an early learning rate, and warm-up is its standard remedy", then cite:
     - Inactive units: CS231n notes (Karpathy; the widely quoted "as much as 40% of your network can be 'dead' … if the learning rate is set too high"). Maas, Hannun & Ng 2013 for the mechanism: a unit that never activates gets no gradient.
     - A measurement that larger learning rates give more dead units: Gulcehre et al. 2022, arXiv:2207.02099, §/Fig. 11–13.
     - Warm-up: He et al. 2016 (CVPR, arXiv:1512.03385), a constant warm-up that is the origin credited by Goyal et al. Goyal et al. 2017 (arXiv:1706.02677, arXiv only), the gradual/linear ramp.
     - Why warm-up helps Adam: Liu et al., ICLR 2020 (arXiv:1908.03265). Ma & Yarats, AAAI 2021 (arXiv:1910.04209), which disputes Liu's variance explanation. Cite both; do not cite Liu alone.
   - **Verified:** yes. I checked each work's text for the quoted claim, except Maas's venue (see row 14).

2. **§3, where the architecture is described; the optimizer is never named anywhere on the page.**
   - **Issue:** The training uses Adam: `torch.optim.Adam(model.parameters(), lr=lr)` with default betas in `src/bugarach/learn/train.py` on replicate-run. The page gives learning rates of 0.003, 0.01 and 0.03 without saying they are Adam step sizes.
     - 0.03 is 30× the α = 0.001 that Kingma & Ba give as the "good default setting".
     - The warm-up remedy's rationale in rows 1 and 13 is specific to Adam.
     - Without the optimizer, the numbers do not carry to another setup, and the reader cannot connect the page to the literature.
   - **Severity:** major.
   - **Fix:** In §3 say "trained with Adam (Kingma & Ba, ICLR 2015, arXiv:1412.6980) at its default β1 0.9 and β2 0.999", and note that lr 0.03 is 30× that paper's default step size.
   - **Verified:** yes (train.py on origin/replicate-run; Kingma & Ba PDF, Algorithm 1).

3. **Candidate citation: Lu et al., "Dying ReLU".**
   - **Issue:** This paper is **not** the source for death caused by the learning rate. Lu, Shin, Su & Karniadakis, "Dying ReLU and Initialization: Theory and Numerical Examples", Commun. Comput. Phys. 28(5):1671–1706 (2020), doi:10.4208/cicp.OA-2020-0165, arXiv:1903.06733:
     - It proves that deep, narrow ReLU nets are "born dead" at a symmetric initialization as depth grows.
     - Its abstract does not mention the learning rate.
     - It credits dying ReLU to Agarap 2018 and Trottier et al. 2017, which are not origins.
     - Its nets are ReLU, and this page's are GELU.
     - It is relevant to one real feature of this page: an 8-layer × 8-unit head, both fits starting with an almost constant output, and the net collapsing to a constant function.
   - **Severity:** minor.
   - **Fix:** If it is cited, cite it only for "deep narrow nets collapse to a constant function", and give the CiCP reference, not "2019". Do not cite it for the learning-rate mechanism.
   - **Verified:** yes (full text read; journal page checked).

4. **§3, "Call a head layer dead…".**
   - **Issue:** "Dead" is borrowed from ReLU, but a GELU unit is not dead in that strict sense. Its gradient Φ(x) + xφ(x) is non-zero for negative input and only decays toward 0. The page's definition is a threshold, which is fine, but a reader who knows "dying ReLU" will read it as exact zero gradient. The closest published operational definition is τ-dormant: a normalized mean activation ≤ τ (Sokar, Agarwal, Castro & Evci, ICML 2023, arXiv:2302.12902, Def. 3.1).
   - **Severity:** minor.
   - **Fix:** Add a clause such as: "with GELU this means near-zero output and near-zero gradient, not exactly zero (compare 'dormant' units, Sokar et al. 2023)".
   - **Verified:** yes.

5. **§3, the GELU gloss.**
   - **Issue:** The gloss "passes positive input and squeezes negative input to small values near zero" is consistent with GELU(x) = xΦ(x), and the "small negative residue" is correct. There is no citation.
   - **Severity:** minor (optional).
   - **Fix:** Cite Hendrycks & Gimpel, "Gaussian Error Linear Units (GELUs)", arXiv:1606.08415 (2016; arXiv only, v5 2023).
   - **Verified:** yes.

6. **§0, "This is not the failure PR #596 fixed"; also §7.**
   - **Issue:** PR #596 ("Every learned model against CoactDetect; gauge and chorus evaluated, chorus repaired") is **OPEN, not merged**. Its head branch is eval-field-size-candidates. Neither `why_chorus.txt` nor the chorus nets exist on origin/main. "Fixed" reads as landed.
   - **Severity:** minor.
   - **Fix:** Write "the failure diagnosed and repaired in PR #596 (open, not merged; the work is on branch replicate-run)".
   - **Verified:** yes (`gh pr view 596`; `git cat-file` on origin/main).

7. **§0, "plain chorus's per-cell encoder starting deaf at every learning rate".**
   - **Issue:** The sources tested two learning rates, 0.01 and 0.001. `why_chorus.txt` runs chorus at both, and the field-size README says "It is not the learning rate: at 1e-3 the loss curve is the same to two decimals". Neither tried 0.03, the rate this page is about. "Every" stretches a two-rate result, and the stretch matters: this page's contrast is that the first failure did not depend on the learning rate and this one does.
   - **Severity:** minor.
   - **Fix:** Write "…starting deaf, which neither learning rate tried (0.01, 0.001) overcame".
   - **Verified:** yes.

8. **§0, "chorus_norm's standardization repaired it".**
   - **Issue:** The claim is correct, but the file §7 cites (`why_chorus.txt`) says nothing about the repair. The support is in `docs/learned/field_size_candidates/README.md`, section "Repairing chorus". There, chorus_norm's vote moves 0.22–0.51 for one onset at initialization against 0.0002–0.0003 for chorus, and it trains to F1 0.741. The PR body's "Since opening" paragraph also covers it.
   - **Severity:** minor.
   - **Fix:** Cite the README section (branch replicate-run) beside `why_chorus.txt` in §7.
   - **Verified:** yes.

9. **§7, "why_chorus.txt (branch replicate-run)".**
   - **Issue:** The file exists on origin/replicate-run (7a95e8a when I checked) and on origin/eval-field-size-candidates. Its own header says it was written on the latter. A branch name is a moving, deletable pointer, and this is a public page.
   - **Severity:** minor.
   - **Fix:** Pin a commit hash, or cite it as PR #596's head.
   - **Verified:** yes.

10. **Throughout (about 7 uses): "goal 2".**
    - **Issue:** The page never names goal 2 or links to it. It resolves to `docs/goals/learned-model-family.md`, "A fair comparison of the coded detectors against the nets", but only through `docs/goals/README.md`.
    - **Severity:** minor.
    - **Fix:** Name it and link it at first use.
    - **Verified:** yes.

11. **§5, "tuned over a smaller grid than the one declared".**
    - **Issue:** There is no pointer to where the grid was declared. It is in `docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/report.html` (lr 0.003, 0.01, 0.03) on main.
    - **Severity:** minor.
    - **Fix:** Cite that report.
    - **Verified:** yes.

12. **§7, the darkroom run folders.**
    - **Issue:** `2026-09-18-fair-comparison-run` and `2026-09-18-replicate-run-status` are given without the `<darkroom>/bugarach/` prefix that the page's own folder carries. Both exist and both hold `results/`.
    - **Severity:** minor.
    - **Fix:** Add the prefix.
    - **Verified:** yes.

13. **§4 and §5, "ramped up over the first 200 steps" and "warm-up".**
    - **Issue:** The shape of the ramp is not stated. The code is linear: `lr = base_lr * min(1, (step+1)/warmup)` at `tools/diagnose_chorus_collapse.py` lines 237–239. That is Goyal et al.'s gradual warm-up, the form Ma & Yarats recommend. Their rule of thumb is 2/(1−β2), which is 2,000 steps at Adam's default β2. That is relevant context for "200 rescued 7 of 8, 50 did not".
    - **Severity:** minor.
    - **Fix:** Write "linear warm-up". Optionally cite the rule of thumb.
    - **Verified:** yes.

14. **Maas et al. 2013 (if the page cites it).**
    - **Issue:** The paper exists: I read the PDF on the author's Stanford page, and it contains the "never activates … will not adjust the weights" passage. I did **not** verify its venue from the document. It is usually cited as an ICML 2013 workshop paper, and Lu et al. cite it as "ICML vol. 30, p. 3".
    - **Severity:** minor.
    - **Fix:** Confirm the venue before printing it.
    - **Verified:** partly (content yes, venue no).

## Checked and clean
- **Replicate report** (`docs/learned/tuned_vs_coact/replicate1/report.html`, on main). It matches everything the page attributes to it:
  - 146 and 153 of 432 fits, and 111 fits the same in both draws (its Table 2).
  - "one of the 15 planted events, so F1 is exactly 0.125", and 1-of-15 arithmetic gives F1 0.125.
  - † means "made one call per recording or called nothing". It sits on chorus_norm in the second draw and on chorus_gain_norm in both draws, consistent with the page's 4 refits.
- **The page's own files.**
  - `collapse_table.json`, `census.json` and `replays/` (14 files) exist.
  - `tools/diagnose_chorus_collapse.py` exists and takes `--code`.
  - The rebuild test (`tests/test_diagnose_chorus_collapse.py`) exists.
  - The chorus-collapse branch is pushed.
  - The chorus nets are registered only on origin/replicate-run, which matches §7.
- **Architecture as described.** The head is 8 Conv1d+GELU layers of width 8 (`_dilated_stack`), and chorus_norm standardizes the encoder output over time (`norm=True`).

## Where the trace stopped
- **Dead units and the learning rate.** Backward: CS231n (course notes, no source given for the 40% figure) and Maas 2013 (a mechanism, not the learning rate). Douglas & Yu 2018 (arXiv:1812.05981) say "Little is understood about this condition". I found **no peer-reviewed origin** for "a large learning rate kills units" earlier than those course notes. Gulcehre 2022 is a later measurement, not the root.
- **Warm-up.** Backward: Goyal 2017 credits constant warm-up to He 2016 (reference [16]). He's text says 0.01 "to warm up the training until the training error is below 80% (about 400 iterations)". I stopped at He 2016. Forward:
  - Liu 2020 (variance explanation).
  - Ma & Yarats 2021 (refutes it; the size of the update is what matters).
  - Kalra & Barkeshli, NeurIPS 2024 (arXiv:2406.09405; warm-up moves training to better-conditioned regions).
  - Vaswani et al. 2017: I saw it only as a citation inside Liu et al. **Not fetched.**
- **Literatures searched:** deep-learning optimization (arXiv) and deep reinforcement learning (dormant neurons, rank collapse).
  - **Not searched, residual ⚠:** pre-2012 neural-network practice (e.g. LeCun et al., "Efficient BackProp", on step size and saturated units), and the learning-rate stability literature (edge-of-stability, loss curvature: Cohen et al. 2021, Gilmer et al. 2022).
- **Correspondence: nobody was asked, residual ⚠.** The page claims no novelty, so this is low-stakes. Still, ask Tony whether anyone has discussed the lr-0.03 grid point, or warm-up, with the authors of the net-design proposal or with a reviewer.

## Files
- Artifact: `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`
- Internal sources:
  - `<worktrees>/weekend-runs/docs/learned/field_size_candidates/why_chorus.txt` and `README.md` (branch replicate-run)
  - `<worktrees>/chorus-collapse/docs/learned/tuned_vs_coact/replicate1/report.html`
  - `<worktrees>/chorus-collapse/tools/diagnose_chorus_collapse.py`
- Intermediates (paper PDFs and extracted text): `<scratchpad>/mb-cc/02/`

Sources:
- [Hendrycks & Gimpel, GELUs](https://arxiv.org/abs/1606.08415)
- [Goyal et al. 2017](https://arxiv.org/abs/1706.02677)
- [He et al. 2016](https://arxiv.org/abs/1512.03385)
- [Liu et al., RAdam](https://arxiv.org/abs/1908.03265)
- [Ma & Yarats](https://arxiv.org/abs/1910.04209)
- [Kalra & Barkeshli](https://arxiv.org/abs/2406.09405)
- [Kingma & Ba, Adam](https://arxiv.org/abs/1412.6980)
- [Lu et al., Dying ReLU (arXiv)](https://arxiv.org/abs/1903.06733) and [journal page](https://www.global-sci.com/cicp/article/view/6894)
- [Maas et al. 2013](https://ai.stanford.edu/~amaas/papers/relu_hybrid_icml2013_final.pdf)
- [CS231n notes](https://cs231n.github.io/neural-networks-1/)
- [Gulcehre et al. 2022](https://arxiv.org/abs/2207.02099)
- [Sokar et al. 2023](https://arxiv.org/abs/2302.12902)
- [Douglas & Yu 2018](https://arxiv.org/pdf/1812.05981)
