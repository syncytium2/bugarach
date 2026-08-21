# Murderboard run — docs/needs/mechanism-changes-need-a-gate.md
- upstream:  syncytium2/murderboard @ 57445b4
- vendored:  a8bace5fa7092756c0dae90c64ee4c4c465c85c7
- freshness: current
- artifact:  docs/needs/mechanism-changes-need-a-gate.md (bdf3af1 -> 49c7f71)
- roles:     11 of 11 run
- rounds:    2 blind verify rounds to clean

**Mode.** Single-pass self-review walking every role's checklist in turn, not an
11-agent fan-out. The process permits this for a small deliverable and forbids
dropping a role either way; this is a 1 400-word prose proposal with no figures, no
new analysis code and no external citations. Stated here because a dropped role and
a clean role are indistinguishable in a report that does not say which mode it ran.

## Role ledger

| # | role | findings | what was checked |
|---|---|---|---|
| 1 | Claim & data verifier | **2 blocking** | Every hash, count and factual claim recomputed against the tree — see ledger below |
| 2 | Citation & reference validator | 0 | No external references. Every internal pointer (`CLAUDE.md`, `.claude/settings.json`, `package.json`, `require-commit-before-message.sh`) resolved against the working tree; all four exist |
| 3 | Consistency auditor | **2** | Term `estate` used against its own definition; "most worth arguing with" / "most likely to be wrong" made the same point twice, 40 lines apart |
| 4 | Adversarial reviewer | **2** | "not at all" overstated — sapper does scan those diffs; and the draft made its proposal without stating the objection a hostile reader raises first (vendored files trip the gate constantly) |
| 5 | Line editor | 1 | The redundancy above; otherwise each sentence asserts one thing. No jargon left undefined after role 8's fix |
| 6 | Methods / domain expert | 0 | No statistical method, library or numerical routine underlies this document. Nothing to ground in. The one mechanism described (a staged-diff content rule) is checked against sapper's actual behaviour, which it matches |
| 7 | Reuse auditor | 0 | Checked whether the proposal re-invents something the estate already has: it explicitly builds on sapper's existing rule shape and on `ALLOW_UNCLAIMED_BOARD`'s escape-hatch pattern rather than proposing a parallel mechanism. `0-REVIEW/` was checked as a possible existing home for cross-repo proposals and is slice submissions, not process |
| 8 | Naive-reader accessibility | **1 blocking** | Read cold as a maintainer of another repo: `sapper`, `murderboard` and `estate` were all used undefined in the first 20 lines, and all three are local vocabulary |
| 9 | Density & figure-first | 0 | Prose is right here: the document is an argument and a request for comment, not a result. The one comparison that benefits from structure (the two cases) is already a table, and the proposed gate's output is already shown as a code block rather than described |
| 10 | Build & craft gate | 0 | Mechanical pass on the file: code fences balanced (2), heading levels consistent (h1/h2 only), table columns consistent across all 4 rows, no TODO/TBD/FIXME, every backticked path resolves in the tree. Re-run in full on the corrected file |
| 11 | Argument order | 0 | Spine: hole → its cost → why the obvious fix fails → the proposal → its cost → what it does not claim → what is asked. Arc used: problem → cost → fix → residual risk. Opens on the problem, not on history or scope |

## Claim ledger (role 1)

| quoted | source | recomputed | verdict |
|---|---|---|---|
| the hook was written by a session building neuronal assemblies | Tony, in conversation | hook commit 2026-08-17 10:01; every assembly commit 2026-08-18 | **MISMATCH — claim removed** |
| postdeploy added in commit `946b4b7` | draft | `git log -S'"postdeploy"' -- package.json` -> `b4973df` | **MISMATCH — corrected** |
| "three days apart" | draft | 2026-08-17 and 2026-08-18 | mismatch — corrected to "a day apart" |
| eleven murderboard roles | `murderboard_roster.sh count` | 11 | match |
| hook has no network / no writes / no privilege | read of all 132 lines + grep for curl/wget/ssh/sudo/rm/git-write | none present | match |
| selftest proves six branches | ran `--selftest` | 6 checks, all PASS | match |
| commit `0dbc37c` carried six other files | `git show --stat` | 7 files total: hook + 6 | match |
| `ALLOW_UNCLAIMED_BOARD=1` is an existing escape hatch | `tools/guard_local_board.sh` | present, documented as "ESCAPE HATCH, deliberate" | match |
| CLAUDE.md opens by recording a session that ignored it | `CLAUDE.md` | "A session on 2026-08-13 went the whole way without reading it" | match |
| "prefer adding a sapper rule over adding prose" | `CLAUDE.md` | verbatim | match |
| sapper runs on every commit and in CI | `.githooks/pre-commit`, `tests/test_sapper.py` | both confirmed | match |

## The finding that mattered

**Role 1, blocking.** The draft's headline attribution — that the message-gate hook
was written by a session whose task was building neuronal assemblies — is not
supported by the record, and the dates point the other way: the hook landed
2026-08-17, the assemblies work is all 2026-08-18. It came into the draft from
conversation and was about to be published to other repos as established fact about
a colleague's session.

Replaced with what the commit itself proves: a vendoring-maintenance commit that
also installed a session-wide behavioural gate. The argument is unchanged and
rests on evidence anyone can re-check.

⚠ **Residual, for Tony:** your recollection may still be right about *which session*
— git shows which commit, not which conversation. The document no longer makes the
claim either way. If you want the assemblies link stated, it needs a source git can
show, or it ships flagged as recollection.

## Adjudications

| finding | role | action |
|---|---|---|
| unverifiable attribution to an assemblies session | 1 | **fixed** — removed, replaced with commit contents |
| wrong commit hash for postdeploy | 1 | **fixed** — `946b4b7` -> `b4973df` |
| "three days apart" | 1 | **fixed** — "a day apart" |
| "mechanisms not at all" overstates | 4 | **fixed** — softened, with the accurate exception stated |
| strongest counter-argument absent | 4 | **fixed** — new section, states the vendoring cost as unresolved |
| local vocabulary undefined for a cross-repo reader | 8 | **fixed** — three-term glossary added above the fold |
| `estate` used against its own definition | 3 | **fixed** — opening line reworded |
| same point made twice | 3, 5 | **fixed** — first instance cut |
