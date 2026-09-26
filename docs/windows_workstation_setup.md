# Running bugarach's Python on a Windows workstation, GPU included

> **Written for the other Windows workstation (WSMIP065)**, by a session on WSMIP064 on
> 2026-09-17, at Tony's request: *"write this up for the other workstation to save time."* It is
> the route WSMIP064 took in one morning, after losing a night to the route before it. Working
> material, not murderboarded. Every number was measured on WSMIP064 and **will differ on your
> machine**. The steps are what carries over.

Abbreviations: **WSL**, Windows Subsystem for Linux; **CUDA**, NVIDIA's GPU computing platform;
**uv**, Astral's Python installer and package manager.

## The short version

1. **Do not use WSL.** Native Windows Python, installed per user with `uv`, needs no admin rights.
2. **Check the NVIDIA driver before blaming anything else.** A driver older than the CUDA build of
   torch reports the GPU as *"busy or unavailable"*, which reads like a hardware or permissions
   problem and is not one.
3. **Updating the driver needs admin rights, and an admin elevation ends by signing you out.** Plan
   for that before you ask for one.

## 1. Why not WSL

WSMIP064 set up WSL2 on 2026-09-16 and lost the overnight run on it. Two failures, either one enough:

- **An elevation's expiry signs you out, and WSL goes with the session.** The admin rights used to
  install WSL expired about 12 hours later, and the CyberArk agent (`vf_agent.exe`) signed the user
  out at 01:57. That closed VS Code and the Claude Code sessions, and stopped WSL with the run inside
  it. A systemd unit inside WSL would not have survived either, because WSL belongs to the signed-in
  user.
- **Afterwards, WSL2 would not start at all**: `Wsl/Service/CreateInstance/CreateVm/HCS/0x80070569`,
  *"the user has not been granted the requested logon type"*. Fixing that needs IT.

It was also slower: a lone fit took 1.25 to 1.4 times the Mac's time (`line_length` 3.3 times), and
with 22 fits at once each took about 4 times its lone time. The full account, and how to plan around an elevation, is in armory's `FINDINGS.md`
§20 (`syncytium2/armory`, private).

## 2. Python, without admin rights

In PowerShell:

```powershell
Invoke-RestMethod https://astral.sh/uv/install.ps1 -OutFile "$env:TEMP\uv-install.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:TEMP\uv-install.ps1"
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
uv python install 3.14 --default
```

`--default` also installs `python.exe` and `python3.exe` in `%USERPROFILE%\.local\bin`, which the
installer adds to your user PATH. **The `python3` name matters**: this repo's git hooks call
`python3`, and without it a commit from Git Bash skips the quote check and sapper. It is marked
experimental and prints a warning; it worked. On WSMIP064 the CyberArk agent blocked none of it.

## 3. A virtual environment in your worktree

From the worktree, **install torch first, from the CUDA index**, then the repo:

```powershell
uv venv .venv --python 3.14
uv pip install --python .venv\Scripts\python.exe torch --index-url https://download.pytorch.org/whl/cu126
uv pip install --python .venv\Scripts\python.exe -e ".[ui,dl,docs,surrogates]" pytest pytest-xdist playwright
```

For a CPU-only machine use `https://download.pytorch.org/whl/cpu` instead. These extras are CI's;
they leave out the `dev` extra's `pyspike`, which compiles C code and did not build under WSL. CI
tolerates its absence, and nothing under `src/` imports it. On WSMIP064 the environment built in
under a minute.

**Windows starts worker processes by spawning, not forking.** A tool that runs work in parallel must
keep its worker a top-level function and its entry point under `if __name__ == "__main__":`.
`tools/tune_learned_vs_coact.py` already does: its 10 tests pass on native Windows, and its
`--quick` mode ran 69 jobs and resumed with nothing rerun.

## 4. Check the GPU and its driver

```powershell
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
.venv\Scripts\python.exe -c "import torch; torch.zeros(1, device='cuda'); print('ok')"
```

⚠ **Windows' own adapter listing understates memory.** It reported the 16 GB RTX A4000 as 4 GB;
`nvidia-smi` is right.

**If the second line prints `ok`, skip to section 6.** If it raises
`CUDA error: CUDA-capable device(s) is/are busy or unavailable`, compare the driver's version with
the CUDA version of your torch (`torch.version.cuda`). On WSMIP064:

| driver | torch | result |
|---|---|---|
| 536.67 (2023; CUDA 12.2) | 2.14.0+cu126, Python 3.14 | the error above; the same outside the tool sandbox, with compute mode `Default` |
| 536.67 | 2.5.1+cu121, Python 3.12 | works: a stopgap if you cannot update the driver |
| **582.78** | **2.14.0+cu126, Python 3.14** | **works** |

## 5. Update the driver (admin rights)

**Before asking for elevation, write down when it will expire** (WSMIP064's was granted for 2 hours
on 2026-09-17; the one before ended in a sign-out about 12 hours after it was granted), and start
nothing long in that session. Close anything using the GPU:
the update resets the display driver, which ends every process that holds it. MATLAB counts, so check
`nvidia-smi` for compute processes first.

For RTX workstation cards (RTX A-series and Quadro), the current production branch on 2026-09-17 was
**R580 U11, version 582.78**, released 2026-07-30. Check NVIDIA's
[branch history](https://www.nvidia.com/en-us/drivers/rtx-enterprise-and-quadro-driver-branch-history/)
for anything newer. A GeForce card needs a different driver from NVIDIA's driver page.

```powershell
$dir = "$env:USERPROFILE\installers"; New-Item -ItemType Directory -Force $dir | Out-Null
$f = "$dir\582.78-quadro-rtx-desktop-notebook-win10-win11-64bit-international-dch-whql.exe"
curl.exe -L --fail -o $f "https://us.download.nvidia.com/Windows/Quadro_Certified/582.78/582.78-quadro-rtx-desktop-notebook-win10-win11-64bit-international-dch-whql.exe"
(Get-Item $f).Length                  # 725128928 bytes
Get-AuthenticodeSignature $f          # Valid, CN=NVIDIA Corporation
(Get-FileHash $f -Algorithm SHA256).Hash
# 7DA29A9E9F367C29C9911ED4141AF14ABECCE4AB48958FAD673AEF94CF7809A2
Start-Process -FilePath $f -ArgumentList '-s','-noreboot' -Verb RunAs -Wait -PassThru
```

`-Verb RunAs` raises the admin prompt; approve it. `-s -noreboot` installs silently. On WSMIP064 it
exited 0 after 4 minutes, the screen went dark briefly while the display driver swapped, VS Code and
the Claude Code session survived it, and **no reboot was needed** for CUDA to work. Then run section 4
again.

## 6. What to expect from the GPU

Measured on WSMIP064 with a copy of `bugarach.learn.train.train`'s optimisation loop, whose only
change was moving the model and each batch onto the GPU. **`train.py` itself has no GPU option yet**;
adding one is the tuning run's next step, on branch `tune-learned-vs-coact`. Each row is one untuned
fit of 900 steps.

| model | where | seconds per fit | fits per hour |
|---|---|---|---|
| `chorus_norm` | CPU, one process (torch 2.5.1) | 244 | 15 |
| `chorus_norm` | CPU, 12 processes at once (torch 2.14.0; timed at 300 steps and scaled) | about 510 each | about 85 in all |
| `chorus_norm` | **GPU, one process** | **6.4** | **575** |
| `line_length` | GPU, one process | 10.4 | 358 |
| `tube` | GPU, one process | 4.2 | 942 |
| `tube` | GPU, 8 processes at once | 15.5 each | 1,904 in all |

**One process saturates the GPU for the larger models.** `chorus_norm` managed 406 to 412 fits per
hour at 4, 8 and 16 processes, against 575 alone, and `line_length` 293 at 8 against 358 alone.
`tube` is small enough that 8 processes help. Each process used under 0.1 GB of GPU memory, so memory
is not the limit. **Measure on your own machine** before choosing a process count: the GPU, CPU and
memory all differ.

**Native Windows CPU is slow for torch.** One `chorus_norm` step took 0.34 s on torch 2.14.0's Windows
CPU build, about twice the Mac's time per fit. If a Windows workstation has a working GPU, use it.

## 7. Keeping a long run alive

- **Nothing in your desktop session survives a sign-out**, including a hidden `Start-Process`
  launcher. Start long runs from Task Scheduler under your own account, which needs no admin, and
  write progress to a file you can read from anywhere.
- **Make runs resumable**, with atomic result files, so that a sign-out costs time, not results.
- **Outputs go outside the repo** (`%USERPROFILE%\runs\`), never in `%TEMP%` or a session scratchpad.
  That makes them durable on **one disk**, which is not the same as readable: section 8.

## 8. Make a long run's status readable from anywhere

**Why.** On 2026-09-16 a detached run wrote `progress.json` into `~/runs/`, the session that
launched it was archived at 01:56, and the next morning nobody could say whether the run was alive:
the answer was on one disk and the person asking was on a phone (armory finding 21). The darkroom is
mounted on every machine and syncs, so the status goes there, stamped with its age.

**The tool** is `tools/mirror_run_status.py` (on `main` since #649). It needs no venv, but it must run
**from a checkout**, because it loads `src/bugarach/paths.py` relative to itself. Read its docstring.
It copies `progress.json` into a darkroom folder, with `mirror.json` and a one-line `STATUS.txt`
saying when it copied the file, how old the file already was, and from which host. `STATUS.txt`
says `STALE` past 15 minutes, and says so plainly if there is no `progress.json` yet, so the mirror
can be scheduled before the run starts, which is the safer order.

**Claim the darkroom folder first**, on `docs/SESSIONS.md` and the machine-local board (CLAUDE.md).

**And give it `--archive-as <dated-name>`, so the finished run goes to Dropbox by itself.**
(Tony, 2026-09-21: *"ensure that future runs go straight to repo and dropbox."* The weekend's two
runs sat in `~/runs` until a session copied them by hand; one run's chosen models were found on one
disk.) Once the run writes `results.json`, the same scheduled task hands it to
`tools/archive_run.py`, which puts the whole run under `<darkroom>/bugarach/runs/<name>/` with the
bulk folders packed, verifies every file, and records it in `ARCHIVED.json`. That happens once. The
repo half needs a session: the briefing lists every finished run not yet in the repo, and
`python3 tools/archive_run.py <run> --name <name> --to-repo` stages it for a normal branch and PR.
**Raise the task's `-ExecutionTimeLimit` when you add it**, to 60 minutes: packing a run's scores
(1.1 GB on the weekend's) takes far longer than the 2 minutes the mirror alone needs, and a task
killed mid-pack on every tick never finishes. `-MultipleInstances IgnoreNew` already keeps a second
tick from starting while the first is still packing.

### Proven on WSMIP065, 2026-09-18

The run this watches: the goal-2 replicate, launched as `bench-replicate1` through
`tools\launch_tuning_run_windows.cmd`, which writes to `%USERPROFILE%\runs\<name>\`. Claimed in #651.
Every path below is the one used; `$env:USERPROFILE` is spelled out only because this repository is
public.

```powershell
$py   = (& "$env:USERPROFILE\.local\bin\uv.exe" python find 3.14)   # absolute: ...\uv\python\cpython-3.14-windows-x86_64-none\python.exe
$tool = "$env:USERPROFILE\bugarach\bugarach-worktrees\weekend-runs\tools\mirror_run_status.py"
$run  = "$env:USERPROFILE\runs\bench-replicate1"
$log  = "$env:USERPROFILE\runs\mirror-bench-replicate1.log"
& $py $tool --selftest                        # selftest: 6 checks, 0 failures
$cmdline  = "/c `"`"$py`" `"$tool`" `"$run`" --into 2026-09-18-replicate-run-status >> `"$log`" 2>&1`""
$action   = New-ScheduledTaskAction -Execute "conhost.exe" -Argument "--headless cmd.exe $cmdline"
$trigger  = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 14)
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 2) -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "bugarach-mirror-bench-replicate1" -Action $action -Trigger $trigger -Settings $settings -Force
Start-ScheduledTask -TaskName "bugarach-mirror-bench-replicate1"
Get-Content $log -Tail 1                      # mirrored to <darkroom>\2026-09-18-replicate-run-status  source age: absent
```

The variables are expanded when the task is registered, so the task holds absolute paths and needs
nothing from your shell. No admin rights: the task runs as you, with an interactive logon. What the
proof settled:

- **`BUGARACH_DARKROOM` was not needed.** It is unset for the user and the machine
  (`[Environment]::GetEnvironmentVariable('BUGARACH_DARKROOM','User')` is empty), and the task still
  found the darkroom through `%LOCALAPPDATA%\Dropbox\info.json`. If your machine needs it, set it
  with `[Environment]::SetEnvironmentVariable('BUGARACH_DARKROOM', '<path>', 'User')`, which a task
  inherits. A `$env:` in your shell is not inherited, and the tool then exits 2 and writes nothing.
- **Prove a tick by its output.** `Get-ScheduledTaskInfo` reported the old `LastRunTime` for about
  three minutes after a manual run; the log line and `STATUS.txt`'s own timestamp were immediate. A
  wait loop keyed on `LastRunTime` hung for exactly that long.
- **Both branches were proven through the task, not only by the selftest:** "absent" with no run
  yet, and a present `progress.json`, which was copied byte for byte with a 0.9 s source age. The
  file used for that proof was labelled as not a run, and was removed from both places afterwards.
- **Enabling a task after its start time has passed fires it at once**, because of
  `-StartWhenAvailable`. That is harmless here, but expect an extra log line.
- **The logon is interactive, the same as the tuning launcher's**: if you are signed out, both
  stop. `STATUS.txt`'s timestamp then goes old, which is itself the signal. `copied_at` is the
  mirror's heartbeat; the file's age is the run's.
- The launcher writes the run's log **beside** the run folder (`%USERPROFILE%\runs\<name>.log`),
  not inside it, so the mirror's `--also` does not reach it as written.

### For WSMIP064: the fair comparison launched 2026-09-18 at 16:14

That run already copies `progress.json` into `<darkroom>/bugarach/archive/2026-09/2026-09-18-fair-comparison-run/`
itself, through the tuning tool's `--mirror`, at least once a minute. That copy is written **by the
run's own driver**, so if the driver dies it stops, and a reader has to notice that its `at` has gone
old. The scheduled mirror is the independent check: a separate process with a one-line verdict. Two
constraints shape it:

- **Do not add files to the running worktree** (`tune-bench-comparison`'s handoff: no changes to
  `tools/` or `src/` until the run ends). Run the tool from the primary checkout after `git pull` on
  `main`.
- **Do not write a second `progress.json` beside the run's own.** Mirror into a subfolder,
  `external/`, of the folder already claimed in #648, and add that subfolder to the claim's
  **Writes** line.

```powershell
git -C "$env:USERPROFILE\bugarach\bugarach" pull --ff-only
$py   = (& "$env:USERPROFILE\.local\bin\uv.exe" python find 3.14)   # an absolute path, not the Store alias
$tool = "$env:USERPROFILE\bugarach\bugarach\tools\mirror_run_status.py"
$run  = "$env:USERPROFILE\runs\fair-comparison-2026-09-18"
$log  = "$env:USERPROFILE\runs\mirror-fair-comparison-2026-09-18.log"
& $py $tool --selftest                        # expect: selftest: 6 checks, 0 failures
$cmdline  = "/c `"`"$py`" `"$tool`" `"$run`" --into 2026-09-18-fair-comparison-run/external >> `"$log`" 2>&1`""
$action   = New-ScheduledTaskAction -Execute "conhost.exe" -Argument "--headless cmd.exe $cmdline"
$trigger  = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 14)
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 2) -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "bugarach-mirror-fair-comparison" -Action $action -Trigger $trigger -Settings $settings -Force
Start-ScheduledTask -TaskName "bugarach-mirror-fair-comparison"
Get-Content $log -Tail 1                      # expect: mirrored to <darkroom>\...\external  source age: <n> s
```

Then open `STATUS.txt` in the folder that log line names: its first line should carry a timestamp
from the last minute and `WSMIP064`. If the primary checkout is somewhere else on WSMIP064, only
`$tool` changes. Run `--selftest` before scheduling. Before its fix, `--into /tmp/x` escaped the
darkroom on Windows (to `C:\tmp\x`), and the selftest was what caught it.

**When the run ends,** delete the task (`Unregister-ScheduledTask -TaskName <name> -Confirm:$false`)
and release the darkroom claim.
