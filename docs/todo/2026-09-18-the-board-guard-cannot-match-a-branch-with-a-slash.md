---
status: open
filed: 2026-09-18
---

# The local-board guard cannot match a branch whose name contains a slash

**Found** by WSMIP064 on 2026-09-18, committing a board claim from the primary checkout on branch
`board/claim-fair-comparison-run`.

`tools/guard_local_board.sh`, `claims_heading`, strips a block heading down to the text after its
**last** `/` and compares that with the worktree's name and its branch. A branch named
`board/claim-fair-comparison-run` is compared whole, but the heading
`### WSMIP064/board/claim-fair-comparison-run` reduces to `claim-fair-comparison-run`, so no heading
can ever match it. The guard's own advice (*"Add a block: ### Mac/board/claim-…"*) is a block it then
refuses. This repo's conventions ask for slashed branch names (`nets/<slug>`, `opt/<slug>`,
`goals/…`), so every session working from the primary checkout on such a branch hits it.

**Workaround used:** a heading naming the worktree directory instead (`### WSMIP064/bugarach — …`),
which the guard does accept.

**Likely fix:** strip only the first `<host>/` segment of the heading, then compare the rest with the
branch, and add the case to `--selftest`.
