---
status: open
filed: 2026-09-21
---

# The chorus-collapse page's two remaining majors: Figure 6 by colour alone, Figure 4 with no legend

The page is [`docs/learned/chorus_collapse/index.html`](../learned/chorus_collapse/index.html), built by
`tools/diagnose_chorus_collapse.py`. After Tony's ruling on the blind verify round (#674) and the
census re-run (#687), its residual list is down to **zero blocking findings**. These are the two
majors left, both **figure craft** rather than claims — no number or conclusion depends on them.

They were left on purpose, not missed. Tony ruled on four specific items; redrawing figures was not
one of them, and the page's blocking count had run 3 → 4 → 6, so every unrequested edit was a new
piece of unreviewed text. Both were raised by the craft gate (murderboard role 10) in round 3 **and
again** in its blind re-run against the repaired page, so neither is a regression.

The evidence is archived in
[`docs/reviews/chorus-collapse-verify-2026-09-20-roles/10-ship-it-round4.md`](../reviews/chorus-collapse-verify-2026-09-20-roles/10-ship-it-round4.md),
findings F1 and F2, with renders named there.

## Figure 6, one change at a time — five series separated by colour alone

Figure 6 overlays five training-loss curves. Line style only splits solid from dashed, and the two
dashed ones differ only by colour. Under a deuteranope colour simulation **the as-run curve and the
"replayed at lr 0.01" curve render as the same yellow-green** — and that pair is exactly the contrast
the figure exists to show: the same fit, trained at a lower learning rate, trains. In greyscale the
four coloured strokes land at 128, 140, 149 and 166 out of 255.

**What would close it:** give each replay its own dash pattern, or label each line at its end, and
move "replayed at lr 0.01" off amber onto a blue or purple. Figures 5 and 7 already keep the as-run
curve orange against blue replays; matching them would fix it too.

## Figure 4, the earlier diagnosis's test — no on-figure legend

Figure 4's whole colour key is the last clause of a five-line grey caption. Working and collapsed get
small coloured squares, but the third category is identified by the **word** "gray", set in the
caption's own grey, with no swatch. The hollow "below 10⁻⁵, drawn on the floor" glyph is explained only
in the same buried sentence. Figure 3, beside it and in the same idiom, carries a proper on-figure
legend row — so the page is inconsistent with itself.

**What would close it:** add the Figure-3-style legend row inside Figure 4's SVG — working, collapsed,
untrained, and the hollow floor glyph.

## Before either lands

This page has been bitten twice by cross-version determinism, both times caught by CI rather than by
review. Neither fix should touch a statistic, but confirm the page still rebuilds **byte-identically
on Python 3.11, 3.13 and 3.14** before pushing, and re-run the craft gate against the new render — a
legend row or a new dash pattern is a layout change, and a fix that moves a shape is where the next
overlap comes from.

The same report lists ten minors (bare counts in Figure 4's row labels, Figure 5B's axis range and
label against Figures 6 and 7, SD used before it is defined, a panel letter wedged into a gutter).
Worth taking in the same pass; none is required.
