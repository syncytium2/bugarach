# rate+context, step by step

A plain-language walk-through of what the **rate+context** program does, written so a person can follow
one recording through it by hand, and precise enough that someone could rebuild the program from this page
alone. Each step links to the lines of code it describes.

**Checked, not just written.** An independent implementation was built from this page alone, with no
access to the code, and run against the real program on many recordings. They agree call for call; see
[the check](#how-this-page-was-checked).

All code links point to one fixed version of the project,
[`c797218`](https://github.com/syncytium2/bugarach/tree/c797218027364e39c7a0171001edfe1a05aaa023), so
they keep showing what this page describes even after the code changes.

[rate]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py
[bench]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/bench.py
[shared]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/_shared.py

---

## The idea in one sentence

Add up the calcium events of every neuron, second by second; wherever that total jumps well above its
own average over the surrounding minute, call a coordinated event.

## What goes in

- **For each neuron, the times of its calcium events**, in seconds. The time used for an event is its
  half-rise time: the moment the neuron's brightness is halfway up.
- **The start and end of the recording**, `t_lo` and `t_hi`: the earliest and the latest of two kinds of
  time — the boundaries of the recording's labelled parts (such as "before the drug" and "during the
  drug"), and the peak time of every event in every event list the recording has.
  ([code: `recording_extent`][rate-extent])
- Only events from `t_lo` to `t_hi` (both included) are used.
  ([code: `stream_trains`][rate-trains])

[rate-extent]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L94-L107
[rate-trains]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L110-L120

## The settings

| setting | stored value | what it does |
| --- | --- | --- |
| grid step | 0.1 s | how finely time is sampled; the lab's frame interval |
| counting window | 1 s | how long a stretch is added up at each moment |
| context window | 60 s | how long a stretch the average is taken over, centred on each moment |
| excess threshold (the bar) | 4.5 events per second | how far the count must rise above the average |
| merge gap | 3 s | moments over the bar closer than this belong to the same call |
| padding | 0.5 s | added to each end of a call |

The stored values are the ones in [`bench.py`, lines 246–248][bench-op]. The merge gap and the padding are
not listed there; they are the program's own defaults ([merge gap][rate-sig], [padding][rate-pad]).
Settings are tuned from time to time, so check that link for the version you are reading.

[bench-op]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/bench.py#L246-L248
[rate-sig]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L260-L275
[rate-pad]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L47

---

## The steps

### Step 1. Check there is something to count

If the recording has **fewer than 2 neurons**, or **no events at all** between `t_lo` and `t_hi`, stop:
there are no calls. A neuron with no events still counts toward the 2. ([code][rate-populated])

`t_hi` is always later than `t_lo`; the program refuses a recording where it is not.

[rate-populated]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L123-L125

### Step 2. Lay down a grid of moments

Make a list of moments 0.1 s apart, starting at `t_lo`: `t_lo`, `t_lo + 0.1`, `t_lo + 0.2`, … and
continuing up to `t_hi` (to within rounding). ([code][rate-grid])

The number of moments is `n = floor(q × (1 + 4ε)) + 1`, where `q = (t_hi − t_lo) / 0.1` and ε is the
smallest relative difference a computer number can hold (about 2.2 × 10⁻¹⁶). The tiny `4ε` lets the last
moment land on `t_hi` when the recording length is a whole number of steps but rounding would otherwise
lose it. ([code][shared-colon])

> **For someone rebuilding this exactly.** The grid copies MATLAB's rule for `t_lo:0.1:t_hi` to the last
> binary digit. Number the moments `k = 0 … n−1`.
>
> 1. The forward value of moment `k` is `t_lo + k × 0.1`.
> 2. The end value is `t_hi` itself if `|forward value of moment n−1 − t_hi| ≤ 4 × spacing(max(|t_lo|, |t_hi|))`
>    (`spacing(x)` is the gap from `x` to the next larger computer number); otherwise it is that forward value.
> 3. Moments `0 … floor(n/2) − 1` take their forward value; moments `floor(n/2) … n−1` are computed
>    backward, `end value − (n−1−k) × 0.1`.
>
> The count in the formula above and the end snap use different tolerances, so when `t_lo` is a large
> number the last moment can lie a hair past `t_hi`. This only matters when an event falls exactly on the
> boundary between two slots in step 3.

[rate-grid]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L128-L132
[shared-colon]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/_shared.py#L14-L32

### Step 3. Count every event into its nearest moment

Give each moment a slot reaching **0.05 s before it and 0.05 s after it**. Neighbouring slots share one
edge, computed from the later moment: the edges are `moment − 0.05` for every moment, plus one final edge
at `last moment + 0.05`. An event belongs to the slot that contains it: a slot includes its start and
excludes its end, except the last slot, which includes both. Then count the events in each slot.

Every event counts, **from every neuron together**. A neuron with two events in one slot adds 2.
([code][rate-hist])

An event that falls in no slot is not counted. That can happen at the very end: when the recording's
length overshoots a whole number of 0.1 s steps by more than 0.05 s, the last slot ends before `t_hi`,
and events between the end of the last slot and `t_hi` are left out.

[rate-hist]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L183-L184

### Step 4. Turn the counts into a rate, for any window length

To get the rate at a moment for a window of length `w` seconds:

1. Work out `h = floor(w / (2 × 0.1) + 0.5)` — half the window, in slots, rounded to the nearest whole
   number (halves round up). For a 1 s window `h = 5`; for a 60 s window `h = 300`.
2. **Add up the counts** of the slots from `h` before this moment to `h` after it: `2h + 1` slots, fewer
   where the grid ends.
3. **Divide by the length of the window that lies inside the recording**:
   `min(t_hi, moment + w/2) − max(t_lo, moment − w/2)`.

The answer is in events per second. Near the start and end of the recording the window is cut short and
the divisor shrinks with it, so the rate does not dip there. ([code][rate-rate])

> **For someone rebuilding this exactly.** Step 2 adds up `2h + 1` slots — 11 slots, which is 1.1 s, for a
> 1 s window — but step 3 divides by the window length itself, 1 s. Keep that asymmetry; it is what the
> program does.

[rate-rate]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L186-L194

### Step 5. Work out the two rates at every moment

- **The count:** the rate from step 4 with the **counting window**, 1 s.
- **The average nearby:** the rate from step 4 with the **context window**, 60 s — unless 60 s is at least
  90% of the recording's length (`t_hi − t_lo`), in which case use 90% of the recording's length instead.

([code][rate-ctx])

[rate-ctx]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L228-L235

### Step 6. Find the moments over the bar

At every moment, **excess = count − average nearby**. A moment is **over the bar** when its excess is at
least the excess threshold, 4.5 events per second (exactly at the bar counts as over). ([code][rate-excess])

[rate-excess]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L336-L356

### Step 7. Join nearby moments into calls

Go through the moments over the bar in time order. Start a new group whenever a moment is **more than
3 s** after the previous moment over the bar (exactly 3 s stays in the same group). "After" is the
difference of the two moments' times from step 2, not of their positions in the list, so a gap meant to be
exactly 3 s can land a rounding error either side. Each group runs from its first moment to its last.
([code][rate-merge])

[rate-merge]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L357-L360

### Step 8. Drop groups that are a single moment

A group whose first and last moment are the same moment is thrown away: one moment over the bar on its
own is treated as noise. ([code][rate-drop])

[rate-drop]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L361-L362

### Step 9. Pad each call, and report it

Move each group's start **0.5 s earlier** and its end **0.5 s later**. Each group is now one **call**:

- **onset** = the padded start;
- **width** = padded end − padded start (with the stored settings every call is at least 1.1 s wide: two
  moments 0.1 s apart, plus 0.5 s at each end).

([code][rate-pad-apply], [returned][rate-return])

[rate-pad-apply]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L366-L369
[rate-return]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/detectors/rate.py#L406-L416

That is the whole decision. The program also reports, for each call, the highest and the average count
inside it, but those numbers describe a call; they do not decide whether it is made.

---

## Options the program has that are not used

The code has three options that the stored settings leave switched off. They are listed so that nobody
reading the code wonders whether this page skipped them.

- **Peak mode** (`detection_mode="peak"`): calls at peaks of the excess instead of at stretches over the
  bar. Not used.
- **A guard band** (`guard_sec`): leaves a band around each moment out of the average nearby, so an event
  does not raise its own bar. Set to 0, so not used.
- **A multiplicative bar** (`threshold_mode="multiplicative"`): calls where the count is at least a
  multiple of the average, instead of the average plus a fixed amount. Not used.

## How the benchmark and the review run it

The simulated recordings are run through [`bench.run_detector`][bench-run]: it works out the recording's
start and end, takes the half-rise times of the events (see "What goes in"), and passes the stored
settings.

[bench-run]: https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/src/bugarach/bench.py#L714-L735

## How this page was checked

The clean-room method this project uses for its specifications
([workflow](https://github.com/syncytium2/bugarach/blob/c797218027364e39c7a0171001edfe1a05aaa023/docs/clean_room/WORKFLOW.md)):
a separate agent was given **this page and nothing else** — no code, no repository — and wrote its own
program from it. That program and the real `rate_detect` were then run on the same inputs and their calls
compared, each case under the stored settings and three other sets of settings (so a rule cannot pass by
matching one number):

- simulated recordings on both backgrounds;
- generated edge cases: very short recordings where the context window is cut to 90%, recordings whose
  length is or is not a whole number of steps, events outside the recording and exactly on slot boundaries,
  zero, one and two neurons, recordings with no events, and bursts 2.9, 3.0 and 3.1 s apart.

**Result: 8,616 runs, 35,553 calls, no differences** in onset or width (to 10⁻⁹ s). The part of this that
runs in a few seconds (4 simulated recordings and 300 generated cases, 1,216 runs) is in the project's
test suite, so if the program changes and this page does not, the tests fail
([harness](https://github.com/syncytium2/bugarach/tree/main/docs/clean_room/harness/rate_context_steps),
[test](https://github.com/syncytium2/bugarach/blob/main/tests/test_rate_context_steps.py)).

The check also improved the page. The agent listed every point where it had to guess: whether a neuron with
no events counts toward the 2, where the grid splits between forward and backward, how neighbouring slot
edges are computed, whether the 3 s gap compares times or positions, and one sentence that overstated when
events are lost at the end. Its guesses all matched the program; the answers are now written into steps
1, 2, 3, 7 and 9 above.
