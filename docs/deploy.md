# Deploying the site

`bugarach.tonydefazio.com` — an **assets-only Cloudflare Worker**, the same shape
`colonel_kernel` uses: no server script, Cloudflare serves `./site` directly.

```bash
python tools/build_site.py     # generate ./site   (Python; runs anywhere)
npx wrangler deploy            # upload            (needs node + wrangler auth)
```

Two machines, because the two halves need different toolchains: the build is
Python and runs on any box with the repo installed; the upload needs node, which
is not on every machine here.

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
