# Deploying the site

> **Check [`DEPLOY_HOLD.md`](DEPLOY_HOLD.md) first.** A deploy can be deliberately
> queued — updates held to land with a piece of work rather than going out one at a
> time. `tools/site_staleness.py` reads that file and says so instead of handing you
> the publish command, so in practice you will have met the hold before you get
> here; this line is for the case where you came straight to the runbook.

`bugarach.tonydefazio.com` — an **assets-only Cloudflare Worker**, the same shape
`colonel_kernel` uses: no server script, Cloudflare serves `./site` directly.

```bash
npm install        # once per clone — installs the pinned wrangler
npx wrangler login # once per machine — OAuth browser flow, cannot be scripted
npm run deploy     # build (Python) + upload (wrangler), every time
```

`npm run deploy` runs `tools/build_site.py` first via `predeploy`, so the site is
never uploaded stale. `npm run dry` does everything except the upload.

## Drive the built site before you upload it

**Everything that reads "tested" about this page, until 2026-08-23, meant
`docs/site/raster_viewer.html` opened from `file://`.** That is the source of one
of the four pages the site actually serves, and driving it proves nothing about
the nav bar, the other three pages, or anything that behaves differently over
HTTP. When somebody finally served the build and walked it, two of the four pages
turned out to have no nav bar at all and the front page's hero figure had been
built with no detections in it — neither visible from `file://`, and neither
loud enough to notice from the build's own output.

So: serve the payload and open it.

```bash
python tools/build_site.py
python -m http.server 5096 --bind 127.0.0.1 --directory site
```

Then click every nav link on every page, and open the viewer and point it at a
real export folder. `tests/test_site_coherence.py` mechanizes the part that can
be: every link on every built page resolves, every page reaches every other, and
the build writes exactly the manifest it declares.

**What a local server cannot tell you** — the honest half, because a check that
overstates its reach is worse than no check:

| behaviour | localhost says | the edge does |
|---|---|---|
| `/viewer.html` | **200**, serves the file | **307 → `/viewer`** (see below) |
| `/viewer` | **404** | 200, the same file |
| secure context | **true** — `localhost` is trustworthy by definition | true, but because Cloudflare serves **HTTPS**, not because of the path |
| injected scripts | none — it serves the bytes on disk | Cloudflare has [added a beacon](#why-there-is-a-check-on-the-far-side-of-the-upload) |

The secure-context row matters for the folder-open route: `showDirectoryPicker`
needs one, and so does the `<input webkitdirectory>` path in practice. Both work
locally and both work deployed, but for *different reasons* — a plain-HTTP
deployment to a non-localhost host would break the first and localhost would
never have told you. The custom domain in `wrangler.jsonc` gets a Cloudflare
certificate automatically, so the deployed page is HTTPS and this is fine; it is
written down because "it worked on localhost" is not the evidence that makes it
fine.

### The `/viewer.html` → `/viewer` redirect, and why it is only a reading hazard

`wrangler.jsonc` sets no `html_handling`, so the assets Worker uses the default,
`auto-trailing-slash`: it serves `viewer.html` at `/viewer` and **307s
`/viewer.html` to it**. A `curl` without `-L` gets zero bytes from the URL every
page on the site links to, which reads exactly like a failed deploy.
`tools/site_staleness.py` follows redirects and says so at its docstring; the
trap is for a person checking by hand.

Nothing is broken by it. Every nav link is a relative `href="viewer.html"`, the
browser follows the 307, and the page loads. It costs one hop and it makes
hand-checking misleading, which is the whole of the problem. **Do not go
changing `html_handling` to make a `curl` tidier** — the redirect is Cloudflare's
default for a reason and the links work; use `-L`, or use the browser-driven
audit below.

**After deploying, check what actually got served:**

```bash
python tools/audit_deployed_page.py
```

It is a step you run, not one that runs itself. It was briefly wired as a
`postdeploy` script, and unwiring it is the point: a step that can fail somebody
else's deploy on every machine is a rule, and rules here are Tony's to install,
not a passing session's.

## The build refuses to publish a page that is missing part of itself

`build_site.py` used to exit **0** on a front page that had lost its lead figure:
no `hero.png` meant a link card in its place, one line on stderr, and a successful
build. Every other asset already returned 1 — a missing `reality.png`,
`landscape.html` or `viewer.html` each stop the build — so the hero was the one
thing that could go missing quietly, on the page a stranger sees first.

It is a hard failure now, and so is the case that made it urgent: **the diagnostic
scoring no detectors at all.** On 2026-08-23 `main` built a site whose hero figure
and diagnostic page contained nothing, because a detector signature changed and
`tools/make_diagnostic.py` was not updated with it; all six raised into the
per-detector `except` that exists so one awkward slice cannot lose the whole
figure. That tolerance is right for a troubleshooting tool and wrong for a publish
step, so the build reads the sidecar and refuses. Neither process had exited
non-zero and stderr had been completely clean.

Two things this leans on, both already written down here:

- **stderr does not carry a warning.** This site once froze 233 commits behind
  because a build exited 1 in a terminal nobody was watching, which looks exactly
  like a build nobody ran. A message that only *mentions* a degraded page is
  strictly weaker than that, and it was what we had.
- **The prose describes the picture.** Two paragraphs of `index.html` introduce
  the hero by what it shows. That is the same reason the build already refuses on
  a missing `reality.png` — publishing text about a figure that is not there.

The escape hatch is `--allow-degraded`, which prints what is wrong and ships it
anyway. It exists for the reason `guard_branch.sh` has `ALLOW_MAIN_COMMIT=1`: a
guard with no way past it gets deleted the first time it is genuinely in the way.
Use it to look at a local build without playwright chromium; do not use it to
deploy. CI installs chromium, so a correct build never meets any of this.

## Is the live page still current?

```bash
python tools/site_staleness.py            # the full report
python tools/site_staleness.py --brief    # the line the session briefing prints
```

**Nothing publishes this site**, so the page advances only when a person runs the
three commands above, and it drifts silently in between — a stale page looks
exactly like a current one. On 2026-08-20 the live site had been three features
behind for weeks and the way that was discovered was somebody opening it. So the
distance is now measured and put in front of whoever starts a session:
`tools/session_start_trimmed.sh` prints one line of it in the briefing (cached for
six hours, three-second timeout, `BUGARACH_SKIP_SITE_CHECK=1` to silence), and
`.github/workflows/site-staleness.yml` reports it daily in the run summary.
**That workflow never fails**: a red tick for something no automation here can fix
teaches people that red means nothing.

It names the deployed version two ways and reports both. `build_site.py` already
writes the building checkout's short sha into the index footer — "built from
`a189d5e`" — and `site/viewer.html` is a byte-for-byte copy of
`docs/site/raster_viewer.html`, so hashing the served viewer against every
committed version of that file names the same commit independently. When they
disagree, the disagreement is the finding: a served page matching no commit is a
hand deploy from an unpushed tree, or the edge rewriting HTML, and neither is
fixed by deploying. **Unreachable is its own answer** — the check reports "could
not look" and never "up to date", because this repo works offline regularly.

Two things it deliberately does not do: it does not deploy (that needs a
Cloudflare credential, and holding none is what let it ship without waiting for
one), and it does not audit what the page reaches — that is the browser-driven
check below, and a plain GET cannot do that job.

**Why there is a check on the far side of the upload.** Everything else guards the
file we wrote: `tests/test_site_viewer.py` greps the viewer's source for `fetch(`
and friends, and `build_site.py` refuses to publish it otherwise. On 2026-08-18 the
*served* page had two network calls anyway — Cloudflare Web Analytics rewrites HTML
at the edge and injected a beacon into the one page that promises it makes none.
Nothing before the upload can see what a CDN adds after it. The audit above drives
the live URL in chromium and fails on any request to anywhere but the site itself. Do not swap it for a `curl`: the injection was conditional on the request
looking like a browser, so `curl` got the file we wrote and reported clean.

**On this Mac, deploys need the venv on PATH.** `predeploy` calls `python` and
macOS has only `python3`, so run
`PATH=<repo>/.venv/bin:$PATH npm run deploy`. Do **not** change `package.json` to
say `python3` — the Windows box this document was written on has `python` and not
`python3`.

**Check what the deploy checkout is pointed at.** Deploys run from whichever clone
holds `node_modules` and the wrangler login, and on the Mac that is a worktree on a
**detached HEAD** which does not follow `main`. It sat at a twelve-commit-old
commit and faithfully republished it, which reads as a failed deploy and is a stale
checkout. `git -C <that worktree> log --oneline -1` before every deploy.

**Node lives in the user profile, not system-wide.** This is a managed Windows
box with no winget/choco/scoop, so node is a checksum-verified portable zip
extracted to `%USERPROFILE%	ools
ode` and appended to the *user* PATH. No
admin, nothing installed system-wide, and uninstalling is deleting that folder
and removing one PATH entry. Version at time of writing: node 24.19.0 LTS,
npm 11.17.0, wrangler pinned to 4.122.0 in `package.json`.

**npm 11 blocks postinstall scripts by default**, so `esbuild` and `workerd`
never fetch their platform binaries. That does not matter for an assets-only
Worker — nothing is bundled, and `wrangler deploy --dry-run` passes. If a future
change needs real bundling, run `npm approve-scripts` for those two.

## What has to be done by hand at Porkbun and Cloudflare

**Porkbun: nothing.** It is only the registrar. `tonydefazio.com`'s nameservers
already delegate to Cloudflare (`arya.ns.cloudflare.com`,
`clyde.ns.cloudflare.com`), so DNS lives entirely in Cloudflare. Porkbun matters
again only if the registrar or the nameservers change.

**Cloudflare: nothing to click either**, because the hostname is declared in
`wrangler.jsonc`:

```jsonc
"routes": [{ "pattern": "bugarach.tonydefazio.com", "custom_domain": true }]
```

On `wrangler deploy`, Cloudflare creates the DNS record and the Worker binding
for that hostname itself. Declaring it here rather than in the dashboard keeps
the hostname in version control with everything else, and means a fresh clone
deploys to the same place instead of to a `workers.dev` URL that someone then has
to re-point by hand. (`colonel_kernel` predates this and was wired up in the UI —
worth backporting there.)

**Could a Python script do it instead?** Yes — Cloudflare has a REST API and DNS
records are a `POST` away. It would be strictly worse: it needs an API token
stored somewhere, it re-implements what `wrangler` already does with the auth you
have, and it puts the hostname in a script instead of in the config file the
deploy already reads. The one-line route above is the smaller, safer version of
the same thing.

The only genuinely manual step is the first `wrangler login` on a machine, which
is an OAuth browser flow and cannot be scripted away.

## Why there is no server

The static site is the whole product for **viewing**. The compute is small — a
full recompute is ~1.6 s for three detectors on a 75-minute two-stream slice — so
a server was never needed for capacity. It would only be needed for
*interaction*: moving a slider and re-running a detector.

| you want | what it takes |
|---|---|
| look at results, zoom a false alarm | the static site — **done** |
| move sliders and re-run detectors | a live Python process (below) |

## Data posture — the constraint that shapes everything

**Only synthetic data is ever built into the site.** FOUNDATIONS §5 keeps real
recordings machine-local behind `BUGARACH_DATA_ROOT`, and both this repo and the
site are public. `build_site.py` generates its data from a seed and has no code
path that reads a store, so this cannot be violated by forgetting — which is the
only kind of guarantee worth having.

If a real slice ever needs to be shown to someone remote, that is a private
deployment with auth, and a separate decision.

## Making it interactive later

The viewer (`bugarach view`) is a Panel app and needs Python. Two routes:

1. **Browser-native (Pyodide).** `panel convert` compiles the app to WASM, and it
   then ships as static assets on the *same* Worker — no server, no sleeping, no
   per-request cost. The blocker was `store.py` importing `h5py` at module level;
   h5py is a compiled extension with no Pyodide build, so the whole package was
   unimportable there. **That import is now lazy**, and the package has been
   verified to import and simulate with h5py absent. Remaining cost: ~10 MB of
   wheels on first load and a slow cold start, plus surrogate-heavy detectors
   being several times slower in WASM.
2. **A hosted Python process** (Spaces, Fly, Render). Full speed, real files, but
   something to keep running, and it drags the data question along with it.

Route 1 fits the existing infrastructure — it stays one static Worker on the
domain that already serves the other projects.

## Deploy gates worth copying

`colonel_kernel/scripts/deploy.sh` encodes its runbook as an executable script
rather than prose, because "each session improvised its own variant" once put a
bad build into production. It refuses to deploy from a shallow clone, off the
release branch, or with a dirty tree, and writes `DEPLOYED.md` recording the
commit and worker version.

bugarach does not have that script yet. It should before anyone deploys twice —
the manual `npx wrangler deploy` above is the improvised variant that story warns
about.
