@echo off
rem Launch tools\tune_learned_vs_coact.py detached from every terminal, for Task Scheduler.
rem
rem The launch path the 2026-09-17 GPU shakedown proved: 2,089 jobs over 13 h 53 min on WSMIP064,
rem unattended, with no session attached (HANDOFF-workstation-tuning.md). Register it as a task so
rem it is not a child of VS Code or of a Claude session:
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
setlocal
rem Before any shift: SHIFT moves %0 too, so %~dp0 afterwards names an argument, not this file.
set "HERE=%~dp0"
if "%~1"=="" (echo usage: launch_tuning_run_windows.cmd ^<name^> [tool arguments] & exit /b 2)
set "NAME=%~1"
shift
set "ARGS="
:collect
if "%~1"=="" goto run
set "ARGS=%ARGS% %1"
shift
goto collect
:run
cd /d "%HERE%.."
set "LOG=%USERPROFILE%\runs\%NAME%.log"
if not exist "%USERPROFILE%\runs" mkdir "%USERPROFILE%\runs"
echo ==== launched %DATE% %TIME% >> "%LOG%"
.venv\Scripts\python.exe -u tools\tune_learned_vs_coact.py --out "%USERPROFILE%\runs\%NAME%"%ARGS% >> "%LOG%" 2>&1
echo ==== exited %ERRORLEVEL% at %DATE% %TIME% >> "%LOG%"
endlocal
