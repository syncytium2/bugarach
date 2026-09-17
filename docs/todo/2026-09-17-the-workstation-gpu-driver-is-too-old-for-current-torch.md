---
status: open
filed: 2026-09-17
---

# The workstation's GPU driver is too old for current torch, so its GPU work is pinned to torch 2.5.1 and Python 3.12

**Filed at Tony's instruction**, the day the tuning run moved from the CPU to the GPU on the Windows
workstation WSMIP064. The driver needs updating, and updating it needs admin rights.

## What was measured, 2026-09-17

The workstation has an **NVIDIA RTX A4000, 16 GB**, on driver **536.67** (2023; `nvidia-smi` reports
it). Windows' own adapter listing says 4 GB, but that field overflows; `nvidia-smi` is right.

| torch build | Python | result on driver 536.67 |
|---|---|---|
| 2.14.0+cu126 (current) | 3.14 | **cannot create a CUDA context**: `torch.zeros(3, device="cuda")` raises `CUDA error: CUDA-capable device(s) is/are busy or unavailable` (`cudaErrorDevicesUnavailable`). Same outside the tool sandbox; compute mode is `Default`. |
| 2.5.1+cu121 | 3.12 | works |

So the failure is the CUDA 12.6 runtime against a driver whose native CUDA version is 12.2, not the
GPU and not the machine. NVIDIA's CUDA toolkit release notes list the minimum driver for each CUDA
version; a driver from the R560 branch or newer covers 12.6.

## Why it matters

The GPU is what makes the tuning run practical. One untuned 900-step fit, same loop, same
recordings, measured 2026-09-17:

| where | seconds per fit | fits per hour |
|---|---|---|
| `chorus_norm`, CPU, torch 2.5.1, one process | 244 | 15 |
| `chorus_norm`, CPU, torch 2.14.0, 12 processes at once (300 steps, scaled) | 510 each | about 85 in all |
| `chorus_norm`, **GPU**, one process | **6.4** | **575** |
| `line_length`, GPU, one process | 10.4 | 358 |
| `tube`, GPU, 8 processes at once | 15.5 each | 1,904 in all |

More than one process on the GPU gained nothing for `chorus_norm` (406 to 412 fits per hour at
4, 8 and 16) or `line_length` (293 at 8): the one GPU is the limit. `tube` is small enough that 8 did.

## What staying on the old driver costs

- **GPU work here is pinned to torch 2.5.1 and Python 3.12**, while this repo's CI runs Python 3.11,
  3.13 and 3.14 with current CPU torch. Code that uses a torch feature newer than 2.5 fails on the GPU
  environment and nowhere else.
- **Every result from the GPU environment must record torch 2.5.1+cu121**, and cannot be mixed with
  fits from a different torch or from the CPU: the floats differ.

## The fix, and how not to lose a run to it

1. **Update the NVIDIA driver** to a current production branch that supports CUDA 12.6 or later. It
   needs admin rights: IT, or CyberArk elevation.
2. **If by elevation, plan for its expiry.** On 2026-09-17 an elevation ended by signing the user
   out about 12 hours later, which killed an overnight run (armory `FINDINGS.md` §20). Do the update
   early, and start nothing long in that session.
3. **Never mid-run.** A driver update resets the display driver, which ends every process using the
   GPU.
4. **Verify:** `%USERPROFILE%\venvs\bugarach-cuda\Scripts\python.exe -c "import torch;
   torch.zeros(1, device='cuda'); print('ok')"` (torch 2.14.0+cu126, Python 3.14) prints `ok`. Then
   the GPU work can move to the same Python and torch as everything else.
