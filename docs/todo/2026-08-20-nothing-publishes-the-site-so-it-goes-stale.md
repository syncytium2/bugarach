---
status: open
filed: 2026-08-20
---

# Nothing publishes the site, so it silently falls behind `main`

> **2026-08-23 — options 2 and 3 landed. Option 1 still needs Tony.**
>
> The gap is now measured and said out loud by `tools/site_staleness.py`: one line
> in the session briefing, a daily run summary from
> `.github/workflows/site-staleness.yml`, and a full report on demand
> (`python tools/site_staleness.py`). None of it publishes anything, which is
> exactly why it could be built without asking.
>
> **What it measured the moment it was wired up: the live page was 46 commits
> behind `main`, two of which change what it serves** — `ab82ccd`, the refusal of
> a sweep where every point ties, and `d152d35`, the whole top-rail navigation
> redesign. The last deploy built from `a189d5e` on 2026-08-22 and the served
> viewer still hashes to its content at `95d94ec`. The gap this file describes was
> real, was still open three days later, and is now the first thing a session
> reads.
>
> **Still owed, and nobody here can pay it: the Cloudflare API token** for option
> 1, plus the decision it stands for — that an Action in a public repo may
> publish. Until that happens the deploy is a hand command and this check is what
> stops it being forgotten. It does not replace option 1; it makes the cost of
> not having it visible.
>
> Two things worth knowing before extending it. It names the deployed version
> **twice, independently** — the `built from <code>…</code>` stamp
> `tools/build_site.py` writes into the index, and the sha256 of the served
> viewer matched against every committed version of
> `docs/site/raster_viewer.html` — and reports both rather than merging them,
> because when they disagree the disagreement is the finding (a page matching no
> commit is a hand deploy from an unpushed tree, or the edge rewriting HTML, and
> neither is fixed by deploying). And **unreachable is its own verdict**: exit 2,
> "could not look", never "up to date". This repo works offline often enough that
> a check whose silence reads as good news would be worse than none.

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
   **DONE 2026-08-23** — `.github/workflows/site-staleness.yml`, daily. It reports
   into the run summary and stays green rather than opening an issue or failing:
   a red tick for something no automation here can fix trains people to ignore
   red, and then a real failure gets waved through too.
3. **Leave it manual and make it visible** — a line in the session briefing that
   prints how far the live page is behind `main`, so it is in front of whoever
   starts work rather than discovered months later.
   **DONE 2026-08-23** — `tools/session_start_trimmed.sh` prints it, cached six
   hours behind a three-second timeout so a session start never waits on the
   network, and under the briefing's byte budget so it cannot repeat the
   2026-08-20 accident of a briefing too big to deliver.

Option 2 or 3 needs nobody's permission. Option 1 does, and is the open half.

## The one gotcha worth writing down

Checking the live page by hand: **`/viewer.html` 307s to `/viewer`**. A `curl`
without `-L` returns zero bytes, which reads as a failed deploy when the deploy
was fine. `tools/audit_deployed_page.py` drives a real browser and does not have
this problem — and the reason it drives a browser rather than curling is
recorded in `docs/deploy.md`: the Cloudflare beacon injection of 2026-08-18 was
conditional on the request looking like a browser, so `curl` reported clean while
the served page had two network calls in it.

---

## 2026-08-24 — three things a person deciding option 1 needs, and none were here

Gathered while option 1 was declined again. Recorded here rather than in a session
note, because this is the file somebody will open when they finally decide.

- **A Cloudflare Workers token cannot be scoped to one script.** Its permissions are
  account-scoped, so the blast radius of a leaked or misused token is *every* Worker
  on the account, not just `bugarach`. `wrangler.jsonc` also binds a custom domain,
  which likely pulls in a Zone permission as well. Verify against the current
  Cloudflare dashboard before deciding — if per-script scoping now exists, most of
  the objection goes away.
- **The public-repo exposure is narrower than it sounds, and concentrated in one
  place.** GitHub does not expose secrets to `pull_request` workflows from forks, so
  a drive-by PR cannot read the token; pushes to `main` need write access. The real
  risk is supply chain — any third-party action in the deploy job runs with the
  secret in scope. Pin actions to full commit SHAs and keep the token out of the
  *build* step's environment.
- **Automating the deploy also automates the silent-degradation path**, which is why
  the hero guard had to land first. `build_site.py` used to substitute a fallback
  and return 0 when the figure failed; a person sees that on stderr, and CI does not.
  That is fixed, and it is the shape of thing to check for before adding any more
  automation on this path.

**Recommended shape, if it is done at all: deploy on tag, behind a GitHub Environment
with a required reviewer** — not deploy-on-merge. The secret is then only exposed to
a job a human approved, publishing becomes a deliberate act, and the version history
matches what is actually live, which pairs with the release stamp the pages now
carry. Deploy-on-merge would have republished the site a dozen times on 2026-08-23,
several of those in states where `main` was internally inconsistent for hours.
