#!/usr/bin/env python3
"""Build the static site served at bugarach.tonydefazio.com.

    python tools/build_site.py            # -> ./site
    python tools/build_site.py --open     # ...and print the file:// URL

Everything here is generated from a seed. **The build reads no store and no
real data**: FOUNDATIONS §5 keeps real recordings machine-local behind
``BUGARACH_DATA_ROOT``, and this site is public. A build that quietly picked up
a real slice would be a data-policy breach, so it has no code path that could.

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

{lead}

<p>Detectors flag moments when many neurons fire together in 2-photon calcium
recordings. Six of them, each asking a different question, each matched to its
MATLAB original to 1e-9 so it can be cited in its place. The figure above is
them run against <b>simulated data where the right answer is known</b> — so a
miss and a false alarm are drawn, not inferred.</p>

<p class="note"><b>Everything here is synthetic.</b> Real recordings stay
machine-local and never reach this site. Every figure on this page is generated
from a seed, so the whole thing is reproducible with one command:
<code>python tools/build_site.py</code>.</p>

<h2 style="font-size:1.15rem">What the benchmark is for</h2>
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
  made of it.</b> Top: one lane per detector, each bar a call it made.
  Middle: the raster every one of them was reading — one row per ROI.
  Bottom: what each detector actually computes.
  The <span class="key">shaded block</span> fires at a higher rate but contains
  <b>no planted events</b>, so every bar inside it is a false alarm by
  construction — you can see which detectors take the bait.
  <a href="diagnostic.html">Open the interactive version &rarr;</a></figcaption>
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
    (SITE / "index.html").write_text(INDEX.format(commit=commit, lead=lead),
                                     encoding="utf-8")

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
