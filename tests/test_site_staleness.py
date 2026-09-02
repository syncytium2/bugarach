"""A stale site looks exactly like a current one, so the check has to say so.

`tools/site_staleness.py` is the answer to the cheap half of
`docs/todo/2026-08-20-nothing-publishes-the-site-so-it-goes-stale.md`: nothing
publishes bugarach.tonydefazio.com, so the page advances only when somebody
remembers, and on 2026-08-20 it had been three features behind for weeks before
anyone noticed. Automating the *deploy* needs a Cloudflare token in a public
repo's secrets, which is Tony's decision; measuring the gap needs nothing.

The properties worth proving, and the reason each one is here:

- it counts the distance right, against a repo whose history the test built
  itself, so the number is checkable rather than whatever the world happens to
  be today;
- **it never reports "up to date" because it could not look.** This repo runs
  offline regularly and a check that goes quiet when the network does is worse
  than no check, because silence reads as good news;
- it distinguishes "behind" from "the served page is not any version we have",
  which is what an edge rewrite looks like (Cloudflare injected a beacon into
  the viewer on 2026-08-18) and which sends you somewhere else entirely;
- the identifiers it reads are still the ones `tools/build_site.py` writes;
- the briefing line stays inside the byte budget that a 60KB briefing already
  blew once, taking the whole session board with it.

Every test is offline: the network call is stubbed and the git history is a
throwaway repo in tmp_path. Nothing here fetches anything.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "site_staleness.py"
WORKFLOW = ROOT / ".github" / "workflows" / "site-staleness.yml"
WRAPPER = ROOT / "tools" / "session_start_trimmed.sh"


def _load():
    spec = importlib.util.spec_from_file_location("site_staleness", TOOL)
    mod = importlib.util.module_from_spec(spec)
    # Registered before execution: @dataclass resolves annotations through
    # sys.modules, and on 3.14 a module that is not there yet raises.
    sys.modules["site_staleness"] = mod
    spec.loader.exec_module(mod)
    return mod


ss = _load()


# --------------------------------------------------------------- a repo to measure


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(("git", "-C", str(repo), *args),
                          capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """Three commits: viewer v1, viewer v2, and one that does not reach the site.

    Built here rather than measured against this checkout because CI clones
    shallow — `git log -- docs/site/raster_viewer.html` there has one entry and
    every distance would be zero. A test whose fixture is the world tests the
    world's mood.
    """
    r = tmp_path / "clone"
    (r / "docs" / "site").mkdir(parents=True)
    (r / "tools").mkdir()
    subprocess.run(("git", "init", "-q", str(r)), check=True)
    _git(r, "config", "user.email", "t@example.invalid")
    _git(r, "config", "user.name", "test")

    viewer = r / "docs" / "site" / "raster_viewer.html"
    shas = {}

    viewer.write_text("<!-- viewer v1 -->\n", encoding="utf-8")
    _git(r, "add", "-A")
    _git(r, "commit", "-qm", "the viewer, first cut")
    shas["v1"] = _git(r, "rev-parse", "--short", "HEAD")

    viewer.write_text("<!-- viewer v2 -->\n", encoding="utf-8")
    _git(r, "add", "-A")
    _git(r, "commit", "-qm", "the viewer grows a top rail")
    shas["v2"] = _git(r, "rev-parse", "--short", "HEAD")

    (r / "README.md").write_text("prose\n", encoding="utf-8")
    _git(r, "add", "-A")
    _git(r, "commit", "-qm", "prose that never reaches the page")
    shas["head"] = _git(r, "rev-parse", "--short", "HEAD")

    monkeypatch.setattr(ss, "ROOT", r)
    return type("Repo", (), {"path": r, "shas": shas, "viewer": viewer})


def serve(monkeypatch, *, stamp: str | None, viewer: bytes):
    """Stand in for the live site: an index carrying a build stamp, and a viewer."""
    index = b"<footer>BSD-3-Clause"
    if stamp is not None:
        index += b" &middot; built from <code>" + stamp.encode() + b"</code>"
    index += b"</footer>"

    def fake(url, timeout):
        return viewer if url.endswith("/viewer.html") else index

    monkeypatch.setattr(ss, "fetch", fake)


def unreachable(monkeypatch, message="URLError: no route"):
    def fake(url, timeout):
        raise ss.Unreachable(f"{url}: {message}", "URLError")
    monkeypatch.setattr(ss, "fetch", fake)


# --------------------------------------------------------------------- the hold


def _hold(monkeypatch, tmp_path, body: str | None):
    """Point the tool at a throwaway hold file (or none)."""
    p = tmp_path / "DEPLOY_HOLD.md"
    if body is not None:
        p.write_text(body, encoding="utf-8")
    monkeypatch.setattr(ss, "HOLD_FILE", p)


HELD = "---\nheld: yes\nrelease-when: the plumbing lands\n---\n"


def test_a_held_deploy_is_not_advertised_as_one_to_run(repo, monkeypatch, tmp_path):
    """The one tool that tells anyone to deploy has to know when not to.

    Tony queued a deploy on 2026-08-28. The report's copy-paste command, the
    daily CI summary and the session briefing all fire without being asked, so a
    queue that lived only in prose would be outvoted every morning — and the
    session that gave in would be right by every signal it could see.
    """
    serve(monkeypatch, stamp=repo.shas["v1"], viewer=b"<!-- viewer v1 -->\n")
    rep = ss.collect("https://site.invalid", None, 1.0)
    assert rep.status == "behind", "the hold must not change the measurement"

    _hold(monkeypatch, tmp_path, HELD)
    text, brief, md = ss.render_text(rep), ss.render_brief(rep), ss.render_markdown(rep)
    for rendered in (text, brief, md):
        assert "hold" in rendered.lower(), "a held deploy that reads as runnable"
    assert "npm run deploy" not in text, (
        "the report still hands over the command that publishes over the hold")
    assert "the plumbing lands" in text and "the plumbing lands" in md, (
        "a hold with no release condition is indistinguishable from a stall")
    assert "DEPLOY_HOLD.md" in brief, "the briefing must say where the hold is"


def test_the_hold_reports_the_distance_unchanged(repo, monkeypatch, tmp_path):
    """Holding a deploy is not the same as pretending the site is current.

    The failure to avoid: a hold that quietly turns the verdict green, so when it
    is lifted nobody knows how far behind the page had drifted.
    """
    serve(monkeypatch, stamp=repo.shas["v1"], viewer=b"<!-- viewer v1 -->\n")
    _hold(monkeypatch, tmp_path, HELD)
    rep = ss.collect("https://site.invalid", None, 1.0)
    assert rep.status == "behind" and rep.exit_code == 1
    assert "behind by 2 commits" in ss.render_text(rep)


@pytest.mark.parametrize("body", [
    None,                                   # no file at all
    "---\nheld: no\nrelease-when: x\n---\n",
    "---\nrelease-when: x\n---\n",           # no `held:` key
    "just some prose about deploying\n",
])
def test_anything_but_an_explicit_yes_means_not_held(repo, monkeypatch, tmp_path, body):
    """Fail open, on purpose.

    The expensive failure is a hold nobody notices, not a typo that fails to stop
    a deploy — and a tool that announced a hold nobody set would be ignored
    inside a week, at which point it would not stop the real one either.
    """
    serve(monkeypatch, stamp=repo.shas["v1"], viewer=b"<!-- viewer v1 -->\n")
    _hold(monkeypatch, tmp_path, body)
    assert ss.deploy_hold() is None
    assert "npm run deploy" in ss.render_text(ss.collect("https://site.invalid", None, 1.0))


def test_the_shipped_hold_file_parses_as_whatever_it_currently_says():
    """The real `docs/DEPLOY_HOLD.md`, read by the real reader.

    Not asserting held-or-not — that changes with the state of the world and a
    test asserting today's answer would fail the day somebody lifts it correctly.
    What must hold is that the file the repo ships is *parseable*: if it is held
    it names a release condition, and either way nothing raises.
    """
    held = ss.deploy_hold()
    if held is not None:
        assert held.strip(), "held with an empty release condition"
        assert "no release condition recorded" not in held, (
            "docs/DEPLOY_HOLD.md is held but records no `release-when:`")


# ----------------------------------------------------------------- the measurement


def test_it_counts_the_distance_and_says_which_commits_matter(repo, monkeypatch):
    serve(monkeypatch, stamp=repo.shas["v1"], viewer=b"<!-- viewer v1 -->\n")
    rep = ss.collect("https://site.invalid", None, 1.0)

    assert rep.status == "behind"
    assert rep.exit_code == 1
    assert rep.behind_total == 2, "two commits landed after the deployed one"
    # ...of which exactly one changes what a reader would see.
    assert [s for _, s in rep.behind_pages] == ["the viewer grows a top rail"]
    assert [s for _, s in rep.viewer_behind] == ["the viewer grows a top rail"]


def test_the_two_identifiers_are_read_independently(repo, monkeypatch):
    """The stamp names a commit; the served bytes name one too. Both are reported.

    They are not averaged into a single guess, because when they disagree the
    disagreement is the finding.
    """
    serve(monkeypatch, stamp=repo.shas["v1"], viewer=b"<!-- viewer v1 -->\n")
    rep = ss.collect("https://site.invalid", None, 1.0)
    assert rep.stamp == repo.shas["v1"] and rep.stamp_on_ref
    assert rep.viewer_matched and rep.viewer_sha == repo.shas["v1"]


def test_a_current_site_is_current_even_though_main_moved(repo, monkeypatch):
    """`main` advancing is not staleness. Only the site's own sources count."""
    serve(monkeypatch, stamp=repo.shas["v2"], viewer=b"<!-- viewer v2 -->\n")
    rep = ss.collect("https://site.invalid", None, 1.0)
    assert rep.behind_total == 1, "the prose commit is behind it..."
    assert rep.behind_pages == [], "...and changes nothing the site serves"
    assert rep.status == "current"
    assert rep.exit_code == 0


def test_a_page_matching_nothing_committed_is_unknown_not_current(repo, monkeypatch):
    """What an edge rewrite looks like from here — and it is not staleness.

    Cloudflare injected an analytics beacon into the viewer on 2026-08-18. If
    that happened again the served bytes would match no commit; calling it
    "behind" would send somebody to run a deploy that fixes nothing.
    """
    serve(monkeypatch, stamp=None, viewer=b"<!-- viewer v2 --><script>beacon</script>")
    rep = ss.collect("https://site.invalid", None, 1.0)
    assert rep.viewer_matched is False
    assert rep.status == "unknown"
    assert rep.exit_code == 2
    text = ss.render_text(rep)
    assert "MATCHES NO COMMITTED VERSION" in text
    assert "audit_deployed_page.py" in text, "point at the tool that can tell why"


def test_a_stamp_this_clone_does_not_have_is_admitted(repo, monkeypatch):
    """A deploy from an unpushed tree, or a clone that has not fetched. Either
    way the honest answer is that the distance is not computable here."""
    serve(monkeypatch, stamp="deadbee", viewer=b"<!-- nothing we ever committed -->")
    rep = ss.collect("https://site.invalid", None, 1.0)
    assert rep.stamp_known is False
    assert rep.status == "unknown"
    assert "unknown to this clone" in ss.render_text(rep)


# ------------------------------------------------------- the offline half, which matters


def test_unreachable_is_never_reported_as_up_to_date(repo, monkeypatch, tmp_path):
    monkeypatch.setattr(ss, "cache_path", lambda: tmp_path / "cache.json")
    unreachable(monkeypatch)
    rep = ss.collect("https://site.invalid", None, 1.0)

    assert rep.reachable is False
    assert rep.status == "unknown"
    assert rep.exit_code == 2
    for rendered in (ss.render_text(rep), ss.render_brief(rep), ss.render_markdown(rep)):
        low = rendered.lower()
        assert "could not reach" in low or "unreachable" in low
        assert "up to date" not in low
        assert "verdict: current" not in low


@pytest.mark.parametrize("exc", [
    OSError("host down"),
    TimeoutError(),
    ValueError("something the ssl layer did"),
    __import__("urllib.error", fromlist=["error"]).HTTPError(
        "https://site.invalid/", 503, "unavailable", {}, None),
])
def test_every_network_failure_becomes_one_answer(monkeypatch, exc):
    """DNS, TLS, timeout, a 503 from the edge — none of them is information
    about the repo, and none of them may escape as a traceback."""
    def boom(*a, **k):
        raise exc
    monkeypatch.setattr(ss.urllib.request, "urlopen", boom)
    with pytest.raises(ss.Unreachable) as caught:
        ss.fetch("https://site.invalid/", 1.0)
    assert caught.value.brief, "the brief form is what the briefing line prints"


def test_a_failed_look_does_not_overwrite_what_we_last_knew(repo, monkeypatch, tmp_path):
    """The cache holds observations of the site, and a failure is not one.

    Overwriting it with our own network trouble would throw away the last thing
    anybody knew about the page in exchange for a record of a bad wifi moment.
    """
    cache = tmp_path / "cache.json"
    monkeypatch.setattr(ss, "cache_path", lambda: cache)

    serve(monkeypatch, stamp=repo.shas["v1"], viewer=b"<!-- viewer v1 -->\n")
    good = ss.collect("https://site.invalid", None, 1.0)
    ss.cache_write(good)
    assert cache.is_file()
    before = cache.read_text(encoding="utf-8")

    unreachable(monkeypatch)
    bad = ss.collect("https://site.invalid", None, 1.0)
    ss.cache_write(bad)
    assert cache.read_text(encoding="utf-8") == before

    # ...and the failed run says what was last seen, as history, not as status.
    assert bad.last_seen == repo.shas["v1"]
    assert bad.status == "unknown"
    assert repo.shas["v1"] in ss.render_brief(bad)
    assert "UNKNOWN" in ss.render_brief(bad)


def test_the_cache_expires_and_is_keyed_on_the_url(repo, monkeypatch, tmp_path):
    cache = tmp_path / "cache.json"
    monkeypatch.setattr(ss, "cache_path", lambda: cache)
    serve(monkeypatch, stamp=repo.shas["v1"], viewer=b"<!-- viewer v1 -->\n")
    ss.cache_write(ss.collect("https://site.invalid", None, 1.0))

    assert ss.cache_read("https://site.invalid", 60) is not None
    assert ss.cache_read("https://site.invalid", 0) is None, "0 minutes means refetch"
    assert ss.cache_read("https://elsewhere.invalid", 60) is None, "wrong site"


def test_the_cached_answer_is_recomputed_against_git_not_replayed(repo, monkeypatch,
                                                                  tmp_path):
    """Only the observation is cached. How far behind it is changes when `main`
    moves, and noticing that needs no network at all."""
    cache = tmp_path / "cache.json"
    monkeypatch.setattr(ss, "cache_path", lambda: cache)
    serve(monkeypatch, stamp=repo.shas["v1"], viewer=b"<!-- viewer v1 -->\n")
    ss.cache_write(ss.collect("https://site.invalid", None, 1.0))

    # main moves again, with the network unavailable this time
    (repo.path / "docs" / "site" / "raster_viewer.html").write_text("v3\n",
                                                                    encoding="utf-8")
    _git(repo.path, "add", "-A")
    _git(repo.path, "commit", "-qm", "a third viewer")
    unreachable(monkeypatch)

    rep = ss.from_cache(ss.cache_read("https://site.invalid", 60), None)
    assert rep.behind_total == 3, "recomputed from git, not replayed from the cache"
    assert len(rep.behind_pages) == 2


# --------------------------------------------------- the assumptions it is built on


def test_the_build_still_writes_the_stamp_this_reads():
    """The identifier is `tools/build_site.py`'s footer. If that wording changes
    this check silently stops recognising it, so the coupling is asserted."""
    tpl = (ROOT / "tools" / "build_site.py").read_text(encoding="utf-8")
    assert "built from <code>{commit}</code>" in tpl, (
        "site_staleness.py names the deployed commit from this footer — if the "
        "footer moved, move STAMP_RE with it"
    )
    assert ss.STAMP_RE.search(b"built from <code>a189d5e</code>")


def test_the_served_viewer_is_still_a_straight_copy_of_the_repo_file():
    """The other identifier: hashing the served page only names a commit while
    `site/viewer.html` is byte-for-byte `docs/site/raster_viewer.html`."""
    tpl = (ROOT / "tools" / "build_site.py").read_text(encoding="utf-8")
    assert re.search(r"shutil\.copyfile\(viewer,\s*SITE\s*/\s*[\"']viewer\.html[\"']\)",
                     tpl), "the viewer is no longer copied verbatim — rehash accordingly"
    assert (ROOT / ss.VIEWER_SOURCE).is_file()


def test_it_needs_no_credentials_and_holds_none():
    """The reason this could ship without waiting for anybody. If it ever grows a
    token it stops being the cheap option and becomes Tony's decision."""
    body = TOOL.read_text(encoding="utf-8")
    for word in ("CLOUDFLARE", "API_TOKEN", "wrangler deploy", "secrets."):
        assert word not in body.replace("`npm run deploy`", ""), \
            f"{word} in a check that is supposed to hold no publish rights"


# ------------------------------------------------------------- reaching a human


@pytest.mark.parametrize("status", ["behind", "current", "unknown", "offline"])
def test_the_briefing_line_fits_the_budget(repo, monkeypatch, tmp_path, status):
    """One line, and a short one. The briefing has a hard byte cap — on
    2026-08-20 blowing it made the entire session board invisible, so a check
    that reports by making the briefing too big to deliver reports nothing."""
    monkeypatch.setattr(ss, "cache_path", lambda: tmp_path / "cache.json")
    if status == "behind":
        serve(monkeypatch, stamp=repo.shas["v1"], viewer=b"<!-- viewer v1 -->\n")
    elif status == "current":
        serve(monkeypatch, stamp=repo.shas["head"], viewer=b"<!-- viewer v2 -->\n")
    elif status == "unknown":
        serve(monkeypatch, stamp=None, viewer=b"unrecognised")
    else:
        unreachable(monkeypatch)

    line = ss.render_brief(ss.collect("https://site.invalid", None, 1.0))
    assert "\n" not in line
    assert len(line.encode("utf-8")) <= 140, f"{len(line)}B is too much briefing"


def test_the_briefing_actually_carries_the_line():
    """A check nobody sees is a check nobody acts on. The wrapper must place it
    in the delivered briefing, not print it somewhere adjacent."""
    r = subprocess.run(["bash", str(WRAPPER)], capture_output=True, text=True,
                       cwd=ROOT, timeout=120,
                       env={**__import__("os").environ,
                            "BUGARACH_SITE_STALENESS_CMD":
                                'echo "site: 4 commits behind origin/main"'})
    if "SESSION START" not in r.stdout:
        pytest.skip("not a git repo / vendored hook unavailable here")
    assert "site: 4 commits behind" in r.stdout
    assert "briefing delivered:" in r.stdout, "and the size canary still fires"


def test_the_briefing_never_reaches_the_network_from_a_test():
    """This suite drives the wrapper (tests/test_board_digest.py does it three
    times). A test that fetches a production URL fails for reasons that are not
    about this repo, and hangs where there is no network."""
    body = WRAPPER.read_text(encoding="utf-8")
    assert "PYTEST_CURRENT_TEST" in body
    r = subprocess.run(["bash", str(WRAPPER)], capture_output=True, text=True,
                       cwd=ROOT, timeout=120)
    if "SESSION START" not in r.stdout:
        pytest.skip("not a git repo / vendored hook unavailable here")
    assert "site: " not in r.stdout


# ------------------------------------------------------------------------- CI


def test_ci_reports_staleness_without_going_red():
    """A red build for something no automation here can fix teaches people that
    red means nothing — and then a real failure gets waved through too."""
    body = WORKFLOW.read_text(encoding="utf-8")
    assert "--exit-zero" in body
    assert "GITHUB_STEP_SUMMARY" in body, "reporting means somewhere a human looks"
    assert "fetch-depth: 0" in body, (
        "naming the deployed commit means hashing history — a shallow clone "
        "would report 'unknown' forever"
    )
    assert "secrets." not in body, "this job deploys nothing and needs no token"


def test_the_workflow_parses():
    yaml = pytest.importorskip("yaml")
    doc = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    # `on:` is YAML 1.1's boolean true — the reason this assertion looks odd.
    triggers = doc.get("on", doc.get(True))
    assert "schedule" in triggers and "workflow_dispatch" in triggers
    assert doc["jobs"]["staleness"]["steps"]


def test_the_tool_runs_end_to_end_offline(tmp_path, monkeypatch):
    """The CLI itself, exercised the way CI and the briefing call it, with the
    network guaranteed absent. It must print something and exit 0 under
    --exit-zero, never traceback."""
    for args in (["--exit-zero"], ["--brief", "--exit-zero", "--cache-ttl", "0"],
                 ["--format", "github", "--exit-zero"]):
        r = subprocess.run(
            [__import__("sys").executable, str(TOOL),
             "--url", "https://bugarach-staleness-test.invalid",
             "--timeout", "2", *args],
            capture_output=True, text=True, cwd=ROOT, timeout=120)
        assert r.returncode == 0, r.stderr
        assert "Traceback" not in r.stderr
        assert r.stdout.strip(), "a check that prints nothing reports nothing"
        assert "up to date" not in r.stdout.lower()


# ---------------------------------------------------------------------------------
# THE GATE HAS TO BE LOOKING AT THE FILES THE BUILD READS.
#
# `PAGE_SOURCES` was a hand-kept copy of `build_site.py`'s inputs, and it went
# stale in the way a second copy always does — quietly, in the copy nobody is
# editing. It never gained `docs/learned/architecture.svg` or
# `docs/learned/learned_detector.html`, so on 2026-09-02, across the one commit
# that replaced the site's lead figure, this tool reported "VERDICT: current".
# ---------------------------------------------------------------------------------

def _build_site():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    import build_site
    return build_site


def test_every_file_the_build_reads_is_watched():
    """Derived, not copied — so this asserts the derivation rather than a list."""
    import site_staleness
    bs = _build_site()
    missing = [p for p in bs.SOURCE_PATHS if p not in site_staleness.PAGE_SOURCES]
    assert not missing, (
        f"{missing} are read by build_site.py and invisible to the staleness "
        "gate, so a commit changing them would report the site current")


def test_the_two_that_were_missing_are_watched():
    """Named individually, because a list can shrink back without the general
    assertion above noticing — `SOURCE_PATHS` is what both sides now read."""
    import site_staleness
    for path in ("docs/learned/architecture.svg",
                 "docs/learned/learned_detector.html"):
        assert path in site_staleness.PAGE_SOURCES, f"{path} is unwatched again"


def test_the_builder_names_the_paths_it_reads():
    """`SOURCE_PATHS` has to be the real constants, not strings beside them."""
    bs = _build_site()
    for const in ("ARCHITECTURE_SVG", "RASTER_VIEWER", "REALITY_CHECK",
                  "LEARNED_REPORT", "LANDSCAPE"):
        rel = getattr(bs, const)
        assert rel in bs.SOURCE_PATHS, (
            f"build_site.{const} is a file the build reads and SOURCE_PATHS "
            "does not list it")
        assert (bs.ROOT / rel).exists(), f"build_site.{const} is missing on disk"


def test_the_gate_runs_on_a_bare_interpreter():
    """It runs in the session briefing, outside the venv. Importing build_site
    to derive the list must not change that — both modules are stdlib only."""
    import subprocess
    import sys
    from pathlib import Path
    tools = Path(__file__).resolve().parent.parent / "tools"
    r = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {str(tools)!r}); "
         "import site_staleness; print(len(site_staleness.PAGE_SOURCES))"],
        capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
    assert r.returncode == 0, r.stderr
    assert int(r.stdout.strip()) >= 6


def test_the_gate_does_not_count_its_own_maintenance():
    """A change to the checker never changes what the site serves.

    The first version of the derivation listed `site_staleness.py` in its own
    `PAGE_SOURCES`, reasoning that a fix here changes the verdict. True, and the
    wrong question: this list answers "what changes the bytes we publish". A gate
    that cries wolf about its own maintenance is a gate people stop reading, and
    this repo has spent two days removing exactly that.
    """
    import site_staleness
    assert "tools/site_staleness.py" not in site_staleness.PAGE_SOURCES
