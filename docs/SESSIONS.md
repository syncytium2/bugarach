# Cross-machine session board — bugarach

**In git, therefore it reaches every session on every machine.** This is the half of the
session board that has to travel. The protocol is
[`docs/session_protocol.md`](session_protocol.md) (vendored from interface2); this file is
its Tier-2 ledger.

Companion, **outside git**: `../bugarach-worktrees/SESSIONS.md` — only what genuinely
cannot travel (live process ids, that box's free disk, local scratch paths).

---

## Which board does this go on?

One test, and it is **not** "is this about my machine?":

> **Can a session on another machine see, reach, or damage the thing you are claiming?**
> **Yes → here, in git. No → the machine-local board.**

The trap is shared storage. A Dropbox or network mount is visible from *every* machine, so a
claim on it is cross-machine even though it feels local.

| goes HERE (git) | stays MACHINE-LOCAL |
|---|---|
| claims on `BUGARACH_DATA_ROOT` stores, the Dropbox darkroom, any `interface2` checkout | live process ids, `pytest -n` jobs |
| exclusive-write claims of any kind | that box's free disk, local scratch |
| "I am regenerating the MATLAB parity fixtures" (needs MATLAB + interface2) | which MATLAB release is installed where |
| messages to another session | — |

**bugarach-specific shared resources worth claiming before writing:**

- `tests/fixtures/ref_*.json` — regenerating these needs MATLAB + an interface2 checkout;
  two sessions regenerating at once will produce conflicting oracles.
- the Dropbox **darkroom** (`<dropbox>/darkroom/constellation/`) — shared across every
  machine and every project that mounts it. Claim before writing.
- any `interface2` worktree you `addpath` — another session may be mid-edit on that branch.

---

## Protocol for a block

- **Add a block at startup** — address (`<machine>/<branch>`), task, which external paths you
  will write, status.
- **Mark it DONE on exit**, and release any exclusive claim explicitly.
- **Scan the board before writing any shared external output.** If an ACTIVE block claims it,
  use a different namespace or wait.

Template:

```
### <machine>/<branch> — <task>
- **Status:** ACTIVE | DONE
- **Started:** YYYY-MM-DD
- **Writes:** <external paths, or "repo only">
- **Claims:** <exclusive-write claims, or "none">
- **Notes:** <anything another session must know>
```

---

## Active

### mac/rewrite-generator-doc — roiRate distribution figure
- **Status:** ACTIVE
- **Started:** 2026-08-15
- **Writes:** `<darkroom>/bugarach/roi_rate_distribution.{html,png}` — that pair only
- **Claims:** the two `roi_rate_distribution.*` names. No claim on the rest of
  `<darkroom>/bugarach/`; another session may write other figures there concurrently.
  **Released:** `roi_concentration.*` — an earlier name for this figure, invented
  rather than taken from the project's vocabulary (Tony, 2026-08-15). The stale pair
  is deleted; nothing else should be written under that name.
- **Reads:** `$BUGARACH_DATA_ROOT/processed_archive/event_store_onset_revised_2v` —
  read-only, 88 slices, baseline regions only. No writes to any store.
- **Notes:** Renders `tools/make_roi_concentration.py`. Evidence for
  `docs/todo/2026-08-14-generator-background-model-is-flat.md`. **Also editing
  `tools/make_diagnostic.py` and `src/bugarach/ui/diagnostic.py` on this branch —
  see the collision note under the site session below before merging either.**

### mac/site-leads-with-the-figure — COLLISION NOTE from rewrite-generator-doc
- **Status:** ACTIVE (theirs) — this block is a message, not a claim
- **Notes:** Both branches edit `tools/make_diagnostic.py` in the same argparse
  block: the site branch adds `--hero`, `rewrite-generator-doc` adds `--scale` and
  gives `_render_png` a `scale` parameter. Textual conflict is small; the real
  overlap is that `--hero` renders the plot alone and `rewrite-generator-doc`
  **changes that plot** — ground truth moves to the top of the lanes, detectors get
  their full names, and trace rows grow 82px → 112px. The site's hero image will
  change when this branch lands, and `--hero` will start rendering at device
  scale 3 rather than 2. Whichever merges second should re-render the hero and
  look at it. Not resolved unilaterally: neither session should rebase the other.

### WSMIP-win/vendor-session-protocol — vendor the session protocol + audit upstream tooling
- **Status:** DONE
- **Started:** 2026-08-12
- **Writes:** repo only
- **Claims:** none
- **Notes:** Installed the vendored session protocol, the SessionStart hook, and this board.
  Read-only survey of `interface2` (`origin/main`, `origin/detector-defaults-optimized`) and
  the Dropbox darkroom — no writes to either. Findings filed in `docs/todo/`.

### WSMIP-win/vendor-session-protocol — create the bugarach darkroom folder
- **Status:** DONE
- **Started:** 2026-08-12
- **Writes:** `<darkroom>/bugarach/` (NEW), `<darkroom>/README.md` (appended one dated
  UPDATE section — that file is the shared convention and asks for notes to be left in it)
- **Claims:** `<darkroom>/bugarach/` — **exclusive-write for bugarach**. No other project
  writes here; nothing branch-routes into it (it is a separate Python repo, like
  `haruspex/` and `no_peak/`).
- **Notes:** Created because bugarach's output is distinct from the `constellation/` team's
  (Tony, 2026-08-12): constellation is the MATLAB **producer**, bugarach is the Python port
  + viewer that consumes the same contract. Did NOT touch `constellation/` or any other
  project folder. Resolve the path via `$BUGARACH_DARKROOM` — never hardcode it (SAP004).
