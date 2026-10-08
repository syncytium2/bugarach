---
status: waiting-on-tony
filed: 2026-10-08
---

# The stack ceiling detector, and the bench with short intervals it led to

**Where this stands.** Session `bugarach-far-pennant` (Mac), 2026-10-08, ended at Tony's word:
*"make sure this detector does not get lost."* Everything is on `main` through PR #877. Nothing
is running and nothing is unpushed. The record with every number and figure is
[`docs/learned/runs/2026-10-08-stack-ceiling/README.md`](../learned/runs/2026-10-08-stack-ceiling/README.md).

## The detector, so it can be picked up cold

Tony's question: *"what is the tallest stack of width w we can create from circular shifting
events over period p?"* Any ROI (region of interest, a cell) with an onset in the period can be
slid into the window, so the tallest stack is the number of ROIs with an onset in the period,
the **ceiling**. No probability is computed.

- **Code:** `src/bugarach/detectors/stack_ceiling.py`, numpy only. `stack_ceiling_detect` is the
  entry point; `tests/test_stack_ceiling.py` holds it.
- **The call rule:** a moment is called when its tower would cost at least a threshold of shift
  per ROI to rebuild at a typical other moment of its period, and at least the recording's floor
  of ROIs stand.
- **Searched settings** (`tools/search_stack_ceiling.py`, picked on the even fresh seeds):

  | stream | window | period | merge gap | threshold |
  |---|---|---|---|---|
  | fast | 0.5 s | 480 s (longest tried) | 1.5 s | 10 s |
  | slow | 1 s | not used | 0.5 s | 0 s (cost off) |
  | combined | 0.5 s | 480 s (longest tried) | 3 s | 8 s |

- **It is not registered in any bench.** `bench.py`, `bench_slow.py` and `bench_combined.py` do
  not know it; the tools above run it beside the registered detectors. Registering count
  (sliding) touched 24 files.
- **The animated page:** `tools/make_stack_ceiling_demo.py` builds
  `explainer_stack-ceiling_20261008.html`, the reference page for ADR-0014's layout.

## What was found, in four lines

1. **The rebuild cost adds at most 0.008 F1** (fast; nothing on slow, 0.001 on combined) over the
   same sliding count with the cost off. It does keep calls out of a raised-rate stretch.
2. **Searched, the rule is about level with the tuned sliding forms of LoCo and CoactDetect on
   fast**, and ahead of the *shipped* points only. The gain is the 0.5 s window, which the
   2026-09-26 count (sliding) search had already found.
3. **Planted events at short gaps separate the detectors** (`tools/measure_close_events.py`, a
   controlled test): at a 10 s gap they sit within 0.09 F1; at 1 s they span 0.40 to 0.66. The
   merge gap decides it, then the window.
4. **Real gaps under 2 s exist and are a small share**: 4 to 6% of gaps in a 0.5 s window. The
   narrower window also counts nearly twice as many fast events, because the floor falls with it.

## Waiting on Tony

1. **What the revised bench is.** Keep events as a 2 s window defines them and add the shorter
   gaps between them, or move the event definition to a narrower window. The second roughly
   doubles the fast events and reaches ADR-0008, which fixes the floor's window at 2 s.
2. **Whether the stack ceiling goes further.** Options: register it and search it with the
   repository's own search; leave it as a recorded idea; or try the one variant not built, where
   every onset of an ROI moves together and repeated membership across towers is what scores.
3. **The fast proposals of 2026-09-26 are still unadopted**: sliding LoCo, sliding CoactDetect,
   and count (sliding) at 0.5 s, refused for a precision difference of 0.146 against a limit of
   0.10 that was set from the untuned point.
4. **Whether a long report counts as checked.** ADR-0014 says a report leads with its main
   figure; nothing checks it. The estate half is armory issue #32.

## What a session can do without a ruling

- **One table of every detector at its searched proposal on the same fresh seeds**, so the
  adoption decision in item 3 has a fair comparison behind it. Today's comparisons used the
  shipped points.
- **The close-events test on slow and combined, and with the sliding proposals** in place of the
  shipped fast points.
- **Extend the period past 480 s** in `tools/search_stack_ceiling.py`; the pick sits on the
  longest value tried on fast and combined.

## Loose ends

- ⚠ **The real-gap measurement ran on the stopped default folder**, on Tony's acknowledgment and
  by his hand (#858 is the stop). Its outputs are in the darkroom only,
  `<darkroom>/bugarach/2026-10-08-stack-ceiling/real-gaps/`. Every number was also computed
  without the four DI recordings the stop names, and no share moves by more than 0.01. When the
  producer's corrected export is the default, run it again.
- **The 2 s run wrote nothing on its first attempt** and ran clean on the second with the same
  command, reproducing the 2026-09-25 measurement byte for byte. The first attempt's output was
  not kept.
- **A session cannot set `BUGARACH_ACK_CONTAMINATION` itself.** The permission layer refused it,
  which is the stop working. Tony ran the measurement from a terminal.
- **Nothing here was murderboarded**: the page, the run record and ADR-0014's reference page.
- The page's verdicts use its own matching (a call within 2.5 s of a planted event) and a
  minimum of 3 ROIs, not the bench's scorer and floor.

## Where things are

- Detector: `src/bugarach/detectors/stack_ceiling.py`; tests `tests/test_stack_ceiling.py`.
- Tools: `tools/make_stack_ceiling_demo.py` (the page), `tools/measure_stack_ceiling.py` (the
  threshold alone), `tools/search_stack_ceiling.py` (every setting),
  `tools/measure_close_events.py` (planted events at short gaps),
  `tools/measure_real_intervals.py --window-sec` and `tools/make_real_gaps_by_window.py` (the
  real gaps in narrower windows).
- Darkroom: `<darkroom>/bugarach/2026-10-08-stack-ceiling/`.
- Rulings from the session: ADR-0014 (page layout).
