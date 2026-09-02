#!/usr/bin/env python3
"""How far behind `main` is the page at bugarach.tonydefazio.com?

    python tools/site_staleness.py             # the full report
    python tools/site_staleness.py --brief     # one line, for the session briefing
    python tools/site_staleness.py --format github   # for a CI step summary

Nothing in this repo publishes the site. `npm run deploy` is a thing a person
remembers, and a stale page looks exactly like a current one — on 2026-08-20 the
live site had been serving five detectors for weeks while `main` had six, and the
way that was discovered was somebody opening it. This tool makes the gap say its
own name. **It does not deploy and cannot**: it reads the public site over HTTPS
and needs no credentials, which is the whole reason it could be built without
waiting for anybody (docs/todo/2026-08-20-nothing-publishes-the-site-so-it-goes-stale.md,
option 2).

WHAT IDENTIFIES THE DEPLOYED VERSION — two answers, kept separate on purpose.

1. **The build stamp.** `tools/build_site.py` already writes the building
   checkout's short sha into the footer of `index.html` ("built from <code>…"),
   so the site says which commit produced it. That is exact and cheap.
2. **The served bytes of the viewer.** `site/viewer.html` is a byte-for-byte copy
   of `docs/site/raster_viewer.html`, so hashing what is served and matching it
   against every committed version of that file names the commit independently.

They are reported together rather than merged. A stamp with no matching viewer
means the served page is not the file we think it is — a hand deploy from an
unpushed tree, or the edge rewriting HTML, which has happened here (2026-08-18,
a Cloudflare beacon injected into the one page that promises no network calls).
Neither is staleness, and calling it staleness would send somebody to fix the
wrong thing. **Whether the served page reaches anything is not this tool's
question** — that is `tools/audit_deployed_page.py`, which drives a real browser
because the injection was conditional on the request looking like one. A plain
GET is fine for *identity*, which is all this asks.

WHAT IT NEVER DOES: report "up to date" because it could not look. Unreachable is
its own answer (exit 2) and says so in every output format. This repo works
offline regularly and a check that goes quiet when the network does is worse than
no check, because its silence reads as good news.

`/viewer.html` 307s to `/viewer`; redirects are followed. A `curl` without `-L`
returns zero bytes there and reads as a failed deploy.

EXIT  0 current · 1 behind · 2 could not tell (unreachable, or the served page
matches nothing committed).  `--exit-zero` pins it to 0 for callers that must not
go red — CI reports this, it does not gate on it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_BASE = "https://bugarach.tonydefazio.com"
VIEWER_SOURCE = "docs/site/raster_viewer.html"

HOLD_FILE = ROOT / "docs" / "DEPLOY_HOLD.md"


def deploy_hold() -> str | None:
    """The condition that releases a held deploy, or None if nothing is held.

    **This tool is the loudest voice telling anyone to deploy** — a copy-paste
    command in the full report, a daily CI summary, and a line in every session
    briefing — so when a deploy is deliberately queued, this is where the queue
    has to be visible. A hold recorded only in prose is outvoted every morning by
    nags that fire by themselves, and the session that gives in is right by every
    signal it can see (Tony, 2026-08-28: *"queue these updates to land with the
    next iteration of the pipeline plumbing"*).

    Deliberately forgiving about the file's shape. A missing file, an unreadable
    one, or `held:` set to anything but a yes all mean "not held" — the failure
    worth engineering against is a hold nobody notices, not a typo that fails to
    stop a deploy. A tool that announced a hold nobody set would be ignored
    inside a week, and then it would not stop the real one either.
    """
    try:
        text = HOLD_FILE.read_text(encoding="utf-8")
    except OSError:
        return None
    held = release = ""
    for line in text.splitlines()[:20]:
        key, _, val = line.partition(":")
        key, val = key.strip().lower(), val.strip()
        if key == "held":
            held = val.lower()
        elif key == "release-when":
            release = val
    if held not in {"yes", "true", "on"}:
        return None
    return release or "see docs/DEPLOY_HOLD.md — no release condition recorded"

# What a commit has to touch to change what the site serves. Everything
# build_site.py opens, and the figure script whose output it embeds.
#
# NOT EXHAUSTIVE, and the report says so rather than pretending: `hero.png` is
# rendered by make_diagnostic.py from `src/bugarach`, so a detector change can
# change the published picture without touching one path below. The honest
# headline is therefore two numbers — commits behind, and commits behind that
# touch these — never one.
def _page_sources() -> tuple[str, ...]:
    """What the site is built FROM, taken from the builder rather than copied.

    THIS LIST USED TO LIVE HERE AND IT WENT STALE, in the way a second copy
    always does — quietly, in the copy nobody is editing. It never gained
    `docs/learned/architecture.svg`, which `build_site.py` inlines into the front
    page as `MODEL_SVG`, nor `docs/learned/learned_detector.html`, which is one
    of the four published pages. So on 2026-09-02, across the single commit that
    replaced the site's lead figure, this tool reported **"VERDICT: current"** —
    the gate whose entire job is to notice a stale front page, saying the page
    was fine because it was not looking at the file that had changed.

    `build_site.SOURCE_PATHS` is now the one declaration and this derives from
    it. Both modules are standard-library only, so the import costs nothing and
    cannot fail where this tool runs (it runs in the session briefing, on a bare
    interpreter, outside the venv).
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_site
    return tuple(build_site.SOURCE_PATHS) + (
        "docs/site",             # the viewer's siblings, which build_site copies
        "tools/make_diagnostic.py",   # not imported by build_site; run by it
    )
    # NOT this file. A change to the CHECKER never changes what the site serves,
    # and listing it here made a commit that only fixed this gate report "deploy
    # it" -- a gate that cries wolf about its own maintenance is a gate people
    # stop reading. The question this list answers is "what changes the bytes we
    # publish", not "what changes the verdict".


PAGE_SOURCES = _page_sources()

# The footer build_site.py writes: `built from <code>a189d5e</code>`.
STAMP_RE = re.compile(rb"built\s+from\s*<code>\s*([0-9a-fA-F]{7,40})\s*</code>")

# How many viewer revisions back to hash before giving up on identifying the
# served bytes. A deploy older than this is "ancient", which is the same call to
# action as "old" and not worth a slow walk through history to refine.
HISTORY_DEPTH = 80

CACHE_NAME = "bugarach_site_staleness.json"


class Unreachable(Exception):
    """The site could not be read. Not evidence about the site's contents."""

    def __init__(self, message: str, brief: str = "") -> None:
        super().__init__(message)
        self.brief = brief or message


# --------------------------------------------------------------------------- git


def git(*args: str, check: bool = False) -> str | None:
    """`git -C ROOT …` as text, or None when it fails. Never raises for the caller."""
    try:
        proc = subprocess.run(("git", "-C", str(ROOT), *args),
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        if check:
            return None
        return None
    return proc.stdout


def git_bytes(*args: str) -> bytes | None:
    try:
        proc = subprocess.run(("git", "-C", str(ROOT), *args),
                              capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout if proc.returncode == 0 else None


def resolve_ref(preferred: str | None) -> str | None:
    """The ref that stands for "what should be published".

    `origin/main` when the clone has it — a worktree's own branch is not what the
    site is behind. Falls back to HEAD so the tool still answers in a clone that
    has never fetched, and the report names which one it used.
    """
    for candidate in ([preferred] if preferred else []) + ["origin/main", "HEAD"]:
        if candidate and git("rev-parse", "--verify", "--quiet", candidate + "^{commit}"):
            return candidate
    return None


def describe(rev: str) -> tuple[str, str, str]:
    """(short sha, subject, ISO date) for a rev, blanks when it is unknown here."""
    out = git("log", "-1", "--format=%h%x00%s%x00%cI", rev)
    if not out:
        return ("", "", "")
    parts = out.strip("\n").split("\0")
    return (parts[0], parts[1], parts[2]) if len(parts) == 3 else ("", "", "")


def commits_between(old: str, new: str, paths: tuple[str, ...] = ()) -> list[tuple[str, str]]:
    args = ["log", "--format=%h%x00%s", f"{old}..{new}"]
    if paths:
        args += ["--", *paths]
    out = git(*args)
    if not out:
        return []
    rows = []
    for line in out.splitlines():
        if "\0" in line:
            sha, subject = line.split("\0", 1)
            rows.append((sha, subject))
    return rows


def viewer_revisions(ref: str, depth: int = HISTORY_DEPTH) -> list[tuple[str, str]]:
    out = git("log", f"-{depth}", "--format=%h%x00%s", ref, "--", VIEWER_SOURCE)
    if not out:
        return []
    return [tuple(line.split("\0", 1)) for line in out.splitlines() if "\0" in line]  # type: ignore[misc]


def match_viewer(served: bytes, ref: str) -> tuple[str, str] | None:
    """The newest commit whose `raster_viewer.html` is byte-identical to `served`."""
    want = hashlib.sha256(served).hexdigest()
    for sha, subject in viewer_revisions(ref):
        blob = git_bytes("show", f"{sha}:{VIEWER_SOURCE}")
        if blob is not None and hashlib.sha256(blob).hexdigest() == want:
            return (sha, subject)
    return None


# ------------------------------------------------------------------------ network


def fetch(url: str, timeout: float) -> bytes:
    req = urllib.request.Request(url, headers={
        # Deliberately honest about who is asking. This is an identity check, not
        # the injection audit — see the module docstring.
        "User-Agent": "bugarach-site-staleness/1 (+tools/site_staleness.py)",
        "Accept": "text/html",
        "Cache-Control": "no-cache",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 — fixed https host
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise Unreachable(f"{url} returned HTTP {exc.code}",
                          f"HTTP {exc.code}") from exc
    except Exception as exc:                      # noqa: BLE001 — every failure is "could not look"
        raise Unreachable(f"{url}: {exc.__class__.__name__}: {exc}",
                          exc.__class__.__name__) from exc


# ------------------------------------------------------------------------- report


@dataclass
class Report:
    base: str
    ref: str | None = None
    ref_sha: str = ""
    ref_subject: str = ""
    reachable: bool = False
    problem: str = ""
    problem_brief: str = ""
    last_seen: str = ""            # sha from an EXPIRED observation, when offline
    last_seen_age_min: float = 0.0
    stamp: str = ""                # short sha the deployed index.html claims
    stamp_known: bool = False      # ...and this clone has that commit
    stamp_on_ref: bool = False     # ...and it is an ancestor of the ref
    stamp_subject: str = ""
    stamp_date: str = ""
    viewer_sha: str = ""           # commit whose viewer bytes match what is served
    viewer_subject: str = ""
    viewer_matched: bool = False
    behind_total: int = 0
    behind_pages: list[tuple[str, str]] = field(default_factory=list)
    viewer_behind: list[tuple[str, str]] = field(default_factory=list)
    checked_at: str = ""
    from_cache: bool = False
    cache_age_min: float = 0.0

    @property
    def status(self) -> str:
        """`current`, `behind`, or `unknown`. Never `current` by default."""
        if not self.reachable:
            return "unknown"
        if not (self.stamp_on_ref or self.viewer_matched):
            return "unknown"
        if self.behind_total == 0 and not self.viewer_behind:
            return "current"
        if not self.behind_pages and not self.viewer_behind:
            # main moved, but nothing the site serves did. Not a reason to deploy.
            return "current"
        return "behind"

    @property
    def exit_code(self) -> int:
        return {"current": 0, "behind": 1, "unknown": 2}[self.status]


def collect(base: str, ref_pref: str | None, timeout: float) -> Report:
    rep = Report(base=base.rstrip("/"))
    rep.checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rep.ref = resolve_ref(ref_pref)
    if rep.ref:
        rep.ref_sha, rep.ref_subject, _ = describe(rep.ref)

    try:
        index = fetch(rep.base + "/", timeout)
        viewer = fetch(rep.base + "/viewer.html", timeout)
    except Unreachable as exc:
        rep.problem = str(exc)
        rep.problem_brief = exc.brief
        attach_last_seen(rep)
        return rep
    rep.reachable = True

    found = STAMP_RE.search(index)
    if found:
        rep.stamp = found.group(1).decode("ascii")
        rep.stamp_known = bool(git("rev-parse", "--verify", "--quiet",
                                   rep.stamp + "^{commit}"))
    if rep.stamp_known:
        _, rep.stamp_subject, rep.stamp_date = describe(rep.stamp)
        if rep.ref:
            rep.stamp_on_ref = subprocess.run(
                ("git", "-C", str(ROOT), "merge-base", "--is-ancestor",
                 rep.stamp, rep.ref)).returncode == 0

    if rep.ref:
        hit = match_viewer(viewer, rep.ref)
        if hit:
            rep.viewer_matched = True
            rep.viewer_sha, rep.viewer_subject = hit
            rep.viewer_behind = commits_between(rep.viewer_sha, rep.ref,
                                                (VIEWER_SOURCE,))

    anchor = rep.stamp if rep.stamp_on_ref else (rep.viewer_sha if rep.viewer_matched else "")
    if anchor and rep.ref:
        rep.behind_total = len(commits_between(anchor, rep.ref))
        rep.behind_pages = commits_between(anchor, rep.ref, PAGE_SOURCES)
    return rep


# -------------------------------------------------------------------------- cache


def cache_path() -> Path | None:
    """Machine-local, shared by every worktree, never committed.

    The deployed site is a property of the world, not of a checkout, so the cache
    lives in the common git dir where all worktrees of this clone see the same
    one. Only the *observation* is cached — the sha the site claims and the bytes
    it served. How far behind that is gets recomputed from git every time, because
    the answer changes when `main` moves and no fetch is needed to notice.
    """
    out = git("rev-parse", "--git-common-dir")
    if not out:
        return None
    common = Path(out.strip())
    if not common.is_absolute():
        common = (ROOT / common).resolve()
    return common / CACHE_NAME if common.is_dir() else None


def cache_read_any(base: str) -> dict | None:
    """The stored observation of `base`, at any age, or None."""
    path = cache_path()
    if not path or not path.is_file():
        return None
    try:
        blob = json.loads(path.read_text(encoding="utf-8"))
        age_min = (time.time() - float(blob["saved_at"])) / 60.0
    except (OSError, ValueError, KeyError):
        return None
    if blob.get("base") != base.rstrip("/") or age_min < 0:
        return None
    blob["_age_min"] = age_min
    return blob


def cache_read(base: str, max_age_min: float) -> dict | None:
    blob = cache_read_any(base)
    if blob is None or blob["_age_min"] > max_age_min:
        return None
    return blob


def attach_last_seen(rep: Report) -> None:
    """Say when the site was last successfully read, without implying it still is.

    An offline run has nothing to report about the site, but "we last saw a189d5e,
    nine hours ago" is worth more than silence to whoever reads the briefing — as
    long as it is never dressed up as the current state. The status stays
    `unknown`; this only fills in the parenthetical.
    """
    blob = cache_read_any(rep.base)
    if not blob:
        return
    rep.last_seen = blob.get("stamp") or blob.get("viewer_sha") or ""
    rep.last_seen_age_min = float(blob.get("_age_min", 0.0))


def cache_write(rep: Report) -> None:
    """Store a SUCCESSFUL observation only.

    A failed fetch says nothing about the site, so writing it would throw away the
    last thing we did know in exchange for a record of our own network trouble.
    """
    path = cache_path()
    if not path or not rep.reachable:
        return
    blob = {
        "saved_at": time.time(),
        "checked_at": rep.checked_at,
        "base": rep.base,
        "reachable": rep.reachable,
        "problem": rep.problem,
        "stamp": rep.stamp,
        "viewer_sha": rep.viewer_sha,
        "viewer_matched": rep.viewer_matched,
    }
    try:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(blob), encoding="utf-8")
        tmp.replace(path)
    except OSError:
        pass          # a cache that cannot be written is not a reason to fail


def from_cache(blob: dict, ref_pref: str | None) -> Report:
    """Rebuild a report from a cached observation, recomputing the git side."""
    rep = Report(base=blob.get("base", DEFAULT_BASE))
    rep.from_cache = True
    rep.cache_age_min = float(blob.get("_age_min", 0.0))
    rep.checked_at = blob.get("checked_at", "")
    rep.reachable = bool(blob.get("reachable"))
    rep.problem = blob.get("problem", "")
    rep.ref = resolve_ref(ref_pref)
    if rep.ref:
        rep.ref_sha, rep.ref_subject, _ = describe(rep.ref)
    rep.stamp = blob.get("stamp", "")
    rep.viewer_sha = blob.get("viewer_sha", "")
    rep.viewer_matched = bool(blob.get("viewer_matched"))
    if rep.stamp:
        rep.stamp_known = bool(git("rev-parse", "--verify", "--quiet",
                                   rep.stamp + "^{commit}"))
    if rep.stamp_known:
        _, rep.stamp_subject, rep.stamp_date = describe(rep.stamp)
        if rep.ref:
            rep.stamp_on_ref = subprocess.run(
                ("git", "-C", str(ROOT), "merge-base", "--is-ancestor",
                 rep.stamp, rep.ref)).returncode == 0
    if rep.viewer_matched and rep.ref:
        rep.viewer_behind = commits_between(rep.viewer_sha, rep.ref, (VIEWER_SOURCE,))
    anchor = rep.stamp if rep.stamp_on_ref else (rep.viewer_sha if rep.viewer_matched else "")
    if anchor and rep.ref:
        rep.behind_total = len(commits_between(anchor, rep.ref))
        rep.behind_pages = commits_between(anchor, rep.ref, PAGE_SOURCES)
    return rep


# ------------------------------------------------------------------------ render


def _age(rep: Report) -> str:
    if not rep.from_cache:
        return "just now"
    mins = rep.cache_age_min
    if mins < 90:
        return f"{mins:.0f}m ago"
    return f"{mins / 60:.0f}h ago"


def render_brief(rep: Report) -> str:
    """One line for the session briefing. Budgeted: the briefing has a byte cap."""
    if not rep.reachable:
        tail = ""
        if rep.last_seen:
            hours = rep.last_seen_age_min / 60
            tail = (f"; last read {rep.last_seen} "
                    f"{hours:.0f}h ago" if hours >= 1 else
                    f"; last read {rep.last_seen} just now")
        return (f"site: UNREACHABLE ({rep.problem_brief}), so staleness is "
                f"UNKNOWN{tail}")
    if rep.status == "unknown":
        return ("site: served page matches nothing committed — "
                f"stamp {rep.stamp or 'absent'}; run tools/site_staleness.py")
    if rep.status == "current":
        return (f"site: current as of {rep.stamp or rep.viewer_sha} "
                f"({_age(rep)}) — nothing it serves has changed since.")
    what = f"{len(rep.behind_pages)} change the pages it serves"
    if rep.viewer_behind:
        what += f", {len(rep.viewer_behind)} the viewer"
    # The briefing is where a session decides what to do before it has read
    # anything, so the hold has to reach it. Without this line the briefing says
    # "deploy it" every morning at a queue that is deliberate.
    if deploy_hold():
        return (f"site: {rep.behind_total} commits behind {rep.ref} ({what}) — "
                f"ON HOLD, do not publish: docs/DEPLOY_HOLD.md")
    return (f"site: {rep.behind_total} commits behind {rep.ref} ({what}) — "
            f"deploy it: docs/deploy.md")


def render_text(rep: Report) -> str:
    out = [f"{rep.base}   vs   {rep.ref or '(no git ref)'} "
           f"{rep.ref_sha} {rep.ref_subject}".rstrip(), ""]
    if not rep.reachable:
        out += [f"  COULD NOT REACH THE SITE — {rep.problem}", ""]
        if rep.last_seen:
            out.append(f"  The last successful read, {rep.last_seen_age_min / 60:.0f}h "
                       f"ago, found {rep.last_seen}. That is history, not status.")
        out += ["  This is not evidence the site is current. It is evidence this",
                "  machine could not look. Try again on a network, or check the",
                "  host; nothing has been established either way.",
                ""]
        return "\n".join(out)

    if rep.stamp:
        where = ("on " + str(rep.ref)) if rep.stamp_on_ref else (
            "NOT an ancestor of " + str(rep.ref) if rep.stamp_known
            else "unknown to this clone — git fetch, or it was deployed unpushed")
        out.append(f"  built from   {rep.stamp}  {rep.stamp_subject}"
                   f"{'  ' + rep.stamp_date[:10] if rep.stamp_date else ''}")
        out.append(f"               ({where})")
    else:
        out.append("  built from   (no build stamp in the served index.html)")

    if rep.viewer_matched:
        out.append(f"  viewer.html  matches {VIEWER_SOURCE} at "
                   f"{rep.viewer_sha}  {rep.viewer_subject}")
    else:
        out += ["  viewer.html  MATCHES NO COMMITTED VERSION of "
                f"{VIEWER_SOURCE}.",
                "               Either the deploy ran from an unpushed tree, or the",
                "               edge is rewriting the HTML — that happened here on",
                "               2026-08-18. tools/audit_deployed_page.py is the tool",
                "               that can tell those apart; it drives a real browser."]
    out.append("")

    if rep.status == "unknown":
        out += ["  VERDICT: unknown. Nothing served could be tied to a commit, so no",
                "  distance can be quoted. This is not 'up to date'.", ""]
        return "\n".join(out)

    if rep.status == "current":
        out += [f"  VERDICT: current. {rep.behind_total} commits have landed since the",
                "  deploy and none of them changes what the site serves.", ""]
        return "\n".join(out)

    out.append(f"  VERDICT: behind by {rep.behind_total} commits, "
               f"{len(rep.behind_pages)} of which change what it serves:")
    out.append("")
    for sha, subject in rep.behind_pages:
        mark = "viewer" if any(sha == v for v, _ in rep.viewer_behind) else "      "
        out.append(f"    {mark}  {sha}  {subject}")
    held = deploy_hold()
    if held:
        out += ["",
                "  ON HOLD — do not publish. This gap is queued on purpose.",
                "",
                f"    releases when: {held}",
                "",
                "  docs/DEPLOY_HOLD.md has the reason and how to lift it. Lifting it",
                "  is a decision somebody makes and records, not something to route",
                "  around because the number above looks large.",
                ""]
    else:
        out += ["",
                "  Publish it (docs/deploy.md — needs the wrangler login on this machine):",
                "",
                "    PATH=$PWD/.venv/bin:$PATH npm run deploy",
                "    python tools/audit_deployed_page.py",
                "",
                "  Nothing here can do that for you: deploying needs a Cloudflare",
                "  credential, and this check deliberately holds none.",
                ""]
    if rep.behind_total > len(rep.behind_pages):
        out += ["  (The other commits touch code, docs or tests that the build does not",
                "   read. One caveat: hero.png is rendered from src/bugarach, so a",
                "   detector change can move the published picture without appearing",
                "   above.)", ""]
    return "\n".join(out)


def render_markdown(rep: Report) -> str:
    head = {"current": "### Site is current",
            "behind": f"### Site is {rep.behind_total} commits behind `{rep.ref}`",
            "unknown": "### Site staleness could not be determined"}[rep.status]
    body = ["", head, "",
            f"`{rep.base}` — checked {rep.checked_at}", ""]
    if not rep.reachable:
        body += [f"**Could not reach the site.** `{rep.problem}`", "",
                 "Nothing was established about the published page. This run "
                 "is not a clean bill of health for it — the check could not "
                 "look.", ""]
        return "\n".join(body)
    body += [f"- build stamp: `{rep.stamp or 'absent'}` "
             f"{rep.stamp_subject}".rstrip(),
             f"- served viewer matches: "
             f"{'`' + rep.viewer_sha + '` ' + rep.viewer_subject if rep.viewer_matched else '**no committed version**'}",
             ""]
    if rep.behind_pages:
        body += ["Commits that change what the site serves:", ""]
        body += [f"- `{sha}` {subject}" for sha, subject in rep.behind_pages]
        held = deploy_hold()
        if held:
            body += ["", f"**On hold — do not publish.** Releases when: {held}. "
                     "See `docs/DEPLOY_HOLD.md`.", ""]
        else:
            body += ["", "Publishing is manual (`npm run deploy`, see `docs/deploy.md`) "
                     "because nothing in CI holds a Cloudflare credential.", ""]
    return "\n".join(body)


# ---------------------------------------------------------------------------- cli


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=os.environ.get("BUGARACH_SITE_URL", DEFAULT_BASE),
                    help="base URL of the deployed site")
    ap.add_argument("--ref", default=None,
                    help="git ref the site should match (default: origin/main, else HEAD)")
    ap.add_argument("--timeout", type=float, default=10.0, help="seconds per request")
    ap.add_argument("--brief", action="store_true",
                    help="one line, cached — what the session briefing prints")
    ap.add_argument("--format", choices=("text", "github"), default="text")
    ap.add_argument("--cache-ttl", type=float, default=360.0,
                    help="minutes an observation stays usable in --brief (0 disables)")
    ap.add_argument("--exit-zero", action="store_true",
                    help="always exit 0 — for callers that must not go red")
    args = ap.parse_args(argv)

    if args.brief:
        # A session-start hook that blocks on the network is a session-start hook
        # somebody disables. Short timeout, and a cached observation is preferred
        # to a fresh one within the TTL.
        if args.timeout > 4.0:
            args.timeout = 3.0
        blob = cache_read(args.url, args.cache_ttl) if args.cache_ttl > 0 else None
        rep = from_cache(blob, args.ref) if blob else collect(args.url, args.ref, args.timeout)
        if not blob:
            cache_write(rep)
        print(render_brief(rep))
        return 0 if args.exit_zero else rep.exit_code

    rep = collect(args.url, args.ref, args.timeout)
    cache_write(rep)
    print(render_markdown(rep) if args.format == "github" else render_text(rep))
    return 0 if args.exit_zero else rep.exit_code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(2)
