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
