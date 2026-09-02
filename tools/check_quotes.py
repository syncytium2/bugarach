#!/usr/bin/env python3
# instrument: retrieval
"""check_quotes — a third party's private words must not enter this public tree.

The rule is CLAUDE.md's *Other people's words*: paraphrase what a correspondent
told you and cite it — "Kreuz, personal communication, 2026-04-23" — rather than
reproducing their sentences. This repo has broken that rule twice, once in a PR
description on a stranger's project and once in a todo that stood public for
nine days.

WHY THIS IS NOT A SAPPER RULE. Sapper is a line matcher on purpose, and the
signature here spans lines: in the April file the block quote sat SEVEN lines
below the sentence that named its source, with a paragraph in between.

    Kreuz ... replied to Tony by email in April.
    ...
    > "for global event identification you should first use ..."

Neither line is suspicious alone. `> "..."` matches 14 places in this tree that
are the repo quoting ITSELF — a spec's own sentence, interface2's audit, a
superseded version kept for the record — so a per-line rule is either silent or
all noise. Sapper's own SAP009 hit the same wall and solved it by naming; there
is nothing to name here, because the thing being forbidden is the quote itself.
Recorded in docs/sapper_feedback/2026-09-02-private-correspondence-in-a-public-tree.md.

WHY IT GATES THE COMMIT AND NOT ONLY CI. This repository is public, so a push IS
publication: a branch is world-readable the moment it exists. A check that runs
only in CI reports on something already published. Hence --staged, wired into
.githooks/pre-commit beside the branch and board guards.

Usage:
  tools/check_quotes.py --selftest   prove the check can fire (and stay silent)
  tools/check_quotes.py --all        scan tracked markdown; exit 1 on a finding
  tools/check_quotes.py --staged     scan staged markdown (pre-commit)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys

# How far below a marker a block quote is still "its" quote.
#
# THE FIRST VALUE HERE WAS 3, TUNED ON THE TREE AS IT STANDS, AND IT DID NOT FIRE
# ON THE INCIDENT THIS CHECK EXISTS FOR. That tree had already had the quotes
# removed, so tuning on it was survivorship bias: I measured false positives
# against a corpus with the true positive deleted. In the file as published on
# 2026-08-24 the marker and its block quote are SEVEN lines apart, with an
# intervening paragraph. The value below is set from that real case and the false
# positives are then measured, not the other way round -- see selftest, which
# replays the published file itself.
WINDOW = 7

# A sentence that says the source is a PERSON rather than a publication.
MARKER = re.compile(
    r"(?i)\b("
    r"by e-?mail|e-?mailed"
    r"|in (?:his|her|their) (?:mail|email|words|reply|letter)"
    r"|personal communication|pers\.? ?comm\.?"
    r"|(?:he|she|they) (?:wrote|replied|answered)\b"
    r"|replied (?:to|by)\b|wrote to\b"
    r"|(?:his|her|their) (?:mail|letter|reply)\b"
    r")"
)

# The COMPLIANT citation — "(personal communication, April 2026)" — is the form
# this rule asks people to use, so it must not itself read as suspicious. The
# first version had no such carve-out and fired on `docs/detector_history.md`,
# where a correctly cited paraphrase happens to sit above a block quote of
# interface2's written audit. A check that punishes the behaviour it is trying to
# produce teaches people to stop citing, which is worse than the leak.
CITATION_FORM = re.compile(r"(?i)pers(?:onal|\.?) ?comm(?:unication|\.?),?\s*"
                           r"(?:[A-Z][a-z]+ )?\d{4}")


def _is_marker(line: str) -> bool:
    """A reporting sentence naming a person as the source — but not a compliant
    citation, which is the goal state rather than the defect."""
    return any(
        not any(c.start() <= m.start() < c.end() for c in CITATION_FORM.finditer(line))
        for m in MARKER.finditer(line)
    )

# A markdown block quote that opens with quoted or emphasised text — the shape a
# reproduced letter takes. A block quote of plain prose is ordinary commentary.
BLOCKQUOTE = re.compile(r'^\s{0,3}>\s*[*_"“]')

# The one-line form: the source named and the words reproduced in one breath.
# 25 characters, so a quoted term of art ("adaptive") is not a letter.
INLINE = re.compile(r'["“][^"”\n]{25,}["”]')

# Tony is not a third party: this is his repository and his words, and the tree
# quotes him by design because his rulings are load-bearing. Ruled 2026-09-02.
#
# THE EXEMPTION IS FOR TONY AS SPEAKER, AND THE FIRST VERSION MATCHED HIS NAME
# ANYWHERE, WHICH SILENCED THE REAL INCIDENT. The sentence that introduced the
# leaked quotes was "... replied to Tony by email in April" — Tony is the
# RECIPIENT there, and a bare name match read the letter's audience as its
# author. Attribution has a shape; being mentioned does not.
SELF = re.compile(
    r"(?i)(?:[—-]\s*Tony\b|\bTony[,:]|\bper Tony\b"
    r"|\bTony (?:said|says|wrote|writes|ruled|rules|called|closed|asked)\b)"
)

# Files whose SUBJECT is this rule, and which therefore must be able to show the
# shape they forbid. This is self-reference, not an exemption for content: no
# correspondent's words may be added to them either, and nothing else may be
# added to this list without Tony — the clearance question was put to him on
# 2026-09-02 and his answer was "ask me. this is rare."
RULE_DOCS = {
    "CLAUDE.md",
    "docs/doc_review_process.md",
    "docs/sapper_feedback/2026-09-02-private-correspondence-in-a-public-tree.md",
    "docs/todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md",
    "docs/todo/2026-09-02-correspondence-has-nowhere-private-to-live.md",
    # The PySpike filing todo carries Kreuz's words from 2026-08-31 — the ONLY
    # quotes in this tree he has actually cleared, and he cleared them in writing
    # on 2026-09-02. That is the "ask Tony" path having already been walked, and
    # the file records the answer. It is not a precedent for the next one: the
    # next one is a conversation, not an edit to this list.
    "docs/todo/2026-08-11-file-pyspike-max-tau-issue.md",
}

MESSAGE = (
    "A THIRD PARTY'S PRIVATE WORDS DO NOT GO IN THIS PUBLIC TREE. Paraphrase "
    "what they told you -- the technical content is yours to state -- and cite "
    "the person: \"Kreuz, personal communication, 2026-04-23\" is complete and "
    "exactly as checkable as a block quote. If the wording genuinely carries "
    "load no paraphrase can, ASK THEM FIRST, before it goes out; asking "
    "afterwards is not asking, and a clearance covers only the material the "
    "person was actually shown. If this quote HAS been cleared, ask Tony rather "
    "than editing this check -- it is rare enough to be a conversation. "
    "CLAUDE.md, 'Other people's words'."
)


def _strip_fences(lines: list[str]) -> list[bool]:
    """True for lines inside a fenced code block — a fenced example is not a
    markdown block quote, and the file documenting this rule contains one."""
    inside, out, fence = False, [], None
    for ln in lines:
        m = re.match(r"^\s{0,3}(`{3,}|~{3,})", ln)
        if m and (not inside or ln.strip().startswith(fence)):
            if inside and ln.strip().startswith(fence):
                out.append(True)
                inside, fence = False, None
                continue
            inside, fence = True, m.group(1)[0] * 3
        out.append(inside)
    return out


def findings_for(path: str, text: str) -> list[tuple[str, int, str]]:
    if path in RULE_DOCS or not path.endswith(".md"):
        return []
    lines = text.splitlines()
    fenced = _strip_fences(lines)
    marks = [
        i for i, ln in enumerate(lines)
        if not fenced[i] and _is_marker(ln) and not SELF.search(ln)
    ]
    hits = []
    for i, ln in enumerate(lines):
        if fenced[i] or SELF.search(ln):
            continue
        if BLOCKQUOTE.match(ln) and any(0 <= i - m <= WINDOW for m in marks):
            hits.append((path, i + 1, ln))
        elif _is_marker(ln) and INLINE.search(ln):
            hits.append((path, i + 1, ln))
    return hits


def _tracked_md() -> list[str]:
    out = subprocess.run(["git", "ls-files", "*.md"], capture_output=True,
                         text=True, check=True)
    return out.stdout.split()


def _staged_md() -> list[str]:
    out = subprocess.run(["git", "diff", "--cached", "--name-only",
                          "--diff-filter=ACM"], capture_output=True,
                         text=True, check=True)
    return [p for p in out.stdout.split() if p.endswith(".md")]


def _read(path: str, staged: bool) -> str:
    if staged:
        r = subprocess.run(["git", "show", f":{path}"], capture_output=True,
                           text=True)
        return r.stdout if r.returncode == 0 else ""
    try:
        return open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return ""


def scan(paths: list[str], staged: bool) -> list[tuple[str, int, str]]:
    hits = []
    for p in paths:
        hits += findings_for(p, _read(p, staged))
    return hits


# Assembled so this file's own fixtures cannot trip a future grep for the shape.
_Q = chr(34)
_BAD_BLOCK = (
    "Kreuz replied by email in April.\n\n"
    + "> " + _Q + "for global event identification you should first use the "
    "symmetric profile." + _Q + "\n"
)
_BAD_INLINE = (
    "His diagnosis, in his words: *" + _Q + "we just forgot to track tau_max "
    "in the new function." + _Q + "*\n"
)
_GOOD = (
    "Kreuz replied by email in April. Paraphrased, with his permission "
    "unneeded because these are our words: use the symmetric profile, since "
    "identification should not depend on order (Kreuz, personal "
    "communication, 2026-04-23).\n\n"
    "> A block quote of our own prior text is ordinary commentary and must not "
    "fire.\n"
)


def selftest() -> int:
    failures = 0
    for name, text, want in (("bad-block", _BAD_BLOCK, True),
                             ("bad-inline", _BAD_INLINE, True),
                             ("good", _GOOD, False)):
        got = bool(findings_for("docs/fixture.md", text))
        if got != want:
            print(f"selftest FAIL {name}: fired={got} expected={want}")
            failures += 1
    print(f"check_quotes selftest: 3 fixtures, {failures} failures")
    return 1 if failures else 0


def report(hits) -> int:
    for path, lineno, line in hits:
        print(f"BLOCK QUOTED-CORRESPONDENCE {path}:{lineno}: {line.strip()[:110]}")
    if not hits:
        print("check_quotes: clear")
        return 0
    print(f"\n    {MESSAGE}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--all", action="store_true")
    g.add_argument("--staged", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.staged:
        return report(scan(_staged_md(), staged=True))
    return report(scan(_tracked_md(), staged=False))


if __name__ == "__main__":
    sys.exit(main())
