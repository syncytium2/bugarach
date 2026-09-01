---
rule: SAP005
status: done
filed: 2026-09-01
---

# A rule that fires on vendored code can only be answered with the override

## What happened

Vendoring `third_party/draughtsman/` (the figure pipeline, 2026-09-01) blocked at
the first commit on two SAP005 findings:

```
BLOCK SAP005 third_party/draughtsman/render.py:196: out.append(f"<title>{escape(title)}</title>")
BLOCK SAP005 third_party/draughtsman/render.py:275: f"<title>{escape(spec.title)}</title>\n"
```

SAP005 wants `<meta charset="utf-8">` beside a `<title>`, because a page opened
over `file://` with no declared charset is read as Latin-1 and every `—`, `×` and
`·` becomes mojibake. That is a good rule and the incident behind it was real.

**Both findings are false positives.** Those are SVG `<title>` elements — the
accessible name of a figure — and an SVG has no `<head>` to put a charset in. The
existing `2026-08-23-sap005-reads-how-a-string-opens.md` records the same rule
matching on shape rather than meaning; this is another shape it cannot tell apart.

## Why the false positive is not the point

Suppose it had been a true finding. **It would still have been unfixable here.**
`CLAUDE.md`'s "Vendored copies" says a vendored file is never edited in place: a
refresh is a re-copy, and a re-copy silently reverts any local patch. So the only
available answers were:

1. edit the copy — reverted by the next `cp`, and the fix disappears without a
   diff to notice it going;
2. `ALLOW_SAPPER=1` — every commit, forever, on a path that will keep matching;
3. fix it upstream and re-vendor — correct, and unavailable in the moment.

Option 2 is the one that actually happens under time pressure, and it is the
expensive one: an override used routinely stops reading as an exception. The gate
does not lose one file, it loses the habit that makes every other file's finding
land. **A rule that fires where it cannot be obeyed trains people out of the
rule.**

## What was done

`tools/sapper.py` grew a `GLOBAL_EXCLUDE = ("third_party/*",)`, checked in
`_applies` before any rule's own include list, with the reasoning in the comment.
Global rather than per-rule: a new rule added next month would otherwise have to
remember, and the property being asserted is about the *path*, not about SAP005.

`sapper --all` is clear; `--selftest` still reports 12 rules, 0 failures.

## What this does not excuse

Vendored code is not exempt from being *correct* — it is exempt from being
**patched here**. A genuine finding in `third_party/` is a bug report to the
upstream repo, and the fix arrives by re-vendoring at a newer stamp, which
`tools/check_vendor_freshness.sh` already tracks. The exclusion moves where the
work happens; it does not delete it.

The general form, which outlives SAP005: **a gate should range over what the repo
can change.** Anything else is either noise or an override in training.
