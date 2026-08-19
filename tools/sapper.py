#!/usr/bin/env python3
"""sapper — bugarach's mechanized rule gate (ported pattern from interface2).

A sapper clears mines from ground others are about to cross: each rule is a
hard-won lesson converted into a check that fires by itself. Every rule MUST
prove it can fire — `--selftest` runs each rule against embedded bad/good
fixtures; a check that cannot fire is worse than no check.

Usage:
  tools/sapper.py --selftest   prove every rule can fire (and stay silent)
  tools/sapper.py --all        scan all tracked files; exit 1 on BLOCK
  tools/sapper.py --staged     scan ADDED lines of the staged diff (pre-commit)
  tools/sapper.py --list       print the rule table

Wiring: tests/test_sapper.py runs --selftest and --all under pytest, so CI
enforces the rules; the optional pre-commit hook (.githooks/pre-commit,
enable with `git config core.hooksPath .githooks`) catches them earlier.
New-rule requests / disputes: file under docs/sapper_feedback/.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class Rule:
    id: str
    level: str            # "BLOCK" | "WARN"
    pattern: str          # regex, matched per line
    include: list[str]    # fnmatch globs of paths the rule applies to
    exclude: list[str]    # fnmatch globs exempt from the rule
    message: str
    fixture_bad: str      # one line the rule MUST fire on
    fixture_good: str     # one line the rule must NOT fire on


# Patterns for self-referential strings are assembled by concatenation so this
# file never trips its own rules when scanned.
_UM = "University of " + "Michigan"

RULES = [
    Rule(
        id="SAP001", level="BLOCK",
        pattern=r"np\.percentile\s*\(",
        include=["src/bugarach/**"], exclude=["src/bugarach/detectors/_shared.py"],
        message="MATLAB prctile matches NO numpy.percentile mode — use "
                "matlab_prctile from detectors/_shared (incident: LoCo port).",
        fixture_bad="thr = np.percentile(pool, 99.9)",
        fixture_good="thr = matlab_prctile(pool, 99.9)",
    ),
    Rule(
        id="SAP002", level="BLOCK",
        pattern=r"default_rng\s*\(",
        include=["src/bugarach/**"], exclude=[],
        message="Parity requires MATLAB's twister stream: rng(seed) == "
                "np.random.RandomState(seed). default_rng breaks every "
                "surrogate-based parity fixture.",
        fixture_bad="rng = np.random.default_rng(7)",
        fixture_good="rng = np.random.RandomState(7)",
    ),
    Rule(
        id="SAP003", level="BLOCK",
        pattern=r"^\s*(import|from)\s+pyspike",
        include=["src/bugarach/**"], exclude=[],
        message="PySpike 0.9.0's max_tau cap is broken (see detectors/sync.py)"
                " — PySpike is a TEST-ONLY cross-check in the uncapped regime,"
                " never a runtime dependency.",
        fixture_bad="import pyspike",
        fixture_good="from bugarach.detectors.sync import adaptive_profile",
    ),
    Rule(
        id="SAP004", level="BLOCK",
        pattern=r"(" + _UM + r"|DeFazio/|Dropbox/)",
        include=["**"],
        exclude=["tools/sapper.py"],
        message="Machine-local personal path in a tracked file — real data "
                "stays behind BUGARACH_DATA_ROOT (FOUNDATIONS §5; public-repo "
                "scrub incident 2026-08-11).",
        fixture_bad='ROOT = Path.home() / "' + _UM + ' Dropbox/name/data"',
        fixture_good='ROOT = os.environ.get("BUGARACH_DATA_ROOT")',
    ),
    Rule(
        id="SAP005", level="BLOCK",
        pattern=r"""["']{1,3}\s*<\s*(html\b|head\b|title\b)""",
        include=["**/*.py"], exclude=["tools/sapper.py"],
        message="An HTML document built here must open with "
                '<meta charset="utf-8">. Opened from disk (file://) a page '
                "with no declared charset is read as Latin-1, and every "
                "en-dash, ×, · and — in it renders as mojibake. Cost a review "
                "document 2026-08-13; the artifact pipeline hides this because "
                "it supplies its own head. (Known gap: sapper matches per line, "
                "so a literal opening '<!doctype html>' on its own line is not "
                "checked — see docs/sapper_feedback/.)",
        fixture_bad='page = f"""<title>Report</title><style>...',
        fixture_good='page = f"""<meta charset="utf-8">\\n<title>Report</title>',
    ),
    Rule(
        id="SAP006", level="BLOCK",
        pattern=r'add_argument\(\s*["\']--out["\'][^)]*required\s*=\s*True',
        # Deliberately NARROW: page and report builders only. Tools that write
        # data for a pipeline (derive_spec, assess_archive, fair_bakeoff) are
        # right to require an explicit --out, and a rule that fires on correct
        # code is a rule someone switches off. Figure tools that still require
        # --out are listed in docs/todo/2026-08-18-figure-tools-require-out.md.
        include=["tools/build_*.py", "tools/md_to_page.py"], exclude=[],
        message="A deliverable's destination must DEFAULT to the darkroom, never "
                "be required. Every figure tool here takes --out with "
                "`default=None` and falls back to bugarach.paths.darkroom(); a "
                "required --out means the output lands wherever the caller "
                "happened to point it. The report builder had this and the one "
                "deliverable meant for a person to read was the only one that "
                "never reached the darkroom — it sat in docs/learned until Tony "
                "asked where it was (2026-08-18). Use `default=None` plus "
                "`out = args.out or darkroom()`.",
        fixture_bad='p.add_argument("--out", type=Path, required=True)',
        fixture_good='p.add_argument("--out", type=Path, default=None)',
    ),
]


def _tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                         check=True)
    return out.stdout.splitlines()


def _applies(rule: Rule, path: str) -> bool:
    hit = any(fnmatch.fnmatch(path, g) for g in rule.include)
    exempt = any(fnmatch.fnmatch(path, g) for g in rule.exclude)
    return hit and not exempt


def _scan_lines(rule: Rule, path: str, lines) -> list[tuple[str, int, str]]:
    rx = re.compile(rule.pattern)
    return [(path, i, line.rstrip("\n"))
            for i, line in lines if rx.search(line)]


def scan_all() -> list[tuple[Rule, str, int, str]]:
    findings = []
    files = _tracked_files()
    for rule in RULES:
        for path in files:
            if not _applies(rule, path):
                continue
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    numbered = list(enumerate(f, 1))
            except OSError:
                continue
            for p, i, line in _scan_lines(rule, path, numbered):
                findings.append((rule, p, i, line))
    return findings


def scan_staged() -> list[tuple[Rule, str, int, str]]:
    out = subprocess.run(["git", "diff", "--cached", "--unified=0"],
                         capture_output=True, text=True, check=True).stdout
    findings = []
    path = None
    lineno = 0
    for raw in out.splitlines():
        if raw.startswith("+++ b/"):
            path = raw[6:]
        elif raw.startswith("@@"):
            m = re.search(r"\+(\d+)", raw)
            lineno = int(m.group(1)) - 1 if m else 0
        elif raw.startswith("+") and not raw.startswith("+++") and path:
            lineno += 1
            for rule in RULES:
                if _applies(rule, path) and re.search(rule.pattern, raw[1:]):
                    findings.append((rule, path, lineno, raw[1:]))
    return findings


def selftest() -> int:
    failures = 0
    for rule in RULES:
        rx = re.compile(rule.pattern)
        if not rx.search(rule.fixture_bad):
            print(f"SELFTEST FAIL {rule.id}: cannot fire on its bad fixture")
            failures += 1
        if rx.search(rule.fixture_good):
            print(f"SELFTEST FAIL {rule.id}: fires on its good fixture")
            failures += 1
    print(f"selftest: {len(RULES)} rules, {failures} failures")
    return 1 if failures else 0


def report(findings) -> int:
    blocked = False
    for rule, path, lineno, line in findings:
        print(f"{rule.level} {rule.id} {path}:{lineno}: {line.strip()}")
        print(f"    {rule.message}")
        blocked = blocked or rule.level == "BLOCK"
    if not findings:
        print("sapper: clear")
    return 1 if blocked else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--all", action="store_true")
    g.add_argument("--staged", action="store_true")
    g.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.list:
        for r in RULES:
            print(f"{r.id} {r.level:5s} {r.pattern}")
            print(f"    {r.message}")
        return 0
    return report(scan_staged() if args.staged else scan_all())


if __name__ == "__main__":
    sys.exit(main())
