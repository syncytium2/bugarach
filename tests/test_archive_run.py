"""Finished runs reach Dropbox by themselves and the repo through a session (tools/archive_run.py).

Tony, 2026-09-21, after finding the weekend's trained models on one disk: *"ensure that future
runs go straight to repo and dropbox."*
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ar = _load("archive_run")


def _run(tmp_path, finished=True):
    run = tmp_path / "runs" / "r1"
    (run / "fits" / "sub").mkdir(parents=True)
    (run / "scores").mkdir()
    (run / "chosen" / "gated").mkdir(parents=True)
    (run / "fits" / "sub" / "a.json").write_text('{"w": [1, 2]}')
    (run / "fits" / "b.json").write_text("{}")
    (run / "scores" / "s.npz").write_bytes(b"\x01" * 128)
    (run / "chosen" / "gated" / "seed0.json").write_text('{"w": 3}')
    (run / "meta.json").write_text("{}")
    if finished:
        (run / "results.json").write_text('{"done": true}')
    return run


def test_the_selftest_passes():
    out = subprocess.run([sys.executable, str(ROOT / "tools" / "archive_run.py"), "--selftest"],
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stdout + out.stderr


def test_dropbox_gets_everything_with_the_bulk_packed(tmp_path):
    run = _run(tmp_path)
    entry = ar.to_darkroom(run, "2026-09-21-r1", root=tmp_path / "dark")
    dest = tmp_path / "dark" / "2026-09-21-r1"
    assert (dest / "chosen" / "gated" / "seed0.json").read_text() == '{"w": 3}'
    assert (dest / "fits.tar.gz").is_file() and (dest / "scores.tar.gz").is_file()
    assert not (dest / "fits").exists(), "bulk goes as an archive, not a second tree"
    assert entry["packed"] == {"fits": 2, "scores": 1}
    assert json.loads((run / ar.MARKER).read_text())["darkroom"]["path"] == str(dest)


def test_the_repo_gets_everything_but_the_bulk(tmp_path):
    run = _run(tmp_path)
    entry = ar.to_repo(run, "r1", dest=tmp_path / "repo" / "r1")
    assert (tmp_path / "repo" / "r1" / "chosen" / "gated" / "seed0.json").is_file()
    assert (tmp_path / "repo" / "r1" / "results.json").is_file()
    assert not (tmp_path / "repo" / "r1" / "fits").exists()
    assert not (tmp_path / "repo" / "r1" / ar.MARKER).exists(), "the marker stays with the run"
    assert entry["left_out"] == ["fits", "scores"]


def test_a_finished_run_is_pending_until_both_halves_are_done(tmp_path):
    run = _run(tmp_path)
    _run(tmp_path / "other", finished=False)
    assert ar.pending(tmp_path / "runs") == [(run, ["darkroom", "repo"])]
    ar.to_darkroom(run, "r1", root=tmp_path / "dark")
    assert ar.pending(tmp_path / "runs") == [(run, ["repo"])]
    ar.to_repo(run, "r1", dest=tmp_path / "repo" / "r1")
    assert ar.pending(tmp_path / "runs") == []


def test_an_unfinished_run_is_not_archived_from_the_command_line(tmp_path):
    run = _run(tmp_path, finished=False)
    assert ar.main([str(run), "--name", "r1"]) == 1


def test_a_name_that_climbs_is_refused(tmp_path):
    run = _run(tmp_path)
    for bad in ("../x", "a/b", "C:\\x"):
        with pytest.raises(ValueError):
            ar.to_darkroom(run, bad, root=tmp_path / "dark")


def test_the_mirror_archives_a_finished_run_once(tmp_path, monkeypatch):
    """The scheduled mirror is the unattended hook: it archives when results.json appears,
    and not again on the next five-minute tick."""
    mirror = _load("mirror_run_status")
    run = _run(tmp_path, finished=False)
    calls = []
    real = ar.to_darkroom

    def fake(run_dir, name, **kw):
        calls.append(name)
        return real(run_dir, name, root=tmp_path / "dark")

    monkeypatch.setattr(ar, "to_darkroom", fake)
    mirror._archive_if_finished(run, "r1", ar=ar)
    assert calls == [], "not finished: nothing archived"
    (run / "results.json").write_text("{}")
    mirror._archive_if_finished(run, "r1", ar=ar)
    mirror._archive_if_finished(run, "r1", ar=ar)
    assert calls == ["r1"], calls
