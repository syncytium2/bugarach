# SAP018 — one vocabulary for what the camera sees

**Filed with the rule.** Scope: the plain-language templates and their builder.

## The ruling

Tony, 2026-09-16, reading the new interval-rule section: "a cell brightened 13.4 times an hour" is not
ok; "a cell with 13.4 events per hour" is. Then:

- define a calcium event **once, at the start**, as an increase followed by a decrease in brightness,
  and after that say events;
- no "brighten" and its relatives;
- **calcium event** for one cell's event, **coordinated event** for a coordinated one;
- "synchronized" only when another author uses it, and then in quotes.

## Why a rule and not a one-off edit

The document had grown three vocabularies for one observation — "brightens", "lights up", "is lit" —
beside the defined term it already had. A reader who meets "brightened" after "calcium event" cannot tell
whether they are the same thing, and the doc's own note 21 had already cut "active" for saying more than
was observed. Forty-odd places needed changing across the templates, the figure text and the darkroom
prose; the next section written would have brought them back.

"Synchronized" is a different fault with the same cure. It is Herbison's and Moore's word for their own
rules, and using it unquoted makes it this document's claim about the cells.

## What it matches, and what it deliberately does not

- `brighten`, `brightens`, `brightened`, `brightening(s)`, `light(s) up`, `lit up`.
- `synchronized` / `synchronous` **not** preceded by an opening quote (`"`, `“`, `‘`, `'`).

It does **not** match:

- `brightness` — the definition needs it, once;
- `synchronization` — it appears in paper titles and in quoted method names ("SPIKE-synchronization"),
  and a line matcher cannot tell a title from prose;
- `glow`, `flash`, `dim` — rewritten by hand this time, too common in other senses to block on.

## What it cannot catch

A quote that opens on the previous line, and a `synchronized` that sits inside quotes but is not another
author's term. Both need a reader.

## Not caught by this rule, and fixed by hand

`real_prose.json` in the darkroom holds the real-recording sentences (FOUNDATIONS §5) and is outside any
repo scan; two "brighten" uses there were reworded directly.
