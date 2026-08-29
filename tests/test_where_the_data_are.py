"""A session must be able to find the data without reading prose.

On 2026-08-27 one could not, and began re-deriving the recordings from a `.mat`
event store. Everything that forbids that was already written down and correct.
Tony's instruction was that another line of prose is not a fix:

    "claude.md is unreliable. help me fix this permanently."

Two mechanisms replaced the prose, and this file holds both to account.

**`current_export.toml` + `dataset.current()`** answer *which* folder. That question
had no single answer before: README, `tests/test_io.py`, `docs/export_for_producers.md`
and eight board blocks each named an export folder, and they did not agree about which
was current or even use the same form of the name.

**`.claude/hooks/the-folder-is-the-input.sh`** catches a session reaching for a store
and hands it the answer. Sapper SAP007 cannot do this: it greps what a commit ADDS, and
interactive analysis never commits. The gate sees the attempt instead of the wreckage.

Following `test_hooks_installed.py`, the gate is checked for being **wired**, not only
for working — an unwired gate reads exactly like a passed one.
"""

import json
import re
import os
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

from bugarach import dataset

REPO = Path(__file__).parent.parent
POINTER = REPO / "current_export.toml"
GATE = REPO / ".claude" / "hooks" / "the-folder-is-the-input.sh"
SETTINGS = REPO / ".claude" / "settings.json"


# --------------------------------------------------------------- the pointer

def test_the_pointer_exists_and_parses():
    assert POINTER.is_file(), f"{POINTER.name} is the only declaration of which " \
                              f"export folder is the input; it must exist"
    with POINTER.open("rb") as fh:
        tomllib.load(fh)


def test_it_declares_the_default_and_the_pensub_pair():
    roles = dataset.declared_exports()
    assert "default" in roles, f"declared: {sorted(roles)}"
    assert "pensub" in roles, f"declared: {sorted(roles)}"
    for role, table in roles.items():
        assert table["name"], f"{role} has no name"
        assert table["name"].strip() == table["name"], f"{role} name has whitespace"


def test_the_export_directories_are_searched_before_the_bare_root():
    """A NAME THAT RESOLVES TO THE WRONG DIRECTORY PASSES EVERY OTHER CHECK.

    `dandi_000219` exists twice under the data root: the raw DANDI download at
    `<root>/dandi_000219`, and the conforming 59-recording export at
    `<root>/exports/external/dandi_000219`. The raw one holds a single CSV, so
    `kind()` classifies it as an export folder and `require(want="export_folder")`
    accepts it — a caller would analyse **1 recording instead of 59** and nothing
    downstream would complain, because every shape check passes. Only the search
    ORDER prevents it.

    Asserted against the order itself rather than a resolved path, so it runs on CI
    where neither directory exists.
    """
    subs = next((c for c in dataset.resolve.__code__.co_consts
                 if isinstance(c, tuple) and "exports" in c), None)
    assert subs is not None, "resolve() no longer carries a search-order tuple"
    assert "exports/external" in subs, (
        "resolve() stopped searching exports/external, where other labs' imported "
        "folders live")
    assert subs.index("exports/external") < subs.index(""), (
        "the bare data root is searched before exports/external, so a name present "
        "in both resolves to the raw download instead of the export folder")


def test_the_name_is_available_without_the_data_being_mounted():
    """`current_name()` must not touch the filesystem.

    CI has no Dropbox and no export folder. An error message, a log line, or the
    PreToolUse gate still has to be able to say WHICH folder is meant there, or the
    answer is only available to the machines that did not need it.
    """
    name = dataset.current_name()
    assert name and not Path(name).is_absolute()
    assert dataset.current_name("pensub") != name


def test_an_unknown_role_names_the_ones_that_exist():
    with pytest.raises(dataset.DataError) as exc:
        dataset.current_name("no-such-role")
    assert "default" in str(exc.value) and "pensub" in str(exc.value)


def test_it_carries_no_absolute_path():
    """Names only. A path here would carry a person's name into a public repo, and
    would be wrong on every other machine — `resolve()` is what knows this one."""
    text = POINTER.read_text()
    for line in text.splitlines():
        if line.lstrip().startswith("name"):
            assert "/" not in line and "\\" not in line, line


def test_the_pointer_is_the_only_declaration_in_code():
    """No source or test file may hardcode an export folder name.

    This is the drift the pointer exists to stop: `tests/test_io.py` named one folder
    while the README named another and the board named a third, so 'which is current'
    had four answers and no authority. Docs and the session board legitimately narrate
    history and are not scanned; code that RESOLVES data is.
    """
    # A DATED name is an export folder. `_revised_2v` alone is not: it also matches
    # the `.mat` STORE names (`event_store_onset_revised_2v`), which several tools
    # legitimately name, and matching those made this test flag the migration debt
    # in `fit_background_shape.py` as a competing declaration. It is not one — a
    # store is not an export folder, which is the distinction the whole gate rests on.
    folder_name = re.compile(r"20\d\d-\d\d-\d\d_[A-Za-z0-9_]+")
    offenders = []
    for base in ("src", "tools"):
        for p in sorted((REPO / base).rglob("*.py")):
            for n, line in enumerate(p.read_text().splitlines(), 1):
                if folder_name.search(line) and not line.lstrip().startswith(("#", "``", '"', "*")):
                    offenders.append(f"{p.relative_to(REPO)}:{n}: {line.strip()}")
    # In tests the rule is narrower, and precisely so: a test may `resolve()` a
    # SYNTHETIC name it built in a tmp_path — `test_dataset.py` does exactly that to
    # exercise the resolver, and flagging it was this test being blunt rather than
    # right. What must not happen is resolving one of the names the pointer DECLARES,
    # because that is the second declaration, and the two then drift apart silently.
    declared = {t["name"] for t in dataset.declared_exports().values()}
    for p in sorted((REPO / "tests").rglob("*.py")):
        if p.name == Path(__file__).name:
            continue
        for n, line in enumerate(p.read_text().splitlines(), 1):
            if "resolve(" in line and any(d in line for d in declared):
                offenders.append(f"{p.relative_to(REPO)}:{n}: {line.strip()}")
    assert not offenders, (
        "these resolve a hardcoded export folder instead of dataset.current():\n  "
        + "\n  ".join(offenders))


@pytest.mark.skipif(shutil.which("git") is None, reason="not a git checkout")
def test_the_pointer_is_tracked():
    """Untracked, it exists on one machine and the problem is unfixed everywhere else."""
    out = subprocess.run(["git", "ls-files", "--error-unmatch", POINTER.name],
                         cwd=REPO, capture_output=True, text=True)
    assert out.returncode == 0, f"{POINTER.name} is not tracked by git"


# ------------------------------------------------------------------ the gate

@pytest.mark.skipif(not GATE.is_file(), reason="gate missing")
def test_the_gate_passes_its_own_selftest():
    """Its selftest covers both directions and the no-interpreter case. A gate that
    cannot fire manufactures exactly the confidence it was built to earn."""
    out = subprocess.run(["bash", str(GATE), "--selftest"],
                         capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "PASS" in out.stdout


def _run_gate(command: str, env: dict | None = None):
    payload = json.dumps({"tool_input": {"command": command}})
    return subprocess.run(["bash", str(GATE)], input=payload, capture_output=True,
                          text=True, cwd=REPO, env={**os.environ, **(env or {})})


@pytest.mark.parametrize("command", [
    'python -c "from scipy.io import loadmat; loadmat(p)"',
    'python3 x.py --store ~/data/processed_archive/event_store_onset_revised_2v',
    'python -c "import mat73"',
])
def test_it_blocks_reaching_for_a_store(command):
    out = _run_gate(command)
    assert out.returncode == 2, out.stderr


@pytest.mark.parametrize("command", [
    'grep -rn "event_store" docs/',                 # naming is not reading
    'pytest tests/test_io.py',                      # the suite reads fixtures on purpose
    'git log -- src/bugarach/store.py',
    'python -c "from bugarach import dataset; dataset.current()"',
    'BUGARACH_STORE_OK=1 python regen.py --store s.mat',
])
def test_it_allows_what_it_must(command):
    out = _run_gate(command)
    assert out.returncode == 0, out.stderr


def test_the_block_hands_over_the_answer():
    """The design property, and the reason this is not merely a refusal.

    The session that prompted this was lost, not defiant — it reached for the store
    because it could not find the folder. A gate that says only "no" leaves it lost.
    """
    out = _run_gate('python -c "loadmat(f)"')
    assert out.returncode == 2
    assert dataset.current_name() in out.stderr, "the block must NAME the folder"
    assert "dataset.current()" in out.stderr, "and give the call that opens it"
    assert "BUGARACH_STORE_OK=1" in out.stderr, "and the way out when it is intended"


# ------------------------------------------------- and the half that was missing
#
# Everything above addresses a session that has already decided to read a store. On
# 2026-08-28, one day after this gate shipped, a session that simply did not know
# where the data was ran `find <home> -maxdepth 6 -type d -name "exports"` and
# hand-pathed the result into --folder four separate times. The gate stayed silent by
# its own correct design (`find` is not store access) and SAP007 stayed silent by its
# own stated one (it greps what a COMMIT adds; an interactive --folder is never
# committed). `dataset.current()` would have answered instantly on that machine.


@pytest.mark.parametrize("command", [
    'find /mnt/lab -maxdepth 6 -type d -name "exports"',      # the 2026-08-28 shape
    'ls /mnt/lab/data/exports/bugarach',
    'ls /mnt/lab/data/processed_archive/event_store_onset_revised_2v | wc -l',
    'find /mnt/lab/data -maxdepth 4 -name "slices.csv"',
    'tree /mnt/lab/data/exports',
])
def test_it_blocks_searching_for_the_data(command):
    out = _run_gate(command)
    assert out.returncode == 2, (
        f"the search gate let this through: {command!r}\n{out.stderr}")


@pytest.mark.parametrize("command", [
    'ls docs/',                                       # an ordinary repo listing
    'ls src/bugarach/',
    'find docs -name "export_folder_spec.md"',        # the contract is not the data
    'find ~/Developer -maxdepth 4 -iname "eval_modularity*"',
    'grep -rn "exports/bugarach" docs/',              # naming a path is not reading it
    'BUGARACH_DATA_OK=1 ls /mnt/lab/data/exports',
])
def test_the_search_gate_leaves_ordinary_work_alone(command):
    """THE OBJECTION TO THIS GATE WAS ALWAYS NOISE, so the answer is a measurement.

    Scored against every Bash command in the 54 bugarach transcripts on the machine
    where it was written — 12,009 of them — the trigger fires 30 times (0.25%), and
    all 30 were read by hand: each is a session locating the data root, listing export
    folders, or counting a store's slices. None is unrelated work.

    Two wider variants were measured and rejected. Allowing the verb after `;` or `&&`
    took it to 140 hits including a heredoc writing a todo file; firing on any `find`
    over the home directory ran at roughly 50% false positives — 23 interruptions to
    buy 2 more true positives. The cases here are the shapes that must stay silent.
    """
    out = _run_gate(command)
    assert out.returncode == 0, (
        f"the search gate fired on ordinary work: {command!r}\n{out.stderr}")


def test_the_search_block_answers_rather_than_only_refusing():
    """Same design property as the store block, for the same reason: the session is
    LOST, and a gate that says only "no" leaves it lost and it churns somewhere else.

    It must also offer `data_root()`, not just `current()`. Six of the thirty measured
    hits were hunting the raw `2R` acquisition folders or the lab workbook, which the
    export folder is not the answer to — the data ROOT is.
    """
    out = _run_gate('find /mnt/lab -maxdepth 6 -type d -name "exports"')
    assert out.returncode == 2
    assert dataset.current_name() in out.stderr, "the block must NAME the folder"
    assert "dataset.current()" in out.stderr, "and give the call that opens it"
    assert "data_root()" in out.stderr, "and the call for the root itself"
    assert "BUGARACH_DATA_OK=1" in out.stderr, "and the way out when it is intended"


def test_the_search_gate_outranks_the_read_only_verb_exemption():
    """ORDER IS THE WHOLE MECHANISM HERE, and getting it wrong is silent.

    The store branch exempts `find`/`ls`/`grep` outright, so that
    `grep -rn event_store docs/` never trips it. That exemption is correct for the
    store branch and is exactly what hid this one for a day. If a future edit moves
    the search check below it, every test above still passes and the gate goes quiet.
    """
    body = GATE.read_text()
    search = body.index("is this command SEARCHING FOR THE DATA")
    exemption = body.index("(git|grep|rg|ag|find|ls|wc|diff|gh)")
    assert search < exemption, (
        "the search check now sits below the read-only-verb exemption, which exempts "
        "find and ls — so it can never fire"
    )


def test_the_named_folder_tracks_the_pointer(tmp_path, monkeypatch):
    """The gate reads the pointer live rather than repeating a name of its own.

    Otherwise the next export makes the gate itself the stale fifth declaration —
    which is the bug, wearing the uniform of the fix.
    """
    assert "current_export.toml" in GATE.read_text()
    body = GATE.read_text()
    assert dataset.current_name() not in body, (
        "the gate hardcodes the folder name; it must read current_export.toml")


def test_it_does_not_fail_open_without_python():
    """`no-heredoc-source.sh` shipped to seven repos exiting 0 for every call because
    `python` was missing from a hook's login PATH. A gate may lose precision when its
    tools are gone. It may not silently stop gating."""
    nopy = ":".join(d for d in os.environ.get("PATH", "").split(":")
                    if "python" not in d.lower())
    out = _run_gate('python -c "loadmat(f)"', env={"PATH": nopy})
    assert out.returncode == 2, "DEGRADED MODE IS OPEN: " + (out.stderr or "(silent)")


# --------------------------------------------------------------- and it is wired

def test_the_gate_is_wired_into_settings():
    """Working and installed are different properties, and only one of them was ever
    checked here before `test_hooks_installed.py` made the point."""
    hooks = json.loads(SETTINGS.read_text())["hooks"]["PreToolUse"]
    wired = [h["command"] for m in hooks if m.get("matcher") == "Bash"
             for h in m["hooks"]]
    assert any(GATE.name in c for c in wired), (
        f"{GATE.name} exists but nothing runs it; PreToolUse(Bash) has: {wired}")
