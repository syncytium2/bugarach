GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1: Claim and data verifier ("Prove It"). Round 1 report

**Artifact reviewed:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html` (the built page, extracted to text)
**Generator:** `...\replicate-report\tools\make_replicate_report.py`

**Method:**
- I recomputed every quantity myself, with independent Python, from these files in both runs' `results/` folders: `results.json`, `meta.json`, `selections/*`, `fits.zip` and `configs/`.
- I regenerated Figure 1's recording (seed 2000 at the quiet background) with `bugarach.bench.make_recording`, then ran CoactDetect on it through `ui.app._compute`.
- I read the code in the `weekend-runs` worktree (7a95e8a) and diffed it against WSMIP064's recorded commit e8764aa.
- I read the rehearsal's `results.json` and its handoff on `origin/tune-bench-comparison`, plus the goal pages, the fold-defect todo, `bench_measured.json` and `HANDOFF-slow-comodulation…` on `origin/main`.
- I wrote nothing outside my scratch folder.

## Findings

Columns: # · location · issue · severity · suggested fix · verified against a source?

1. **"The answer, first", bullet 2, and §9 bullet 3 ("On F1 alone…")** · major · verified: yes (`results.json`, both runs)
   - **Issue:** The headline compares the **untuned** chorus_norm with CoactDetect chosen on F1 alone, but labels the comparison "On F1 alone… the leading net".
   - In the column the page actually calls "chosen on F1 alone", the leading net trails CoactDetect in **both** draws:
     - WSMIP064: chorus_norm 0.741 − 0.748 = −0.007
     - WSMIP065: chorus_gain_norm 0.719 − 0.748 = −0.029
   - That is the same sign twice. The "opposite sign, question open" conclusion (−0.012 / +0.006) exists only because the untuned column was swapped in, and the page never says so.
   - **Fix:** Label the bullet "untuned chorus_norm against CoactDetect". Also report the F1-alone comparison. If the untuned model was used to avoid the fold-1 collapse, say that.

2. **§4 text, Figure 3 and its caption ("train on two of the three training folds"; "refitted on all three training folds")** · major · verified: yes (`fits.zip` run records; `tune_learned_vs_coact.py` line 140)
   - **Issue:** Every net fit, inner and refit, trains on **10 recordings** (5 seeds × 2 backgrounds) and picks its threshold on 2. `N_TRAIN = 10`.
   - I checked all 1,943 run records in WSMIP065's `fits.zip`:
     - 1,728 inner fits: 10 fitted recordings, 48 available.
     - 215 refits: 10 fitted recordings, 72 available.
   - The coded detectors are searched on all 72 recordings.
   - "Refit on all three training folds" reads as "trained on 72". In a page about a *fair* comparison, this asymmetry is left out.
   - **Fix:** State that each net fit trains on 10 recordings drawn round-robin from those folds and picks its threshold on 2, while coded searches score all 72.

3. **Summary bullet 3, §6 and §9 bullet 1 ("the rehearsal … leading net ahead of CoactDetect by +0.011 F1 under the budget")** · medium · verified: yes (shakedown `results.json`; `HANDOFF-workstation-tuning.md` lines 892–900)
   - **Issue 1:** The rehearsal's leading net under the budget was **chorus_gain_norm, at +0.016** (0.7284 − 0.7124). The +0.011 is chorus_norm's budgeted margin (0.7236 − 0.7124 = +0.0112).
   - **Issue 2:** The rehearsal ran the retired home simulation, with the coded side tuned on three settings only, the old budget and no context rule. The handoff says "No readout is planned and nothing quotes them." Measuring it against the bench's draw-to-draw movement mixes conditions.
   - **Source defect, for the record:** the handoff's prose says "+0.011 ungated and +0.012 gated". Its own `results.json` has these swapped: +0.0122 without the budget, +0.0112 under it.
   - **Issue 3:** The number is typed into the generator by hand.
   - **Fix:** Use +0.016 for the leading budgeted net, or name chorus_norm. Say the rehearsal ran on a different simulation. Read the number from the file.

4. **Summary bullet 3, §7 and §9 ("median over 20 entries … without a named defect")** · medium · verified: yes (recomputed)
   - **Issue:** The 20 "clean" entries include two that the page itself marks †:
     - chorus_gain_norm chosen on F1 alone: † in both draws, and §8 names its failed seed.
     - tube under the budget: † in WSMIP064, where fold 0 refit seed 4 called nothing.
   - The generator excludes only chorus_norm (both selections) and the two ‡ cells.
   - Excluding every † and ‡ entry leaves 18 entries. Their median move is **0.0065**, not 0.0082. The maximum stays 0.0268.
   - "About 3 times the median move" becomes about 4 times.
   - **Fix:** Exclude every †/‡ entry, or drop "without a named defect".

5. **§9 bullet 4 ("line_length gained +0.032 and +0.029 … more than any entry moved between draws")** · medium · verified: yes
   - **Issue:** This is false as written. chorus_norm moved −0.051 (F1 alone) and −0.060 (under the budget), and binned SCE under the budget moved −0.060.
   - The claim is true only of the entries without a defect, where the maximum is 0.027.
   - **Fix:** Add "…than any entry without a named defect".

6. **Figure 4's text ("every entry in that column is held to the false-alarm rate of one fixed detector") and the summary's "under one shared false-alarm budget"** · medium · verified: yes (`seeds_over_budget` and `over_budget` in `results.json`)
   - **Issue:** Admissibility is checked on the training recordings only. On the held-out recordings, budgeted net refit seeds went over the ceilings:
     - WSMIP064: **25 of 80** (chorus_gain_norm 7 of 20, tube 11 of 20)
     - WSMIP065: **16 of 80** (chorus_gain_norm 5 of 20)
   - CoactDetect itself went over in WSMIP064 fold 2 (busy stretch 14.0 per hour against a ceiling of 12.8).
   - None of this appears on the page.
   - **Fix:** Report how often held-out results exceed the budget, per entry, or say plainly that the budget holds on training recordings only.

7. **§7 ("its best setting on F1 alone already meets it" because "the budget is built around its own settings")** · medium · verified: yes (`chosen_params` in `results.json`)
   - **Issue:** In WSMIP064, the F1-alone search moved off the reference settings in 3 of 4 folds (α 3×10⁻⁵ in folds 0 and 2; guard 0 s in fold 1). The fold-2 choice then exceeded the ceiling on the held-out recordings.
   - The two columns are identical (same `config_key` in all 8 folds), but the stated reason holds only for WSMIP065.
   - **Fix:** Say the F1-alone choice happened to be admissible on the training recordings in every fold. Drop the causal "built around its own settings".

8. **§8, "Settings at the edge" ("SCE's lead on F1 alone may be … a long merge")** · medium · verified: yes
   - **Issue:** SCE leads on F1 alone only in WSMIP064 (0.771 against 0.748, +0.023). In WSMIP065 the two are tied: 0.74779 against 0.74777.
   - A page whose thesis is two-draw agreement states a one-draw fact without saying so. (Not an error in itself: under the budget, SCE also beats CoactDetect in WSMIP064, 0.770 against 0.748, and in 3 of 4 WSMIP065 folds. The page does not mention this.)
   - **Fix:** Say "in WSMIP064's draw". Consider noting SCE's budgeted lead.

9. **Figure 1 caption ("6 decoys, real bursts of coincidence that are not coordinated events")** · medium · verified: yes (`simulate.py` lines 791–808; `score.py` lines 44–51; recomputed recording)
   - **Issue:** A decoy is built exactly like an 18% planted event: 6 ROIs, the same 0.36 s jitter. It meets §1's own definition of a coordinated event and differs only by its label and its window (120–1,100 s).
   - `score.py` calls "should a burst count?" a live question, and every call on a decoy costs precision.
   - In Figure 1's own recording, CoactDetect fired on **all 6 decoys**: 6 of its 8 unmatched calls. It matched 12 of the 15 planted events.
   - **Fix:** Say the decoys are constructed like planted events and counted as false alarms by rule, and that this lowers every detector's precision.

10. **§11 ("nothing on it is typed by hand"; generator docstring "Nothing is retyped")** · medium · verified: yes (generator source)
    - **Issue:** This is false. Hard-coded in the generator:
      - +0.011
      - 30–36%, 8 s, 6 s
      - 0.03%, 12 ROIs, 4 recordings, "eight fitted constants", 2026-09-17
      - "2 of its 5", F1 0.125, "at 0", "trains at 3"
      - 1000–1009, "folds 3 and 4"
      - "3 training seeds" (§8)
      - Figure 3's "48 seeds", "72 training recordings", "0.002" and the "4 × 5 refits" formula
      - Figure 4's "0.0052 Hz", "300 s", "36 training seeds"
      - "one graphics processor"
      - the fold ranges' `seeds[f*12]`
    - Most of them are correct, but the provenance claim is not.
    - **Fix:** Read these from the files, or change the sentence to "every result number…".

11. **Figure 3 ("Every learned model: 432 inner fits, then 4 × 5 refits")** · low · verified: yes (`fits.zip`)
    - **Issue:** The 432 inner fits per net are correct. Refits are **55, 55, 55 and 50 per net** (215 in total in WSMIP065), because the untuned choice and both selections are each refitted at 5 seeds.
    - **Fix:** Write "up to 3 configurations × 4 folds × 5 seeds".

12. **Figure 6 caption ("The lone low dots are defects named in section 8"); Table 1's † note ("section 8")** · low · verified: yes
    - **Issue:** WSMIP064 tube under the budget, fold 0 (0.505) is low because refit seed 4 called nothing. §8 does not name it.
    - **Fix:** Name it in §8.

13. **§8, locust ("a ceiling near 17"; "the quiet busy stretch")** · low · verified: yes (`meta.json` budgets)
    - **Issue:** The quiet ceilings across the 8 folds run from 14.9 to 18.1 per hour; 16.5 is WSMIP065 fold 0 only. The range 449–527 calls per hour and the 16 of 16 refused are correct.
    - **Fix:** Write "ceilings of 15–18 per hour". Reword "the busy stretch at the quiet background".

14. **§8 ("tiny, showed in every published run")** · low · verified: partly
    - **Issue:** The todo `2026-08-28-two-architectures-have-no-operating-point.md` shows one bake-off with 4 of 4 folds at the threshold floor and F1 0.125. "Every published run" is not established.
    - **Fix:** Write "in every fold of the bake-off that measured it", and cite the todo.

15. **§10 ("the lab's treatments move the two streams in opposite directions")** · low · verified: yes (`goals/README.md` decision 4, citing FOUNDATIONS §9)
    - **Issue:** The source says this happens **under TTX**; the page generalises it to all treatments.
    - **Fix:** Write "under TTX, the two streams move in opposite directions".

16. **§4 warn box ("The rehearsal run found that two outer folds trained the same net")** · low · verified: yes (the fold-defect todo)
    - **Issue:** The defect was found by the 2026-09-17 murderboard of the rigid-shift report, in a different harness. The shakedown instance was identified afterwards. "Counting from 1" and 1000–1009 are correct.
    - **Fix:** Fix the attribution.

17. **§11 ("the chosen refits (loadable by `bugarach detect --model`)")** · low · verified: yes (`origin/main` nets folder)
    - **Issue:** chorus_norm and chorus_gain_norm are not registered on `main`, so they load only from `replicate-run` or `tune-bench-comparison`.
    - **Fix:** Name the branch.

18. **§10, the re-measurement ("Both workstations re-measured … eight fitted constants on the corrected export")** · low · verified: yes (`origin/tune-bench-comparison:HANDOFF-workstation-tuning.md` lines 839–856)
    - **Issue:** The content is correct: the changes sit far inside their bootstrap intervals, and participation is outside its interval in both folders. But the only source is an unmerged branch handoff. `bench_measured.json` on `main` covers `steps_excluded` alone.
    - **Fix:** Cite the source.

19. **§9 bullet 2 ("about 3 times the median move, though not beyond the largest")** · low · verified: yes
    - **Issue:** 0.030 (WSMIP064) *is* beyond the largest move (0.0268). Only 0.025 is not.
    - **Fix:** Write "one of the two beyond it".

20. **§8 ("8 s, is the value goal 1 checked against crowded recordings")** · low · verified: yes (`coded-detector-optimization.md` lines 78 and 86)
    - **Issue:** This is correct: the sliding values passed the crowded veto. But goal 1 also records that an 8 s merge "fuses crowded events planted 6 s apart. Part of the loss may be that".
    - **Fix:** Add the caveat.

21. **§9 ("two draws that share nothing")** · low · verified: yes
    - **Issue:** The two runs share configurations, training seeds and code (the page itself says so in §6). They share no *recordings*.
    - **Fix:** Write "that share no recording".

## Claim ledger (quoted value · source · my recomputed value · verdict)

**Table 1.** All 44 cells match to 3 decimals.
- Examples: chorus_norm 0.736/0.753 · 0.741/0.690 · 0.716/0.656; chorus_gain_norm under the budget 0.718/0.723; CoactDetect 0.748 in all four cells; binned SCE 0.771/0.748 · 0.770/0.710; locust 0.549/0.544 under the budget; SPIKE-synch 0.274/0.261.
- † placement matches the `failed_training_signature` and `f1_was_nan` flags.
- ‡ placement matches the searches that refused every candidate (cicada in all 8 folds; SCE in WSMIP065 fold 2).
- Nothing is missing: every cell has 5 refit seeds, `errors` is empty in both runs, and there are no "no admissible configuration" notes.
- Verdict: match.

**Summary and results numbers:**

| quoted | source | recomputed | verdict |
|---|---|---|---|
| chorus_gain_norm − CoactDetect under the budget: 0.030 / 0.025 | `comparisons` | −0.0303 / −0.0250 | match |
| untuned chorus_norm − CoactDetect: −0.012 / +0.006 | table means | −0.0122 / +0.0055 | match (but mislabelled; see finding 1) |
| median move 0.008, maximum 0.027, over 20 entries | recomputed | 0.0082 / 0.0268 over 20 | match as computed; set is mislabelled (finding 4) |
| per-entry moves in Figure 7 (all 24) | recomputed | all match | match |
| "about 3 times" | recomputed | 3.04 | match |
| chorus_gain_norm moved +0.005; CoactDetect 0.000 | recomputed | +0.0050 / −0.0002 | match |
| line_length tuning gain +0.032 / +0.029 | recomputed | +0.0319 / +0.0291 | match |
| chorus_norm tuning change +0.005 / −0.063 | recomputed | +0.0053 / −0.0629 | match |

**Collapse (§8, Figure 8):**
- Config 75d4474550026cfa; failed refit seeds 1 and 2; F1 0.125 at threshold index 0.
- Fold mean 0.501 against 0.745 untuned.
- Under the budget, the same config: seeds 1 and 2 called nothing (F1 0).
- Untuned lowest seed 0.696.
- chorus_gain_norm single failed seeds: WSMIP064 fold 2 seed 3; WSMIP065 fold 3 seed 1.
- Verdict: all match.

**Refused searches:**
- locust 16 of 16 refused in all 8 folds, with no moves, so the reported value is the starting point.
- SCE WSMIP065 fold 2: 26 of 26 refused; held-out F1 0.557.
- locust fires 449–527 per hour in the busy stretch at the quiet background.
- Verdict: match.

**Table 2:**
- 8 of 8 folds at the top of the grid for all six detectors on F1 alone.
- Tops: CoactDetect and LoCo 8 s, SCE 30 s, rate+context 8 s, SPIKE-synch 2 s, locust 16 frames.
- Verdict: match.

**Figure 4 (WSMIP065 fold 0):**
- Reference rates: 10.33 and 8.0 per hour in the busy stretch; 5.407 per hour on the empty recording.
- Ceilings: 16.53, 12.8 and 8.65 per hour.
- Margin 1.6. Measured on 36 training seeds; busy stretch 300 s.
- Verdict: match.

**Figure 2 parameter counts:**
- 1,149 / 1,233 / 1,897 / 1,905, from `n_params` in 38 untuned fits per net in `fits.zip`.
- Verdict: match.
- The architecture descriptions match the code (chorus_gain_norm's learned gain and bias account for its extra parameters).

**Counts:**
- 432 inner fits per net: match.
- 1,943 and 1,938 fits: match.
- 13.2 and 12.7 hours: match, as the sum of `train_sec` with `--gpu-jobs 1` on CUDA.
- 48 seeds; 4 folds × 12 seeds (24 recordings); 72 training recordings; 96 recordings; 24 configurations per net, the same in both runs; 3 training seeds; 5 refit seeds; minimum gain 0.002.
- Verdict: all match.

**Bench (§2):**
- 33 ROIs over 2,700 s; 15 events, 5 at each level.
- 30%, 18% and 10% of ROIs, rounding to 10, 6 and 3 cells (`matlab_round`).
- Onset jitter 0.36 s as a standard deviation (`randn`); spacing at least 120 s.
- Backgrounds 0.0052 and 0.019 events per second per ROI, at p25 and p75.
- Match window 2.5 s (`TOL_SEC`); 0.1 s frames.
- Busy stretch 20–25 minutes, where every ROI's rate rises.
- Verdict: all match.

**Figure 1:**
- 15 planted events, 6 decoys, 20 CoactDetect calls at the reference settings, 0 calls in the busy stretch.
- Verdict: match (recomputed).

**Declaration and code:**
- The two declarations differ only in `recording_seeds` and `replicate`; `replicate` is absent from WSMIP064's by design.
- The code diff e8764aa→7a95e8a touches only the `--replicate` option (plus a test and the handoff). The GPUs, driver, torch and numpy versions are identical.
- The record says WSMIP064 ran at e8764aa, not the 9ba49bc given in the brief. 9ba49bc is a later status-only commit.
- `fold_check.distinct` is true with no problems in both runs.
- The empty-recording seeds (101xxx and 102xxx) do not overlap.
- Verdict: match.

**Other sources:**

| quoted | source | verdict |
|---|---|---|
| 30–36% of calls lost when a recording is shifted | `forks.md` §14: 64% and 70% of calls kept | match |
| "6 s apart" | goal-1 page | match |
| decisions on the binned settings table and the viewer | `meta.json` `coded_base` | match |
| CoactDetect settings: 2 s, 120 s, α 10⁻⁵, 8 s, 1 s | `meta.json` `coded_base` and `reference` | match |
| HANDOFF item 3, "untouched", 0.03% | slow-comodulation handoff; 83 of 264,075 events = 0.031% | match |
| 12 ROIs, 4 recordings | WSMIP064 handoff | match |
| baseline only, 2026-09-17 | `goals/README.md` decision 2 | match |
| fold defect: folds 3 and 4 (counting from 1) fitted 1000–1009; "three fits" | fold-defect todo | match |
| rehearsal +0.011 for "the leading net" | shakedown `results.json` | **mismatch** (finding 3) |

## Record of design and unit membership

- **The source of record here** is each run's `meta.json` declaration: the recording seeds, the fold rule and the per-fold budget seed lists. Units are simulated recordings; no export folder or withdrawn unit enters, except through the bench's fitted constants, which §10 discloses.
- **Folds reconcile with Figure 5:** in all 8 folds, the held-out set is exactly seeds[12h : 12h+12] and the training set has 36 seeds.
- **The quiet and busy recordings of one seed are not clones:** their planted times differ (checked for seeds 2000, 2001 and 1000).
- **No unit is withdrawn,** because none can be in a simulation.
- **Unit dependence:** the one question of this kind is that the four folds share training data within a run, and the page states that.

## Relevant paths

- `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`
- `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\tools\make_replicate_report.py`
- `%USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\tools\tune_learned_vs_coact.py` (lines 140, 1600, 1637–1667)
- `%USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\src\bugarach\simulate.py` (lines 791–808)
- `%USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\src\bugarach\score.py` (lines 44–51)
- Scratch: `<session-scratch>\scratchpad\mb\role01\` (`report.txt`, `meta.txt`, `shakedown.json`, `handoff064.md`, `handoff_slow.md`)
