---
rule: SAP005
kind: note
filed: 2026-08-23
---

# SAP005 reads how a string OPENS, and the message does not say so

Hit while adding `tests/test_site_dates.py`. Recording it because I misdiagnosed
it twice before reading the rule, and the message is what led me astray both
times.

## What the rule actually does

```python
pattern = r"""["']{1,3}\s*<\s*(html\b|head\b|title\b)"""
```

It fires when a Python string literal **begins** with `<html`, `<head` or
`<title`. It does not look for a charset at all. `fixture_good` is the real
specification: a page literal should open with `<meta charset="utf-8">`.

That is a good heuristic and I am not asking for it to change.

## Where the message misleads

It says *"An HTML document built here must open with `<meta charset="utf-8">`"*
and then, parenthetically, *"sapper matches per line, so a literal opening
`<!doctype html>` on its own line is not checked"*.

Read that as a person hitting the block, and the obvious inference is *"put a
charset somewhere in the string"*. So I did:

```python
page = '<html><head><meta charset="utf-8"></head><body>x</body></html>'
```

Still blocked — correctly, since it opens with `<html`. The message gave me no
way to work out why, and the parenthetical about line matching pointed at a
different mechanism entirely. I wrote a wrong feedback note about line-wrapping
before reading `sapper.py`.

**Suggested wording**, which costs nothing and would have saved both rounds:

> A page literal must **start** with `<meta charset="utf-8">` (or `<!doctype
> html>`) — not merely contain one. Opened from disk (file://) a page with no
> declared charset is read as Latin-1 …

Naming `<!doctype html>` as a sanctioned opening rather than as a "known gap"
also matters: it is the correct way to open a real document, so a page that does
it is right, not slipping past.

## The fixture

Fixed by making it an actual document — doctype, then charset — which is better
than what I started with. No rule change needed.

## Second, smaller thing

The block printed the same finding **twice** for one wrapped string literal (once
per line). Deduplicating by (rule, file, line) would make a multi-line hit read as
one problem instead of two.
