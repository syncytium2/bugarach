GRANT 4 ok — Read, Grep, Glob, Bash

Reviewed the report against every shipped data file, both figures as images, and the four tools. **20 findings, 6 blocking.** Artifact: `docs/learned/tube_self_supervised/README.md`

---

## Blocking

**1 · "the architecture that leads the bake-off is last of the four supervised models" (line 211) — false against the cited file.**
`line` is **third of four**, not last. From `real_compare/summary.json`, share of each reference's events caught: tube_guard 0.854/0.872 · tube 0.829/0.802 · **line 0.774/0.758** · line_length 0.745/0.688. Chance-corrected the ordering is identical (κ 0.836 · 0.800 · 0.744 · 0.693). The sentence quotes only tube and line — the two rows that make "last" readable — and omits the two that refute it. **Fix:** "third of four, ahead of its own ablation and behind both tube builds," and print all four rows. *Verified: yes.*

**2 · The untrained control does work, and the paragraph that dismisses it quotes two of four models (lines 170–176).**
"The rate-limited label-free threshold collapses it to 0.07 and 0.00, which is the label-free rule behaving correctly… there is no working baseline in it." From `training/results.jsonl`, untrained at ≤2 events/10 min: tube **0.071**, line **0.000**, tube_guard **0.099**, **line_length 0.272**. Untrained `line_length` is not collapsed — recall 0.264, precision 0.320, **30.2 detections per fold**, not a model that is on everywhere. Its 0.272 beats *nine of the sixteen* trained label-free cells, including trained `tube` at sim-*J*20 (0.124) and trained `line_length` at sim-*J*20 (0.211). At oracle, untrained `tube` scores **0.507**, above every one of the sixteen trained cells. The escape hatch "there is no working baseline in it" is contradicted by the run's own file, and it is the hatch the report's third headline depends on. **Fix:** print all four untrained cells at both thresholds; restate as "training against rigid shift did not beat random initialisation at the label-free operating point." *Verified: yes.*

**3 · The 7.9× fitting cost is charged to the second sensor; the ablation costs the same (lines 94–95, 247).**
The paragraph's subject is "That is what the second sensor did… It is also 7.9 times slower to fit (51.4 s against `tube`'s 6.5 s)", and item 1 of *What waits on Tony* repeats it as "fitting is eight times slower" **on the against-it side of the orientation decision**. `line_bakeoff/bakeoff.json`: `line` train 51.41 s, **`line_length` train 50.71 s**, `tube` 6.48 s. The second sensor costs **1.4 %**, not 7.9×; detect 0.152 s vs 0.148 s, **2.7 %**, not 6.3×. The 7.9× is the cost of the `line` family over `tube` and belongs in the family comparison. As written it is a wrong number on the decision line Tony is being asked to rule on. *Verified: yes.*

**4 · "most of what these models learned needs no cross-ROI structure at all" (line 64) / "Most of that last number needs no coordination" (line 180) — the pooled trace IS the co-activity count.**
`tools/tube_aggregate_leak.py:13` defines the channel: *"binary raster, each onset widened ±1 frame, **mean over ROIs**"*. That is the share of the field lit per frame — verbatim the quantity `line` is built to compute (`src/bugarach/learn/nets/line.py`: *"The votes are averaged over ROIs, so the output is the **share of the field that is lit**"*). A classifier on that trace is reading cross-ROI co-activity; what it is *not* reading is ROI identity or pairwise structure. The correct claim is "no **pairwise or identity** structure is needed — the co-activity count alone suffices," which is a different and much less alarming result. As written the report tells the lead its detectors learned nothing about coordination, using as evidence the one channel that measures coordination. **Fix:** restate; and note the claim contradicts the architecture section two screens earlier. *Verified: yes.*

**5 · The gap the word "most" quantifies does not exist at the stated confidence.**
Models: 0.73–0.76. Aggregate channel: 0.66–0.69 — but `aggregate_leak/results.json` carries the CIs and the report drops them. Fast *J*=10: **0.688 [0.634, 0.734]**; *J*=20: **0.664 [0.621, 0.721]** (mouse-grouped, n_boot 1000). The upper bounds reach the models' own scores. The data are consistent with the aggregate channel explaining **all** of the models' separation, and with the models doing no better than it. "Most" is an unquantified fraction of a difference that is not resolved. **Fix:** print the CIs and say "the aggregate channel is not separable from the models." *Verified: yes.*

**6 · Figure 1 Panel B: the two largest numbers in the table have denominators indistinguishable from zero.**
`probe/line_vs_fuzz.json`: the 3.90 and 5.05 ratios at plant 4 are `line` 10.29 ÷ **burst 2.64 ± 3.37** and `line_length` 11.50 ÷ **burst 2.28 ± 2.19** (n = 12 fields). Both denominators are within one SD of 0. The figure's most dramatic feature — the collapse from ~4–5 at plant 4 to ~1.6–2.0 at plant 8 — is a denominator crossing zero, not a property of the sensors. The report quotes a single spread ("±4.4 on a mean of 18.5") taken from the *largest-signal* cell of twelve and lets it stand for the whole panel. **Fix:** plot the differences with CIs, or drop plant 4 from the headline. *Verified: yes.*

---

## Major

**7 · The orientation claim is one cell of six, selected, and unbounded (lines 115–119).**
"The orientation channels show up **only at the largest plant** (1.32 against 1.14)." Of three plant sizes × two comparisons, the claim rests on one, and the report itself says the other five go the wrong way or tie. 1.319 vs 1.139 is `line` 18.50±4.38 ÷ wave 14.02±4.50 against `line_length` 17.56±4.89 ÷ 15.42±4.68 — no per-field paired values are stored, so it cannot be tested from the shipped file, and on the unpaired numbers it is under 1 SD. One training seed. This is the only positive evidence in the report for the sensor whose default state Tony is being asked to rule on. *Verified: yes (the file holds means and SDs only — no pairing).*

**8 · The probe's own named comparison is computed and not shown — and it is the unflattering one.**
The tool is `probe_line_vs_fuzz.py`; `fuzz` is the direct test of the "temporal concentration" the ⚠ at line 121 says these channels measure. Figure 1B plots ÷burst and ÷wave and omits ÷fuzz. The stored line÷fuzz ratios: `line` 1.27 / 1.44 / 1.99, `line_length` 1.24 / 1.31 / 1.75, `tube` 1.22 / 1.08 / 1.43. At plant 4 all three models barely separate a one-frame line from the same onsets spread over 2.9 s. **Fix:** show all three ratios or say why fuzz was dropped. *Verified: yes.*

**9 · "Every architecture lands at 0.40–0.49 with an oracle threshold" (line 61) is contradicted by the table directly below it.**
The table at lines 159–164 contains **0.338** (tube_guard, sim *J*10) and **0.382** (tube, sim *J*20). The full sixteen-cell range is 0.338–0.488. *Verified: yes.*

**10 · The on-real ranges are wrong at both ends (lines 212–214).**
"catch 47–72 %" — actual **26.8–77.4 %** (line_length *J*20 → loco 0.268; tube_guard *J*10 → loco 0.774). "place 19–30 % of their own events" — actual **15.8–30.5 %**. "against chance rates of 4–13 %" pairs the model→reference shares with a chance range that belongs to the **other** direction: chance for model→reference is 3.4–6.3 %; 8.4–13.3 % is reference→model. *Verified: yes.*

**11 · The real-recording "catch" metric has no precision partner, and the stated ceiling is exceeded without comment.**
"The two references agree with each other 0.71–0.77, so that is the ceiling any model is measured against" — then three of four supervised models sit **above** it (0.802–0.872). They fire 4.2–5.0 events/10 min against the references' 2.57–2.70, i.e. 5.4× as many events as LoCo in absolute count (2313 vs 429). Catching more of a reference by firing more is exactly the promiscuity the bake-off section warns about ("a detector can buy recall with promiscuity") and then does not apply here. The reverse direction is in the file (tube→coact **0.473**, line→coact 0.444) and is reported for the rigid-shift models but not for the supervised ones — the flattering direction only for the arm being promoted. **Fix:** report both directions for every arm, or a rate-matched comparison. *Verified: yes.*

**12 · The `bake-off threshold` arm exists for all four supervised models and is absent from the report.**
`real_compare/summary.json` carries eight supervised arms; the table shows four. The omitted four fire 5.2–6.7 events/10 min and have *lower* participation (tube 0.781 vs 0.803 at ±2 frames) — i.e. the reported threshold is the better-looking of the two the run produced, with no statement that a second exists. *Verified: yes.*

**13 · "random times in the same recordings — 1, 0.21–0.27 | 1, 0.21–0.27": the ±2-frame column holds the ±1-second numbers.**
At ±2 frames the random share ≥3 ROIs is **0.066–0.184** (per arm); 0.186–0.271 is the ±1 s column. Putting the wider-window chance rate in the narrow-window column inflates the stated baseline 2–4× and makes the rigid-shift rows' 0.14 and 0.22 read as *below* chance when against their own ±2-frame randoms (0.103, 0.105) they are at 1.3–2.1×. *Verified: yes.*

**14 · The null on the lab fast stream has no demonstrated power on that stream.**
"that control reads at chance, 0.49–0.53… out to 40 s" is offered as evidence of no per-ROI leak. In `../rigid_shift_look/controls/lab/results.json` the same classifier reads **0.486–0.505 for rigid shift too**, at every *J* from 1.6 s to 40 s — it never rises above chance on lab fast for *either* surrogate. It does ring on Cossart (0.586 at *J*=10) and lab slow (0.567 at 44.8 s), but that is a different preparation with 566 ROIs. The `freeze_half` graded control (line 45) demonstrates power for the **destruction** measure, not for this classifier. On the stream the whole label-free experiment ran on, the shared-offset control is a check that has never been shown able to fail. **Fix:** either state it as "not detectable by this classifier on lab fast", or run the positive control (plant a known per-ROI rate change and show the number moves). *Verified: yes.*

**15 · "Statistics are pooled over events, not clustered by mouse" (line 237) is wrong for two of the four analyses it appears to cover.**
`tools/tube_aggregate_leak.py` passes `mice` as the grouping for both folds and the refitting bootstrap; `controls/lab/results.json` ships `by_mouse`, `by_slice` **and** `by_group` (DI n=10 mice, MALE n=12, ORX n=12, OVX n=10) with CIs. The per-group breakdown the caveat says is not given **already exists in the sibling artifact the report links**. A global caveat that understates the work will be read as "none of this is mouse-clustered." **Fix:** scope the caveat to `real_compare/`, and surface the by-group table that exists. *Verified: yes.*

**16 · The picture says training made things worse; the prose never does.**
Figure 2 Panel A: the `untrained` bar for tube sits at ~0.51, **above all four of its own trained arms** (0.41 / 0.38 / 0.43 / 0.49) and above most other trained bars in the panel. A reader looking at the image sees the second-highest group in the figure labelled "not a baseline" in pink. The prose reports the trained arms against *supervised* only. Whatever the shaded band's disclaimer, the figure is making a claim the text declines to address. *Verified: yes — matches finding 2.*

---

## Minor

**17 · "Two of these rows are this project's detection layer wrapped around someone else's measure" (line 98) — three are then named:** SPIKE-synch, locust, binned SCE. *Verified: yes.*

**18 · "by the looser cut of 0.6 used in the figure, 1 to 4 did" (line 168) — actual range is 1 to 5** (ssl_sim *J*20 `line`: 5 of 12). *Verified: yes.*

**19 · The edge-enrichment constant is unjustified and is not the model's.** "the difference-of-Gaussians half-width of **12.8 s**" is `max_center_frames` 128 × dt — the architectural *cap*, never a fitted value. The fitted centre widths in `training/results.jsonl` are **0.058–1.66 s** across every arm (supervised `line`: 0.15/0.20/0.35/0.81 s). The edge window is 13–90× the largest scale any model actually fitted, and no derivation is given. Separately, none of the edge numbers (2.7–4.6 %, 4.9–6.4 %, 0.8 %, 2.1 %, "0 of 429") appears in any shipped file or in `tube_ssl_real_compare.py` — the only ⚠ escalated to "an edge artefact is not excluded, it is indicated" is the one number a reader cannot reproduce from the folder or the provenance table. *Verified: yes.*

**20 · "At the event itself, half the label-free calls contain no ROI onset at all" (line 207) inverts against the table above it.** The table's four `label-free` rows are the *supervised* models at the label-free threshold, median 4–5 ROIs. The rows with median 0 are `line vs rigid shift`. The sentence uses "label-free" for the rigid-shift-trained models and the table uses it for a threshold rule; on the table's own vocabulary the sentence is false. **Fix:** name the arm. *Verified: yes.*

---

## Two more where the picture and the prose part company

- **Figure 1 Panel A is ordered by score inside every family**, top row first, `line` at the top — line 71 says "Rows are grouped by family and **not** ordered by score", and the banner invokes the MILESTONES ruling *"a table of performance, not a ranking."* The eye reads a ranking. Within learned: 0.713 → 0.110 monotone; within hand-written: 0.651 → 0.267 monotone.
- **Figure 1's right panel carries no `B`.** The prose calls it "Panel B" three times. (Figure 2 labels A/B/C correctly.) Flagging as a prose/picture mismatch; the mechanical sweep is role 10's.

## What the picture supports that the prose undersells

Panel A's bars are the honest artifact in this report: `line`'s 0.64–0.81 whisker contains `tube`, `tube_guard`, `CoactDetect` and `LoCo` entirely. The paired per-fold arithmetic agrees — `line` − `line_length` t(3)=1.39, `line` − `tube` t(3)=1.45, **`line` − `CoactDetect` +0.063 ± 0.096, t(3)=1.31**, and `line_length` − `CoactDetect` **+0.005, t(3)=0.34**. Fold 2 carries all of it (`line` 0.811 vs CoactDetect 0.606; drop that fold and the margin over CoactDetect is +0.015). The report applies "the mean carried by one fold" to the ablation comparison and not to the comparison that decides whether the learned family is worth having at all: **the ablation is statistically indistinguishable from the existing hand-written detector.** The section heading "The counting architecture is worth having" is not supported at that strength by anything in the folder.
