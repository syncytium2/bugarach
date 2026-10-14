GRANT 4 ok — Read, Grep, Glob, Bash

Role 4, Reviewer 2: murderboard round 1 on `docs/learned/coordination_share_explainer/README.md` and fig1–fig5.

I read the README, the generator, numbers.json, `tools/measure_coordination_rates.py` (docstring, `shifted`, `solve`, `pooled_ratio`, `per_recording`, `CAL_NO_PROBE`, `ADOPTED_MODEL`) and FOUNDATIONS §9. I opened all five PNGs.

To test power I ran the explainer's own `recording()` simulator against the tool's estimator, inline with `python -c`. Nothing was written to the repo or the artifact. I don't hold Write, so I made no scratch file either. The scratch folder `.../scratchpad/mb-r1/r4/` exists but is empty. Every "verified: yes" below comes from those runs: 24 seeds unless stated, quiet background, 1 s window.

## Findings
Format: location · issue · severity · suggested fix · verified

**1. "What it cannot see", bullet 2, and Fig 5A bottom row (the slow 3× rise) · blocking · verified: yes**
- **Issue:** the ramp test cannot fail.
  - At the README's level (quiet background, 3× rise), the recording's own cumulants are already zero before any shifted copy is subtracted: f₂ = +0.0016 and f₃ = −0.0007 (median).
  - A linear ramp has no skew, so it puts essentially no triples in f₃. A pooled f₃ ≤ 0 means "no answer" whether or not the shifted copies carry the ramp.
  - So the row cannot tell "subtracted because it survives the sliding" from "never registered". The mechanism the README gives for it is asserted, not shown.
- **Fix:** rerun the ramp at a size that registers before subtraction. I checked one: a 3× ramp at a mean of 0.0635 onsets/s/cell gives f₂ = +0.19 before subtraction, and the shifted copies remove 99% of it. Show f₂ before and after subtraction side by side.

**2. Same section: "A shared change faster than about a minute is counted; a slower one is not" · blocking · verified: yes**
- **Issue 1: the "about a minute" boundary is asserted, and the page's own middle row contradicts it.** A 5-minute busy stretch is slower than a minute, and it is counted.
- **Issue 2: the stated mechanism is wrong.** The README says "the shifted copies cannot remove it ... the stretches no longer line up". In fact the copies remove about 92% of the stretch's f₂. What gets counted is the leftover at its abrupt edges.
- **Issue 3: there is no boundary at a minute, only a gradual roll-off.** Share of f₂ that survives subtraction, by stretch length:

  | Stretch length | f₂ kept |
  |---|---|
  | 10 s | 0.85 |
  | 30 s | 0.61 |
  | 60 s | 0.36 |
  | 120 s | 0.16 |
  | 300 s | 0.08 |
  | 900 s | 0.03 |

  The reported share, if pooled with a planted run, peaks near 7% for 30–60 s stretches. The tool docstring's "slower than ~a minute survives" has the same over-sharpness.
- **Fix:** replace the sentence with a curve: kept fraction (or reported share) against stretch length. Say that abrupt field-wide changes leak at their edges whatever their length, roughly in proportion to (shift span ÷ duration). Drop the "had this backwards" aside, or qualify it.

**3. Bullet 1: "busier stretch ... median 3.7%, up to 5.7%" · major · verified: yes**
- **Issue:** the only amplitude tested is a 26× jump (0.127 vs 0.0049 onsets/s/cell). Stretch onsets are then about 75% of all onsets, so the 3.7% sits on a denominator the stretch itself tripled.
- 300 s stretch at other sizes, pooled with a planted run:

  | Stretch size | Reported share |
  |---|---|
  | 2× quiet | −0.01% |
  | 5× quiet | 0.23% |
  | 10× quiet | 0.7% |

  The number cannot be carried over to a treatment recording.
- **Fix:** show the response against amplitude. State the stretch's share of all onsets. Never quote 3.7% as a size.

**4. Bullet 3 and Fig 5A rows 1 and 3: "no answer at all, not a small one" · major · verified: yes**
- **Issue 1:** "no answer" happens only because all 24 recordings in the pooled set are null, so `pooled_ratio` (not `solve`, as the README says) returns NaN.
  - In a real run, a null recording is pooled with recordings that do have coordination, and it gets a number.
  - Reported share for 24 null recordings pooled with the planted set: median −0.04%, range −0.43% to +0.66%. Ramp recordings: −0.59% to +0.72%.
  - Negative shares are possible, and the page never says so.
- **Issue 2:** the figure text says "no coordination reported in any of 24 recordings", which reads as zero and contradicts the README's "no answer".
- **Fix:** say "no answer when every recording in the set is null". Show what a null recording reports inside a mixed run, and say that shares can be negative. Fix the figure text.

**5. Few-moments paragraph and Fig 5B diamonds: "Pooling ... pulls each set back to about 81% to 83%" · blocking · verified: yes**
- **Issue:** the diamond is a median. The tool's actual per-recording answer (pooled f₃/f₂ with each recording's own f₂) is wider than the black dots, not narrower:

  | Moments planted | Tool's own answer, q10–q90 | Range |
  |---|---|---|
  | 6 | 0.56–0.98 | down to 0.46 |
  | 3 | 0.52–1.03 | 0.39 to 1.22 |

  Pooling fixes the participant count to the set average, so each recording's error then depends on how its own moments were sized. A treatment reader gets these per-recording numbers. The figure implies pooling cures the noise.
- **Fix:** plot the tool's per-recording answers, not only their median. Reword to "pooling steadies the median, not the individual recording".

**6. Fig 5B, 3-moment column: "Few shared moments make one recording's own answer noisy" · major · verified: yes**
- **Issue:** much of that spread is the planted sizes, not the count.
  - Moments sized (3, 3, 10) recover 0.59–0.87 of the planted share.
  - (3, 3, 3) gives 1.07.
  - (3, 3, 6) gives 1.37.
  - Size mixture, the number of moments and noise are confounded.
- The quoted 69–105% (q10–q90) also hides the plotted extremes, about 0.58 and 1.37.
- **Fix:** say the spread includes which sizes the moments had. Quote the full range or show it.

**7. "So a lower event rate on its own does not make the answer noisy" · major · verified: yes; the claim holds, the evidence does not**
- **Issue 1:** the evidence offered is the pooled median (79/81/81%), which measures bias, not noise.
- **Issue 2:** the low-background sets use the mixed gap schedule (default kwargs), not the 120-s schedule of Fig 5B that the next sentence implies.
- **What I checked:** per-recording spread, 15 moments, 120-s schedule. The claim survives:

  | Background | Recording's own answer, q10–q90 | Tool's answer, q10–q90 |
  |---|---|---|
  | 1× quiet | 0.78–0.84 | 0.76–0.86 |
  | 0.25× quiet | 0.81–0.85 | 0.78–0.87 |
  | 0.1× quiet | 0.80–0.84 | 0.78–0.86 |

  Note that planted share rises from 21% to 71% as background falls, which is why the noise does not grow. The test never raises the background (busy level), which is the direction where noise would grow.
- **Fix:** cite per-recording spread at each background, put it on the same schedule as Fig 5B, and say the busy direction is untested.

**8. §4: "every fixed-model share here reads low by about a fifth ... take the fixed-model share as an underestimate of that size" · major · verified: yes**
- **Issue:** the bias belongs to the planted size mixture (10/6/3 cells), not to the measure, so "of that size" overreaches. Single-size runs:

  | Planted size | Fixed model error | Binomial model error |
  |---|---|---|
  | All moments 10 cells | −4.6% | +5.1% |
  | All moments 3 cells | −1.1% | +118% |

  - So "the binomial is the closer of the two" is also specific to this mixture: with small uniform moments it doubles the answer.
  - A real field's size distribution is unknown, so the size of the error is unknown too.
- "Every fixed-model share ... about a fifth" is also inexact: the medians run −10% to −21% (Fig 4A), and individual recordings vary.
- **Fix:** state that the direction and size of the error depend on how widely moment sizes vary. Give the single-size results as the other end of the range.

**9. §4: "The reason both read low is ... three sizes" · minor · verified: partly**
- **Issue:** the mixture alone predicts about −14% (fixed) and −4.5% (binomial). Fig 3 and numbers.json show −21% and −11%, and single-size runs still read −1% to −5%. Several points of loss are unexplained (window edges, jitter, or subtraction).
- **Fix:** "mostly because"; name the remainder as unexplained.

**10. §5: "The share hardly moves ... survives", and "read k, λ at 1 or 2 s ... about 3 percentage points" · major · verified: yes**
- **Issue 1:** the "twice the size at half the rate" argument is exact only when both merged moments have the same size.
  - Fig 4A at 4 s: 120-s-only reads −10%, close pairs and mixed read −18%. That is an 8-point shift from just 2 pairs; with 5 pairs it is −19% against −10%.
- **Issue 2:** close pairs are only tested at 2 s, never closer than a window.
  - At a 0.5 s gap and a 1 s window, participants per moment reads +75% (against +28%), and +96% at 2 s.
  - So the "1 or 2 s" advice holds only for pairs at least about 2 s apart.
- **Fix:** qualify both, and add a sub-window close-pair set.

**11. §5 recommendation and "How we know it works" · major · verified: yes (numbers.json)**
- **Issue:** participants per moment (+28% to +32%) and moments per minute (−35% to −39%) fall outside the ±25% band at every window and schedule. The README recommends reading them at 1–2 s and says "the check passes", without saying the band is applied only to the share.
- **Fix:** state plainly that k and λ fail the same tolerance on these recordings, and are reported for description only.

**12. "The simulated recordings" / "What it cannot see": limits of the simulated set · major · verified: no (reasoned; frequent moments not simulated)**
- **Issue:** the simulated set has:
  - steady Poisson backgrounds;
  - no bursts within a cell;
  - random participant subsets;
  - moments at least 120 s apart except the planned pairs.

  The shifted copies spread cells over about ±32 s, so moments that recur more often than that could realign cells onto neighbouring moments and subtract real coordination. No check here can register that. None of these are listed as limits.
- **Fix:** add them to "What it cannot see", or test a set with moments every 20–30 s.

**13. "A blank page" header: "will report how much of the activity is coordinated under treatment" · minor · verified: yes**
- **Issue:** the tool's docstring (line 81) says "Baseline only (FOUNDATIONS §9)".
- **Fix:** say the treatment use needs a window change that is not in the tool yet, or point to where it is planned.

**14. §1: "For cells with independent onsets, both are zero on average, whatever each cell's rate" · minor · verified: yes (docstring says "at constant rates")**
- **Fix:** add "and steady rates". §2 then motivates the shifted copies.

**15. §4 and Fig 3: "Both are inside the pass band" · minor · verified: yes (picture)**
- **Issue:** the pass test is on the median. In Fig 3, several fixed-model recordings at about 24–25% planted sit at or below the band's lower edge.
- **Fix:** "the medians are inside; individual recordings reach the edge".

**16. Fig 4 (all panels) · minor · verified: yes (generator)**
- **Issue:** medians only, so the spread across the 48 recordings behind every "hardly moves" claim is hidden.
- **Fix:** add q10–q90 bars.

Pictures read: Fig 1 shows two close pairs and one medium pair, and no aqua single moment, although the legend lists one. Fig 2 supports the text. Fig 3 is systematic underestimation, consistent with the text. Fig 5B shows the 3-moment outliers at about 0.58 and 1.37 that the text's percentile range hides.

Paths:
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\explain_coordination_share.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\tools\measure_coordination_rates.py
