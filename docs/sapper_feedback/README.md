# sapper feedback

One file per finding — a new-rule request, a disputed rule, or a trap that
bit a session and should become a check. Same shape as interface2's
`docs/sapper_feedback/`: concurrent sessions never conflict because each
files its own dated file.

Filename: `YYYY-MM-DD-<slug>.md`. Frontmatter:

```
---
rule: SAPxxx | none-yet
status: open | done
filed: YYYY-MM-DD
---
```

Body: **What happened** (the incident, concretely), **Why it is wrong / what
is missing**, **Suggested fix** (ideally a regex + known-good exceptions).
Answers are appended inline and `status:` flips to `done`. A rule ships only
with self-test fixtures proving it can fire (`tools/sapper.py --selftest`).
