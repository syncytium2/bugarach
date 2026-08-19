#!/usr/bin/env python3
"""Build the assembly report as one self-contained HTML file.

    python tools/build_assembly_report.py --src docs/assembly_report.md \\
        --figures <darkroom>/bugarach --out docs/learned

Markdown in, `docs/learned/report.css` around it, figures embedded as data URIs,
out. Self-contained by the same rule the export contract uses on data: one file,
no external requests, so the page a reader opens is the page that was reviewed.

It differs from `tools/md_to_page.py` in exactly one way — that one does not embed
images, and a report whose figures live beside it as separate files is a report
that arrives without its evidence the first time someone forwards it. Everything
else, including the stylesheet, is shared.

`![alt](figure_id)` in the markdown resolves to `<figures>/figure_id.png`, base64
inlined. A missing figure is an error, never a silently empty page.
"""
from __future__ import annotations

import argparse
import base64
import html
import re
import sys
from pathlib import Path


def _inline_figures(md: str, figures: Path) -> str:
    """Replace image references with embedded data URIs."""
    def sub(m):
        alt, fid = m.group(1), m.group(2).strip()
        png = figures / (fid if fid.endswith(".png") else f"{fid}.png")
        if not png.is_file():
            raise SystemExit(f"figure not found: {png}")
        b64 = base64.b64encode(png.read_bytes()).decode("ascii")
        return (f'<figure><img alt="{html.escape(alt)}" '
                f'src="data:image/png;base64,{b64}">'
                f'<figcaption>{html.escape(alt)}</figcaption></figure>')
    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", sub, md)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--src", type=Path, required=True)
    p.add_argument("--figures", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--css", type=Path, default=Path("docs/learned/report.css"))
    a = p.parse_args(argv)

    try:
        import markdown  # noqa: F401
        render = lambda t: markdown.markdown(  # noqa: E731
            t, extensions=["tables", "attr_list", "md_in_html"])
    except Exception:
        try:
            import mistune
            render = mistune.create_markdown(plugins=["table"])
        except Exception:
            print("need `markdown` or `mistune` to build the page", file=sys.stderr)
            return 1

    md = _inline_figures(a.src.read_text(encoding="utf-8"), a.figures)
    body = render(md)
    css = a.css.read_text(encoding="utf-8") if a.css.is_file() else ""
    title = next((l.lstrip("# ").strip() for l in md.splitlines()
                  if l.startswith("# ")), a.src.stem)

    # The charset comes first and stays first. Opened from disk a page with no
    # declared charset is read as Latin-1, and every en-dash and · in this report
    # becomes mojibake (sapper SAP005, after it cost a review document).
    # The charset comes first and stays first, in the same literal as the title
    # so the rule that enforces it can see it on one line. Opened from disk, a
    # page with no declared charset is read as Latin-1 and every en-dash and · in
    # this report becomes mojibake (sapper SAP005, after it cost a review doc).
    meta = (f'<meta charset="utf-8">\n<title>{html.escape(title)}</title>\n'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<meta name="generator" content="build_assembly_report.py">')
    # report.css already owns figure, figure img and figcaption; overriding them
    # is how this page stopped matching the other reports and dropped its captions
    # below AA contrast. The one rule it lacks is code-block overflow, which
    # otherwise scrolls the whole document sideways on a narrow screen.
    style = f'<style>\n{css}\npre{{overflow-x:auto}}\n</style>'
    page = (f'<!doctype html>\n<html lang="en">\n<head>\n{meta}\n{style}\n'
            f'</head>\n<body>\n<div class="wrap">\n{body}\n</div>\n'
            f'</body>\n</html>\n')

    a.out.mkdir(parents=True, exist_ok=True)
    dest = a.out / f"{a.src.stem}.html"
    dest.write_text(page, encoding="utf-8")
    kb = dest.stat().st_size / 1024
    print(f"wrote {dest}  ({kb:.0f} KB, self-contained)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
