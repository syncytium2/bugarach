# Hand derivations for `adversary_vectors.json` (pattern_jitter, spec revision 1)

Every expected value below was derived by hand from `docs/clean_room/pattern_jitter_spec.md`
**before any code ran on it**, then cross-checked against `adversary.py` and against the
brute-force enumerator in `fuzz.py` (which walks the onset-by-onset definition, not the count
table). The primary, `src/bugarach/pattern_jitter.py`, was never read; it is imported as a black
box. Any mismatch on the cross-check is recorded at the end of this file.

Notation, as in the spec: patterns `P0 .. P(d-1)`; `G_p = span_p + R + 1`; `A_p` the allowed
starts; `W_p` the chosen start; `k = u * 2**53`; the pick is the smallest `r` with
`2**53 * C_r > k * T`. "Block of t" is `start + L*floor((t - start)/L) .. + L - 1`.

## Support vectors

**`interval_R_and_R_plus_1`** `[0, 2, 5, 9]`, window `(0, 12)`, `L = 4`, `R = 2`.
Intervals 2, 3, 4. The interval of exactly `R` joins `{0, 2}` into one pattern (span 2); the
interval of `R + 1` starts a new one. Patterns `{0, 2}` (fixed), `{5}` (free), `{9}` (fixed).
`G0 = 2 + 3 = 5`, so `W1 >= 5`; `G1 = 3`, so `W1 <= 6`; block of 5 is `4..7`. `W1 in {5, 6}`,
count 2. Kills any reading that splits patterns at `>= R`, and any gap that forgets the fixed
first pattern's span (which would admit 4, since the block starts there).

**`span_leaves_block_offset_start`** `[3, 8, 9, 10, 15]`, window `(3, 16)`, `L = 5`, `R = 1`.
Patterns `{3}`, `{8, 9, 10}` (span 2), `{15}`. Block of 8 anchored at 3 is `3 + 5*1 = 8 .. 12`.
`W1 >= 3 + 2 = 5`; `W1 + 2 + 2 <= 15` gives `W1 <= 11`. So `W1 in 8..11`, count 4. At
`W1 = 11` the pattern's onsets are 11, 12, 13: the last one is **outside** the block `8..12`
and must not be clipped. Anchoring at 0 instead makes the block `5..9` and the count 5.

**`duplicates_in_both_fixed_patterns`** `[4, 4, 9, 14, 14]`, window `(0, 20)`, `L = 5`, `R = 0`.
Zero intervals are `<= R`, so `{4, 4}` and `{14, 14}` are the fixed patterns, span 0, `G = 1`.
The free `{9}`: block `5..9`, `W1 >= 5`, `W1 <= 13`. Count 5. The onset at index 3 belongs to
the fixed last pattern even though it is not the last onset.

**`triple_same_frame`** `[7, 7, 7]`, `R = 0`: one pattern, `d = 1`, count 1, no draw.

**`two_patterns_of_duplicates`** `[0, 0, 5, 5]`, `L = 2`, `R = 0`: `d = 2`, both fixed, count 1,
no draw — four onsets and still zero calls to `rng`.

**`R_equals_largest_interval`** `[2, 5, 9, 12]`, `R = 4`: intervals 3, 4, 3, all `<= 4`. One
pattern; count 1; no draw.

**`L_exceeds_window`** `[0, 3, 7]`, window `(0, 8)`, `L = 100`: the block of 3 is `0..99`.
`W1 in 1..6`, count 6. `u = 0.5`: `T = 6`, `k*T = 3 * 2**53`, first `C_r = r` exceeding 3 is
`r = 4`, so frame 4.

**`shared_block_pair`** `[0, 2, 3, 6]`, window `(0, 8)`, `L = 4`, `R = 0`. Both free onsets
share the block `0..3`. Valid `(W1, W2)` with `1 <= W1 < W2 <= 3`: `(1,2), (1,3), (2,3)`, count
3. Tables: `N2 = 1` on `0..3`; `N1(1) = 2`, `N1(2) = 1`, `N1(3) = 0`.
`u = (0.5, 0.5)`: `k*T = 1.5 * 2**53`, `C_1 = 2` exceeds it, `W1 = 1`; then candidates `2, 3`,
weights `1, 1`, `k*T = 2**53` ties `C_1 = 1`, strict rule moves on, `W2 = 3`: `[0, 1, 3, 6]`.
`u = (0.6875, 0)`: `k*T = 33 * 2**49` against `C_1 * 2**53 = 32 * 2**49`: not greater, so
`W1 = 2`; the only candidate left is 3, which still consumes the second draw.

**`weighted_strict_tie`** `[0, 4, 6, 9, 14]`, window `(0, 16)`, `L = 3`, `R = 2`. Patterns `{0}`,
`{4, 6}` (span 2), `{9}`, `{14}`; `G0 = 3`, `G1 = 5`, `G2 = 3`. Blocks `3..5` and `9..11`;
`W2 <= 11`. `W1 = 3`: `W2 in 9..11` (3); `W1 = 4`: 3; `W1 = 5`: `W2 >= 10` (2). Count 8.
`u = (0.75, 0)`: `T = 8`, weights `3, 3, 2`, `k*T = 6 * 2**53` ties `C_2 = 6` exactly; strict
rule takes `r = 3`, `W1 = 5`; then `W2 = 10`: `[0, 5, 7, 10, 14]`. `>=` would give `W1 = 4`.
`u = (0.5, 0.5)`: `k*T = 4 * 2**53`, `C_2 = 6` exceeds, `W1 = 4`; then `9, 10, 11` equal,
`T = 3`, `k*T = 1.5 * 2**53`, `C_2 = 2` exceeds, `W2 = 10`.

**`float_share_trap`** `[0, 7, 14]`, window `(0, 15)`, `L = 5`, `R = 0`. Five equal candidates
`5..9`. `float(0.6)` is `5404319552844595 / 2**53` (0.6 * 2**53 = ...595.2, rounded down — the
reason `repr` of the stored value reads 0.59999999999999997...). `k*T = 27021597764222975`,
`3 * 2**53 = 27021597764222976`: the third running total exceeds it by one, so frame 7.
A floating-point rule "first `C_r / T > u`" computes `3/5` as the same double as `u`, rejects
`r = 3` and returns frame 8. This is the smallest vector I found that separates the integer
rule from a float one without overflow.

**`anchor_changes_count`** `[5, 9, 13, 15]`, window `(1, 16)`, `L = 4`, `R = 0`. Anchored at 1:
blocks `9..12` and `13..16`; `W1 >= 6` is slack; `W2 <= 14`; `W2 > W1` is slack. `4 * 2 = 8`.
Anchored at 0 the blocks are `8..11` and `12..15` and the count is `4 * 3 = 12`, so this vector
kills the wrong anchor on the count alone. `u = (0.5, 0.5)`: `T = 8`, weights 2 each,
`k*T = 4 * 2**53`, `C_3 = 6` first exceeds it, `W1 = 11`; then `13, 14`, the tie at `C_1`
moves on, `W2 = 14`.

**`count_one_with_zero_weight_tail`** `[0, 3, 6]`, window `(0, 7)`, `L = 3`, `R = 2`. The block
`3..5` lists three candidates, but only 3 keeps `6 - W1 > 2`. Weights `1, 0, 0`, count 1, and
the draw is still consumed. At `u = 1 - 2**-53`, `k*T = 2**53 - 1 < 2**53 * 1`, frame 3.

**`single_candidate_draws`** `[0, 2, 9]`, window `(0, 10)`, `L = 3`, `R = 1`. Block `0..2`,
`lo = 0 + 2 = 2`: the candidate list is `{2}` alone. Count 1; one draw.

**`empty_in_empty_window`** `[]`, window `(5, 5)`: `start == end` is not `start > end`, so it is
valid; the empty train is its own resampling; no draw.

**`pattern_tail_in_next_block`** `[0, 4, 5, 8, 12]`, window `(0, 13)`, `L = 4`, `R = 1`.
Patterns `{0}`, `{4, 5}` (span 1), `{8}`, `{12}`; `G0 = 2`, `G1 = 3`, `G2 = 2`. Blocks `4..7` and
`8..11`; `W2 <= 10`. `W1 = 4, 5, 6, 7` leave `3, 3, 2, 1` completions, count 9. At `W1 = 7` the
pattern's tail sits at 8, inside the next pattern's block, which the next pattern then clears
at 10. `u = (1 - 2**-53, 0)`: `k*T = 9 * 2**53 - 9`; `C_3 = 8` does not exceed it, `C_4 = 9`
does, `W1 = 7`; then candidates `10, 11` with weights `1, 0`, `W2 = 10`.
`u = (0.5, 0.5)`: `k*T = 4.5 * 2**53`, `C_2 = 6` exceeds it, `W1 = 5`; then `8, 9, 10, 11` with
weights `1, 1, 1, 0`, `T = 3`, `C_2 = 2 > 1.5`, `W2 = 9`.

## Error vectors

`L_bool` / `R_bool`: `bool` is an `int` subclass in Python and the spec rejects it by name.
`decrease_after_duplicate`: the decrease comes after a repeat, so a check that only compares
distinct values would miss it. `empty_start_after_end_by_one`: the window is checked even when
the train is empty. `last_onset_equals_end_single`: half-open window with one onset.
`first_onset_before_nonzero_start`: the bound is `start`, not 0.

The type cases JSON cannot express (numpy float `L`, bool-dtype train, 2-D empty train, and the
valid numpy-integer and unsigned inputs) are in `tests/test_pattern_jitter.py`.

## Big vectors (built from their rule)

**`five_pow_thirty`**: `train = [5*j for j in range(32)]`, window `(0, 156)`, `L = 5`, `R = 0`.
Thirty free singletons, disjoint blocks `5j .. 5j+4` (so `G = 1` never binds), fixed ends at 0
and 155. Count `5**30`, which needs 70 bits: past `2**64` and not exact in a float64.
All draws 0.5: every step has five equal weights, `2**53 * r > 2.5 * 2**53` first at `r = 3`,
so every free onset moves to `5j + 2`. All draws 0.6: by the `float_share_trap` arithmetic,
again `r = 3`, `5j + 2`; the float rule would give `5j + 3` on all thirty.

## Cross-check record

Run on 2026-09-11 after the derivations above were written: `adversary.py` and the
brute-force enumerator in `fuzz.py` reproduced every one of this file's support sets, counts,
marginals and scripted outputs, every one of the spec's own support, scripted, seeded, error
and overflow vectors, and both big vectors. **No mismatch on the first run, so nothing was
revised.**
