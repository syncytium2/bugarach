# Pipelines — the established routes to a result

**Look here first.** Before designing a run, check whether the route already exists. This repo
re-solves problems it has already solved, and the cost is not wasted compute — it is a second
route that gets the gates wrong in a different way, so two results stop being comparable.

Each row says what the route is for and what it costs. The page it links to has the commands, in
order, with the gate that must hold before the next stage is worth starting.

⚠ **This is not [`pipeline.md`](pipeline.md)** — that page is the *product* loop, what the app does
for a lab, dictated by Tony on 2026-09-04. These are named, repeatable routes to a particular kind
of result. The names are one letter apart and the things are unrelated, which is worth knowing
before you open the wrong one; [`INDEX.md`](INDEX.md) carries the same ⚠ about `workflow_plan.md`,
which a session once read as the loop and reported the centrepiece missing.

## The routes

| route | use it when | cost |
|---|---|---|
| [**learned-model evaluation**](pipelines/learned-model-evaluation.md) | a new learned architecture exists and someone needs a number for it that will be quoted, compared, or decided on | ~one overnight at `--jobs 12` |

## This index is checked, not trusted

`tools/check_pipelines.py`, wired into the suite as `tests/test_pipelines_resolve.py`. It holds the
two ways a hand-kept index decays:

- a row pointing at a pipeline that has been renamed, moved or deleted — the reader follows it to
  nothing and concludes the route does not exist;
- **a pipeline on disk that no row mentions** — the route exists, this page says it does not, and
  the next session builds it again. That is the failure this index is for, and it is the silent one.

It also refuses an index that lists nothing, and requires each route to say what it is for and what
it produces. `python3 tools/check_pipelines.py --selftest` proves every rule can still fire.

The claim "look here first" is only worth something while the page is true, and a page that asserts
a gate it does not have is exactly the defect `check_milestones.py` was built for — its own first
version shipped four rules that could not fire and reported success anyway.

## Adding a route

1. Write it at `docs/pipelines/<route-name>.md`. Open with **Use it when**, **It produces**, and a
   cost line; then the commands in order; then a stage per gate.
2. **Verify the commands against the tools' actual flags before committing.** The first draft of the
   learned-model route had `--checkpoints` backwards — it is a write on one stage and a read on the
   next — which would have sent the next session down a chain that cannot run.
3. Every gate carries the failure that earned it. A rule without its incident gets argued with and
   dropped; a rule with one gets followed.
4. Add a row above, and an [`INDEX.md`](INDEX.md) row with the words someone would actually grep.
5. `python3 tools/check_pipelines.py` before you push.

## Where this came from, and where it is going

Written 2026-09-16 after the learned-model route had been run end to end overnight and reviewed
twice. Asked armory first whether the estate owned a convention for this: **it does not** — no
spec, no naming scheme, no template, no location rule, anywhere in fifteen repositories.

Armory's recommendation was to invent it here and **not** to generalise it until a second repo wants
one, on the grounds that the estate's documented failure is fourteen instruments that never left a
single repository rather than an absence of standards — and that the part worth exporting is
whichever fields the *second* route cannot do without. So this index deliberately asks for very
little. Its write-up, with the search that established the gap, is on armory's `pipelines-convention`
branch (`9a3ec96`, unmerged), so the next repo that grows a second route finds it.

Four things in the estate are already routes to a result under other names, and are worth reading
before inventing a fifth shape: `interface2/docs/pipeline.yaml` with `tools/build_pipeline_map.py`
(one source, generated views, `--check` verifying the branches still exist — written because two
hand-maintained maps in that repo decayed into being wrong); `interface2/docs/handoffs/RUNBOOK_*.md`,
which are what a pipeline document looks like in the estate today, filed as handoffs only because
there was nowhere else to put them; `downLow/tools/verify_pipeline.py`, whose gates are checks that
can fail, each paired with a deliberate breaker and a `--selftest`; and `docs/session_protocol.md`,
vendored into six repos, which is this estate's proof that a plain document name travels when the
name is stable and the content stays local.
