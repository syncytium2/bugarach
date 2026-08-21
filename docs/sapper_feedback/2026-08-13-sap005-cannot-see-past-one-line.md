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

---

## 2026-08-18 — the same one-line horizon, from the other direction

`tools/md_to_page.py` builds a page from markdown. Written as
`head_constant + f"<title>..."`, SAP005 blocked it — the produced document was
**correct**, with the charset on line 4, but the rule sees one line at a time and a
fragment whose first tag is the title is indistinguishable from a document with no
head at all.

**Not filed as a false positive to be narrowed away.** The rule fired on a real
shape: a document assembled from fragments, where the head is somebody else's
responsibility, is precisely how a page ships with no charset — and the incident
this rule exists for was exactly that. What the block did was push the code from
"assemble a document from parts" to "write the document as one template", which is
better code *and* makes the guarantee visible to a reader rather than only to the
author. That is a gate doing its job.

**Two notes for whoever maintains the pattern.**

1. **Describing the rule trips the rule.** Both the comment explaining why the code
   was restructured, and this file, have to avoid writing the blocked shape
   literally. That is now three occurrences across two rules (see also the SAP004
   note from 2026-08-17). It is survivable — elide the shape and say it in words —
   but it means the codebase cannot easily document its own gates, and a rule whose
   explanation cannot be written next to the code is a rule people work around
   instead of understanding.
2. **The known gap noted in the message is load-bearing in a good way.** Because a
   literal opening doctype line is not checked, writing the document as one
   multi-line template passes — and that shape is the one that is actually safe.
   So the gap is currently rewarding the right structure by accident. Worth making
   deliberate rather than leaving as an accident, because the next person to
   "tighten" the pattern will remove the only shape that both passes and is correct.
