---
status: open
filed: 2026-08-13
rule: SAP005
---

# SAP005 catches the common shape but not the correct-looking one

SAP005 fires on a Python string literal that opens an HTML document with
`<html`, `<head` or `<title` — because a document whose first tag is one of
those cannot have declared a charset, and a page served from `file://` with no
charset is read as Latin-1.

It deliberately does **not** fire on a literal opening `<!doctype html>`, and
that is a hole rather than a decision.

## Why

Sapper matches one line at a time (`_scan_lines`). The idiomatic, *correct*
shape is two lines:

```python
INDEX = """<!doctype html>
<meta charset="utf-8">
```

`tools/build_site.py` does exactly this, and the first version of SAP005 blocked
it — a false positive on the public site's own builder, which is the worst kind
of rule. Including `!doctype` in the pattern cannot distinguish that file from
one where the next line is `<title>`.

## The hole

```python
PAGE = """<!doctype html>
<title>No charset here</title>
```

fires nothing, and is the bug SAP005 exists to catch.

## What would fix it

A rule that can look at more than one line — either a `window` field (match the
pattern, then require a second pattern within the next N lines) or a whole-file
mode for rules that opt into it. The window form is smaller and covers this
case: *"if a line opens an HTML document, `charset` must appear within the next
2 lines."*

That is an engine change to `tools/sapper.py`, not a rule change, which is why
it is filed here rather than done inline. Until then SAP005 catches the shape
that actually bit us (`f"""<title>` — a review document rendered as mojibake for
Tony on 2026-08-13) and misses the doctype-first variant.

## Not a substitute

Note the interaction worth remembering: the Artifact pipeline supplies its own
`<head>`, so the same builder code renders **correctly** as a published artifact
and **wrongly** as a file on disk. Testing the artifact proves nothing about the
file. That asymmetry is why this needs to be mechanized rather than remembered.
