---
status: open
opened: 2026-08-18
area: site
needs: a Cloudflare dashboard toggle — not fixable from this repo
---

# Cloudflare injects an analytics beacon into the one page that promises none

The raster viewer tells whoever opens it:

> **Your files never leave this computer:** the page has no network calls in it, and
> the site is static files with no server to send anything to.

`tests/test_site_viewer.py` proves that of the **file**, and `tools/build_site.py`
refuses to publish it otherwise. Both are checks on what we wrote. What Cloudflare
**serves** is not what we wrote:

```
script tags in the live DOM:
  https://static.cloudflareinsights.com/beacon.min.js/v4513226cdae34746b4dedf0b4dfa099e1781791509496
requests the page makes on load:
  https://static.cloudflareinsights.com/beacon.min.js/...
  https://bugarach.tonydefazio.com/cdn-cgi/rum?
```

Cloudflare Web Analytics auto-injection rewrites the HTML at the edge. Our built
`site/viewer.html` contains no such string — `grep -c cloudflareinsights` is 0 —
and it is in the response anyway.

## Why a plain curl says the page is clean

Injection is conditional on the request looking like a browser. `curl` gets the
file we wrote; `curl -A "Mozilla/5.0 …" -H "Accept: text/html"` gets the beacon,
and so does every real visitor. **So the obvious way to check this reports the
answer we want to hear.** Any future audit has to send browser headers or drive a
real browser.

## What is and is not true

**Still true:** a lab's recordings do not leave their computer. The beacon reports
page views and load timings; it does not read the DOM, and the folder is read
through a local file handle that never becomes a request.

**No longer true as served:** "the page has no network calls in it". It has two,
before the reader clicks anything.

That distinction is not a defence. The page's promise is written as a **property
of the code** rather than a policy — that is the whole rhetorical move, and it is
why the test exists. A third-party script executing in the same document as
somebody's unpublished lab data breaks the property even while the consequence
stays benign, and a reader who opens devtools finds the page's first paragraph
contradicted by its own network tab.

## The fix, which is not in this repo

Turn off Web Analytics for the `tonydefazio.com` zone, or for this hostname:
Cloudflare dashboard → Web Analytics → remove/disable automatic setup. It is a
zone-level toggle on a custom domain, so `wrangler.jsonc` cannot express it and no
change here will help. **This needs Tony at the dashboard.**

Until it is off, the page overstates. Two ways to close the gap, in preference
order:

1. **Turn the beacon off.** The claim goes back to being true as written, and the
   existing tests keep guarding it. This is the one to do — the analytics are worth
   nothing next to the sentence they falsify.
2. **Weaken the sentence** to "no network call this page makes carries your data".
   Accurate, and much less good: it turns a checkable property into a promise about
   intent, which is exactly what the current wording was written to avoid.

## The check that would have caught it

Every guard we have reads the source. Worth adding one that reads the **deployed**
page with browser headers and fails on any third-party origin — as a `tools/`
script run at deploy time rather than a pytest, since CI has no business fetching
production. It would also catch the next thing an edge feature injects, which is
the general version of this problem: **anything checked before upload cannot see
what the CDN adds after it.**

## How it turned up

Driving the live page with Playwright after deploying, and reading the request log
rather than trusting the page. The deploy itself was fine.
