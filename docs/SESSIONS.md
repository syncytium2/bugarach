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

### Mac/dt-required-at-load — FOUNDATIONS §6 reversed: dt is required, not defaulted
- **Status:** ACTIVE — open PR
- **Started:** 2026-08-16
- **Writes:** repo only
- **Claims:** none
- **Notes:** **Read this before writing anything that loads data.** FOUNDATIONS §6 used
  to say `grid_dt` is the caller's responsibility at detection time and that omitting it
  falls back to 0.1 s with a warning. Tony, 2026-08-16: *"we cannot allow data loading
  without the user specifying a dt."* §6 now requires it at the **load boundary**, and
  refusing beats defaulting — a warning fires after the number already exists.

  Doc-only so far; the code still falls back. The gap is
  `docs/todo/2026-08-16-dt-must-be-required-at-load.md`. Until it closes,
  `GridDtNotSetWarning` still fires and still must not be silenced. **The six ports keep
  their seconds-valued MATLAB parameters — parity is untouched by this.**

### Mac/generator-records-realized-onsets — the generator should record what it planted
- **Status:** ACTIVE — open PR #46, **wants review before it lands**
- **Started:** 2026-08-16
- **Writes:** repo only
- **Claims:** none
- **Notes:** `PlantedEvent` gains an `onsets` field (what each participant actually got)
  and an `observed_span` property. `span` untouched, still nominal ±3σ. Emitted data
  verified bit-identical across 36 generator configurations, so no committed figure,
  bench number or fixture moves. The ±3σ window is 2.7× wider than the median realized
  footprint on the bench recording. **If you are working on scoring tolerance
  (`docs/todo/2026-08-13-scoring-tolerance-vs-detector-resolution.md`, which reasons
  about `span` in the old terms), this PR is either in your way or is your answer.**

### Mac/— — lit folder in the darkroom
- **Status:** DONE
- **Started:** 2026-08-16
- **Writes:** `<darkroom>/bugarach/lit/` (NEW), `<darkroom>/bugarach/lit/DL/` (NEW)
- **Claims:** none — new namespace, nothing else writes there
- **Notes:** A reference library for papers a bugarach design decision actually rests on,
  each entry naming the decision. Seeded with Deep Sets (Zaheer 2017) and PointNet (Qi
  2017), which bear on set-structured input and the distinct-ROI rule. Undated on purpose
  — everything else in `bugarach/` is a dated review artifact; a citation does not expire.
  Rule in `lit/README.md`: a PDF with no index entry is indistinguishable from one someone
  downloaded and forgot. Fetch by hand — murderboard's `fetch_paper.py` is deliberately
  not vendored (SAP004, personal paths).

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
