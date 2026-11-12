# Great Lakes — what is available to a bugarach job

**Use this page when** writing a run sheet or a job script. Access and rules:
[`README.md`](README.md).

> Working material, not murderboarded. Written 2026-11-12. "Verified" names who checked and
> when. A row without a check is a thing to confirm on the first run sheet, not a fact.

## On the cluster

| what | status | source |
|---|---|---|
| Slurm, partition `standard`: 28 or more cores and about 180 GB per node, 14-day limit | verified 2026-07-30 by interface2 | interface2 `greatlakes/ACCESS.md`, step 2 |
| partition `largemem` | exists; bugarach has no use for it | same |
| billing on `standard`: by reserved memory above 7 GB per requested core | measured 2026-08-28 by interface2 | same, "what a job actually costs" |
| MATLAB, pinned `matlab/R2025b` | verified by interface2; not used by bugarach | same |
| **Python** (which module, which version) | **unknown** | nobody has asked |
| **`uv` on a login node** | **unknown** | nobody has asked |
| outbound access to GitHub and PyPI from a login node | GitHub yes (interface2 clones there); PyPI **unknown** | same, step 3 |
| the shared research drive ("turbo") mounted on login and compute nodes | verified by interface2 | same |

## interface2's helpers, on the cluster in Tony's interface2 checkout

Read-only for bugarach. Each is documented where it lives.

| script | what it does |
|---|---|
| `greatlakes/gl_exchange.sh` | defines `cx <name> <command>`: runs a command, scrubs credentials, writes its output to turbo so a workstation session can read queue listings and shell errors |
| `greatlakes/gl_publish.sh` | writes a run's queue state and log tails to `run_record/STATUS_<project>.txt` on turbo, and defines the verdict contract |
| `greatlakes/gl_session.sh` | one human login, later commands over the same connection. Built on a branch; interface2 has not confirmed it is in use |
| `docs/greatlakes_gotchas.md` | what has gone wrong there and how it looked: a job pending forever, mail that says END on a failure, pastes mangled in the browser shell |
| `greatlakes/REBOOTS.md` | the cluster's node reboots and what they do to a running job |

## bugarach's own, for the cluster

None exists yet. Owed, in the order the first run needs them:

1. **An environment recipe**: the module line and the commands that build bugarach's Python
   environment from `pyproject.toml`, pinned.
2. **A job script for one search**
   (`tools/search_all_settings.py --bench <stream> --sliding --out <dir>`), with cores,
   memory and wall time from a timed run.
3. **An array over the benches**, one task per bench, writing to turbo.
4. **A verdict check** that opens each search's output and writes PASS, FAIL or
   FAILED-TO-RUN.
5. **A run sheet** for Tony: login, environment, one test job, the array, the status command.

## On a workstation, not the cluster

Stage 1 (measuring the baseline on the export folder) and stage 7 (detecting on it) stay on a
workstation, because the export folders do not go to the cluster. The tools are listed in
[`../pipelines.md`](../pipelines.md).
