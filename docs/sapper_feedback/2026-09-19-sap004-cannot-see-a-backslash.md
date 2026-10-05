---
rule: SAP004
status: open
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
`wsl\$` as an alternative. Self-test fixtures: a line holding `C:\Users\someone\x` and one holding
`\\wsl$\Ubuntu\home\someone\x` must fire; `C:\Program Files\MATLAB\R2025b\bin\matlab.exe`, which
CLAUDE.md's launch recipe spells out, must not. Then have the report's test call the sapper
pattern rather than keep its own.
