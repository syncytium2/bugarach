GRANT 4 ok — Read, Grep, Glob, Bash

Role 4, Reviewer 2 (adversarial). I found 18 problems: 1 blocking, 9 major, 8 minor. I edited nothing and ran no simulations; the figures were checked against numbers.json and the generator's code. I opened all six PNGs.

**What I checked:**
- `README.md` in full.
- All six figure PNGs, plus `numbers.json`.
- `explain_coordination_share.py`: how the recordings are built (`recording`, `schedule`), `run_set`, `in_run`, `own`, `recovered`, `figure5`, `figure6`, `main`.
- `tools/measure_coordination_rates.py`: module docstring, constants, `shifted`, `solve`, `pooled_ratio`, `per_recording`, `summarize`, `truth`, `_sim`, `calibrate`, `group_stats`, the calibration loop in `main`, `CAL_NO_PROBE`.
- `src/bugarach/bench.py`: `REGIMES`, the elevated-rate recording, decoys, the spacing block, `realistic_counts`.
- `src/bugarach/simulate.py`: decoys.
- `docs/learned/runs/2026-09-25-real-intervals/`: which dataset it was measured on.
- FOUNDATIONS §9 and §11.

## Findings (location · issue · severity · suggested fix · verified)

**1. The readouts that will be reported are understated** · README l.39–41 and l.137–138
- Issue: FOUNDATIONS §11 (confirmed 2026-10-14) names three treatment readouts: the share of events, the rate of shared moments, and the share of the field per moment, each per stream and per group. The page says only "the share of calcium events that are coordinated, beside the overall event rate". It then says participants per moment (*k*) and moments per minute (λ) "are not checked", while its own Figure 4 shows them reading 26–69% high and 34–55% low. They also move when moments come closer together, with no change in coordination. So two of the three reported quantities will reach readers of treatment results without a warning on the page that explains them.
- Severity: **blocking**.
- Fix: name all three readouts as §11 does. Say plainly that λ and *k* are biased by more than any plausible effect and are not validated. Either advise against reading them as treatment effects or show that they work.
- Verified: yes.

**2. No simulated treatment comparison** · whole page; l.248–249
- Issue: the page exists to read paired baseline/treatment results, but every figure tests recovery within one condition. No figure plants a known change and shows the paired ratio recovering it. Examples: the share doubled with moment sizes held; the same share with sizes changed; a rising field rate. Nothing translates the per-recording spread (Fig 6: 0.59–0.98 with 6 moments) into the smallest paired change that could be seen. Can the alarm ring? Not shown.
- Separately, `per_recording` pools f3/f2 over the whole set. If a baseline and its treatment window are pooled, *k* is identical in both by construction, so the "share of the field per moment" readout cannot register any treatment effect. l.249 calls the pooling choice "open"; it should say this readout is structurally null under pooling.
- Severity: **major**.
- Fix: add a figure with planted paired changes. State the construction issue with pooled *k*.
- Verified: yes (pooling in code; absence of a paired test).

**3. Only the fast stream is validated** · l.68–71; whole page
- Issue: the tool reports fast, slow and combined (`BENCHES`, `CAL_JITTER` slow = 0.135 s), and §11 requires per-stream results. Every figure copies the fast stream (jitter 0.106 s), and the page never says slow and combined are untested. The tool's own `CAL_NO_PROBE` warns that on slow "the share at the probe is 35.9%, it is not obviously small". That is the "What else it counts" problem at its worst, and the page omits it.
- Severity: **major**.
- Fix: state that the figures cover the fast stream only. Carry the slow-stream warning into "What else it counts", or add slow-stream figures.
- Verified: yes.

**4. "One input comes from real recordings" is false** · l.48–50
- Issue: at least four other inputs were measured on the same contaminated default data set (senktide_ttx):
  - the quiet and busy backgrounds 0.0049/0.0169 (FOUNDATIONS §9; the 2026-09-23 coordination-rates run);
  - the 0.106 s jitter (the 2026-09-23 jitter-correlogram run, `bench.py` l.1065–1071);
  - the elevated-rate level of 0.1334 Hz (`bench.py` l.1573);
  - the generator's per-cell rate spread and clumping.

  Cells pinned by motion correction, with events at the same moments, plausibly narrow the measured jitter and bias the backgrounds. Separately, the quiet and busy figures are background rates with this tool's own fixed-model share subtracted. So the bench that checks the tool was partly built by the tool: that is a consistency check, not an independent one.
- CLAUDE.md says "a known contamination stops the work. It does not become a caveat."
- Severity: **major**.
- Fix: list every input taken from real recordings, with its source run and the likely direction of the contamination's effect. The main thread should decide whether the page may ship under the stop.
- Verified: yes.

**5. Figure 3 pools quiet and busy without marking them** · Fig 3 and l.134, l.154
- Issue: each panel holds 24 quiet plus 24 busy recordings, unmarked. The tool's check pools them the same way (`main`, `jobs` over both regimes, one median). In the picture, the low-planted-share cluster (about 5–10%, which by inference is busy) holds the widest spread and every low value (fixed model 0.67–0.72). The 15–28% cluster sits tightly at about 0.78–0.88. A pooled median can pass while one background is materially worse.
- Severity: **major**.
- Fix: mark quiet and busy, give a median for each, and say the tool's check pools them.
- Verified: partly. The pooling is in the code; which cluster is busy is my inference from planted share and was not computed.

**6. Every nothing-planted test is at the quiet background only** · Fig 5 and l.197–228
- Issue: `nulls`, `durations`, `amplitudes` and the planted run they are pooled with are all built with `bgs=(QUIET,)` (generator l.632–645). The Fig 5 caption and the claim "with no stretch, a recording reports close to zero" (l.224) never say quiet. The busy background with nothing planted, and busy plus a stretch, are untested.
- Severity: **major**.
- Fix: scope the caption and text to quiet, or add busy.
- Verified: yes.

**7. Unexplained constants in Figure 5** · l.204–205, Fig 5A axis, Fig 5C
- Issue: the page never says that +0.1334 onsets/s is the 99th percentile of real 300 s baseline stretches, close to the worst case. So the headline "8.2% for 1 minute" describes a rare extreme, and the reader cannot judge the typical size. "13× quiet" (3.8× busy, beyond the real interquartile range) and "rising 3× over 45 min" are unexplained.
- Severity: **major**.
- Fix: state the percentile; justify 13× and 3×.
- Verified: yes.

**8. Figure 6 assigns causes its own caveat forbids** · l.236–237 against l.250–251
- Issue: the page says the groups are "descriptions, not separated causes", then says "a lower event rate *alone* did not add spread … a busier background did". The ¼-quiet group raises the planted share to 50% and busy lowers it to 7%. Spread tracks planted share: the groups at 5–8% (3 and 6 moments, busy) are wide and those at 20% and 50% are narrow. The picture supports planted share as the driver at least as well as background.
- Severity: **major**.
- Fix: drop "alone". Restate as: the groups with a low planted share spread widest, however it was lowered.
- Verified: yes (numbers.json, `planted_share_median`).

**9. Unsupported claim that pooling "steadies the median"** · l.121–122
- Issue: Figure 6 shows one set per group, and steadiness of a median needs repeated sets. The medians shown (own/pooled: 0.83/0.82, 0.83/0.79, 0.87/0.83, 0.81/0.81, 0.81/0.81) are no evidence either way.
- Severity: **major**.
- Fix: remove the claim or show repeated runs.
- Verified: yes.

**10. The realistic case is described, not simulated** · l.243–245; Figs 3, 4, 6
- Issue: the page says real fast recordings hold about 7 moments per 45 minutes, and baseline windows can be 15 minutes long (about 2–3 moments; `MIN_BASELINE_SEC` = 900, 9.7 per hour). Figure 6's few-moment groups are quiet-only and 45 minutes long. Figures 3A/B and 4 use 15 moments, about twice the realistic count and the narrowest case. The likely real case (few moments, short window, busy) is never shown.
- Also, "Real recordings are nearer the narrow end of moments" reads as "narrow spread", the opposite of the intended meaning.
- Severity: **major**.
- Fix: simulate 15-minute windows with 2–3 moments at both backgrounds, or say plainly that this is untested. Reword the sentence.
- Verified: yes.

**11. Size variation does not explain the 5% in the one-size set** · l.160–161
- Issue: "From size variation alone it reads 5% low (one size)" cannot hold, because one size has no size variation. Figures 3A and 3B also both use the mixed schedule (`recording()` defaults to `mixed=True`; 3B only sets `size=6`), which includes close pairs.
- Severity: minor.
- Fix: "with one size it reads 5% low (window edges and close pairs); with three sizes, 18% low, so size variation adds about 13 points."
- Verified: yes.

**12. Counts are given as "some"** · l.154–155
- Issue: "some fall outside the band" should be a count per panel. By eye, about 7 of 48 fixed-model points in Fig 3A fall below 0.75.
- Severity: minor.
- Fix: give the counts.
- Verified: no (counted by eye).

**13. The title overclaims** · title
- Issue: "counted without defining a coordinated event", yet l.33 concedes an implicit definition: several cells within 1 s, beyond what ±32 s slides give, including any shared rate change shorter than about a minute.
- Severity: minor.
- Fix: "…without deciding which onsets form an event".
- Verified: yes.

**14. Figure 2's equal mean is guaranteed, not observed** · Fig 2 title, l.85–86
- Issue: the circular shift keeps every count (`shifted` wraps around), so the shifted copy must have the same mean. The page presents it as an observation.
- Severity: minor.
- Fix: say "by construction".
- Verified: yes.

**15. Figure 5C hides an over-subtraction and gives no share for what is left** · l.218–223
- Issue: at the quiet background, subtraction removes 257% of what the rise added (it adds 0.0008, leaves −0.0013), but the text says it "barely registers". At 13× quiet, the residual after subtraction (f₂ 0.0024–0.0059) is never turned into a share. So "removes 98–99%" does not tell the reader what error remains.
- Severity: minor.
- Fix: state the over-subtraction, and give the residual as a share.
- Verified: yes.

**16. Figure titles name quantities, not findings** · Fig 3 and Fig 4 titles
- Issue: "Recovered against planted" and "Window size and the intervals between moments" say what is plotted, not what it shows.
- Severity: minor.
- Fix: e.g. "Figure 3. The share reads 2–18% low, inside the ±25% band; the model decides how much."
- Verified: yes.

**17. The novelty claim is too strong for a public repo** · l.291–295
- Issue: the page lists a "two-number shortcut" among what is this project's, while also flagging (⚠) that the literature search was shallow. Closing a fixed-size compound Poisson model from second- and third-order factorial cumulants is a standard method of moments.
- Severity: minor.
- Fix: say "this project's use of…", or drop the novelty claim.
- Verified: no.

**18. The check cannot inform the model choice** · l.134–138, l.166–170
- Issue: all six model-by-set medians pass ±25% (numbers.json, fig3). So the check has no power over the decision that moves the answer by about 10 points.
- Severity: minor.
- Fix: say that explicitly beside "the choice is not settled by accuracy".
- Verified: yes.

**What the pictures show beyond the captions:**
- Figure 3: the quiet/busy split described in finding 5.
- Figures 1, 2, 4 and 6: each matches its text and numbers.json (Fig 1C bars 4 and 6 at 30m25s, the 10-bar at 32m32s; Fig 2B excesses of 0.20 and 1.21; the Fig 4 ranges; the Fig 6 percentiles).
- Figure 5: the B and C values match numbers.json.

**Files:**
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\explain_coordination_share.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\numbers.json
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\tools\measure_coordination_rates.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\src\bugarach\bench.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\FOUNDATIONS.md
