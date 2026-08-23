# Murderboard run — docs/reaper_handoff.md

## The headline number was wrong, and only recomputation found it

The draft opened on a measurement: *"median useful life of a worktree: ten minutes."*
It was the load-bearing fact — the whole argument is that worktree life is a task and
cleanup was modelled as a session-end ceremony, so the two differ by an order of
magnitude. Role 1 recomputed it instead of re-reading it, and the distribution is not
what the claim said:

```
under 20 min  13  #############
20–60 min      1  #
1–4 h          2  ##
4–24 h         7  #######
over a day     4  ####

n = 27   median 37 min   p25 5 min   p75 750 min   mean 825 min
```

**The median is 37 minutes.** "Ten minutes" was roughly the median of the *short mode*
(median of those under an hour: 7 min) presented as the median of the population. The
distribution is sharply bimodal — 13 worktrees under twenty minutes, 11 over four hours,
one solitary case in the 20–60 minute band — so no single number describes it, which is
exactly why quoting one hid the error. The mean, 825 minutes, describes no worktree that
ever existed.

The argument survives, and is arguably better stated by the true shape: half the
worktrees were used for under twenty minutes, and the rest are session-scale. But the
number had already **shipped** — into `tools/merge_when_green.sh`'s header comment and
`docs/git_workflow.md`, both landed on `main` in PR #240 — so this run's fixes extend
beyond the artifact to the two files that repeated it.

## What else the roles caught

Two more findings would have reached a reader as working instructions:

**The evaluation snippet in §7 counted the primary checkout.** It is the command an
interface2 session is told to run to decide whether this is worth building, and it
reproduced the exact bug §4 of the same document warns about — the primary checkout is
the first row of `git worktree list`, not the tree you are standing in. It reported 20
removable worktrees where the true figure is 19. Fixed and then **run verbatim from the
document** against interface2: 19 rows, all `dirty=0`.

**A false claim about interface2's history.** The draft said `main` is linear, citing
"100 of the last 100 commits are non-merges". That reading was wrong — `git log
--no-merges -100` applies its limit *after* filtering, so it proves only that 100
non-merge commits exist. Measured properly by parent count, **22 of the last 100 commits
on interface2's `main` are merges**. The claim it supported (that branches land by
fast-forward) is still the best reading of the evidence, but it is now stated as
inference, with what was actually observed, and with an explicit note that nobody watched
a branch land.

## What would validate this

The document's own §7 is the test: an interface2 session runs the count, gets its own
number, and either builds the reaper or declines on the evidence. The claim most exposed
to being wrong is the one now marked as inference — where interface2's landing step
actually is. If it turns out there is no single such step, §7's fallback (give landing an
entry point, or accept a hook that fires on more paths) is what the document is really
recommending.

Generalising: the failure this run caught twice is the same one — **a number or a command
that was reasoned about rather than executed**. The median was read off a sorted list by
eye; the snippet was written from the pattern rather than run. Both looked right. The
only defence that worked was running them.

---

## Appendix — run record

- upstream:  syncytium2/murderboard @ `fae0eca`
- vendored:  `fae0eca` (re-vendored this session in PR #256 — the gate refused this run
  as STALE at `f26414a`, which is the gate working)
- freshness: current
- artifact:  `docs/reaper_handoff.md` (`8939702` → `512a09d`, then further edits in the
  blind pass)
- roles:     11 of 11 run
- rounds:    1 blind verify round; stopped on **severity floor** (no blocking, no major
  findings surviving), not on the round cap

**Deviation from the process, stated rather than hidden:** step 2 prescribes parallel
subagents for a substantial deliverable. This session is instructed not to spawn agents,
so all 11 roles were run as a single-pass walk of every role's checklist, in order, with
each mechanical check actually executed. The rule that every role runs was met; the
isolation between roles was not, and a single reviewer walking eleven checklists shares
context with the author in a way eleven subagents would not. Treat the judgement roles
(4, 8, 11) as the weakest rows below.

### Role ledger

| # | Role | Findings |
|---|---|---|
| 1 | Claim & data verifier — "Prove It." | **4.** (a) **BLOCKING** — "median ten minutes" false; recomputed to 37 min over n=27, bimodal. (b) **MAJOR** — "about 150 lines including its tests" understated PR #240: 140 lines of tool + 165 of tests, 340 insertions. (c) **BLOCKING** — the quoted `reap_verdict` was not byte-identical to the shipped source (whitespace), in a document instructing verbatim reuse; now diffed against `tools/merge_when_green.sh` and identical. (d) **MAJOR** — provenance sha stale (`045b999` → `7813613`). Claim ledger: 14 quantities checked, 11 verified against source, 3 corrected. |
| 2 | Citation & reference validator — "DOI or Die." | **0.** No external literature. Checked instead that every internal reference resolves: PRs #230/#240/#241/#256, shas `c2fbaed`/`7813613`/`fae0eca`/`c711e737`, the sapper rule `SAP032`, the DO-NOT-PRUNE closeout date, and every quoted line from interface2's `CLAUDE.md` — all read from source, none from memory. |
| 3 | Consistency auditor — "Cross-Examiner." | **1 MAJOR.** "27 offered on 2026-08-23" (§3) sat unreconciled against "28 worktrees, 17 removable" (§1) on the same date. Both are true at different hours; §3 now carries the times and the explicit warning that the population moves all day. Counting basis pinned throughout: **non-primary worktrees**, stated at each use. |
| 4 | Adversarial reviewer — "Reviewer 2." | **2.** (a) **BLOCKING** — interface2's landing mechanism asserted as fact from an inference; now marked as inference with the evidence shown. (b) **MINOR** — "no CI wait, the session is standing right there" rests on the same inference; scoped to it. Attacked and let stand: the §8 limits section already refuses the overclaims a reader would reach for (weeks of use, cross-platform, concurrent landings). |
| 5 | Line editor — "Kill Your Darlings." | **3 MINOR**, applied. Cut a redundant restatement of the rule in §3, tightened the opening two paragraphs so the problem lands before the provenance block, removed a hedge that duplicated §8. |
| 6 | Methods / domain expert — "RTFM." | **0.** The method here is git. Verified against behaviour, not memory: `merge-base --is-ancestor` exit semantics; `git worktree list --porcelain` first row is the main working tree; `git worktree remove` deletes ignored files while `git status --porcelain` does not report them (reproduced in a scratch repo); `git log --no-merges -N` applies its limit after filtering — the trap that produced finding 4(a). |
| 7 | Reuse auditor — "Reinventing the Wheel." | **1 MINOR**, applied. The document described the reaper without noting that it and `worktree_sweep.sh` share their notions of "clean", "primary" and "merged"; §3 now tells interface2 to build one collector, not two, because the drift between them is the predictable defect. |
| 8 | Naive-reader accessibility — "You Lost Me." | **3 MINOR**, applied. Reader is an interface2 session: expert in the domain, cold on bugarach. "Primary checkout" was used before being defined (§4 now defines it in place); the sweep defect was referenced before its path was given (§3 now names the todo file); §1's bucket table replaced a bare summary statistic a reader could not act on. Per-section verdict: all 9 sections followable cold after fixes. |
| 9 | Density & figure-first — "Show, Don't Tell." | **1 MAJOR**, applied. The central quantitative claim was a lone summary statistic with the data never shown — and it was *wrong*, which a shown distribution would have exposed immediately. Replacement artifact named and built: the bucket histogram in §1. **Deliberately a text histogram rather than a PNG**: the deliverable is markdown destined to be read inside another repository, where an image asset in `bugarach/docs/` would not travel. |
| 10 | Build & craft gate — "Ship It." | **1 BLOCKING**, applied. Table below. |
| 11 | Argument order — "Start With the Problem." | **1 MINOR**, applied. The cold open was a provenance stamp and an audience note; the problem arrived third. Reordered so the first sentence is the leak. Spine checked against the arc *problem → cost → rule → why the alternative fails → mechanism → what you must add → failure directions → how to evaluate → limits*; the one deviation (evaluation at §7 rather than early) is deliberate and now stated. |

### Role 10 — mechanical table

| what was checked | against | result |
|---|---|---|
| §4 code block vs shipped source | `diff` against `tools/merge_when_green.sh` | **identical** after fix |
| §7 snippet executes | run verbatim against `~/Developer/interface2` | 19 rows, all `dirty=0` |
| §7 snippet excludes the primary checkout | grep for the primary's basename in output | 0 rows — **was 1 before the fix** |
| artifact fingerprint changed | `git hash-object` | `8939702` → `512a09d` |
| section numbering contiguous | headings 1–9 | contiguous |
| stale "ten minutes" anywhere in artifact | grep | only in §8's own self-correction |
| same number still shipped elsewhere | grep across tree | **2 hits fixed**: `tools/merge_when_green.sh:38`, `docs/git_workflow.md:132` |
| tables render, code fences balanced | read | pass |

### Residual ⚠

- **⚠ Where interface2's landing step is** is inference from history shape, not
  observation. Flagged in §2 in the document itself.
- ~~**⚠ The §1 population cannot be re-measured.**~~ **Resolved during the run.** Those
  worktrees have since been collected, so the distribution rests on one recorded
  measurement at 16:34 on 2026-08-23 — which is why the raw born/last-write pairs and the
  script that reduces them are now committed beside this record as
  `reaper_handoff_2026-08-23_worktree_lifetimes.csv` and
  `reaper_handoff_2026-08-23_lifetimes.py`. Anyone can re-derive every number in §1;
  nobody can re-observe the population.
