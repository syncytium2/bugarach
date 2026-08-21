#!/usr/bin/env python3
"""Does the DEPLOYED viewer still reach nothing?

    python tools/audit_deployed_page.py                     # the live site
    python tools/audit_deployed_page.py --url http://…      # a preview

Exit 0 when the page fetched nothing but itself, 1 when it fetched anything else,
so it drops into a deploy step.

**Every other check in this repo reads what we wrote.** `tests/test_site_viewer.py`
greps the source for `fetch(` and friends; `tools/build_site.py` refuses to publish
a viewer containing them. Both are properties of the file, and on 2026-08-18 the
served page had two network calls anyway: Cloudflare Web Analytics rewrites HTML at
the edge and injected a beacon into the one page that promises it makes none. The
file was clean the whole time.

So this drives the deployed URL in a real browser and records every request the
page makes. Nothing before the upload can see what a CDN adds after it.

⚠ **A plain `curl` cannot do this job.** The injection was conditional on the
request looking like a browser, so `curl` received the file we wrote and reported
clean — the obvious audit returning the answer we wanted to hear. That is the
reason this drives chromium instead of fetching.

Needs `playwright` and its chromium, the same one the figures use. Not a pytest:
CI has no business fetching production, and a test that needs the network is a test
that fails for reasons that are not about this repo.
"""

from __future__ import annotations

import argparse
import sys
from urllib.parse import urlparse

DEFAULT_URL = "https://bugarach.tonydefazio.com/viewer.html"


def audit(url: str, *, timeout_ms: int = 30000):
    """Return every request the page made, split into own-origin and foreign."""
    from playwright.sync_api import sync_playwright

    seen: list[str] = []
    host = urlparse(url).netloc
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.on("request", lambda r: seen.append(r.url))
        page.goto(url, timeout=timeout_ms)
        page.wait_for_timeout(2500)
        # exercise it too: an injected script can be lazy, and the simulator is
        # the one path that runs a lot of code after load
        try:
            page.click("#simCta", timeout=5000)
            page.wait_for_selector("#view:not([hidden])", timeout=timeout_ms)
            page.wait_for_timeout(1500)
        except Exception as exc:                    # noqa: BLE001 — reported, not raised
            print(f"note: could not drive the simulator ({exc.__class__.__name__}); "
                  f"the load-time audit below still stands", file=sys.stderr)
        scripts = page.eval_on_selector_all("script[src]", "ns => ns.map(n => n.src)")
        browser.close()

    # /cdn-cgi/ is same-host and still not ours: it is the edge's own endpoint,
    # which is exactly how the beacon reported back
    foreign = [u for u in seen
               if urlparse(u).netloc != host or "/cdn-cgi/" in u]
    own = [u for u in seen if u not in foreign]
    return own, foreign, scripts


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=DEFAULT_URL)
    args = ap.parse_args(argv)

    try:
        own, foreign, scripts = audit(args.url)
    except ImportError:
        # Exit 0: "could not check" is not "checked and clean", but it is also not
        # a reason to fail a deploy on a box without chromium — the build degrades
        # the same way for hero.png. It says so at volume instead, because a check
        # that skips silently is the one nobody notices has stopped running.
        print("audit: SKIPPED — no playwright here, so the deployed page was NOT "
              "checked. pip install playwright && python -m playwright install "
              "chromium to get the check back.", file=sys.stderr)
        return 0

    print(f"{args.url}\n")
    for u in own:
        print(f"  ok   {u}")
    if scripts:
        print()
        for s in scripts:
            print(f"  script  {s}")

    if not foreign:
        print("\nThe page fetched nothing but itself. The promise on it holds as "
              "served, not merely as written.")
        return 0

    print("\n  !! the page reached these, and it tells its readers it reaches "
          "nothing:", file=sys.stderr)
    for u in foreign:
        print(f"     {u}", file=sys.stderr)
    print("\nEither stop whatever is adding them — an edge feature injecting into "
          "HTML is the way this happened before, and no change in this repo can "
          "express it — or take the claim off the page. Not both.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
