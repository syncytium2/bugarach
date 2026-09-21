GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
(I also hold SubagentHandback, which only delivers this report. I hold no Edit, Write or NotebookEdit.)

# Role 2 (DOI or Die): `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`

**Summary:** The 8 references all exist, and their authors, years, titles and arXiv IDs are all correct. The trouble is in what the prose says two of them support, and in one link that is dead on this branch. I found 3 major and 5 minor issues, with no fabricated metadata. The internal references all check out: PR #596, commit 7fc052d, the files it points to, the replicate report, the glossary entries and the darkroom folders.

## Findings
Each row gives: location · issue · severity · suggested fix · verified against a source.

1. **§4 "A known failure, with a standard remedy": "Sokar et al. (2023) define such 'dormant' units by a threshold on their activity, as this page does".** · Sokar's Definition 3.1 does not match this page's rule. Sokar scores each neuron by its mean absolute activation, normalized by its layer's average, and calls it τ-dormant if that score is ≤ τ. That is a threshold on how large the activation is, relative to the layer. This page thresholds how much the output varies: a standard deviation under 0.001, absolute, and only when all 8 units of a layer meet it. A GELU unit stuck at a constant −0.17 is "silent" here but not dormant under Sokar. The page's own round-1 note says it dropped a size-based rule for exactly that reason. So "as this page does" claims a shared method that does not exist. · **major** · Suggested wording: "Sokar et al. (2023) call a unit dormant when its normalized mean absolute activation falls below a threshold; this page thresholds the variation of a layer's outputs instead, because GELU's negative dip carries signal." · verified: **yes** (arXiv 2302.12902v2, Definition 3.1, eq. 1)

2. **Summary box ("This is a known failure of training at too large a step size, and a warm-up is its standard remedy") and §4 (the same claim, with its citations).** · No cited source links warm-up to this failure. Sokar and Gulcehre are about dead or dormant units, and warm-up is not the remedy either proposes. Sokar's remedy is ReDo (recycling dormant neurons); in their §5.2 a lower learning rate helps but does not solve the problem. Gulcehre proposes no remedy. The warm-up papers (He, Goyal, Liu, Ma & Yarats) are about unstable or divergent training early on, not dead units. Stitching the two literatures together is the page's own inference, and the page's own §4 result is what supports it. · **major** · Present warm-up as the standard remedy for early instability at a large step size (He; Goyal; Liu; Ma & Yarats), and the silent-layer fix as this page's result: 6 of 7 distinct runs train. Keep "known failure" for the dead-unit observation alone. · verified: **yes** (Sokar §5.2 and the ReDo abstract; Gulcehre §7; Goyal §2.2; He §4.2)

3. **"the fair-comparison report" link (`../tuned_vs_coact/fair_comparison_2026_09_18/report.html`) and the same path in §7.** · The link is dead in the tree this page is built from. The chorus-collapse branch is based on 89f6469 (#663), and the report came to `main` later, in #665 (4fb5671). The report exists on origin/main, and there it does declare 24 configurations per net, with learning rates 0.003, 0.01 and 0.03. So the claim cited to it is correct, but a reader of this branch, or a link test run on it, finds nothing. · **major** (blocking if the page ships from this branch without rebasing onto main) · Rebase or merge `main` into chorus-collapse before landing, then rebuild. · verified: **yes** (`git ls-tree` of HEAD against origin/main)

4. **§4: "Gulcehre et al. (2022) measure more of them at larger learning rates".** · The paper does say this, but "them" is dead ReLU units: units with zero activation for every input, in the penultimate layer of offline-RL DQN and behavioural-cloning (BC) nets (§7; Figs 11 and 14; the "Observation" box). The page's own glossary says a silent layer is not the ReLU sense of "dead". The "long-standing observation" has no citation of its own. Gulcehre credits the supervised-learning origin to Glorot et al. 2011 and Gulcehre et al. 2016, "Noisy activation functions". **I stopped there:** I did not open either paper, so I have not checked that they tie dying units to the learning rate. · **minor** · Write "measure more dead ReLU units at larger learning rates in offline RL". Either cite the origin once it has been checked, or drop "long-standing". · verified: **yes** for Gulcehre (PDF §7 text quoted to scratchpad); **no** for its sources

5. **Reference list, Gulcehre et al. (2022).** · The venue is missing. The paper was published in *Transactions on Machine Learning Research* (TMLR) 2022, per dblp and the ML Anthology. Every other formally published reference in the list names its venue. · **minor** · Add "TMLR;" before the arXiv ID. · verified: **yes**

6. **§5, "The refits that collapsed": the replicate report's † is "its own flag (F1 near 0.125 with the threshold at the grid floor, or F1 undefined)".** · This paraphrases the code, not the report. The paraphrase matches the code exactly: `failed_training_signature` requires F1 within 0.01 of 0.125 at a threshold ≤ 1e-4 (`tools/tune_learned_vs_coact.py:1581` on replicate-run), or `f1_was_nan` (`seed_flags` in `tools/make_replicate_report.py`). The report's own footnote says something different: "made one call per recording or called nothing on the held-out fold". A reader who opens the report will not find the page's wording. · **minor** · Quote the report's footnote, or say "the run's failed-training signature (…), which the report words as one call per recording or no call". · verified: **yes**

7. **Summary box and §7: "PR #596 (open, not merged)".** · This is true today: state OPEN, head `eval-field-size-candidates`. It will go stale. Everything else checks out:
   - 7fc052d is one of PR #596's commits, and it is on replicate-run.
   - At that commit, `why_chorus.txt` exists and the README has "## Repairing chorus" at line 195.
   - Plain chorus was tested at lr 1e-2 and 1e-3.
   - The PR's diagnosis is "per-cell encoder starts deaf": a 1.5e-6 gradient at the encoder against 0.41 at the head. That matches "the encoder barely responded to events".
   - The row is **minor** · Write "(open as of 2026-09-19)". You could also say the commit is part of PR #596, so a reader can find it from the PR. · verified: **yes**

8. **§4, the warm-up and collapse citations (what is absent).** · The citations stop at 2021. Some relevant work is not cited:
   - Kalra & Barkeshli 2024, "Why Warmup the Learning Rate? Underlying Mechanisms and Improvements", NeurIPS 2024, arXiv:2406.09405. It studies warm-up with both SGD and Adam and would be the modern restatement.
   - The literature on training behaviour at initialization in deep, narrow networks: Hanin & Rolnick 2018, "How to Start Training: The Effect of Initialization and Architecture", NIPS 2018, arXiv:1803.01719; and Lu, Shin, Su & Karniadakis, "Dying ReLU and Initialization: Theory and Numerical Examples", arXiv:1903.06733. These bear on the page's "flat start" in an 8 × 8 head.
   - The row is **minor** and optional, with a residual ⚠ · Consider one of them. · verified: **yes** for the arXiv pages. **no** for the published version of Lu et al., which I did not check. **no** for Vaswani et al. 2017 (linear warm-up with Adam), which I did not fetch, so I give no metadata for it.

## References I checked and found correct (for the record)
- **Hendrycks & Gimpel (2016)**, arXiv:1606.08415. GELU = xΦ(x). I computed its minimum at −0.16997 (x ≈ −0.75), which supports "no lower than −0.17". The code uses exact `nn.GELU()` (`src/bugarach/learn/nets/__init__.py:94`). The paper has never had a formal venue, so listing it as arXiv only is correct.
- **Kingma & Ba (2015)**, ICLR, arXiv:1412.6980. The paper's defaults are α = 0.001, β1 = 0.9, β2 = 0.999. The trainer calls `torch.optim.Adam(..., lr=lr)` with its default betas (`train.py:228`), so "30 times the default" holds.
- **He et al. (2016)**, CVPR, arXiv:1512.03385. §4.2 warms up at 0.01 until training error falls below 80% (about 400 iterations). This is the origin of warm-up that Goyal credits.
- **Goyal et al. (2017)**, arXiv:1706.02677. §2.2 introduces gradual (linear) warm-up and credits constant warm-up to He et al. The page's linear ramp comes from this line of work. Both are correctly cited.
- **Liu et al. (2020)**, ICLR, arXiv:1908.03265. It argues that warm-up reduces the variance of Adam's adaptive learning rate early in training.
- **Ma & Yarats (2021)**, AAAI, arXiv:1910.04209. It rebuts Liu's argument, which makes "is argued" fair. Its rule of thumb is linear warm-up over 2/(1 − β2) iterations, i.e. 2,000 steps at β2 = 0.999, so "ten times" the 200-step ramp is correct.
- **Glossary, "Tuning the learned nets" section:** the entries for configuration, inner fit, refit, draw, collapse and silent layer agree with the replicate report's wording ("Each run is a draw"; Table 2's "exactly one call on every recording"). The "ReLU sense of dead" in the silent-layer entry matches Gulcehre's definition (zero activation for all inputs). F1 0.125 = 2/16 is correct.
- **Replicate report link:** it resolves, and the report's Table 2 has 146 and 153 of 432 collapsed fits, 111 of them the same fit in both draws.
- **The rest of §7:** `tools/diagnose_chorus_collapse.py` exists. The chorus nets are registered only on replicate-run, not main, which is why the tool needs `--code`. The three darkroom folders exist, and the darkroom copy of the page is byte-identical to the repository copy.
- **Figure and table captions:** none contains a citation.

## What I searched, and where I stopped
- **Searched:**
  - the warm-up and optimization literature for SGD and Adam;
  - dead, dormant and plasticity units in deep reinforcement learning;
  - dying ReLU and training behaviour at initialization;
  - the repository's own record: PR #596, the replicate-run branch, origin/main.
- **Did not search (residual ⚠):**
  - the literature on Transformer training instability and on output or attention collapse;
  - the literature on signal propagation at initialization, beyond Hanin & Rolnick.
- **Stopped one step short of the origin** of "units die at high learning rate": I did not open Glorot et al. 2011 or Gulcehre et al. 2016, and I did not check the informal course-notes source this observation is usually traced to.
- **Forward trace:** the page builds on no third-party tool beyond PyTorch, GELU and Adam, and none of these needs one.
- **Correspondence:** the page claims nothing as novel. It attributes both the failure and the remedy to the literature, so "nobody was asked" does not apply to this page. No correspondence is quoted or needed.

## Files
The page text and the fetched PDFs (Gulcehre, Sokar, He, Goyal, Adam, Ma & Yarats), with their extracted text, are in the session scratchpad under `mb2-cc/02/`.

Sources:
- [arXiv 2207.02099 (Gulcehre et al.)](https://arxiv.org/abs/2207.02099)
- [dblp: Gulcehre et al., TMLR 2022](https://dblp.dagstuhl.de/rec/journals/tmlr/GulcehreSSOFHPD22.html)
- [ML Anthology: Gulcehre et al., TMLR 2022](https://mlanthology.org/tmlr/2022/gulcehre2022tmlr-empirical/)
- [arXiv 2302.12902 (Sokar et al.)](https://arxiv.org/abs/2302.12902)
- [arXiv 1606.08415 (Hendrycks & Gimpel)](https://arxiv.org/abs/1606.08415)
- [arXiv 1412.6980 (Kingma & Ba)](https://arxiv.org/abs/1412.6980)
- [arXiv 1512.03385 (He et al.)](https://arxiv.org/abs/1512.03385)
- [arXiv 1706.02677 (Goyal et al.)](https://arxiv.org/abs/1706.02677)
- [arXiv 1908.03265 (Liu et al.)](https://arxiv.org/abs/1908.03265)
- [arXiv 1910.04209 (Ma & Yarats)](https://arxiv.org/abs/1910.04209)
- [arXiv 2406.09405 (Kalra & Barkeshli)](https://arxiv.org/abs/2406.09405)
- [NeurIPS 2024 proceedings: Kalra & Barkeshli](https://proceedings.neurips.cc/paper_files/paper/2024/file/ca98452d4e9ecbc18c40da2aa0da8b98-Paper-Conference.pdf)
- [arXiv 1803.01719 (Hanin & Rolnick)](https://arxiv.org/abs/1803.01719)
- [arXiv 1903.06733 (Lu et al.)](https://arxiv.org/abs/1903.06733)
