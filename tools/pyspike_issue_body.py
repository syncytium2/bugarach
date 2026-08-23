"""Emit the PySpike max_tau issue exactly as it must be pasted into GitHub.

The report lives hard-wrapped near 80 columns inside
docs/todo/2026-08-11-file-pyspike-max-tau-issue.md, because that is how the repo
reads. GitHub renders an issue body with hard line breaks on, so pasting the
wrapped source ships every paragraph as a stack of short ragged lines. This
unwraps prose runs and leaves fenced blocks, tables, headings and blockquotes
exactly as written -- the same distinction the file's own paste instructions
draw, mechanized so nobody has to redraw it by hand.

    python tools/pyspike_issue_body.py            # body to stdout
    python tools/pyspike_issue_body.py --title    # the issue title, alone
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
TITLE = re.compile(r"^\*\*Title:\*\*\s*(.+)$")


def _slice(text: str) -> list[str]:
    lines = text.splitlines()
    try:
        first = next(i for i, ln in enumerate(lines) if ln.startswith(START))
        last = next(i for i, ln in enumerate(lines) if ln.startswith(END))
    except StopIteration:  # pragma: no cover - the file would have to be gutted
        sys.exit("%s: cannot find the draft section" % SOURCE)
    return lines[first + 1:last]


def title(text: str) -> str:
    for line in _slice(text):
        found = TITLE.match(line)
        if found:
            # Keep the backticks: the title opens with a literal `max_tau`.
            return found.group(1).strip()
    sys.exit("%s: the draft has no **Title:** line" % SOURCE)


def body(text: str) -> str:
    lines = _slice(text)
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
    ap.add_argument("--title", action="store_true",
                    help="print the issue title instead of the body")
    args = ap.parse_args()
    text = SOURCE.read_text(encoding="utf-8")
    sys.stdout.write(title(text) + "\n" if args.title else body(text))


if __name__ == "__main__":
    main()
