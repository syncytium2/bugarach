GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

Role 6 (RTFM): I checked the one-page methods against the code at 2fa3127e in <repo>. The artifact is docs/methods/one_page/methods_one_page.html (I read its text) and the PDF built from it.

Most of the page matches the code, including every number I checked:
- **Floor:** J = 20 s, 2 s window, 1,000 draws, at most 1 per hour, at least 3 ROIs.
- **Timing spread:** 0.105, 0.131 and 0.150 s.
- **Background rates:** all six REGIMES values.
- **Recordings:** 32 ROIs and 2,700 s.
- **Spacing:** gap medians, events per hour, and events per 45 min (7, 17, 19).
- **Search:** 2.5 s matching tolerance; budgets 7, 1 and 10 per hour, 1 per minute, 0.10; ALPHA_CAP 6e-16; contexts 20–120 s; guard at most a quarter of the context.
- **Chorus:** Adam, lr 0.01, 900 steps, 4,096-frame (409.6 s) crops, pos_weight BCE, seeds 0–4, 2,000 bootstrap resamples over seeds.
- **Output:** apertures ±1 s and ±5 s, gaps 0.5 s and 2.5 s.
- **Dataset:** 66 recordings, 2,109 ROIs, groups 17/17/13/19.

The architecture arithmetic also checks out: an ROI stack of depth 4 sees 31 frames and a head of depth 8 sees 511, so 541 frames, about ±27 s. The findings below are where a description breaks the method or the code.

## Findings (location · issue · severity · suggested fix · verified against source)

1. **CoactDetect, "cell-averaging CFAR test (Finn & Johnson, 1968)"** · This overclaims. In CA-CFAR the threshold is a multiplier on the mean of the reference cells, and the cell under test is excluded. CoactDetect instead tests a z-score against a circular-shift null. With guard = 0, its context includes the test window's own onsets. The project's own table (docs/detector_history.md §4) gives CA-CFAR and Finn & Johnson to rate+context. For CoactDetect it leaves attribution and "held" blank ("—"). · **major** · Say "an adaptive-threshold test in the CFAR family: the background is estimated from a local reference window, optionally with a guard band (cf. Finn & Johnson, 1968)". Do not call it CA-CFAR. · yes (coact.py, sliding.py, detector_history.md; Finn & Johnson citation details confirmed)

2. **CoactDetect, "compared with a significance level α"; search, "α allowed down to 6×10⁻¹⁶"** · α is a normal-tail cut-off on the mean and SD of a Poisson-binomial count (sliding.moments). It is not a calibrated p-value, and the gap is largest in the tail. For 32 ROIs with catch probability 0.03, the normal cut at α = 6e-16 falls at S ≥ 9, where the exact tail is 3e-7. At p = 0.1 the exact tail is 1.3e-9, and at p = 0.01 it is 1.6e-5. So the error is 6 to 11 orders of magnitude (my computation with sliding.poisson_binomial). The code's own docstring calls the cap "about 8 SD of its normal approximation". · **major** · Describe α as a z threshold, e.g. "α = 6×10⁻¹⁶, i.e. z ≥ 8, under a normal approximation". Say it is not a false-alarm probability; the budgets and the floor carry that role. Also say the null's mean and variance are computed exactly (closed form, ROIs independent), not sampled. · yes

3. **Chorus, "each seeing about ±27 s of the recording"** · The dilated stacks do reach ±27 s. But chorus_norm standardises each ROI channel over the whole input window (chorus.py: h.mean and h.std over dim=2). So every frame's logit depends on the entire window. In training that window is a 409.6 s crop. At inference it is the whole analysis window (detect_folder._run_learned) or the whole 45-min bench recording. The docstring flags this train/inference mismatch itself. · **major** · Replace with, e.g., "its convolutions see ±27 s, but the per-ROI standardisation uses the whole input window: 409.6 s in training, the full window at inference". · yes

4. **Simulated recordings, "six decoy bursts"; Scoring (precision)** · A decoy is built exactly like a middle-level planted event. It has the same ROI count after rounding: fast 0.18×32 and 0.203×32 both give 6; slow 0.38 and 0.375 both give 12; combined 0.24 and 0.25 both give 8. It also has the same jitter. A call on a decoy still counts as a false alarm (score.py docstring). Precision therefore penalises calls that no onset-based detector can tell apart from targets. score_bench_candidates reports F1 both with and without decoys; the page mentions neither. · **major** · Define the decoy (a burst with the middle level's participation and spread, not scored as an event). Say that calls on decoys count against precision, and that F1 is also reported without them. · yes

5. **Scoring, "matched one-to-one to planted events within 2.5 s"** · The 2.5 s is measured to the call's span, not its onset. A call whose span contains the planted time matches at any distance (score_detections, `_gap`). Matching is greedy, closest pair first. Calls matched to under-floor events are removed from the score too, not only the events. · **major** (the spans of CoactDetect episodes and chorus runs are long) · Change to "within 2.5 s of the call's span (a span containing the event always matches)", and add "calls matched to sub-floor events are also left out". · yes

6. **Chorus, "Every detector was compared with CoactDetect … paired F1 difference"** · tools/score_bench_candidates.py has `MODELS = ("chorus_norm", "chorus_gain_norm")` and reads only those models' training logs. At this commit the participation variant chorus_norm_part is never scored or paired, even though train_learned_on_bench.py trains it. · **major** (the claim is not supported by the code as it stands) · Add the *_part models to MODELS before the claim ships, or narrow the sentence to the models that are scored. · yes

7. **CoactDetect description vs the shipped fast point** · The page describes only the sliding mode: S over (t − w, t] and an exact null. But fast's `OPERATING_POINTS["coact"]` in bench.py is still binned: fixed bins and 100 Monte Carlo surrogates ("⚠ STILL BINNED HERE"). score_bench_candidates uses that as the "shipped" CoactDetect baseline for every paired comparison, so on fast one of the two CoactDetect baselines is the binned detector. The search runs in sliding mode only with `--sliding`, and `--realistic` does not imply it. · **major** · State that CoactDetect runs in sliding mode and which CoactDetect (shipped or tuned) chorus is compared with. Check that the ADR-0010 night passed `--sliding` and that the fast "shipped" baseline is the one intended. · partly: code yes; the night's command line no (the 2026-09-25-final-parameters README shows `--sliding`, but the ADR-0010 run record is not on main)

8. **Simulated recordings, "gaps resampled from the measured gaps"** · simulate._place_mixed lays the drawn gaps end to end and places the block at a uniform random start. The event count comes from events per hour over all windows (9.7 per hour on fast). The gaps come only from windows with at least two events: the mean fast gap is 100.6 s, which alone implies about 36 per hour. So the planted events sit in one block of about 10 min (fast), 14 min (slow) or 18 min (combined) inside a 45-min recording. The rest holds background only, and decoys only in 120–1,100 s. · **major** (a reader will assume events spread across the recording at the measured rate) · Say so explicitly, e.g. "events are laid end to end at resampled gaps in one block placed at random". Note that count and gaps come from different populations of windows. · yes (my computation from gaps_for_generator.json)

9. **Output, "table of calls (onset, span, count of participating ROIs)"** · Chorus calls carry `n_roi=None` (detect_folder._run_learned). This includes chorus_norm_part, whose internal count is not emitted. · minor · Say the count is reported for CoactDetect only. The call measure's core ROI count is available for both. · yes

10. **Output, "onsets within a fixed aperture around the call's centre"** · measure_call widens the aperture to cover the call's own reported span (window = onset to onset + width). · minor · Change to "a fixed aperture around the call's centre, widened to cover the call's span". · yes

11. **Chorus training: how logits become calls** · Two steps are missing. The per-frame threshold is chosen by pooled F1 on held-apart validation recordings (pick_threshold, fold_maker), and supra-threshold runs within 2 s are merged (decode, merge_gap_frames = 20). Also, each fit uses 10 training recordings with batch 3, and half the crops are centred on an event. · minor · Add one clause on thresholding and merging, e.g. "threshold chosen on separate validation recordings; runs within 2 s merged". · yes

12. **Chorus, "One dilated convolutional filter … shared by all ROIs"** · It is a stack of four dilated Conv1d layers (kernel 3, dilation doubling, 4 channels, GELU) plus a 1×1 convolution. The head is an eight-layer stack of the same kind. Yu & Koltun is cited correctly for exponentially dilated stacks. · minor · Change to "a shared four-layer dilated convolutional stack". · yes (arXiv 1511.07122 abstract read)

13. **Chorus, "the fit with the best F1 … within CoactDetect's empty-recording budget was kept"** · If no seed is within budget, the code keeps the best seed overall (`ok = [...] or rows`). That F1 is also a selection score, a point the tool's docstring asks to be stated wherever it is quoted. · minor · Add "(or the best overall if none meets it)". · yes

14. **Search, "a best value at the limit that switches a setting off was reported as a finding"** · Ruling 5 also covers a value at a cap, e.g. α at 6e-16 (bracketing reason "cap"). · minor · Change to "…at an off-limit or at a cap…". · yes

15. **Scoring, "a precision drop of at most 0.10"** · The drop is between the quiet and busy backgrounds at one setting (MAX_PRECISION_DROP). As written, the reference is unstated. · minor · Add "between the quiet and busy backgrounds". · yes

16. **Floor vs CoactDetect's S** · The floor is always computed on a 2 s co-activity window (event_floor.WINDOW_SEC). CoactDetect's S uses int_win_sec, which the search varies from 0.5 to 5 s. Every shipped point uses 2 s, but a proposal could compare S at w ≠ 2 s with a floor counted at 2 s. · minor · Either fix w at 2 s in the text, or note the mismatch if a proposal moves it. · yes (FULL_GRIDS)

17. **Spacing, "coordinated events were located … at or above each window's floor"** · Each maximal run at or above the floor is one event, and events under 2 s apart are merged. The floor is set so chance produces up to 1 such run per hour, so the 9.7/22.0/25.3 per hour include up to about 1 per hour of chance crossings. · minor · Add "(the floor admits up to 1 chance crossing per hour)". · yes

18. **Background rate** · The p25/p75 come from the 63 recordings that pass the shape fit's floors, not all 66. Fast's time heterogeneity uses two Gamma scales (300 s and 60 s); slow and combined use one. · minor · Say "63 of 66" if the page quotes the total elsewhere. · yes

19. **Empty and elevated recordings** · The elevated-rate recording is run at both the quiet and busy backgrounds, and its stretch has 30 s ramps. The empty recording is at the quiet background only. · minor · Change to "…one (at each background) containing a 300 s stretch…". · yes

## Citations
- **Bibliographic details:** all five are correct. I checked Deep Sets and Yu & Koltun on arXiv, and Finn & Johnson's RCA Review 29(3):414–464 via search. Efron, Annals of Statistics 7(1):1–26, and Kingma & Ba, ICLR 2015, match what I know of them.
- **Where the page uses them:**
  - Yu & Koltun: correct.
  - Zaheer et al.: correct. The pools (mean, population SD, top-4 mean) are symmetric in the ROI axis, which is the claim made.
  - Kingma & Ba: correct.
  - Efron 1979: acceptable for the bootstrap. The code computes a percentile interval over seeds, and the unit (the seed, with F1 pooled over its quiet and busy recordings) could be stated.
  - Finn & Johnson: misapplied to CoactDetect (finding 1).

Sources:
- [Deep Sets, arXiv:1703.06114](https://arxiv.org/abs/1703.06114)
- [Yu & Koltun, arXiv:1511.07122](https://arxiv.org/abs/1511.07122)
- [Finn & Johnson 1968 (SciSpace record)](https://scispace.com/papers/adaptive-detection-mode-with-threshold-control-as-a-function-5d5m9eoan0)
- [Finn & Johnson 1968 (Semantic Scholar)](https://www.semanticscholar.org/paper/Adaptive-detection-mode-with-threshold-control-as-a-Finn/1d775905f818bf867029ba6b80ab9974a5566090)

Files behind the findings (all under <repo>):
- src/bugarach/detectors/coact.py, src/bugarach/detectors/sliding.py
- src/bugarach/bench.py, src/bugarach/simulate.py, src/bugarach/score.py
- src/bugarach/learn/nets/chorus.py, src/bugarach/learn/train.py, src/bugarach/learn/encode.py
- src/bugarach/call_measure.py, src/bugarach/detect_folder.py
- tools/score_bench_candidates.py, tools/search_all_settings.py, tools/train_learned_on_bench.py
- docs/detector_history.md
- docs/learned/runs/2026-09-25-real-intervals/

No files edited and nothing written to scratch.
