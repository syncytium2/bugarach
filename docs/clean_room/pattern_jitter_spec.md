# Clean-room specification: `pattern_jitter`

**Revision 1** (2026-09-11). First issue, written for the overnight surrogate screen (the plan:
`docs/proposals/2026-09-10-surrogate-evaluation-overnight.md`, on the `surrogate-screen-plan`
branch when this was written). If this header ever
names a later revision, re-read the whole document before touching code: a revision means the
rules changed.

You are implementing ONE sampler, plus one counting helper, from this behavioural
specification.

**Ground rules for the implementer.** Work ONLY from this document. Do not consult Elephant,
the software published alongside the method, any other pattern-jitter or spike-resampling
implementation, or any web reference. The method comes from Harrison & Geman (2009), but you do
not need the paper: every rule you need is stated here, and where this document and the paper
differ (the partition's anchor, the fixed first and last onsets, the random-number protocol,
exact integer arithmetic), **this document wins**. The process around this spec — a primary and an
adversary working apart, hand-derived vectors, a differential fuzzer and its mutant check — is
[`WORKFLOW.md`](WORKFLOW.md).

## What the function does, in one paragraph

It takes one ROI's onsets as integer frame indices and returns a resampled copy. Onsets that sit
close together, within *R* frames of their predecessor, form rigid **patterns** that move as one
piece. Each pattern's first onset is re-placed uniformly at random inside the fixed-length
**jitter block** of *L* frames that contained it originally, subject to patterns staying more
than *R* frames apart. Among all trains satisfying these rules, with the first and last onsets
held where they were, every train is equally likely. A dynamic program over the patterns makes
sampling exact and linear in the number of onsets.

## Interface

```python
def pattern_jitter(train, window, L, R, rng):
    """-> 1-D numpy int64 array, same length as train"""

def pattern_jitter_count(train, window, L, R):
    """-> Python int: the number of valid resamplings of train"""
```

Both live in `src/bugarach/pattern_jitter.py`. Only numpy and the standard library may be used.

- `train`: 1-D array-like of integer frame indices, **non-decreasing** (repeats allowed: two
  onsets in one frame are an interval of zero). Converted with `numpy.asarray`.
- `window`: `(start, end)`, two integers, half-open: every onset must satisfy
  `start <= onset < end`. This is the **generation window**, the span the surrogate is generated
  over. Its only role in the arithmetic is to **anchor the partition** into jitter blocks (see
  *Jitter blocks*); the fixed first and last onsets already keep every output onset inside it.
- `L`: jitter-block length in frames, an integer `>= 1`.
- `R`: history length in frames, an integer `>= 0`. The overnight screen sets `R = f - 1`, *f*
  being its provisional dead time in whole frames.
- `rng`: an object with a `random_sample()` method, in practice a `numpy.random.RandomState`
  (sapper rule SAP002 forbids `default_rng` in `src/`, and the implementation must not create
  a generator of its own). The protocol that consumes it is fixed below, draw for draw.
- Return value of `pattern_jitter`: a **new** int64 array (never the input object or a view of
  it); the input is not modified.
- Return value of `pattern_jitter_count`: an exact Python `int`, arbitrary size. It is the
  normalising constant *Z* of the distribution below. It is `1` exactly when the input is its
  own only valid resampling — which is how a caller tells "this train cannot move" from "this
  draw happened not to move it".

### Input validation

Raise `ValueError`, **before any call to `rng`**, when:

- `train` is not 1-D;
- `train` is non-empty and its dtype is not an integer kind (numpy kind `'i'` or `'u'`). An
  empty `train` of any dtype is valid — `numpy.asarray([])` is float64 — and yields an empty
  int64 result;
- `train` decreases anywhere (`train[i] < train[i-1]` for some `i`);
- `start > end`, or any onset lies outside `[start, end)`;
- `L` or `R` is not an integer (a Python `int` or a numpy integer; `bool` and every `float`,
  even `2.0`, are rejected), or `L < 1`, or `R < 0`.

`pattern_jitter_count` applies the same checks to its four arguments.

## Definitions

Indices are 0-based. Write `x[0], ..., x[n-1]` for the input train and `y` for the output.

### Patterns

Onset `i >= 1` **starts a new pattern** when `x[i] - x[i-1] > R`. Onset 0 always starts one.
A **pattern** is a maximal run of consecutive onsets in which every neighbouring interval is
`<= R` frames. Let there be `d` patterns, numbered `0 .. d-1` in time order; pattern `p` holds
onsets `a_p .. b_p` (inclusive), so `a_0 = 0`, `b_{d-1} = n-1`, and `a_{p+1} = b_p + 1`.

- The **offset** of onset `i` in pattern `p` is `x[i] - x[a_p]`.
- The **span** of pattern `p` is `span_p = x[b_p] - x[a_p]` (zero for a single-onset pattern).
- The **gap** after pattern `p` is `G_p = span_p + R + 1`: the smallest allowed distance from
  the start of pattern `p` to the start of pattern `p+1`.

Pattern 0 (the one holding the first onset) and pattern `d-1` (the one holding the last onset)
are **fixed**. Every other pattern, `1 .. d-2`, is **free**. With `d <= 2` no pattern is free.

### Jitter blocks

The frames from `start` onward are partitioned into consecutive blocks of `L` frames, the first
beginning at `start`. The block of a frame `t` begins at

```
block_start(t) = start + L * floor((t - start) / L)
```

and holds frames `block_start(t) .. block_start(t) + L - 1`. The partition depends only on
`start` and `L`, never on the train. (The last block may run past `end`; that is harmless,
because no output onset can pass the last input onset — see *Properties*.)

### Allowed starts

The set `A_p` of frames where pattern `p` may start:

- `A_0 = {x[a_0]}` and `A_{d-1} = {x[a_{d-1}]}` — the fixed patterns stay where they are. When
  `d = 1` these are the same single set.
- For a free pattern, `A_p` is the whole jitter block containing its original start:
  `block_start(x[a_p]) .. block_start(x[a_p]) + L - 1`.

### The resampling distribution (normative)

A **valid resampling** is a sequence of pattern starts `W_0, ..., W_{d-1}` with

1. `W_p` in `A_p` for every `p`, and
2. `W_{p+1} >= W_p + G_p` for every `p` from `0` to `d-2`,

and the output train it defines is `y[i] = W_p + (x[i] - x[a_p])` for each onset `i` of
pattern `p`. `pattern_jitter` returns one valid resampling drawn **uniformly** from the set of
all of them (to within the 2^-53 resolution of `rng`, below); `pattern_jitter_count` returns the
number of them, `Z`. The input itself is always valid, so `Z >= 1`. For an empty train, `Z = 1`
(the empty resampling) and the result is empty.

**The same distribution stated onset by onset**, which is how Harrison & Geman write it and
what the vectors' brute-force derivations use: `y` is any integer train with

- `y[0] = x[0]` and `y[n-1] = x[n-1]`;
- for every `i >= 1`: if `x[i] - x[i-1] <= R` then `y[i] - y[i-1] = x[i] - x[i-1]` exactly;
  otherwise `y[i] - y[i-1] > R` (their equation 2.2);
- for every onset `i` other than the first and the last, with `p` its pattern:
  `y[i]` lies in `block_start(x[a_p]) + (x[i] - x[a_p]) + {0, ..., L-1}` (their equation 4.2,
  with the partition anchored at `start`).

The two statements define the same set: equation 2.2 makes every within-pattern interval exact,
so a train is fixed by its pattern starts, and every onset's window in equation 4.2 is its
pattern-start's block shifted by the onset's offset, so all of a pattern's window conditions
reduce to `W_p` lying in `A_p`. Note what this implies: **a pattern's later onsets follow its
start rigidly and may leave the start's block** (the vector `rigid_pair` pins this).

## Properties every output has

These follow from the definition. They are the invariants a fuzzer checks on every draw.

- Same length as the input; non-decreasing; `y[0] = x[0]` and `y[n-1] = x[n-1]`.
- Every interval of `R` frames or less in the input is reproduced exactly, at the same position
  in the sequence; every longer interval stays longer than `R`. Hence the output's multiset of
  intervals `<= R` equals the input's, and **no interval of `R` frames or less is created**.
- Every output onset lies in `[x[0], x[n-1]]`, hence in the window.
- Each free pattern's start lies in the jitter block of its original start.
- The number of patterns, their order and their internal shapes are unchanged.
- If `L = 1`, or `d <= 2`, the output equals the input.

## The algorithm

Harrison & Geman's section 3 samples from this distribution exactly with a dynamic program:
a backward pass that counts completions, then a forward pass that samples one pattern at a time.
This section specifies both passes at the level of patterns, fully enough to implement.

### The count table (backward pass)

For each pattern `p` and each `w` in `A_p`, let `N_p(w)` be the number of ways to place patterns
`p+1 .. d-1` validly given `W_p = w`:

```
N_{d-1}(w) = 1                                   for w in A_{d-1}
N_p(w)     = sum of N_{p+1}(v) over v in A_{p+1} with v >= w + G_p
                                                 for w in A_p, p = d-2 down to 0
Z          = N_0(x[0])
```

`N_p(w)` is non-increasing in `w`, so the zero entries of a table, if any, sit at its high end.
With suffix sums over `A_{p+1}` each table costs `O(L)`, so the whole pass is `O(n L)` time and
`O(d L)` storage.

**Exact integers are required.** Counts can reach `L` to the power of the number of free
patterns: at `L = 20`, fifteen free patterns can pass int64's range, and a few hundred can pass
float64's (the vector `overflow_chain` has `Z = 10^309`, beyond float64's largest value of about
1.8 × 10^308). Use Python integers. Harrison & Geman suggest normalising
each table to avoid overflow; that is **not** allowed here, because the selection rule below is
pinned to exact arithmetic, so that two independent implementations given the same `rng` return
**identical** trains — the property the differential fuzzer and the overnight plan's stop rule
depend on.

### The sampling pass (forward pass)

```
W_0 = x[0]
for p = 1 .. d-2, in increasing order:                 # the free patterns only
    lo      = W_{p-1} + G_{p-1}
    c_1 < c_2 < ... < c_m  = the elements of A_p that are >= lo, ascending
    weights = N_p(c_1), ..., N_p(c_m)
    T       = N_p(c_1) + ... + N_p(c_m)                 # always equals N_{p-1}(W_{p-1}) >= 1
    u       = rng.random_sample()                       # exactly one call per free pattern
    k       = u * 2**53                                 # an exact integer, see below
    C_r     = N_p(c_1) + ... + N_p(c_r)                 # running total
    W_p     = c_r for the SMALLEST r with  2**53 * C_r  >  k * T
W_{d-1} = x[a_{d-1}]            (when d >= 2)
y[i]    = W_p + (x[i] - x[a_p]) for every onset i of every pattern p
```

The selection rule, precisely:

- `u` comes from `rng.random_sample()` called **with no arguments**, **exactly once per free
  pattern, in pattern order**, including a free pattern whose candidate list has one member.
  Nothing else calls `rng`. When `d <= 2` (so for trains of 0, 1 or 2 onsets) `rng` is not
  called at all. A test passes a stub whose `random_sample()` returns scripted values and fails
  if it is called too often or too rarely.
- `numpy.random.RandomState.random_sample()` returns multiples of 2^-53 in `[0, 1)`, so
  `k = u * 2**53` is an exact integer with `0 <= k < 2**53` (in Python, `int(u * 2**53)` is
  exact because multiplying by a power of two is exact). A scripted value that is not a multiple
  of 2^-53 is outside this contract.
- The comparison `2**53 * C_r > k * T` is between exact integers. It is **strict**. It always
  has a solution because `C_m = T` and `k < 2**53`. It never selects a zero-weight candidate
  (its running total equals its predecessor's). Equivalently, `W_p` is the first candidate whose
  cumulative share `C_r / T` exceeds `u` — but floating-point evaluation of that form is not
  guaranteed to agree with the integer rule, and on `overflow_chain` the counts cannot be held
  in a float64 at all. The vector `quarter_boundary` pins the strictness.
- Candidates are taken in **ascending** frame order.

**Why this is uniform.** The chance of the sequence of choices `W_1 .. W_{d-2}` is the product of
`N_p(W_p) / N_{p-1}(W_{p-1})`, which telescopes to `N_{d-2}(W_{d-2}) / N_0(x[0]) = 1 / Z`, since
a valid last choice has exactly one completion. The pinned rule realises each ratio to within
2^-53.

**Why it never fails.** The input is valid, so `Z >= 1`. If `N_{p-1}(W_{p-1}) >= 1` then
`T >= 1`, and the chosen candidate has `N_p(W_p) >= 1`. At the end, `N_{d-2}(W_{d-2}) >= 1`
means the fixed last pattern is reachable, so the output is always valid.

**Caching is allowed.** The count tables depend on `(train, start, L, R)` and not on `rng`; an
implementation may cache them across calls, provided outputs and `rng` consumption are exactly as
specified.

## What this does on the overnight screen's data

A consequence of the plan's definitions, not a measurement. The plan sets `R = f - 1` with the
dead time *f* at or below a folder's observed floor, the shortest within-ROI interval in that
folder's baselines. So on the `steps_excluded` baselines every real interval is longer than *R*,
**every onset is its own pattern**, and the method reduces to fixed-partition jitter in which
resampled neighbours stay at least *f* frames apart, with the first and last onsets fixed. Rigid
multi-onset patterns arise only where real intervals of *R* frames or less exist. That can happen
on the Cossart folder, whose floor is two frames only to within the frame interval's rounding,
and whose onsets are mapped to their nearest frame — which can also make two onsets share a
frame, the zero interval the vector `duplicate` pins.

## Test vectors

Every vector must reproduce exactly. Trains are frame indices; windows are `[start, end]` as
JSON lists meaning the half-open `(start, end)`.

### Support vectors

For each, the complete set of valid resamplings, listed in lexicographic order. Each member has
probability exactly `1 / count` under the distribution; `pattern_jitter_count` must return
`count`. Every output `pattern_jitter` produces on these inputs must be a member. The frequency
check against `1 / count` is statistical and belongs to the harness (see *Validation*).
Where given, `marginals` counts the members by the start of each free pattern, keyed by pattern
number.

```json
[
 {"name": "empty", "train": [], "window": [0, 10], "L": 3, "R": 0,
  "count": 1, "support": [[]]},
 {"name": "single", "train": [4], "window": [0, 10], "L": 3, "R": 0,
  "count": 1, "support": [[4]]},
 {"name": "two", "train": [2, 7], "window": [0, 10], "L": 5, "R": 0,
  "count": 1, "support": [[2, 7]]},
 {"name": "L1_identity", "train": [0, 3, 5, 9], "window": [0, 10], "L": 1, "R": 0,
  "count": 1, "support": [[0, 3, 5, 9]]},
 {"name": "one_pattern", "train": [1, 3, 6, 8], "window": [0, 10], "L": 4, "R": 3,
  "count": 1, "support": [[1, 3, 6, 8]]},
 {"name": "three_singletons", "train": [0, 4, 9], "window": [0, 10], "L": 5, "R": 0,
  "count": 4, "support": [[0, 1, 9], [0, 2, 9], [0, 3, 9], [0, 4, 9]]},
 {"name": "R_binds", "train": [0, 4, 9], "window": [0, 10], "L": 5, "R": 2,
  "count": 2, "support": [[0, 3, 9], [0, 4, 9]]},
 {"name": "coupled_two_free", "train": [0, 3, 5, 12], "window": [0, 15], "L": 5, "R": 1,
  "count": 14,
  "support": [[0, 2, 5, 12], [0, 2, 6, 12], [0, 2, 7, 12], [0, 2, 8, 12], [0, 2, 9, 12],
              [0, 3, 5, 12], [0, 3, 6, 12], [0, 3, 7, 12], [0, 3, 8, 12], [0, 3, 9, 12],
              [0, 4, 6, 12], [0, 4, 7, 12], [0, 4, 8, 12], [0, 4, 9, 12]],
  "marginals": {"1": {"2": 5, "3": 5, "4": 4},
                "2": {"5": 2, "6": 3, "7": 3, "8": 3, "9": 3}}},
 {"name": "chain_three_free", "train": [0, 3, 6, 9, 12], "window": [0, 15], "L": 3, "R": 1,
  "count": 13,
  "support": [[0, 3, 6, 9, 12], [0, 3, 6, 10, 12], [0, 3, 7, 9, 12], [0, 3, 7, 10, 12],
              [0, 3, 8, 10, 12], [0, 4, 6, 9, 12], [0, 4, 6, 10, 12], [0, 4, 7, 9, 12],
              [0, 4, 7, 10, 12], [0, 4, 8, 10, 12], [0, 5, 7, 9, 12], [0, 5, 7, 10, 12],
              [0, 5, 8, 10, 12]],
  "marginals": {"1": {"3": 5, "4": 5, "5": 3},
                "2": {"6": 4, "7": 6, "8": 3},
                "3": {"9": 5, "10": 8}}},
 {"name": "frozen", "train": [0, 2, 4, 6, 8], "window": [0, 10], "L": 3, "R": 1,
  "count": 1, "support": [[0, 2, 4, 6, 8]]},
 {"name": "rigid_pair", "train": [0, 6, 7, 13], "window": [0, 15], "L": 4, "R": 2,
  "count": 4, "support": [[0, 4, 5, 13], [0, 5, 6, 13], [0, 6, 7, 13], [0, 7, 8, 13]]},
 {"name": "span_binds_next", "train": [0, 5, 6, 10], "window": [0, 12], "L": 4, "R": 2,
  "count": 3, "support": [[0, 4, 5, 10], [0, 5, 6, 10], [0, 6, 7, 10]]},
 {"name": "end_to_start_gap", "train": [0, 1, 5, 9, 10], "window": [0, 12], "L": 3, "R": 2,
  "count": 2, "support": [[0, 1, 4, 9, 10], [0, 1, 5, 9, 10]]},
 {"name": "duplicate", "train": [0, 5, 5, 11], "window": [0, 12], "L": 4, "R": 0,
  "count": 4, "support": [[0, 4, 4, 11], [0, 5, 5, 11], [0, 6, 6, 11], [0, 7, 7, 11]]},
 {"name": "anchor_at_start", "train": [2, 6, 11], "window": [2, 14], "L": 4, "R": 0,
  "count": 4, "support": [[2, 6, 11], [2, 7, 11], [2, 8, 11], [2, 9, 11]]},
 {"name": "anchor_at_zero", "train": [2, 6, 11], "window": [0, 14], "L": 4, "R": 0,
  "count": 4, "support": [[2, 4, 11], [2, 5, 11], [2, 6, 11], [2, 7, 11]]},
 {"name": "partial_last_block", "train": [0, 9, 10], "window": [0, 11], "L": 4, "R": 0,
  "count": 2, "support": [[0, 8, 10], [0, 9, 10]]}
]
```

### Scripted vectors

`rng` is a stub whose `random_sample()` returns the listed values in order. The output must be
exactly `expected`, and the stub must be exhausted — no more and no fewer calls than listed.
Every value is a multiple of 2^-53: `0.9999999999999999` is 1 − 2^-53 and `0.2499999999999999`
is 1/4 − 2^-53, as Python's `repr` writes them. The trains are those of the support vectors with
the same base name.

```json
[
 {"name": "empty_no_draw",          "base": "empty",            "u": [], "expected": []},
 {"name": "two_no_draw",            "base": "two",              "u": [], "expected": [2, 7]},
 {"name": "one_pattern_no_draw",    "base": "one_pattern",      "u": [], "expected": [1, 3, 6, 8]},
 {"name": "L1_draws_anyway",        "base": "L1_identity",      "u": [0.5, 0.5], "expected": [0, 3, 5, 9]},
 {"name": "zero_first",             "base": "three_singletons", "u": [0.0], "expected": [0, 1, 9]},
 {"name": "quarter_just_below",     "base": "three_singletons", "u": [0.2499999999999999], "expected": [0, 1, 9]},
 {"name": "quarter_boundary",       "base": "three_singletons", "u": [0.25], "expected": [0, 2, 9]},
 {"name": "half",                   "base": "three_singletons", "u": [0.5], "expected": [0, 3, 9]},
 {"name": "three_quarters",         "base": "three_singletons", "u": [0.75], "expected": [0, 4, 9]},
 {"name": "top",                    "base": "three_singletons", "u": [0.9999999999999999], "expected": [0, 4, 9]},
 {"name": "coupled_low",            "base": "coupled_two_free", "u": [0.0, 0.0], "expected": [0, 2, 5, 12]},
 {"name": "coupled_half",           "base": "coupled_two_free", "u": [0.5, 0.5], "expected": [0, 3, 7, 12]},
 {"name": "coupled_top_then_low",   "base": "coupled_two_free", "u": [0.9999999999999999, 0.0], "expected": [0, 4, 6, 12]},
 {"name": "coupled_weights_matter", "base": "coupled_two_free", "u": [0.34375, 0.0], "expected": [0, 2, 5, 12]},
 {"name": "chain_low",              "base": "chain_three_free", "u": [0.0, 0.0, 0.0], "expected": [0, 3, 6, 9, 12]},
 {"name": "chain_half",             "base": "chain_three_free", "u": [0.5, 0.5, 0.5], "expected": [0, 4, 7, 10, 12]},
 {"name": "chain_top",              "base": "chain_three_free", "u": [0.9999999999999999, 0.9999999999999999, 0.9999999999999999], "expected": [0, 5, 8, 10, 12]},
 {"name": "chain_weights_matter",   "base": "chain_three_free", "u": [0.6875, 0.0, 0.0], "expected": [0, 4, 6, 9, 12]},
 {"name": "frozen_draws_anyway",    "base": "frozen",           "u": [0.9999999999999999, 0.9999999999999999, 0.9999999999999999], "expected": [0, 2, 4, 6, 8]},
 {"name": "rigid_pair_half",        "base": "rigid_pair",       "u": [0.5], "expected": [0, 6, 7, 13]},
 {"name": "rigid_pair_top",         "base": "rigid_pair",       "u": [0.9999999999999999], "expected": [0, 7, 8, 13]},
 {"name": "span_binds_next_top",    "base": "span_binds_next",  "u": [0.9999999999999999], "expected": [0, 6, 7, 10]},
 {"name": "end_to_start_gap_low",   "base": "end_to_start_gap", "u": [0.0], "expected": [0, 1, 4, 9, 10]},
 {"name": "end_to_start_gap_half",  "base": "end_to_start_gap", "u": [0.5], "expected": [0, 1, 5, 9, 10]},
 {"name": "duplicate_three_quarters","base": "duplicate",       "u": [0.75], "expected": [0, 7, 7, 11]},
 {"name": "anchor_at_start_half",   "base": "anchor_at_start",  "u": [0.5], "expected": [2, 8, 11]},
 {"name": "anchor_at_zero_half",    "base": "anchor_at_zero",   "u": [0.5], "expected": [2, 6, 11]},
 {"name": "partial_last_block_half","base": "partial_last_block","u": [0.5], "expected": [0, 9, 10]}
]
```

### Seeded vectors

`rng = numpy.random.RandomState(seed)`. The output must be exactly `expected`, and afterwards
`rng` must have advanced by exactly `draws` samples: its next `random_sample()` equals the
`(draws + 1)`-th value of a fresh `RandomState(seed)`. The first values of the seeds used are
seed 0: 0.5488135039273248, 0.7151893663724195, 0.6027633760716439; seed 1: 0.417022004702574,
0.7203244934421581, 0.00011437481734488664; seed 2: 0.43599490214200376, 0.025926231827891333,
0.5496624778787091.

```json
[
 {"name": "coupled_seed0", "base": "coupled_two_free", "seed": 0, "draws": 2, "expected": [0, 3, 8, 12]},
 {"name": "coupled_seed2", "base": "coupled_two_free", "seed": 2, "draws": 2, "expected": [0, 3, 5, 12]},
 {"name": "chain_seed0",   "base": "chain_three_free", "seed": 0, "draws": 3, "expected": [0, 4, 7, 10, 12]},
 {"name": "chain_seed1",   "base": "chain_three_free", "seed": 1, "draws": 3, "expected": [0, 4, 7, 9, 12]},
 {"name": "chain_seed2",   "base": "chain_three_free", "seed": 2, "draws": 3, "expected": [0, 4, 6, 10, 12]},
 {"name": "frozen_seed0",  "base": "frozen",           "seed": 0, "draws": 3, "expected": [0, 2, 4, 6, 8]},
 {"name": "L1_seed0",      "base": "L1_identity",      "seed": 0, "draws": 2, "expected": [0, 3, 5, 9]},
 {"name": "two_seed0",     "base": "two",              "seed": 0, "draws": 0, "expected": [2, 7]},
 {"name": "empty_seed0",   "base": "empty",            "seed": 0, "draws": 0, "expected": []}
]
```

### The overflow vector

Too long for JSON; built from its rule. `overflow_chain`: `train = [10 * j for j in range(311)]`
(311 onsets, 0 to 3100), `window = (0, 3101)`, `L = 10`, `R = 0`.

- Every onset is its own pattern; the 309 free patterns each have the block `10j .. 10j + 9`,
  and adjacent blocks are disjoint, so no constraint couples them: `count` is exactly `10**309`
  (a Python `int`; it overflows float64).
- Scripted with 309 values of `0.5`: `expected[j] = 10 * j + 5` for `j = 1 .. 309`, with
  `expected[0] = 0` and `expected[310] = 3100`.
- Scripted with 309 values of `0.0`: the input.
- Scripted with 309 values of `0.9999999999999999`: `expected[j] = 10 * j + 9` for the free
  patterns — the last candidate of every block, reached only because the integer comparison is
  exact at the top of the range.
- None of these counts fits in a float64 unnormalised: in Python, multiplying `u` by `10**309`
  raises `OverflowError`. Normalised floating-point tables can survive the size, but nothing
  guarantees they reproduce the pinned choices; the harness should run all three scripted cases.

### Error vectors

Each must raise `ValueError` without calling `rng` (use a stub that fails if called).

```json
[
 {"name": "decreasing",        "train": [3, 1],        "window": [0, 10], "L": 3,   "R": 0},
 {"name": "before_start",      "train": [0, 5],        "window": [1, 10], "L": 3,   "R": 0},
 {"name": "at_end",            "train": [2, 10],       "window": [0, 10], "L": 3,   "R": 0},
 {"name": "start_after_end",   "train": [],            "window": [5, 4],  "L": 3,   "R": 0},
 {"name": "L_zero",            "train": [0, 4, 9],     "window": [0, 10], "L": 0,   "R": 0},
 {"name": "R_negative",        "train": [0, 4, 9],     "window": [0, 10], "L": 3,   "R": -1},
 {"name": "L_float",           "train": [0, 4, 9],     "window": [0, 10], "L": 2.0, "R": 0},
 {"name": "R_float",           "train": [0, 4, 9],     "window": [0, 10], "L": 3,   "R": 0.0},
 {"name": "float_train",       "train": [0.0, 4.0],    "window": [0, 10], "L": 3,   "R": 0},
 {"name": "two_dimensional",   "train": [[0, 4], [5, 9]], "window": [0, 10], "L": 3, "R": 0}
]
```

`float_train` means a numpy float64 array; `two_dimensional` a 2-D int64 array. The empty
float64 array, by contrast, is valid (see *Input validation*).

### How the decisive vectors were derived

Every support set was enumerated by hand from the onset-by-onset definition, then cross-checked
against a throwaway brute-force enumerator that tries every onset in its equation-4.2 window and
keeps the trains satisfying equation 2.2, independently of the pattern-level algorithm. The
cross-check agreed on every vector.

- **`three_singletons`** `[0, 4, 9]`, `L = 5`, `R = 0`. Three one-onset patterns; the ends are
  fixed. The middle start's block is `0..4`; it must exceed 0 and be below 9, so it is one of
  `1..4`, four ways. A centred window, as in the paper's equation 2.1, would give a different set.
- **`R_binds`** is the same train with `R = 2`: the middle start must be at least 3 from both
  neighbours, leaving `{3, 4}`. Reading "longer than *R*" as "at least *R*" would admit 2.
- **`coupled_two_free`** `[0, 3, 5, 12]`, `L = 5`, `R = 1`. Blocks `0..4` and `5..9`; the gap
  is 2. The first free start is in `{2, 3, 4}`; given it, the second runs from
  `max(5, first + 2)` to 9. That leaves 5, 5 and 4 completions, so 14 in all, and the first free
  start is **not** uniform (5 : 5 : 4). Sampling each free start uniformly from what remains open
  would give 1 : 1 : 1; `coupled_weights_matter` separates the two: with `u = 11/32`, the
  weighted rule lands in the first third (`2**53 * 5 > k * 14`), the unweighted one in the second.
- **`chain_three_free`** `[0, 3, 6, 9, 12]`, `L = 3`, `R = 1`. Blocks `3..5`, `6..8`, `9..11`;
  the gap is 2 and the last free start must be at most 10. The count tables are
  `N_3 = (1, 1, 0)` over `9, 10, 11`; `N_2 = (2, 2, 1)` over `6, 7, 8`; `N_1 = (5, 5, 3)` over
  `3, 4, 5`; `Z = 13`. `chain_half` walks them: `u = 1/2` picks 4 (running totals 5, 10, 13
  against half of 13), then 7 from weights `(2, 2, 1)`, then 10 from `(1, 1, 0)`: with `T = 2`,
  `k * T` equals `2**53`, the first running total ties it and the strict rule moves on.
  `chain_top` shows the zero-weight candidate 11 is never chosen, even at the largest `u`.
- **`frozen`** `[0, 2, 4, 6, 8]`, `L = 3`, `R = 1`. The only valid resampling is the input, yet
  the three free patterns each consume one draw.
- **`rigid_pair`** `[0, 6, 7, 13]`, `L = 4`, `R = 2`. `{6, 7}` is one pattern (interval 1). Its
  start's block is `4..7`, and starting at 7 puts its second onset at 8, **outside** the block:
  later onsets follow the start and are not clipped to it.
- **`span_binds_next`** `[0, 5, 6, 10]`, `L = 4`, `R = 2`. The free pattern `{5, 6}` has span 1,
  so its start must satisfy `10 - (start + 1) > 2`, i.e. at most 6, although its block runs to 7.
  Forgetting the span admits `[0, 7, 8, 10]`, whose last interval of 2 would merge two patterns.
- **`end_to_start_gap`** `[0, 1, 5, 9, 10]`, `L = 3`, `R = 2`. Patterns `{0, 1}`, `{5}` and
  `{9, 10}`. The middle start must be more than 2 after the **end** of the first pattern (frame
  1), so at least 4 — measuring from its start (frame 0) would admit 3 — and at most 6 below the
  last pattern's start at 9; its block `3..5` leaves `{4, 5}`.
- **`duplicate`** `[0, 5, 5, 11]`, `R = 0`. The zero interval is `<= R`, so the two onsets
  sharing frame 5 stay together wherever the pattern goes.
- **`anchor_at_start`** and **`anchor_at_zero`**: the same train with the window starting at 2
  and at 0. The block holding frame 6 is `6..9` in the first and `4..7` in the second. This pins
  the partition's anchor at `start`.
- **`partial_last_block`** `[0, 9, 10]`, window `(0, 11)`, `L = 4`: the middle start's block is
  `8..11`, which runs past the window's end; the fixed last onset at 10 cuts it to `{8, 9}`.
- **`quarter_boundary`**: with four equal candidates, `u = 1/4` makes `k * T` equal to
  `2**53 * 1` exactly. The strict rule rejects the first candidate and takes the second; `>=`
  would take the first.

## Validation (for the adversary and the harness)

Per [`WORKFLOW.md`](WORKFLOW.md): both implementations pass every vector above before anything
else; the adversary then hand-derives vectors of its own, and a seeded structured fuzzer
compares the two.

- **Exact differential targets.** On any valid input, both implementations must return the
  same `pattern_jitter_count`, and, given `RandomState`s built from the same seed, the same output
  and the same `rng` consumption. Any difference is a disagreement, adjudicated against this text.
- **Invariants on every draw:** the properties listed under *Properties every output has*.
- **Distribution.** On inputs small enough to enumerate (the support vectors, and fuzzed trains
  with `count` in the hundreds or less), the output frequencies over many seeded draws must be
  consistent with uniform over the support, by a goodness-of-fit test at a stated α. The
  enumeration used as the reference must be a brute force over the onset-by-onset definition,
  not the count table.
- **Fuzzer shapes worth forcing:** zero intervals; intervals of exactly `R` and `R + 1`; patterns
  whose span lands their last onset in the next block; blocks cut by the window's end;
  `start > 0`; `L = 1`; `R` at least the largest interval (one pattern); trains of 0, 1, 2 and
  3 onsets; long trains whose counts exceed 2^64.
- **Mutants the fuzzer must kill** (WORKFLOW's sanity check), each with a vector that already
  kills it: centred windows instead of the fixed partition (`three_singletons`); the partition
  anchored at frame 0 instead of `start` (`anchor_at_start`); `>= R` for "longer than *R*"
  (`R_binds`); the gap measured start to start (`end_to_start_gap`); the span left out of the gap
  (`span_binds_next`); later onsets clipped to their start's block (`rigid_pair`); the last onset
  left free (`three_singletons`, which then draws twice); uniform choice among open candidates
  instead of count-weighted (`coupled_weights_matter`, `chain_weights_matter`); `>=` in the
  selection rule (`quarter_boundary`); skipping the draw for a one-candidate pattern
  (`frozen_draws_anyway`); unnormalised floating-point counts (`overflow_chain`).

## Acceptance

1. Every vector in this document passes exactly, for both functions.
2. The adversary's hand-derived vectors pass, and the differential fuzz shows no disagreement,
   with every mutant above killed.
3. Divergences found later come back as new vectors or a revision header **in this file**, never
   as reference code.

## Deliverable and harness

- **Deliverable:** `src/bugarach/pattern_jitter.py`, defining `pattern_jitter` and
  `pattern_jitter_count` exactly as specified (plus private helpers), with a module docstring
  stating that it was implemented solely from this specification. `src/bugarach/surrogates.py`
  imports it lazily and converts the screen's jitter radius *J* to `L` (the plan: √2·*J* in
  whole frames) and its dead time *f* to `R = f - 1`; neither conversion is this function's job.
- **Harness:** `docs/clean_room/harness/pattern_jitter/` — the adversary's implementation, its
  hand-derived vectors with derivation notes, and the fuzzer.
- **Runner:** `tests/test_pattern_jitter.py`, wiring this spec's vectors, the adversary's
  vectors, a differential fuzz pass and the mutant check into the normal suite.

## Source

Harrison, M. T. & Geman, S. (2009). A rate and history-preserving resampling algorithm for
neural spike trains. *Neural Computation* 21:1244–1258. Used here: equation 2.2 (the history
constraint), equation 2.3 (the uniform distribution), section 3 (the dynamic program), equation
4.2 (fixed-partition windows applied to pattern starts), footnote 1 (the tables may be rescaled;
declined here in favour of exact integers) and footnote 4 (hold the first and last onsets fixed).
The continuous version in their appendix is not used; frames are already discrete. On the shelf
at `<darkroom>/lit/surrogates/harrison_geman_2009_pattern_jitter.pdf`.
