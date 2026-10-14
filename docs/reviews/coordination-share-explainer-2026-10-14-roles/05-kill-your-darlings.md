GRANT 5 ok — Read, Grep, Glob (SubagentHandback is also held. It is the hand-back channel, not an editing tool. No Edit, Write or NotebookEdit.)

# Role 5, line editor: README for the coordination-share explainer, round 1

Artifact: c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md (229 lines). I checked figures against c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\numbers.json. I did not open the PNGs; role 10 owns them.

## Tool receipt

`murderboard_prose.sh` was **not run**. It is not vendored in this repo and is not on this machine. That is a gap in this review, not a clean result.

I ran a substitute: Grep (case-insensitive) on the README for the checklist's house list in doc_review_process.md, role 5, unedited:
- not just/not only
- it's/it is not about
- worth noting
- delve, leverag-, robust, seamless, crucial, landscape, tapestry
- In today's
- em-dash (—)

I added the house checks from CLAUDE.md:
- fire/fires/fired/firing
- data is/was/has/itself

I also hand-checked every "a, b and c" triple. There is no block word/sentence table; the counts in the passage test are hand estimates.

| line | construction | kind |
|---|---|---|
| 185 | `survives the sliding — after a shift of a minute or so, … neighbours — so the copies…` | em-dash pair (a parenthetical, not a pivot into an uplifting close) |
| 186 | (the same pair, closing dash) | em-dash |

Zero hits for:
- every banned word and the "not just" / "not about" / "worth noting" / "In today's" forms
- "fire"
- singular "data"

Triples:
- Lines 15, 63, 140, 156 and 168 hold real three-value sets (windows of 1, 2 and 4 s; moment sizes of 10, 6 and 3 cells). None is a rhythm triple.
- Line 115, "three answers", counts real outputs.

The only clock time is none: the page gives dates only, so the Michigan-time rule does not apply.

## Findings

Format: location · issue · severity · suggested fix · verified against a source?

1. **L148**: "every fixed-model share here reads low by about a fifth" overstates. numbers.json fig 4 puts fixed-model share errors at −10.4% to −20.7%, and L157 says "between −10% and −21%". The sentence contradicts the page nine lines later, and it is the sentence a treatment reader will act on. · **major** · "fixed-model shares here read 10% to 21% low (21% on the mixed set at 1 s)", and make the advice on L149 match. · **yes**

2. **L165–166**: "Medium pairs … change nothing at any window" is not what numbers.json shows. Participants per moment (k):

   | k | 1 s | 2 s |
   |---|---|---|
   | 120 s gaps only | 27.5% | 29.5% |
   | medium pairs | 30.2% | 31.7% |
   | close pairs | 29.7% | 32.3% |

   So at 1–2 s medium pairs move k as much as close pairs do. "Nothing" asserts something the numbers do not. (Boundary: whether the claim is supported is role 4's. The word choice is mine.) · **major** · "Medium pairs move every number by no more than close pairs do at 1–2 s, and do not produce the 4 s jump." · **yes**

3. **L92–93**: Figure 2 is used before its contents exist. "both versions of one recording" points at a shifted copy that section 2 introduces only on L106–108. Also, the inline name "In Figure 2, the same mean, wider spread, both versions…" makes the sentence fail to parse. · **major** · "In Figure 2 (same mean, wider spread), the recording and a copy with its cells shuffled in time (section 2) both average 0.47 onsets per window; only the recording has windows holding 5 to 11 onsets." · no

4. **L131–134**: The stated reason does not explain the claim. Why pairs and triples cannot tell fixed from binomial apart has nothing obvious to do with "a moment joined by one cell looks exactly like background". A non-math reader gets a non-sequitur. · **major** · State the actual reason in one sentence (two numbers cannot fix both the typical size and its spread plus the rate). If the one-cell point is the reason, explain the link. · no

5. **L27–28**: The sentence is ambiguous. "the measure that will report … under treatment, before any treatment result is shown (that is a separate piece of work)" reads as if the measure reports before results are shown. · minor · "It explains the measure that will report how much activity is coordinated under treatment. The treatment results are a separate page." · no

6. **L76–77**: Two problems.
   - "chosen as the stretch where a close pair and a medium pair are both in view and largest" does not say largest in what.
   - "seed 10" and "seed 3" are indexes, not names, and "seed" is undefined for this reader.

   · minor · "…where a close pair and a medium pair of 10-cell moments are both in view." Put the seed numbers in the script, or say "simulated recording no. 10". · no

7. **L85**: "That count is *X*, the bottom row of Figure 1, the count." The name colliding with the noun produces a stutter. · minor · "That count is *X*, the bottom row of Figure 1 (the count)." · no

8. **L136–138**: "they disagree by about a factor of two in their errors" is redundant with the bolded numbers right after it. It is true (20.7/11.0 = 1.9). "neither model recovers the planted share exactly" is a hedge. · minor · Cut both clauses: "On these recordings both models read low: fixed 21%, binomial 11% (Figure 3, …)." · yes

9. **L144–150**: The payload is buried. The single most actionable sentence on the page ("take the fixed-model share as an underestimate…") is the last line of section 4. · minor · Promote it to open the paragraph, or repeat it in the "What waits" bullet on the real numbers. Fix with finding 1. · no

10. **L146**: "what the bench's background subtraction removes" is jargon that is used and never defined. · minor · One clause on what is subtracted, or cut down to "matches how the bench plants its moments". · no

11. **L154**: "answers both questions at once" points at questions the page never posed. It is a preview sentence (throat-clearing). · minor · Cut the sentence. The bullets stand alone. · no

12. **L185–186**: Em-dash pair (the only hit). It is a parenthetical, not a pivot, but the house list counts it as a defect unless kept on purpose. · minor · Use a colon: "A change that slow survives the sliding: a minute later each cell is still about as busy as its neighbours, so the copies carry it too and it is subtracted." · yes

13. **L188–189**: "(The todo that commissioned this page had this backwards; the tool's own docstring has it right.)" is a process aside. It asserts nothing about the measure, and an outside reader cannot use it. · minor · Move it to the PR/commit, or to the todo. · no

14. **L193–201**: "No recording failed to give an answer" is a double negative. The paragraph also mixes two experiments, and it is unclear whether the background-lowering result (79/81/81%) is in any figure: L199 says Figure 5B is all quiet background. · minor · "Every recording gave an answer." Mark the lowering result "(not drawn; numbers.json)". · yes (79/81/81 confirmed)

15. **L221–222**: "DI" is an abbreviation never defined (house rule: define at first use). "ROIs" breaks the page's own chosen term, "cell" (L44). "motion-correction pinning census" and "pinning" are undefined for this reader. · minor · "four DI (dioestrus) recordings" (confirm the expansion with the author); "cells"; one clause on what pinning is ("motion correction pinned some cells' traces to the lowest frame value"). · no

16. **L65**: "(0.0169)" is a bare number (house rule: every number carries its unit). · minor · "(0.0169 onsets per second per cell)". · no

17. **L61, L182**: "fast stream", "slow stream" and "the fast stream's bench" are used without a gloss on a page for non-math outside readers. · minor · Add a one-line entry to Terms. · no

18. **L108**: "(`shifted`)" and "`solve`" (L125, L191) are bare code identifiers mid-sentence. They are indexes, not names. · minor · Keep them only where a reader is told to look them up, e.g. "(the tool calls this `shifted`)". · no

19. **L7 caption**: "rigidly shifted copy" uses a different word from the body's "slid". · minor · "one copy with each cell slid in time". · no

20. **L19 caption**: "…(open diamond), divided by the planted share" leaves unclear what is divided. · minor · "B: recovered share ÷ planted share, for each recording's own answer (dots) and for the answer with *f*₃/*f*₂ pooled over 24 recordings as the tool does (open diamond)". · no

21. **L1 title**: "What share of calcium events are coordinated" pairs "share" with "are". · minor · "What share of calcium events is coordinated" (or keep it; "events are" is defensible). · no

22. **L228**: "Not murderboarded as of the first draft…" is a placeholder that has to change before delivery. · minor · Replace it with the review-record link at step 5. · no

## Passage test, one row per block

Word counts are hand estimates. "Buys" means what the other words in the block add.

| Block | ~words | Payload (one sentence) | Where it sits | What the rest buys | Verdict |
|---|---|---|---|---|---|
| L25–30 front matter | 70 | This explains `measure_coordination_rates.py`; the figures come from the script and numbers.json. | start | links a sceptic needs | keep; fix L27–28 |
| L32–33 | 25 | Every figure is simulated; real numbers wait. | start | — | keep |
| L37–40 objection | 70 | The measure counts onsets in windows and reads coordination from how uneven the counts are, so it never defines an event. | spread across the block | the opening question earns its place | keep |
| L44–57 terms | 190 | (reference list) | — | each entry is used later | keep; add a stream entry |
| L61–65 simulations | 95 | The simulations copy the bench: 32 cells, 45 min, 15 moments of 10, 6 and 3 cells. | start | parameters a sceptic would ask for | keep |
| L67–74 spacing | 130 | The main set adds close and medium pairs to the bench's 120 s spacing; the bench itself is unchanged. | middle | the three isolating sets are evidence; the attribution and todo link are provenance | slightly long; acceptable |
| L76–78 | 50 | Which recording each figure shows. | — | — | keep; fix finding 6 |
| L84–87 | 60 | *X* = onsets per window, counted twice with shifted windows. | start | the parenthetical is a real method detail | keep |
| L89–93 | 85 | Sharing leaves the mean alone and widens the spread. | start (bolded) | the Figure 2 example is evidence | keep; fix order (finding 3) |
| L95–101 | 75 | *f*₂ and *f*₃ are zero for independent cells and positive when onsets come together. | end (L100) | formulas, for the reader who wants them | keep; the payload is already bolded |
| L105–113 | 135 | Chance is measured by sliding each cell's train, which keeps rates and breaks timing. | middle | the 0.214/1.369 three-decimal values buy little for this reader | trim the decimals to 2 significant figures |
| L117–127 | 145 | *k* = *f*₃/*f*₂ + 2, then λ, then share = λ*k*/*N* ÷ rate. | middle | the pooling sentence is essential (it links to Fig 5B) | keep |
| L131–134 | 55 | Two models; pairs and triples can't separate them. | — | — | keep; fix the reasoning (finding 4) |
| L136–142 | 115 | Both models read low because moments come in mixed sizes. | middle | the mechanism sentence is real evidence; the "factor of two" clause and the hedge are padding | cut per finding 8 |
| L144–150 | 105 | Fixed was adopted to match the bench, not for accuracy, so read its share as 10–21% low. | **end** | the reason is evidence | **promote the last sentence; fix the "a fifth" claim** |
| L154–170 §5 | 230 | The share holds at any window; the other two numbers should be read at 1–2 s. | **end** (L168) | the bullets are evidence | promote L168–170 to open the section; cut L154 |
| L174–191 blind spots | 330 | A shared change faster than about a minute reads as coordination; slower ones and a steady field do not. | middle (L187–188, bolded) | three experiments, each evidence; the todo aside is satisfaction | cut L188–189 |
| L193–201 | 165 | Few shared moments make one recording's answer noisy; a low event rate does not. | **end** (L200–201) | two experiments; the background-lowering one is unfigured | **promote the last sentence to open; flag the lowering result as unfigured** |
| L203–206 | 60 | `shape_usable` drops tiny recordings; none of the simulated ones. | start | — | keep |
| L210–214 | 75 | It passes its own ±25% check at every window and schedule. | middle | — | keep |
| L218–226 | 130 | Real numbers wait on the contamination stop; the schedule is temporary. | start | why the numbers are withheld is required | keep; define terms (finding 15) |

## Not checked

- I did not render or view the figures (role 10).
- I did not check the formulas or the method's correctness beyond line-level clarity (roles 4 and 8).
- I did not check the order of sections (role 11).
