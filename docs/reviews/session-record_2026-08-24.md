# The review that stopped a document from shipping

The draft was a session record: what a day of end-to-end work changed, what it cost,
what is still open. Eleven roles ran against it. **The finding was that it should not
exist.**

Not because it was wrong in some fixable way — though it was wrong in eleven fixable
ways, listed below. Because the same artifact, in the same directory, had been closed
the previous day for exactly the reason this one would have been:

> *A status page is only useful while its status is current, and a stale one is worse
> than none: this one still said the sixth detector was missing on a day the page ran
> all six.*
> — `docs/todo/2026-08-20-webapp-session-status.md`, on closing

And a session working the same tree the same afternoon reached the same conclusion
independently, writing `docs/RESET.md` with declared precedence over exactly this
remit. Its own review record:

> *Four of the counts the draft asserted about the project's own state were wrong
> within the hour of writing them … Correcting them would have bought nothing, so
> **every count came out and the commands that produce them went in.** Two status
> documents in this repo have already gone stale while reading as current; a third
> with a reset's authority would have been worse than none.*

Same day, same failure mode, opposite decision — and that document got there first.
The draft carried twelve PR numbers, six timings, four row counts and a file size:
perishable on commit, in a directory whose last such file had just been buried.

## What shipped instead

Nothing was discarded. Each finding went to the file that already owns it.

| what | where it went | why there |
|---|---|---|
| the failure-mode synthesis — a degraded result and an exit code that says success | new section in `docs/testing_a_sampling_port.md` | the closed precedent moved *"test the screen, not the function"* to exactly this file; the new section sits beside it and references it |
| the routes disagree by 52% on one folder | `docs/todo/2026-08-24-two-routes-two-answers-on-one-folder.md` (new) | genuinely new, actionable, and owned by nothing else |
| three facts a person needs to decide the Cloudflare token | appended to `docs/todo/2026-08-20-nothing-publishes-the-site-so-it-goes-stale.md` | that is the file somebody opens when they decide |
| three README claims retired the same night by this session's own PRs | fixed in `README.md` | the defect was live in the most outward-facing document |
| `docs/lanes.md`'s banner naming a defect since fixed | corrected, and pointed at the new one | it directs whoever next holds the viewer |
| a stale `ACTIVE` claim from the previous day | released on `docs/SESSIONS.md` | it is the habit the draft confessed to, still running |

## The eleven, and what they caught

| role | findings | the one that mattered |
|---|---|---|
| 1 · Prove It | 19 checked, 8 defects | the tune timing was measured on **four simulated recordings**, printed inside a table headed *"the real 84-recording export"* |
| 2 · DOI or Die | 9 defects, 20+ clean | two quotations attributed to Tony **exist nowhere in the tree**; *"test the screen, not the function"* attributed to CLAUDE.md, which does not contain it |
| 3 · Cross-Examiner | 15 defects | *"published empty for a day"* — **it never published**; the site was frozen at an older build and the window on `main` was 73 minutes |
| 4 · Reviewer 2 | 14 attacks | *"verified as served"* meant a local `http.server`; the live site is 34 commits behind and carries none of it |
| 5 · Kill Your Darlings | 18 | the five bugs were **numbered, never named** — the exact construction the house style forbids |
| 6 · RTFM | 7 defects, 8 clean | `detector_history.md` §6.4 **still recommends the guard** the draft says was retired, so the doc it cites would send the next session to re-add it |
| 7 · Reinventing the Wheel | 10 | the precedent, and `RESET.md`. This is the role that killed the document |
| 8 · You Lost Me | 14 | **six of eight sections unreadable cold**, and the two a stranger would act from were the worst |
| 9 · Show, Don't Tell | 4 | a document whose own thesis is *open the screenshot* contained **no images**; built the nav before/after crop to prove the point |
| 10 · Ship It | 7 defects, 12 rows clean | renders correctly at three widths; flagged that the reviewed file was still untracked |
| 11 · Start With the Problem | 6 | the asks sat at **79% down**, and the only section demanding a decision was the longest bullet in the file |

Every role reported. No role returned silence.

## Residual ⚠, for a person

1. **`docs/detector_history.md` §5.1 and §6.4 are stale** and were not fixed here — they still recommend the guard interval on the masking rationale that `forks.md` §4a retired, with no cross-reference to the reversal. A session reading §6.4 will re-add it. Role 6 also found `docs/todo/2026-08-23-censoring-is-the-instrument-the-guard-was-not.md` **mis-cites §6.4** as prescribing censoring; it does not.
2. **`CHANGELOG.md` says 0.1.0 was cut after 286 merged pull requests.** The highest PR number in the repo is in the 270s and 264 are merged, so 286 was never reachable.
3. **`docs/todo/2026-08-18-spike-synch-knob-may-not-be-the-knob.md` computes the coincidence quantum at 30 ROIs (1/29).** The bench has used 33 since the difficulty-axis correction, so the quantum is 1/32 and the arithmetic in that note is one step out of date. The conclusion is unaffected.
4. **A `waiting-on-tony` frontmatter status landed today** and the items this session leaves open are that kind — done but for one human decision. They were filed before it existed and are not tagged.

## What I would tell the next session

The murderboard is worth running on a document you are proud of, because the roles
that pay are not the ones that find typos. Two of eleven changed what shipped: role 7
found the artifact had a closed precedent and a live competitor, and role 3 found a
sentence — *"published empty for a day"* — that was vivid, memorable, repeated by its
author in conversation, and false. Neither is the kind of error rereading catches.

The cheapest structural lesson, which cost this session a duplicated fix and three
stale board claims: **disjoint file ownership across parallel lanes prevents
collisions and does nothing about shared facts.** Six lanes each measured their own
route honestly. The 52% disagreement between two of them was only visible to
something that read all six reports at once, and nothing was going to do that until a
review forced it.

---

## Appendix — run record

- upstream:  syncytium2/murderboard @ fae0eca
- vendored:  fae0eca (this repo's copy)
- freshness: current (`murderboard_freshness.sh --refresh --verbose`, exit 0)
- artifact:  `docs/todo/2026-08-24-the-app-goes-folder-to-file-and-what-that-cost.md`
  (`f50e4ab2bcfc36e21cc29ba57dada2aa3218ba84` → **withdrawn, not shipped**)
- roles:     11 of 11 run
- rounds:    1 review round; the verify pass applies to the replacement artifacts
  listed above, not to the withdrawn draft

**On the rounds count, stated rather than glossed:** the process asks for blind verify
rounds until clean *on the corrected artifact*. The corrected artifact here is a set
of edits to six existing files rather than one rewritten document, so the iterate-to-
clean loop does not apply in its usual form. What was done instead: every replacement
claim was re-verified against the tree at the time of writing, and the two numbers the
new todo rests on — 34,124 detections, and its 16,743 / 17,381 split by stream — were
**re-measured by this session directly** rather than quoted from a lane report, which
is the specific failure role 1 caught in the draft. The 51,968 browser figure is still
a quotation from a lane report and is flagged as such in the todo itself.
