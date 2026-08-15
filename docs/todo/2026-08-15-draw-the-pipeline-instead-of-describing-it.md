---
status: open
filed: 2026-08-15
---

# The project's driving idea is a flow diagram, and the site describes it in prose

The landing page now states why this project simulates baseline recordings and
never a treatment: a model trained across everyone's data learns what is usually
true, and what is usually true is the textbook. In this preparation the textbook
is wrong, so the instrument has to be built from the preparation's own untreated
statistics and only then pointed at the treatments.

That argument is a **flow**, and it ships as two paragraphs of prose — the exact
failure CLAUDE.md names in terms ("show the picture — don't describe it"). The
murderboard flagged it and it was filed rather than fixed, to keep that change to
the text that was asked for: `docs/reviews/index_driving-idea_2026-08-15.md`,
residual ⚠ 2.

## The figure

One horizontal schematic, boxes left to right:

```
 recording  ->  measure baseline    ->  confirm  ->  simulate
                parameters              (human)      baseline
                                                        |
                                            +-----------+-----------+
                                            |                       |
                                    tune the six            train the model
                                      detectors
                                            |                       |
                                            +-----------+-----------+
                                                        |
                                              analyse the FULL dataset
                                                (treatments included)
```

The load-bearing detail is that **treatment enters only at the last box**. A
reader who sees that once does not need the paragraph. The two middle boxes run
in parallel — the same synthetic baseline feeds the detector sweep and the
training set — and the confirm step is a human, which is the part no other
pipeline in this space draws.

## Notes for whoever builds it

- Inline SVG in `tools/build_site.py`, not a rendered PNG: it is a diagram, not
  a data figure, so it should not need chromium and should stay legible in both
  light and dark.
- It also resolves residual ⚠ 3 from the same review for free — nothing on the
  page currently shows that a recording carries two event streams.
- Two of the six boxes describe work that does not exist yet (no parameter
  estimator in `src/`, no model). Whatever the diagram does, it must not imply
  they are built — the paragraph beside it says "the plan, not yet the
  practice", and the picture has to agree.
