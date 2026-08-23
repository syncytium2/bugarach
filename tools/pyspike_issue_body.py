"""Emit the PySpike max_tau issue exactly as it must be pasted into GitHub.

The report lives hard-wrapped near 80 columns inside
docs/todo/2026-08-11-file-pyspike-max-tau-issue.md, because that is how the repo
reads. GitHub renders an issue body with hard line breaks on, so pasting the
wrapped source ships every paragraph as a stack of short ragged lines. This
unwraps prose runs and leaves fenced blocks, tables, headings and blockquotes
exactly as written -- the same distinction the file's own paste instructions
draw, mechanized so nobody has to redraw it by hand.

    python tools/pyspike_issue_body.py            # issue body to stdout
    python tools/pyspike_issue_body.py --title    # the issue title, alone
    python tools/pyspike_issue_body.py --note     # the note to Kreuz, unwrapped

The note is the shorter, personal route -- Kreuz is senior author on the measure
papers and maintains cSPIKE, and Mulansky is his collaborator -- so it unwraps
the same way, for pasting into mail.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

SOURCE = (pathlib.Path(__file__).resolve().parent.parent
          / "docs" / "todo" / "2026-08-11-file-pyspike-max-tau-issue.md")

START = "## Draft issue text"
END = "## Notes for the reviewer"
NOTE_START = "**Subject:**"          # the guidance above it is not the note
NOTE_END = "## Draft issue text"
TITLE = re.compile(r"^\*\*Title:\*\*\s*(.+)$")


def _slice(text: str, first_marker: str = START,
           last_marker: str = END, keep_first: bool = False) -> list[str]:
    lines = text.splitlines()
    try:
        first = next(i for i, ln in enumerate(lines)
                     if ln.startswith(first_marker))
        last = next(i for i, ln in enumerate(lines)
                    if i > first and ln.startswith(last_marker))
    except StopIteration:  # pragma: no cover - the file would have to be gutted
        sys.exit("%s: cannot find %r .. %r" % (SOURCE, first_marker, last_marker))
    return lines[first if keep_first else first + 1:last]


def title(text: str) -> str:
    for line in _slice(text):
        found = TITLE.match(line)
        if found:
            # Keep the backticks: the title opens with a literal `max_tau`.
            return found.group(1).strip()
    sys.exit("%s: the draft has no **Title:** line" % SOURCE)


def body(text: str, lines: list[str] | None = None) -> str:
    lines = _slice(text) if lines is None else lines
    out: list[str] = []
    para: list[str] = []
    fenced = False

    def flush() -> None:
        if para:
            out.append(" ".join(s.strip() for s in para))
            para.clear()

    for line in lines:
        if line.startswith("```"):
            flush()
            fenced = not fenced
            out.append(line)
            continue
        if fenced:
            out.append(line)
            continue
        if TITLE.match(line):          # the title is not part of the body
            continue
        stripped = line.strip()
        # A table row, a heading, a rule or a blank line stands on its own.
        if (not stripped or stripped.startswith("#") or stripped.startswith("|")
                or stripped == "---"):
            flush()
            out.append(line)
            continue
        # A list item or a blockquote opens a new run, and unwraps into it.
        if re.match(r"^\s*([-*+]|\d+\.)\s|^>", line):
            flush()
            para.append(line.rstrip())
            continue
        para.append(line)
    flush()

    joined = "\n".join(out).strip("\n")
    return re.sub(r"\n{3,}", "\n\n", joined) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    what = ap.add_mutually_exclusive_group()
    what.add_argument("--title", action="store_true",
                      help="print the issue title instead of the body")
    what.add_argument("--note", action="store_true",
                      help="print the note to Kreuz instead of the issue")
    args = ap.parse_args()
    text = SOURCE.read_text(encoding="utf-8")
    if args.title:
        sys.stdout.write(title(text) + "\n")
    elif args.note:
        note = _slice(text, NOTE_START, NOTE_END, keep_first=True)
        while note and note[-1].strip() in ("", "---"):   # drop the section rule
            note.pop()
        sys.stdout.write(body(text, note))
    else:
        sys.stdout.write(body(text))


if __name__ == "__main__":
    main()
