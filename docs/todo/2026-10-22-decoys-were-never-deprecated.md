---
status: done
filed: 2026-10-22
closed: 2026-10-23
---

# Decoys were never formally deprecated; the ruling waits on Tony

> **Closed 2026-10-23 by [ADR-0019](../adr/0019-the-decoys-are-retired-negatives-are-rate-matched.md).**
> Tony: *"Consider old decoys dead. We'll add rate matched negatives to our toolset."* What is left
> to build is in [the follow-on todo](2026-10-23-rate-matched-negatives-and-the-bench-without-decoys.md).
> The rest of this page is the record of the search.

**Tony, 2026-10-22:** *"pretty sure we deprecated decoys. that should recorded as an adr."* Then,
on hearing that no record was found: *"we've got to find that discussion on decoys … it means we
lost track and some stuff did not get pushed."*

## What the search found (2026-10-22)

Three sessions searched for the discussion, one on each machine: WSMIP065, WSMIP064 and the Mac.
Each read every Claude transcript on its machine, every local branch that has not been pushed,
every worktree and every stash. A further search covered `origin`, GitHub issues and PRs, and the
darkroom `claude-link` inbox. **None of them holds a ruling that deprecates decoys, and no decoy
work is unpushed on any machine.** Before 2026-10-22, Tony's typed messages never mention
"decoy" or "distractor" on any of the three machines.

The trail, in date order. Each step argues against decoys, and none of them removes them:

| date | what happened | where |
|---|---|---|
| 2026-09-15 | Review round 3 removes the "precision with decoys set aside" column, because the count behind it measured coverage, not calls | `510aafd1`, branch `detector-review-doc` |
| 2026-09-16 | Tony's second review pass *keeps* decoys and adds a paragraph explaining why a test plants them | `e1053d29`, same branch |
| 2026-09-17 | Murderboard reviewers recommend saying what decoys model or dropping them from precision. They measure 119 of 150 decoys within 60 s of a planted event. A recommendation only | [PR #587](https://github.com/syncytium2/bugarach/pull/587) |
| 2026-09-23 | **ADR-0006**: a call on a decoy is not a false alarm. F1 is reported with and without decoy calls. Whether decoys leave the bench is left to "the objective's ADR", which was never written | [ADR-0006](../adr/0006-a-false-alarm-is-coincidence-the-event-rates-explain.md); `dfd89de5` |
| 2026-09-25 | The final-parameters report asks Tony whether decoys below the floor should be "don't care". No answer is recorded | [`coded-detector-optimization.md`](../goals/coded-detector-optimization.md) |
| ADR-0010 | Retires the *old bench*, not the decoys. This may be the ruling remembered | [ADR-0010](../adr/0010-tune-train-and-review-against-the-data-as-they-are.md) |

**The bench still plants six decoys per recording** (`n_distractors=6` in `src/bugarach/bench.py`).

## The decision

- **Recommended:** write the ADR as a ruling dated the day Tony makes it, *not* backdated, with
  the trail above as its context. It closes the question ADR-0006 left open.
- **Separately:** taking decoys off the bench (`n_distractors=0`) changes every bench number. That
  is its own PR, after the ADR.
- The places left unsearched are claude.ai or cloud chats, and conversations outside Claude. If the
  original discussion turns up there, cite it in the ADR.

## Does anyone else use decoys? (2026-10-23)

No synchrony or assembly benchmark does it our way (ADR-0006's references). Fields that use
decoys build them to be **known false while looking real**: the target–decoy search in proteomics
(Elias & Gygi 2007, doi:10.1038/nmeth1019); knockoffs in statistics (Barber & Candès 2015,
doi:10.1214/15-AOS1337; Candès et al. 2018, doi:10.1111/rssb.12265); and property-matched decoys
in drug screening, DUD-E (Mysinger et al. 2012, doi:10.1021/jm300687e). Ours were true positives
scored as false. Full citations are in ADR-0019.

Goal page: [`detector-review-document.md`](../goals/detector-review-document.md). The reply to the
plain document's reviewer answers her decoy comment from whatever this ruling says.
