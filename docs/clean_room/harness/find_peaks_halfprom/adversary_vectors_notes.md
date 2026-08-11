# Hand derivations for adversary_vectors.json

All expected outputs below were derived by hand from the spec's rules
BEFORE running any code, then cross-checked against `adversary_impl.py`.
No mismatches were found on the cross-check, so nothing was revised.

**Revision 2 update.** Under the rev-2 saddle rule (runs of equal adjacent
values in the (possibly truncated) interval collapse to the run's FIRST
(leftmost) index on BOTH sides; only ties between DISTINCT runs go to the
run nearest the peak), every vector was re-derived by hand. Exactly ONE
changed: vector 3 `plateau_saddle_clamp` (see its section). Vectors 4, 5,
12 involve interval plateaus or min ties but are rev-1/rev-2 invariant, as
re-argued inline. Three new rev-2-specific vectors (15-17) were added.

Notation: peak value `V`, base minima `(l, r)`, `prom = V - max(l, r)`,
`ref = V - prom/2`. Left interpolation `j + (ref - S[j])/(S[j+1] - S[j])`,
right interpolation `j - (ref - S[j])/(S[j-1] - S[j])`.

A structural fact used repeatedly: WITHOUT saddle truncation, the saddle
sample is always `<= ref` (that side's min `m <= max(l,r) < (V+max(l,r))/2
= ref`), so a crossing is always found and clamping can ONLY happen when an
equal-height maximum truncated the interval. Every clamp case below is
built that way.

## 1. plateau_touch_nan — `[NaN,4,4,1,3,1,NaN,2,5,5]`, gate 0

Segment A = indices 1..5 `[4,4,1,3,1]`. Collapsed: 1(4), 3(1), 4(3), 5(1).
Only local max: pos 4 (3>1, 3>1). The leading 4,4-plateau starts the
segment (touches the NaN) -> not a peak (no left neighbor).
Segment B = indices 7..9 `[2,5,5]`. Collapsed: 7(2), 8(5). The 5,5-plateau
ends the segment (array end) -> not a peak.
Peak 4: left base walk from 3: 1<=3, then S[2]=4>3 -> interval [3], l=1.
Right: walk from 5: 1<=3, then NaN -> interval [5], r=1. prom=2, ref=2.
No truncation; saddles 3 and 5. Left j=3: 3+(2-1)/(3-1)=3.5.
Right j=5: 5-(2-1)/(3-1)=4.5.
=> idx [4], prom [2], left_x [3.5], right_x [4.5].

## 2. triple_equal — `[0,5,1,5,1,5,0]`, gate 0

Three equal 5-peaks at 1, 3, 5. Bases look THROUGH equal maxima, so every
peak reaches a 0 floor on at least one side and the valleys (1) on the
other are irrelevant: max(l,r)=0... carefully:
- p=1: l=min[0]=0, r=min[2..6]=0 -> prom 5, ref 2.5.
- p=3: l=min[0..2]=0, r=min[4..6]=0 -> prom 5, ref 2.5.
- p=5: l=min[0..4]=0, r=min[6]=0 -> prom 5, ref 2.5.
Saddle truncation stops at the NEAREST equal max:
- p=1 right: trunc at pos 3 -> [2], saddle 2 (val 1). 1<=2.5 -> j=2:
  right_x = 2-(2.5-1)/(5-1) = 1.625. Left j=0: 0+(2.5-0)/5 = 0.5.
- p=3 left: trunc at pos 1 -> [2], saddle 2, j=2:
  left_x = 2+(1.5)/4 = 2.375. Right: trunc at pos 5 -> [4], j=4:
  right_x = 4-1.5/4 = 3.625.
- p=5 left: trunc at pos 3 (nearest of the two maxima to its left) ->
  [4], j=4: left_x = 4+1.5/4 = 4.375. Right j=6: 6-2.5/5 = 5.5.
=> idx [1,3,5], prom [5,5,5], left_x [0.5,2.375,4.375],
   right_x [1.625,3.625,5.5].

## 3. plateau_saddle_clamp — `[0,6,4,4,4,6,0]`, gate 0

**RE-DERIVED FOR REV 2 (the only vector whose expectations changed).**
Plateau-shaped saddle (4,4,4) between equal 6-peaks at 1 and 5.
Both peaks: bases (0,0) through the equal twin -> prom 6, ref 3.
The truncated interval on the inner side of each peak is [2,3,4], which is
a SINGLE run of 4s -> one candidate at its leftmost index, position 2, for
BOTH peaks. No distinct-runs tie exists, so the nearest-run rule never
fires.
- p=1 right: saddle 2; walk 2..2: 4 > 3 -> CLAMP right_x = 2.0.
  Left j=0: 0+3/6 = 0.5.
- p=5 left: saddle 2 (NOT 4 as under rev 1's nearest-occurrence rule);
  walk 4,3,2 all 4 > 3 -> CLAMP left_x = 2.0. Right j=6: 6-3/6 = 5.5.
Rev-1 expectation was left_x [0.5,4.0]; rev 2 changes peak 5's clamp to
the run's leftmost index: left_x [0.5,2.0].
=> idx [1,5], prom [6,6], left_x [0.5,2.0], right_x [2.0,5.5].

## 4. exact_gate — `[0,2,0,1.5,0]`, gate 2.0

p=1 (V=2): l=min[0]=0; right walk from 2: 0<=2, 1.5<=2, 0<=2 -> [2,3,4],
r=0. prom = 2 - 0 = 2 == gate -> KEPT (inclusive). ref 1.
Right saddle: no local max >= 2 inside (the 1.5 peak is < 2); runs are
2(0), 3(1.5), 4(0) — two DISTINCT single-sample runs tie at 0 -> nearest
peak -> 2 (rev-2 rule; same result as rev 1 here).
Walk j=2: 0<=1 -> 2-(1-0)/(2-0) = 1.5.
Left j=0: 0+(1-0)/2 = 0.5.
p=3 (V=1.5): left walk from 2: 0<=1.5 then S[1]=2>1.5 -> l=0; r=min[4]=0.
prom 1.5 < 2 -> dropped.
=> idx [1], prom [2], left_x [0.5], right_x [1.5].

## 5. ref_on_plateau — `[0,3,3,6,3,3,0]`, gate 0

p=3, V=6, bases (0,0), prom 6, ref 3. The flanking 3,3-plateaus equal ref
exactly. Walk left from 2: S[2]=3 <= 3 -> STOP at j=2 (a sample equal to
ref stops the walk; do not continue across the plateau to index 1):
left_x = 2 + (3-3)/(6-3) = 2.0 exactly. Mirror: right_x = 4.0.
=> idx [3], prom [6], left_x [2.0], right_x [4.0].

## 6. negatives — `[-5,-1,-4,-2,-6]`, gate 0

p=1 (V=-1): l=min[0]=-5; right walk: -4,-2,-6 all <= -1 -> r=-6.
prom = -1 - max(-5,-6) = -1-(-5) = 4. ref = -3.
Left j=0: -5<=-3 -> 0 + (-3-(-5))/(-1-(-5)) = 2/4 = 0.5.
Right: no trunc (the -2 max < -1); saddle 4. j=2: -4<=-3 ->
2 - (-3-(-4))/(-1-(-4)) = 2 - 1/3 = 1.6666666667.
p=3 (V=-2): left walk from 2: -4<=-2 then S[1]=-1>-2 -> interval [2],
l=-4. r=min[4]=-6. prom = -2-(-4) = 2, ref = -3.
Left j=2: -4<=-3 -> 2 + (-3+4)/(-2+4) = 2.5.
Right j=4: -6<=-3 -> 4 - (-3+6)/(-2+6) = 4 - 0.75 = 3.25.
=> idx [1,3], prom [4,2], left_x [0.5,2.5], right_x [5/3,3.25].

## 7. tiny_segments — `[NaN,7,NaN,1,2,NaN,NaN,3]`, gate 0

Segments: [7] (1 sample), [1,2] (2 samples, monotone), [3] (1 sample).
First/last samples of a segment are never peaks -> no candidates at all.
=> four empty arrays.

## 8. all_nan — `[NaN,NaN,NaN]` -> four empty arrays (spec: all-NaN input).

## 9. empty — `[]` -> four empty arrays (spec: empty input; idx int dtype).

## 10. shallow_valleys_clamp_both — `[0,6,5,6,5,6,0]`, gate 0

Like triple_equal but valleys (5) sit ABOVE ref: peaks 1,3,5, all V=6,
bases (0,0) through the equal maxima -> prom 6, ref 3.
- p=1: right trunc at pos 3 -> [2], saddle 2 (5 > 3) -> CLAMP right_x=2.0.
  Left j=0 -> 0.5.
- p=3 (base interval truncated by an equal max on BOTH sides): left trunc
  at 1 -> saddle 2, clamp left_x = 2.0; right trunc at 5 -> saddle 4,
  clamp right_x = 4.0.
- p=5: left clamp 4.0; right j=6 -> 6-3/6 = 5.5.
=> idx [1,3,5], prom [6,6,6], left_x [0.5,2.0,4.0], right_x [2.0,4.0,5.5].

## 11. asymmetric_valleys_first_trunc — `[0,5,1,5,3,5,0]`, gate 0

Peaks 1,3,5, all V=5, prom 5 (floors 0 through equals), ref 2.5.
Valleys differ: 1 (below ref) and 3 (above ref).
- p=1: right trunc at pos 3 -> [2], j=2: 2-(2.5-1)/4 = 1.625. Left 0.5.
- p=3: left trunc at pos 1 -> [2], j=2: 2+1.5/4 = 2.375 (interpolates);
  right trunc at pos 5 -> [4], S[4]=3 > 2.5 -> CLAMP right_x = 4.0.
  One side clamps, the other interpolates.
- p=5: left trunc must use the FIRST (nearest) equal max, pos 3, NOT pos 1
  -> interval [4], 3 > 2.5 -> CLAMP left_x = 4.0. (Truncating at pos 1
  instead would give interval [2,3,4], saddle 2, and a crossing at j=2 —
  a discriminating case for the "first" rule.) Right j=6: 6-2.5/5 = 5.5.
=> idx [1,3,5], prom [5,5,5], left_x [0.5,2.375,4.0],
   right_x [1.625,4.0,5.5].

## 12. plateau_equal_max_trunc — `[0,6,6,2,6,0]`, gate 0

Equal maxima where one is a PLATEAU (6,6 at 1-2, collapsed position 1) and
one a point peak (4). Collapsed: 0(0),1(6),3(2),4(6),5(0); maxima 1 and 4.
- p=1 (plateau peak, reported at LEFT edge): l=min[0]=0; right walk from
  p+1=2 THROUGH its own plateau sample (6<=6): interval [2..5], r=0.
  prom 6, ref 3. Right trunc at pos 4 -> interval [2,3] (6,2), min 2 at 3
  -> saddle 3. Extent walk from 2: S[2]=6 > 3 (crosses the plateau top),
  S[3]=2<=3 -> j=3: right_x = 3-(3-2)/(6-2) = 2.75. Left j=0: 0+3/6 = 0.5.
- p=4: left walk from 3: 2<=6, 6<=6, 6<=6, 0<=6 -> interval [0..3], l=0;
  r=min[5]=0. prom 6, ref 3. Left trunc at the plateau max, position 1
  (its collapsed FIRST index) -> interval [2,3] = (6,2); min 2 at 3 ->
  saddle 3. j=3: left_x = 3+(3-2)/(6-2) = 3.25. Right j=5: 5-3/6 = 4.5.
  (Rev 2: the truncated interval [2,3] starts mid-run — index 2 is the
  tail of the 6,6 run cut at the truncation boundary. It collapses to a
  candidate at position 2 with value 6 == V, which can never be the
  minimum, so the saddle is unchanged: 3.)
=> idx [1,4], prom [6,6], left_x [0.5,3.25], right_x [2.75,4.5].

## 13. mixed_magnitude — `[0,0.001,10,0.001,0]`, gate 5.0

p=2, V=10, bases (0,0), prom 10 >= 5 -> kept. ref 5.
Left j=1: 0.001<=5 -> 1 + (5-0.001)/(10-0.001) = 1 + 4.999/9.999
= 1 + 0.49994999499949995 = 1.4999499949995.
Right j=3: 3 - 4.999/9.999 = 2.5000500050005.
=> idx [2], prom [10], left_x [1.4999499949995], right_x [2.5000500050005].

## 14. monotone_and_tiny — `[1,2,NaN,5,4,3,NaN,2,2]`, gate 0

Segments: [1,2] (2 samples), [5,4,3] (monotone descending; middle collapsed
point 4 is not > previous 5), [2,2] (collapses to a single point, no
neighbors). No peaks anywhere.
=> four empty arrays.

## 15. equal_run_tie_near_plateau — `[0,6,4,4,5,4,4,6,0]`, gate 0 (rev 2)

Two DISTINCT equal-depth valley RUNS (4,4 at 2-3 and 4,4 at 5-6) between
equal 6-peaks at 1 and 7, with a 5-bump (peak 4) between them. This is the
case where rev 1 and rev 2 tie handling diverge: candidates are run
positions 2 and 5, both value 4.
- p=1 (V=6): bases (0,0) through equals -> prom 6, ref 3. Right trunc at
  pos 7 -> interval [2..6]; runs 2(4), 4(5), 5(4); tie of distinct runs at
  4 -> nearest peak 1 -> saddle 2. Walk 2..2: 4>3 -> CLAMP right_x = 2.0.
  Left j=0: 0+3/6 = 0.5.
- p=7 (V=6): prom 6, ref 3. Left trunc at pos 1 -> interval [2..6]; tie of
  runs at positions 2 and 5 -> nearest peak 7 -> saddle 5 (the RUN's
  leftmost index; rev 1's nearest-occurrence rule would have said 6).
  Walk 6,5: both 4>3 -> CLAMP left_x = 5.0. Right j=8: 8-3/6 = 7.5.
- p=4 (V=5): left base walk from 3: 4,4<=5 then 6>5 -> [2,3], l=4; right
  [5,6], r=4. prom 1, ref 4.5. Saddles: single runs at 2 / 5. Left j=3:
  4<=4.5 -> 3+(4.5-4)/(5-4) = 3.5. Right j=5: 5-(4.5-4)/(5-4) = 4.5.
=> idx [1,4,7], prom [6,1,6], left_x [0.5,3.5,5.0], right_x [2.0,4.5,7.5].

## 16. single_run_leftmost_clamp — `[0,6,5,4,4,5,6,0]`, gate 0 (rev 2)

A left-side valley run (4,4 at 3-4) NOT touching any interval boundary,
where the leftmost-index rule and rev 1's nearest-the-peak rule pull in
OPPOSITE directions with no tie involved. Peaks 1 and 6 (V=6; the interior
5s are not maxima: collapsed values 0,6,5,4,5,6,0). Bases (0,0) -> prom 6,
ref 3 for both.
- p=6 left: base [0..5], trunc at pos 1 -> interval [2..5]; runs 2(5),
  3(4), 5(5); unique min run 4 -> saddle = its LEFTMOST index 3 (rev 1
  nearest-occurrence would say 4). Walk 5,4,3: values 5,4,4 all > 3 ->
  CLAMP left_x = 3.0. Right j=7: 7-3/6 = 6.5.
- p=1 right: trunc at pos 6 -> interval [2..5]; same run -> saddle 3.
  Walk 2,3: 5>3, 4>3 -> CLAMP right_x = 3.0. Left j=0: 0+3/6 = 0.5.
=> idx [1,6], prom [6,6], left_x [0.5,3.0], right_x [3.0,6.5].

## 17. trunc_cuts_plateau_runs — `[0,7,7,3,7,7,0]`, gate 0 (rev 2)

Both flavors of a run cut MID-RUN by an interval boundary: equal plateau
peaks 7,7 (collapsed 1) and 7,7 (collapsed 4) around a 3-valley.
- p=1 (V=7): l=min[0]=0; right base walk from p+1=2 THROUGH its own
  plateau tail: [2..6], r=0. prom 7, ref 3.5. Right trunc at pos 4 ->
  interval [2,3]: index 2 is the cut tail of p's OWN 7,7-run -> candidate
  position 2 (value 7), plus run 3(3). Min 3 -> saddle 3. Walk from 2:
  7>3.5, S[3]=3<=3.5 -> j=3: right_x = 3-(3.5-3)/(7-3) = 2.875.
  Left j=0: 0+3.5/7 = 0.5.
- p=4 (V=7): left base [0..3], l=0; r=min[6]=0. prom 7, ref 3.5. Left
  trunc at pos 1 -> interval [2,3]: index 2 is the cut tail of the
  TRUNCATING maximum's 7,7-run -> candidate position 2 (value 7), plus
  3(3). Saddle 3. j=3: left_x = 3+(3.5-3)/(7-3) = 3.125.
  Right j=6: 6-3.5/7 = 5.5.
In both cases the cut run's candidate has value V and can never win the
minimum, so the "position of a partial run" interpretation (leftmost index
INSIDE the interval) is exercised structurally but cannot change output —
consistent with the argument in the impl docstring.
=> idx [1,4], prom [7,7], left_x [0.5,3.125], right_x [2.875,5.5].

## Cross-check result

Rev 1: `verify_vectors.py` ran all 14 vectors against `adversary_impl.py`;
all passed at 1e-9 with no reconciliation needed.

Rev 2: all 17 vectors re-derived/derived by hand first, then cross-checked
against the rev-2 implementation: 17/17 pass at 1e-9. The only revision was
vector 3's `left_x` (4.0 -> 2.0 for peak 5), forced by the spec change
itself, not by a derivation error; the hand re-derivation and the updated
implementation agreed on the first run.
