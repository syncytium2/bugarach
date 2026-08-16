# HANDOFF — workflow app plan, awaiting its murderboard

Delete this file when the murderboard record lands and the plan is either accepted
or revised. A handoff file on `main` means something is in flight.

## What this session was asked for

Grow bugarach from a detector viewer into the full workflow: a folder of recordings
in, generator fitting, generated-vs-real comparison, simulated data for detector
optimization, all six detectors, publishable figures, statistics handoff.

**Nothing was implemented.** This session produced a plan, had it reviewed, and
cleared the gate that was blocking its review. That is the whole of it — by
Tony's instruction, no implementation code until the review lands.

## Where the work is

**The plan:** [`docs/todo/2026-08-16-workflow-app.md`](docs/todo/2026-08-16-workflow-app.md).
It carries what Tony settled, the export contract to port, the fitting stage's
design, and the traps. Read it before doing anything on this task.

It began life outside the repo, in the harness's plan directory, which is
machine-local and therefore invisible to the next session — moving it here is the
only reason this branch exists. If a newer revision exists in a live session's plan
file, that session's copy and this one may have diverged; the repo copy is the one
that survives.

## In flight, and the one thing to check first

**A murderboard is running in another session** against the same plan (fingerprint
`19bae3d9d5ca4355be15337c36f0f35cd7874a2f`, verified identical on both sides). Its
record is claimed at `docs/reviews/jazzy-watching-pixel_2026-08-16.md`.

- **If that file exists**: read it, apply the findings to the todo, confirm
  `bash tools/murderboard_roster.sh check <report>` exits 0, and delete this handoff.
- **If it does not**: the review never landed. The plan has had peer review from four
  sessions but not the gate. **Re-run it** — `/murderboard docs/todo/2026-08-16-workflow-app.md`
  — rather than building from an unreviewed plan.

## Landed this session

- **PR #42** — the murderboard vendor refreshed from `b2b2ba2` to `f43a07b`. The
  freshness gate had been failing at exit 1, which is a hard stop: a review run
  against a stale process silently omits rules and then reports coverage it did not
  have. The upstream delta turned out to be spelling only, which made re-vendoring
  cheap rather than optional — the first time a gate is rationalized past is when it
  stops being a gate. Gate now exits 0, roster 11, sapper clear.
- Two stale sha references bumped alongside it, in `tools/check_vendor_freshness.sh`
  (the documented upstream defect **is** still present at `f43a07b` — verified, not
  assumed) and in `CLAUDE.md`'s role count.
- `fetch_paper.py` was **not** re-vendored, deliberately — it carries a personal
  library path that SAP004 blocks and that must not sit in a public repo.

## Open decisions the plan cannot resolve alone

- **Which mode does a generated run report as?** The three peak source keys are
  emitted in REAL mode only, so a generated run reports either nine keys or six.
  Choosing wrong silently omits or fabricates three of them.
- **Where identity metadata comes from** for a folder of bare CSVs. Design is a
  sidecar carrying the treatment *index*, not just the label — but nobody has said
  what produces that sidecar.

## Not held by this session

`tools/build_site.py` (PR #37 merged — the TTX result was reworked rather than
published, so §5 was honored), `src/bugarach/simulate.py` (the generator session
landed clustered arrival timing in PR #41), the darkroom (nothing written, no board
claim taken).

## One thing worth flagging rather than resolving

Two sessions this session believed they had authored the same work, and the git
record supports only one lineage. It changed no outcome — the vendor refresh landed
correctly either way — but it was raised with Tony as a possible harness issue and
is noted here so a third session does not spend time reconciling it.
