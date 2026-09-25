"""Build the one-page methods PDF, and refuse a build that breaks the page.

    python tools/build_methods_one_page.py                     # to the darkroom
    python tools/build_methods_one_page.py --also docs/methods/one_page

The source is `docs/methods/one_page/methods_one_page.html`, written by hand; its numbers are
pinned to the code by `tests/test_methods_one_page_numbers.py`. This tool prints it to PDF with
headless Chromium and then checks what Tony asked for: the methods text on page 1 and the
references alone on page 2 (2026-09-25). The page was built with under 2 pt to spare, and a
single added line silently moved the references to page 3 in the review's spill test, so the
check is part of the build rather than something to remember.

The destination defaults to the darkroom (sapper SAP006); `--also` writes the repo copy that
review and git history need. The author field is stamped when PyMuPDF is importable, because
Chromium ignores `<meta name="author">`.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "docs" / "methods" / "one_page" / "methods_one_page.html"
AUTHOR = "Tony DeFazio"


def chromium() -> str:
    """The Chromium binary: $CHROMIUM, else Playwright's, else one on PATH."""
    if os.environ.get("CHROMIUM"):
        return os.environ["CHROMIUM"]
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", str(Path.home() / ".cache/ms-playwright"))
    for pattern in ("chromium-*/chrome-linux/chrome", "chromium-*/chrome-mac/Chromium.app/"
                    "Contents/MacOS/Chromium", "chromium-*/chrome-win/chrome.exe"):
        hits = sorted(glob.glob(str(Path(base) / pattern)))
        if hits:
            return hits[-1]
    for name in ("chromium", "chromium-browser", "google-chrome"):
        if shutil.which(name):
            return shutil.which(name)
    raise SystemExit("no Chromium found; set CHROMIUM to its binary")


def print_pdf(html: Path, pdf: Path) -> None:
    subprocess.run([chromium(), "--headless", "--no-sandbox", "--disable-gpu",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf}", str(html)],
                   check=True, capture_output=True)


def page_count(pdf: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))


def check(pdf: Path, html: Path) -> list[str]:
    """What is wrong with this build, or nothing."""
    problems = []
    if page_count(pdf) != 2:
        problems.append(f"{page_count(pdf)} pages, not 2")
    body_only = Path(tempfile.mkdtemp()) / "body.html"
    body_only.write_text(re.sub(r'<div class="refs">.*?</div>', "", html.read_text(
        encoding="utf-8"), flags=re.S), encoding="utf-8")
    body_pdf = body_only.with_suffix(".pdf")
    print_pdf(body_only, body_pdf)
    if page_count(body_pdf) != 1:
        problems.append("the methods text does not fit on page 1")
    return problems


def stamp_author(pdf: Path) -> bool:
    try:
        import pymupdf
    except ImportError:
        return False
    doc = pymupdf.open(pdf)
    meta = dict(doc.metadata or {})
    meta["author"] = AUTHOR
    doc.set_metadata(meta)
    tmp = pdf.with_suffix(".tmp.pdf")
    doc.save(tmp)
    doc.close()
    tmp.replace(pdf)
    return True


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source", type=Path, default=SOURCE)
    p.add_argument("--out", type=Path, default=None,
                   help="destination folder; default the darkroom (sapper SAP006)")
    p.add_argument("--also", type=Path, default=None,
                   help="a second destination, usually docs/methods/one_page")
    a = p.parse_args(argv)

    from bugarach.paths import darkroom, unresolved_message
    out = a.out or darkroom()
    if out is None and a.also is None:
        print(unresolved_message(), file=sys.stderr)
        return 1

    work = Path(tempfile.mkdtemp()) / "methods_one_page.pdf"
    print_pdf(a.source, work)
    problems = check(work, a.source)
    if problems:
        print("REFUSED: " + "; ".join(problems) + ". Cut text; do not shrink the type.",
              file=sys.stderr)
        return 1
    stamped = stamp_author(work)
    for d in [x for x in (out, a.also) if x is not None]:
        d.mkdir(parents=True, exist_ok=True)
        dest = d / "methods_one_page.pdf"
        shutil.copyfile(work, dest)
        print(f"wrote {dest}  (2 pages, methods on page 1; author "
              f"{'stamped' if stamped else 'not stamped: PyMuPDF absent'})")
    if out is None:
        print("darkroom not found: repo copy only. " + unresolved_message(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
