---
status: open
filed: 2026-08-28
---

# The freshness gate hard-stopped a review over five byte-identical files

`murderboard_freshness.sh` reported **STALE**, which the skill makes a hard stop —
*"Do not 'note it and continue'"* — and blocked the review of PR #292. The
vendored content was **identical to upstream, byte for byte**, and had been the
whole time.

## What was actually true

```
$ bash tools/murderboard_freshness.sh --refresh --verbose ; echo $?
--- !! MURDERBOARD IS STALE — update before relying on it ---
   vendored: 3593c44   upstream: d68d789
1
```

Against that, the diff of every vendored file to upstream `origin/main`, with the
stamp line — which upstream does not carry at all — removed:

| vendored file | lines differing from upstream |
| --- | --- |
| `docs/doc_review_process.md` | 0 |
| `tools/murderboard_freshness.sh` | 0 |
| `tools/murderboard_roster.sh` | 0 |
| `tools/murderboard_revendor.py` | 0 |
| `.claude/skills/murderboard/SKILL.md` | 0 |

And upstream agrees:

```
$ git -C ~/Developer/murderboard log --oneline 3593c44..origin/main -- \
    doc_review_process.md murderboard_freshness.sh murderboard_roster.sh \
    murderboard_revendor.py skills/murderboard/SKILL.md
(empty)
```

**No commit in that span touched any vendored file.** `3593c44` itself changed
`traffic.yml` and `metrics/`; the two commits after it changed `.claude-plugin/`,
`.github/workflows/ci.yml` and a traffic script. The review process, the roster,
the gate and the skill were untouched throughout.

`murderboard_revendor.py` had it right all along, and says so in the same tree:

```
$ python3 tools/murderboard_revendor.py --root . --check
murderboard  upstream f62acb3
  would re-copy (body changed): none
  stamp bumped only:    5 file(s)
```

## Why this matters more than a nuisance

The gate is a **hard stop by design**, and correctly so — a review run against a
stale process silently omits rules already paid for. But it fires on *stamp
inequality*, not on *content difference*, so **any** upstream commit makes every
consumer stale, whether or not it touched a vendored file. Upstream is an active
repo; its CI config and metrics move constantly.

The process file warns about exactly this failure, twice:

> *"noise is what gets a check switched off"*

> *"a gate that cries wolf gets bypassed"*

A gate that stops work over files that did not change teaches sessions to reach
for the override. The next genuinely stale copy will meet a session that has
learned the alarm is usually wrong.

**It also costs a real rebuild every time.** Clearing it requires a re-vendor PR
onto the default branch — the message says so, because vendoring onto a leaf
branch leaves every new worktree inheriting the old copy. That is a full
branch/PR/CI cycle to bump five comment lines.

## Options

1. **Compare content, not stamps.** The information is already in the tool that
   sits beside it: `murderboard_revendor.py --check` answers *"did any vendored
   body change?"* exactly. If the answer is no, the gate should pass — and say
   *"stamp is behind but content is current"* rather than blocking.
2. **Compare against the last commit that touched a vendored file**, instead of
   upstream `HEAD`. Cheaper than (1), and would have passed this case.
3. Leave the gate and accept periodic no-op re-vendor PRs. Honest, and the
   current state; the cost is one PR per unrelated upstream commit, plus the
   erosion above.

**This belongs upstream**, in `syncytium2/murderboard`, not patched here — the
gate is vendored and editing it in place is the one thing its own header forbids.
`docs/todo/2026-08-12-vendored-lit-tool-carries-personal-paths.md` is the
precedent for how this repo records an upstream-bound finding.

## Not to be confused with

`docs/todo/2026-08-26-murderboard-revendor-selftest-is-not-portable.md` — a
different defect in a neighbouring tool. Its two `--selftest` failures reproduce
on an unmodified primary checkout and are unrelated to this.
