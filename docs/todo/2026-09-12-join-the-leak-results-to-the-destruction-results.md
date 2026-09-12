---
status: open
filed: 2026-09-12
---

# Nobody has crossed the leak results with the destruction results, and the answer is already on disk

The surrogate screen measured two things the verdict needs: whether a candidate can be told from real
data **without** cross-ROI information (it leaks), and whether it **removes** planted coordination.
Both are measured. Neither has been read against the other, and a candidate is only viable where both
answers are right.

## What the leak detector already says

From `run_summary.json` in `<darkroom>/bugarach/2026-09-11-surrogate-screen/`, read 2026-09-12. The
candidates showing **no** per-ROI leak:

| stream | no leak detected |
|---|---|
| cossart | do-nothing; interval jitter and pattern jitter at 1 frame; **rigid shift at 1, 2 and 4 frames** |
| `steps_excluded` fast | do-nothing; interval and pattern jitter at 0.1 s; **rigid shift at 0.1 through 1.6 s** |
| `steps_excluded` slow | do-nothing; **rigid shift at 1.4 s** |

**The test has power where it matters**, which is what makes the table readable: the known-bad
positive control is caught even at one frame of displacement (accuracy 0.742, *p* = 0.005 on cossart)
and at 0.990 by sixteen frames. So survival is not the absence of a working test.

## Why the join is the whole decision

**Do-nothing survives in every stream.** It must — it changes nothing, so there is nothing to detect.
That single row proves the leak filter cannot rank candidates on its own: it is a gate, not a score.
The surrogate that leaks least is the one that does least, which is the shape of defect the plan's own
review already caught once.

**Most survivors sit at one frame of displacement.** A single frame is 0.1 s. Coordination in this
data is a seconds-scale phenomenon, so a one-frame displacement is unlikely to destroy what the
objective needs destroyed. If that holds in the destruction results, those survivors are do-nothing
wearing a different name.

**The only candidate surviving at a displacement comparable to real event structure is rigid shift**
— out to 1.6 s fast and 1.4 s slow. That agrees with Stella's preference for whole-train shifting,
reached by a completely different route, which is far better grounds than citing them
([why](2026-09-12-stellas-criterion-is-a-significance-test-not-a-training-signal.md)).

## What to do

Build one table, per stream: candidate × displacement, with two columns — leaks, and destroys. No new
runs; the destruction measure and the leak results are both in the run folder. Report the intersection
as the viable set, and say plainly if it is empty or contains only rigid shift.

⚠ **Read it after the encoder questions are settled**, not before — the
[boundary pile-up](2026-09-10-the-encoder-clips-onsets-onto-the-boundary-frames.md) and the
[frame truncation](2026-09-11-the-encoder-truncates-frame-positions.md) both sit between every
candidate and every statistic, so part of what these numbers measure is the encoder.

## Closes when

The joined table exists in the run folder's report, and the verdict rule is written against it rather
than against either half alone.
