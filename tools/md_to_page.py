#!/usr/bin/env python3
"""Render a markdown document as a self-contained page, in the reports' own look.

    python tools/md_to_page.py docs/overnight_spec.md --out docs/learned

**Why this exists.** Three deliverables in two days were published and then not
found, and one of them was found and then not read because it was a `.md` in a
folder of JSON. Tony's note on the reports was that the HTML is working well — so
anything meant to be *read* gets the same treatment: one file, no external
requests, the same stylesheet as the reports, readable in light and dark.

It is deliberately thin. Markdown in, `docs/learned/report.css` around it, out. No
token substitution: a page built from a markdown source has its numbers checked in
that source, and adding a second substitution path would give the same quantity two
places to drift between.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "docs" / "learned"


#: The whole document as one template, charset on the line it has to be on.
#:
#: Built by concatenation instead, this tripped sapper SAP005 twice — the rule
#: matches per line, so a fragment whose first tag is the title looks exactly like
#: a document with no declared charset, even when a correct head is prepended two
#: lines later. (Quoting the offending shape here trips the rule too — that is the
#: third time a comment explaining a sapper rule has matched it.) The rule is right to be crude: a page read from disk with no
#: charset is decoded as Latin-1 and every dash in it turns to mojibake. Writing
#: the document as one literal is what makes the guarantee visible to a reader and
#: to the checker at the same time.
DOC = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{css}
{extra}
</style>
<div class="wrap"><div class="doc">
{body}
</div></div>
</html>
"""


def _inline_images(body: str, base: Path) -> str:
    """Embed every local ``<img src>`` as a data URI.

    Without this the page says "self-contained" and is not: a markdown source
    lives in ``docs/`` and writes ``learned/fig.png``, correct on GitHub, while
    the page it renders to lands in ``docs/learned/`` and in the darkroom root,
    where that path resolves to nothing. The figure is the one element whose
    absence is invisible in the source and total in the render — the document
    still reads as though it had one. Caught by a craft pass on a document whose
    lead evidence was the broken image.

    Remote sources are left alone, and so is a missing local file: the caller
    gets a warning and a broken link rather than a silently dropped figure.
    """
    import base64
    import mimetypes

    def sub(m):
        src = m.group(1)
        if "://" in src or src.startswith("data:"):
            return m.group(0)
        p = (base / src).resolve()
        if not p.is_file():
            print(f"  ! image not found, left as a link: {src}", file=sys.stderr)
            return m.group(0)
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        b64 = base64.b64encode(p.read_bytes()).decode("ascii")
        return m.group(0).replace(f'src="{src}"',
                                  f'src="data:{mime};base64,{b64}"')

    return re.sub(r'<img [^>]*src="([^"]+)"[^>]*>', sub, body)


def render(md: str, *, title: str, css: str, base: Path | None = None) -> str:
    """A complete, self-contained document — head, styles and body."""
    import markdown

    body = markdown.markdown(
        md, extensions=["tables", "fenced_code", "sane_lists", "attr_list"])
    if base is not None:
        body = _inline_images(body, base)

    # A blockquote that opens with a stop sign is a gate, not an aside. Give it the
    # warning treatment so it cannot be skimmed past — the whole point of the block
    # is that a reader who skims runs unapproved work.
    body = body.replace("<blockquote>\n<h2>\u26d4",
                        '<blockquote class="gate">\n<h2>\u26d4')

    # Same reasoning one notch down: a blockquote opening with a warning sign is
    # a caveat the author hoisted to the top ON PURPOSE. Left as a plain
    # blockquote it renders in the muted aside colour, which makes the most
    # important sentence in the document the faintest text on the page \u2014 the
    # failure this project has already recorded once, for a colour key demoted
    # into gray footer text.
    body = body.replace("<blockquote>\n<p>\u26a0",
                        '<blockquote class="warn">\n<p>\u26a0')

    return DOC.format(title=title, css=css, extra=EXTRA, body=body)


EXTRA = """
  /* markdown lands as one flow rather than the reports' hand-set columns */
  .doc { max-width: 74ch; }
  .doc h1 { font-size: clamp(1.8rem, 4.5vw, 2.4rem); margin-bottom: 1.4rem; }
  .doc h2 { border-top: 1px solid var(--rule); padding-top: 1.6rem; }
  .doc h3 { font-size: 1.05rem; margin-top: 2.2rem; }
  .doc table { margin: 1.4rem 0; }
  .doc td, .doc th { vertical-align: top; }
  .doc blockquote { border-left: 2px solid var(--rule); margin: 1.6rem 0;
                    padding: .1rem 0 .1rem 1.1rem; color: var(--muted); }
  .doc blockquote.gate { border-left: 4px solid var(--learned);
                         background: var(--bad-bg); color: var(--bad-fg);
                         padding: .2rem 1.3rem 1rem; border-radius: 3px; }
  .doc blockquote.gate h2 { border-top: 0; padding-top: 1.2rem;
                            color: var(--bad-fg); }
  .doc blockquote.gate strong { color: var(--bad-fg); }
  /* a hoisted caveat reads at body weight, not aside-gray */
  .doc blockquote.warn { border-left: 4px solid var(--learned);
                         color: var(--ink); padding: .2rem 1.3rem;
                         background: color-mix(in srgb, var(--learned) 7%,
                                               transparent);
                         border-radius: 3px; }
  /* A figure wider than the 74ch column silently overflows it and the page
     ships with its evidence cropped. Caught on a document whose lead figure
     ran off the right edge. */
  .doc img { max-width: 100%; height: auto; display: block;
             margin: 1.6rem auto; }
  .doc code { background: color-mix(in srgb, var(--ink) 7%, transparent);
              padding: .08em .32em; border-radius: 2px; }
  .doc li { margin-bottom: .5rem; }
"""


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", type=Path)
    p.add_argument("--out", type=Path, default=None,
                   help="destination; default $BUGARACH_DARKROOM. A page built "
                        "to be read has to reach the place people read from "
                        "(sapper SAP006).")
    p.add_argument("--also", type=Path, default=None,
                   help="a second destination, written identically — usually the "
                        "repo copy, which review and git history need")
    p.add_argument("--name", default=None, help="output stem (default: source stem)")
    p.add_argument("--title", default=None)
    a = p.parse_args(argv)

    md = a.source.read_text()
    title = a.title or (re.search(r"^#\s+(.+)$", md, re.M).group(1)
                        if re.search(r"^#\s+(.+)$", md, re.M) else a.source.stem)
    css_path = HERE / "report.css"
    if not css_path.exists():
        print(f"missing {css_path}", file=sys.stderr)
        return 1

    from bugarach.paths import darkroom, unresolved_message
    out = a.out or darkroom()
    if out is None:
        print(unresolved_message(), file=sys.stderr)
        return 1

    page = render(md, title=title, css=css_path.read_text(),
                  base=a.source.resolve().parent)
    for d in [x for x in (out, a.also) if x is not None]:
        d.mkdir(parents=True, exist_ok=True)
        dest = d / f"{a.name or a.source.stem}.html"
        dest.write_text(page)
        print(f"wrote {dest}  ({dest.stat().st_size/1024:.0f} KB, self-contained)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
