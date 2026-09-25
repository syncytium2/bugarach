# For ml2dl: which chorus variant, and how it is configured

Written 2026-09-25 by the bugarach orchestrator session, in answer to ml2dl's question. Every
number is read from `main` at `3471f0c0` unless another source is named. **Read item 4 before
building the site around any number here: a retrain on a new bench starts tonight and may change the
answer.**

## 1. Which variant is on par with the best coded detector

**`chorus_norm`.** It is level with **CoactDetect**, the best coded detector, on the fast and
combined streams, and about 0.02 F1 below it on slow. `chorus_gain_norm` is roughly level too, and
lower than `chorus_norm` on fast. Plain `chorus`, `chorus_gain` and `chorus_line` were not in the
latest run. Plain `chorus` does not train (item 5).

**The latest run: the final-parameters night of 2026-09-25**
(`docs/learned/runs/2026-09-25-final-parameters/README.md`, table rows 502–518, and
`adoption.json`). F1 is fresh-seed F1: the mean over the quiet and busy backgrounds, on seeds
6000–6023 (24 recordings per background), with 95% intervals from 2,000 resamples.

| stream | CoactDetect, shipped → its search's proposal | `chorus_norm` (training seed the rule picked) | `chorus_gain_norm` |
|---|---|---|---|
| fast | 0.769 [0.755, 0.782] → 0.809 [0.791, 0.831] | 0.773 [0.746, 0.802] (seed 1) | 0.744 [0.723, 0.766] (seed 4) |
| slow | 0.848 [0.838, 0.857] (no proposal) | 0.825 [0.815, 0.834] (seed 3) | 0.827 [0.819, 0.834] (seed 3) |
| combined | 0.777 [0.763, 0.788] → 0.803 [0.788, 0.818] | 0.778 [0.760, 0.796] (seed 1) | 0.772 [0.752, 0.793] (seed 0) |

- **These are separate intervals, not a paired difference.** No paired chorus-minus-CoactDetect
  interval exists yet. ADR-0010 asks for one in the next run.
- **The false-alarm gate.** Chorus has no gate of its own. It is held to CoactDetect's budgets: 7 / 1 /
  10 calls per hour on the recording with nothing planted (fast / slow / combined), and 1.0 call per
  minute inside the elevated-rate stretch. Slow `chorus_norm` **fails** that stretch test, at 1.43 calls
  per minute. Every other chorus fit passes.
- **Chorus has no held-out F1 in that table.** Its training-seed pick is a selection score on seeds
  4000–4023, not a held-out result (docstring of `tools/train_learned_on_bench.py`).

## 2. The configuration, as trained

**Registry entry** (`src/bugarach/learn/nets/chorus_norm.py`):
`register("chorus_norm", roi_width=4, roi_depth=4, head_width=8, head_depth=8, top_m=4, norm=True)`,
built by `build_chorus` in `chorus.py`. Unset: `input_gain=None`, `vote_gain=None`; `eps=1e-6`. The
saved checkpoints record **1,897 parameters**. `chorus_gain_norm` is the same with `vote_gain=8.0`
(1,905 parameters).

**What the net sees** (`src/bugarach/learn/encode.py`):
- A binary raster, cells × frames. A frame is 1 where that cell has an event onset (the producer's
  t50rise) in it. No rates and no amplitudes; two onsets in one frame are still 1.
- 0.1 s per frame.
- Rows are sorted busiest first. The sort reads the whole recording, so the encoding is not causal.

**The architecture** (`chorus.py`; `_dilated_stack` in `nets/__init__.py`):
1. **The same temporal filter runs on every cell:** a dilated 1-D convolution stack (kernel 3,
   dilations 1, 2, 4, 8; GELU; 4 channels; then a 1×1 layer). It sees 31 frames.
2. **`norm`:** each cell's filter output is standardised over time, per channel, across whatever
   span the model is given.
3. **The bounded vote:** a sigmoid on each cell's output. (`chorus_gain_norm`: `sigmoid(g·(z − b))`,
   with a learnable gain g started at 8 and a learnable bias b started at 0.5.)
4. **Pooling over cells, symmetric in the cell axis:** the mean, the spread (standard deviation), and
   the mean of the top 4 cells. That makes 12 channels, and it works at any number of cells.
5. **The head:** a dilated stack 8 channels wide and 8 layers deep, seeing 511 frames. It outputs one
   logit per frame.

**Training** (`tools/train_learned_on_bench.py`, `src/bugarach/learn/train.py`):

| setting | value |
|---|---|
| optimiser | Adam, learning rate 0.01, constant; no warm-up |
| steps / batch | 900 steps, 3 crops per batch |
| crop | 4,096 frames = 409.6 s |
| recordings per fit | 10; the last 2 are held back to pick the threshold |
| data | the bench's seeds 1000–1023, quiet and busy backgrounds |
| loss | `BCEWithLogitsLoss`, `pos_weight` = (1 − p) / p, where p is the share of positive frames |
| targets | frames from the first to the last participant onset of each planted event are 1 |
| crop sampling | half the crops are centred on an event |
| training seeds | 5 fits per stream (seeds 0–4); one is picked (item 1) |
| streams | one model per stream, fast, slow and combined, each trained on its own bench |

- **Threshold:** `pick_threshold` maximises pooled F1 on the 2 held-back recordings, over a grid from
  1e-4 to 1 − 1e-4.
- **Merge gap:** 20 frames = 2 s.
- **Span at inference:** the whole recording. Training uses 409.6 s crops. Commit `c66c5da7` ("Chorus
  needs about 100-200 s, not 409.6") found F1 unchanged down to 200 s pieces, at most 0.026 lower at
  100 s, and broken at 60 s and below.

## 3. Where the weights live

- **Format:** JSON checkpoints (`src/bugarach/learn/checkpoint.py`). Each carries the architecture
  config, the encoding, the threshold, the merge gap and the training record.
- **The 2026-09-25 picks** are in the Dropbox darkroom, not in the repo:
  `<darkroom>/bugarach/2026-09-25-final-parameters/064/phase2/` (for example
  `chorus_norm_fast_seed1.json`), with scoring in `064/phase3*/`.
- **In the repo:** earlier checkpoints under `docs/learned/tuned_vs_coact/replicate1/chosen/`.

## 4. How strong the claim is, and what could change it

- **`docs/MILESTONES.md` has no chorus row.** Its only mention is that plain `chorus` is *measured not
  to train*. Every chorus-versus-CoactDetect run record says **nothing here is adopted**, and the
  records are working material that has not been through review. By the MILESTONES legend, "chorus_norm
  is level with CoactDetect" is **evidence**, not measured-and-decided.
- **Do not quote:**
  - "chorus beats CoactDetect";
  - 0.789 against 0.747 on fast (2026-09-24), which predates the event floor, on a bench being replaced;
  - +0.103 F1, from a branch, withdrawn;
  - any F1 on seeds 4000–4023, which is a selection score.
- **Open, and it starts tonight.** ADR-0010 (accepted 2026-09-25, PR #820) retrains `chorus_norm`,
  `chorus_gain_norm`, `line` and `tube` on a bench whose gaps between events are drawn from real
  recordings. The old bench never planted events closer than 120 s; three in four real gaps are
  shorter. Each model is also trained to learn participation. PR #824 adds variants named `*_part`
  (for example `chorus_norm_part`): they sum the per-cell votes into a count, take the recording's
  participation floor as an input, and add a per-cell membership term to the loss. A detector more
  than 0.01 F1 behind the leader on at least 2 of the 3 streams is dropped. **So the right variant for
  the site may be `chorus_norm_part`, or not chorus at all.** The report on that run is due the
  morning of 2026-09-26. Ask again then, or build the site on the architecture, which is stable,
  rather than on its scores.

## 5. What someone explaining this net should get right

- **It cannot count.** Mean, spread and top-4 are all fractions of the field, so today's `chorus_norm`
  cannot learn "at least 7 cells". The `*_part` variants exist to fix that.
- **"One cell, one vote" is a soft bound, not an exact one:** each vote is a sigmoid between 0 and 1.
- **Plain `chorus` does not train.** Its per-cell encoder starts deaf; `norm` and the gain are the
  repairs, and that is a good teaching story in its own right.
- **Fits collapsed at learning rate 0.03** (F1 0.125, flat). None of the 30 fits at 0.01 collapsed, so
  do not say "chorus often fails".
- **The model knows frames, not seconds.** Its time scales are in 0.1 s frames.
- **The normalisation depends on the span.** It is computed over the span the model is given, so the
  length of the piece changes the input.
- **House vocabulary** (`docs/GLOSSARY.md`, `docs/writing_conventions.md`):
  - Calcium events do not "fire". Say *event*, *onset*, *active*; a detector *calls*.
  - A *stream* is fast, slow or combined. "Modality" is not used.
  - "Data" is plural.
