---
status: open
filed: 2026-08-28
proposes: SAP010
---

# A contract promised producers that their column was ignored, five days after it stopped being

`docs/export_folder_spec.md` revision 5 asked producers for `width_sec` and attached:

> ⚠ **Nothing in bugarach reads `width_sec` today** — not the loader, not the folder
> check, not any detector.

True on 2026-08-18. False from 2026-08-23, when `load_folder` was taught all four
optional columns. The warning stood until 2026-08-28, and the producer-facing page said
worse — that the width it received was *"read from the file and discarded"*.

**A negative claim about what the code does is the one kind a reader cannot check**, and
in a contract it is load-bearing in the wrong direction: it is what a producer reads when
deciding whether the column is worth maintaining, and it answered no.

## Why the existing gates could not see it

- **Sapper** greps what a commit *adds*. The commit that made the sentence false
  (`8a8b031`) added code; it did not touch the sentence. Nothing connects them.
- **The tests** pin behaviour, not documentation.
- **The todo that did the work** (`2026-08-20-the-contract-asks-for-width-and-drops-it.md`)
  closed on 2026-08-23 with its own "What is left" section — and the contract that *asked
  for* the column was not on the list.

## Why the obvious search confirms the wrong answer

Worth recording because the trap is still armed. `cicada_detect` reaches the column
through `getattr(stream, duration_field)` — a dynamic attribute lookup. Grepping
`detectors/` for `width_sec` finds no *reader* of the input column, but it does not come
back empty: it returns `SceStream.width_sec`, `rate`'s `widths`, locust's own `width_sec`
output and two `bin_width_sec` constants. Those are the **detectors' own output spans**, a
different quantity sharing the word. A full result list reads exactly like confirmation,
which is how the murderboard's first pass on revision 8 concluded "no detector consumes
width" and had to be corrected by a second.

## Proposed SAP010

Precedent is six days old and near-identical in reasoning — **SAP008**
(`tools/sapper.py:189`): *"A claim about what the green tick COVERS is the one thing a
reader cannot check for themselves, so it does not get to go stale quietly."* It is scoped
`include=["tests/**"]` only because that incident was in test docstrings.

- **level:** BLOCK
- **include:** `docs/**`
- **pattern:** roughly `(?i)nothing in bugarach (reads|consumes|uses)|read from the file and discarded|is (currently )?not (even )?carried`
- **message:** the four optional columns have been read since 2026-08-23
  (`io.py::_read_event_rows`). A *negative* claim about what the reader does belongs
  beside the reader, not in the contract — state the obligation, not the implementation.
- **fixtures:** both real sentences exist verbatim in git history, so `fixture_bad`
  and `fixture_good` cost nothing and the selftest is honest.

**Known limitation, stated rather than skipped.** A keyword rule catches these two
sentences and not the next one, which will be phrased differently. It is a tripwire on a
known-bad phrasing, not a general doc↔code checker. The general version is the pin below,
and where a pin is possible it is strictly better.

## Already done, in the same change as revision 8

The higher-value half did not need a new rule, only a test — `tests/test_site_viewer.py`:

- **`test_both_readers_agree_which_widths_reach_a_peak`** — `io.py:97` claims its
  `WIDTH_REACHES_PEAK` is "kept identical" to the viewer's. Nothing checked it; a third
  name in either left both suites green. Now set-equality, both directions, mutation-tested.
- **`test_the_contract_names_the_widths_that_reach_a_peak`** — every accepted string must
  appear verbatim in both producer-facing documents. The rule is an exact-string match, so
  describing it semantically (which both documents did until revision 8) is a promise the
  code does not keep.

That is the shape worth generalising: where a document states a *value* the code holds,
pin the value. SAP010 is for the residue that cannot be pinned.
