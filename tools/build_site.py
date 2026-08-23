#!/usr/bin/env python3
"""Build the static site served at bugarach.tonydefazio.com.

    python tools/build_site.py            # -> ./site
    python tools/build_site.py --open     # ...and print the file:// URL

**The build still reads no store.** Every figure it generates comes from a seed,
and there is no code path here that opens ``BUGARACH_DATA_ROOT`` — FOUNDATIONS §5
keeps real recordings machine-local and this site is public.

The one exception is carried, not read: ``docs/generator/reality_check.png`` is a
committed figure that contains a real baseline recording, released by name under
the §5 carve-out (Tony, 2026-08-15 — that slice is baseline-only, and this lab's
results are all baseline-vs-treatment, so it can never carry one). The build
copies that file. It does not regenerate it, which is why a clean clone with no
data still builds the whole site.

Output is an assets-only Cloudflare Worker payload (``wrangler.jsonc`` points at
``./site``) — the same shape colonel_kernel uses. No server, nothing to sleep.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# Every way a page can talk to a host, including the ones that do not look like a
# request. Kept here, next to the build that refuses on them, and imported by
# tests/test_site_viewer.py so the two can never drift into disagreeing about what
# counts as reaching the network.
NETWORK = (
    "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket(", "EventSource(",
    "import(", '<script src', '<link rel="stylesheet"', "<iframe", "<img",
    "@import",
)


def viewer_network_leaks(body: str) -> list[str]:
    """The network primitives a page actually uses, ignoring the ones it discusses.

    COMMENTS ARE STRIPPED FIRST, and that is the whole point of this function.
    The viewer's header promises the reader "there is no fetch(), no XHR", and a
    note further down explains why the page builds nodes instead of markup, quoting
    an `<img` injection to show what it is avoiding. Both are prose. A scan that
    reads them as code fires on the explanation of why it will never fire.

    **Do not cite a particular comment here.** This paragraph used to quote one
    reading "contains no `fetch(` and must not grow one". It was reworded three
    commits later, and both this docstring and the test that counted its occurrences
    went stale together — `main` turned red over a rephrasing, with nothing about
    the page's safety changed. The property is that prose about network primitives
    exists and gets stripped, never which sentence happens to carry it.

    That is not hypothetical. The old scan neutralised exactly one phrase — the
    promise in the header — and missed the comment beside the lab panel. From the
    day that comment was written the build refused every run, so the published site
    froze 233 lines behind `main`, missing SCE and CoactDetect in the browser, and
    nothing said so out loud: a build that exits 1 in a terminal nobody is watching
    looks exactly like a build nobody ran. The guard was correct about the property
    and wrong about the evidence, which is the failure mode that gets real guards
    deleted rather than fixed.

    Stripping comments cannot hide a real call: a call outside a comment is still
    there afterwards, and one inside a comment does not run.
    """
    return [w for w in NETWORK if w in strip_comments(body)]


def strip_comments(text: str) -> str:
    """The page with HTML and JS comments blanked, for any check that reads code.

    The line-comment pattern is anchored to the start of a line on purpose: an
    unanchored `//` would eat the rest of a line containing a URL, and with it any
    real call sitting after it. Blanking to a space rather than deleting keeps
    tokens from being glued together across the removal.
    """
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)        # HTML
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)         # JS block
    return re.sub(r"^\s*//[^\n]*", " ", text, flags=re.M)      # JS line

INDEX = """<!doctype html>
<meta charset="utf-8">
<title>bugarach — coordinated-event detection</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font: 16px/1.65 system-ui, sans-serif; margin: 0; }}
  .col {{ max-width: 46rem; margin: 2.2rem auto 3rem; padding: 0 1.2rem; }}
  h1 {{ font-size: 1.6rem; margin-bottom: .2rem; }}
  .sub {{ color: #666; margin-top: 0; }}
  /* the figure breaks out of the text column: it is the lead, not an
     illustration slotted into the prose. */
  figure.lead {{ width: min(94vw, 78rem); margin: 1.6rem 0 1.9rem 50%;
                 transform: translateX(-50%); }}
  figure.lead img {{ display:block; width:100%; height:auto;
                     border:1px solid #8883; border-radius:10px; }}
  figure.lead a {{ display:block; text-decoration:none; }}
  figure.lead a:hover img {{ border-color:#888; }}
  figcaption {{ color:#666; font-size:.92rem; margin-top:.55rem;
                max-width: 46rem; margin-left:auto; margin-right:auto; }}
  .key {{ white-space:nowrap; font-weight:600; }}
  a.card {{ display:block; border:1px solid #8884; border-radius:10px;
            padding: .9rem 1.1rem; margin: .7rem 0; text-decoration:none;
            color:inherit; }}
  a.card:hover {{ border-color:#888; background:#8881; }}
  .card b {{ display:block; font-size:1.05rem; }}
  .card span {{ color:#666; font-size:.92rem; }}
  code {{ background:#8881; padding:.1rem .35rem; border-radius:4px; }}
  /* Site nav, first thing on the page — the viewer used to be reachable only by
     scrolling past every paragraph below, which is a good way to publish a tool
     nobody finds. */
  /* full-bleed bar, links still starting at the text column's left edge — the
     body is a 46rem column and a nav indented with it reads as a paragraph */
  nav.site {{ display:flex; align-items:center; gap:4px; flex-wrap:wrap;
              padding:.55rem max(1.2rem, calc(50% - 23rem));
              border-bottom:1px solid #8883; font-size:.88rem; }}
  nav.site .brand {{ font-weight:600; margin-right:.6rem; }}
  nav.site a {{ color:#666; text-decoration:none; padding:.25rem .55rem;
                border-radius:6px; }}
  nav.site a:hover {{ background:#8881; color:inherit; }}
  nav.site a[aria-current="page"] {{ color:inherit; background:#8881; }}
  .note {{ border-left:3px solid #e8a33d; padding:.4rem 0 .4rem .9rem;
           color:#555; font-size:.94rem; }}
</style>

<nav class="site">
  <span class="brand">bugarach</span>
  <a href="index.html" aria-current="page">Overview</a>
  <a href="viewer.html">Raster viewer</a>
  <a href="diagnostic.html">Detector diagnostic</a>
  <a href="landscape.html">Landscape</a>
</nav>

<div class="col">
<h1>bugarach</h1>
<p class="sub">Six coordinated-event detectors, ported from MATLAB to Python —
and a synthetic benchmark with planted ground truth to test them against.</p>

{real}

<p><b>Coordination is not one phenomenon, so there is no one detector to train.</b>
Stars coordinate and cells coordinate, and between them the timescales run over
many orders of magnitude — along with the sampling rates, the mechanisms, and
what even counts as an event. A network trained across every source of
coordination spends its capacity on a space in which almost nothing transfers,
and comes out mediocre at all of it. Worse for a working lab: what it learns is
the average case, so the preparation that departs from the average is the one it
scores as noise.</p>

<p><b>So the instrument gets built for your recordings, not for coordination in
general.</b> Measure the coordination parameters of an <i>untreated</i>
recording, simulate from those alone, and let
that synthetic baseline do two jobs at once: tune the six detectors, and train
the model. Only then is the finished instrument pointed at the whole dataset,
treatments included. Simulate the treatment and you have spent the effect you
ran the experiment to measure; withhold it and it comes back as a result. The
detectors and the generator below are built and tested; <b>the training half is
the plan, not yet the practice</b>.</p>

<p>Each row above is one <b>ROI</b> — one cell's worth of signal pulled out of a
2-photon calcium recording. Detectors flag the moments when many of them fire
together. There are six here — LoCo, CICADA, SCE, CoactDetect, RateDetect and
SPIKE-synch — each asking a different question, and each matched to its MATLAB
original to 1e-9 on committed fixtures, so it can be cited in its place.</p>

<p>All six work by finding moments that stand out from the rest of the
recording, which is what makes the shape of the background more than a cosmetic
detail: on the pair above, the same detector at the same settings finds
<b>twice as many</b> coordinated events in the imitation as in the original.
Matching the rate, the jitter and the participation is necessary and not
sufficient. That gap is open work, and it is written down rather than papered
over.</p>

<p class="note"><b>One real recording; everything else is synthetic.</b> The top
panel above is a real baseline-only slice, published deliberately — it carries no
before/after result, so releasing it costs nothing this lab intends to publish.
It is a committed figure rather than a live read: the build opens no data store,
and generates every other figure here from a seed.</p>

<h2 style="font-size:1.15rem">What it cost to get this wrong</h2>
<p>Tuning a detector against a synthetic benchmark that does not match reality
is not a hypothetical failure here — it happened, and cost two weeks. Settings
tuned on a benchmark with events every 14&nbsp;s collapsed when run on sparse
data, because four planted events sat inside every 60&nbsp;s context window and
contaminated the null the detectors depend on. Precision fell from 74% to 10%
for one of them.</p>
<p>So the generator carries the things that catch that: a
<b>dense-but-random block</b> containing no planted events (a detector fooled by
rate lights it up), <b>correlated bursts</b> that are real coincidence but not
coordination, and <b>variable event timing</b>, so nothing can be predicted from
the clock.</p>

<h2 style="font-size:1.15rem">What the detectors do with a known answer</h2>
<p>That is what the generator is <i>for</i>. Every coordinated event below was
planted, so a miss and a false alarm are drawn, not inferred.</p>

{lead}

<h2 style="font-size:1.15rem">Where this sits, and who else is doing it</h2>
<p>Detecting coordinated events is not a new problem, and a page that positions
itself against work a reader cannot go and look at is marketing. So: three
groups already train networks whose output is a population event with times —
<a href="https://github.com/Dreem-Organization/dosed">DOSED</a> on sleep EEG,
<a href="https://github.com/PridaLab/cnn-ripple">cnn-ripple</a> on hippocampal
LFP, and SEED on sleep spindles. None of them works on calcium imaging, and all
of them learn from events a human expert labelled. What is different here is the
substrate and where the answers come from — the events are planted in a
simulation fitted to one lab's own recordings, so the ground truth is exact and
the benchmark is rebuilt per lab.</p>
<p>The classical side of the same problem is
<a href="https://gitlab.com/cossartlab/cicada">CICADA</a> and the coactivity-vs-shuffle
rule it comes from, both of which are among the six detectors this project ports
and scores against.
<b>No method from the literature has yet been run on this project's corpus</b>, so
nothing here claims to beat one.</p>
<p><a href="landscape.html">The full landscape &rarr;</a> — what a dozen methods
emit, whether they learned it, and what that leaves this work entitled to claim.</p>

<h2>Open your own recordings</h2>
<p><a href="viewer.html">The raster viewer &rarr;</a> — point it at a folder of
event times and it draws them. It reads the
<a href="https://github.com/syncytium2/bugarach/blob/main/docs/export_folder_spec.md">import
contract</a>: one CSV per recording with <code>roi</code> and <code>time_sec</code>,
which most labs can write from whatever their detector already produces.
<b>Your files never leave your computer</b> — the page has no network call in it,
and this site is static files with no server to receive anything. Nothing is
installed and nothing is uploaded.</p>

<p><b>No recordings to hand?</b> The same page will invent a folder — event times
drawn from the generator described above, written as the contract describes and
read back through the same loader, so what you drive is the viewer rather than a
demonstration of it. It opens at the measured settings: about six of thirty-three
ROIs per coordinated event, a third of a second of spread, and a background whose
quiet tail is the fitted one. The guesses those replaced are left on the switches,
because the difference is worth seeing. Its treatment windows are
<b>labels over identical statistics</b> — simulating an effect would spend the one
the experiment exists to measure.</p>

<p style="margin-top:2rem;color:#666;font-size:.9rem">
  Source: <a href="https://github.com/syncytium2/bugarach">github.com/syncytium2/bugarach</a>
  · BSD-3-Clause · built from <code>{commit}</code>
</p>
</div>
"""

SITE_BORN = "2026-08-13"
"""The day this site first existed, and it does not move.

`f84e8d2`, *"Static site for bugarach.tonydefazio.com, on the existing Worker
pattern"*. Written down rather than derived at build time on purpose: a born-on
date computed from `git log --reverse` over a path silently resets the day
somebody renames a directory, and a first-published date that quietly becomes
last Tuesday is worse than none — it is the same class of error as a fabricated
frame interval, which this project has already been bitten by.

A reader uses the pair. The born-on date says how long the thing has existed;
the version date says whether what they are reading is current. Either alone
invites the wrong inference.
"""


def _stamp_dates(commit: str) -> tuple[str, str]:
    """(born, version) as ISO dates, for the footer of every page.

    The version date is the **committer date of the commit being built**, not
    the wall clock. Two builds of one commit must produce identical bytes:
    `tests/test_lab_server.py` pins the viewer copy that way, the site-staleness
    check identifies the deployed version by hashing what is served, and a
    timestamp that advances on every rebuild would break both while telling a
    reader nothing they did not already know from the sha.
    """
    out = subprocess.run(["git", "log", "-1", "--format=%cs", commit], cwd=ROOT,
                         capture_output=True, text=True)
    version = out.stdout.strip() if out.returncode == 0 else ""
    if not version:
        # Degrade loudly. A stamp reading "unknown" is honest; one silently
        # showing the born-on date twice would say the page had never changed.
        print("build_site: could not read the commit date — the pages will say "
              "so rather than guess. A shallow clone does this.", file=sys.stderr)
        version = "unknown"
    return SITE_BORN, version


STAMP_MARKER = "data-bugarach-born"
"""What proves a page carries its dates.

It lives on the visible element, not on a `<meta>`, because half this site's
pages have no `<head>` to put a meta in — `index.html` and `landscape.html` are
HTML5 without explicit `html`/`head`/`body` tags. The first version of this check
looked for the meta and reported those two pages unstamped when they were fine,
which is the right failure to have had: a marker that only exists on some page
shapes cannot verify all of them.
"""


def date_stamp(commit: str) -> str:
    """The visible footer line, identical on every page, and self-describing.

    Carries the three facts as data attributes as well as prose. Anything asking
    whether a deployed page is current — `tools/site_staleness.py` today — can
    then read them off any page instead of parsing English out of the one footer
    that happened to be hand-written.
    """
    born, version = _stamp_dates(commit)
    return (f'<p class="site-dates" {STAMP_MARKER}="{born}"'
            f' data-bugarach-version-date="{version}"'
            f' data-bugarach-commit="{commit}"'
            f' style="margin:1.5rem max(1.2rem, calc(50% - 23rem));'
            f'color:#666;font-size:.85rem">\n'
            f'  First published {born} · this version {version}'
            f' (<code>{commit}</code>)\n</p>\n')


def meta_stamp(commit: str) -> str:
    """The same three facts in `<head>`, for the pages that have one."""
    born, version = _stamp_dates(commit)
    return (f'<meta name="bugarach:born" content="{born}">\n'
            f'<meta name="bugarach:version-date" content="{version}">\n'
            f'<meta name="bugarach:commit" content="{commit}">\n')


def stamp_html(body: str, commit: str) -> str:
    """Put the dates into a finished page, whatever shape it is.

    Insertion is by anchor with a fallback rather than by assuming a shape:
    `landscape.html` and `diagnostic.html` are produced by other tools and their
    structure is not this file's to guarantee. Re-stamping is a no-op, so a
    rebuild over an existing `site/` does not accumulate footers.
    """
    if STAMP_MARKER in body:
        return body
    if "</head>" in body:
        body = body.replace("</head>", meta_stamp(commit) + "</head>", 1)
    if "</body>" in body:
        return body.replace("</body>", date_stamp(commit) + "</body>", 1)
    return body + "\n" + date_stamp(commit)

# The page leads with the figure. If the flat render could not be made — no
# playwright chromium — it leads with a link to the interactive one instead of
# a broken image, and says so on stderr. A public page with a missing <img> is
# worse than a public page with one fewer picture.
LEAD_FIGURE = """<figure class="lead">
  <a href="diagnostic.html" title="Open the interactive version — zoom and pan the same figure">
    <img src="hero.png" width="{w}" height="{h}"
         alt="Six detector lanes above a 30-ROI raster and six analysis traces.
              Each lane marks where that detector called a coordinated event;
              the shaded block is a dense-but-random stretch containing none.">
  </a>
  <figcaption><b>Thirty minutes of simulated recording, and what six detectors
  made of it.</b> One lane per detector, each bar a call it made; then the raster
  all six were reading, one row per ROI; then what each detector computes.
  Each lane carries its detector's own name; two of the six are named for what
  they measure rather than for the tool — <span class="key">rate+context</span>
  is RateDetect, and <span class="key">binned SCE</span> is SCE.
  In the lanes, <span class="key">&#10007;</span> marks a false alarm and
  <span class="key">&#9711;</span> a second call on an event another detection
  had already claimed. The top lane is the ground truth:
  <span class="key">&#9650;</span> an event some detector recovered,
  <span class="key">&#9660;</span> one they all missed.
  The <span class="key">shaded block</span> fires at a higher rate but contains
  <b>no planted events</b>, so every bar inside it is a false alarm by
  construction — you can see which detectors take the bait.
  <a href="diagnostic.html">Open the interactive version &rarr;</a></figcaption>
</figure>"""

# The real recording. Carried from docs/, never regenerated here — see the module
# docstring for why that distinction is the whole reason a clean clone can build
# this page. Its numbers (5 events found above, 10 below) are printed inside the
# image itself, so quoting them in the caption cannot drift away from the figure.
LEAD_REAL = """<figure class="lead">
  <img src="reality.png" width="{w}" height="{h}"
       alt="Two rasters stacked, each with a lane above it carrying LoCo's calls.
            Top, a real recording: most rows nearly empty, a few dense, activity
            arriving in bursts. Bottom, the generated imitation: events spread
            evenly across every row and all 30 minutes, with the planted events
            marked in its lane.">
  <figcaption><b>The match is in the numbers, not in the shape.</b> The ROI
  count, the duration, the per-ROI rate, the participation and the jitter are
  the same above and below. The texture is not: a real field has a few ROIs
  carrying most of the activity and many carrying almost none, and what activity
  there is arrives in bursts, while the generator spreads events evenly — across
  every ROI, and across the whole recording.</figcaption>
</figure>"""

LEAD_FALLBACK = """<a class="card" href="diagnostic.html">
  <b>Detector diagnostic &rarr;</b>
  <span>Detector lanes over an ROI raster, with the planted events marked.
  Hits, misses and false alarms are drawn, not inferred.</span>
</a>"""


def _png_size(path: Path) -> tuple[int, int] | None:
    """Width/height straight out of the IHDR chunk.

    Stating them on the <img> keeps the page from reflowing once a 900 KB
    render arrives, and it costs 24 bytes of file to read — not a Pillow
    dependency for the site build.
    """
    try:
        head = path.read_bytes()[:24]
    except OSError:
        return None
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--duration", type=float, default=1800.0)
    args = ap.parse_args(argv)

    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)

    # The diagnostic writes straight into the site payload. --out keeps it out
    # of the darkroom: the published copy and the review copy are different
    # artifacts with different audiences.
    cmd = [sys.executable, str(ROOT / "tools" / "make_diagnostic.py"),
           "--out", str(SITE), "--tag", "site",
           "--hero", str(SITE / "hero.png"),
           "--seed", str(args.seed), "--duration", str(args.duration)]
    print("$", " ".join(cmd))
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        print("build_site: the diagnostic failed to build", file=sys.stderr)
        return 1

    (SITE / "coord_diagnostic_site.html").rename(SITE / "diagnostic.html")
    for stray in ("coord_diagnostic_site.png", "coord_diagnostic_site.txt"):
        p = SITE / stray
        if p.exists():
            p.rename(SITE / stray.replace("coord_diagnostic_site", "diagnostic"))

    # The real-recording figure is committed, so this is a copy and not a build —
    # which is what lets a clone with no data store build the whole page. Its
    # absence is a broken tree, not a degraded environment, and three paragraphs
    # of this page describe it by name. Refuse rather than publish prose about a
    # picture that is not there.
    src = ROOT / "docs" / "generator" / "reality_check.png"
    if not src.exists():
        print(f"build_site: {src.relative_to(ROOT)} is missing. The page leads "
              f"with that figure and its text describes it, so this is a build "
              f"failure, not something to ship without.", file=sys.stderr)
        return 1
    shutil.copyfile(src, SITE / "reality.png")

    # The landscape page is a self-contained single file, so publishing it is a
    # copy. It has to travel: the page above links to it, and the coordination
    # report's retraction points at it too — a relative href to a file that was
    # not shipped is a dead end where the correction should be.
    land = ROOT / "docs" / "learned" / "landscape.html"
    if not land.exists():
        print(f"build_site: {land.relative_to(ROOT)} is missing, and the page "
              f"links to it. Run tools/build_learned_report.py on "
              f"landscape.src.html first.", file=sys.stderr)
        return 1
    shutil.copyfile(land, SITE / "landscape.html")

    # The raster viewer is hand-written and self-contained, so publishing it is
    # a copy too. IT SHIPS NO DATA AND CANNOT: there is no network call in it,
    # and the recording it draws is whichever folder the reader opens from their
    # own disk. That is what lets a page which reads real recordings sit on a
    # public site with §5 having nothing to say about it — the repo publishes an
    # empty reader, not a recording.
    viewer = ROOT / "docs" / "site" / "raster_viewer.html"
    if not viewer.exists():
        print(f"build_site: {viewer.relative_to(ROOT)} is missing, and the "
              f"index links to it.", file=sys.stderr)
        return 1
    body = viewer.read_text(encoding="utf-8")
    # The privacy line on that page is a property of its code, so it is checked
    # here rather than believed. A page that fetches is a page that could send.
    leaks = viewer_network_leaks(body)
    if leaks:
        print(f"build_site: the viewer page contains {', '.join(leaks)}. It tells "
              f"the reader their files never leave their computer, and that is "
              f"only true while this page reaches nothing.", file=sys.stderr)
        return 1
    shutil.copyfile(viewer, SITE / "viewer.html")

    real_size = _png_size(SITE / "reality.png")
    if real_size is None:
        print(f"build_site: {src.relative_to(ROOT)} is not a readable PNG.",
              file=sys.stderr)
        return 1
    real = LEAD_REAL.format(w=real_size[0], h=real_size[1])

    size = _png_size(SITE / "hero.png")
    if size:
        lead = LEAD_FIGURE.format(w=size[0], h=size[1])
    else:
        lead = LEAD_FALLBACK
        print("build_site: no hero.png — the page falls back to a link instead "
              "of leading with the figure. Install playwright chromium to get "
              "the picture back.", file=sys.stderr)

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip() or "unknown"
    (SITE / "index.html").write_text(
        stamp_html(INDEX.format(commit=commit, lead=lead, real=real), commit),
        encoding="utf-8")

    # EVERY page carries the pair, not just the one with a hand-written footer.
    # A reader who arrives on the viewer — which is the page the README sends
    # people to — was previously given no way at all to tell whether they were
    # looking at this month's build or February's.
    #
    # `viewer.html` is the exception and it is deliberate: it is a byte-for-byte
    # copy of a hand-written page, pinned that way by
    # `tests/test_lab_server.py::test_the_built_viewer_is_the_source_viewer` so
    # that the build cannot quietly transform a page that promises the reader it
    # reaches nothing. Its stamp belongs in the source page, where a reader can
    # audit it, not injected here where the guard would have to be loosened to
    # allow it.
    for page in ("landscape.html", "diagnostic.html"):
        p = SITE / page
        if not p.is_file():
            continue
        p.write_text(stamp_html(p.read_text(encoding="utf-8"), commit),
                     encoding="utf-8")

    unstamped = [p.name for p in sorted(SITE.glob("*.html"))
                 if p.name != "viewer.html"
                 and STAMP_MARKER not in p.read_text(encoding="utf-8")]
    if unstamped:
        print(f"build_site: no date stamp reached {', '.join(unstamped)} — a "
              f"published page with no born-on date and no version date is the "
              f"thing this stamp exists to prevent. Check the insertion anchors "
              f"in stamp_html().", file=sys.stderr)

    total = sum(f.stat().st_size for f in SITE.rglob("*") if f.is_file())
    print(f"\nsite/ built — {total/1024:.0f} KB")
    for f in sorted(SITE.rglob("*")):
        if f.is_file():
            print(f"  {f.relative_to(SITE)}  ({f.stat().st_size/1024:.0f} KB)")
    print(f"\nlocal:  {(SITE / 'index.html').as_uri()}")
    print("deploy: npx wrangler deploy      (needs node; see docs/deploy.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
