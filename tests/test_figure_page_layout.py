"""ADR-0014: a figure page is figures, then controls, then text.

Checked on the reference page, the stack ceiling explainer, as committed. The four points are the
ADR's: figures first, each with its legend and nothing else, the controls in one block after them
that sticks to the bottom of the window, and the text last.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = [
    ROOT / "docs/learned/runs/2026-10-08-stack-ceiling/explainer_stack-ceiling_20261008.html",
    ROOT / "tools/stack_ceiling_demo.template.html",
]


class Outline(HTMLParser):
    """The order of the page's top-level parts, and each figure caption's words."""

    def __init__(self):
        super().__init__()
        self.order: list[str] = []
        self.captions: list[str] = []
        self.depth = 0
        self.in_main = False
        self.in_caption = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "main":
            self.in_main, self.depth = True, 0
            return
        if not self.in_main or tag in ("br", "input", "meta", "link"):
            return
        if self.depth == 0:
            classes = (a.get("class") or "").split()
            self.order.append("controls" if "tools" in classes else
                              "figure" if tag == "figure" else
                              "title" if tag == "h1" else "text")
        if tag == "figcaption":
            self.in_caption = True
            self.captions.append("")
        self.depth += 1

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main = False
        elif self.in_main and tag not in ("br", "input", "meta", "link"):
            self.depth -= 1
            if tag == "figcaption":
                self.in_caption = False

    def handle_data(self, data):
        if self.in_caption:
            self.captions[-1] += data


def outline(path: Path) -> Outline:
    o = Outline()
    o.feed(path.read_text())
    return o


def test_figures_then_controls_then_text():
    for page in PAGES:
        order = outline(page).order
        assert order[0] == "title", page.name
        kinds = [k for k in order[1:]]
        collapsed = [k for i, k in enumerate(kinds) if i == 0 or kinds[i - 1] != k]
        assert collapsed == ["figure", "controls", "text"], (page.name, collapsed)


def test_each_figure_is_numbered_and_carries_only_its_legend():
    for page in PAGES:
        captions = outline(page).captions
        assert captions, page.name
        for n, caption in enumerate(captions, start=1):
            words = " ".join(caption.split())
            assert words.startswith(f"Figure {n}. "), (page.name, words[:40])
            # A legend is a heading and a list of short keys. Sentences of explanation belong in
            # the text at the bottom of the page.
            after_heading = words.split(". ", 2)[2] if words.count(". ") >= 2 else ""
            assert ". " not in after_heading, (page.name, n, after_heading[:80])
            assert len(words) < 420, (page.name, n, len(words))


def test_the_controls_stick_to_the_bottom_of_the_window():
    for page in PAGES:
        css = page.read_text().split("</style>")[0]
        rule = re.search(r"\.tools\s*\{([^}]*)\}", css)
        assert rule, page.name
        assert re.search(r"position:\s*sticky", rule[1]) and re.search(r"bottom:\s*0", rule[1])
