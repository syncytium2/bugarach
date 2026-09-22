# Handoff: goal 2's comparison landed, and the stopping rule is deliberately not set

> ⚠ **This file covers goal 2 alone — the learned model family against the coded
> detectors.** The other root handoffs are other threads and are NOT superseded by this
> one. Delete only your own file. (The `HANDOFF.md` this line used to name was retired on
> 2026-09-21, its in-flight #466 having landed —
> [`docs/handoffs/2026-09-08-the-loop-closes.md`](docs/handoffs/2026-09-08-the-loop-closes.md).)

**Written 2026-09-21 by the orchestration session**, which drove goal 2's two GPU runs
from Friday evening through Monday morning and is ending here. `main` is green.

**Start at [`docs/goals/learned-model-family.md`](docs/goals/learned-model-family.md)**
— it is current and carries every result this file summarises.

> **Not murderboarded** — working material for sessions in this tree, at Tony's
> instruction. Nothing here is for an outside reader.

**No counts retyped.** Derive them: `git rev-parse --short origin/main` ·
`python3 tools/leaderboard.py` · `pytest -q` · `python3 tools/sapper.py --all`.

---

## In flight right now

Two workstation sessions were dispatched Monday morning and had not reported when this
was written. Both work from `main`.

| machine | task | why it matters |
|---|---|---|
| **WSMIP064** | the **crowded-allowance sensitivity sweep**, then options A and B on the merge-gap page, then deleting two stale virtual environments | every merge gap in the weekend's result is the boundary an unsigned 0.02 F1 constant imposes, so this decides whether the constant can be signed |
| **WSMIP065** | chorus-collapse **items 1-3 plus the GPU census re-run** | the census never stored the head's **input**, and the signal never reached the head in **32 of 75** collapsed `chorus_gain_norm` fits, so the page's headline may be wrong for 43 % of one net |

**065 has since reported**: [#687](https://github.com/syncytium2/bugarach/pull/687),
`census-rerun` — items 1-3 plus the census re-run, with the re-run reproducing every
pre-existing field bit-identically across all 974 fits, so the two new fields are pure
addition. It confirms the split above: the head is the site of the stall in 143 of
chorus_norm's 153 collapsed fits, and is handed a constant input in 32 of
chorus_gain_norm's 75, where **a repair aimed at the head cannot reach**. Merge on green.

**064 has not.** It was still running when this was written. If it is idle when you
arrive, poke it rather than assume it finished.

⚠ **Nothing under `runs\` on 064 may be deleted while the sweep is running** —
`tune_net_merge_gap.py` reads the saved fits and writes the `-gaps` scratch, which are
items on its own deletion list. The virtual environments are unaffected.

**#683 landed** (`5f906ec`), so `tools/leaderboard.py` is on `main` and the field below
is a command rather than a paragraph.

## What Tony decided on 2026-09-21

Recorded here because a ruling that lives only in a chat transcript is a ruling nobody
can find.

| decision | ruling |
|---|---|
| the 0.02 F1 crowded allowance | **sweep the sensitivity first, then sign** — the sweep is the input to the signature, not a consequence of it |
| `tune-bench-comparison` | **land the nets only** — done, #680. The big branch stays open |
| the merge-gap page's verdict | **options A and B together** — demote the verdict to a measurement, and run the missing no-merge check on CoactDetect |
| the chorus-collapse findings | **items 1-3 now, plus the census re-run** |
| 064's disk | **the two stale virtual environments only**, 8.60 GB. Every run folder stays |

**Ruled since this was written (2026-09-22):** `gauge` and `chorus` stay in the lab
server's capabilities and the browser's model picker. #680 had already put them there —
registering a net is what lists it — and Tony chose to leave them, each with its warning
note. Whether [#596](https://github.com/syncytium2/bugarach/pull/596)'s run output lands
is still open.

**Still deliberately unruled — do not infer it:**

- **the fate of `tune-bench-comparison` itself.** Its scan is
  [`docs/todo/2026-09-19-landing-tune-bench-comparison.md`](docs/todo/2026-09-19-landing-tune-bench-comparison.md);
  gate 3 closed with #672 and gate 5 is answered by #680, so gates 2 and 4 remain. The
  two-hour CI suite arrives on `main` with that branch and then applies to every PR.

## The stopping rule, and why there is not one yet

Tony asked how we know when the game is over. The answer was **not yet**, and the reason
is worth keeping: three things that move the numbers are still in motion — the unsigned
allowance, the unresolved collapse mechanism, and the merge-gap page's verdict being
demoted. Pre-registering against rules still moving would freeze the wrong thing.

**What is left once those land**, in order:

1. **Freeze and pre-register** — the models, the selection, the decision rule and what
   stays tunable, in a committed document, *before* anything runs.
2. **Run once on recording seeds nothing has touched.** 1000-1047 and 2000-2047 are
   spent; **3000-3047 are free.** That is what makes it a final run rather than the run
   where we happened to stop.
3. **Read the result against the attempt count**, which `tools/leaderboard.py` shows.

The bar needs no inventing: the goal page states it, and the leaderboard computes its
first clause.

## What the field actually looks like

Run `python3 tools/leaderboard.py` rather than trusting a number here. Two facts from it
that a nets-versus-CoactDetect table hides, and that an earlier draft of that very tool
hid until Tony caught it:

- **Binned SCE leads both selections on mean held-out F1**, not CoactDetect. CoactDetect
  is a defensible *reference* only because it is the highest-scoring coded detector whose
  settings pass the crowded-recording veto in every fold; SCE's pass 1 of 4 under the
  budget and 0 of 4 on F1 alone.
- **The nets sit inside the coded field, not behind it.** Under the budget
  `chorus_gain_norm` is third of ten, ahead of `loco`, `cicada`, `rate` and `sync`. On
  F1 alone `tube` is last of ten, below every coded detector.

## Two traps this session fell into

**An idle session does not volunteer.** WSMIP064 sat idle for six hours on Saturday with
its turn ended and its work invisible, while this session waited for a report that was
never coming. Check `get_session` and the branch list, not the absence of news.

**Restating another session's summary is how wrong numbers travel.** This session
relayed two claims without checking: that a review's blocking count was "flat" at 11
then 10, when round 1 ran 11 roles and round 2 ran 5, so per role run it **doubled**;
and that about 30 GB of scratch sat on 064, when measured it was 3.14 GB. Both were
caught by someone else. Check the denominator, and measure the disk.

## Where the work is

| what | where |
|---|---|
| the goal's current state | [`docs/goals/learned-model-family.md`](docs/goals/learned-model-family.md) |
| both run reports and the merge-gap page | `docs/learned/tuned_vs_coact/` |
| why a third of `chorus_norm`'s fits never train | `docs/learned/chorus_collapse/` |
| the full field, derived from the run files | `tools/leaderboard.py` |
| three review records, every role report verbatim | `docs/reviews/` |
| the training-failure literature, both papers filed | `lit/optimization/` |

## Delete this file when

064's sweep and 065's census have both landed and #683 has merged — at which point
either the stopping rule can be set, or a new handoff says what changed. **No handoff on
`main` means nothing is in flight**, so this must not outlive the work it describes.
