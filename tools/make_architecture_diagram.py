#!/usr/bin/env python3
"""Draw the network from the model, through draughtsman, and check nothing was lost.

    python tools/make_architecture_diagram.py     # -> docs/learned/architecture.svg + architecture-phone.svg
    python tools/make_architecture_diagram.py --arch tube --out /tmp

**Why this exists, and why it replaces a hand-written SVG.** The original
`architecture.svg` was six labelled boxes — a *stage* diagram. Tony, 2026-09-01,
with an Inception-v3 figure in hand: *"i want this kind of figure."* That style
carries three things the stage diagram cannot: **typed glyphs** (you can see at a
glance how much of the model is convolution), **real branch topology** (the places
where the signal fans out and rejoins), and **shapes** at every step.

The tube earns that style, because it genuinely branches. Four difference-of-Gaussian
kernels run over one trace, the raw brightness **bypasses** them entirely, and the
five channels concatenate into the dilated stack. That fan-out and rejoin is the
architecture's one interesting piece of structure and the box diagram drew it as a
dashed afterthought.

**Everything here is read off the built module, never typed.** That was true of the
hand-rolled generator this replaces and it is still the rule. What changed is who
does the reading.

---------------------------------------------------------------------------------
WHAT THIS FILE IS NOW: THREE STAGES, NOT ONE.

    build_tube()  --[1 trace]-->  graph.json  --[2 check]-->  --[3 render]-->  SVG
                     facts                      coverage         layout
                     (torch)                    (must pass)      (deterministic)

`third_party/draughtsman` is vendored (see CLAUDE.md, "Vendored copies"). Its
`trace` walks the built module and writes every fact — shapes, parameter counts,
kernel widths, dilations — into a `graph.json`. `docs/learned/architecture.spec.json`
says which traced operations collapse into which drawn box and what to call them,
and **contains no numbers at all**: where the figure wants a quantity the spec
carries a reference like `{stage.params}`, resolved against the trace at render
time. Then `check` proves every traced operation landed in exactly one box.

WHY THE MIDDLE STAGE IS THE POINT. Five existing tools drew this model and the
worst of them produced a clean publication-styled figure that silently omitted the
max-pool, the mean over cells, the four kernels, the bypass and the concat — the
architecture — and reported success. `check` is what makes that impossible here: if
the model gains an operation, coverage fails by name and this script exits non-zero
BEFORE writing a figure that quietly leaves it out.

WHY graph.json IS NOT COMMITTED. It is regenerated on every run, from the live
`build_tube()`. A committed trace would be a file a human refreshes by hand, which
is the same defect one level up from the hardcoded `1,128 params` this generator
was written to kill. `tests/test_architecture_diagram_is_current.py` regenerates
and byte-compares, so the model moving turns the suite red.

⚠ ONE COST OF TRACING AT BUILD TIME, STATED SO NOBODY REDISCOVERS IT. The node ids
the spec references (`n0149`) are positional over the traced graph, so a torch
release that decomposes an operation differently shifts them and the spec stops
matching. That failure is LOUD and legible — `check` reports "node n0149 is in no
stage" — rather than a mysterious byte mismatch, and it is the trade taken
deliberately: the alternative is a committed trace that cannot notice the model
changing at all. If it fires, re-run draughtsman's stage 2 against the new trace.

**No fitted values appear here, and draughtsman now enforces that rather than
trusting it.** Centre widths are *initialised* across a geometric spread and then
trained, so a fitted width belongs to one training run and this diagram describes
the architecture. That distinction used to live only in this docstring, and it was
not enough: the first draughtsman figure said "max-pool, width 3", which is
`2*kmin+1` with kmin read off a TRAINED parameter — 3 at initialisation, 9-15 once
trained. The tracer now records that it baked a Python value out of a tensor
(`hazards` in graph.json) and `check` refuses to let the figure quote a traced
constant until the spec declares why that one is architectural. See
`docs/todo/2026-09-01-a-traced-figure-cannot-tell-a-constant-from-an-initialisation.md`
and draughtsman's DECISIONS.md correction 4.

`make_architecture_figures.py` remains where fitted kernels are drawn, measured off
a trained model. This figure is true of the design; that one is true of a run.

The output is a standalone SVG that ships **no styling of its own** — it inherits
`.arch` from whatever embeds it, which is how `build_site.py` inlines it and how
`report.css` styles it in the learned-detector page. Rendering it as a bare `<img>`
gives coloured boxes with no text, which is by design and is why the front page
inlines rather than links it.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "third_party"))

LEARNED = ROOT / "docs" / "learned"

#: `arch` -> the draughtsman specs that say how to draw it, one per figure written,
#: and the trace target and input shape to build it from. A spec is a
#: per-architecture document, so an architecture without one cannot be drawn by
#: this script and says so rather than falling back to something generic.
#:
#: The tube has TWO specs over ONE trace, because the front page has one slot and
#: two widths. draughtsman drew it one row wide for the laptop box (1203 px) and top
#: to bottom for the phone box (395 px), each spec stating its slot as `output.width`
#: with a `min_type` floor. `build_site.lead_model` picks between them; the learned
#: pages inline only the wide one.
DRAWABLE = {
    "tube": {
        "figures": {
            "architecture.svg": LEARNED / "architecture.spec.json",
            "architecture-phone.svg": LEARNED / "architecture-phone.spec.json",
        },
        "target": "bugarach.learn.nets.tube:build_tube",
        # One recording's worth of cells and frames. The model is invariant to the
        # cell count -- it sums over cells -- so this is the shape the trace was
        # taken at, not a constraint the architecture carries.
        "input_shape": [1, 30, 600],
    },
}


def build(arch: str, out_dir: Path) -> int:
    try:
        from draughtsman.check import check, report
        from draughtsman.facts import Graph
        from draughtsman.render import render
        from draughtsman.spec import load
        from draughtsman.tracing import trace
    except ImportError as exc:                                  # pragma: no cover
        print(f"make_architecture_diagram: third_party/draughtsman is not "
              f"importable — {exc}", file=sys.stderr)
        return 2

    entry = DRAWABLE.get(arch)
    if entry is None:
        print(f"make_architecture_diagram: no spec for `{arch}`. Drawable: "
              f"{', '.join(sorted(DRAWABLE))}. A spec says which traced operations "
              f"collapse into which box; there is no generic answer, so this "
              f"refuses rather than drawing something plausible.", file=sys.stderr)
        return 2

    # -- 1. facts, off the live module --------------------------------------------
    try:
        graph_doc = trace(entry["target"], entry["input_shape"])
    except Exception as exc:                                    # pragma: no cover
        print(f"make_architecture_diagram: cannot trace `{arch}` — "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    graph = Graph(graph_doc)

    # -- 2 and 3, per figure: check, then render deterministically ----------------
    # Every spec is checked before anything is written, so one that fails leaves
    # no half-updated pair behind: the two figures always describe the same model.
    drawn = {}
    for name, spec_path in entry["figures"].items():
        spec = load(json.loads(spec_path.read_text(encoding="utf-8")))
        result = check(spec, graph)
        if not result.ok:
            print(report(result), file=sys.stderr)
            print(f"\nmake_architecture_diagram: refusing to draw `{arch}` as "
                  f"{name}. The spec no longer accounts for every operation the "
                  f"model performs, so the figure would omit one silently — which "
                  f"is the exact failure this pipeline exists to prevent. Re-run "
                  f"draughtsman's stage 2 against a fresh trace and re-vendor "
                  f"{spec_path.relative_to(ROOT)}.", file=sys.stderr)
            return 1
        drawn[name] = render(spec, graph)

    out_dir.mkdir(parents=True, exist_ok=True)
    for name, svg in drawn.items():
        (out_dir / name).write_text(svg, encoding="utf-8")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arch", default="tube")
    ap.add_argument("--out", type=Path, default=LEARNED,
                    help="directory to write the architecture SVGs into")
    a = ap.parse_args(argv)
    return build(a.arch, a.out)


if __name__ == "__main__":
    raise SystemExit(main())
