# The murderboard roster gate cannot see an archive whose name has underscores

**What happened, 2026-09-19.** The merge-gap addendum's run record named its role-report archive
`net_merge_gap_2026-09-19-roles/`, which existed and held all eleven non-empty reports.
`tools/murderboard_roster.sh check --require-reports` refused it:

    murderboard: report names a role-report archive that does not exist: netmergegap2026-09-19-roles/

**Why.** `reports_decl()` strips markdown emphasis from the line before reading the path —
`gsub(/[*`_|>]/, "", line)` — and the underscore in that character class is there for `_italic_`. A
directory name containing `_` is silently rewritten, so the gate looks for a path nobody wrote and
reports the archive as missing.

**Why it matters more than a naming annoyance.** This gate's whole purpose is the "cited but missing"
case: *"a record pointing at an archive that is not there is worse than one admitting it has none,
because it reads as the complete run."* The failure mode here is the inverse and just as bad — a
complete, preserved archive reported as missing. The honest response to a red gate is to look for the
missing reports; the response that makes it green is to rename the directory, which is what this
repository did. A reviewer who instead deleted the `reports:` line to quiet it would have turned a
complete run into an undeclared one, and the gate would have passed.

**Not fixed here.** `tools/murderboard_roster.sh` is vendored from syncytium2/murderboard (stamp on
line 1) and this repo does not edit vendored files in place. The fix belongs upstream: strip emphasis
only where it is emphasis — for example, drop the `_` from the character class, or unwrap
`` `backticks` `` and `*stars*` as pairs rather than deleting the characters wherever they fall.

**What this repository did instead:** renamed the archives to
`docs/reviews/net-merge-gap-2026-09-19-roles/` and `-round2-roles/`, and the record to
`net-merge-gap-2026-09-19.md`, so every path on the `reports:` line survives the strip. The parent
fair-comparison record passed only because its name happened to use hyphens.

**Not a sapper rule.** Sapper is a line matcher, and this is a defect in another tool's parser, not a
pattern in this tree's source. Filed here so the next person who meets a red roster gate on a green
archive knows to check the name before they go looking for missing reports.
