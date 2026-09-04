---
status: open
filed: 2026-09-04
---

# A `# instrument:` line in a vendored copy is erased on the next re-vendor, and the fix is upstream

**If you are about to add an instrument-family declaration to a file carrying a
`vendored from <repo> @ <sha>` stamp, read this first.** Six files in this repo
already have one, six is more than half of what a re-vendor would silently revert,
and putting the line in the wrong *place* has already broken a gate once.

## What is settled, and already fixed

`bfbc375` gave seventeen instruments a `# instrument: <family>` line. **Five of the
seventeen went into vendored copies**, and a sixth file,
`.claude/hooks/send-goes-nowhere.py`, had the same collision.

> ⚠ **CORRECTION, 2026-09-04, same day.** The commit that filed this note — and PR
> #474's description with it — says that sixth file was "a second session repeating
> the mistake independently". **That is false, and the truth is worse for everyone
> downstream.** The declaration was not added here at all; it arrived with the file:
>
> ```
> $ git -C ~/Developer/armory show 548f734:.claude/hooks/send-goes-nowhere.py | head -2
> #!/usr/bin/env python3
> # instrument: verification
>
> $ git show 049864e:.claude/hooks/send-goes-nowhere.py | head -3
> #!/usr/bin/env python3
> # instrument: verification
> # vendored from armory @ 6fc2271 — do NOT edit here; ...
> ```
>
> Armory declares the family on line 2 of its own instruments. Line 2 is also the
> only line the vendoring stamp may occupy in a shebanged file. So **vendoring an
> armory instrument displaces the stamp by construction** — no session has to make
> a mistake for it to happen, and it will happen again for every consumer and every
> such file. Six armory instruments declare on line 2 today (`dragnet.py`,
> `instrument_ledger.py`, `mutation_check.sh`, `inline_asset_drift.py`,
> `vendor_reach.py`, `send-goes-nowhere.py`), so this is a structural collision
> between two conventions rather than an incident. Submitted to armory 2026-09-04;
> where the line should go is a convention call across armory, murderboard and
> interface2, and is not this repo's to make. The commit message is immutable and
> will keep saying the wrong thing — this paragraph is the correction of record.

Each was inserted at **line 2**, under the shebang and **above** the vendoring
stamp. Line 2 is the only line `murderboard_revendor.stamp_line_index` will read in
a shebanged file, so the stamp moved out of the one position its own writer looks
at. Measured, with the tool, not reasoned about:

```
$ python3 tools/murderboard_revendor.py --check --root .
  !! STAMP IN THE WRONG PLACE — the gate sees it, this tool will not
     touch it, so it would stay unbumped behind a green check:
     ['tools/murderboard_freshness.sh (stamp on line 3)',
      'tools/murderboard_roster.sh (stamp on line 3)',
      'tools/murderboard_revendor.py (stamp on line 3)']
```

Two instruments disagreed about the same files — `check_vendor_freshness.sh` scans
loosely and went on reporting *current*, while the tool that does the re-copying
refused to touch them. That is the `propagation` family describing its own
breakage, in the tool named after it, including its own file.

**Repaired in the same commit as this note**: the stamp is back on line 2 in all
six, with the declaration directly beneath it, and
`tests/test_instrument_families.py::test_a_declaration_never_displaces_a_vendoring_stamp`
asserts it through the re-vendor tool's own parser so the two cannot drift apart.

## What is NOT settled, and is the actual todo

**The declaration still does not survive a re-vendor.** `recopy_with_stamp` is
explicit about what it keeps — *"Upstream's content, carrying the local stamp
line"* — so every other local line, the declaration included, is replaced by
upstream's body. `.murderboard-vendor.json` carries `"adapted": []`, which is the
mechanism that would report the drift and refuse to overwrite. Confirmed after the
repair: `--check` now lists all three murderboard tools as *would re-copy (body
changed)*, and the body that changed is the one line we added.

Three ways out, and the third is the one to take:

1. **List them in `adapted`.** The tool then reports drift and refuses to
   overwrite. Rejected: it freezes a `propagation` gate against genuine upstream
   updates in order to protect an annotation. Wrong trade.
2. **Delete the declarations from vendored copies.** Honest, restores
   byte-identity, and loses the family for six instruments — five of which are the
   *most* travelled instruments here, and so exactly the ones an estate-wide ledger
   most wants classified.
3. **Ask the canonical source to declare.** ✅ The family belongs in the file, and
   for a vendored file the file is upstream's. When murderboard, interface2 and
   armory declare, every consumer inherits it for free and the local lines become
   redundant rather than lost — which is what a propagation instrument is supposed
   to achieve.

**Who to ask, and for what:**

| upstream | files here | family |
|---|---|---|
| `syncytium2/murderboard` | `tools/murderboard_freshness.sh` | propagation |
| | `tools/murderboard_roster.sh` | verification |
| | `tools/murderboard_revendor.py` | propagation |
| | `.claude/hooks/require-commit-before-message.sh` | concurrency |
| `interface2` | `.claude/hooks/no-heredoc-source.sh` | retrieval |
| | `.claude/hooks/session-start.sh` | **undeclared here on purpose** — retrieval |
| `syncytium2/armory` | `.claude/hooks/send-goes-nowhere.py` | **already declared upstream** — nothing to ask for; the ask is where the line goes, see the correction above |
| | `tools/show.py` | **undeclared here on purpose** — verification |

The two marked *on purpose* are the ones this repo did **not** annotate:
`session-start.sh` is upstream's re-copyable core and its own header says to keep it
intact, and `show.py`'s header says in terms *"treat this file as read-only"*.
Adding a seventh and eighth doomed line to make a count look complete is the thing
this note exists to stop.

Armory is the natural place to raise all three at once: its
`tools/instrument_ledger.py` is the consumer that wants the family, and its own
finding is that registered instruments travel and hand-invoked ones do not — every
file in the table above is a registered one.

## Two things found on the way, not part of this

- **`murderboard_revendor.py` defaults its root to its own directory.**
  `root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent`,
  so run from the repo root it looks for `.murderboard-vendor.json` in `tools/`,
  reports *no config found*, and exits — and `--config` with a relative path is
  resolved against that same wrong root, so it does not rescue you. `--root .` is
  the incantation. Upstream's, not ours.
- **Two vendored families are stale right now**: session-protocol is at `9df9a16`
  against upstream `80951ce`, and armory at `548f734` against `6fc2271`. Unrelated
  to the declaration, surfaced by running the gate, and left for whoever re-vendors.
