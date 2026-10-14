GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 6 (methods / RTFM): round 1 findings

**Artifact:** `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md`, with its figures, `explain_coordination_share.py` and `numbers.json`.

**Sources I grounded in:**
- **Staude, Rotter & Grün 2010 (CuBIC).** Full text from Europe PMC PMC2940040, read through §5.3. What matters here:
  - Z is the population count in bins of width h, with no clipping.
  - It is a compound Poisson model with a *general* amplitude distribution f_A, so mixtures of sizes are allowed.
  - Its output is a **lower bound on correlation order**. It "avoids the direct estimation" of how big or how frequent the events are.
  - It assumes stationarity.
  - It assumes coincidences are synchronous, so jitter has to be "small compared to the applied bin size". The paper says its sensitivity to imprecise coincidences "remains to be assessed systematically".
  - The fixed and binomial closures in `solve` are therefore the tool's own; CuBIC does not supply them.
- **Kuhn, Aertsen & Rotter 2003:** not reached; one search found nothing. This needs `--need`. The README does not cite it, so nothing below depends on it.
- **Code:** `tools/measure_coordination_rates.py`, `src/bugarach/simulate.py` (`simulate_coordination`), `src/bugarach/bench.py` (`BENCH_RECORDING`, `make_recording`, `spacing_overrides`), the generator, and the stored tool run `docs/learned/runs/2026-09-23-coordination-rates/coordination_rates.json`.
- **Probes:** all run with python -c from the worktree root, importing the generator. Nothing was written to the repo. The Write tool is not granted and the heredoc hook blocks heredoc writes, so there are no saved scripts in scratch.

## Findings

Each row: location · issue · severity · suggested fix · verified against a source?

**1. §1 parenthetical ("so that a moment cut by a window edge is not lost"), §3 derivation, §4 "The reason both read low…" · HIGH**

Issue: a moment split by a window edge loses pairs and triples, and averaging the two offsets does not get them back.
- Each offset splits moments equally often, so averaging lowers the variance and leaves the bias where it was.
- I measured this on the generator's own planting (200 recordings, background near zero, 120 s spacing):

| window | f₂ captured | f₃ captured | f₂ at offset 0 | f₂ at half-window offset |
|---|---|---|---|---|
| 1 s | 0.877 | 0.811 | 0.875 | 0.879 |
| 2 s | 0.930 | 0.881 | | |
| 4 s | 0.950 | 0.897 | | |

- The cause is jitter of 0.106 s against a 1 s window, which CuBIC's "jitter small vs bin" assumption does not cover.
- **This splitting is about a third of the fixed model's error at 1 s.**
  - The size mix alone, computed analytically from 10/6/3 cells, gives fixed share −14.0%, k +37.6%, λ −37.5%, binomial −4.4%.
  - Adding the measured edge loss predicts fixed −19.3%, k about +30%, binomial about −9.4%.
  - The page observes fixed −18% (120 s only) and −21% (mixed), k +28–30%, binomial −8% and −11%.
  - The edge loss also explains why the error shrinks at wider windows.

Suggested fix:
- Say the share reads low for two reasons, the size mix and moments split by window edges.
- Drop "is not lost". Say instead that the second count reduces scatter but not the loss.
- Also flag the tool docstring's "halve the share … split" claim to whoever owns the tool.

Verified: yes.

**2. §"Few shared moments…" ("Pooling f₃/f₂ … pulls each set back to about 81% to 83%") and Figure 5B · HIGH**

Issue: pooling recentres the median but makes each recording's answer wider, not narrower. 10th / 50th / 90th percentiles of answer ÷ planted:

| moments planted | pooled, as the tool reports each recording | own (unpooled) |
|---|---|---|
| 15 | 0.76 / 0.81 / 0.86 | 0.78 / 0.81 / 0.84 |
| 6 | 0.56 / 0.81 / 0.98 | 0.73 / 0.82 / 0.91 |
| 3 | 0.52 / 0.83 / 1.03 | 0.69 / 0.87 / 1.05 |

- Figure 5B draws only the pooled *median* diamond, which hides this.
- Cause: in the 6- and 3-moment sets each recording has its own size mix. One pooled k misfits every recording, and the own ratio fits its own recording better. Fewer moments also means less size mixing, which pulls the own median toward 1.
- So "few moments make the own answer noisy" is mixed up with "few moments make the fixed model more nearly right".
- This matters for the tool as shipped: `per_recording` shares feed `remeasure_bench`, and `group_stats` pools within a group.

Suggested fix:
- Draw the pooled per-recording answers as points beside the own ones, not just a median.
- Rewrite the claim: pooling stabilises the median, and individual recordings scatter more when moment sizes differ between recordings.

Verified: yes, re-run with the generator's own `run_set` and `recovered`.

**3. §"What it cannot see", first bullet ("The shifted copies cannot remove it … the stretches no longer line up") and the "faster than about a minute" rule · HIGH**

Issue: the mechanism is misdescribed, and the page's own rule contradicts its own result.
- The shift offsets span about ±31 s, but the stretch is 300 s. In the copies the stretches still mostly line up: the surrogates keep **92%** of the stretch's f₂ (raw 1.486 against a surrogate mean of 1.370; f₃ 4.44 against 3.91; 8 seeds).
- What gets counted is the residual from the stretch's **sharp edges**, which the shifts smear.
- That residual is small next to the stretch's own f₂, and still gives a 3.7% share.
- The README's rule ("a slower one is not [counted]") would predict that a 5-minute stretch is not counted. Figure 5A shows it is.

Suggested fix: say that what is counted is fast change, and that the steps into and out of a busy stretch are fast change even when the stretch is long. Restate the rule in terms of how fast the rate changes, not how long the change lasts.

Verified: yes.

**4. §"What it cannot see", second bullet ("A change that slow survives the sliding … so the copies carry it too and it is subtracted") · MEDIUM**

Issue: the ramp test does not exercise the surrogate subtraction.
- Before any subtraction, the ramp's raw f₂ is 0.0014, identical to the steady null's 0.0014, and its raw f₃ is −0.0014.
- A linear ramp gives an unskewed rate distribution, so f₃ ≈ 0 by construction and `solve` declines with or without surrogates.

The same bullet calls the outcome "reported as no coordination". The steady row's identical outcome (`solve` declines, NaN) is called "no answer at all, not a small one". Note that the tool's `summarize` treats NaN as zero in the background calculation.

Suggested fix:
- Either show the unsubtracted value beside it, or use a skewed slow modulation (for example a slow bump) so the subtraction has something to do.
- Describe both rows the same way: the tool gives no answer.

Verified: yes.

**5. §"The simulated recordings" ("They copy the fast stream's bench") and §"How we know it works" ("Figure 3 is that check") · MEDIUM**

Issue: the generator leaves out two parts of the bench that the tool's own calibration includes.
- **Per-cell clumping in time.** `BENCH_RECORDING` sets `bg_burst_shape=(1.770, 1.439)` over 300 s and 60 s bins. The generator's background is homogeneous Poisson. Clumping gives each cell a nonzero f₂ of its own, which the surrogates have to remove, so the generator's test is easier than the tool's.
- **Six distractors** (`n_distractors=6`, `distractor_frac=0.18`, so 6 cells each). The tool's `truth()` counts them as coordinated, so the size mix it is scored against changes.
- The tool's own stored calibration (2026-09-23 run, fast bench) is not the page's:

| window | fixed, tool | binomial, tool | page (fixed / binomial, mixed set) |
|---|---|---|---|
| 1 s | −16.5% | −4.7% | −21% / −11% |
| 2 s | −13.9% | −2.2% | |
| 4 s | −11.5% | +0.5% | |

- So "every fixed-model share here reads low by about a fifth … take [it] as an underestimate of that size" is a number about the page's own recordings. The tool's calibration says about a sixth at 1 s.
- Smaller point: the generator raises each cell *to* 0.127/s in the stretch. The bench's hot window *adds* 0.127/s.

Suggested fix:
- Say what the generator leaves out of the bench.
- Quote the tool's own calibration numbers beside the page's, after checking that the run matches the current bench constants.
- Call Figure 3 "the same check, on this page's recordings", not "that check".

Verified: yes, from code and the stored JSON. Whether the 2026-09-23 run predates any change to the bench constants is not verified.

**6. §1 ("For cells with independent onsets, both are zero on average, whatever each cell's rate") and §2 (why the copies are needed) · MEDIUM**

Issue:
- Zero holds only when each cell's count is Poisson, meaning a constant rate (the tool's docstring says "constant rates", and CuBIC assumes Poisson).
- Independent cells whose own trains are bursty or refractory give nonzero f₂ and f₃. The bench's background is bursty.
- §2 gives field-wide drift as the only reason for the copies. Each cell's own clustering is the other reason, and the copies handle it because each cell keeps its own train.

Suggested fix: say "independent cells, each at a steady rate". In §2, add that the copies also cancel each cell's own clustering.

Verified: yes (CuBIC model, tool docstring, bench code).

**7. §3 ("dividing that by the cell's event rate") and Terms ("of all a cell's onsets, the fraction…") · LOW**

Issue: the tool divides λk/N by the **slice-mean** per-cell rate (`share / raw`, where raw is the mean count over cells divided by T). The result is a population share: coordinated onsets over all onsets. It is not any one cell's fraction, and with gamma-heterogeneous rates the two differ greatly between cells.

Suggested fix: write "divided by the average cell's event rate", and define the share as the fraction of all onsets in the recording.

Verified: yes.

**8. §1 ("a shared moment only moves onsets in time, it does not add any") · LOW**

Issue: in this generator, and in `simulate_coordination`, planted onsets are *added* on top of the background. Figure 2's means match because the copy is a shift of the same onsets, not because sharing preserves the rate.

Suggested fix: write "sliding each cell's onsets does not change how many there are, so the copy has the same mean".

Verified: yes.

**9. §"Few shared moments…", the background-lowering sentence followed by "Figure 5B's recordings are all at the quiet background, with every moment 120 s or more…" · LOW**

Issue: the lowered-background set (`low`, run with the default arguments, so close and medium pairs are present) uses the **mixed** schedule. Its "79% at the quiet level" is therefore not the same set as Figure 5B's 15-moment quiet set (120 s only, 81%). A reader sees two different answers for "quiet, 15 moments".

Suggested fix: run the lowered-background set on the 120 s schedule, or say it is the mixed set.

Verified: yes (`main()` and numbers.json).

## Checked and sound

- **(a) Formulas.** The f₂ and f₃ expressions are the correct second and third factorial cumulants, and match `factorial_cumulants`. The fixed-k result, f₂ = λwk(k−1) and f₃ = λwk(k−1)(k−2), is correct for moments that fall whole inside a window: the factorial cumulants of a compound Poisson count are λw·E[(k)ₙ], consistent with CuBIC's compound Poisson model. The only problem is the split-window caveat in finding 1. Verified: yes.
- **(b) Planting.**
  - k = round(p·N) gives 10, 6 and 3, as `matlab_round` does.
  - Each cell's onsets are unique per frame, with planted onsets winning a collision. This matches the tool's `_frames` and its `np.unique`.
  - Jitter is Gaussian with sd 0.106 s (`CAL_JITTER`).
  - The gamma rates have the bench's mean and shape.
  - The ramp-by-thinning is correct: density runs from a to 3a with mean r.
  - The departures are listed in finding 5.
- **(c) How the tool is called.**
  - `per_recording` is pooled over all 48 quiet+busy recordings, as `calibrate` does.
  - Each recording's surrogate RNG is RandomState(seed), as in the tool.
  - The truth basis n_pl/(n_bg+n_pl), compared against share/rate, is algebraically the same as the tool's Σk/(N·T) compared against share_hz, apart from frame collisions, which are negligible.
  - The one difference is distractors (finding 5). Verified: yes.
- **(d) `solve()` unpooled** is exactly `per_recording` on a single recording: `pooled_ratio` reduces to f₃/f₂, and the NaN conditions are identical. It is a fair stand-in. The problem is what Figure 5B shows of the pooled answers (finding 2). Verified: yes.
- **(e) The size-mix explanation** is correct in direction: f₃/f₂ is weighted by k(k−1), so it leans toward the large moments, k reads high and λ reads low. It is incomplete; see finding 1.
- **Figure 2's numbers:** excess f₂ = 0.214 and excess f₃ = 1.369 match numbers.json.

## Sources

- [CuBIC, Staude, Rotter & Grün 2010 (Europe PMC full text)](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2940040/fullTextXML)
- [PMC2940040](https://pmc.ncbi.nlm.nih.gov/articles/PMC2940040)
- Kuhn, Aertsen & Rotter 2003: not obtained; needs `--need`.
