"""The darkroom resolver must never guess a path.

It writes into a Dropbox mount shared by every machine and several other
projects, so a wrong guess lands files in someone else's folder instead of
failing locally. Unset => None => caller skips the export.
"""

from pathlib import Path

from bugarach.paths import ENV_VAR, darkroom


def test_unset_returns_none(monkeypatch):
    monkeypatch.delenv(ENV_VAR, raising=False)
    assert darkroom() is None
    assert darkroom("parity", "x.png") is None


def test_empty_or_whitespace_is_treated_as_unset(monkeypatch):
    for value in ("", "   "):
        monkeypatch.setenv(ENV_VAR, value)
        assert darkroom() is None, f"{value!r} must not resolve to a path"


def test_returns_root_and_joins_parts(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV_VAR, str(tmp_path))
    assert darkroom() == tmp_path
    assert darkroom("parity", "summary.png") == tmp_path / "parity" / "summary.png"


def test_does_not_create_by_default(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV_VAR, str(tmp_path / "nope"))
    p = darkroom("sub")
    assert p == tmp_path / "nope" / "sub"
    assert not p.exists(), "asking where output would go must not touch the disk"


def test_create_makes_dir_for_a_directory_path(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV_VAR, str(tmp_path))
    p = darkroom("figs", create=True)
    assert p.is_dir()


def test_create_makes_the_parent_for_a_file_path(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV_VAR, str(tmp_path))
    p = darkroom("figs", "roc.png", create=True)
    assert p.parent.is_dir()
    assert not p.exists(), "create must not create the file itself"


def test_expands_user(monkeypatch):
    monkeypatch.setenv(ENV_VAR, "~/darkroom/bugarach")
    p = darkroom()
    assert p is not None and "~" not in str(p)
    assert p == Path.home() / "darkroom" / "bugarach"
