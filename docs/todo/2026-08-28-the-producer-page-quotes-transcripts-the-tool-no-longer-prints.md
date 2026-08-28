---
status: open
filed: 2026-08-28
---

# The producer page's "checked, not illustrative" transcripts are stale, and one count is wrong by 17

Found by the murderboard's blind verify pass on export contract revision 8. **None of this
was introduced by that revision** — it is pre-existing drift in the same document, surfaced
because revision 8 points a reader at it. Filed rather than fixed to keep the revision's
diff to the width contract.

## The transcripts no longer match the tool

`docs/export_for_producers.md` prints sample `bugarach check` output under the heading
**"This example is checked, not illustrative."** The blind pass wrote the document's own
tiny example to disk byte-for-byte and ran it. Five differences:

- the `export folder: <path>` line is missing from the printed block
- the verdict is on line 2 with a `CONFORMING — ` prefix, not a bare `CONFORMING` at the
  bottom (`conform.py:302-306`)
- the note renders as a short line plus a wrapped detail, not one inline sentence
- the trailing line is now "notes — these read fine and may still not be what you meant:"
- **the `per-event width:` line is absent** — and revision 8 promises that line five lines
  earlier

The last one matters most: the document's own proof-of-checking disproves the sentence
above it. The spec's two-recording sample has the same missing verdict prefix.

**Fix:** re-run and paste. Both documents. Then consider whether a test should pin the
transcripts the way `tests/test_site_dates.py` pins the page's date — a block labelled
"checked" that nothing checks is the same failure class as the ⚠ revision 8 withdrew.

## The silent-ROI count is 76 of 84, not 59

`docs/export_for_producers.md` says the silent-ROI note fires on **59 of the 84**
recordings and glosses it as "a note that fires on 70% of a folder". Measured on the
declared current export: **76 of 84**, which is ~90%.

The reason sharpens the page's own §2: the note counts an ROI silent in *every* stream
(`conform.py:194-196`), so it fires on `20240726_34` despite that recording correctly
sending per-`(roi, stream)` `NA` rows. The note does not credit per-stream silence.

## A code hole behind one of revision 8's sentences

Revision 8 tells producers `bugarach check` will "name any stream that carries none".
There is a reachable case where it does not: a stream whose event rows all carry
`width_def` but leave `width_sec` empty loads with `has_width == True`, `width_def` set,
and an all-NaN width array. `bugarach check` then prints a normal `per-event width:` line
and no "carries none" note, and `load_folder(require_width=True)` does not raise.

`_assemble` collects `defs` from every row that has a time, whether or not its width is
finite (`io.py:396-399`). That contradicts `store.py:79-82`, which says `width_def is None`
means there is no width worth reading.

**It is reachable by imitation**: the current export already writes `width_def` on rows
whose `width_sec` is empty (the `NA` rows), so a producer copying that shape onto real
events lands in it.

**Fix (code):** collect `defs` only from rows with a finite width. Then `has_width` cannot
be True over an all-NaN array and the documented behaviour becomes true.

## Smaller, same source

- **`fwhm` is "reasonable on a fast stream"** understates the risk. The fast stream's
  shipped half-prominence width runs to a **maximum of 50.8 s** (median 0.9 s) across the
  current export. Against a 1 s fixed operating point that is the same failure the sentence
  warns about on slow, one order down. Worth a hedge.
- **Rule 7 says missing is "literally `NA`, never an empty field"**, which contradicts the
  body ("An empty field means the same thing, because that is what a spreadsheet writes"),
  `io.py:75`, the producer page, and the tiny example's own `3,NA,fast,,`.
- **"`!` is an error"** in the spec's "Check it yourself": a load-level refusal — including
  both refusals revision 8 documents — prints `NOT CONFORMING` and a `FAIL` line with no
  per-recording listing at all. `!` only ever prefixes a per-recording error, so a producer
  told to look for `!` will not find one on either new failure.
