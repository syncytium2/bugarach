---
status: open
filed: 2026-09-03
---

# `analysis_*` bounds reject the contract's own spelling of missing

Found while building the stage-one hard tell, on a test fixture rather than on real
data — so nothing has been mis-analysed by it, and the next producer to send it will
be told their conforming folder is unreadable.

## What happens

`docs/export_folder_spec.md` closes with rule 7: **"Missing is written as missing —
literally `NA`, never an empty field and never a plausible substitute."** A producer
who follows it on the two optional analysis columns gets:

```
ValueError: could not convert string to float: 'NA'
```

from [`src/bugarach/io.py`](../../src/bugarach/io.py), in the `regions.csv` reader:

```python
analysis_start_sec=float(a0) if a0 else None,
analysis_end_sec=float(a1) if a1 else None))
```

`a0` is truthy for the string `"NA"`, so the guard passes it to `float()`.

## Why it is worth a row of its own

**The empty field works and the documented spelling does not**, which is the exact
inversion of what the contract asks for. And the failure is a bare `ValueError` from
inside the loader rather than a message naming the file and the line — so a producer
gets a traceback where every other refusal in this reader gets an address. Two of the
neighbouring checks in the same function are models for what this should say.

`NO_EVENT` in the same module already carries the vocabulary — `("", "na", "nan",
"none", "null")`, case-insensitive, with the bare empty field included *because that
is what a spreadsheet writes*. The region reader does not use it.

## Scope, and one question inside it

The fix is small. What is not obvious is whether **`start_sec` / `end_sec`** should
take `NA` too. They are required, so `NA` there is a producer error rather than a
missing optional value — and it should say so in those terms rather than crash with
the same `ValueError`. Probably: accept the vocabulary on the optional pair, and give
the required pair a message that names the file, the line and the column.

Worth checking the same shape on every other optional numeric the loader reads before
closing this — the defect is a guard written as `if a0` where the vocabulary was
meant, and that is a pattern rather than one line.
