# Architecture Decision Records

One decision per file, recorded when it is made. The form is borrowed from
`colonel_kernel`, which has been running it for fifty-odd decisions; the point of
copying it rather than inventing one is that Tony already reads that shape.

Where this sits against the rest of the tree:

- **[`docs/FOUNDATIONS.md`](../FOUNDATIONS.md)** — settled foundations and the reasoning
  behind them. Canonical; it wins over anything said in conversation and over anything
  here.
- **ADRs (this directory)** — individual decisions, as they are taken.
- **[`docs/todo/`](../todo/)** — open work items, one file each.

When an ADR changes a settled point in `FOUNDATIONS.md`, update `FOUNDATIONS.md` so the
two never disagree, and cross-reference them.

## Convention

- One decision per file, named `NNNN-title-in-kebab-case.md`, zero-padded, incrementing.
- **Michael Nygard template**: Title, Status, Context, Decision, Consequences.
- **Status** is `Proposed`, `Accepted`, `Deprecated`, or `Superseded by ADR-NNNN`.
- Accepted ADRs are immutable. To change a decision, write a new one that supersedes it
  and update the old one's status — do not edit the history.
- In-place amendments are allowed **only when they change no decision**: dated pointer
  notes recording who delivered it, a correction, or an implementation divergence.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-the-lab-server.md) | The lab server — training off the page, without changing what ships | Accepted |
| [0002](0002-the-sixth-detector-is-called-locust.md) | The sixth detector is called locust, not CICADA | Accepted |
| [0004](0004-ci-installs-torch-from-the-cpu-wheel-index.md) | CI installs torch, and takes it from the CPU wheel index | Accepted |

`0003` is reserved, not skipped. Nine files on `main` cite it for *"Parity was the
inheritance, not a standing contract"*, which is written and was green on the
`parity-was-the-inheritance` branch when PR #298 was closed unmerged. Until
[that question](../todo/2026-08-26-nine-files-name-an-adr-that-does-not-exist.md) is
answered the number stays held — filling the gap would break all nine citations.
