> Archived verbatim except machine-local paths (shown as `<darkroom>`, `<worktree>`, `<scratchpad>`, `<repo>`, SAP004) and redactions: values of individual calls and positions on real recordings (findings 2, 4,
> 12 and 17) are replaced by `[t]` or `[n]`, because nothing derived from real data goes into this public repo
> (FOUNDATIONS §5). Aggregate counts are kept. Each finding's substance survives.

GRANT 4 ok — Read, Grep, Glob, Bash

Role 4 (Reviewer 2), round 1. The artifact is the built page `<darkroom>\bugarach\2026-09-26-full-panel\briefing\index.html`, and I read it as rendered text. I looked at all 9 example PNGs and rendered Figure 1 myself (scratch copy: `<scratchpad>\mb\r2_fig1.png`). I checked the page against the generator `<worktree>\tools\make_briefing.py`, the night's `065/README.md`, the candidates.json files, `065/review/detect/calls.csv` and `windows.csv`, ADR-0006, ADR-0010, `src/bugarach/score.py` and `docs/performance_table.md`. I edited nothing. No recording ids appear below.

Format per finding: location · issue · severity · fix · verified.

**Blocking**

1. **§1, the F1 definition in Terms, and every table** · The F1 on the page is the bench F1 as scored, and it counts calls on decoys as false alarms. ADR-0006 rules that decoys are coordination by construction. Its consequences say that until the objective ADR is written, "anything reported in the meantime shows F1 with and without decoy calls". The page never mentions decoys. This changes the reading, not just the wording:
   - On slow (new bench), nearly every row has F1 without decoys of 0.99 or more. CoactDetect's shipped setting has 0.949, and on the old bench it has 1.0.
   - On fast, the tube pick is 4th on F1 (0.663) but has F1 without decoys of 0.696. CoactDetect's proposal has 0.651 and 0.996.
   - So the slow table, and much of fast, is ordered by decoy handling. ADR-0006 already found this on slow: "what separated detectors on slow was the decoys alone".

   · blocking · Add an F1-without-decoys column (`mean_f1_without_decoys` is already in candidates.json) beside each bench's F1. Define decoys in Terms. Say in the slow table that the spread there is decoy-driven. · verified: yes

2. **§2, Figures 2–10 and the "median participant" rule** · The page gives no counts for any of the three kinds of call, so a one-off cannot be seen as one. Counted from calls.csv with the page's own rule (baseline windows):

   | stream | both call it | leader only | CoactDetect only |
   |---|---|---|---|
   | fast | 91 | 32 | 1 |
   | slow | 422 | 1 | 3 |
   | combined | 388 | 3 | 71 |

   - "The median of its kind, not the most striking one" means nothing when a pool holds one call. Figure 6 is the only slow leader-only call in the whole data, and Figure 4 is the only fast CoactDetect-only call.
   - Figure 6's call starts [t] before its baseline window ends. It has [n] participants against a floor of [n] for that window. It looks like an artifact of the window edge, not a disagreement.
   - Figure 10's call starts [t] after the recording begins.

   · blocking · Print the per-kind counts, and the number of recordings they come from, above the figures. Mark a pool of one to three calls as a one-off. Flag or exclude calls within about 2 s of a window or recording edge before taking the median. · verified: yes

3. **§2, the reference setting in the examples** · The page says the examples set each leader "against CoactDetect as it ran there". `065/README.md` step D says CoactDetect ran at its **proposal** on every stream. The leaderboard, Table 1 and Figure 1 all use CoactDetect's **shipped** setting as the reference. So §1 and §2 have different references, and the page never says so. Two of those proposals are themselves ruling-5 findings: guard at 0 on fast, guard at the grid edge of 8 s on combined. · blocking · Name the setting in §2 ("CoactDetect at its proposal, which is not the leaderboard's reference"), and show CoactDetect proposal's own ΔF1 beside each leader. · verified: yes

**Major**

4. **Figure captions 2, 3, 6 and 9** · Four of the nine captions give the call's time one minute late, and Figure 6 reads "20m60s". The cause is in the generator: `f"{t / 60:.0f}m{t % 60:02.0f}s"` rounds the minutes instead of truncating them. The actual onsets are a minute earlier in each case, and the plotted windows centre on those times, not on the captioned ones. · major · Use `int(t // 60)` and round the seconds with carry, or reuse the house time formatter. · verified: yes

5. **Table 1 and Figure 1, slow stream** · "16 rows above, 1 below" on the new bench and "0 above, 18 below" on the old are mostly one row moving: the reference. CoactDetect shipped falls from 0.848 to 0.786, while the other rows sit at about 0.82–0.83 on both benches. Figure 1 shows exactly this: every filled mark bunched at +0.03 to +0.04, every open mark at −0.02. Counting "rows above" reads as 16 improvements.
   - `065/README.md` finding 4 gives the other view. Against CoactDetect's **proposal**, the learned picks run from −0.050 to +0.013, and only one pick's interval is above zero (chorus_gain_norm_part on combined).

   · major · Add a sentence per stream saying how far the reference itself moved between benches. Add the comparison against CoactDetect's proposal as a second reference column, or at least to Table 1. · verified: yes

6. **§1 ordering, "#", "leaderboard", "top row", "leader"** · The page has no statement that the order is not a ranking; that disclaimer exists only in the generator's docstring. On slow, 16 rows lie within 0.007 of each other.
   - ADR-0010 part 1 fixed a rule before the run: a detector more than one noise unit (0.01 F1) behind the leader on at least two streams is dropped. The page neither mentions nor applies it.
   - About 126 intervals are read as "the seeds resolve", with no correction for multiplicity.

   · major · State on the page that the order is a reading of intervals, not a ranking. Show the 0.01 noise unit (for example a band in Figure 1). Say that the intervals are per-row and uncorrected. · verified: yes

7. **§1, the old-bench column** · ADR-0010 ruling 2 says "The old bench is not scored as a reference". Tony asked for the comparison afterwards (the generator's docstring quotes him), but the page does not say it departs from the ruling.
   - Meanwhile the check ruling 1 required, a bench spaced like slow ORX, was scored (`065/fresh-orx/candidates.json`) and is left out. It is the one robustness check tied to a group difference.

   · major · Say that the old column was requested after the ADR and is outside ruling 2. Add the ORX-spacing column, or say why it is absent and where it lives. · verified: yes

8. **§1, pooled across the bench's design factors** · ΔF1 pools the quiet and busy backgrounds, and the per-background F1s differ a lot. Fast SPIKE-synch shipped is 0.635 (quiet) against 0.738 (busy); fast rate+context proposal is 0.57 against 0.76. The page flags "precision swing" as a budget failure but never shows the split.
   - ADR-0010 part 3 says every score reports a merge count. `merged_calls` is in the data but not on the page, although merging is why the new bench exists.
   - "Background" and "seeds per background" are never defined.

   · major · Show ΔF1 per background (or at least per-background F1) and the merge count per row. Define "background" in Terms. · verified: yes

9. **§1, the "new mean F1" / "old mean F1" columns** · These columns are undefined and do not reconcile with ΔF1. Fast SPIKE-synch: 0.686 − 0.608 = 0.078, but ΔF1 is +0.063. Fast binned SCE proposal: 0.043 against 0.027, although it has the same mean F1 as CoactDetect's proposal, whose ΔF1 is 0.040. The column is the mean of two background-pooled F1s (`score_bench_candidates.py:322`); ΔF1 is the mean of per-seed differences. · major · Define both estimators in Terms and say why the columns do not subtract. · verified: yes

10. **Learned-pick rows and their intervals** · The bootstrap resamples bench seeds only. Each learned row is one training seed, chosen as the best of five on held-out F1, and training variability is large: some fast and combined seeds collapse to F1 0.264 and 0.111. So "a difference the seeds resolve" understates the uncertainty for the model family, and the best-of-five choice is not visible. · major · Say that the interval covers bench seeds only, and show the five-training-seed spread (min–max F1) per family. · verified: yes (fresh seeds 6000+ are disjoint from search seeds 1–96, so there is no leakage)

11. **§2, the 2.5 s agreement rule** · The page says it is "the bench's scoring tolerance, so agree means what a hit means there". It does not mean the same thing:
    - The bench matches one call to one planted event, measuring from the event time to the call's span (`score.score_detections`).
    - The examples call two spans in agreement if they overlap after padding by 2.5 s, and one call can agree with many others.
    - So a wide CoactDetect call that merges two events "agrees" with both of the leader's calls. This hides merges, the ADR-0010 defect. I counted 4 such CoactDetect calls on fast and 4 on combined.
    - The 2.5 s value was calibrated where LoCo and CoactDetect plateau on the fitted field, and slow and combined inherit it without argument.

    · major · State the rule as it is (span overlap ± 2.5 s, many-to-one). Count calls that overlap two or more calls of the other detector as a separate kind. Drop the "means what a hit means" claim. · verified: yes

12. **Pictures: Figures 6, 9 and 10** · What the images show:
    - **Figure 6:** the plotted window runs past the baseline window's end into time where no detector ran. It shows large stripes with no call in any lane, notably one near [t], so a reader sees three detectors "missing" obvious events in unanalysed time.
    - **Figure 9:** a run of 3–4 close stripes around [t] is mostly uncalled by every lane. This is the close-events regime the night was built for, and the text never mentions it.
    - **Figure 10:** the call is at the recording's first half-second, and the window is cut at the recording start although the caption says "120 s either side".

    · major · Show unanalysed spans in a lane (not on the raster) or clip windows to the analysed window. Correct the "either side" wording when the window is cut. Mention the uncalled cluster in Figure 9. · verified: yes

13. **§2, pooled across groups** · All nine examples come from DI or MALE; none from OVX or ORX. Disagreements concentrate in DI: 48 of the 71 combined CoactDetect-only calls, and 16 of the 32 fast leader-only calls. FOUNDATIONS §9 says results depend on group. The breakdown is available: windows.csv carries group and hours, so its absence cannot be claimed. · major · Give per-group counts and rates per baseline hour for each kind. · verified: yes

14. **Budgets and the "pick" rule** · The page gives no source or justification for any limit: 0.1 and 0.15 for precision swing, 1 call/h, 1 call/min, and 4 calls/min for locust. The "pick" definition uses only the null-recording budget, yet the page marks several picks over other budgets. Table 1 counts over-budget and ruling-5 rows among "rows above", and its "top row" for fast is over budget (SPIKE-synch shipped). The worker README says only one row is over budget; the page never explains the difference. · major · Say where the limits come from. Exclude or separately count over-budget and ruling-5 rows in Table 1. Add one line reconciling the README's count with the page's. · verified: yes

**Minor**

15. **Budget marks** · "0.10 against a limit of 0.1" and "1.13 against 1" read as within budget at the printed precision. · minor · Print enough digits to show the excess. · verified: yes

16. **§2, rows passed over** · On fast, rows 7 and 8 (count binned proposal, LoCo shipped) did not run on the real recordings and are skipped silently; only LoCo proposal is named. · minor · Name every row passed over and why. · verified: yes

17. **Figure 5** · The "agree" example cannot show a disagreement: LoCo and CoactDetect are identical in every call across the window (422 of 426 slow calls agree overall). The line lane calls stripes that both miss, at two places in the window ([t] and [t]), and the text never mentions it. · minor · Say that LoCo ≈ CoactDetect on real slow data. Note the line-only stripes. · verified: yes

18. **Figure 1 colour** · Red means both "over a budget on that bench" and "no pick". · minor · Use a separate mark for no pick. · verified: yes

**Boundary notes for other roles:** the truncated y-label in Figure 9 ("30 RO") is for agent 10. The page lists recording ids in its captions and tables; that is fine for the darkroom copy, and the generator keeps it out of `--also`.
