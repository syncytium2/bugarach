"""An architecture is a file in a folder, and dropping one in is the whole of adding it.

Tony, 2026-08-29: *"we need the dl networks as objects too."*

The registry was always right — ``@register`` into ``ARCHITECTURES``, read by the
bake-off, the lab server's ``/api/capabilities`` and the browser's model picker.
What was wrong was the layout: six architectures in one 467-line module, so
"adding a model" meant editing a file that five other things also live in.

These tests pin the property that makes the folder worth having: **the registry
is whatever the folder contains, and no list of names exists anywhere to fall
behind.**
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parent.parent / "src" / "bugarach" / "learn" / "nets"


def test_every_architecture_has_its_own_file():
    from bugarach.learn.nets import ARCHITECTURES

    files = {p.stem for p in PKG.glob("*.py") if p.stem != "__init__"}
    assert set(ARCHITECTURES) == files, (
        f"registry {sorted(ARCHITECTURES)} does not match the folder "
        f"{sorted(files)} — one file is one architecture, so a name in one and "
        f"not the other means either a file that registers nothing or a "
        f"registration hiding in a module named for something else")


def test_the_registry_holds_no_hand_written_list():
    """The failure this layout exists to prevent, stated as a check.

    A list of names in ``__init__`` would be a second place to edit, and the
    first thing to go stale when somebody adds a file.
    """
    src = (PKG / "__init__.py").read_text(encoding="utf-8")
    assert "iter_modules" in src, "the folder is no longer auto-imported"
    for name in ("tube", "tiny", "trace"):
        assert f'"{name}"' not in src, (
            f"'{name}' is named in nets/__init__.py — the folder is the list")


def test_a_new_file_registers_with_nothing_else_edited(tmp_path):
    """Drop a module in, reload the package, and it is registered.

    Written and removed inside the test rather than committed as a fixture: a
    permanent seventh architecture would show up in every sweep, every
    capabilities response and every scoreboard, which is a large price for a
    test to charge.
    """
    new = PKG / "zz_probe.py"
    new.write_text(
        '"""A throwaway architecture, written by a test and removed by it."""\n'
        "from bugarach.learn.nets import register\n\n\n"
        '@register("zz_probe", note="written by test_architectures_are_files")\n'
        "def build_zz_probe(**cfg):\n"
        "    raise NotImplementedError('never built — registration is the point')\n",
        encoding="utf-8")
    try:
        for mod in [m for m in sys.modules if m.startswith("bugarach.learn.nets")]:
            del sys.modules[mod]
        nets = importlib.import_module("bugarach.learn.nets")
        assert "zz_probe" in nets.ARCHITECTURES, (
            "a file in the folder did not register — the autoload is broken, and "
            "with it the only claim this layout makes")
    finally:
        new.unlink()
        for mod in [m for m in sys.modules if m.startswith("bugarach.learn.nets")]:
            del sys.modules[mod]
        importlib.import_module("bugarach.learn.nets")


def test_a_broken_architecture_is_loud(tmp_path):
    """An import error must NOT be swallowed into a quietly smaller registry.

    A registry that skips what it cannot load reports a smaller model set as if
    that were the truth — the same "a finding and a bug must not look alike"
    rule the run.json roster is built on.
    """
    bad = PKG / "zz_broken.py"
    bad.write_text("raise RuntimeError('deliberately broken')\n", encoding="utf-8")
    try:
        for mod in [m for m in sys.modules if m.startswith("bugarach.learn.nets")]:
            del sys.modules[mod]
        with pytest.raises(RuntimeError):
            importlib.import_module("bugarach.learn.nets")
    finally:
        bad.unlink()
        for mod in [m for m in sys.modules if m.startswith("bugarach.learn.nets")]:
            del sys.modules[mod]
        importlib.import_module("bugarach.learn.nets")
