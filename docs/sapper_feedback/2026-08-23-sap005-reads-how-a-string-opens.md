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

## Appended 2026-08-23 (built-site-works): it also fires on a regex, and `--all` disagrees with `--staged`

Same rule, two shapes the note above does not cover. Both cost a commit
round-trip while adding `tests/test_site_coherence.py`.

**It cannot tell a pattern from a page.** A literal that reads a title out of a
document —

```python
re.search(r"<title>(.*?)</title>", body, re.S | re.I)
```

— opens with `<title` and blocks. There is no document here to give a charset to;
the string is a *matcher for* documents. Same for a `re.sub` replacement built as
`f"<title>{want}</title>"`.

Two workarounds, and the honest thing is that both are better code anyway, which
is why I am not asking for a rule change:

- put the flags inline so the pattern opens with them — `r"(?si)<title>(.*?)</title>"`;
- rewrite the substitution to replace only the text node, `r"(?<=<title>).*?(?=</title>)"`,
  which does not construct head markup out of a literal at all.

Worth considering all the same: a literal containing `(.*?)`, `(?s`, `\b`, `[^>]`
or ending in a regex quantifier is a pattern, not a page.

The wrapped-literal case from the note above also bit again, and is worth one
concrete example since it is easy to write by accident:

```python
page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<title>x</title>\n<style>body{color:red}</style>\n'   # <- blocks
        '<h1>the content</h1>')
```

The whole literal opens correctly; the *second line of it* opens with `<title`.
Rewrapping so no continuation line starts with a tag fixes it.

## Third: `--all` says "clear" about files it did not look at

This is the one I would actually change something about.

`scan_all()` iterates `_tracked_files()`. **A new file that has not been
`git add`ed is not scanned**, so the loop that the instructions here encourage —
write the file, run `python tools/sapper.py --all`, see `sapper: clear`, commit —
gets a clean bill of health for a file sapper never opened, and then the
pre-commit hook blocks on it. Which is the gate working exactly as designed; the
problem is the `clear` that came before it.

That is worse than either false positive above, because a gate that reports clean
and then blocks anyway is one people learn to read as noise. Cheap fixes, in
preference order:

1. have `--all` scan untracked, non-ignored files too — they are about to be
   committed, which is the only reason to scan anything;
2. failing that, make the summary line count what it saw: `sapper: clear (312
   tracked files; 1 untracked file NOT scanned — git add first)`.

Either one turns a silent gap into a visible one. The second is honest without
changing what the rule does to anybody.
