---
status: open
filed: 2026-09-19
---

# The roster gate cannot find a role archive named the way the skill says to name it

waiting: nothing here — the fix is upstream (syncytium2/murderboard), since `murderboard_roster.sh` is
vendored and is not edited in place.

The murderboard skill (step 4b) names the role-report archive `docs/reviews/<artifact-stem>_<YYYY-MM-DD>-roles`.
`murderboard_roster.sh`'s `reports_decl` strips `*`, backquote, `_`, `|` and `>` from the `reports:` line
before resolving it (`gsub(/[*`_|>]/, "", line)`), so the declared path loses its underscore and never
resolves. `check --require-reports` then fails with "report names a role-report archive that does
not exist", on a run whose eleven reports are all on disk.

Seen on the replicate report's run record (`docs/reviews/replicate1-report_2026-09-19.md`), which
renamed its archive `replicate1-report-2026-09-19-roles/` to pass. Earlier records dodged it by
choosing hyphenated stems (`tube-self-supervised-2026-09-17-round4-roles/`), which is why it went
unnoticed.

**Fix upstream:** strip only the markdown that can wrap the value (emphasis markers around the whole
value, backquotes), not underscores inside a path; add a selftest with an underscore in the archive
name. Then re-vendor.
