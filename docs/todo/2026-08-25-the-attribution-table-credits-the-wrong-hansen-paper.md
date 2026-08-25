---
status: open
filed: 2026-08-25
---

# The attribution table credits the wrong Hansen paper, and the glossary two files away already knows

`docs/detector_history.md` §4 line 281 attributes greatest-of selection to **Hansen & Sawyers,
IEEE T-AES AES-16(1), Jan 1980** and marks it **read in full**. That paper exists, is correctly
cited, is on the shelf, and is the detectability-**loss analysis** — the source of the "0.1 to
0.3 dB" figure §5.4 quotes.

**It is not where greatest-of comes from.** The origin is **V. G. Hansen, "Constant False Alarm
Rate Processing in Search Radars", IEE Conf. Publ. 105, *Radar — Present and Future*, London,
1973, 325–332.**

The repo half-knows this already, which is what makes it worth filing: `docs/GLOSSARY.md` and
`docs/detector_history.md:28` both say **"GO-CFAR (Hansen 1973)"**. Only the attribution table
— the one a reader would quote, and the one a downstream page was built from — says 1980.

## Why this is not a citation-style nitpick

**§4 has already made this exact error once and corrected it.** An earlier draft credited the
censoring fix to Gandhi & Kassam; Rohling 1983 already credits Weiss and Rickard & Dillard, so
Gandhi & Kassam is the standard *analysis*, not the origin. The correction is recorded in §4's
own prose. The Hansen row is the same shape — a well-known later analysis standing in for an
earlier origin — sitting in the same table, uncorrected.

Role 2 of the murderboard on `loco_coact_as_cfar` found it precisely because the new process
requires the citation role to run as its own agent on any deliverable that attributes a method.
A single-pass self-review would have inherited the drafter's search history and stopped where
the table stopped.

## What has to happen, and the part that cannot be done from here

- Fix line 281: origin **Hansen 1973**, with Hansen & Sawyers 1980 named as the loss analysis
  that §5.4 actually quotes.
- **Hansen 1973 is not on the shelf.** `<darkroom>/bugarach/lit/radar/` holds five PDFs — Finn
  & Johnson, Rohling, Gandhi & Kassam, Hansen & Sawyers, Weinberg. So the origin claim currently
  reaches this repo second-hand, and §7's standing claim that every radar attribution is matched
  against a PDF on the shelf **does not hold for this one**. Either acquire it, or mark the row
  as attributed-but-unread, which is what the rest of the table does honestly elsewhere.
- The **read in full** marking on that row is wrong either way: what was read in full was the
  1980 paper, which is not the paper the row is claiming.

Related: [`2026-08-24-the-history-document-describes-a-tree-that-has-moved-on`](2026-08-24-the-history-document-describes-a-tree-that-has-moved-on.md)
is the other open correction to the same document, and the two should probably land together.
Run record: [`loco_coact_as_cfar_2026-08-25`](../reviews/loco_coact_as_cfar_2026-08-25.md) §E1.
