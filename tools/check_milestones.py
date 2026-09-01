#!/usr/bin/env python3
"""Every row in MILESTONES.md must resolve against the tree it describes.

    python3 tools/check_milestones.py [FILE]     check (default docs/MILESTONES.md)
    python3 tools/check_milestones.py --selftest prove every rule can still fire

WHY THIS EXISTS, AND WHAT ITS FIRST VERSION GOT WRONG. A milestone doc's whole value is
that it does not rot, and the failure it guards against -- a document stating as settled
something the commit behind it called open -- is not caught by prose review. The first
version of this file was reviewed by eleven roles and **four of its rules were broken in
ways that all reported success**:

  * the path rule required a file extension, so `src/bugarach/detectors/` and `docs/site/`
    were never looked at while the summary printed "29 paths" -- coverage reported over a
    set that silently excluded its own members;
  * a directory branch existed and could never execute, because no path the regex matched
    could end in `/`;
  * an empty document printed "OK -- every row resolves" and exited 0;
  * the evidence/decided rule fired on "K was never decided" and PASSED "was never an open
    question", which is the exact sentence the real decay used.

So every rule below is exercised by `--selftest`, in both directions where it has two. A
rule that cannot fail is not a check, and this file has already shipped four of them.

RESOLUTION TARGET. Commits are checked for ancestry (that claim IS the row's content).
Paths are checked on the FILESYSTEM, because MILESTONES' own rule is that a row lands in
the same change as the work it describes -- resolving paths against origin/main would make
the documented workflow impossible and would fail on a shallow CI clone.
`tests/test_index_resolves.py` reached that conclusion first; see its lines 99-104.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_DOC = REPO / "docs" / "MILESTONES.md"

STRENGTHS = {"built", "measured", "decided", "evidence"}
STATUS_RE = re.compile(r"^(current|held|inert|open|superseded by .+)", re.I)

SHA = re.compile(r"`([0-9a-fA-F]{7,40})`")
# Any backticked token that looks like a path: contains a slash, OR ends in a known
# extension. Extension-only was the bug that skipped every directory row.
PATHY = re.compile(
    r"`([A-Za-z0-9_.\-/]*/[A-Za-z0-9_.\-]*"
    r"|[A-Za-z0-9_.\-]+\.(?:md|py|json|toml|html|js|sh|yml|cff))`")
# Cells that are deliberately not paths: a dotted code symbol, or a placeholder.
NOT_A_PATH = re.compile(r"^(—|-|n/a|[A-Za-z_][A-Za-z0-9_]*\.[A-Z][A-Z0-9_]*)$")

# An `evidence` row asserting its own subject is settled. Negation and futurity are
# exempt: the honest hedge must survive, or the rule punishes the writing it protects.
ASSERTS_SETTLED = re.compile(
    r"\b(the decided|was decided|is decided|has been decided|settled"
    r"|was chosen|is final|never an open question)\b", re.I)
NEGATED = re.compile(r"\b(not|never|no|yet|pending|awaiting|refuses|unchosen|open)\b", re.I)


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


def base_ref():
    """The ref to test ancestry against. Never invent one: a checker that cannot resolve
    its baseline must say so, not report every row as broken -- which is what a shallow
    `actions/checkout` would otherwise produce."""
    for ref in ("origin/main", "main", "HEAD"):
        if git("rev-parse", "--verify", "-q", f"{ref}^{{commit}}").returncode == 0:
            return ref
    return None


def rows(text):
    """(line_no, cells) for every data row of every pipe table."""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s.startswith("|") or set(s) <= set("|-: "):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) >= 4 and cells[0].strip().lower() != "milestone":
            out.append((i, cells))
    return out


def bare(s):
    return re.sub(r"[*_`⚠]+", "", s).strip()


def check(doc):
    fails, stats = [], {"sha": 0, "path": 0, "rows": 0, "skipped": 0}
    if not doc.exists():
        return [f"{doc} does not exist"], stats

    ref = base_ref()
    if ref is None:
        return ["cannot resolve a base ref (origin/main, main or HEAD) -- run "
                "`git fetch origin main`; refusing to judge rows against nothing"], stats

    data = rows(doc.read_text())
    stats["rows"] = len(data)

    # A document with no rows certifying itself is the failure this repo has shipped
    # three times. cf. tests/test_index_resolves.py::test_the_index_has_not_quietly_emptied
    if not data:
        fails.append("no milestone rows found -- an empty document cannot pass")

    for lineno, cells in data:
        row = " | ".join(cells)
        plain = bare(row)

        for m in SHA.finditer(row):
            sha = m.group(1)
            stats["sha"] += 1
            if git("cat-file", "-e", f"{sha}^{{commit}}").returncode != 0:
                fails.append(f"line {lineno}: `{sha}` no such commit")
            elif git("merge-base", "--is-ancestor", sha, ref).returncode != 0:
                fails.append(f"line {lineno}: `{sha}` not an ancestor of {ref}")

        for m in PATHY.finditer(row):
            p = m.group(1)
            if NOT_A_PATH.match(p):
                stats["skipped"] += 1
                continue
            stats["path"] += 1
            if not (REPO / p).exists():
                fails.append(f"line {lineno}: path `{p}` does not exist")

        # The strength column is what the whole document turns on; leaving it
        # unvalidated is how `done` -- a fifth value -- shipped in the first draft.
        strength = bare(cells[2]).split("(")[0].strip().lower() if len(cells) > 2 else ""
        if strength and strength not in STRENGTHS:
            fails.append(f"line {lineno}: strength `{strength}` is not one of "
                         + "/".join(sorted(STRENGTHS)))
        if len(cells) >= 6:
            status = bare(cells[5])
            if status and not STATUS_RE.match(status):
                fails.append(f"line {lineno}: status `{status[:40]}` must start with "
                             "current/held/inert/open/superseded by")

        if re.search(r"superseded", plain, re.I) \
                and not re.search(r"superseded by\s+\S", plain, re.I) \
                and "supersedes" not in plain.lower():
            fails.append(f"line {lineno}: 'superseded' without 'superseded by <row>'")

        if strength == "evidence":
            hit = ASSERTS_SETTLED.search(plain)
            if hit and not NEGATED.search(plain[max(0, hit.start() - 24):hit.start()]):
                fails.append(f"line {lineno}: an `evidence` row asserts "
                             f"`{hit.group(0)}` about its own subject")

    return fails, stats


HEAD = ("---\nstatus: living\n---\n# t\n\n"
        "| milestone | what | strength | commit | doc | status |\n"
        "|---|---|---|---|---|---|\n")


def selftest():
    """Every rule, proven fireable -- in both directions where it has two."""
    good = git("rev-parse", "--short", "HEAD").stdout.strip()
    cases = [
        ("clean control", f"| a | b | measured | `{good}` | `docs/INDEX.md` | current |", 0),
        ("bad sha", "| a | b | measured | `0000000` | `docs/INDEX.md` | current |", 1),
        ("bad file path", f"| a | b | measured | `{good}` | `docs/nope.md` | current |", 1),
        ("bad DIRECTORY path", f"| a | b | measured | `{good}` | `docs/no_dir/` | current |", 1),
        ("good directory path (MUST PASS)",
         f"| a | b | measured | `{good}` | `docs/site/` | current |", 0),
        ("undeclared strength", f"| a | b | done | `{good}` | `docs/INDEX.md` | current |", 1),
        ("undeclared status", f"| a | b | measured | `{good}` | `docs/INDEX.md` | FINE |", 1),
        ("superseded, no successor",
         f"| a | b | measured | `{good}` | `docs/INDEX.md` | superseded |", 1),
        ("evidence asserts settled",
         f"| a | the decided K | evidence | `{good}` | `docs/INDEX.md` | open |", 1),
        ("evidence, the real decay wording",
         f"| a | it was never an open question | evidence | `{good}` | `docs/INDEX.md` | open |", 1),
        ("evidence hedges honestly (MUST PASS)",
         f"| a | K was never decided; still open | evidence | `{good}` | `docs/INDEX.md` | open |", 0),
        ("empty document", "", 1),
    ]
    bad = 0
    tmp = REPO / ".selftest_milestones.md"
    for name, row, want in cases:
        tmp.write_text(HEAD + row + "\n" if row else "---\nstatus: living\n---\n# t\n")
        got = 1 if check(tmp)[0] else 0
        if got != want:
            bad += 1
        print(f"  {'ok  ' if got == want else 'FAIL'} {name}: "
              f"expected {'fail' if want else 'pass'}, got {'fail' if got else 'pass'}")
    tmp.unlink(missing_ok=True)
    print(f"selftest: {len(cases)} cases, {bad} failures")
    return 1 if bad else 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    doc = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DOC
    fails, st = check(doc)
    print(f"checked {st['sha']} commit refs, {st['path']} paths "
          f"({st['skipped']} non-path cells), {st['rows']} rows")
    for f in fails:
        print("  FAIL", f)
    print("OK -- every row resolves" if not fails else f"{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
