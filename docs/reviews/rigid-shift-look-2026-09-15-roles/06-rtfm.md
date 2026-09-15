GRANT 6 MISMATCH — missing Grep, Glob; holds none (no Edit, Write or NotebookEdit)

The two missing tools cost nothing here: I searched with `grep` through Bash. Having no Write tool meant the check scripts ran inline with `python3 -c`. Their results are logged at `<scratchpad>/mb_scratch/role06/checks.txt`.

**Sources read:** the Elephant 1.2.1 installed source for `dither_spike_train` and `dither_spikes` (`surrogate-screen-overnight-venv/lib/python3.14/site-packages/elephant/spike_train_surrogates.py`, line 397). Also the adapter `src/bugarach/surrogates.py`, the classifier `src/bugarach/surrogate_discriminator.py`, `src/bugarach/surrogate_stats.py` (the twins) and `src/bugarach/assess.py`. Also both tools, the three runs' `meta.json` and `results.json`, and the pre-registration `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md`, which is where the percentile convention comes from.

## Findings

1. **Blocking. The classifier sees cross-ROI structure, so the large-displacement "leak" on the slow stream and on Cossart is not a leak.**
   - **Location:** README lines 20–22 (the slow headline and "slow drift moved in time"), 31–32 ("so it cannot see cross-ROI timing"), Figure 3's slow bullet, Figure 5's leak bullet, the Cossart reading at 121–124, and the slow decision item.
   - **Mechanism:** the pooled statistics taken across ROIs (spread, minimum, maximum) respond to ROIs whose rates rise and fall together within a 60 s window. An independent shift per ROI breaks that shared modulation, and a linear model detects it.
   - **Synthetic test** (31 ROIs, 20 min, shared log-rate modulation with a 20 s timescale): accuracy is 0.836 at a 40 s displacement. The same modulation drawn independently per ROI gives 0.500. Brief planted synchronous events stay at chance: 0.513 planted against 0.475 unplanted, from 2,160 window pairs.
   - **Decisive test on the real data:** I shifted every ROI of a recording by the same offset. That keeps all cross-ROI structure and moves each ROI's drift in time exactly as rigid shift does. Each value is the mean of 3 draws × 3 fold seeds:

     | cell | independent shift per ROI (matches the shipped run) | one shift shared by all ROIs |
     |---|---|---|
     | slow, 44.8 s | 0.558 (shipped 0.563) | 0.502 |
     | slow, 22.4 s | 0.539 (shipped 0.549) | 0.502 |
     | Cossart, 40 s | 0.589 (shipped 0.604) | 0.517 |
     | Cossart, 10 s | 0.560 (shipped 0.581) | 0.500 |

   - **Consequence:** drift moved in time cannot be what the classifier detects. It is detecting that shared co-modulation within ±*J* was removed, which is the timescale caveat the note itself raises. The narrow slow window, "Cossart only near 5 s", and "larger shifts leak" all rest on reading this as a leak.
   - **Fix:** rewrite those passages and add the shared-shift control beside every leak cell. Correct the claim of blindness "by construction" in the docstring of `src/bugarach/surrogate_discriminator.py` as well.
   - **Verified against a source:** yes.

2. **Major. "Almost entirely in the DI group" is not supported.**
   - **Location:** README line 20; Figure 3, the slow bullet.
   - **Issue:** at 44.8 s, resampling mice without refitting gives MALE (12 mice) 0.593, interval 0.557–0.633. That is clearly above chance, beside DI (10 mice) at 0.608–0.744. ORX and OVX sit at chance. The group accuracies come from a single fold seed and carry no interval; the DI value moves between 0.645 and 0.681 with the seed.
   - **Fix:** say DI and MALE, and give intervals.
   - **Verified against a source:** yes.

3. **Major. Controls reading 0 and 1 do not show the destruction measure can register partial removal on Cossart.**
   - **Location:** README lines 129–131 ("with K scaled, the controls read 0 and 1, so here it can").
   - **Issue:** the pre-registration labels homogeneous resample only a guard against saturation and do-nothing only a machinery check. It requires a graded `freeze_half` control for exactly this claim, and that control was not run.
   - **What the data show:** the Cossart response is close to a step. Every displacement of 5 s or more reads 0.000. At 1.6 s, K = 110 reads 0.03 while K = 55 reads 0.87.
   - **Fix:** drop the claim, or run `freeze_half`.
   - **Verified against a source:** yes.

4. **Minor. Lab panels plot a retained share where planted events cannot reach K.**
   - **Location:** Figures 2 and 4, K = 8 at 20 % participation.
   - **Issue:** 20 % of 31 ROIs is 6 planted ROIs, fewer than K = 8. The excess before any shift is 0.15 (fast), 0.08 (slow, 1 s bin) and 0.42 (slow, 2 s bin), so each plotted ratio is noise. The pre-registered visibility rule (excess before at least 1.0) would exclude these points. The README already treats the matching Cossart case, K = 146, as "no point".
   - **Fix:** omit those points and say why.
   - **Verified against a source:** yes.

5. **Minor. The leak intervals sit below the point estimate, and the point depends on the fold seed.**
   - **Location:** Figures 1, 3 and 5, and the README's "hides" wording.
   - **Issue:** at slow 44.8 s the refitting mouse bootstrap has median 0.551 against the point 0.563. At fast 20 s it is 0.497 against 0.505. The point itself ranges 0.549–0.575 over 10 fold seeds.
   - **Consequence:** an upper bound read as "hides" is about 0.01 optimistic. That matters for slow at 11.2 s (upper bound 0.551, called "hides" without the caveat that Cossart at 5 s gets) and for Cossart at 5 s.
   - **Fix:** report the point averaged over fold seeds. State that 1.67–98.33 % is the pre-registered one-sided 0.05/3 bound, which is a 96.67 % interval.
   - **Verified against a source:** yes.

6. **Minor. "Bars are 95 % over the 20 twin pairs" misdescribes the bars.**
   - **Location:** Figure 2 caption, inherited by Figures 4 and 6.
   - **Issue:** the bars are 2.5–97.5 percentile bootstrap intervals of a ratio of mean excesses, resampling twin pairs. They are not the spread of the twins. They also use a different convention from Figures 1, 3 and 5, and from the 98.33rd percentile that the 0.25 reference line was signed against.
   - **The estimator itself is sound:** wherever planted events are visible, the excess before is 4–258 excess ROI·events per minute, well above zero.
   - **Fix:** say "95 % bootstrap interval of the ratio of mean excesses", or switch to 98.33.
   - **Verified against a source:** yes.

7. **Minor. The note leaves out settings a reader needs.**
   - **Location:** "What was measured" and the Cossart section.
   - **Issue:** draws per twin (20 on the lab folder, 10 on Cossart), 200 assessor surrogates and 1,000 bootstrap resamples are not stated.
   - **What does match:** Cossart used the same window, edge band, displacement and bin rules, with K scaled and twins and draws halved. `meta.json` agrees with the README on everything the README does state. The lab runs came from commit 93d05bb, and the later diff leaves lab behaviour unchanged.
   - **Fix:** one line per run.
   - **Verified against a source:** yes.

8. **Minor. Two statements are loose about displacement and K.**
   - **Location:** README line 14 and the Figure 2 caption.
   - **Issue:** "removes 84–99 %" at 10–20 s holds for K = 3–4 only; K of 6 or more removes 100 %. "5 s still keeps … 0.60 (slow, 2 s bin)" is actually the 5.6 s displacement.
   - **Fix:** name K and 5.6 s.
   - **Verified against a source:** yes.

9. **Minor. The count statistic differs from the pre-registered one.**
   - **Location:** "Count" in "What was measured".
   - **Issue:** the tool reports a pooled ratio of sums with a mouse bootstrap. The pre-registration averages within mouse. The README does not claim compliance, but the ±2 % band drawn beside it was signed for the other statistic.
   - **Fix:** one clause saying so.
   - **Verified against a source:** yes.

## Checked and sound

- **Rigid shift really is rigid.** With `edges=True`, `dither_spike_train` draws one uniform offset per surrogate for the whole train and drops what leaves [t_start, t_stop). In the wrapper, all 200 of 200 test ROIs moved by one exact whole-frame offset (range −16 to 16 frames at *J* = 16 frames), independently per ROI. Every Elephant parameter is passed explicitly.
- **Edge loss does not reach the scored windows.** Interior windows avoid it for every *J* under 60 s.
- **The edge-thinning control lines up.** Its tiles coincide with the analysis windows, so it is a valid control for the count.
- **The feature mask does what it says.** It removes all 10 edge columns.
- **Mouse grouping holds under resampling.** A duplicated mouse stays inside one fold.
- **The quoted numbers match.** Every leak, count and retained value in the README matches `results.json` and `destruction_table.json`, within the rounding noted in finding 8.
