---
status: open
filed: 2026-08-27
---

# The commit gate loses your claim if the task text mentions a path

`tools/guard_local_board.sh` reads a board heading's identifier by dropping everything up
to the **last** slash on the line. Hosts may contain slashes, so the loop is deliberate.
But it runs across the *whole heading*, task description included — and a task description
that says `docs/`, `src/` or `learn/` is a path, not a host. The identifier goes with it.

**Seven of the 199 blocks on the live board are already parsed as the wrong worktree.**
None of them is a typo; every one is a session that claimed correctly and would have been
refused a commit.

```
heading                                                       parses as
### Tonys-MacBook-Pro/wip-modularity-port — validating the     Louvain
    STTC/Louvain port against MATLAB
### Tonys-MacBook-Pro/lanes-update — `docs/lanes.md` said      lanes.md`
    fan out, and the fan-out is over
### Tonys-MacBook-Pro/branch-survey — FINISHED — evaluated     worktrees,
    all branches/worktrees, find website workflow blockers
### Tonys-MacBook-Pro/detector-history — history of            modify
    coordination detection; where our six fit; keep/modify advice
### Mac/sweep-board-note — file the worktree-sweep/board       board
    gap found while closing out
### Tonys-MacBook-Pro/forks-next — evaluate what comes         forks.md
    next in docs/forks.md
### Tonys-MacBook-Pro/prior-art-cfar — the guard result        genomics
    against radar/sonar/astro/genomics prior art
```

## It is one day old, and it arrived inside a fix

The slash loop was added on 2026-08-26 by
[`4f25769`](https://github.com/syncytium2/bugarach/commit/4f25769) — *"A mention is not a
claim, and the gate could not tell the difference"* — which replaced a substring match:

```sh
-  if [ -n "$name" ] && grep -qF -- "$name" "$file"; then echo ALLOW; return; fi
+      if (index(s, "/")) { while (index(s, "/")) sub(/^[^\/]*\//, "", s) }
```

The old form was too loose: naming another worktree in a `Touches:` line counted as
claiming it. The new form is exact, which is right, and reads too much of the line while
getting there. So this is a regression introduced by a tightening, and the fix below keeps
every bit of the strictness — it only stops the parser reading past the identifier.

Worth noting the shape: the previous bug was *"accepts something it should not"*, and it
was found by reasoning about the check. This one is *"rejects something it should"*, and it
was found by tripping over it. The second kind does not surface from reading the code,
because the code looks correct and its tests pass.

## How it was found

Landing [PR #347](https://github.com/syncytium2/bugarach/pull/347), whose block was headed
`… — torch is declared, CI never installed it, learn/ never ran`. The trailing `learn/`
made the parse land on ` never ran`, whose leading space then matched
`sub(/[[:space:]].*$/, "", s)` and left the empty string. The gate refused the commit and
printed its standard lecture about claiming before starting — which had been done, hours
earlier, exactly as the briefing asks.

That is the part worth keeping in view. **The gate's failure mode is to accuse a session
that complied.** It is not a missed check; it is a false accusation with a paragraph of
prose behind it, and the natural response is `ALLOW_UNCLAIMED_BOARD=1` — which is the
override existing to keep the guard from being disabled wholesale, spent here on a bug.

## The fix

Two lines are in the wrong order. Take the first whitespace-delimited token, *then* strip
to its last slash:

```awk
    /^###[[:space:]]/ {
      s = $0
      sub(/^###[[:space:]]+/, "", s)
      sub(/[[:space:]].*$/, "", s)                                   # <-- moved up
      if (index(s, "/")) { while (index(s, "/")) sub(/^[^\/]*\//, "", s) }
      if (s == "") next
      ...
```

The identifier cannot contain a space, so taking the token first loses nothing, and the
slash loop still handles a host with slashes in it — `### some/host/with-slashes/my-worktree
— a task about docs/ and src/` parses to `my-worktree`.

Checked against the real board: **199 headings, 0 empty, and all seven above recover their
intended identifier.**

## The selftest gap, which is the more interesting half

`--selftest` has ten cases and they are good ones — two are adversarial (*"the repo name in
every path is not a claim"*, *"a prefix of another block is not a claim"*). Every case
drives `verdict()` through `claims_heading()`. **Not one heading in the fixtures contains a
slash anywhere but the host.** So the selftest passes, has always passed, and proves the
parser correct on the only inputs it was ever shown.

Whatever else is done, add the case that fails today:

```sh
  t "a path in the task text is not part of the id"  ALLOW  "$tmp/real.md" "known" "known" ""
  #   with the fixture heading: ### Mac/known — a task about docs/ and src/
```

A rule this repo already holds — a check that cannot fail is worse than no check — applies
to the checks themselves.

## Scope

- `tools/board_digest.sh` is **not** affected. It matches `/^### /` to find block
  boundaries and keeps whole blocks; it never extracts the identifier. The startup briefing
  has been showing these seven blocks correctly the whole time, which is why nobody noticed.
- The vendored `docs/session_protocol.md` does not define this parse. The gate is a
  bugarach-local addition, so the fix stays here and nothing needs re-vendoring.
- Nothing needs to change on the board. The seven headings are legitimate; the parser is
  what is wrong, and rewording them would be treating the symptom.
