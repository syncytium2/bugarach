"""Every .py in the tree parses at the OLDEST Python this project supports.

WHY THIS EXISTS. On 2026-09-04 `tools/make_group_raster_summary.py` shipped an
f-string with a newline inside the replacement field:

    f"{chip(MARKED_INK, 'event on a confirmed step '
                        '(field-step artifact)')}"

That is PEP 701, which landed in **3.12**. On 3.11 the same source is
`SyntaxError: unterminated string literal` — raised at IMPORT, so the module
never loads and every test in the file errors at collection rather than failing
with something that names the cause. The local interpreter is 3.14 and accepted
it; `requires-python` says `>=3.11`; the only thing that disagreed was CI's 3.11
leg, two minutes and a push later.

**The gap is structural, not a slip.** A developer runs one interpreter and the
project promises three, so the floor is tested exactly once per push and nowhere
else.

TWO CHECKS, BECAUSE ONE OF THEM CANNOT SEE THE DEFECT THAT PROMPTED IT
----------------------------------------------------------------------
The obvious implementation is `ast.parse(src, feature_version=floor)`, and the
first draft of this file was exactly that. **It passes the bad f-string above.**
Measured here rather than assumed: `feature_version` constrains the *grammar*,
and f-strings are handled by the **tokenizer**, which it does not downgrade. It
correctly rejects `match`, `except*`, `type X = int` and `def f[T]()`, and is
blind to every PEP 701 construct.

Shipping that alone would have been a check that reports success while doing
nothing — the same "can the alarm ring?" family this project keeps finding, and
it would have been introduced *by the fix for the incident it was named after*.
So there is a second, narrower check that reads the token stream and finds the
two PEP 701 forms directly.

WHAT THIS STILL DOES NOT CATCH, said plainly so nobody reads it as more:
`feature_version` is grammar only and the token scan is two specific forms.
A 3.12+ standard-library call, a new method on a builtin, or a changed default
still imports fine here and still breaks on 3.11. **This is a syntax floor, not
a compatibility suite.** It catches the class that actually bit.
"""

from __future__ import annotations

import ast
import io
import re
import sys
import token as tokmod
import tokenize
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

#: Directories whose contents this project is responsible for. `.venv`, build
#: artefacts and anything vendored from elsewhere are deliberately absent — a
#: dependency's syntax is not ours to hold to our own floor.
SOURCE_DIRS = ("src", "tools", "tests")


def declared_floor() -> tuple[int, int]:
    """The floor from `pyproject.toml`, so this cannot drift from the promise.

    Read rather than hardcoded: a hardcoded (3, 11) would keep passing on the day
    someone raises `requires-python`, and would then be testing a version the
    project no longer claims to support.
    """
    text = (ROOT / "pyproject.toml").read_text()
    m = re.search(r'requires-python\s*=\s*"[^"]*?(\d+)\.(\d+)', text)
    assert m, "pyproject.toml declares no requires-python floor"
    return int(m.group(1)), int(m.group(2))


def python_files() -> list[Path]:
    out: list[Path] = []
    for d in SOURCE_DIRS:
        out += sorted((ROOT / d).rglob("*.py"))
    assert out, "found no Python files — the globs are wrong, not the tree"
    return out


def pep701_offences(src: str) -> list[tuple[int, str]]:
    """Find f-strings that only tokenize on 3.12+.

    Two forms, both `SyntaxError` on 3.11:

    * a replacement field spanning a **newline**, in a non-triple-quoted
      f-string — the one that shipped;
    * a string inside a replacement field reusing the **enclosing quote
      character**, e.g. ``f"{d["k"]}"``.

    Needs 3.12+ to run, because it reads the FSTRING_* tokens PEP 701 introduced.
    On an older interpreter there is nothing to do: that interpreter *is* the
    floor, and `ast.parse` there rejects both forms itself.
    """
    if sys.version_info < (3, 12):
        return []
    starts: list[tuple[str, int]] = []   # (quote characters, start line)
    out: list[tuple[int, str]] = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == getattr(tokmod, "FSTRING_START", -1):
            q = tok.string[tok.string.index(tok.string[-1]):]
            starts.append((q, tok.start[0]))
        elif tok.type == getattr(tokmod, "FSTRING_END", -1):
            if not starts:
                continue
            q, line = starts.pop()
            if len(q) < 3 and tok.end[0] != line:
                out.append((line, "a replacement field spans a newline inside a "
                                  "single-quoted f-string (PEP 701, 3.12+)"))
        elif tok.type == tokmod.STRING and starts:
            q, line = starts[-1]
            if len(q) < 3 and tok.string.lstrip("rbfuRBFU").startswith(q):
                out.append((tok.start[0],
                            f"a string inside a replacement field reuses the "
                            f"enclosing {q} quote (PEP 701, 3.12+)"))
    return out


def test_the_floor_is_declared_and_this_interpreter_is_not_below_it():
    floor = declared_floor()
    assert floor >= (3, 8), f"ast.feature_version cannot express {floor}"
    assert sys.version_info[:2] >= floor


def test_the_pep701_scan_can_actually_fire():
    """The check that would have caught it, proving it would have.

    `ast.parse(feature_version=...)` accepts BOTH of these, which is the whole
    reason this second scan exists — asserted here so that if a future Python
    makes `feature_version` cover the tokenizer, this test says so rather than
    quietly leaving two checks where one would do.
    """
    shipped = 'x = f"{chip(A, \'one \'\n               \'two\')}"\n'
    nested = 'x = f"{d["k"]}"\n'
    if sys.version_info >= (3, 12):
        assert pep701_offences(shipped), "the scan missed the form that shipped"
        assert pep701_offences(nested), "the scan missed the nested-quote form"
    # and the blindness it compensates for is real, not assumed
    ast.parse(shipped, feature_version=(3, 11))
    assert pep701_offences("x = f'{a}{b}'\ny = f'''{c\n}'''\n") == []


@pytest.mark.parametrize("path", python_files(), ids=lambda p: str(p.relative_to(ROOT)))
def test_parses_at_the_declared_floor(path: Path):
    floor = declared_floor()
    rel = path.relative_to(ROOT)
    src = path.read_text(encoding="utf-8")

    for line, why in pep701_offences(src):
        pytest.fail(
            f"{rel}:{line} does not parse on Python {floor[0]}.{floor[1]}: {why}.\n"
            f"Hoist the expression into a named local above the f-string.")

    try:
        ast.parse(src, filename=str(path), feature_version=floor)
    except SyntaxError as e:  # pragma: no cover - the message IS the test output
        pytest.fail(
            f"{rel}:{e.lineno} does not parse on Python {floor[0]}.{floor[1]}, "
            f"which pyproject.toml says this project supports:\n"
            f"    {e.msg}\n"
            f"    {(e.text or '').strip()}\n"
            f"This interpreter is {sys.version_info.major}.{sys.version_info.minor} "
            f"and accepts it, so only CI's oldest leg would have caught it.")
