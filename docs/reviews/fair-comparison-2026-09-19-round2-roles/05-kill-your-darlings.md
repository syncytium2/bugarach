<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round2/. -->

GRANT 5 ok — Read, Grep, Glob (SubagentHandback is the hand-off channel. I hold no Edit, Write, NotebookEdit or Bash.)

**Role 5 (Line editor, "Kill Your Darlings") on `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html` (git 16ac704)**

**Mechanical search.** I did not run `murderboard_prose.sh`. My grant has no Bash, so I cannot run it. The output I rely on is the caller's run, pasted verbatim in the brief (upstream syncytium2/murderboard @ 08f5ddb, with the banned list from this repo's `docs/doc_review_process.md`). It found no banned construction.
- **My own check against that list:** I read every prose line, captions included. I found no fake-rhythm three-item list: the two triples (line 113 "mean, spread, loudest few"; line 275 "the new simulator, CoactDetect's sliding values…, or the tuning") each name three real things. There is no em-dash pivot and no "In today's" opener.
- **House-rule greps:** No singular "data", no British spellings except the tool name "draughtsman", and one "a F1".
- **How I read the prose:** Lines 75, 141, 156, 190, 223, 235, 251 and 289 are single-line SVG figures. I read their captions and Table 1's text cells through Grep, not whole.

---

## Passage test: the 15 blocks over 120 words

| block (HTML line) | words | payload sentence | where it sits | what the other words buy |
|---|---|---|---|---|
| 29: title, question, answer, terms | 419 | "So this run does not settle which side is better." (l.46) | Middle of the Answer paragraph, after 8 numbers | The margins earn their place. The fold counts ("4 of 4", "3 of 4") repeat Section 6 word for word and can go. The *t* entry in Terms defines a symbol that first appears in Section 6, which defines it again, so cut it. The Terms paragraph comes **after** three uses of F1 (l.35, 40, 43). |
| 60: §1 and Figure 1 | 359 | "A detector has to find the few real events without firing on either." (l.66) | Middle | One 60-word sentence (l.67–71) walks through Figure 1, and the caption then says the same thing again (triangles, lane, probe). The body could just point at the figure and define *distractor* and *probe*. It also says "quiet/busy background" before §2 has introduced two backgrounds. |
| 78: §2 bench | 264 | "…every planted event is known." (l.81–82) | End of the first paragraph, which is correct here | Specification a sceptic needs. It passes. One preview ("One consequence matters later") can become a cross-reference "(section 4.5)". |
| 103: §3, Table 1, warning box | 592 | "The difference between the nets that matters most is where each stops treating ROIs separately." (l.109) | Second paragraph, which is fine | Most of the words are Table 1, which earns them. The 70-word "not on this page yet" box (tool name, darkroom path, PR #660) is plumbing for the author, not content for the reader. Cut it to one row in §8. |
| 122: §4.1 and Figure 2 | 428 | "The winner is then scored once on the held-out fold, which is never seen while choosing." (l.128) | End of the first paragraph | Needed. It passes, apart from a broken cross-reference (finding F3). |
| 143: §4.2 and Figure 3 | 411 | "Four outer folds were then fewer than four independent fits…" (l.149–151) | End of the first paragraph. The heading already says it. | Needed, but the tense makes it ambiguous whether the defect hit *this* run (F7). |
| 158: §4.3 first paragraph | 123 | "The project's defaults are still binned, so a search built on them would have tuned the coded side in its weaker mode." (l.164) | **Last sentence.** Written in the order it was thought. | Put it first. The binned/sliding definitions then follow as the reason. |
| 176: §4.4 | 302 | "So every contestant was chosen twice." (l.178) | Early, which is good | Needed. Two wording defects (F9, F10). |
| 192: §4.5 | 633 | The section's point is never stated in one sentence. The closest is "Nothing was re-chosen, so these curves bound what tuning the gap could do rather than measure it." (l.208–209), and it sits **at the end of the second of four paragraphs**. The claim the reader needs, *"only the coded side tuned its merge gap, and on this bench a wider gap buys F1 for nothing"*, has to be put together from paragraphs 1 and 2. | Buried | Paragraph 1 (why merging is free here) and paragraph 2 (the numbers) earn their place. The provenance in paragraph 3, "It was applied afterwards, when the other workstation pointed at the merge gaps, by `tools/…`. That tool uses goal 1's own scoring on 12 crowded recordings per background", is 40 words about the process, not the result. It also refers ahead to a workstation §5 has not introduced, and restates the 24 recordings as 12 per background. Paragraph 4's last sentence (nets not crowd-checked) is repeated at l.267 and l.328. **Fix:** open §4.5 with the one-sentence claim, and move the tool name to §8. |
| 226: §5 | 179 | "A difference between the two runs is then a difference between draws of data." (l.232) | Middle | Mostly needed. The hostname "WSMIP065" and the path with a parenthesis inside the `<code>` element add nothing a reader can use (F13). |
| 238: §6 intro, Figure 7, Table 2 | 551 | "Read the corrected values as a ranking of consistency, not as tests." (l.246) | Middle of the second paragraph | The citation history (Bouckaert and Frank; Bengio and Grandvalet, ~40 words) shows thoroughness and does not help a newcomer. Keep one clause and a reference. Start the *t* paragraph with the payload. |
| 255: results bullets | 448 | Each bullet leads with a bold claim, which is the right structure. **Exception:** bullet 3's real payload is its *last* sentence, "The earlier lead does not reappear on this simulator, but this run cannot say which of three changes removed it" (l.274–275). That answers the question the lede opens with (the +0.103 lead), and it sits under the bold heading "Tuning moved some nets and not others". | Buried in bullet 3 | Promote it to the bold lead of bullet 3 (F5). Bullet 2 largely restates the lede and §4.5. That is acceptable in a results section, but its "not checked on crowded recordings" clause is the second of three copies. |
| 289: Figure 8, Table 3, refits, budget overruns | 648 | "Exceeding the budget can only help a net's F1 under the budget, so this does not favor the coded side." (l.302) | Last sentence, which fits a closing aside | Needed. Wording defects F15–F17. |
| 308: §7 Limits | 540 | A list, so each item is its own payload. Items 2 and 3 are too long. Item 2 (~110 words) carries a commit hash, a branch name, a handoff filename and "decision 3". Those are lookup keys, not content, and belong in §8. Item 3 (~70 words) is a pasted declaration that never names *which* value is out of interval (F4). | n/a | Cut item 2 to its claim and its unknown. Rewrite item 3 in plain prose. |
| 348: §8 | 184 | Reference list. The word count is mostly paths. | n/a | Passes. The ~60-word developer warning about `ARCHITECTURES[name].make()` is true and useful to someone reusing the code, but it is instructions for a developer inside a report for a reader. Low priority; consider a code comment or the README instead. |

---

## Findings

Format: location · issue · severity · suggested fix · verified against source (yes/no)

**F1** · l.35, 40, 43 (lede) vs l.51–53 · F1 is used three times before the Terms paragraph defines it. This breaks "define every abbreviation at first use", and in the lede a reader new to the project cannot skip it. · **medium** · Move the Terms paragraph above "The question", or gloss F1 at l.35 ("F1, a 0-to-1 score combining events found and false calls"). · yes

**F2** · l.48 (lede) · "binned SCE" is used in the headline answer, but SCE is expanded only in Table 1 (l.113, "synchronous calcium events, SCE"). · **medium** · Expand it at l.48. · yes

**F3** · l.139 · "Settings that break the context-window rule in section 4.5 were skipped." §4.5 (l.192–222) has no context-window rule. It covers the merge gap and the crowded-recording check. A reader who follows the reference finds nothing. · **high** · Point to the section that really states the rule, or state the rule here in one clause. · yes (grep: "context" appears in prose only at l.139 and l.169)

**F4** · l.322–323 (Limits, item 3) · "One of the bench's values sits outside its own measured interval." The item never names the value. The quoted declaration gives "0.18", "0.1905 (6 median participants over 31.5 median ROIs)", "BENCH_RECORDING's docstring" and "awaiting Tony". That is a code identifier and a first name the page otherwise calls "the project lead". A new reader cannot tell what quantity is meant or who Tony is. · **medium-high** · Paraphrase it: name the quantity (it looks like the 18% participation level from l.85, but confirm), give the measured value and interval as percentages, and say "the decision is the project lead's and is open". Drop the docstring reference. · partly (the text was checked; which quantity it is was not)

**F5** · l.270–275 (results, bullet 3) · The answer to the question the lede opens with (the earlier +0.103 lead is gone, and this run cannot say why) is the last sentence of a bullet headed "Tuning moved some nets and not others". · **medium** · Make it the bold lead: "The earlier +0.103 lead does not reappear, and this run cannot say which of three changes removed it." The per-fold lists then support it. · yes

**F6** · l.61, 90, 75 caption, 314 · "Event" means two things: a single cell firing ("one tick per event", "0.0052 events per second per ROI", "2,595 events in the whole 45-minute recording", "detectors call events on the steps") and a *coordinated* event (the thing being detected: "15 planted events", "finds the most events"). l.314 also uses "detectors" for what looks like upstream per-cell event detection. · **medium** · Keep "event" for coordinated events only. Call the per-cell ones "firings" or "cell events" throughout, and at l.314 name which step does the detecting. · yes

**F7** · l.146–147 · "At some training seeds the run of 10 then fell inside the first training fold, so held-out folds that share that fold **trained** exactly the same model." The past indicative says this run was affected. The heading, the "would have fitted" at l.149 and the Figure 3 caption say the defect was fixed first. · **medium** · Change it to "would have trained". · yes

**F8** · l.184, 190 caption vs l.70 · "The quiet recordings with nothing planted" clashes with "the quiet background" (the 0.0052 rate) from §1. A reader can take "quiet recordings" to mean the low-background ones. · **medium** · Call the planted-nothing set "the empty recordings" (or "null recordings") everywhere, and keep "quiet" for the background. · yes

**F9** · l.186 · "a floor that bound in no fold". "Bound" (past tense of bind) reads as a noun. · low · Change to "a floor no fold reached". · yes

**F10** · l.173 · "LoCo uses the 99.9th percentile": the sentence does not say a percentile of what. · low · Add "of the same count on time-shifted copies (Table 1)". · yes

**F11** · l.210–218 · "It was applied afterwards, when the other workstation pointed at the merge gaps, by `tools/crowded_check_fair_comparison.py`." "The other workstation" has not been introduced (that happens in §5), and "pointed at" makes a machine the actor for what a person flagged. The recording count appears twice ("24 bench recordings", "12 … per background"). · low-medium · "It was applied after the run, once the replicate's author flagged the merge gaps, using goal 1's scoring on the 24 crowded recordings." Move the tool name to §8. · yes

**F12** · l.35–36 · "CoactDetect tuned on one setting" is ambiguous: one parameter tuned, or tuned at one operating point? · low · Say which. · no (the meaning cannot be checked from the page)

**F13** · l.117, l.234 · A parenthesis sits inside `<code>`: "`comparison.svg (pull request #660, not yet on main)`" and "`…replicate-run-status/ (WSMIP065's report)`". It reads as part of the path. The hostname WSMIP065 (l.228, 234) is a label, not a name. · low · Move the parenthesis outside the code element, and write "a second workstation" (put the hostname in §8 if it is needed). · yes

**F14** · l.308–321 (Limits, items 1–2) · Dates and keys used as content ("decision of 2026-09-17", "commit 2120516 on branch …", "`HANDOFF-…md`, decision 3"). In "…asked for exactly that; **it** is not evidence that the effect is negligible", the antecedent of "it" is ambiguous. The sentence just before reports a re-measurement that *is* evidence the effect is small, so the reader cannot tell what "it" means. · medium · Move the hash, branch and handoff to §8. Rewrite as "Listing it here does not show the effect is negligible", or say directly what the re-measurement does and does not show. · yes

**F15** · l.295 · "a F1 with no calls counts as 0" · low · Change to "an F1". · yes

**F16** · l.295 vs l.148, 156 · Training seeds are numbered two ways: "training seed 0" (0-based, Figures 3 and 3's caption) and "training seed 4 of 5", "5 of 5" (1-based ordinals). Figure 2's caption calls out the equivalent fold-numbering shift. The seed shift is not called out. · low-medium · Pick one convention and state it once. · yes

**F17** · l.295 vs l.95 · "It calls one long stretch per recording, so its few hits come at perfect precision and almost no recall." That clashes with §2's rule that "a call that spans a long stretch hits any event inside it", which suggests a long call would have *high* recall. As written, the reader cannot square the two. · low-medium · Add the clause that resolves it (for example, one call can claim only one event, or the stretch is short relative to the recording). · no

**F18** · l.282–283 · "4 coded detectors" are listed as "LoCo, SPIKE-synch, rate+context", missing the conjunction, with the fourth (locust) in the next sentence. "Admissible" is used here and in the Figure 7 caption and Table 2 but never defined in the prose. · medium (the undefined term) · Define "admissible" once, in §4.5 (within budget *and* passing the crowded check, if that is the meaning), and write "LoCo, SPIKE-synch and rate+context". · yes (term undefined); meaning not verified

**F19** · l.53–54 (Terms) · *t* is defined in the Terms paragraph, but no *t* appears before §6, which defines it again. · low · Cut the *t* entry from Terms. · yes

**F20** · l.94–95 · "One consequence matters later:" is a preview. · low · Replace with "(this matters in section 4.5)". · yes

**F21** · l.85–86 · "Each event's onsets are spread by 0.36 s": only the Figure 1 caption says this is a standard deviation. · low · Write "have a standard deviation of 0.36 s". · yes

**F22** · l.158–165 · The payload of §4.3's first paragraph is its last sentence. Also, "binned mode" (a counting mode of CoactDetect and LoCo) sits beside a detector *named* "binned SCE" with no note on how the two relate. · low · Lead with the payload, and add one clause relating the two. · yes

**F23** · American English and consistency · Plain-text "draughtsman" (l.115, a tool name) reads as British spelling; mark it as code. "rescored" (l.201) vs "re-scored" (l.47, 327). "fitted" (body) vs "fit" (Figure 3 caption). ASCII hyphen used as minus in l.271. "1e-05" (l.168) is code notation. · low · Mark the tool name as `draughtsman`, pick one hyphenation, use "−" for minus, and write "10⁻⁵". · yes

**F24** · l.336 · "Under the budget, a search can even score higher than without it." This is counterintuitive and unexplained, and "even" is doing the work an explanation should do. · low · Give the reason (path dependence of the one-setting-at-a-time search) in one clause, or cut the sentence. · no

## What I checked and found clean

- No banned constructions (the caller's tool run plus my own read).
- No singular "data".
- No closing recap paragraph.
- The per-bullet bold leads in §6 put each payload in front, except bullet 3 (F5).
- "0.02 is a judgment the project lead has not yet signed" and "this run cannot say which of three changes removed it" name their unknowns instead of hedging, which is the house voice working as intended.

## One item outside my scope

Not scored, passed on for role 4: l.292 says 210 held-out net refits, while 4 nets × 4 folds × 5 seeds × 2 selections = 160, and l.300 gives 80 under the budget.
