# HANDOFF — deploy the site to `bugarach.tonydefazio.com`

**In flight:** the static site is built, configured, and verified up to the
authentication boundary. It has **never been deployed**. The one remaining step
is an OAuth browser flow, which is why it is a handoff rather than a commit.

Written 2026-08-15 from the Windows box (WSMIP). Delete this file when the
deploy lands — a handoff file on `main` means something is in flight.

---

## The exact next step

On the laptop, from a shell that has `node` on PATH:

```bash
cd <repo>
npm install          # once per clone — installs the pinned wrangler (4.122.0)
npx wrangler login   # opens a browser; the step that cannot be scripted
npm run deploy       # builds the site with Python, then uploads
```

`npm run deploy` runs `tools/build_site.py` first via `predeploy`, so a stale
site cannot be published.

**Watch the login.** If the browser happens to be signed into a different
Cloudflare account, the deploy fails with a zone-not-found error that does not
name the real problem. `tonydefazio.com` must be in the account you authorize —
the same one already serving `kernel.tonydefazio.com`.

## How to verify it worked

```bash
curl -sI https://bugarach.tonydefazio.com | head -1     # expect HTTP/2 200
```

Then open it and **look at the page** — that is not a formality here. The first
version of this figure shipped with its labels written on top of the data
because it was published without anyone rendering it. `site/diagnostic.png` is
the flat render; compare it to what the browser shows.

Current state, for comparison — all four should still be true after deploying:

| check | expected today |
|---|---|
| `bugarach.tonydefazio.com` | **does not resolve** (nothing deployed yet) |
| `bugarach.tonydefazio.workers.dev` | **404** (worker never created) |
| `npx wrangler whoami` | not authenticated, no `~/.wrangler/config` |
| `kernel.tonydefazio.com` | **HTTP 200** — control: domain and account are fine |

## What is already done, so you do not redo it

- `site/` builds: 241 KB, four files. `npm run dry` passes — reads 4 files,
  config valid.
- `wrangler.jsonc` declares the custom domain:
  `"routes": [{"pattern": "bugarach.tonydefazio.com", "custom_domain": true}]`.
  Cloudflare creates the DNS record and the Worker binding on deploy. **Nothing
  to do at Porkbun** — it is only the registrar, and the nameservers already
  delegate to Cloudflare (`arya`/`clyde.ns.cloudflare.com`).
- wrangler is **pinned** at 4.122.0 with a lockfile, not `@latest`, so the
  deploy cannot change under you. (4.123.0 exists; the pin is deliberate.)
- The build reads **no store**. It generates from a seed and has no code path
  that could pick up a real slice — FOUNDATIONS §5, and this site is public.

## Machine notes

**This Windows box:** node had to be installed. No winget/choco/scoop, so it is
a checksum-verified portable zip at `%USERPROFILE%\tools\node` on the *user*
PATH. Only new shells see it.

**The laptop:** node is almost certainly already there — `colonel_kernel`
deploys from it. Confirm with `node --version` before assuming. The Python side
needs `pip install -e ".[dev]"`; the PNG render additionally wants
`python -m playwright install chromium`, and is skipped with a warning if
absent rather than failing the build.

## One thing that will fail on the laptop only if it is Windows

`tests/test_session_briefing.py::test_it_is_fast_enough_to_be_unconditional`
asserts the session briefing runs in under 3 s, because it sits on the blocking
SessionStart path. **On this Windows box it takes 15.8 s.** CI is green (Linux),
so `main` is genuinely green — but the guard does not hold here, and the thing it
guards against is real: interface2 lost half a day to a SessionStart hook that
took sessions down at 60 s. Filed as
[`docs/todo/2026-08-15-briefing-too-slow-on-windows.md`](docs/todo/2026-08-15-briefing-too-slow-on-windows.md).
On macOS it will almost certainly pass; do not "fix" it by raising the budget.

## Still open, unrelated to the deploy

- `docs/todo/` — the standing list.
- The interactive-in-the-browser route (`panel convert` to WASM, shipping on the
  same static Worker) is unblocked but not built: `store.py`'s `h5py` import is
  lazy now, and the package is verified to import and simulate without it.
