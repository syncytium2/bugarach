# ADR-0014: A figure page is figures, then controls, then text

## Status

Accepted, 2026-10-08, by Tony. On the stack ceiling page, rearranged at his word into this order:
*"much improved. this architecture (figures at the top, controls stuck to bottom, explainer text
at the bottom of the scroll) needs to be standardized for the estate."*

Numbers 0012 and 0013 are held by open proposals (#848, #855), so this record is 0014.

## Context

**The first draft of the page opened with a paragraph, two rows of controls and a second
paragraph.** The first figure began below the fold. Tony's note on it: *"redo the page with the
main figures at the top, then tool row, then text. keep the legend with the figures."*

**A reader opens a page to look at the figure.** Text above it has to be scrolled past every
time the page is opened, by the same reader who read it once. A legend is different: it is
needed at the moment of looking, so it cannot move down with the rest of the text.

**Controls placed after tall figures end up far from what they drive.** On the stack ceiling
page the play button would sit about 1,300 px below the animation it starts. Fixing the control
block to the bottom of the window keeps the figure and its controls on screen together.

## Decision

A page built around figures is laid out in this order:

1. **The figures come first**, directly under the page title. Nothing but the title sits above
   the first figure.
2. **Each figure carries its own legend**, in its heading line: the figure number and name
   (`Figure 1. …`), then the key to its colours, line styles and symbols. Nothing else goes
   there. What the figure means, and how to read it, is text and goes last.
3. **The controls come after the figures, in one block that sticks to the bottom of the
   window** while the figures are on screen. A page with no controls has no such block.
4. **The explanatory text comes last**, at the bottom of the scroll: any readout of the current
   state, what is measured, how to read each figure (named by number and name), and provenance.

**Reference implementation:** `tools/stack_ceiling_demo.template.html`, built by
`tools/make_stack_ceiling_demo.py`. `tests/test_figure_page_layout.py` checks the built page
against the four points above.

## Consequences

- **It applies to pages built from here on.** The existing pages are not converted by this
  record; a page is brought into line when it is next rebuilt for another reason.
- **Only one page is checked.** The test reads the stack ceiling page. A check that covers every
  page builder needs a shared page shell that builders use, which does not exist yet.
- **The estate half is not bugarach's to do.** The standard is for every repository. The request
  for a shared shell and a check that travels with it goes to the armory repository, which
  holds the estate's shared tools, as an issue.
- **Open, and Tony's to rule:** whether a long written report with figures placed through its
  text (the comparison reports, the methods pages) is a "figure page" under this record. As
  written it covers pages a reader opens to look at and work a figure: explainers, demonstrations,
  viewers and status pages.
- The plot conventions still hold inside each figure: numbered figures, units on every number,
  minutes-friendly time axes, nothing drawn on a raster.
