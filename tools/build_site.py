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
         margin: 3rem auto; padding: 0 1.2rem; }}
  h1 {{ font-size: 1.6rem; margin-bottom: .2rem; }}
  .sub {{ color: #666; margin-top: 0; }}
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

<p>Detectors flag moments when many neurons fire together in 2-photon calcium
recordings. Six of them, each asking a different question, each matched to its
MATLAB original to 1e-9 so it can be cited in its place. This page shows them
run against <b>simulated data where the right answer is known</b>.</p>

<a class="card" href="diagnostic.html">
  <b>Detector diagnostic &rarr;</b>
  <span>Detector lanes over an ROI raster, with the planted events marked.
  Hits, misses and false alarms are drawn, not inferred.</span>
</a>

<p class="note"><b>Everything here is synthetic.</b> Real recordings stay
machine-local and never reach this site. The data below is generated from a
seed, so the whole page is reproducible with one command:
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

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip() or "unknown"
    (SITE / "index.html").write_text(INDEX.format(commit=commit), encoding="utf-8")

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
