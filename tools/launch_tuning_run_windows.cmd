@echo off
rem Launch tools\tune_learned_vs_coact.py detached from every terminal, for Task Scheduler.
rem
rem The launch path the 2026-09-17 GPU shakedown proved: 2,089 jobs over 13 h 53 min on the
rem workstation, unattended, with no session attached (HANDOFF-workstation-tuning.md). Register it
rem as a task so it is not a child of VS Code or of a Claude session:
rem
rem   schtasks /create /tn bugarach-tune-<name> /sc once /st 23:59 /f ^
rem     /tr "conhost.exe --headless cmd.exe /c \"%USERPROFILE%\bugarach\bugarach-worktrees\<worktree>\tools\launch_tuning_run_windows.cmd\" <name> <tool arguments>"
rem   schtasks /run /tn bugarach-tune-<name>
rem
rem Arguments: %1 = the run's name (its folder under %USERPROFILE%\runs), then the tool's own
rem arguments, e.g.  bench-v1 --device cuda --gpu-jobs 2 --jobs 12
rem Resumable: run it again with the same name and finished jobs are skipped. Delete the task when
rem the run ends (schtasks /delete /tn bugarach-tune-<name> /f), or it fires again at 23:59.
rem Do not change tools\ or src\ in the worktree while it runs: a resume would load the new code, and
rem the tool refuses a changed declaration.
rem
rem COMMAS, and why the argument tail is taken whole. cmd treats a comma as an argument separator,
rem so an unquoted list arrives already split: `--detectors coact,loco,sce` reached this script as
rem four arguments rather than two, and argparse refused the run before anything was written. Both
rem workstations hit it on 2026-09-18 and both launched through a machine-local wrapper that quoted
rem the list. The tail is now taken verbatim from %*, which keeps the separators as they were typed,
rem instead of being rebuilt token by token with SHIFT. Either form arrives as one argument now.
rem
rem CHECK BEFORE YOU SCHEDULE: set BUGARACH_LAUNCH_DRYRUN=1 and this prints the exact command it
rem would run, then exits -- nothing written, nothing started. Worth one run per task registration,
rem because the failure it guards against was a task that fired at 23:59 and died in argparse.
rem
rem One character the run name may not carry, since the tail is found by locating the name in the
rem raw command line: a space. It is refused below with a message rather than silently mis-split.
setlocal EnableDelayedExpansion
rem %~dp0 must be read before anything touches the argument list.
set "HERE=%~dp0"
if "%~1"=="" (echo usage: launch_tuning_run_windows.cmd ^<name^> [tool arguments] & exit /b 2)
set "NAME=%~1"
echo(!NAME!| findstr /c:" " >nul && (echo error: the run name may not contain a space: !NAME!& exit /b 2)

rem %* is the command line as typed -- commas, quotes and all. Drop the leading run name from it,
rem rather than reassembling the rest argument by argument, which is what split the lists.
set "ALLARGS=%*"
set "ARGS=!ALLARGS:*%NAME%=!"

cd /d "%HERE%.."
if defined BUGARACH_LAUNCH_DRYRUN (
  echo .venv\Scripts\python.exe -u tools\tune_learned_vs_coact.py --out "%USERPROFILE%\runs\!NAME!"!ARGS!
  endlocal & exit /b 0
)
set "LOG=%USERPROFILE%\runs\!NAME!.log"
if not exist "%USERPROFILE%\runs" mkdir "%USERPROFILE%\runs"
echo ==== launched %DATE% %TIME% >> "!LOG!"
.venv\Scripts\python.exe -u tools\tune_learned_vs_coact.py --out "%USERPROFILE%\runs\!NAME!"!ARGS! >> "!LOG!" 2>&1
echo ==== exited %ERRORLEVEL% at %DATE% %TIME% >> "!LOG!"
endlocal
