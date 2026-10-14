GRANT 5 ok — Read, Grep, Glob

(I also hold SubagentHandback, which only delivers this report. I hold no editing tool.)

Artifact reviewed: c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md (330 lines). House rules read: CLAUDE.md "Writing for a human reader", and the headings and "American English" section of c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\writing_conventions.md.

## Mechanical search

**`murderboard_prose.sh` was not available**: it is not vendored here or on this machine. I ran the search with Grep instead.

**List used:** the house list from doc_review_process.md role 5, unedited:
- not just X, but Y
- it's / it is not about
- worth noting
- delve, leverage, robust, seamless, crucial, landscape, tapestry
- In today's
- em-dash (—), to find em-dash pivots

The house rules added three more checks:
- "fire" and its forms (SAP017)
- "data is / was / has" (SAP015)
- British spellings: analyse/analysed, colour, behaviour, centre, favour

Patterns run:
1. `(?i)not just|it's not about|it is not about|worth noting|\bdelve|\bleverag|\brobust|\bseamless|\bcrucial|\blandscape|\btapestr|in today's|—`
2. `(?i)analys(e|ed|es|ing)\b|\b(colour|behaviour|centre|favour)|\bfir(e|es|ed|ing)\b|data (is|was|has)`

| line | construction | kind |
|---|---|---|
| — | banned list (pattern 1), including em-dash | **0 hits** |
| 121 | "it analyses together" | British spelling (writing_conventions "American English": analyze) |
| 200 | "(Analysed only alongside each other…" | British spelling |
| — | "fire" / "data is" | 0 hits |

Grep cannot detect a three-item rhythm list. I checked those by reading. Every list of three in the text names three real things (lines 142–143, 291–293), so none is a hit.

**Block word counts are hand estimates, not tool output.** Body blocks (with approximate words / sentences):
- Question ¶1: ~110 words / 5 sentences
- Question ¶2: ~110 / 4
- Simulated ¶: ~45 / 2
- Step 1: ~65 / 4
- Step 2 ¶1: ~140 / 7
- Step 3 ¶1: ~110 / 7
- "Why the fixed model reads low": ~130 / 8
- "Window size" intro: ~120 / 6
- Stretch bullet (203–212): ~165 / 6
- "Real numbers" bullet (299–306): ~110 / 4

## Findings

| # | location | issue | severity | suggested fix | verified |
|---|---|---|---|---|---|
| 1 | L126–128 | "Every simulated recording here … with 15 shared moments planted per recording, 5 each joined by 10, 6 and 3 cells" is false for most of the page. 3B has every moment at 6 cells. 3C has about 7 moments (L266). Fig. 5 plants nothing. Fig. 6 has 6 and 3 moments. The sentence asserts something untrue. | high | "Unless a figure says otherwise, each simulated recording has 32 cells over 45 minutes … 15 shared moments, 5 each of 10, 6 and 3 cells." | yes (in-text) |
| 2 | L161 | "From size variation alone it reads 5% low (one size) to 18% low (three sizes)." With one size there is no size variation, so the 5% must come from the window edge (the "second reason"). The sentence contradicts the two reasons just given. | high | "With one size it reads 5% low, from window edges alone. Three sizes take it to 18%." | yes (in-text) |
| 3 | L243 | "Real recordings are nearer the narrow end of moments" is garbled. The few-moments end is the *wide*-spread end, so "narrow" points the reader the wrong way. | high | "Real recordings sit at the few-moments end." | yes |
| 4 | L62–63 vs L117, L325–326 | λ is defined as "moments per minute" in Terms, but λ*k*/*N* gives "coordinated onsets per second" (L117), and the formulas use "rate λ per second" (L325). One symbol carries two units. | medium | Pick one unit. Either define λ per second and convert to per minute only where it is reported, or write λ*k*/(60*N*) at L117. | yes (in-text) |
| 5 | L42–46 | "one caveat matters most:" is followed by two caveats: the field-wide rate change, and the change in size or spacing of moments. L308 itself says "the caveats". | medium | "two caveats matter most:" | yes |
| 6 | L115–116 | "so the answer reads high; *Why the fixed model reads low*, below, says why". The reader is sent to a heading that says the opposite. The section explains that *k* reads high while the share reads low, but this sentence doesn't say that. | medium | "so *k* reads high. *Why the fixed model reads low*, below, explains why a high *k* makes the share read low." | yes |
| 7 | L137–138 | "are outside it on every set here … and are not checked". "Outside it" can mean outside the band's scope or outside ±25%. Both happen to be true, so the sentence asserts two things at once. | medium | "read more than 25% off on every set here (Figure 4, 26–69%), and the check does not test them." | yes (L192) |
| 8 | L90–91 | "*f*₃, triples beyond that". "That" reads as "beyond the pairs", but it means beyond what independent cells give. | medium | "and *f*₃, triples beyond the same baseline" | yes |
| 9 | L33–35 | "Implicitly, it counts as coordination onsets in several cells … more often than the same cells give when…". "Implicitly" is a hedge. The bolded sentence has a buried verb ("counts as coordination [X]") and the odd verb "give". | medium | "What it counts as coordination: onsets in several cells within one window (1 s here), more often than those cells produce once each one's onsets are slid by up to about half a minute." | n/a (judgment) |
| 10 | L39–41 | Parenthetical "(ADR-0017 makes this the first exception … `fireflies` analysis's work)" is internal governance shown to a public, non-math reader. A record number is an index, not content (writing_conventions "Name things"). | low–medium | Cut it, or move it to *For developers*. | yes (house rule) |
| 11 | L127–130 | "Figure 3 checks…; Figure 4 varies…; Figure 5 plants nothing; Figure 6 varies…" previews what the next sections say, which the house voice forbids. It is also incomplete: Fig. 6 also varies the background (L250–251). | low | Cut the sentence. Each subsection already names its figure. | yes |
| 12 | L37, 86, 180–181, 197, 235–236 | The figure name is set in commas ("In Figure 2A, same mean, wider spread, the recording…"). It reads as an appositive clause and stalls the parse. The pattern recurs. | low | Mark the name off: "In Figure 2A (*Same mean, wider spread*), …" | yes |
| 13 | L97–98 | The heading says "Chance is measured, not assumed", and the body repeats "So chance is measured." | low | Cut "So chance is measured." | yes |
| 14 | L103–105 | "each cell keeps its number of onsets over the whole recording" restates "Each cell keeps its rate" from the sentence before. | low | End at "the columns of ticks in Figure 1B are gone." | yes |
| 15 | L69–71 | "copy the **fast stream**: … these simulations copy the fast one" says the same thing twice. "each recording's events" also blurs real recordings with bench recordings. | low | "Its recordings copy the **fast stream**, one of the two named streams (fast and slow) into which each real recording's events are split." | yes |
| 16 | L121, L200 | British spellings "analyses" (verb) and "Analysed". The house rule is American English. | low | "analyzes", "Analyzed" | yes (Grep + writing_conventions L142–144) |
| 17 | L299–301 | "is under a contamination stop since 2026-10-05" has the wrong tense. | low | "has been under a contamination stop since 2026-10-05" | yes |
| 18 | L205 | "28 times the quiet background in all": "in all" is unclear. It means the total rate, 0.1334 + 0.0049 = 28× quiet, which I checked. | low | "a total rate 28 times the quiet background" | yes (arithmetic) |
| 19 | L221 | "barely registers at all": "barely" and "at all" pull against each other. | low | "barely registers." | yes |
| 20 | L230 | "These recordings" has no clear referent. It could mean the nothing-planted set or the changing-rate set. | low | "Recordings whose rate changes like these are what … was written for" | yes |
| 21 | L286 | "this page's two weaknesses". The page names more than two: the model choice, close moments, single-recording spread. "The same authors" is also loose, since Reimer and Ehm are not all of the earlier list. | low | "two of the weaknesses above … The same group" | yes |
| 22 | L261, L276–281 | Undefined jargon for the stated non-math audience: "correlogram", "cumulants", "compound Poisson family", "multiple-interaction process". The literature section can keep a scholarly register. "Correlogram" in the body is unexplained. | low | Define "correlogram" or drop it ("the measured fast-stream jitter"). Note that the literature section is for specialists. | yes |
| 23 | L136 | Code name `CAL_NO_PROBE` sits in body prose for a lay reader. It is repeated at L320. | low | Say "the tool's own note" in the body and keep the identifier under *For developers*. | yes |
| 24 | L178 | "every pair and single at least 120 s from the next". "Single" used as a noun is unclear. | low | "every pair and every single moment" | yes |

## Passage test, per block

For each block: its payload sentence, where that sentence sits, and what the other words buy.

- **The question ¶1 (L31–37).** Payload: "anything that lines cells up over less than about a minute counts, including … a stretch where the whole field gets busier" (near the end). The opening question and the method sketch are worth keeping. Fix: promote the payload to right after the question, and apply #9.
- **The question ¶2 (L39–46).** Payload: the two treatment caveats (end). The ADR parenthetical buys nothing a reader needs (#10). After the cut, the payload sits second, which is fine.
- **Simulated note (L48–50).** Payload is first. Lean.
- **Terms (L54–73).** Definitions, not argument. The only waste is the repeated fast-stream line (#15).
- **Step 1 ¶1 (L79–82).** Payload: the half-window double count. The straddle example is concrete and earns its place.
- **Step 1 ¶2–3 (L84–93).** Payload: "sharing shows in how spread out the counts are" (middle). The 90 vs 720 example is the evidence a sceptic needs. Keep.
- **Step 2 (L97–109).** Payload: "what is destroyed is which cells had onsets at the same time" (L103, near the end of ¶1). The parenthetical on slide spacing (L101–102) is real evidence. Cut the redundancies (#13, #14) and lead with the payload after the first sentence.
- **Step 3 (L113–122).** Payload: "dividing that by the average cell's event rate gives the share" (the last sentence of ¶1). The worked 8.1 example buys a lot. The "reads high / reads low" pointer costs a stumble (#6). ¶2's payload, "steadies the median, not a single recording's answer", is last and fine.
- **Does it get the right answer? intro (L126–130).** Payload: the generator settings. The roadmap sentence buys nothing (#11), and the first sentence overclaims (#1).
- **The check, and the two models (L134–155).** The payloads ("±25% on the share only"; "pairs and triples alone cannot tell the two apart") are each stated once. The bullets are evidence. Lean, apart from #7.
- **Why the fixed model reads low (L157–164).** Payload: "In real recordings the spread of moment sizes is not known, so neither is the size of the error." It is bold and near the end, as expected. Promote it to the first sentence ahead of "Two reasons" and fix #2.
- **Model choice (L166–170).** Payload is last, at the right weight. Keep.
- **Window size intro (L174–181).** Payload: "the bench never plants the closest moments real recordings may hold; these sets plant them on purpose" (middle). The set inventory is necessary for Figure 4. The final pointer sentence is filler, since the heading already names the figure.
- **Window bullets (L183–193).** Bold leads carry the payloads. The rest is numbers a sceptic would ask for. L192's "Across all sets…" duplicates the per-set figures, but it is the one sentence L137 relies on. Keep it and cut the per-case ranges at L191 instead.
- **What else it counts, intro (L197–201).** Lean.
- **Stretch bullet (L203–212, ~165 words).** Payload: the bold lead. The mechanism (slides of about half a minute, so only the edges survive) and the 8.2/3.0/1.2% series are the evidence. "The worst single recordings read up to 14%" earns its place. This is the longest block on the page, but every clause carries a number someone will check. No cut. Fix #18.
- **Busier bullet (L213–217).** Two points under one lead: the size of the rate rise, and ramp versus sharp edge. Fine, but the last sentence repeats the 2.8 vs 3.0 comparison that is already implicit. Optional trim.
- **Smooth change, clumping, no stretch (L218–228).** Payloads lead in bold. Lean, apart from #19.
- **Staude pointer (L230–231).** Payload at the end ("not tried here"). The same point is made again at L289 ("Neither correction has been tried here"). One of the two is redundant. Keep L289 and cut L230–231, or keep L230–231 as a forward pointer only.
- **How far one recording strays (L235–253).** The payloads are bold leads. The bullet at L243 is broken (#3). L253 is a one-liner that answers L200–201's "usually give no answer". Keep.
- **Simulated recordings (L257–269).** Payload: the bench generator with events replaced by planted moments. The last sentence repeats the 3C description from L149–150. Low-value repetition.
- **Where the method comes from (L273–295).** Payload: "What is this project's" (L291), which comes last. This is correct for an attribution section, since the prior work must come first. Lean.
- **What waits (L299–310).** Payload: "They are not quoted here, because … contamination stop" (bold, second sentence). The mechanism detail (pinned cells, four DI recordings, three awaiting review) is the evidence a sceptic would want. Keep. Fix #17.
- **For developers.** Out of scope for prose length. L322–323 ("said to 'bracket' the answer; in Figure 3A and 3C both read low") is precise and earns its place.

**Summary:** none of the banned constructions appear. Three statements are false or self-contradicting (#1, #2, #3). One unit is inconsistent (#4). Four sentences are ambiguous (#5–#8). The rest are low-severity redundancies and house-rule slips. No block is longer than its point by the standard of this role. The page's density is evidence, not padding. Promoting the payload is the fix in Step 2, "Why the fixed model reads low", and The question ¶1.
