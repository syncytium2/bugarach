"""Adding a detector or an architecture must not silently miss a consumer.

Tony, 2026-08-29: *"the structure was always intended to be flexible. detectors
and dl models added removed at will."* It is — in the library. ``DETECTORS`` is
``tuple(OPERATING_POINTS)`` and an architecture is one ``@register`` line. But two
consumers keep their own copies of those lists, and **nothing compared them**, so
"add a detector" was a change with a silent second half:

- ``docs/site/raster_viewer.html``'s ``const DETECTORS`` — the browser cannot
  import Python, has no build step and makes no network request, so this copy is
  structural and is not going away. What was missing is anything that *notices*
  when it falls behind.
- ``tools/fair_bakeoff.py``'s ``LEARNED`` — a hand-listed tuple beside a real
  registry. Here the duplication is not structural: it is the run's *selection*,
  which is a legitimate thing to state, but it must be visible as a selection
  rather than mistakable for the full set.

These tests do not forbid the copies. They make a divergence fail out loud, which
is what turns a duplicated list from a trap into a decision. When one fires, the
answer is either to update the copy or to record why the difference is deliberate
— never to delete the test.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "docs" / "site" / "raster_viewer.html"


def _webapp_detector_keys() -> set[str]:
    """Every detector the viewer page offers, however it got there.

    **Two sources, because the page is mid-migration** (ADR-0005). Detectors that
    have been converted to object files live in ``docs/site/detectors/*.js`` and
    arrive as ``registerDetector({key: "rate", ...})``; the rest are still
    entries in the ``const DETECTORS = { ... }`` literal. Both are read, so this
    check keeps working across the conversion instead of going quiet in the
    middle of it — which is when a drift test is least affordable to lose.

    The literal is parsed by brace-matching from the declaration rather than by a
    regex over the whole file: the page is 10,000 lines, the word appears in
    prose and comments and inside other objects, and a looser match would drift
    between finding too much and too little without saying which.
    """
    text = PAGE.read_text(encoding="utf-8")
    registered = set(re.findall(r'registerDetector\(\s*\{\s*key:\s*"([a-z_]+)"', text))
    start = text.index("const DETECTORS = {")
    i = text.index("{", start)
    depth, end = 0, None
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                end = j
                break
    assert end is not None, "const DETECTORS is not brace-balanced"
    body = text[i + 1:end]
    # Top-level keys only — nested config objects have keys too.
    keys, depth = [], 0
    for line in body.splitlines():
        stripped = line.strip()
        if depth == 0:
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:", stripped)
            if m:
                keys.append(m.group(1))
        depth += line.count("{") - line.count("}")
    return set(keys) | registered


def test_the_browser_offers_every_detector_the_library_has():
    from bugarach.bench import OPERATING_POINTS

    page, lib = _webapp_detector_keys(), set(OPERATING_POINTS)
    missing, extra = lib - page, page - lib
    assert not missing, (
        f"the library has {sorted(missing)} and the viewer page does not offer them. "
        "Add them to `const DETECTORS` in docs/site/raster_viewer.html, or if the "
        "omission is deliberate, say so here and pin it.")
    assert not extra, (
        f"the viewer page offers {sorted(extra)}, which the library does not define. "
        "A detector a reader can run but nothing else can reproduce is worse than "
        "one that is missing.")


def test_the_bakeoff_selection_is_a_subset_of_what_is_registered():
    """``LEARNED`` may be narrower than the registry; it may never name a ghost.

    A run choosing not to sweep an architecture is a real decision. Naming one
    that no longer exists is a stale list, and it fails here rather than at the
    ``KeyError`` three minutes into a bake-off.
    """
    import bugarach.learn.nets as nets

    src = (ROOT / "tools" / "fair_bakeoff.py").read_text(encoding="utf-8")
    listed = set(re.findall(r'"([a-z_]+)"',
                            re.search(r"LEARNED = \(([^)]*)\)", src).group(1)))
    ghosts = listed - set(nets.ARCHITECTURES)
    assert not ghosts, (
        f"tools/fair_bakeoff.py sweeps {sorted(ghosts)}, which nothing registers")


def test_a_new_architecture_reaches_the_bakeoffs_provenance_without_editing_it():
    """The registry is read, not retyped — an added ``@register`` shows up on its own.

    This is the half that makes "added at will" true of the *record* as well as
    of the code: `registered` comes from the registry, so a new architecture
    appears in the next run's provenance whether or not that run swept it.
    """
    src = (ROOT / "tools" / "fair_bakeoff.py").read_text(encoding="utf-8")
    assert "sorted(ARCHITECTURES)" in src, (
        "fair_bakeoff's provenance stopped reading the registry; a hand-listed "
        "copy there would go stale the first time somebody adds an architecture")
    assert "registered_but_not_run" in src, (
        "the gap between what exists and what ran is the interesting half — "
        "without it, skipped and absent look identical")
