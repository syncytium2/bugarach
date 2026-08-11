# Clean-room specification: `find_peaks_halfprom`

You are implementing ONE pure function from this behavioral specification.

**Ground rules for the implementer:** work ONLY from this document. Do not
consult MATLAB, Octave, SciPy source, or any existing peak-finding
implementation — the point of this exercise is an independent
implementation whose only inputs are the behavior described here and the
test vectors below. Any algorithm and code structure of your own choosing
is fine as long as every vector passes exactly.

## Interface

```python
def find_peaks_halfprom(S, min_prominence=0.0):
    """-> (idx, prominence, left_x, right_x), four 1-D numpy arrays"""
```

- `S`: 1-D array-like of floats. May contain NaN. (±Inf behavior is not
  required.)
- `idx`: int array — 0-based sample index of each qualifying peak,
  ascending. The other three arrays align with it.
- `prominence`: float array (definition below).
- `left_x`, `right_x`: float arrays — fractional 0-based sample positions
  of the peak's half-prominence extent (definitions below).
- Only numpy and the standard library may be used.
- Empty input, all-NaN input, or no qualifying peaks -> four empty arrays
  (`idx` of integer dtype).

## Definitions

### Segments

NaN values split `S` into maximal runs of non-NaN samples ("segments").
Nothing crosses a NaN: peaks, prominence intervals, and extents are all
confined to the peak's own segment.

### Local maxima (candidate peaks)

Within a segment, collapse each run of equal adjacent values to a single
point, keeping the run's FIRST index. A collapsed point is a local maximum
iff its value is strictly greater than the previous collapsed value AND
strictly greater than the next collapsed value, both of which must exist
within the segment. Consequences the vectors exercise:

- A flat-topped peak reports at the LEFT edge of its plateau.
- The first/last samples of a segment are never peaks (no neighbor on one
  side), so a monotone staircase has no peaks at all.

### Prominence

For a peak at index `p` with value `V = S[p]`:

- **Left base interval**: walk left from `p - 1` while samples are `<= V`,
  stopping before the first sample `> V`, at a NaN, or past the segment
  start. (Equal-height samples are walked through.)
- **Left base value** = the minimum value in that interval. If the interval
  is empty (immediate neighbor is `> V` — impossible for a true local
  maximum on that side, but stated for completeness), the base is `V`.
- Right side symmetric.
- `prominence = V - max(left_base_value, right_base_value)`.

A peak QUALIFIES iff `prominence >= min_prominence` (**inclusive** — a peak
whose prominence exactly equals the gate is kept). Non-qualifying peaks are
dropped entirely.

### Saddle (the extent bound)

The half-prominence extent on each side is bounded by that side's
**saddle**, defined as follows for the left side (right symmetric):

- Take the left base interval from the prominence definition.
- Truncate it at the first LOCAL MAXIMUM (as defined above) whose value is
  `>= V`, if one lies inside the interval — the truncated interval ends
  just before that maximum's position. (Only equal-height maxima can occur
  inside, since anything strictly greater already terminated the base
  interval.)
- **Left saddle index** = the index of the minimum value within the
  (possibly truncated) interval; if that minimum occurs more than once,
  take the occurrence NEAREST the peak.

Note the asymmetry that the vectors pin down: the prominence base looks
THROUGH equal-height peaks (so twin equal peaks each get full prominence
down to the outer floor), but the saddle STOPS at an equal-height peak (so
their extents cannot bleed through each other).

### Half-prominence extents

For a qualifying peak `p` with prominence `prom`:

- Reference height: `ref = S[p] - prom / 2`.
- **Left edge** (`left_x`): walk left from `p - 1` toward the left saddle
  index (inclusive). Stop at the first sample with value `<= ref`, at
  index `j`:
  - If found: `left_x = j + (ref - S[j]) / (S[j+1] - S[j])` — the linear
    interpolation of the crossing on the segment between samples `j` and
    `j + 1`. When `S[j] == ref` this lands exactly on `j` (a sample equal
    to the reference stops the walk; do not continue past it).
  - If every sample down to and including the saddle is `> ref`: clamp
    `left_x = float(saddle index)` — no interpolation.
- **Right edge** (`right_x`): mirror image, walking right, interpolating
  between `j - 1` and `j`, clamping at the right saddle.

`left_x <= p <= right_x` always holds. The extent may cross a plateau top
(values equal to the peak are `> ref` and are walked through).

## Output ordering

Arrays are sorted ascending by `idx`.

## Test vectors

Every vector must reproduce EXACTLY (float tolerance 1e-9). `null` in `S`
means NaN. Positions/indices are 0-based.

```json
[
 {"name": "triangles",
  "S": [0,1,3,1,0,2,6,2,0,1,4,1,0], "min_prominence": 0.0,
  "idx": [2,6,10], "prominence": [3.0,6.0,4.0],
  "left_x": [1.25,5.25,9.333333333333],
  "right_x": [2.75,6.75,10.666666666667]},
 {"name": "plateau",
  "S": [0,1,4,4,4,1,0,2,5,5,2,0], "min_prominence": 0.0,
  "idx": [2,8], "prominence": [4.0,5.0],
  "left_x": [1.333333333333,7.166666666667],
  "right_x": [4.666666666667,9.833333333333]},
 {"name": "staircase",
  "S": [0,0,1,1,2,2,3,3,4,4], "min_prominence": 0.0,
  "idx": [], "prominence": [], "left_x": [], "right_x": []},
 {"name": "twin_equal",
  "S": [0,5,0,0,5,0,0,0,3,0], "min_prominence": 0.0,
  "idx": [1,4,8], "prominence": [5.0,5.0,3.0],
  "left_x": [0.5,3.5,7.5], "right_x": [1.5,4.5,8.5]},
 {"name": "equal_saddle",
  "S": [0,5,4,5,0], "min_prominence": 0.0,
  "idx": [1,3], "prominence": [5.0,5.0],
  "left_x": [0.5,2.0], "right_x": [2.0,3.5]},
 {"name": "nan_segments",
  "S": [0,3,0,null,0,4,0,null,null,2,5,2], "min_prominence": 0.0,
  "idx": [1,5,10], "prominence": [3.0,4.0,3.0],
  "left_x": [0.5,4.5,9.5], "right_x": [1.5,5.5,10.5]},
 {"name": "prom_gate",
  "S": [0,2,0,0,3,0], "min_prominence": 2.0,
  "idx": [1,4], "prominence": [2.0,3.0],
  "left_x": [0.5,3.5], "right_x": [1.5,4.5]},
 {"name": "ref_equal_stop",
  "S": [0,1,2,4,2,1,0], "min_prominence": 0.0,
  "idx": [3], "prominence": [4.0],
  "left_x": [2.0], "right_x": [4.0]},
 {"name": "multi_bump",
  "S": [0,1,0.5,2,0.2,8,0.2,2,0.5,1,0], "min_prominence": 1.5,
  "idx": [3,5,7], "prominence": [1.8,8.0,1.8],
  "left_x": [2.4,4.487179487179,6.5],
  "right_x": [3.5,5.512820512821,7.6]}
]
```

Worked notes on the two decisive vectors:

- **equal_saddle** `[0,5,4,5,0]`: each 5-peak has prominence 5 (base looks
  through its equal twin to the 0 floor), so `ref = 2.5`. Walking inward
  from either peak, the valley sample 4 is `> 2.5`, and the saddle (index
  2) is reached without a crossing — the inner edge CLAMPS to exactly 2.0.
  The outer edges interpolate normally (0.5 / 3.5).
- **ref_equal_stop** `[0,1,2,4,2,1,0]`: `ref = 2.0` and the flanking
  samples equal it exactly — the walk stops there and the edge lands
  exactly on the sample (2.0 / 4.0), NOT further out at the 1-samples.

## Acceptance

1. All vectors above pass at 1e-9.
2. The integrator will additionally run a larger hidden regression suite
   (real-data traces) against your implementation; expect iteration if a
   corner case diverges — divergences will come back to you as new vectors
   in this document's format, never as reference code.

## Deliverable

One self-contained Python file defining `find_peaks_halfprom` exactly as
specified (plus any private helpers), with a docstring stating it was
implemented solely from this specification.
