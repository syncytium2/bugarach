---
status: open
filed: 2026-08-20
---

# Nothing publishes the site, so it silently falls behind `main`

The live page at `bugarach.tonydefazio.com` was **three features behind** on
2026-08-20: it had been published while it served five detectors, and since then
CICADA, the fold-based sweep with held-out scoring, the training panel and the
CSV export had all landed on `main`. Nothing was broken. Nobody had run
`npm run deploy`.

`.github/workflows/ci.yml` is the only workflow in the tree, and it tests. There
is no publish step anywhere, so the site advances only when a person remembers —
and the gap is invisible, because a stale page looks exactly like a current one.

## Why this matters more here than on a normal project

FOUNDATIONS §8 makes the repo a portfolio artifact and the site is its front
door. A reviewer who opens it sees whatever was true the last time somebody
deployed by hand, which on 2026-08-20 was a page missing the sixth detector and
the entire output half of the pipeline.

It is also the failure the darkroom rule already names in a different costume:
*"a report counts as output, and in the repo is not delivered."* Work that
reached `main` and not the site is in the same position.

## What makes it non-trivial

**`npx wrangler login` is an OAuth browser flow and cannot be scripted** —
`docs/deploy.md` says so. CI would need a Cloudflare API token as a repository
secret instead, which is a real decision rather than a chore: it puts deploy
rights in GitHub Actions, and this repo is public.

So the options are genuinely different in kind:

1. **Deploy on merge to `main`, from CI**, with a scoped Cloudflare API token in
   secrets. Fully automatic, never stale. Requires Tony to mint the token and
   accept that a compromised Action can publish.
2. **A staleness check rather than a deploy** — a scheduled job that fetches the
   live page, compares it with `docs/site/raster_viewer.html` at `main`, and
   opens an issue or fails when they differ. No credentials, no publish rights;
   it only tells you the page is behind. Cheapest honest option.
3. **Leave it manual and make it visible** — a line in the session briefing that
   prints how far the live page is behind `main`, so it is in front of whoever
   starts work rather than discovered months later.

Option 2 or 3 needs nobody's permission. Option 1 does.

## The one gotcha worth writing down

Checking the live page by hand: **`/viewer.html` 307s to `/viewer`**. A `curl`
without `-L` returns zero bytes, which reads as a failed deploy when the deploy
was fine. `tools/audit_deployed_page.py` drives a real browser and does not have
this problem — and the reason it drives a browser rather than curling is
recorded in `docs/deploy.md`: the Cloudflare beacon injection of 2026-08-18 was
conditional on the request looking like a browser, so `curl` reported clean while
the served page had two network calls in it.
