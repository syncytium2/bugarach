GRANT (blind verify reviewer): held Read, Grep, Glob, Bash, WebSearch, WebFetch, plus Edit, Write and Artifact tools. I did not use the editing tools and changed no repo file. I wrote nothing under the scratch path (the output was only printed), and I opened nothing under docs/reviews/methods_one_page_2026-09-25*.

Artifact: docs/methods/one_page/methods_one_page.html, which matches HEAD, and its built PDF, which is 2 pages and was rebuilt at 20:42 UTC, after the HTML's 20:38. I checked it against src/bugarach, tools, ADR-0008, 0009 and 0010, the run records, GLOSSARY, README and decisions_pending. The reference metadata was resolved on Crossref.

## Findings (role · location · issue · severity · fix, net length ≤ 0 · verified)

1. **Prove It · Output, "width is … floored at one frame"** · The code does not floor the width. `core_span_sec` is last onset minus first onset and can be 0. The floor applies only to the amplitude's divisor: `core_n_roi / max(span, min_interval_sec)` in `src/bugarach/call_measure.py`. The long methods document (`docs/methods/coordination_pipeline_methods.md` l.496–497) places the floor correctly, so the page also contradicts its companion. · **major** · Move the floor with no added words: "*width* is the core's first-to-last onset span; *amplitude* is core ROIs divided by width floored at one frame (ROIs s⁻¹), undefined for one ROI." · yes

2. **Prove It / Reviewer 2 · Output, last sentence, "over-counts on combined"** · This understates the check. `docs/learned/runs/2026-09-25-realistic-bench/README.md` shows over-counting on every stream: fast 25–32% of events, slow 41–47%, combined 75–84% with a median of +2 to +3 ROIs. It never under-counts. The check was also centred on the planted event's time, not on a detector's call. · major · Replace with "where it never under-counts but over-counts, most on combined (median +2–3 ROIs)". This is about the same length. · yes

3. **DOI or Die · CoactDetect, the lineage sentence** · The page credits only cell-averaging CFAR (Finn & Johnson). The repo's own README (l.645–651) places CoactDetect's statistic in the Unitary Events family (Grün, Diesmann & Aertsen 2002, *Neural Comput* 14:43–80) and its shift null nearer Amarasingham et al. 2012 (*J Neurophysiol* 107:517–531). Amarasingham 2012 is shelved and read (`docs/lit_needed.md` l.83–89). Grün 2002 is still unread (`docs/decisions_pending.md` §7). As written, the page credits the radar ancestor and omits the neuroscience one. · **major** · Change to "…resembles cell-averaging CFAR detection (Finn & Johnson, 1968) and excess-coincidence tests against a shifted null (Amarasingham et al., 2012), reached independently." Pay for it by cutting "a z threshold rather than a false-alarm probability" to "a z threshold". Page 2 has room for one more reference line. Grün 2002 stays a residual ⚠ until someone reads it. · yes (repo); papers by metadata only

4. **DOI or Die · Event floor, "(after Pipa et al., 2008 …)"** · This is not the origin. By the repo's own lineage trace, Harrison & Geman 2009 credit whole-train shifting to Pipa, Riehle & Grün 2007 (*Neurocomputing* 70:2064–2068, doi:10.1016/j.neucom.2006.10.142). Pipa 2008 names Grün 1999 as its predecessor. The glossary (l.531–536) lists 2007 first, and says the published form shifts by ~25 ms per trial where this project shifts by ±20 s over a whole recording. · minor · Cite Pipa, Riehle & Grün 2007 in place of, or beside, 2008 (same length if swapped). Optionally change "but dropping" to "but by up to 20 s and dropping". · yes (repo); 2007 by metadata only

5. **DOI or Die · Qi et al. 2017, pages** · "652–660" are the CVF open-access pages. The DOI given (10.1109/CVPR.2017.16) resolves on Crossref to pages 77–85. · minor · Use 77–85 with the DOI. · yes

6. **Prove It · Scoring, "budgets set at 1.6× the rates of CoactDetect's released settings"** · The records don't fully support this.
   - Rule actually applied: `max(1, ceil(1.6 × measured))` (`docs/learned/bench_*_budgets.json`).
   - Slow no-coordination budget: 1 is the minimum of 1, since measured was 0.00.
   - Elevated-stretch budget: 1 call/min is that same minimum on all three streams (measured 0.07–0.22).
   - Precision limit: 0.10 is a separate floor rule, `max(0.10, measured + 0.05)`, not 1.6×.
   - Fast budget: 7 is a legacy declared value; the rule gives 5.
   - Settings measured at: slow's at the fast settings and combined's at "the settings this module started from", not the released ones.
   - Spacing: all budgets were measured on the old 120 s-spacing bench and are applied unchanged on the realistic bench (ADR-0009 R4). · major · Change to "budgets from CoactDetect's measured rates with headroom (1.6×, never below 1)". This is the same length. · yes

7. **Cross-Examiner / Reviewer 2 · Scoring "Every setting must meet budgets" vs Chorus "(the best overall if none met it)"** · These contradict each other. The chorus fallback (`tools/train_learned_on_bench.py`: `ok = [...] or rows`) can keep a model outside the no-coordination budget, and chorus is gated only on that one budget. · major · Change Scoring to "Every CoactDetect setting must meet…". This adds 1 word; cut "one to one," elsewhere or "closest pairs first" if needed. · yes

8. **Cross-Examiner · Scoring vs Benchmark, F1 basis** · The search pools F1 per background and averages the two (`search_all_settings.py`). The fresh-seed benchmark computes F1 per seed, pooled over that seed's quiet and busy recordings (`score_bench_candidates.per_seed_f1`). These are two counting bases and the page states only one. · minor · In Benchmark, change "as a paired F1 difference" to "as a paired per-seed F1 difference". This adds 1 word; cut "Each tuned or trained detector" to "Each detector". · yes

9. **Cross-Examiner / Start With the Problem · Scoring, "CoactDetect's released settings"** · This is used before CoactDetect is introduced, which happens in the next paragraph. "Released" is also not the repo's term: the glossary and code say "shipped", and neither word is in the glossary. · minor · Use "shipped" and let the Scoring clause point forward: "(below)". About net 0. · yes

10. **Cross-Examiner · Chorus, "threshold chosen on validation recordings"** · This names a fourth seed set, outside the "selection / held-out / final" set named in Simulated recordings. It is real (`fold_maker` keeps a threshold-validation block), but the reader has been told there are three sets. · minor · Change to "chosen on training-side validation recordings" (+1 word). Or leave it and add "validation" to the seed sentence. · yes

11. **Reviewer 2 · Parameters, "events cluster, so the median gap is short"** · No clustering statistic was measured. The pooled gaps are also dominated by the high-rate groups: 444 of 507 combined gaps come from DI and MALE (real-intervals README). Part of the short pooled median is group mixing, not clustering. · minor · Change to "the distribution is skewed (mean gap far above median)". Or cut the clause, which saves 7 words. · yes

12. **Reviewer 2 · CoactDetect, "The floor is always computed at 2 s, whatever w"** · True (`event_floor.WINDOW_SEC`), but the consequence is unstated. At w > 2 s a count of floor-many ROIs is easier to reach by chance, so the once-per-hour guarantee holds only at w = 2 s. At other widths α does the remaining work (ADR-0010 ruling 6 notes α acting as a second floor). · minor · Add "so its once-per-hour guarantee holds only at w = 2 s" and pay for it by cutting the Benchmark drop-rule sentence (see 13). · yes

13. **Kill Your Darlings / Start With the Problem · Benchmark, "A detector more than 0.01 F1 behind … is dropped from further tuning"** · This is a panel-selection rule (ADR-0010 part 1) for detectors the page has scoped out. With only CoactDetect and chorus described, it has no job in this section. The tense also shifts to present. · minor · Cut it. That saves about 19 words, which funds 3, 7 and 12. · yes

14. **You Lost Me / house rule · Input, "TTX or senktide"** · TTX is an undefined abbreviation (CLAUDE.md: define every abbreviation at first use), and a non-endocrine reader does not know what senktide is. · minor · Write "tetrodotoxin (TTX) or senktide (an NK3 receptor agonist)" (+6 words). Pay for it with cut 13, or cut "Each recording is divided into windows, its baseline and treatment periods." down to "Windows are baseline and treatment periods." · partly (the agonist class is not verified in the repo)

15. **You Lost Me · Parameters, "cluster of at least 4 co-active ROIs"** · "Cluster" is undefined: it has no time window. The code uses `assess_coactivity` at K = 4 in a 1 s coincidence bin on slow and combined (`tools/measure_slow_bench.py`; the value does not move with the bin). "Seed" in Simulated recordings is also undefined for a cold reader. · minor · Change "per cluster of at least 4 co-active ROIs" to "per moment with ≥4 ROIs co-active within 1 s". This is about the same length. · yes

16. **Kill Your Darlings · Simulated recordings, "It plants the stream's measured events per 45 min"** · Ambiguous: it reads as the measured events themselves. The number meant is the measured event rate × 45 min (`bench.realistic_counts`). · minor · Change to "It plants the stream's measured event rate over 45 min". · yes

17. **RTFM · CoactDetect, CA-CFAR resemblance** · Cell-averaging CFAR excludes the cell under test. CoactDetect with a zero guard keeps the tested window's own onsets in the null (`detector_history.md` l.632–636, self-masking). "Resembles" hedges, but the one structural difference that matters most in dense data is unstated. · minor · No net-length fix is available except "…resembles cell-averaging CFAR…, reached independently; without a guard the test window's own onsets stay in its null", paid for by cut 13. Otherwise accept it as a residual. · yes

## Verified as stated (claim ledger, all match)

- **Cohort and input:** 66 recordings / 2,109 ROIs / 36 mice; groups 17/17/13/19 in DI, OVX, MALE, ORX order; group nested in day; 0.1 s grid; t50 onset; combined stream keeps near-coincident pairs.
- **Event floor:** 2 s window, ±20 s shift drawn uniform in [−J, J), 1,000 draws, ≤1 per hour, minimum 3, dual floors on treatment windows.
- **Measured spacing:** gaps 41.3/25.1/24.8 s at 9.7/22.0/25.3 events per hour; peaks under 2 s apart merged.
- **Measured participation and timing spread:** participation 0.203/0.375/0.25; spreads 0.105/0.131/0.150 s, as SDs from correlogram calibration.
- **Simulated recordings:** 32 ROIs; 45 min; 7/17/19 events; gaps laid end to end from a uniform start; 6 decoys at middle-level participants; 300 s elevated stretch at the 99th percentile; ORX variant; fast seeds doubled.
- **Scoring:** 2.5 s tolerance, one to one, closest first; sub-floor events and their calls leave the score; merge count.
- **CoactDetect:** sliding S(t) in (t−w, t]; exact Poisson-binomial moments; guard is supported in sliding mode (the docstring saying otherwise is stale); α cap 6e-16 ≈ z 8; contexts 20–120 s; guard ≤ ¼ of context; fast shipped binned at 2 s; adoption and cap rules.
- **Chorus:** 4-layer dilated stack; standardise then sigmoid; mean/SD/top-4 pooling; dilated head; 2 s merge (20 frames); 409.6 s = 4,096 frames; whole window at inference; Adam, lr 0.01, 900 steps, pos-weighted BCE; boundary planting at floor ±1; 5 initialisations; fallback.
- **Benchmark and output:** 2,000 bootstrap resamples; call-measure lengths 0.5/1 s and 2.5/5 s, which are judgements; core chosen by distinct ROIs; amplitude undefined at 1 ROI and "dominated by width" (decisions_pending §6).
- **References:** Efron, Perkel, Pipa 2008 and Qi all resolve on Crossref with the cited volume, issue and pages, except Qi's pages (finding 5). Kingma, Yu & Koltun and Zaheer arXiv IDs match. Finn & Johnson metadata matches the repo's read copy.

## Verdict per role

- **1 Prove It:** 3 findings (1, 2, 6), about 60 quantities recomputed or traced; all others match.
- **2 DOI or Die:** 3 findings (3, 4, 5). Searched the repo lineage docs and Crossref. Grün 2002 is unread, and the paper texts were not re-read (residual ⚠).
- **3 Cross-Examiner:** 4 findings (7, 8, 9, 10). Group order, glossary terms ("decoy" is an accepted alias; "call" and "stream" correct) and the "data are" rule are all fine.
- **4 Reviewer 2:** 3 findings (2, 11, 12), plus the budget caveat in 6.
- **5 Kill Your Darlings:** 2 findings (13, 16). `murderboard_prose.sh` is not in this checkout, so I ran my own scan. Banned list from doc_review_process role 5: 0 hits, 0 em-dashes. Block sizes: 141/113/190/118/117/193/185/49/132 words, 1,238 total. The largest blocks (Parameters, CoactDetect) carry distinct facts per sentence, and I found nothing to cut beyond 13.
- **6 RTFM:** 1 finding (17). Bootstrap, BCE weighting, z/α and permutation invariance are used correctly.
- **7 Reinventing the Wheel:** nothing found. The page is hand-written HTML, not generated. It describes the canonical implementations (`call_measure`, `event_floor`, `sliding`) rather than re-deriving anything; its one divergence from them is finding 1.
- **8 You Lost Me:** 2 findings (14, 15). Per block: Input has TTX and senktide undefined; Parameters has "cluster" undefined; Simulated has "seed" undefined. No block has 3 or more undefined terms, so none is blocking.
- **9 Show, Don't Tell:** nothing found. A one-page journal methods section with a full page has no room for a figure without cutting required content; prose is right here.
- **10 Ship It (non-render checks only):** nothing found. The build is current (PDF 20:42 after HTML 20:38, and the HTML matches HEAD). PDF is 2 pages, references alone on page 2. Title and author metadata are set. The rendering table is left to the other reviewer.
- **11 Start With the Problem:** 2 findings (9, 13). The spine is input → floor → simulation parameters → simulated recordings → scoring → CoactDetect → chorus → benchmark → output, the standard methods arc, and it covers every item in the PI's request.
