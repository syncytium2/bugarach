---
to: short-course
from: bugarach (Mac, milestones-and-case-report)
status: NOT SENT — withheld on its own review
opened: 2026-08-31
---

> # ⚠ NOT SENT. This is a record, not a delivery.
>
> Held on the verdict of its own murderboard round
> ([run record](../reviews/case_report_to_short_course_2026-08-31.md)). The adversarial
> blind pass found the report's central structure unsound, and it is right: the "five
> nested levels" are a **fan, not a nest** — levels 3, 4 and 5 are all components of
> level 2 — and "an assertion outran its verification" is a category broad enough to
> cover any mistake anyone makes. Worse, the metric is **incentive-inverted**: the worse
> the first draft, the deeper the "depth measurement", so any draft can be enumerated to
> whatever depth the argument needs.
>
> **Level 1 — the K decay — is real, checkable, and needs none of the scaffolding.**
> Everything built on top of it was scaffolding.
>
> It is kept here rather than deleted because the sequence it records is the most
> complete account this project has of one failure mode reproducing through its own
> machinery, including inside the review built to catch it. **Do not send it, and do not
> quote it as a finding.** If anything goes to the short course, it is the two-paragraph
> correction: we drafted a critique from a stale copy of their material, and they had
> already published the finding.

# You wrote the diagnosis at 09:36 on 31 August. The thing it diagnoses was happening in our repo at that moment, and ran for another two and a half hours

**One line:** *"Retrieval failed, not recording"* is yours — we are not bringing you a finding.
We are bringing you a **recurrence**, in the machinery built to stop it, with the first draft
of this document as five of its instances and the draft correcting them as two more.

---

## The specimen

A commit, and then what four documents made of it in the next day and a half.

```
08-29 18:50  80b8db6   "NOTE TWO PEAKS … CHOOSING K IS STILL NOT DONE
                        and is not done here. This file is the evidence
                        for that decision, not the decision."     K=12 / K=16
             ─────────────── 34h 30m, nothing ───────────────
08-31 05:20  ee2f946   a todo                      "K=12 was already decided"
08-31 06:41  81cc134   docs/INDEX.md lands — the index built to fix findability
08-31 09:26  abc7a35   the gate-fix handoff        "the decided value is K=12"
   ····· 09:36  YOUR PAGE IS WRITTEN, in another repo: "Retrieval failed,
                 not recording" ·····
08-31 12:02  cc2489d   the transfer README + PR #427 title  "THE DECIDED K"
                                                   K=16 in none of them
```

Four hops in **6 h 41 m**, on one morning, after a day and a half of silence. Not slow drift
across independent readers — a same-morning cascade. One of the four documents is itself an
**incident report about decisions being ignored**; it opens by asserting that K *"was decided
by a real effort."* It was not. Nobody chose. `derive_spec --k` still refuses to choose.

**Your page was written into the middle of it** — ten minutes after the third hop, two and a
half hours before the last. Neither of us knew.

`K` is how many cells firing together the analysis counts as one coordinated event. Every
cross-lab comparison downstream is conditioned on it, and the scan has two defensible peaks —
12 by one summary, 16 by another. The commit said so. Two days later the repository said the
question had never been open.

## What is yours already, and why we are not repeating it

Your page, `the-email-contained-no-new-information`, about this project. ⚠ We first wrote
"published 29 August" here; a blind check found it was **written 2026-08-31 09:36**, sits on
an unmerged branch, and carries none of the version stamps your four public handouts do. The
`2026-08-24` in its filename is the date of the email it is about. Corrected:

> The uncomfortable corollary: the repository was not missing information. Everything needed
> was written down, correctly, in three files that were open and current. Retrieval failed,
> not recording.

That is the diagnosis. We have nothing to add to it and we are not proposing you teach it —
you already do. **This report exists because the first draft of it did not know that.**

That draft argued your course lacked a timescale for the project outgrowing the person. It
sourced the claim to `course-outline.md`, Draft 2, last modified **25 August** — six days
stale against four handouts you republished on the 31st. It would have told you your material
lacked the thing your material contains, by reading an old copy and not opening the current
one. An eleven-role review caught it; we did not.

## What the recurrence adds

Not a new mechanism. A **depth measurement** — the same failure nested inside itself, each
instance caught only by the layer outside it. Five in the first draft:

| # | where | the claim | what was true |
|---|---|---|---|
| 1 | the project | four documents: "the decided K" | the commit said choosing was **not done** |
| 2 | the report about #1 | "a test fails if…"; "counted, not recalled" | a script nothing runs; six of nine counts wrong |
| 3 | the cure proposed in #2 | "the decay is stopped by one machine-checkable rule" | the rule **fired backwards** — fixed since; see below |
| 4 | the critique in #2 | "your loop has no step for that" | read from your six-day-stale outline |
| 5 | the evidence in #2 | "13 rules that fire by themselves" | `sapper --selftest` says **12** |

**And two more in the draft that corrected those five** — a daily-commit series copied from a
reviewer's report instead of recomputed (three wrong figures), and "published 29 August" for a
page written on the 31st. **Seven, and counting, in about thirty hours.** Every one was caught
by a check from outside the author; none by the author. That is the rate, and it is the only
number in this report we would defend as generalizable.

**Level 5 is the smallest and the most instructive.** We counted the rules with
`grep -oE 'SAP[0-9]{3}'` and got 13, because `SAP011` appears once in a comment reserving it
for an unbuilt proposal. The tool answers in one command and says 12. Grepping for text and
asking the tool are different acts, and only the second is a measurement.

Then, during the review: **one of the eleven reviewers checked that number the same way and
returned the same 13**, while two others asked the tool and got 12. The error reproduced
inside the apparatus built to catch it, from the same method, on the same afternoon.

## Level 3, in full, because it is the one that would fool a reader

The proposed cure was a milestone index with a `strength` column — `built` / `measured` /
`decided` / ⚠ `evidence` — and a check refusing any `evidence` row that calls its own subject
decided. Offered to you, in the first draft, as *"the K=12 decay is stopped by one
machine-checkable rule."* Run against the rows that matter:

| row, marked `evidence` | the check | should |
|---|---|---|
| "K was never decided; still open" | **FAILS** | pass |
| "not yet decided" | **FAILS** | pass |
| "K=12 is settled and final" | passes | fail |
| **"was never an open question"** — the actual decay wording | **passes** | fail |

It punished the hedge and waved through the assertion. (All of this is the FIRST draft; the version in the tree now fails every one of these and proves it with `--selftest`.) It would have rejected `80b8db6`'s own
phrasing and accepted the sentence that undid it. It also reads one file while the real decay
happened in four others, is defeated by a one-word edit to the label it keys on, skips seven
of thirty-six rows whose paths lack a file extension, and returns *"OK — every row resolves"*
on an empty document. Nothing runs it, in a document that said a test did.

**We are not offering it to you.** It is in this report as instance #3, not as a proposal.

## The scale it took to get here

One researcher directing agents, 2026-08-10 to 2026-08-31 — **22 days with commits**:

| measure | count |
|---|---|
| commits on `main` | **1,074** |
| merge commits on `main` | **424** |
| open items in `docs/todo/` | **108** |
| open items in `docs/sapper_feedback/` | **12** |
| rules that fire by themselves | **12** |
| test suite | **1,660 passed, 48 skipped** — before this change adds its own eight |

Commands are in the sources table; every figure is pinned to `6d9ca6d` and was recomputed
after the review, because the first draft pinned them to a commit at which four of them do
not reproduce.

Daily commits ran **11 · 15 · 25 · 39 · 14 · 28 · 63 · 93 · 95 · 76 · 103 · 17 · 52 · 94 ·
61 · 46 · 41 · 39 · 105 · 31 · 16 · 10** — a two-day ramp, a ten-day plateau topping out at
105, then a collapse across the final three days. The first draft called this "roughly fifty
a day, every day": a mean that two peak days carry, while **twelve of the twenty-two days sit
below 45**. The three days where the volume falls off are the days in the specimen above.

**That sentence was wrong when we first fixed it.** The corrected draft took this series from
a reviewer's report instead of recomputing it, and shipped three wrong figures — a wrong final
day, "three days over 100" when there are two, "ten days below 45" when there are twelve. A
blind pass caught it. **That is level 2 again, committed inside the document correcting level
2, one revision later.** We are leaving the trace here rather than quietly repairing it,
because it is the only honest way to report a rate: the error did not stop when we knew about
it, and what caught it each time was a check from outside, never the author.

## The limits, stated where you will read them

- **This is one project, one day, one agent.** Nothing here establishes a rate.
- **The §"specimen" and §"recurrence" tables are checkable; the conversation is not.**
  Levels 2–5 were surfaced by a researcher correcting an agent four times in one session.
  That exchange is a transcript, not a repository artifact, and you cannot verify it.
- **We changed the diagnosis mid-review.** The first draft claimed encoding succeeded and
  retrieval failed. That is wrong here: `docs/INDEX.md` line 41 carries a `⚠ Read this first`
  flag asserting that the other lab's published data holds **no coordination ground truth** —
  a claim nobody had ever checked, and which is still unchecked. The index was not unreached; it
  was reached, and it was wrong, having inherited the error from what it indexed. An index
  built for findability is not therefore a check on truth, and its priority flags convert an
  inherited error into a confident one. That is the part we did not know on the 29th.
- **The index landed at 06:41 on the morning it failed**, five hours before the last hop. The
  first draft said "four days earlier", which was wrong and, being wrong, understated it.

## One question, and it is the only ask

You measured the token cost of an eleven-role review across three projects on 29 August.
Do you have anything like a **volume** figure for the others — commits, PRs, open items per
week? We have depth from one project and no idea whether three weeks is when this arrives or
whether bugarach is simply unusually dense. You have the wider view; we cannot get it from here.

## Sources

| what | where |
|---|---|
| the commit that measured K and said the choice was open | `80b8db6` |
| the four documents that then called it decided | `docs/learned/cossart_transfer/README.md`; `docs/todo/2026-08-31-a-decision-in-prose-will-be-re-derived.md`; `docs/handoffs/2026-08-31-the-gate-fix-the-bakeoff-calibrates-without-one.md`; `docs/todo/2026-08-31-two-overnight-results-need-a-ruling.md` — plus PR #427's title |
| the index, and the read-this-first line that carried the error | `docs/INDEX.md` (#415, landed 08-31 06:41) |
| the importer that reads three groups of the source and stops | `interface2`: `dandi/extract_dandi219.py` (`2f09f560`, 2026-07-15) |
| the ingest that ran no detector | `interface2`: `build_dandi_store.m`, `dandi_to_event_store.m` (same commit) |
| commits, merges | `git rev-list --count 6d9ca6d`, `git rev-list --count --merges 6d9ca6d` — `gh pr list` moves daily and is not pinnable |
| open items | `grep -l '^status: open$' docs/todo/*.md \| wc -l`, same for `docs/sapper_feedback/` |
| rules | `python3 tools/sapper.py --selftest` — **not** a grep for `SAP\d{3}` |
| suite | `PYTHONPATH=$PWD/src pytest -q` |

The repository is public. Every count above was produced by the command beside it, run against
`6d9ca6d` on 2026-08-31, after an eleven-role review found six of the first draft's nine
counts wrong.
