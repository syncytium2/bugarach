#!/usr/bin/env python3
# instrument: verification
"""`docs/pipelines.md` and `docs/pipelines/` must agree, in both directions.

    python3 tools/check_pipelines.py [INDEX]     check (default docs/pipelines.md)
    python3 tools/check_pipelines.py --selftest  prove every rule can still fire

WHY THIS EXISTS. `pipelines.md` claims to be the first place a session looks to find out
whether an established route to a result already exists. That claim is only worth
anything while the index and the directory agree, and a hand-kept index decays in two
directions that prose review does not catch:

  * a row pointing at a pipeline that has been renamed, moved or deleted — the reader
    follows a link to nothing and concludes the route does not exist;
  * a pipeline on disk that no row mentions — the route exists, the index says it does
    not, and the next session builds it again. That is the failure the whole index is
    meant to prevent, and it is the silent one.

Both are checkable, so neither is left to memory. The pattern is `check_milestones.py`'s,
deliberately: that tool's docstring records that its own first version shipped four rules
that could not fire and reported success anyway, including an empty document printing
"OK" and exiting 0. So every rule here is exercised by `--selftest` in both directions,
and an index that parses no rows is a failure, not a pass.

Consulted armory (2026-09-16) before writing this: no convention for pipelines exists
anywhere in the estate, and its recommendation was "generated or checked, never
hand-kept" — on interface2's evidence that two hand-maintained maps in that repo decayed
into being wrong. This is the "checked" half. The index stays hand-written, because what
a route is FOR is not derivable from the tree; what is derivable — that it exists and is
listed — is what this checks.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_INDEX = REPO / "docs" / "pipelines.md"
PIPELINE_DIR_NAME = "pipelines"

#: A markdown link whose target sits inside the pipelines directory. Anchors and titles are
#: tolerated; the captured group is the path as written.
ROW_RE = re.compile(r"\[[^\]]+\]\(\s*(?:\./)?(" + PIPELINE_DIR_NAME + r"/[^)\s#]+\.md)")

#: Every pipeline answers these before a reader commits a night to it. Kept deliberately
#: short: armory's advice was that the generalisable fields are whichever ones the SECOND
#: route cannot do without, so this asserts only what the first one proved it needed.
REQUIRED_FIELDS = ("Use it when", "It produces")


def _listed(index_text: str) -> set[str]:
    return set(ROW_RE.findall(index_text))


def _on_disk(root: Path) -> set[str]:
    d = root / PIPELINE_DIR_NAME
    if not d.is_dir():
        return set()
    return {f"{PIPELINE_DIR_NAME}/{p.name}" for p in sorted(d.glob("*.md"))}


def check(index: Path) -> list[str]:
    """Return a list of problems; empty means the index and the directory agree."""
    problems: list[str] = []
    if not index.is_file():
        return [f"{index} does not exist — the index a session is told to read first is missing"]

    text = index.read_text(encoding="utf-8")
    root = index.parent
    listed, on_disk = _listed(text), _on_disk(root)

    # An index that lists nothing must not pass. `check_milestones.py` shipped exactly this
    # bug: an empty document printed "OK -- every row resolves" and exited 0.
    if not listed:
        problems.append(
            f"{index.name} lists no pipelines — either it is empty, or its rows do not link "
            f"into `{PIPELINE_DIR_NAME}/`. An index that resolves nothing cannot be the first "
            f"place a session looks")

    for rel in sorted(listed):
        if not (root / rel).is_file():
            problems.append(
                f"{index.name} points at `{rel}`, which does not exist — a reader follows that "
                f"row to nothing and concludes the route was never built")

    for rel in sorted(on_disk - listed):
        problems.append(
            f"`{rel}` exists but no row in {index.name} mentions it — the route exists, the "
            f"index says it does not, and the next session builds it again")

    for rel in sorted(listed & on_disk):
        body = (root / rel).read_text(encoding="utf-8")
        missing = [f for f in REQUIRED_FIELDS if f.lower() not in body.lower()]
        if missing:
            problems.append(
                f"`{rel}` does not say {' or '.join(repr(m) for m in missing)} — a reader "
                f"cannot tell whether this route is the one they want without running it")

    return problems


# --------------------------------------------------------------------------- selftest

def _write(root: Path, index_rows: str, pipelines: dict[str, str]) -> Path:
    (root / PIPELINE_DIR_NAME).mkdir(parents=True, exist_ok=True)
    for name, body in pipelines.items():
        (root / PIPELINE_DIR_NAME / name).write_text(body, encoding="utf-8")
    idx = root / "pipelines.md"
    idx.write_text("# Pipelines\n\n" + index_rows, encoding="utf-8")
    return idx


GOOD_BODY = "# Pipeline: x\n\n**Use it when** you need x.\n**It produces** a result.\n"


def selftest() -> int:
    """Every rule, fired and not fired. A rule that cannot fail is not a check."""
    cases = []

    def case(name, rows, files, *, want_problem):
        with tempfile.TemporaryDirectory() as td:
            idx = _write(Path(td), rows, files)
            got = check(idx)
            ok = bool(got) == want_problem
            cases.append((name, ok, got))

    row = "- [the x route](pipelines/x.md) — does x\n"
    case("clean index passes", row, {"x.md": GOOD_BODY}, want_problem=False)
    case("empty index fails", "", {}, want_problem=True)
    case("index with prose but no links fails", "nothing here yet\n", {}, want_problem=True)
    case("row pointing at a missing file fails", row, {}, want_problem=True)
    case("pipeline missing from the index fails", row,
         {"x.md": GOOD_BODY, "orphan.md": GOOD_BODY}, want_problem=True)
    case("pipeline without the required fields fails", row,
         {"x.md": "# Pipeline: x\n\nnothing useful\n"}, want_problem=True)
    case("two listed and present pass", row + "- [y](pipelines/y.md) — does y\n",
         {"x.md": GOOD_BODY, "y.md": GOOD_BODY}, want_problem=False)

    failed = [(n, g) for n, ok, g in cases if not ok]
    for name, ok, got in cases:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
        if not ok:
            print(f"        got: {got}")
    if failed:
        print(f"\ncheck_pipelines --selftest: {len(failed)} of {len(cases)} rules did not behave")
        return 1
    print(f"\ncheck_pipelines --selftest: {len(cases)} rules, every one fires and clears")
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return selftest()
    index = Path(argv[0]) if argv else DEFAULT_INDEX
    problems = check(index)
    if problems:
        print(f"check_pipelines: {len(problems)} problem(s) in {index}", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1
    n = len(_listed(index.read_text(encoding="utf-8")))
    print(f"check_pipelines: {index.name} and {PIPELINE_DIR_NAME}/ agree — {n} route(s), "
          f"each listed, present, and saying what it is for")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
