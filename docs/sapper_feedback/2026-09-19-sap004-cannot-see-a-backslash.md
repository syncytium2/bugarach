---
rule: SAP004
status: done
filed: 2026-09-19
---

**What happened.** The fair comparison ran on a Windows workstation, and its summaries, review
reports and figure tools all passed through paths of the form `C:\Users\<name>\…` and
`\\wsl$\…`. SAP004 matches personal paths with forward slashes only, so none of them would have
been blocked at the commit. The report's own test
(`tests/test_build_fair_comparison_report.py`,
`test_no_personal_path_reaches_the_page_or_the_committed_files`) widened the pattern to both slash
forms and to the running machine's user name, but only for that report's files. A reuse review of
the report (round 2, role 7) called that a second copy of SAP004 covering one folder, where the gap
is repository-wide.

**Why it is wrong.** The repository is public, and a Windows session is as likely to write a
personal path as a Mac one. The rule's own comment records that its pattern was once believed to
cover personal paths and did not; this is the same shape, one separator over.

**Suggested fix.** Let SAP004's path alternatives take either separator, `[\\/]`, and add
`wsl\$` as an alternative. Self-test fixtures: a line holding `C:\Users\<name>\x` and one holding
`\\wsl$\Ubuntu\home\someone\x` must fire; `C:\Program Files\MATLAB\R2025b\bin\matlab.exe`, which
CLAUDE.md's launch recipe spells out, must not. Then have the report's test call the sapper
pattern rather than keep its own.

## What was done (2026-10-18, the armory session on the Mac)

SAP004 now matches a Windows home, `C:\Users\<name>`, with one backslash or two (the
JSON-escaped form), so the run records that carried it are caught. `Public` and `Default` are
Windows' own folders and pass, and so does a name that does not start with a letter or digit, so
`C:\\Users\\...` in `src/bugarach/paths.py`'s docstring is not a hit.
`tests/test_sapper.py::test_sap004_sees_a_windows_home` holds the vectors, including the MATLAB
path from CLAUDE.md that must not trigger it.

The 29 lines in the tree are replaced, by `%USERPROFILE%` (and the project folder Claude names
after the home, `c--Users-<user>-...`, by `c--Users-USER-...`). History is not rewritten:
Tony, 2026-10-18, *"leaky path is not scary, just minimize instances somehow. not rewriting
history for an obscure path."* The example above now reads `<name>` rather than a made-up
name, so this file does not trip the rule it asks for.

Not done: the `\\wsl$\` form, which no tracked file carries, and pointing
`tests/test_build_fair_comparison_report.py` at this pattern.
