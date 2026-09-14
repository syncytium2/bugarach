---
status: open
filed: 2026-09-14
---

# A lane drawn over part of a recording turns an outside call into a bar across the lane

`bugarach.ui.diagnostic._spans` clips each detection to the extent it is given:

```python
out.append((max(a, ext[0]), min(a + max(ww, floor), ext[1])))
```

For a call whose onset lies **after** `ext[1]`, that is `(a, ext[1])` with `a > ext[1]` — an
inverted rectangle, which bokeh draws from the call back to the right edge. A call **before**
`ext[0]` becomes a sliver pinned to the left edge. Either way, a call outside the window is drawn
inside it.

**Why nobody saw it.** Every caller until 2026-09-14 passed the whole recording as `ext`, so no
call could lie outside it. `tools/make_mechanism_figure.py` was the first to pass a 3-minute
window, and its first render showed each detector's lane as one solid bar from the first
out-of-window call to the right edge. It now filters calls to the window before calling
`lane_panel`, and says why at the site.

**The fix** is one line in `_spans`: skip a span with `a > ext[1]` or `a + width < ext[0]`
instead of clamping it. Scoring inside `lane_panel` (the ✕ verdicts) uses the unclipped onsets,
so it is unaffected. A test would pass a sub-extent with one call on each side and assert no
rectangle is drawn for either.
