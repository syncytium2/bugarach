#!/usr/bin/env python3
# instrument: verification
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

# An `evidence` row asserting its own subject is settled.
#
# THIS WAS A BLOCKLIST OF FIVE IDIOMS AND AN ADVERSARIAL PASS DEFEATED IT FOURTEEN WAYS,
# including with a sentence sitting in the tree right now --
# `docs/todo/2026-08-31-two-overnight-results-need-a-ruling.md`: "K=12 was already
# decided". One inserted adverb broke a literal `was decided` match. So: match the LEMMA
# (decid/chos/settl/resolv/final/rul/pick/clos) and allow intervening words, rather than
# freezing the phrasings we happened to think of.
#
# TWO PATTERNS, BECAUSE NEGATION CUTS BOTH WAYS. "K was never decided" is the honest
# hedge and must pass; "it was never an open question" is the assertion and must fail.
# Both contain "never". What differs is WHAT is negated -- the settling, or the openness.
# So a negator exempts a SETTLED-lemma hit, and never exempts a DENIES_OPEN hit.
ASSERTS_SETTLED = re.compile(
    r"\b(?:the|is|was|were|has been|have been|been|we|i)\b[^.;|]{0,40}?"
    r"\b(decided|chosen|settled|resolved|final|finalised|finalized|ruled|picked|closed"
    r"|canonical|signed off|stands)\b"
    r"|\bthe decided\b", re.I)
DENIES_OPEN = re.compile(
    r"\b(?:never|not|no longer|nor)\b[^.;|]{0,24}?"
    r"\b(open|in question|unsettled|undecided|up for debate)\b", re.I)
# Negation exempts an assertion only when it actually negates it: the negator must be
# adjacent to the matched verb, not merely somewhere in a 24-character window. The window
# form was itself a bypass -- putting the word "open" nearby switched the rule off.
NEGATED = re.compile(
    r"\b(not|never|no|nor|yet|unchosen|undecided|pending|awaiting"
    r"|refuses?|cannot|isn't|wasn't|hasn't)\b", re.I)


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

    # A shallow clone has no history, so EVERY historical sha reports "no such commit"
    # and the run reads as 36 fabricated citations. That is a checker blaming the
    # document for its own environment -- and it is what turned CI red on this file's
    # first run, exactly as two review roles predicted. Say the real reason, once.
    if git("rev-parse", "--is-shallow-repository").stdout.strip() == "true":
        return ["this clone is SHALLOW, so commit ancestry cannot be checked at all. "
                "This is an environment fault, not a document fault -- set "
                "`fetch-depth: 0` on the checkout step. Refusing to report rows as "
                "broken when the history to judge them against is absent."], stats

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
            # Denying that the question is open is an assertion that it is settled, and
            # no negator exempts it -- the negation IS the assertion.
            denial = DENIES_OPEN.search(plain)
            if denial:
                fails.append(f"line {lineno}: an `evidence` row asserts "
                             f"`{denial.group(0)}` about its own subject")
            else:
                hit = ASSERTS_SETTLED.search(plain)
                # The negator usually sits INSIDE the assertion ("was never decided"),
                # not before it. Checking only the preceding window is how the earlier
                # rule failed the honest hedge while passing the real decay.
                if hit and not NEGATED.search(hit.group(0)) \
                        and not NEGATED.search(plain[max(0, hit.start() - 24):hit.start()]):
                    fails.append(f"line {lineno}: an `evidence` row asserts "
                                 f"`{hit.group(0)}` about its own subject")

    return fails, stats


HEAD = ("---\nstatus: living\n---\n# t\n\n"
        "| milestone | what | strength | commit | doc | status |\n"
        "|---|---|---|---|---|---|\n")


def selftest():
    """Every rule, proven fireable -- in both directions where it has two."""
    # NOT `HEAD`: the moment this work is committed on a feature branch, HEAD stops being
    # an ancestor of origin/main and every fixture using it fails for a reason that has
    # nothing to do with the rule under test. Use a commit that is an ancestor by
    # construction -- the merge base -- so the fixtures test the rules and not the branch.
    ref = base_ref() or "HEAD"
    good = (git("merge-base", "HEAD", ref).stdout.strip()
            or git("rev-parse", "HEAD").stdout.strip())[:7]

    # THE FIXTURES USED TO NAME `docs/INDEX.md` AND `docs/site/` AND THAT WAS A DEFECT.
    # Both are bugarach paths, so the selftest asserted THIS repo's directory layout
    # rather than the rules under test. Carried anywhere else, four MUST-PASS cases go
    # red on first run for a reason that has nothing to do with a milestone row -- which
    # is the same shape as the unfireable rules this file's header confesses to, one level
    # out. short-course found it by carrying the file and watching it fail; they are the
    # reason these two lines exist. Derive from the tree so the fixtures travel.
    f_ok = next((p for p in ("docs/INDEX.md", "docs/SESSIONS.md", "README.md")
                 if (REPO / p).is_file()), "README.md")
    d_ok = next((p for p in ("docs/site/", "docs/", "tools/")
                 if (REPO / p).is_dir()), "docs/")

    # A FIFTH RULE THAT COULD NOT FIRE, and the one this tool is named for. The only
    # bad-sha fixture was `0000000`, which dies at `cat-file -e` and never reaches the
    # ancestry branch below it -- so `a row may not cite a commit unreachable from the
    # trunk` was asserted and never exercised. Reproduced before fixing: replacing that
    # branch with `elif False:` left the selftest reporting 18 cases, 0 failures. Found by
    # short-course's mutation gate, not by review, which is why it survived four rounds of
    # someone reading this file.
    #
    # The fixture is a commit that EXISTS and is NOT an ancestor: same tree, parented on
    # the merge base, so it is a descendant of the trunk rather than on it. `cat-file -e`
    # finds it; `merge-base --is-ancestor` refuses it. Built with `commit-tree` so no ref
    # moves and there is nothing to clean up -- it is a loose object git will collect.
    # IDENTITY IS PASSED EXPLICITLY, and CI is why. `commit-tree` needs a committer, and a
    # fresh runner has no `user.email` configured, so this returned empty there while
    # passing here -- and an empty sha makes the row below contain an empty backtick pair,
    # which the SHA regex does not match, so the case PASSED for want of a fixture. That is
    # the exact defect this block exists to fix, reproduced one level along: my unfireable
    # rule got an unfireable fixture. `-c` on the command keeps it local to this call rather
    # than writing anybody's git config.
    not_anc = git("-c", "user.name=selftest", "-c", "user.email=selftest@invalid",
                  "commit-tree", f"{good}^{{tree}}", "-p", good,
                  "-m", "fixture: exists, not an ancestor").stdout.strip()[:7]
    # AND IT IS CHECKED, because the failure above was silent. A fixture that did not get
    # built must stop the selftest, not quietly turn one case into a no-op.
    if not re.fullmatch(r"[0-9a-f]{7}", not_anc):
        print("selftest CANNOT RUN: `git commit-tree` produced no commit, so the "
              "not-an-ancestor fixture does not exist. Refusing to report on a rule "
              "with nothing to test it -- that is the defect this case was added for.")
        return 1

    cases = [
        ("clean control", f"| a | b | measured | `{good}` | `{f_ok}` | current |", 0),
        ("bad sha", f"| a | b | measured | `0000000` | `{f_ok}` | current |", 1),
        # The case the ancestry rule never had. `0000000` above stops at `cat-file -e`;
        # this one gets past it and must be refused for the other reason.
        ("sha exists but is NOT an ancestor",
         f"| a | b | measured | `{not_anc}` | `{f_ok}` | current |", 1),
        ("bad file path", f"| a | b | measured | `{good}` | `docs/nope.md` | current |", 1),
        ("bad DIRECTORY path", f"| a | b | measured | `{good}` | `docs/no_dir/` | current |", 1),
        ("good directory path (MUST PASS)",
         f"| a | b | measured | `{good}` | `{d_ok}` | current |", 0),
        ("undeclared strength", f"| a | b | done | `{good}` | `{f_ok}` | current |", 1),
        ("undeclared status", f"| a | b | measured | `{good}` | `{f_ok}` | FINE |", 1),
        ("superseded, no successor",
         f"| a | b | measured | `{good}` | `{f_ok}` | superseded |", 1),
        # The four sentences the real decay actually used, verbatim from the tree.
        # An adversarial pass defeated the previous rule with the first of these.
        ("decay wording 1/4: 'was already decided'",
         f"| a | K=12 was already decided | evidence | `{good}` | `{f_ok}` | open |", 1),
        ("decay wording 2/4: 'the decided K'",
         f"| a | the decided K | evidence | `{good}` | `{f_ok}` | open |", 1),
        ("decay wording 3/4: 'was decided by a real effort'",
         f"| a | K was decided by a real effort | evidence | `{good}` | `{f_ok}` | open |", 1),
        ("decay wording 4/4: 'never an open question'",
         f"| a | it was never an open question | evidence | `{good}` | `{f_ok}` | open |", 1),
        ("paraphrase: 'is the chosen value'",
         f"| a | K=12 is the chosen value | evidence | `{good}` | `{f_ok}` | open |", 1),
        ("paraphrase: 'the question is closed'",
         f"| a | the K question is closed | evidence | `{good}` | `{f_ok}` | open |", 1),
        ("paraphrase: 'we picked K=12'",
         f"| a | we picked K=12 | evidence | `{good}` | `{f_ok}` | open |", 1),
        ("hedge MUST PASS: 'was never decided'",
         f"| a | K was never decided; still open | evidence | `{good}` | `{f_ok}` | open |", 0),
        ("hedge MUST PASS: 'not yet decided'",
         f"| a | not yet decided | evidence | `{good}` | `{f_ok}` | open |", 0),
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
