"""The darkroom resolver may find a path; it must never invent one.

It writes into a Dropbox mount shared by every machine and several other
projects, so a wrong path lands files in someone else's folder instead of
failing locally. Two routes are allowed: an explicit ``BUGARACH_DARKROOM``, and
Dropbox's own ``info.json`` — and the second counts as finding rather than
guessing only because it accepts a location solely when the directory is already
there, and declines when several accounts have one. Nothing found => None =>
caller skips the export.

Discovery is pinned here by replacing ``_info_json_candidates``, so these tests
say the same thing on a laptop with the darkroom mounted and on a CI runner
without it.
"""

import json
from pathlib import Path

import pytest

from bugarach.paths import (
    DARKROOM_SUBPATH,
    ENV_VAR,
    _as_local_path,
    darkroom,
    discover_darkroom,
    dropbox_roots,
    resolve_root,
)


@pytest.fixture
def no_dropbox(monkeypatch):
    """A machine with no Dropbox at all."""
    monkeypatch.delenv(ENV_VAR, raising=False)
    monkeypatch.setattr("bugarach.paths._info_json_candidates", lambda: [])


def write_info(tmp_path: Path, name: str, accounts: dict) -> Path:
    """Write one ``info.json`` shaped like the real client's."""
    info = tmp_path / name / "info.json"
    info.parent.mkdir(parents=True, exist_ok=True)
    info.write_text(json.dumps(accounts))
    return info


def account(root: Path, *, with_darkroom: bool) -> dict:
    if with_darkroom:
        root.joinpath(*DARKROOM_SUBPATH).mkdir(parents=True, exist_ok=True)
    else:
        root.mkdir(parents=True, exist_ok=True)
    return {"path": str(root), "is_team": True}


# --- nothing to find ---------------------------------------------------------


def test_unset_and_undiscoverable_returns_none(no_dropbox):
    assert darkroom() is None
    assert darkroom("parity", "x.png") is None
    assert resolve_root() == (None, "none")


def test_empty_or_whitespace_is_treated_as_unset(no_dropbox, monkeypatch):
    for value in ("", "   "):
        monkeypatch.setenv(ENV_VAR, value)
        assert darkroom() is None, f"{value!r} must not resolve to a path"


# --- the explicit route ------------------------------------------------------


def test_returns_root_and_joins_parts(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV_VAR, str(tmp_path))
    assert darkroom() == tmp_path
    assert darkroom("parity", "summary.png") == tmp_path / "parity" / "summary.png"
    assert resolve_root() == (tmp_path, "env")


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


def test_env_wins_over_a_discoverable_dropbox(tmp_path, monkeypatch):
    """An explicit answer is not second-guessed, even by a real mount."""
    mount = tmp_path / "Dropbox" / "Someone"
    info = write_info(tmp_path, "dot", {"business": account(mount, with_darkroom=True)})
    monkeypatch.setattr("bugarach.paths._info_json_candidates", lambda: [info])
    monkeypatch.setenv(ENV_VAR, str(tmp_path / "elsewhere"))
    assert darkroom() == tmp_path / "elsewhere"
    assert resolve_root()[1] == "env"


# --- the discovery route -----------------------------------------------------


def test_discovers_the_one_account_that_has_a_darkroom(tmp_path, monkeypatch):
    mount = tmp_path / "Dropbox-UM" / "Someone"
    info = write_info(tmp_path, "dot", {"business": account(mount, with_darkroom=True)})
    monkeypatch.setattr("bugarach.paths._info_json_candidates", lambda: [info])
    monkeypatch.delenv(ENV_VAR, raising=False)

    expected = mount.joinpath(*DARKROOM_SUBPATH)
    assert discover_darkroom() == expected
    assert darkroom() == expected
    assert resolve_root() == (expected, "dropbox")
    assert darkroom("figs", "roc.png") == expected / "figs" / "roc.png"


def test_ignores_an_account_with_no_darkroom_in_it(tmp_path, monkeypatch):
    """Dropbox mounted is not the darkroom present — this is the guess to refuse."""
    mount = tmp_path / "Dropbox-personal" / "Someone"
    info = write_info(tmp_path, "dot", {"personal": account(mount, with_darkroom=False)})
    monkeypatch.setattr("bugarach.paths._info_json_candidates", lambda: [info])
    monkeypatch.delenv(ENV_VAR, raising=False)

    assert dropbox_roots() == [mount], "the account is still reported"
    assert discover_darkroom() is None
    assert darkroom() is None


def test_declines_when_two_accounts_both_have_one(tmp_path, monkeypatch):
    """Ambiguity is not settled by ordering: nobody chose either of these."""
    work = tmp_path / "Dropbox-UM" / "Someone"
    home = tmp_path / "Dropbox-personal" / "Someone"
    info = write_info(
        tmp_path,
        "dot",
        {
            "business": account(work, with_darkroom=True),
            "personal": account(home, with_darkroom=True),
        },
    )
    monkeypatch.setattr("bugarach.paths._info_json_candidates", lambda: [info])
    monkeypatch.delenv(ENV_VAR, raising=False)

    assert discover_darkroom() is None
    assert resolve_root() == (None, "none")


def test_the_same_mount_seen_twice_is_not_an_ambiguity(tmp_path, monkeypatch):
    """Windows lists both AppData roots, and WSL globs every drive."""
    mount = tmp_path / "Dropbox-UM" / "Someone"
    entry = {"business": account(mount, with_darkroom=True)}
    first = write_info(tmp_path, "roaming", entry)
    second = write_info(tmp_path, "local", entry)
    monkeypatch.setattr("bugarach.paths._info_json_candidates", lambda: [first, second])
    monkeypatch.delenv(ENV_VAR, raising=False)

    assert discover_darkroom() == mount.joinpath(*DARKROOM_SUBPATH)


def test_a_broken_dropbox_install_finds_nothing_and_does_not_raise(
    tmp_path, monkeypatch
):
    """A figure script must not die because info.json is half-written."""
    junk = tmp_path / "junk" / "info.json"
    junk.parent.mkdir(parents=True)
    junk.write_text("{not json at all")
    listy = write_info(tmp_path, "listy", {})
    listy.write_text("[1, 2, 3]")
    absent = tmp_path / "gone" / "info.json"
    monkeypatch.setattr(
        "bugarach.paths._info_json_candidates", lambda: [junk, listy, absent]
    )
    monkeypatch.delenv(ENV_VAR, raising=False)

    assert dropbox_roots() == []
    assert darkroom() is None


def test_discovery_creates_nothing(tmp_path, monkeypatch):
    mount = tmp_path / "Dropbox-UM" / "Someone"
    info = write_info(tmp_path, "dot", {"personal": account(mount, with_darkroom=False)})
    monkeypatch.setattr("bugarach.paths._info_json_candidates", lambda: [info])
    monkeypatch.delenv(ENV_VAR, raising=False)

    darkroom("figs", create=True)
    assert not mount.joinpath(*DARKROOM_SUBPATH).exists(), (
        "create must never conjure the darkroom itself — that is how an empty "
        "folder gets synced to every other machine"
    )


# --- reading the client's own record ----------------------------------------


def test_windows_path_is_translated_for_wsl():
    r"""Read from Linux, `C:\Users\...` names nothing; /mnt/c does."""
    assert _as_local_path(r"C:\Users\rd\Dropbox-UM\Someone") == Path(
        "/mnt/c/Users/rd/Dropbox-UM/Someone"
    )
    assert _as_local_path("D:/data/darkroom") == Path("/mnt/d/data/darkroom")


def test_posix_path_is_left_alone():
    assert _as_local_path("/Users/rd/Dropbox-UM/Someone") == Path(
        "/Users/rd/Dropbox-UM/Someone"
    )


def test_a_missing_path_field_is_not_an_account():
    assert _as_local_path("") is None
    assert _as_local_path("   ") is None
