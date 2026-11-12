# Great Lakes — access for bugarach

**Use this page when** a bugarach job is too long for a workstation: the detector-settings
searches are about one overnight each on 12 cores, and nine of them are wanted at once.
**What is on the cluster and what is not:** [`TOOLS.md`](TOOLS.md).

> Working material, not murderboarded. Written 2026-11-12. Nothing from bugarach has run on
> the cluster yet, so every statement here is marked with where it comes from.

Great Lakes is the university's Slurm cluster. The lab's other repository,
interface2, has run on it since July 2026 and documents access in full. **That page is the
authority; this one says what bugarach needs from it.** It is `greatlakes/ACCESS.md` in
interface2, a private repository, and it holds the login name, the Slurm account and the
exact storage paths, which are not repeated here because this repository is public.

## Who does what

| step | who | source |
|---|---|---|
| log in (interactive, Okta MFA, VPN off campus) | **Tony** | interface2 `ACCESS.md`, relayed 2026-11-12 |
| paste the run sheet's commands | **Tony** | same |
| write the run sheet, job scripts and the verdict check | a bugarach session | this page |
| read status and results from the shared drive | a bugarach session | same |

**A session cannot log in or submit.** There is no key; the login is a person at a prompt.
A session's deliverable is a **run sheet**: single-line commands, in order, starting with the
login line, that Tony pastes. Multi-line pastes get mangled, so one command per line.

## What goes to the cluster and what does not

- **Goes:** the bugarach repository (public, cloned from GitHub) and the records the benches
  are built from, which are in the repository.
- **Does not go:** any export folder. The searches simulate their own recordings and read no
  lab data. Stage 1 of the route (measuring the baseline) and stage 7 (detecting on the folder)
  run on a workstation ([`../pipelines.md`](../pipelines.md)).

If a job ever needs an export folder on the cluster, that is a new decision and Tony's.

## Storage: the shared research drive ("turbo")

Every workstation and the cluster mount the same volume, so nothing is copied back.

- **Write everything a session must read to turbo:** results, Slurm logs, the status file. A
  log left in the cluster home directory cannot be seen from a workstation.
- **The folder name contains a space.** Paths are absolute and quoted, always.
- **bugarach's folder** is `data/bugarach/` under the lab's turbo root, one dated folder per
  run. Proposed 2026-11-12; it does not exist yet.

## Rules a bugarach job follows

Each of these was earned in interface2 and is taken over as it stands.

1. **The job states its own verdict.** A check opens the job's output and writes
   `VERDICT: PASS`, `FAIL` or `FAILED-TO-RUN`. Exit code 0 says nothing: an array there once
   wrote 189 files of NaN and exited 0 on every task.
2. **Status is published to a fixed path** on turbo (`run_record/STATUS_<project>.txt` under
   the run's folder), so "how is the run doing" needs no job id.
3. **Memory and wall time are sized from a measured run,** never guessed. The `standard`
   partition bills on reserved memory once a job asks for more than 7 GB per core.
4. **Jobs survive a reboot.** Nodes are rebooted for patches. A search either resumes from
   what it has written or is short enough to rerun.
5. **The cluster checkout is read-only.** Clone, pull, run. Never commit there.
6. **Versions are pinned.** A module is loaded by exact version, never by its default.
7. **Nothing with a credential is written to turbo.** interface2's capture wrapper refuses to
   run without its scrubber; do not work around it.

## Not known yet

- **How Python is set up on the cluster.** interface2 runs only MATLAB there. Which Python
  module exists, and whether `uv` works on a login node, are the first lines of bugarach's
  first run sheet.
- **How long a search takes on a cluster node.** The one-overnight figure is from a 12-core
  workstation.
- **Whether a search resumes after being killed.**

## bugarach does not act in interface2

interface2's pages and scripts are read as reference (ADR-0007). A run sheet may call
interface2's status and capture scripts from Tony's own checkout on the cluster, with his
agreement; it never changes them.
