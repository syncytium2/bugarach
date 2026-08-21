# Murderboard run — the uniform raster (figures + captions)

- upstream:  syncytium2/murderboard @ 57445b4
- vendored:  57445b4 (`murderboard_freshness.sh --refresh --verbose` → current)
- freshness: current
- artifact:  `docs/generator/coord_diagnostic_bench_quiet{,_hero}.png` + the eleven
  `generator_*.png` sweeps + the prose that captions them (README, `docs/generator.md`,
  `legend_html`). Hero: `03990c3` → rebuilt after the last fix.
- roles:     11 of 11 run — 1–4 and 8–11 as subagents, 5–7 in the main thread
- rounds:    1 verify round on the rebuilt figures

**The change under review.** Every raster inked the onsets falling inside a detected
or planted window and muted the rest. Tony: *"it's bad to bold the rasters
participating in an event. make all rasters the same and use only markers at the
top."* `raster_panel` now draws one ink for every onset, `member_spans` and
`_is_member` are gone, and detections live in the lanes and markers above.

## Role ledger

| # | Role | Findings | What was checked |
|---|---|---|---|
| 1 | Prove It | 4 | Every quantity in the changed captions recomputed. The `.txt` sidecar and the `.png` proved to be one run by reconstructing all six score rows from the per-lane detection counts (e.g. CICADA `111 − 85 probe = 26` scored, `12/26 = 0.46` precision) — which independently confirms the README's claim that probe firings leave both numerator and denominator. |
| 2 | DOI or Die | 0 | No new external reference is introduced by any changed text; the only proper nouns are the six in-project detector names, already attributed in the README. "No findings, and that is what I checked." |
| 3 | Cross-Examiner | 6 | Whole-tree grep for the old convention in prose; every other raster in the tree (viewer, site raster viewer, explainer figures) confirmed single-ink; the todo checked against the real publication surface; GLOSSARY collision on "membership"; a counting-basis clash between `generator.md` and the diagnostic. |
| 4 | Reviewer 2 | 6 | Attacked the justification field-by-field across all six detector result classes, and the change itself under *relocate, don't delete* and *can the alarm ring?* |
| 5 | Kill Your Darlings | 2 | The new prose against `writing_conventions.md`; folded into the rewrites below. |
| 6 | RTFM | 1 | Read the six detectors' returns before trusting the docstring's claim about them — this is where CICADA's internal `members` set was found. |
| 7 | Reinventing the Wheel | 1 | Whether a second raster implementation still grades: `ui/app.py::_raster` was **already** single-ink, so the change makes the figure agree with the viewer rather than inventing a convention. |
| 8 | You Lost Me | 5 | Every render opened and described in one sentence, at publication width and at 100%. |
| 9 | Show, Don't Tell | 3 | Old vs new payload, per figure, judged on the render. |
| 10 | Ship It | 6 | Mechanical table: 16 embed paths, dimensions, weights, legibility at width, legend marks counted in the render, alt text, `sapper --all`, mtimes. |
| 11 | Start With the Problem | 4 | The spine of both changed sections, order only. |

## What survived review, and what it cost

**The justification was wrong three times, in my favour each time.** The first draft
said no detector reports which events it recruited. CICADA computes exactly that set
(`np.flatnonzero(raster[…].any(axis=1))`) and returns its size; binned SCE and LoCo
build it too. A second draft said "a window and a participant count" — false for
rate+context, which reports no participation quantity at all. Verified field by
field: `nrois` (CoactDetect), `n_participating_rois` (SPIKE-synch), `mag_total`
(LoCo, SCE, CICADA), nothing (rate+context). The claim that survives is narrow and
true: **their returned results carry a window, and for five of them a count; not one
carries which onsets.** So the old ink was located by this figure's own rule and
wore the detector's authority.

**The change loses something, and it is now written down rather than glossed.** Five
detectors report a participant count that no figure draws. Removing a wrong proxy is
not showing the quantity — filed, with the plumbing obstacle named
(`ui.app._compute` drops the field at its tuple boundary), as
`docs/todo/2026-08-18-the-participant-count-is-reported-and-never-drawn.md`.

**Two blocking findings, both fixed.** The shipped figures were one source edit
behind their legend text — rebuilt as the last action, mtimes confirm it. And
`reality_check.png`, which cannot be rebuilt without the real archive, still carries
the old convention *and says so in its own caption*, 142 lines from a page that now
says every onset is drawn the same. That contradiction is now disclosed at both
embeds instead of waiting to be discovered.

**The alarm can ring.** `generator_participation.png` is the test: at 0.45 the
columns under each ▲ are unmistakable, and at 0.10 — three ROIs, below the shipped
`min_rois` floor — the raster reads as structureless. That is the honest rendering
of a stress point, and precisely the row the old ground-truth ink would have drawn
tidy columns onto regardless.

## Findings and adjudications

| # | Role | Finding | Verdict |
|---|---|---|---|
| 1 | 10 / 1 | Shipped PNGs one edit behind their source legend. **blocking** | Rebuilt after every fix; mtimes verified. |
| 2 | 8 / 11 | `reality_check.png` contradicts the same page, undisclosed. **blocking** | Disclosure note added under both embeds, in the README and at `generator.md`'s "Start here". |
| 3 | 4 | "no detector reports a participant count" — false for rate+context; "CICADA is the only one that computes the roster" — false. **major** | Rewritten to the narrow true claim. |
| 4 | 4 | The participant count five of six report is now drawn nowhere. **major** | Filed as a todo; the loss is stated in the docstring rather than left silent. |
| 5 | 4 | The reality-check caption claimed a diamond is "the resolution LoCo actually reports" — LoCo reports onset **and** width. **major** | Caption corrected; the todo gains a second required edit (draw the span). |
| 6 | 8 / 11 | The README never stated the new convention. **major** | Its key paragraph now says every onset is drawn the same, and why. |
| 7 | 11 | The retraction sat mid-document; `generator.md` has a corrections appendix holding its twin. **major** | Moved there; §Parameters keeps only the reading instruction. |
| 8 | 8 | Legend listed ▼ "missed by all" — zero present in the render. **minor** | The entry is now conditional, and proven to fire in both directions. |
| 9 | 10 | The documented rebuild command reproduced neither committed file (wrong scale, no `--out`, no `--hero`). **minor** | Both docs now print the real invocation — and it is the command that built the shipped figures. |
| 10 | 10 | Eleven `generator.md` embeds had the knob name as alt text. **minor** | Descriptive alt text written for all eleven. |
| 11 | 3 | `generator.md` quoted 93% recall against a single-seed figure showing 80%. **minor** | Both bases named. |
| 12 | 4 / 8 | ▽ defined in the headline but drawn in only one of eleven sweeps. **minor** | The sub-caption now names ▽ only where the sweep plants distractors. |
| 13 | 9 | The docstring claimed the sort makes coordination "read as a vertical stripe"; at page width it does not. **minor** | Softened to what the render supports. |
| 14 | 3 | "membership"/"roster" collide with `bugarach.assembly`'s live meaning, where a roster **is** returned. **minor** | Wording avoids both terms. |
| 15 | 3 | `make_explainer_figures.py` draws a VLine across a raster, which the site's own viewer argues against. **minor, pre-existing** | Filed as its own todo; out of scope here. |
| 16 | 9 | The participation sweep lost the *quantity* (15 ROIs vs 3), keeping only the qualitative fade. **minor** | Restoration folded into the participant-count todo: a coactivity lane, derived from data rather than from `gt`. |
| 17 | 8 | `jitter_sec` and `grid_sec` sweeps are visually indistinguishable. **minor, pre-existing and already disclosed** | No change; recorded as looked-at. |
| 18 | 10 | Diagnostic's x axis has no name, unlike the sweeps. **minor, pre-existing** | Not changed; noted. |

## Residual ⚠

1. **`docs/generator/reality_check.png` still shows the old convention.** It needs
   `BUGARACH_DATA_ROOT`, which is set on no machine reachable from here. Two edits
   are required before its re-render, both in the todo. Disclosed to readers at both
   embeds meanwhile.
2. **Renders are not bit-reproducible.** A rebuild from identical source gave
   identical marker pixels but a different tick stroke weight (darkest tick
   `(64,64,64)` vs `(75,75,75)`) — chromium sub-pixel rasterization. So a figure
   cannot be certified byte-identical to its source; the practical rule is to
   rebuild everything in one pass and ship that, which is what happened here.
3. **The participant count is still drawn nowhere**, and the participation sweep is
   still qualitative-only. Both filed.
