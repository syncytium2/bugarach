---
status: open
filed: 2026-09-19
---

# The vendor freshness gate is advisory, and nothing runs it

`tools/check_vendor_freshness.sh` checks whether this repo's four vendored families —
the session protocol, the murderboard harness, draughtsman, and armory's send gate —
are current with their upstreams. **Nothing invokes it.** A grep of the tree finds it
named in `CLAUDE.md`, `docs/SESSIONS.md`, `docs/DEPLOY_HOLD.md`, four todos and a
sapper-feedback note — and in no workflow under `.github/`, no test under `tests/`,
and no hook under `.githooks/`. It runs when a session remembers to type it.

That is the whole of the defect, and it is worth naming because the gate exists to
catch a failure that already happened: `third_party/draughtsman/` sat pinned at
`cb7fc2a` for three days while draughtsman had already fixed, in `bb83174`, an edge
routed through the box it bypassed. The front page published that figure the whole
time with nothing red. A gate nobody runs would not have caught it either.

## What it would take

Not obvious, which is why this is a todo and not a patch. The gate resolves upstream
through `gh` and falls back to a local clone, so on a CI runner it needs a token that
can reach two **private** repositories, and `BUGARACH_INTERFACE2` names a machine-local
path that no runner has. Its own exit codes anticipate this: `2` means *could not
determine*, and the wrapper deliberately answers `2` rather than guess — the header
explains that a false STALE is its own harm, because a gate that cries wolf gets
ignored. So wiring it into CI as a hard gate probably turns every run amber.
Candidates, in rough order of cost: run it in the `SessionStart` briefing where the
clones and the env vars actually exist; or add a CI leg that treats `2` as a pass and
only `1` as a failure; or leave it advisory and say so where it is described, instead
of listing it beside gates that do fire.

## A claim about this gate that is wrong, and is published

[PR #669](https://github.com/syncytium2/bugarach/pull/669) — merged 2026-09-19 — says
in its body:

> `tools/check_vendor_freshness.sh` compares each family file with the last upstream
> commit touching that file. The two front-page specs' sources last changed at
> `5705c46`, so once the package moves without them, the family stamp can never agree
> and the gate reports stale permanently.

**That is not what it does**, and the correction is recorded here because a merged PR
body cannot be unpublished and a later session will read it:

- There is no per-file history lookup anywhere in `tools/murderboard_freshness.sh` —
  no `git log -- <path>`. The **first** listed file supplies one stamp for the whole
  family; for draughtsman that is `third_party/draughtsman/__init__.py`. The other
  files are reported only when their stamps **disagree with that one**, which is the
  half-finished-re-vendor check the wrapper's own comment describes.
- That single family stamp is compared against **upstream HEAD** (`upstream_from_gh`,
  `upstream_from_clone`, both `rev-parse`).
- So the family reads stale whenever the upstream's HEAD moves past the vendored
  commit, whether or not any vendored file changed. That is the gate working as
  designed, not a permanent false stale. The remedy is a re-vendor that bumps every
  stamp in the family together — which is what #660 and #669 each did.

The other half of that finding is the real one, and it is the subject of this todo:
the gate is advisory and nothing runs it.

## The upstream answer it gives you can be twelve hours old

Found by the session that wrote #669, while working out where its own wrong claim came
from — the more useful half of that story.

`murderboard_freshness.sh` caches the resolved upstream HEAD per family in the git common
dir for `TTL` seconds, defaulting to **43,200 — twelve hours**
(`.git/murderboard-head.<slug>.cache`). `--refresh` is the only bypass. So a run can name
an upstream sha that the real upstream left behind hours ago, and the verdict line reports
that sha as "upstream" without saying it came from a cache. That is exactly what happened
here: the cache held a draughtsman sha written before draughtsman #1 merged, and a session
reasoning from it built a finding on a repository state that no longer existed.

The gate is not naive about a behind answer — it has a guard for it, and a self-test
("a BEHIND cache is not stale") that keeps a consumer stamped at or after the cached sha
from being accused. But *provably at-or-ahead of a twelve-hour-old sha* is a weaker
statement than *current*, and the report does not distinguish them.

**The window this matters in is the exact one the gate exists for**: upstream merges
something, a session re-vendors within the day and checks its work. Worth considering
alongside the CI question above, since both are about the gate answering when it cannot
really tell: a much shorter TTL, `--refresh` by default off the warm path, or simply
printing the cache's age beside the sha so a reader knows what they are being told.

## Also worth noting about #669

It was opened at 17:42 EDT and merged at 17:44, before its CI finished. The branch it
targets carries the serial tuning fixture, so its suite takes about two hours.
`tools/merge_when_green.sh` refuses a merge whose checks have not passed; merging
through the API or the web UI goes around it. The change itself is three stamp lines
over a byte-identical package, so nothing broke — but the route is the point, and the
same route on a code change would not be harmless.

## Closes when

The gate either fires by itself somewhere a session cannot skip, or the places that
describe it say plainly that it is advisory and name who is expected to run it.
