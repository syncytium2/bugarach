GRANT 4 MISMATCH — missing Grep, Glob; holds Read, Bash (no forbidden editing tools). I substituted `grep`/`find` via Bash, so no check was skipped; the gap is in the tool grant, not in coverage.

Reviewed: the README, both PNGs (opened and read, not captioned), `line_bakeoff/bakeoff.json`, `training/results.jsonl` + `meta.json`, `real_compare/summary.json` + `events.json`, `probe/line_vs_fuzz.json`, `aggregate_leak/results.json` + `meta.json`, `../rigid_shift_look/controls/{lab,cossart}/`, and `line.py`, `line_length.py`, `fair_bakeoff.py`, `tube_self_supervised.py`, `tube_ssl_real_compare.py`, `probe_line_vs_fuzz.py`, `make_tube_ssl_figure.py`.

---

## BLOCKING

**B1 · "What holds", line 28–34 · Claim (a) has no rigid-shift evidence at all on the only stream the report uses.**
The destruction control was run with `rigid_shift@J` variants **only on Cossart**. `controls/lab/results.json`'s destruction block carries `['homogeneous_resample', 'freeze_half', 'do_nothing']` in all six entries — no rigid shift, fast or slow. And on the lab fast stream the leak classifier reads rigid shift at **0.4966–0.5043 at every J tested** (1.6 s through 40 s; at *J* = 10 s it is 0.4991, at 20 s 0.4980) — i.e. no rise to attribute to anything. The rise the sentence explains exists only on the lab **slow** stream (0.550/0.561 at 22.4/44.8 s) and on Cossart (0.536–0.599). So the report's phrasing *"including on the Cossart folder"* inverts the record: Cossart is not an additional confirmation, it is the **only** folder where rigid shift was shown to destroy planted coordination, and the fast stream — which carries every label-free fit, every checkpoint and the entire real-recording section — has a leak test returning chance and no destruction test. *Fix:* restate as "rigid shift is a sound teacher **on Cossart** at that folder's participation; on the lab fast stream neither side of the control has been run with rigid shift, and the leak classifier cannot separate real from rigid-shifted there at any *J*." Then say what that implies for Figures 1 and 2. **Verified: yes.**

**B2 · Figure 2 panel C, "real vs rigid shift (what it learned)" · The report's own `aggregate_leak/` folder holds the baseline that removes most of this result, and the report never quotes it.**
`aggregate_leak/results.json`, lab fast stream: a classifier built from **aggregate-channel features only** (pooled-trace mean/sd/p99 and centre–surround responses of the pooled trace — nothing that reads cross-ROI alignment) separates real from rigid-shifted at **0.681 / 0.688 / 0.664 / 0.686** at *J* = 5/10/20/40 s. The trained models in panel C reach 0.73–0.77 on the same comparison. Almost the whole of "what it learned" is available without any cross-ROI structure. Two other rows in the same file sharpen it: `real_vs_shared_offset` is 0.520–0.530 (so it is not a trivial artefact of shifting) and `unplanted_vs_rigid_shift` on twins is **0.494–0.536** (so the aggregate channel sees nothing on surrogate data with no plants) — meaning the 0.68 is driven by a property of *real* recordings the twin generator does not reproduce, which is exactly the "lab-specific artefact" `tube_ssl_real_compare.py`'s own docstring names as the worry. *Fix:* draw the 0.68 aggregate-only line on panel C, restate the panel as "the models clear an aggregate-only classifier by ~0.05–0.09", and say what the unexplained 0.68 is. **Verified: yes.**

**B3 · "On real recordings", lines 128–144 · The crosstalk check is normalized so that it cannot register the harm, and the report's own prose predicts that harm.**
`tube_ssl_real_compare.py` computes `top_pair_share` **only over events carried by exactly two ROIs** at the tight ±2-frame window. Those subsets differ five-fold between the two sides of the comparison:

| detector | events | share ≤2 ROIs (±2 frames) | 2-ROI events | top-pair share |
|---|---|---|---|---|
| supervised line, label-free | 2,476 | 0.183 | 454 | 0.333 |
| line vs rigid shift, *J* 20 s | 2,870 | **0.861** | **2,471** | 0.292 |
| line vs rigid shift, *J* 10 s | 2,855 | 0.784 | 2,237 | 0.333 |
| CoactDetect / LoCo | 451 / 429 | **0.000** | 0 | undefined (`n_recordings_with_pairs: 0`) |

The label-free model emits **five times as many two-ROI events**, and the check divides that away. Worse, the metric is the *concentration* within the pair set, so the failure it was written to catch — optical bleed-through, which produces many different neighbouring pairs rather than one recurring pair — pushes the number **down**, not up. Construct the instance: give the *J* = 20 s model 2,471 events each from a different adjacent-ROI pair; top-pair share falls to ~1/n and the check reports "less crosstalk than the supervised model". It has no power in the direction that matters, and it is structurally undefined for the two reference detectors. The report's own "What this does not settle" already says *"a two-ROI coincidence earns as much as a crowd"* — that is the confession, and `participation_share_le2` is the measurement that confirms it and is absent from the page. *Fix:* report `share ≤2 ROIs` at the ±2-frame window as its own row; restate the conclusion as "not attributable to a **single recurring** ROI pair" and add the caveat that distributed bleed-through is not excluded by this test; state that the references cannot contribute to it. **Verified: yes.**

**B4 · Line 128–144 · The real-recording table shows the one architecture row that supports claim (b) and omits three rows in the same file that reverse it.**
`real_compare/summary.json` holds every model's agreement. At label-free threshold, `supervised tube` beats `supervised line` on all four agreement numbers **while firing fewer events** (4.62 vs 4.95 per 10 min), and `tube_guard` beats both:

| model | coact→ | loco→ | →coact | →loco | events / 10 min |
|---|---|---|---|---|---|
| supervised tube_guard | **0.854** | **0.872** | 0.462 | 0.435 | 5.01 |
| supervised tube | 0.829 | 0.802 | **0.473** | **0.428** | **4.62** |
| supervised line | 0.774 | 0.758 | 0.444 | 0.399 | 4.95 |
| supervised line_length | 0.745 | 0.688 | 0.431 | 0.381 | 4.24 |

The report quotes only `line`'s 0.774/0.758 as "76–77 %". On the only real data in the report, the architecture declared "the best detector in the bake-off" is **last of the four**, and not by a rate artefact. *Fix:* show all four rows, or drop the section's implicit support for claim (b). **Verified: yes.**

**B5 · "What holds", line 36–38 · "`line` … is now the best detector in the bake-off" is contradicted by the caveat 26 lines below, by the paired per-fold data, and by the standard the tool the report ran already encodes.**
Per-fold paired differences (the more powerful test the report did not run):

- `line` − `line_length`: `[+0.045, −0.009, +0.179, +0.017]`, mean +0.058, paired *t* = 1.39 on 3 df (*p* ≈ 0.26), wins 3/4. **The mean is carried by one fold**; the median difference is +0.031, and on fold 1 the ablation wins.
- `line` − CoactDetect: `[+0.029, +0.022, +0.205, −0.005]` — the same single fold. Drop it and the mean ordering collapses to line 0.681, LoCo 0.671, tube 0.667, CoactDetect 0.666, line_length 0.663, tube_guard 0.658 — a 0.023 spread across six detectors on 90 planted events.
- The single fold doing the work is one where `line_length`'s recall fell to 0.60 against 0.833/0.833/0.733 elsewhere — a one-seed training outlier is the most likely reading, and `--train-seed` exists to test it.

`fair_bakeoff.py` states the standard in its own source: *"The tube's headline is a 0.017 gap inside a 0.061 fold spread, so a variant that moves F1 by less than that has demonstrated nothing until this axis is populated."* This headline is a 0.058 gap inside a 0.078 fold spread with the axis unpopulated. A bolded "is now the best detector" in **What holds** is not a claim the run supports. *Fix:* move it out of "What holds" — "`line` leads the bake-off's mean ordering by 0.027–0.058, driven by one of four folds, and is not separable at one training seed" — and keep the existing ⚠ where it is. **Verified: yes.**

---

## MAJOR

**M1 · Lines 154–158 · The untrained-baseline caveat is built on a rounding artefact, and quarantining it suppresses the strongest evidence for claim (c).**
"Untrained models scored 0.00 on every plant in the probe — no response to a planted line at all" is **false**. `probe/line_vs_fuzz.json` gives untrained `tube` at *K* = 16: line 3.84e-05, burst 1.60e-05, wave 7.98e-06, fuzz 5.37e-06 — small, but **correctly ordered**, monotone in *K*, and with a line ÷ fuzz ratio of **7.15**, five times sharper than the supervised tube's 1.43. Every threshold in the pipeline is chosen from quantiles of the model's own logits (`probs()` says so explicitly: *"a ranking loss fixes no scale"*), so output scale is irrelevant by construction and a random centre–surround net is a legitimate coincidence filter. The stated suspect — "the quantile-grid threshold on a near-constant output" — is refuted by the same run: untrained tube, fold 0, oracle threshold, **24 hits from 35 detections against 30 planted events** (F1 0.80). A degenerate threshold cannot produce that.

The consequence is the report's, not mine: at the oracle threshold, untrained `tube` scores **0.507** while every rigid-shift-trained tube arm scores 0.382–0.488. On this evidence the label-free objective is not merely weak, it is **net harmful for `tube`** — which is claim (c) in its strongest form, sitting in the one paragraph that tells the reader not to quote it. *Fix:* withdraw the "0.00 / no response" sentence, report the untrained probe numbers as they are, and either promote or explicitly test the trained-vs-untrained comparison. **Verified: yes.**

**M2 · Figure 2, lines 88–121 · The figure omits both `line` architectures, and the omitted arm is the one that fails a control the figure asserts "must be 0.5".**
`make_tube_ssl_figure.py` hard-codes `MODELS = {"tube", "tube_guard"}`. Figure 2 therefore shows two of the four architectures whose numbers the section tabulates, and the README nowhere says so. This matters because of what is missing: taking the 12 fits of each arm as the unit and testing the share against 0.5,

- `ssl_real line, J = 20 s` — the arm the report headlines **and the checkpoint it puts on real recordings** — reads **0.555 on `real_vs_shared_offset`, *t* = +3.11**. That is the control whose job is to show rigid shift does not leak, and for this arm it fails.
- `ssl_real tube, J = 10 s` reads **0.571** on `unplanted_twin_vs_rigid_shift`, *t* = +2.93; `tube_guard, J = 20 s` reads 0.575, *t* = +2.17. Panel C draws these pooled at ~0.54/0.55, visibly above its own dotted line, under a caption reading "must be 0.5" — and the README text does not mention the twin control at all.

*Fix:* draw all four architectures; mark the arms that fail either control; and reconcile panel C's 0.54–0.575 with the "must be 0.5" caption in the prose rather than leaving the reader to notice it in the image. **Verified: yes.**

**M3 · Figure 1 panel B and lines 68–86 · The probe is reported at one of three *K* values, and that is the *K* at which the preferred model wins.**

| model | *K* = 4 | *K* = 8 | *K* = 16 (the only one reported) |
|---|---|---|---|
| line ÷ burst — line / line_length | 3.90 / **5.05** | 1.63 / **1.99** | **1.83** / 1.82 |
| line ÷ wave — line / line_length | 1.01 / 1.01 | 1.05 / 1.04 | **1.32** / 1.14 |

At *K* = 4 and 8 the ablation is the better line-vs-burst discriminator and the wave separation is absent for both. The data are in the same JSON. Separately, the wave result is not separable as stated: at *K* = 16, line vs wave for `line` is *t* = 2.47 (n = 12 fields per side), for `line_length` *t* = 1.10, and the report's actual claim is a **difference of two ratios across models**, for which no test is offered; `tube`, which has no orientation channel, sits between them at 1.17. Reading the image confirms it — the `line_length` wave bar (15.4) is **higher** than the `line` wave bar (14.0), with error bars spanning roughly 9.5–20 on both. *Fix:* show all three *K*; state the test for the ratio-of-ratios or soften to "described, not tested". **Verified: yes.**

**M4 · Line 70 · "so its own scale cancels" is wrong, and the `line` column of the probe table is therefore not a cross-model comparison.**
The probe score is `peak(with plant) − peak(without plant)`. Subtraction removes the **baseline offset**; it does not remove the **gain**. Double a model's output scale and every number doubles. The evidence is in the same file: across the self-supervised checkpoints the `line_16` values run 17.7, 150, 143, 28.8, 45.9 — a factor of eight between fits of the *same* architecture. The three ratio columns are scale-free and fine; the `line` column (18.50 vs 17.56 vs 15.84) compares three models' raw gains and carries no meaning. *Fix:* delete the `line` column or normalize it; correct the sentence to "so the field's own baseline cancels". **Verified: yes.**

**M5 · Line 128–135 · Two columns of the real-recording table are definitional for the reference detectors and empirical for the models, and the comparison is invited anyway.**
CoactDetect and LoCo run at `min_rois=4` on the fast stream (`bench.py`, line 60: *"fast stream, min_rois=4 (the file's own headline_K)"*). Their `participation_share_le2` is exactly **0.000** and their "share with ≥ 3 ROIs" is exactly **1.00** — a floor, not a finding. Their median of 7–8 ROIs is likewise bounded below by 4. Placing those in the same columns as the learned models' 0.88/0.63/0.48 reads as "the learned models find thinner events", when half the comparison cannot report a thin event at all. *Fix:* annotate both rows "floored at 4 ROIs by the operating point". **Verified: yes.**

**M6 · Line 125–140 · CoactDetect and LoCo are not two independent references, and the number that shows it is in the report's own file and unquoted.**
`coact → loco` = 0.705 and `loco → coact` = 0.774. The two references agree with each other **less** than `supervised tube` agrees with either (0.829 / 0.802). They are both threshold-on-coactivity detectors reading the same ROI onset raster at the same `min_rois`, so they share upstream data and derivation — correlated errors, and agreeing with both is close to agreeing with one. Quoting "76–77 % of CoactDetect's **and** LoCo's events" as a range across two references presents a consistency check as double corroboration. *Fix:* report the coact↔loco agreement as the ceiling any detector is being measured against, and call this a consistency check, not validation. **Verified: yes.**

**M7 · Line 113–118, column "fits that learned anything" · Undefined quantity, and two of its four values do not reproduce.**
The term appears nowhere else. The figure tool defines a different word (`"A fit that fires nothing on the held-out fold is drawn at F1 0 and counted as silent"`) — and by that rule **all 12** fits of every headline arm fired, so it is not the rule used. Counting fits whose final training loss stayed at chance (ln 2 ≈ 0.6931) gives 10/12 for `line_length, J = 10 s` ✓ and 9/12 for `tube_guard, J = 10 s` ✓, but **11/12** for `line, J = 20 s` where the report says 10, and **11/12** for `tube, J = 20 s` where it says 9. *Fix:* define the column on-page and reconcile the two values; hand the arithmetic to Prove It. Related: "A quarter of the fits never left chance loss" is 7 of 48 (15 %) by the loss rule, 10 of 48 (21 %) by the report's own counts. Also worth stating: one `tube_guard` fit *ended above* chance loss at 0.762. **Verified: yes (cannot reproduce two values).**

---

## MODERATE

**D1 · Lines 111–121 · Each of the four "no labels" rows is silently the better of the two displacements.** `line` J20 0.463 over J10 0.405; `line_length` J10 0.455 over J20 0.448; `tube` J20 0.488 over J10 0.432; `tube_guard` J10 0.487 over J20 0.441. Selecting *J* per architecture on the outcome being reported, without saying so, is a selection on the test statistic — and it makes "Every architecture lands between 0.41 and 0.49" a statement about the maxima (`line` J10 is 0.405, below the stated floor; the simulated arms run down to 0.338). *Fix:* show both *J* per architecture, or say the row is the max and give the other. **Verified: yes.**

**D2 · Line 45–59 · Panel A contains fourteen detectors; the table shows eight, and the six dropped are all mid-table.** `rate+context` (0.571), `locust` (0.541), `tube_ratio` (0.503), `tube_ratio_guard` (0.471), binned SCE (0.451) and SPIKE-synch (0.267) are in the image and the JSON but not the table, while the two worst (`tiny`, `trace`) are kept. The table also does not state its *n*: eight simulated recordings from one spec, two per fold, 30 planted events per fold, 120 total — so the 0.058 headline gain is 22 recovered events. *Fix:* complete the table or say it is truncated, and give the event counts. **Verified: yes.**

**D3 · Line 92–95 and the section as a whole · The "orientation" sensor makes no new measurement of the data.** `line.py` line 163: `channels.append(count[:, :-1] / (count[:, 1:] + eps))` — the orientation channels are a fixed ratio of the four `count` channels the head **already receives** in the ablation. Nothing new is read off the raster; a nonlinearity is handed to the head that a 6-deep dilated stack cannot easily synthesise itself (pointwise division). Calling it "a second sensor" and "what put it there" overstates the mechanism and predicts a larger effect than the architecture can deliver — which is consistent with the effect being inside the noise. *Fix:* say the orientation channels are a derived ratio of the existing count channels. **Verified: yes.**

**D4 · Line 36–38 and 78–86 · The report answers a question Tony did not ask and files it as "the answer is Tony's".** Tony asked for an **orientation** detector reading the raster as a line. `line.py` and the ⚠ at line 83 both say plainly that orientation is unreadable by a permutation-invariant model over rate-sorted rows, and that what is measured is **temporal concentration**. Those are different quantities. The bolded "The architecture question has an answer, and it is Tony's" attributes to the request something the implementation explicitly declines to do. *Fix:* "Tony's orientation cannot be read by an order-free model; the nearest readable quantity is temporal concentration, and that is what `line` measures." **Verified: yes.**

**D5 · Line 128 header vs line 142–144 · Two different definitions of "participation" in one section, with only the generous one named.** The table's "ROIs within ±1 s" uses `participation(..., pad=1 s)`; the crosstalk check uses the default `pad=2 frames` (0.2 s). The headline "share with ≥ 3 ROIs" for `line, J = 20 s` is 0.63 at ±1 s and **0.139** at ±2 frames. The reader is told only about ±1 s. *Fix:* report both windows, or state which window each column uses. **Verified: yes.**

**D6 · Line 144 · "3–4 % of events sit within 5 s of a window edge, so it is not the window boundary" has no null.** Under a uniform null the expected share is 10 s ÷ window length; for a ~28-minute baseline window that is ≈ 0.6 %, so 3–4 % is **five to six times chance**, not evidence of absence. The number is also not in `summary.json` or `events.json` and I could not locate the code that produces it. *Fix:* state the expected share under the uniform null beside the observed one, and cite where it is computed. **Verified: partially — the arithmetic yes, the provenance no; hand to Prove It.**

**D7 · Figure 2 panels A and B · The figure plots prominently, at the second x position, a quantity the text says is untrustworthy and must not be quoted.** No mark on the figure says so. If M1's diagnosis holds the quarantine should be lifted; if it does not, the bar should not be drawn unmarked. **Verified: yes (read from the image).**

**D8 · Figure 1 panel A · `line`'s fold range (0.64–0.81) overlaps every detector from `tube` down to LoCo, and the report flags this only against the ablation.** The ⚠ at line 62 covers `line` vs `line_length`. Nothing covers `line` vs CoactDetect (paired *t* = 1.31) or `line` vs LoCo (*t* = 1.12), both of which the text's "best detector in the bake-off" asserts. *Fix:* extend the caveat's scope. **Verified: yes.**

---

## MINOR

**N1 · Line 68–70 · The probe's plants are under-specified and one is mis-described.** "Burst" is four onsets at frames t₀, t₀+2, t₀+4, t₀+6 — a **0.6 s** span, which the report omits and the tool's own docstring gives as 0.4 s. More consequentially, "wave" is called *"a line in every respect except that its members arrive one frame apart"*; at *K* = 16 it spans **16 frames = 1.6 s**, against the line's single frame and fuzz's 3 s. It is a narrower fuzz, not a line, and the plant set contains **no pair matched on temporal extent** — so the probe cannot separate "orientation" from "shorter window", which is the distinction the section is built on. *Fix:* state each plant's span; add a duration-matched pair if the mechanism claim is to stand. **Verified: yes.**

**N2 · Line 44–48 and 70 · The probe's models are not the bake-off's models, and the page reads as though they are.** `probe_line_vs_fuzz.py` refits "supervised line" itself (`n_train = min(10, n_fit)`, 900 steps, seed 0, no held-out fold), while Figure 1 panel A reports the bake-off's per-fold fits. Panels A and B are set side by side under one heading with panel B offered as the mechanism for panel A. *Fix:* say the probe refits. **Verified: yes.**

**N3 · Probe, throughout · Each probe number is a single maximum, and the untrained arm is one random initialisation.** `peak()` takes `np.max` over ±2 s; the report quotes the mean of 12 such maxima with `np.std` (population, so the spread is slightly understated) and no distribution. The untrained models are one `torch.manual_seed(0)` draw each — the caveat at line 154 rests on *n* = 1 per architecture. *Fix:* several inits; show the distribution, not the bare peak. **Verified: yes.**

**N4 · Paired-control machinery generally · With 26–60 % of crops tied and ties scored 0.5, several of these checks have most of their mass pinned to the null before any evidence.** Worst case, untrained `tube`: tie share **0.90**, so the maximum possible deviation from 0.5 is ±0.05 and the observed 0.494 is the only answer available. The trained `line` arms are fine (ties 0.00–0.36) — but the tie share belongs beside every quoted share, otherwise "reads at chance" cannot be distinguished from "cannot read anything". *Fix:* report `tie_share` and effective *n* wherever a share is quoted. **Verified: yes.**

**N5 · Throughout · Load-bearing constants are defined but not justified.** *J* = 10 s and 20 s (and item 2 of "What waits on Tony" makes *J* the very question at issue, so the choice selects the answer); ±1 s agreement tolerance, which sets the 76–77 % headline with no sensitivity shown; ≤ 0.5/1/2 events per 10 min; 900 steps; top 1 % pooling; *K* = 4/8/16; 3 s fuzz span; ±2 s peak window; three surrogates per threshold. The report justifies the pooling rule and step count as untuned (line 149–151) and leaves the rest bare. *Fix:* one clause of rationale each, or an explicit "chosen arbitrarily; unswept". **Verified: yes.**

**N6 · Line 44, 105, 128 · `tube_guard` is never defined.** It appears in three tables and both figures. Given that `aggregate_leak/` is what it presumably guards against, and that B2 makes the aggregate channel central, the reader needs the one sentence. *Fix:* define at first use, per the repo's abbreviation rule. **Verified: yes.**

**N7 · Line 30 · "0.49–0.53" is the rounded envelope; the underlying shared-offset means run 0.485 (lab slow, *J* = 11.2 s) to 0.528 (Cossart, *J* = 20 s).** Defensible as 2-dp rounding, but given B1 the band should be quoted per stream rather than pooled across folders. **Verified: yes.**

---

### What I could not check
The window-edge statistic at line 144 (D6) — I could not find it in any artifact or tool; the arithmetic objection stands regardless of where it came from. The reproduction commands at lines 181–187 were not run (Prove It's surface). Numbering, captions, units and abbreviation conventions were left to agent 10 except where a definition gap changed what a claim means (D5, N1, N6).
