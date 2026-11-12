# Great Lakes — what is available to a bugarach job

**Use this page when** writing a run sheet or a job script. Access and rules:
[`README.md`](README.md).

> Working material, not murderboarded. Written 2026-11-12. "Verified" names who checked and
> when. A row without a check is a thing to confirm on the first run sheet, not a fact.

## On the cluster

Two sources. **ARC** is the university's own documentation, read on 2026-11-12; its pages carry
no update date. **interface2** is what the lab's other repository verified at a terminal
(`greatlakes/ACCESS.md` there).

| what | value | source |
|---|---|---|
| partition `standard`, per node | 36 cores, 187 GB (180 GB requestable) | ARC, [configuration][cfg] |
| wall time on `standard` | 60 minutes if not asked for; 14 days at most | ARC, [defaults and limits][lim] |
| memory if not asked for | 768 MB per core | same |
| limits per account on `standard` | 500 cores and 3,500 GB running; 5,000 jobs queued per user | same. The table was hard to read; confirm on the page |
| partition `debug` | 4 hours, 8 cores, 40 GB, one job per user | ARC, [policies][pol] |
| billing | by the share of a node a job takes: the larger of its weighted cores and weighted memory | ARC, [policies][pol]. No weights are published |
| billing, measured | memory decides once a job asks for more than 7 GB per core | interface2, 2026-08-28 |
| login nodes | 2 cores and 4 GB at most; for Slurm, files and quick debugging. Idle shells close after 2 hours | ARC, [policies][pol] |
| job arrays | `--array=0-15`, `--array=0-15%4` to run 4 at a time; indices 0 to 499,999 | ARC, [job arrays][arr] |
| Slurm output | `slurm-<jobId>.out` beside the submit command unless `--output` and `--error` say otherwise; the folder must exist | ARC, [batch files][bat] |
| stopping cleanly | `--signal=<sig>@<seconds>` warns a job before its time limit. ARC provides no checkpointing; it is the user's | ARC, [accounting][acc] and [policies][pol] |
| outages | scheduled ones announced a month ahead on ARC's home page | ARC, [policies][pol] |
| home directory | 80 GB; for scripts and software builds | ARC, [defaults and limits][lim] |
| `/scratch` | 10 TB and 1 million files per account; **a file not read for 60 days is deleted**; no backup | ARC, [policies][pol] |
| the shared research drive ("turbo") | mounted on login and compute nodes | interface2 |
| Python modules | `module available python` lists them. ARC's examples are `python/3.9.1` and `python3.8-anaconda/2021.05`, and read as written in 2021 | ARC, [Python][py] |
| a Python environment | `python -m venv <path>`, `pip install --user`, or conda; pick one and keep to it. Install from a login node | ARC, [packages][pkg] |
| MATLAB, pinned `matlab/R2025b` | present; not used by bugarach | interface2 |

[cfg]: https://documentation.its.umich.edu/node/4976
[lim]: https://documentation.its.umich.edu/arc-hpc/greatlakes/user-guide/defaults-limits
[pol]: https://documentation.its.umich.edu/node/5008
[arr]: https://documentation.its.umich.edu/node/4986
[bat]: https://documentation.its.umich.edu/node/5078
[acc]: https://documentation.its.umich.edu/node/5111
[py]: https://docs.support.arc.umich.edu/python/installations
[pkg]: https://docs.support.arc.umich.edu/python/pkgs_envs/

**What ARC's pages do not say, and the first run sheet has to find out:**

- **Which Python versions are installed today.** bugarach needs Python 3.11 or later
  (`pyproject.toml`); ARC's own example is 3.9.1. If no module is new enough, `uv` can bring its
  own Python, which depends on the next point.
- **Whether a login node can reach PyPI.** ARC says only that compute nodes cannot be reached
  from the internet. interface2 clones from GitHub on a login node, so outbound access exists
  for that at least.
- **Whether `uv` runs there.** ARC allows software built in the home directory and does not
  mention it.

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
