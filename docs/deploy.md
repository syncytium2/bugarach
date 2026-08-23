# Deploying the site

`bugarach.tonydefazio.com` — an **assets-only Cloudflare Worker**, the same shape
`colonel_kernel` uses: no server script, Cloudflare serves `./site` directly.

```bash
npm install        # once per clone — installs the pinned wrangler
npx wrangler login # once per machine — OAuth browser flow, cannot be scripted
npm run deploy     # build (Python) + upload (wrangler), every time
```

`npm run deploy` runs `tools/build_site.py` first via `predeploy`, so the site is
never uploaded stale. `npm run dry` does everything except the upload.

**After deploying, check what actually got served:**

```bash
python tools/audit_deployed_page.py
```

It is a step you run, not one that runs itself. It was briefly wired as a
`postdeploy` script, and unwiring it is the point: a step that can fail somebody
else's deploy on every machine is a rule, and rules here are Tony's to install,
not a passing session's.

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
