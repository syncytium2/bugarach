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
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

INDEX = """<!doctype html>
<meta charset="utf-8">
<title>bugarach — coordinated-event detection</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font: 16px/1.65 system-ui, sans-serif; max-width: 46rem;
         margin: 2.2rem auto 3rem; padding: 0 1.2rem; }}
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
  .note {{ border-left:3px solid #e8a33d; padding:.4rem 0 .4rem .9rem;
           color:#555; font-size:.94rem; }}
</style>

<h1>bugarach</h1>
<p class="sub">Six coordinated-event detectors, ported from MATLAB to Python —
and a synthetic benchmark with planted ground truth to test them against.</p>

{real}

<p><b>A model trained across everyone's recordings learns what is usually true —
and what is usually true is the textbook.</b> The results worth having are often
the ones where a preparation departs from it, and those are exactly the ones such
a model scores as noise: confidently, and with no way for the recording to answer
back. An instrument built from the average of other people's tissue cannot be
trusted to report what is unusual about yours.</p>

<p>So nothing here is trained on a treatment. Measure the coordination
parameters of an <i>untreated</i> recording, simulate from those alone, and let
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

<p style="margin-top:2rem;color:#666;font-size:.9rem">
  Source: <a href="https://github.com/syncytium2/bugarach">github.com/syncytium2/bugarach</a>
  · BSD-3-Clause · built from <code>{commit}</code>
</p>
"""

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
       alt="Two rasters stacked. Top, a real recording: most rows nearly empty,
            a few dense, activity arriving in bursts. Bottom, the generated
            imitation: events spread evenly across every row and all 30 minutes.">
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
        INDEX.format(commit=commit, lead=lead, real=real), encoding="utf-8")

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
