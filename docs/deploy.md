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
