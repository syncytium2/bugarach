#!/usr/bin/env python3
"""Report which quotations in a document can be found in a PDF on the lit shelf.

    python tools/verify_quotes.py docs/detector_history.md \
        "<darkroom>/bugarach/lit/radar" "<darkroom>/bugarach/lit/coordination"

Murderboard role 2 ("DOI or Die") done by machine, for the one class of claim it
cannot check by reasoning: a quoted sentence either is in the source or it is not.

⚠ **PROVISIONAL — a reporting aid, not a gate, and deliberately not wired into
CI.** On the 1980s scans this shelf holds it still reports **false misses**: OCR
breaks words across lines without hyphens ("mea-\\nsure" but also "supe\\nrior"),
drops characters, and the column reconstruction below does not always reassemble a
sentence that spans a line break. Measured on `detector_history.md`, it traced 11
of 30 quotations while hand-checking every one against ``pdftotext -layout``
confirmed **all sixteen paper quotations were genuine** — the rest quote repo docs
and interface2, which are not PDFs and can never match.

So: **a MISS means "check this by hand", never "this is wrong."** A hit is
meaningful; a miss is not. Finishing it is
`docs/todo/2026-08-22-quote-verification-is-not-a-gate-yet.md`.

**Its one sound contribution today is the hazard it documents** (below): the
obvious implementation can *manufacture* a quotation that appears nowhere on the
page, and that is worth knowing whether or not this script ever becomes a gate.

**Why this is not a one-line grep.** The obvious check — extract the PDF text,
collapse all whitespace, search — is unsound on the two-column scans this shelf is
full of, and it is unsound in *both* directions:

- **False negatives.** A sentence broken across a line keeps a hyphen
  ("mean-\\nlevel"), and a phrase spanning a column break never appears contiguous.
  Two real quotations from Gandhi & Kassam 1988 failed exactly this way.
- **False positives, which are worse.** `pdftotext` without ``-layout`` interleaves
  the columns line by line, so collapsing whitespace **splices text from the left
  column onto text from the right** and manufactures sentences that appear nowhere
  on the page. A checker that can invent a match is not a checker.

So: extract with ``-layout``, split each line into cells on runs of 3+ spaces,
bucket cells by their starting x-offset into columns, join each column separately,
then de-hyphenate and normalise. A quotation matches only if it is contiguous
*within one column* — which is the same standard a human reading the page applies.

OCR of a 1980s scan is imperfect ("a r e" for "are"), so matching is done on
letters and digits only, with all other characters dropped from both sides.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

#: quotations are marked in the markdown as *"..."* or **"..."**
QUOTE_RE = re.compile(r'\*{1,2}"([^"]{25,400})"\*{1,2}|\*"([^"]{25,400})"\*')
#: a run of this many spaces in -layout output separates columns
COL_GAP = 3


def squash(s: str) -> str:
    """Letters and digits only, lowercased — OCR noise and markup fall away."""
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def columns(pdf: Path) -> list[str]:
    """The PDF's text as one string per column, never spliced across columns."""
    try:
        raw = subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                             capture_output=True, text=True, timeout=120).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    # Two passes, because neither ordinal nor raw offset works alone. Ordinal
    # position fails on any line where the left column is blank — that line's
    # single cell is right-column text and lands in stream 0, splicing the two
    # columns together, which is the exact false-positive this tool exists to
    # rule out. Raw offset fails because these scans drift several characters of
    # indent per line, scattering one column across many streams.
    #
    # So: learn the column origins from the whole page first, then assign every
    # cell to its nearest origin.
    cells_by_line = []
    for line in raw.splitlines():
        row, pos = [], 0
        for cell in re.split(rf" {{{COL_GAP},}}", line):
            if cell.strip():
                row.append((pos + len(cell) - len(cell.lstrip()), cell.strip()))
            pos += len(cell) + COL_GAP
        if row:
            cells_by_line.append(row)

    offsets = sorted(off for row in cells_by_line for off, _ in row)
    origins: list[int] = []
    for off in offsets:                       # single-pass clustering, 15-char tolerance
        if not origins or off - origins[-1] > 15:
            origins.append(off)
    # keep only origins that carry real text; stray indents make singleton columns
    counts = {o: 0 for o in origins}
    for row in cells_by_line:
        for off, _ in row:
            counts[min(origins, key=lambda o: abs(o - off))] += 1
    origins = [o for o in origins if counts[o] >= max(3, 0.02 * sum(counts.values()))]
    if not origins:
        origins = [0]

    buckets: dict[int, list[str]] = {}
    for row in cells_by_line:
        for off, text in row:
            key = min(origins, key=lambda o: abs(o - off))
            buckets.setdefault(key, []).append(text)
    # de-hyphenate at line ends, then join each column into one running text
    out = []
    for _, lines in sorted(buckets.items()):
        text = "\n".join(lines)
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
        out.append(text.replace("\n", " "))
    # A single-column paper has no column structure to respect, so its whole text
    # is a legitimate haystack. A MULTI-column one is not: joining it splices the
    # left column onto the right and can manufacture a match. Only add the
    # whole-page text when the page really is one column.
    if len(buckets) <= 1:
        out.append(re.sub(r"(\w)-\n(\w)", r"\1\2", raw).replace("\n", " "))
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("document", type=Path)
    p.add_argument("shelves", type=Path, nargs="+",
                   help="directories of source PDFs")
    p.add_argument("--min-len", type=int, default=25)
    a = p.parse_args(argv)

    pdfs = sorted(q for s in a.shelves for q in s.glob("*.pdf"))
    if not pdfs:
        print("no PDFs found on the given shelves", file=sys.stderr)
        return 2
    haystacks = {q.stem: [squash(c) for c in columns(q)] for q in pdfs}

    quotes = []
    for m in QUOTE_RE.finditer(a.document.read_text()):
        q = m.group(1) or m.group(2)
        if q and len(q) >= a.min_len:
            quotes.append(q)

    missing = 0
    for q in quotes:
        needle = squash(q)
        hit = next((stem for stem, cols in haystacks.items()
                    if any(needle in c for c in cols)), None)
        if hit is None:
            missing += 1
        flat = " ".join(q.split())
        print(f"{'ok  ' if hit else 'MISS'}  {flat[:58]:58s}  {hit or '—'}")

    print(f"\n{len(quotes) - missing}/{len(quotes)} quotations traced to a shelf PDF")
    if missing:
        print("Misses need hand-checking against pdftotext -layout; this tool "
              "under-reports on two-column scans (see the module docstring).",
              file=sys.stderr)
    return 0   # provisional: a miss means "check by hand", never "this is wrong"


if __name__ == "__main__":
    sys.exit(main())
