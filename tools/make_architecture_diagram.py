#!/usr/bin/env python3
"""Draw the network the way a network is drawn — layers, branches, and a legend.

    python tools/make_architecture_diagram.py                 # -> docs/learned/architecture.svg
    python tools/make_architecture_diagram.py --arch tube_guard --out /tmp

**Why this exists, and why it replaces a hand-written SVG.** The previous
`architecture.svg` was six labelled boxes — a *stage* diagram. Tony, 2026-09-01,
with an Inception-v3 figure in hand: *"i want this kind of figure."* That style
carries three things the stage diagram cannot: **typed glyphs** (you can see at a
glance how much of the model is convolution), **real branch topology** (the places
where the signal fans out and rejoins), and **shapes** at every step.

The tube earns that style, because it genuinely branches. Four difference-of-Gaussian
kernels run in parallel over one trace, the raw brightness **bypasses** them
entirely, and the five channels concatenate into the dilated stack. That fan-out
and rejoin is the architecture's one interesting piece of structure and the box
diagram drew it as a dashed afterthought.

**Everything here is read off the built module, never typed.** The old file
hardcoded "1,128 params" in its markup; this counts parameters per stage from
`build_tube()` itself, derives the dilation schedule from the stack, and takes the
kernel width from `max_center_frames`. A number in a figure that a human maintains
by hand is a number that goes stale silently — which is the same defect
`docs/learned/bakeoff.md` documents about its own table.

**No fitted values appear here.** Centre widths are *initialised* across a
geometric spread and then trained, so a fitted width belongs to one training run
and this diagram describes the architecture. `make_architecture_figures.py` is
where fitted kernels are drawn, measured off a trained model, and that division is
deliberate: this figure is true of the design, that one is true of a run.

The output is a standalone SVG that ships **no styling of its own** — it inherits
`.arch` from whatever embeds it, which is how `build_site.py` inlines it and how
`report.css` styles it in the learned-detector page. Rendering it as a bare `<img>`
gives coloured boxes with no text, which is by design and is why the front page
inlines rather than links it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

#: One colour per layer KIND, and the legend is generated from this same dict so a
#: new kind cannot appear in the drawing without appearing in the key. The palette
#: is the Inception figure's, which is a deliberate borrowing: a reader who knows
#: that figure reads this one without being taught.
KINDS = {
    "conv":    ("#f5b74e", "Convolution"),
    "dog":     ("#e07b39", "Centre − surround (DoG)"),
    "maxpool": ("#8bc34a", "MaxPool"),
    "avgpool": ("#5b9bd5", "Mean over cells"),
    "concat":  ("#c0504d", "Concat"),
    "act":     ("#9b8ec4", "GELU"),
    "out":     ("#8e44ad", "Score / threshold"),
}

GW, GH, GAP = 13, 30, 5          # glyph width, height, gap between glyphs in a run


def _model_facts(arch: str) -> dict:
    """Layer shapes and parameter counts, BUILT rather than quoted.

    Instantiating costs milliseconds and removes the whole class of defect where a
    figure's caption and its model disagree. If torch is absent this raises, and
    the caller turns that into a refusal — a diagram of a model nobody could build
    is worse than no diagram.
    """
    from bugarach.learn.nets import ARCHITECTURES, n_params

    spec = ARCHITECTURES[arch]
    cfg = dict(spec.cfg)
    model = spec.make()

    n_scales = int(cfg.get("n_scales", 4))
    depth = int(cfg.get("depth", 6))
    width = int(cfg.get("width", 8))
    k = int(cfg.get("max_center_frames", 128))

    # Per-stage parameter counts, summed off the real modules. `head` is the
    # dilated stack; everything else on the module is the DoG bank's three
    # parameter vectors.
    head_params = sum(p.numel() for p in model.head.parameters())
    total = int(n_params(model))
    dog_params = total - head_params

    # The stack's own layers, in order, read from the Sequential rather than
    # recomputed from `depth` — if the builder ever changes shape this follows it.
    stack = []
    for m in model.head:
        cls = type(m).__name__
        if cls == "Conv1d":
            stack.append({"kind": "conv", "k": int(m.kernel_size[0]),
                          "d": int(m.dilation[0]), "cout": int(m.out_channels),
                          "params": sum(p.numel() for p in m.parameters())})
        elif cls == "GELU":
            stack.append({"kind": "act"})

    from bugarach.learn.nets import receptive_field
    return {
        "arch": arch, "note": spec.note, "n_scales": n_scales, "depth": depth,
        "width": width, "k": k, "kernel_taps": 2 * k + 1,
        "dog_params": dog_params, "head_params": head_params, "total": total,
        "stack": stack, "rf": int(receptive_field(depth)),
    }


def _swatch(x, y, w, h, fill, rx=2.5):
    """A coloured block, styled so no host stylesheet can repaint it.

    **`style=` and not `fill=`, deliberately.** Both places that embed this SVG
    carry a `.arch rect { fill: ... ; stroke: ... }` rule written for the old
    box diagram — `report.css` and the front page's inlined block. A presentation
    attribute LOSES to a stylesheet declaration, so `fill="#f5b74e"` would be
    repainted the card colour and every glyph in this figure would come out the
    same flat shade. That is the black-box failure the previous diagram already
    had, arriving by a different route. An inline `style` wins, so the colours
    are the figure's own wherever it is embedded.
    """
    return (f'<rect class="g" x="{x:.0f}" y="{y:.0f}" width="{w}" height="{h}" '
            f'rx="{rx}" style="fill:{fill};stroke:none"/>')


def _glyphs(x, y, items):
    """A run of glyphs left to right; returns (svg, x_after)."""
    out = []
    for kind in items:
        fill, _ = KINDS[kind]
        out.append(_swatch(x, y, GW, GH, fill))
        x += GW + GAP
    return "".join(out), x


def build_svg(f: dict) -> str:
    """The diagram. Coordinates are laid out by hand; the CONTENT is all from `f`."""
    mid = 250                      # vertical centre line
    p = []                         # svg body
    lab = []                       # labels, drawn last so nothing overlaps them

    def text(x, y, s, cls="lbl", anchor="middle", size=None):
        st = f' font-size="{size}"' if size else ""
        lab.append(f'<text class="{cls}" x="{x:.0f}" y="{y:.0f}" '
                   f'text-anchor="{anchor}"{st}>{s}</text>')

    x = 46

    # ---- input ---------------------------------------------------------------
    # Every stage label goes ABOVE its glyph and every shape BELOW it, on two
    # fixed rules. The first draft put lane labels beside their glyphs and the
    # rejoin wires ran straight through the text — legible in the source, struck
    # through in the render, which is the whole reason this file renders and looks
    # rather than trusting the markup.
    up, down = mid - 30, mid + 40

    # The gap between these two is set by the LABELS, not the glyphs: "mean over
    # cells" is ~95px and "widen" ~34, so glyphs 34px apart put one word inside
    # the other. Space them by what has to fit above them.
    text(x + GW / 2, up, "widen", "lbl", size=11)
    g, x = _glyphs(x, mid - GH / 2, ["maxpool"])
    text(x - GW / 2 - GAP, down, "N × T", "lbl", size=11)
    p.append(g)

    x += 92
    text(x + GW / 2, up, "mean over cells", "lbl", size=11)
    g, x = _glyphs(x, mid - GH / 2, ["avgpool"])
    text(x - GW / 2 - GAP, down, "1 × T", "lbl", size=11)
    p.append(g)

    # ---- the fan-out ---------------------------------------------------------
    # The figure's reason to exist: four kernels in parallel, plus a bypass that
    # skips them, rejoining at one concat.
    split = x + 16
    fan = 340
    join = split + fan
    lanes = [mid - 168, mid - 106, mid - 44, mid + 18]      # the four DoG scales
    bypass = mid + 116
    gx = split + 150                                        # glyph column in the fan

    for yl in lanes + [bypass]:
        p.append(f'<path class="wire" style="fill:none" d="M{split:.0f},{mid} '
                 f'C{split + 52:.0f},{mid} {split + 52:.0f},{yl:.0f} '
                 f'{split + 104:.0f},{yl:.0f}" fill="none"/>')
        p.append(f'<path class="wire" style="fill:none" d="M{split + 104:.0f},{yl:.0f} '
                 f'L{gx:.0f},{yl:.0f}" fill="none"/>')
        p.append(f'<path class="wire" style="fill:none" d="M{gx + GW:.0f},{yl:.0f} '
                 f'C{join - 52:.0f},{yl:.0f} {join - 52:.0f},{mid} '
                 f'{join:.0f},{mid}" fill="none"/>')

    for i, yl in enumerate(lanes):
        g, _ = _glyphs(gx, yl - GH / 2, ["dog"])
        p.append(g)
        text(gx + GW / 2, yl - 24, f"DoG scale {i + 1}", "lbl", size=11)

    g, _ = _glyphs(gx, bypass - GH / 2, ["avgpool"])
    p.append(g)
    text(gx + GW / 2, bypass - 24, "bypass — the raw trace", "lbl hi", size=11)
    text(gx + GW / 2, bypass + 34, "the kernel cannot cancel what it never sees",
         "lbl", size=10.5)

    text(gx + GW / 2, mid - 208,
         f"{f['n_scales']} kernels · {f['kernel_taps']} taps · area-matched, "
         f"so a flat field integrates to zero", "lbl", size=11)

    x = join
    text(x + GW / 2, up, "concat", "lbl", size=11)
    g, x = _glyphs(x, mid - GH / 2, ["concat"])
    text(x - GW / 2 - GAP, down, f"{f['n_scales'] + 1} × T", "lbl", size=11)
    p.append(g)

    # ---- the dilated stack ---------------------------------------------------
    x += 26
    stack_x0 = x
    for layer in f["stack"]:
        if layer["kind"] == "act":
            g, x = _glyphs(x, mid - GH / 2, ["act"])
            p.append(g)
            continue
        g, x = _glyphs(x, mid - GH / 2, ["conv"])
        p.append(g)
        cx = x - GW / 2 - GAP
        text(cx, up, "1×1" if layer["k"] == 1 else f"d{layer['d']}", "lbl", size=10.5)
    stack_x1 = x - GAP

    text((stack_x0 + stack_x1) / 2, mid - 52,
         f"dilated stack — {f['depth']} conv, {f['width']} ch", "lbl hi")
    text((stack_x0 + stack_x1) / 2, down,
         f"{f['width']} × T · sees {f['rf']:,} samples", "lbl", size=11)

    # ---- output --------------------------------------------------------------
    x += 18
    text(x + GW / 2, up, "score", "lbl hi", size=11)
    g, x = _glyphs(x, mid - GH / 2, ["out"])
    text(x - GW / 2 - GAP, down, "T", "lbl", size=11)
    p.append(g)

    width_total = x + 40
    top, bot = mid - 236, mid + 268

    # ---- parameter ledger ----------------------------------------------------
    text(width_total / 2, mid + 176,
         f"kernels {f['dog_params']:,} params  ·  stack {f['head_params']:,}  ·  "
         f"{f['total']:,} total", "lbl", size=11.5)
    text(width_total / 2, mid + 194,
         "N = cells, any number · T = samples, one per frame · "
         "the model never sees which cell is which", "lbl", size=11)

    # ---- legend --------------------------------------------------------------
    # Laid out from the same dict the glyphs are drawn from, so a kind cannot
    # reach the picture without reaching the key. Centred by measuring the run
    # first — a legend that runs off the viewBox is invisible, and the first
    # version did exactly that to its last entry.
    ly = mid + 232
    widths = [40 + 6.6 * len(name) for _, name in KINDS.values()]
    lx = max(20.0, (width_total - sum(widths)) / 2)
    for (fill, name), w in zip(KINDS.values(), widths):
        lab.append(_swatch(lx, ly - 9, 11, 11, fill, rx=2))
        lab.append(f'<text class="lbl" x="{lx + 17:.0f}" y="{ly}" '
                   f'text-anchor="start" font-size="11">{name}</text>')
        lx += w

    body = "".join(p) + "".join(lab)
    aria = ("Signal path of the centre-surround model: a raster of onsets is widened "
            "per cell, averaged across cells into one brightness trace, then split "
            f"into {f['n_scales']} parallel difference-of-Gaussian kernels plus a "
            "bypass carrying the raw trace; the five channels concatenate into a "
            f"{f['depth']}-layer dilated convolution stack and a one-by-one layer "
            "that emits a score per frame.")
    return (f'<svg viewBox="0 {top} {width_total} {bot - top}" '
            f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{aria}">'
            f'{body}</svg>\n')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arch", default="tube")
    ap.add_argument("--out", default=str(ROOT / "docs" / "learned"),
                    help="directory to write <arch>-shaped architecture.svg into")
    ap.add_argument("--name", default="architecture.svg")
    a = ap.parse_args(argv)

    try:
        facts = _model_facts(a.arch)
    except Exception as exc:                                   # noqa: BLE001
        print(f"make_architecture_diagram: cannot build `{a.arch}` — {type(exc).__name__}: "
              f"{exc}\nThis figure is generated FROM the model on purpose; drawing it "
              f"from remembered numbers is the defect it exists to prevent.",
              file=sys.stderr)
        return 1

    dest = Path(a.out).expanduser()
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / a.name
    path.write_text(build_svg(facts), encoding="utf-8")
    print(f"wrote {path}  ({facts['total']:,} params, {facts['depth']} conv, "
          f"{facts['n_scales']} kernels, receptive field {facts['rf']:,} samples)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
