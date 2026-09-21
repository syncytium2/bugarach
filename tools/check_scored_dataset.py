#!/usr/bin/env python3
"""What was every result scored on — and is it the default dataset?

Tony, 2026-09-21: *"there should be a startup check that the default data set is what
everything was scored against. benchmarks derived from an older data set should be
flagged."* When this was written, 2 of the 18 JSON result files under ``docs/learned/``
named the export folder they were scored on. Two more named the closed ``.mat`` store — 85
recordings, one of them withdrawn by the lab — and one of those, ``generator_spec.json``,
is what parameterises the synthetic benchmark. The rest said nothing.

A result declares its data with ``dataset.stamp()`` under the key ``"dataset"``. Older
shapes are read too, so the existing record is classified rather than ignored:

    current     scored on the folder ``current_export.toml`` names as ``default``
    eval        scored on a declared ``eval`` corpus (Cossart) — another corpus on purpose
    older       scored on another export folder — the benchmark predates the default
    store       scored on a closed ``.mat`` store (the store is closed; CLAUDE.md)
    unstamped   says nothing about its data; cannot be checked

``--brief`` prints the one line the session briefing carries. The default exit is 0
whatever it finds — a startup check that fails takes the session with it; ``--strict``
exits 1 when anything is not ``current``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RESULTS = ROOT / "docs" / "learned"
NOT_RESULTS = ("*.spec.json",)          # figure specifications, not measurements


def _dataset():
    """``bugarach.dataset`` loaded by file, not through the package.

    The session briefing runs this under a 10-second hook budget, and ``import bugarach``
    pulls scipy in through ``bugarach.store`` — 0.7 s of a check that needs one
    stdlib-only module. Same file, same answers; only the package ``__init__`` is skipped.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_bugarach_dataset", ROOT / "src" / "bugarach" / "dataset.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod            # dataclasses resolves annotations through it
    spec.loader.exec_module(mod)
    return mod


def results(folder: Path = RESULTS) -> list[Path]:
    skip = {p for pat in NOT_RESULTS for p in folder.glob(pat)}
    return sorted(p for p in folder.glob("*.json") if p not in skip)


def scored_on(doc) -> tuple[str, str | None]:
    """(kind, name) — ``kind`` in dataset / folder / store / none."""
    if not isinstance(doc, dict):
        return "none", None
    ds = doc.get("dataset")
    if isinstance(ds, dict) and ds.get("name"):
        return "dataset", str(ds["name"])
    if isinstance(doc.get("folder"), str):
        return "folder", doc["folder"]
    for where in (doc, doc.get("provenance") or {}):
        if isinstance(where, dict) and isinstance(where.get("store"), str):
            return "store", where["store"]
    return "none", None


def classify(path: Path, default_name: str,
             eval_names: frozenset = frozenset()) -> tuple[str, str | None]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "unstamped", None
    kind, name = scored_on(doc)
    if kind == "none":
        return "unstamped", None
    if name == default_name:
        return "current", name
    if name in eval_names:              # another corpus on purpose (Cossart), not stale
        return "eval", name
    return ("store" if kind == "store" else "older"), name


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--brief", action="store_true", help="one line, for the briefing")
    ap.add_argument("--strict", action="store_true", help="exit 1 unless all current")
    a = ap.parse_args(argv)

    dataset = _dataset()
    try:
        default_name = dataset.current_name("default")
    except dataset.DataError as exc:
        print(f"!! scored-on check: {exc}")
        return 1 if a.strict else 0

    evals = frozenset(str(t["name"]) for t in dataset.declared_exports().values()
                      if t.get("use") == "eval")
    rows = [(p, *classify(p, default_name, evals)) for p in results()]
    by = {k: [r for r in rows if r[1] == k]
          for k in ("current", "eval", "older", "store", "unstamped")}
    n = len(rows)
    ok = len(by["current"]) + len(by["eval"])

    if a.brief:
        bad = n - ok
        # One short line: the briefing runs within a byte budget measured against what
        # the harness has refused (tests/test_session_briefing.py), and this line was
        # what pushed it over on its first draft. The full list is one command away.
        # A fragment the briefing appends to its data line, not a line of its own.
        # Every byte here is paid for in the briefing's budget; docs/INDEX.md names the tool.
        print(f"{len(by['current'])}/{n} results on it")    # eval corpora are not "on it"
        return 1 if (a.strict and bad) else 0

    print(f"default dataset: {default_name}")
    labels = {"current": "on the default", "eval": "on a declared eval corpus (by design)",
              "older": "on an OLDER export", "store": "on the CLOSED .mat store",
              "unstamped": "UNSTAMPED - cannot be checked"}
    for k in ("older", "store", "unstamped", "eval", "current"):
        if not by[k]:
            continue
        print(f"\n{labels[k]} ({len(by[k])} files):")
        for p, _, name in by[k]:
            print(f"  {p.relative_to(ROOT).as_posix()}" + (f"  <- {name}" if name else ""))
    return 1 if (a.strict and ok < n) else 0


if __name__ == "__main__":
    raise SystemExit(main())
