---
status: open
filed: 2026-09-16
---

# `sapper --all` crashes on Windows when a finding's line holds a non-ASCII character

Running the tree-wide scan on Windows dies partway through printing its findings:

```
File "tools/sapper.py", line 582, in report
    print(f"{rule.level} {rule.id} {path}:{lineno}: {line.strip()}")
UnicodeEncodeError: 'charmap' codec can't encode character '⚠' in position 191
```

The console is cp1252; the offending line contains `⚠`, which this project's own docs use freely as a
status marker. So **the scan fails on exactly the files whose conventions the project mandates.**

## Why nobody hit it before

- `--staged` (the commit hook) only prints findings for staged files, and had none with non-ASCII.
- CI runs on Linux, where stdout is UTF-8.

So the gate that matters is green and the tool a person runs by hand is the one that breaks — the same
shape as the report-in-the-repo incident in CLAUDE.md: the path built for a human is the one that fails.

**It fails loudly, which is the saving grace.** A traceback is not a silent wrong answer: nobody has
shipped a clean bill of health from a crashed scan. But it stops the scan partway, so any finding after
the first non-ASCII one is unreported, and a person reading a truncated list has no way to know it was
truncated.

## Fix

Reconfigure stdout at entry rather than asking callers to set `PYTHONIOENCODING`:

```python
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```

`errors="replace"` matters as much as the encoding: a console that genuinely cannot render a glyph should
print a replacement character, not take the scan down with it.

Worth a test that feeds `report()` a finding containing `⚠` with a cp1252 stdout and asserts it does not
raise.

## Workaround until then

`PYTHONIOENCODING=utf-8 python tools/sapper.py --all`

Found while adding SAP017 (2026-09-16) — the scan crashed, and the crash was mistaken for a finding at
first glance.
