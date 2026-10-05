---
status: open
filed: 2026-09-22
---

# Sapper crashes instead of reporting, on Windows, when a finding's line carries `⚠`

**Found** by a WSMIP065 session on 2026-09-22, running `python tools/sapper.py --all`
before starting the overnight bench work. The scan does not finish; it ends in a
traceback:

```
UnicodeEncodeError: 'charmap' codec can't encode character '⚠' in position 191
  File "tools/sapper.py", line 551, in report
    print(f"{rule.level} {rule.id} {path}:{lineno}: {line.strip()}")
```

## What is actually wrong

`report()` prints each finding's **source line verbatim**. Python's `sys.stdout.encoding`
on this machine is `cp1252`, which has no `⚠` (U+26A0), so the `print` raises and the
process dies on the first finding whose line carries one. Everything after that finding
goes unreported, and the exit code is a crash rather than a verdict.

**The input side of this was already fixed and the output side was not.** `scan_staged`
carries the comment:

> `encoding="utf-8"` is load-bearing on Windows: without it the diff is decoded in the
> locale codepage, the reader thread swallows the `UnicodeDecodeError`, and `.stdout`
> comes back `None` — so any staged ▼ or ✕ crashed the pre-commit hook (2026-09-14).
> `check_quotes.py` hit and fixed the same thing in #535.

Same defect, same file, other direction. Reading was hardened; writing was not.

## Why it matters more than a broken `--all`

`.githooks/pre-commit` ends with `exec python3 tools/sapper.py --staged`. `scan_staged`
only inspects **added** lines, so the gate crashes when a newly added line both matches a
rule and carries `⚠`. The commit is then refused with a traceback that reads like a broken
tool rather than a refused rule — and the natural reaction to a broken gate is to work
around it.

This is not hypothetical on the lines a session is likely to add. Three tracked files
already carry lines that both trigger a rule and carry the glyph:

| file | rule |
|---|---|
| `docs/INDEX.md:69` | SAP015 |
| `docs/generator.md:204` | SAP015 |
| `src/bugarach/bench.py:162` | SAP015 |

The third is the one to look at: `bench.py` is the file the 2026-09-22 overnight work
edits, and this repository writes `⚠` into exactly the docstring tables and provenance
notes that job touches. SAP015 (`"data"` is plural) fires on ordinary prose, so the two
conditions meet easily.

## The fix

One line, at the top of `main()` or beside the other Windows notes:

```python
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```

`errors="replace"` rather than a bare `encoding` so a console that genuinely cannot render
the glyph degrades to `?` instead of trading one crash for another. Verified by hand:
`PYTHONIOENCODING=utf-8 python tools/sapper.py --all` completes and exits 0, while the bare
form dies at the first `⚠`.

**Add the case to `--selftest`**, which is the part that keeps it fixed. The selftest proves
every rule can fire; it does not prove a finding can be *printed*. A fixture whose line
carries a non-Latin-1 character, reported through the same path, would have caught this and
would catch the next glyph.

## Wider than sapper

`read_text()` with no `encoding=` has the same failure mode wherever it walks the repo's own
source, which carries em-dashes, `Grün`, and `×`/`÷`/`√`. Two such reads made
`tests/test_where_the_data_are.py` and `tests/test_background_is_measured.py` red on Windows
while green on Linux CI; both are fixed in the same PR as the bench constants. **There are
242 encoding-less `read_text()` calls in the tree.** Most read ASCII JSON out of `tmp_path`
and are harmless, so a blanket sweep is the wrong shape — but a check that flags the ones
reading **repo source** would be worth more than fixing these two by hand, and is the
natural companion to the selftest case above.

The general point is the one worth keeping: **CI is Linux and both workstations are
Windows**, so this whole class is invisible to the suite that gates merges and visible only
to the machines that do the measuring.
