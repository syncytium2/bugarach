---
status: open
filed: 2026-08-27
---

# The contract warns that nothing reads `width_sec`. The loader has been reading it.

`docs/export_folder_spec.md`, revision 5, carries this in bold:

> ⚠ **Nothing in bugarach reads `width_sec` today** — not the loader, not the folder
> check, not any detector. It is not validated, not carried through, and no result
> changes by supplying it.

That was true when it was written on 2026-08-18. It is not true now. `load_folder`
reads the column, and `tests/test_io.py::test_the_real_export_carries_finite_widths_with_their_rule`
asserts on it over the real export — `has_width`, `has_peak`, `width_def`, one rule per
stream, and that the two streams' rules genuinely differ.

**Why this is worth a todo rather than a quiet edit.** The ⚠ is not decoration; it is
the thing a producer reads to decide whether shipping the column is worth the effort.
Left as it is, it tells interface2 that the column they were asked for is still inert
— which is now an argument for not maintaining it. The correction is small and the
consequence of not making it is that a producer stops sending a column that four
things depend on.

**What it should say instead**, and this needs checking rather than assuming, because
"the loader reads it" and "an analysis uses it" are different claims and only the first
is verified:

- `load_folder` reads `width_sec` / `width_def` into the stream — **verified**.
- No *detector* consumes width — **believed, not checked**. Whoever fixes this should
  grep the detectors before writing the sentence, because the current ⚠ was accurate
  when written and went stale by exactly this route.

**Found while** answering "what did the MATLAB team build to our spec — fast width vs
slow width", 2026-08-27. The answer itself is unchanged and correct: fast carries
`halfprom_width_findpeaks_w`, slow carries `rise_interval_peak_minus_t50rise`, and
`peak_sec - time_sec` reproduces `width_sec` on 150,703 of 150,715 slow rows across
both current exports (the twelve exceptions are ±1e-6 s float noise). The confirmation
note beneath the ⚠ is right. It is only the "nothing reads it" line above it that has
aged.

See also `current_export.toml`, added the same day: the reason the question was hard to
answer at all was that nothing declared which export folder was current.
