# Clean-room implementation workflow (adversarial differential validation)

How clean-room specs in this directory get implemented and validated. Used for
`find_peaks_halfprom` (spec rev 2, accepted 2026-08-11); reuse it for the next
spec or the next revision of an existing one.

## Ground rules

Every spec here is implemented ONLY from its document: no MATLAB, Octave, or
SciPy source, no existing implementations of the same algorithm, no web
references. Two parties work in parallel and must never see each other's code:

- **Primary** — writes the deliverable named in the spec.
- **Adversary** (a separately-spawned agent) — writes an independent
  implementation of the same spec, derives extra test vectors BY HAND from the
  spec's rules *before* running any code, and builds a seeded structured
  fuzzer.

## Steps

1. Both sides implement independently from the spec alone.
2. Both must pass the spec's own vectors at 1e-9 before anything else.
3. The adversary hand-derives hostile vectors (paper first, then cross-check
   against its own impl; any mismatch is reconciled by re-reading the spec,
   not by trusting the code). Both impls must pass them.
4. Differential fuzz: seeded structured signals (integer-grid quantization to
   force exact ties/plateaus, NaN runs, ramps, gates set to exactly-realized
   prominences) run through BOTH impls; any disagreement is adjudicated
   against the spec text, never by majority.
5. Sanity-check the fuzzer itself against deliberately broken mutants — if a
   known-wrong variant isn't detected at a useful rate, strengthen the
   generator with a dedicated shape branch before trusting a zero-disagreement
   result.
6. Spec revisions: the integrator returns divergences as new vectors / a new
   revision header IN the spec file (never reference code). On a revision,
   re-read the whole spec, then both sides update independently and the full
   differential suite reruns.

## Where things live

- Spec: `docs/clean_room/<name>_spec.md` (check the top for a revision
  header every time the user points at it).
- Deliverable: the self-contained file the spec names; after acceptance the
  integrator may fold it into the package (for `find_peaks_halfprom`, now in
  `src/bugarach/detectors/peaks.py` — the tests target the integrated copy).
- Harness: `docs/clean_room/harness/<name>/` — adversary implementation,
  hand-derived vectors + derivation notes, fuzzer.
- Runner: `tests/test_<name>.py` — pytest wiring the spec vectors, the
  adversary vectors, and a differential fuzz pass into the normal suite, so
  the validation reruns forever with `pytest`.

## Ambiguity log (find_peaks_halfprom)

Interpretations both sides reached independently, kept in
`harness/find_peaks_halfprom/adversary_vectors_notes.md`:

- "First local maximum" in the saddle truncation = nearest the peak in the
  walking direction (pinned by `asymmetric_valleys_first_trunc`).
- A run cut mid-run by the truncation boundary takes its leftmost index
  *inside* the interval — proved observationally unreachable as a saddle.
- The spec's "empty base interval → base = V" branch is provably unreachable
  for a true local maximum; implemented defensively anyway.
