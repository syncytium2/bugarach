---
status: open
filed: 2026-08-27
---

# A password manager offers to fill the sweep's "from" box

> Tony, 2026-08-27, on the page deployed as `acac81b2`, minutes after the sweep
> range landed: *"also lastpass is trying to put a password into the from box on
> the sweep page."*

The three range inputs per detector — `tRange_<detector>_from`, `_to`, `_n` in
`docs/site/raster_viewer.html` — carry no autofill hints, so LastPass treats them
as fillable and offers a credential in a box that wants a percentile.

Not cosmetic. A manager that fills one of these silently writes a **number the
sweep will then search**, and the panel has no way to tell a value somebody typed
from a value something typed for them. The results block reports the range it was
measured over, which is the saving grace: a nonsense range would at least show up
there rather than in a quoted operating point. But the reader would have to
notice.

## The fix, and the decision inside it

Four attributes, because the managers do not agree on one:

```html
autocomplete="off" data-lpignore="true" data-1p-ignore data-form-type="other"
```

`autocomplete="off"` alone is not enough — Chrome and most managers ignore it on
inputs they have decided are credential-shaped. `data-lpignore` is LastPass's,
`data-1p-ignore` 1Password's, `data-form-type="other"` Dashlane's. Bitwarden
reads `data-bwignore`. Adding all of them is ugly and is what actually works.

**The decision that is not mine to make:** whether this applies to the three new
inputs or to every input on the page. The page carries **46 `type="number"`
inputs** and **not one** of them has an `autocomplete` or ignore attribute of any
kind — the detector settings, the simulate fields, the match tolerance, all the
same shape, and none reported as a problem until now. Two readings:

- **Only the range boxes were reported, so only they are broken.** Possible: the
  `from`/`to` ids are new, and a manager's heuristics are opaque enough that
  three new fields could trip something the other thirty do not.
- **They are all fillable and nobody had noticed.** More likely, and it means
  patching three boxes fixes the report and leaves the defect.

Worth ten seconds with a manager installed before choosing: open the deployed
page, click each panel's inputs, see which ones the manager offers on. That
answer decides between a three-line change and a loop over every
`input[type=number]` in the builder.

## Where

- The inputs are built in `paintRanges()` in `docs/site/raster_viewer.html` — one
  place, so covering the three is genuinely three lines.
- The other number inputs are static markup in the panel section of the same
  file, so covering all of them is a mechanical pass, not a refactor.
- If this becomes a rule, it is a candidate sapper check: a new `<input>` in this
  page without the ignore attributes.
