GRANT 4 ok — Read, Grep, Glob, Bash

Role 4, Reviewer 2 (adversarial). Artifact: `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md` and its six PNGs. I opened all six PNGs and read the pictures. I checked every quoted number in the prose against `numbers.json`, read the generator, `tools/measure_coordination_rates.py` and FOUNDATIONS §9 and §11, and re-ran the generator's Figure 1 and Figure 2 recordings in the venv to check two claims (inline `python -c`; I wrote no files). I edited nothing.

Each finding gives: location · issue · severity · suggested fix · verified against a source (yes/no).

**F1** · "What else it counts", first bullet (README l.175–182), against Figure 5A and 5B
- **Issue:** The figure contradicts the stated mechanism.
  - The text says the stretch "is counted most when it is short" and that "it is how fast the rate changes that matters, not how long the change lasts."
  - In Figure 5A every point has the same sharp edges, yet the reading goes from 1.2% to 8.2% depending only on length. The curve is also not monotone: the shortest stretch (10 s) reads 3.7%, below 30 s (7.9%) and 1 m (8.2%). The prose skips the 10 s and 2 m points.
  - The same 5-minute, 28× stretch reads 3.0% with sharp edges (5A) and 2.8% with the bench's 30 s ramps (5B). So slowing the edges by 30 s barely moves it, which is the opposite of what the bolded sentence predicts.
- **Severity:** blocking. The picture refutes the sentence the section is built on.
- **Fix:** Restate it as what was measured: length matters, it peaks at 30 s to 1 min, and a 30 s ramp is no better than a sharp edge. Drop or properly test the "edges" mechanism, for example with a ramp-duration sweep at a fixed length.
- **Verified:** yes (`numbers.json` fig 5 A: 10 s 0.037, 30 s 0.079, 60 s 0.082, 120 s 0.058, 300 s 0.030, 900 s 0.012; B 28x: 0.028).

**F2** · "The question" (l.38–40) together with "What else it counts" and Figure 5
- **Issue:** The page says this is the measure treatment results will be read through, and Figure 5 shows that a field-wide rise in rate, with nothing planted, is reported as up to about 8% coordinated (90th percentile 11.8%). That is the same size as the planted shares in Figure 3 (about 3–28%). The page never connects the two.
  - FOUNDATIONS §9 says senktide "raises event frequency and the GCaMP6f background over time."
  - A drug's wash-in, or any rate step inside a treatment window, is exactly the confound in Figure 5.
  - The tool's own `CAL_NO_PROBE` records a +43% share error (FAIL) when the bench's elevated-rate stretch is present.
- **Severity:** blocking, for the stated use.
- **Fix:** Add a caveat in "The question" or "What waits": a treatment window that holds a change in the field's rate (wash-in, or a rise under senktide) will read as more coordination. Say which part of a treatment window must be excluded, or that this has not yet been established.
- **Verified:** yes (FOUNDATIONS §9 and §11; tool l.245–272).

**F3** · "The check, and the two models" (l.106–126, "All three medians pass")
- **Issue:** The built-in check passes only because the case it failed on was taken out, and the explainer's body does not say so.
  - The tool's calibration (`_sim`, l.406–413) turns off the bench's elevated-rate stretch.
  - `CAL_NO_PROBE` records that with the stretch in, the fast calibration failed at +43% share error, 1.7× the tolerance.
  - The explainer mentions this only as a symbol name under "For developers."
  - A reader of "all three medians pass" is not told that the check cannot see the confound in F2.
  - The ±25% band (`CAL_TOL`) is given with no reason (the tool gives none either), and it passes an estimator with a known 16–18% bias.
- **Severity:** major.
- **Fix:** One sentence in the body: the check runs without the bench's elevated-rate stretch, because with it the check fails (share +43%). Justify ±25%, or say that it is unjustified.
- **Verified:** yes.

**F4** · "Why the fixed model reads low" and its adoption rationale (l.137–140)
- **Issue:** The stated reason contradicts itself. "The tool adopts the fixed model because the bench plants a fixed number of cells at each level, so it is the model that matches how the bench was built."
  - The bench plants three different sizes (10, 6 and 3 cells; `BENCH_RECORDING participation=(0.30, 0.203, 0.10)`). Its moments are therefore not all one size, which is exactly the case where the fixed model reads 16–18% low.
  - On the bench itself (Figure 3C) the binomial model is closer: 2% low against 16% low.
  - So the adopted model matches neither the bench's structure nor its accuracy.
  - Separately, the tool's docstring says the two models "bracket" the answer. Figures 3A and 3C show both models reading low, so that claim in the source is also refuted (a source finding for the main thread).
- **Severity:** major.
- **Fix:** State plainly that the bench plants three sizes, so the fixed model's assumption does not hold on it, and give the real reason for adopting it, or flag that the choice is open. Separately, fix "bracket" in the tool docstring (l.36, l.175).
- **Verified:** yes (tool l.34–37, l.177–178, l.274–278; `numbers.json` fig 3).

**F5** · Treatment use against the size and interval biases (l.128–140, l.157–167; FOUNDATIONS §11)
- **Issue:** The bias depends on things a treatment could change, so a difference between baseline and treatment can be produced by the bias alone. The page says this only as "read as an underestimate."
  - The share's bias moves from 5% to 18% (up to 23% in Figure 4) with how much moment sizes vary.
  - §11's confirmed exception reports the moment rate and the share of the field per moment under treatment. The page itself says those two read 26–69% high and 33–55% low depending on how far apart moments are, and that "they are not checked against a tolerance."
  - So a baseline-to-treatment difference in these numbers can be pure bias if the treatment changes how much moment sizes vary or how far apart moments are.
- **Severity:** major.
- **Fix:** Add the comparative caveat: a change of up to about 13 points in the share, and of tens of percent in participants per moment and moments per minute, can come from changes in size variation or spacing with no change in coordination. Name participants and moment rate as unvalidated for comparisons between conditions.
- **Verified:** yes (`numbers.json` fig 3 and 4; FOUNDATIONS §11).

**F6** · "How far one recording strays" (l.204–207, "Pooling steadies the median, not the single recording") and l.100–102
- **Issue:** Figure 6 does not support pooling, and nothing on the page shows that it helps.
  - Pooled medians are equal or lower than the unpooled ones: 0.82 vs 0.83, 0.79 vs 0.83, 0.83 vs 0.87, 0.81 vs 0.81, 0.81 vs 0.81.
  - With 6 moments, the pooled spread is wider (middle 80% 0.59–0.98) than the unpooled spread (0.67–0.95).
  - The stated reason, "one recording's f3 is noisy," is not shown to be cured. `no_answer` is 0 for the unpooled answers in every set, so pooling is not rescuing missing answers either.
  - The page also does not say what pooling set the treatment comparison will use. The tool pools within the set passed in (`group_stats`). Pooling baseline and treatment together would force the same k on both and push any change in moment size into λ.
- **Severity:** major.
- **Fix:** Either show what pooling buys (on what quantity, and by how much) or state that it was not shown to help here. Say what the pooling set must be for treatment pairs, and why.
- **Verified:** yes (`numbers.json` fig 6; tool l.281–304, l.449–451).

**F7** · Figure 6 and "The simulated recordings" (l.201–203, l.218–231)
- **Issue:** The headline per-recording spread (15 moments: 0.78–0.86) comes from the most favourable case. Real recordings are nearer the worst one.
  - The page itself says real recordings hold "about 7 events per 45 minutes" (bench, Figure 3C). That is the "6 moments" column: middle 80% 0.59–0.98, single recordings 0.53–1.07.
  - Real baselines can be as short as 15 minutes (`bench.MIN_BASELINE_SEC = 900`). At that rate that is about 2–3 moments, which is the "3 moments" column.
  - All simulations are 45 minutes.
  - §11 pairs each treatment window with its own baseline, so it is the spread for a single recording that matters.
- **Severity:** major.
- **Fix:** Say which column real recordings resemble, and that real windows may be shorter than the simulations. Quote the 6-moment and 3-moment spreads as the realistic ones.
- **Verified:** partly. The bench events-per-45-min figure is from the page, `MIN_BASELINE_SEC` from `bench.py` l.288. The real window lengths I could not check, because I did not read real data.

**F8** · Figure 5 caption and "What else it counts" (l.19, l.172–194)
- **Issue:** It is not disclosed that the shares reported for "nothing planted" recordings were computed with f3/f2 pooled over a run of 24 recordings that do have planted moments (`in_run(nulls, run)` with `run=quiet_run`, generator l.468, 473, 493).
  - The 8%, 3.0% and 1.2% figures, and the null −0.4% to +0.6%, depend on the k borrowed from those other recordings.
  - A reader takes "nothing planted" to mean the recording was analysed as found.
  - Only l.193–194 hints at this.
- **Severity:** major.
- **Fix:** State it in the caption and the text: each test recording is analysed as one recording in a run of 24 that hold planted moments. Explain why: on its own, f3 would not be above zero and the tool would give no answer.
- **Verified:** yes.

**F9** · Figure 2B and l.95–96 ("≈ 8.1 cells per moment")
- **Issue:** The worked example reads 27% high and the reader is not told.
  - The recording (busy, seed 3) plants 5 moments each of 10, 6 and 3 cells, a mean of 6.3.
  - 8.1 is close to the size-weighted value, 8.7. A cold reader takes 8.1 as the right answer.
- **Severity:** major. This is a worked example of the method with its error hidden.
- **Fix:** Add "(planted: 10, 6 and 3 cells, average 6.3; why it reads high is under *Why the fixed model reads low*)" to the text and to the panel annotation.
- **Verified:** yes (re-ran `recording(3, BUSY)`: ks mean 6.33, size-weighted 8.71).

**F10** · Section 2, l.85–86 ("every cell has the same number of ticks")
- **Issue:** False for the 5 minutes shown. In the Figure 1 window, 9 of 32 cells have a different number of ticks in D than in B, and the totals are 102 vs 96. It holds only over the whole recording, because the shifts move onsets into and out of view.
- **Severity:** minor. It is a factual error about the figure, but the fix is trivial.
- **Fix:** Change to "every cell keeps the same number of onsets over the whole recording; in this 5-minute view some move in or out."
- **Verified:** yes (re-ran seed 13 with surrogate seed 11).

**F11** · Figure 1C against the planted lane
- **Issue:** The picture shows something the text never mentions. The 10-cell moment of the medium pair (planted at 1825.0 s, exactly on a 1-s window edge) appears in C as two bars, 4 and 6, not one bar of 10. This is the window-edge split the text describes in l.130–132, sitting unexplained in the first figure. A reader looking for "a moment of 10 cells puts 10 onsets in one window" (l.68) finds a 6.
  - Separately, the window was chosen to maximise the sizes of the paired moments (generator l.267). The text discloses only the "holds all three kinds" part of that selection.
- **Severity:** minor.
- **Fix:** Point at it in the caption or text as the window-edge split. Disclose that the window was picked as the most vivid.
- **Verified:** yes.

**F12** · Figure 5B text (l.185) "three quarters of all the recording's onsets fall inside the stretch"
- **Issue:** The quantity is not what the sentence says. It is `added·span/(added·span + quiet·T)`: the share of onsets the stretch added, which leaves out the background onsets inside the stretch and the ramps. The share that actually falls inside is about 0.78 at 28×, and about 0.19 rather than 0.10 at 2×.
- **Severity:** minor.
- **Fix:** Say "three quarters of all onsets are extra ones the stretch added," or compute the fraction inside.
- **Verified:** yes (generator l.600–602, and checked arithmetically).

**F13** · Figure 6 design (l.201–210)
- **Issue:** Each "fewer moments" step also changes the planted share, so the two effects cannot be told apart. The planted shares are 20% (15 moments), 8.5% (6), 4.9% (3), 50% (¼ quiet) and 6.8% (busy).
  - The causal reading "fewer moments, more spread" and "busier background adds spread because moments are a smaller part" is not isolated.
  - Lowering the rate makes moments a larger part (50%), yet does not reduce spread, which undercuts the stated reason.
- **Severity:** minor.
- **Fix:** Give the planted share under each column, and soften the causal wording to "described."
- **Verified:** yes (`numbers.json` fig 6, `planted_share_median`).

**F14** · Constants and ranges defined too loosely
- **Issue:**
  - (a) l.180 and l.191: "from −0.4% to +0.6%" is the minimum to maximum of 24 recordings, not stated, while the figure's band is the 10th–90th percentile (−0.3% to +0.3%).
  - (b) "scattered by 0.106 s" (l.224) is a standard deviation, not stated. Its justification ("the jitter the tool's own check uses") is circular; the source is the correlogram's measured value (tool l.110).
  - (c) 20 shifted copies, and "at least two windows apart," have no reason given on the page. The tool has one for the spacing: 35% of pairs were lost otherwise.
  - (d) l.133–134: "ranges from 5% to 18%" is contradicted by Figure 4 on the same page (21% and 23%).
  - (e) l.188: "removes 99%" is a ratio of medians, not paired per recording.
- **Severity:** minor.
- **Fix:** Label (a) as lowest to highest. Say "standard deviation" and give the source for (b). Give one-line reasons for (c). Widen (d) to 5–23%, or scope it to Figure 3. Say how (e) is computed.
- **Verified:** yes.

**F15** · l.190 "Each cell's own clumping is removed in the same way (Figure 5C, the steady rows)"
- **Issue:** At the quiet background only 52% of raw f₂ is removed (`steady, quiet`, `removed` 0.52). It is 99.4% only at 13× quiet. "In the same way" overstates the quiet case. The figure hides it: at quiet the open and filled points sit on top of each other.
- **Severity:** minor.
- **Fix:** Scope the claim to the busy row, or give both numbers.
- **Verified:** yes.

**Checked and found no defect**
- Every other quoted number against `numbers.json`: Figure 3 medians and the 0.67–1.12 range; all Figure 4 ranges; Figure 6 middle-80% ranges.
- The f₂/f₃ formulas and k − 2 against the tool.
- "At most about half a minute": offsets are a permutation of 32 × 2 s, centred, so ±32 s.
- The slow-ramp null in Figure 5C has the power to fail: raw f₂ is clearly nonzero at 13× before subtraction, and the quiet case's lack of power is disclosed.
- No real recording is quoted; the contamination stop is cited.
- Group ordering: no groups appear.

Paths
- `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md`
- `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\explain_coordination_share.py` (l.267, 468–502, 600–602)
- `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\numbers.json`
- `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\tools\measure_coordination_rates.py` (l.34–37, 105, 245–278, 281–304, 406–413, 449–451)
- `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\FOUNDATIONS.md` §9 (senktide), §11 (the exception)
- `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\src\bugarach\bench.py` l.288 (`MIN_BASELINE_SEC`)
