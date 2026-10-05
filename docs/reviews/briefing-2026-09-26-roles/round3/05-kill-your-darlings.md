> Archived verbatim except one redaction: in finding 4, the gap to one real call is replaced by `[t]`
> (FOUNDATIONS §5). The finding's substance survives: a raw-seconds value with false precision.

GRANT 5 ok — Read, Grep, Glob

(I also hold SubagentHandback, which is only the hand-off channel and cannot edit anything. I hold no Edit, Write, NotebookEdit or shell.)

## Role 5, Kill Your Darlings: blind review of the full-panel briefing

**Artifact:** `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html` (693 lines). Its prose comes from `<worktree>/briefing-page/tools/make_briefing.py`. I did not open `docs/reviews/briefing_2026-09-26-roles/`.

**The count was not run.** `murderboard_prose.sh` does not exist in this repo and I have no shell, so I did the search with Grep and counted words by hand. The block word counts below are my estimates, not tool output. Treat this as the tool not running, not as a clean result.

**Which banned list I ran:** the role-5 list in `doc_review_process.md`. I also checked the house rules in CLAUDE.md and `writing_conventions.md`: American English, "data" is plural, no "fire" for calcium events, define every abbreviation.

**Search results (line · construction · kind):**
- delve, leverage, robust, seamless, crucial, landscape, tapestry, "it's worth noting", "not just X but Y", "it's not about", "In today's": 0 hits.
- Em-dash pivots: 0. The only dashes are en-dashes in the Table 3–5 ranges and summary.
- Three-item lists built for rhythm: none. Each list I checked (streams; budgets; leader, runner-up, comparison) has that many real items.
- "fire/fires/fired/firing": 0.
- "data is/was/shows": 0.
- British spelling: 1 hit, "favour" at line 62. It comes from `make_briefing.py:1213`. Defect under the American English rule.

**Block sizes (block · words · sentences), estimated:**
- byline, line 59: ~75 words · 3 sentences
- headline box, line 62: ~420 · ~22
- Table 1 caption: ~110 · 6
- "How to read it" details, line 582: ~560 · ~20
- viewer box, line 589: ~170 · 6
- "Read this first" box, line 590: ~65 · 3
- examples rule, line 591 (two paragraphs): ~210 · 8
- "Passed over…" lines: 40–110 words each

## Findings (location · issue · severity · fix · verified against a source)

1. **Headline box, line 62.** The box never states its own conclusion. Across the three bullets the numbers say this: against the *shipped* CoactDetect, most rows beat it on the new bench; against CoactDetect *retuned on the new bench*, 0, 1 and 1 rows do. So the new bench mostly exposes the shipped setting. It does not show better detectors. That reading sits mid-bullet three times, and the title "What the new bench against the old bench shows" points somewhere else. **Major.** Fix: open the box with that one sentence, taken straight from the counts, and retitle it. Then the per-stream bullets become evidence rather than the message. Verified: yes (headline and Table 1 agree).

2. **Headline bullets.** The three bullets repeat the same 25-word clause ("have a 95% interval of ΔF1 wholly above zero against CoactDetect's shipped setting") and differ only in numbers. They are also not parallel:
   - Only fast gets the "F1 without decoys" sentence, yet slow's figure (17 of 18) is the striking one.
   - Fast says F1 "falls". Slow and combined say "moves" for falls too.

   **Medium.** Fix: say the clause once, then give per stream `new x/N · old y/N · vs proposal z/N · without-decoys w/N`, or point to Table 1. Use "falls" throughout. Verified: yes (the fast-only condition is at `make_briefing.py:1191`).

3. **Figure 3 caption, line 601.** It says CoactDetect's nearest call "is 2.5 s away, beyond the 2.5 s tolerance". At the precision shown, that contradicts itself. **High:** a reader stops here. Fix: print one more decimal where the rounded gap equals the tolerance, or write "just beyond". Verified: yes.

4. **Figure 4 caption, line 602.** It gives a gap of "[t]" in raw seconds to one decimal. That is false precision in raw seconds, against the minutes-friendly rule. **Low.** Fix: write it as minutes and seconds. Verified: yes.

5. **"Passed over for the runner-up", slow, line 606.** It says "no disagreement with CoactDetect · proposal to show (… 62 calls only its own, 0 calls only CoactDetect's)". The sentence is false as written: 62 calls only its own *is* disagreement. The rule needs disagreement *each way*. There are also nested parentheses. **High.** Fix: "never lacks a call CoactDetect makes (0 calls only CoactDetect's; 62 only its own), so there is no two-way disagreement to show". Verified: yes.

6. **Examples rule, line 591.** "both agrees and disagrees with CoactDetect at least once each way": agreement has no direction, so "each way" garbles the rule. **Medium.** Fix: "shares at least one call with CoactDetect, and each has at least one call the other lacks." Verified: yes.

7. **Line 591, first paragraph.** "the calls counted are the ones the review pages draw: the four detectors that take the participation floor as their minimum at their own window's floor, the rest as they ran" has no verb. **Medium.** Fix: "for the four detectors that take the participation floor as their minimum, the run at each window's own floor; for the rest, the run as it is." Verified: yes.

8. **Line 591, second paragraph.** "ROIs with an onset in [onset − 1 s, onset + width + 1 s]" uses "onset" for two different things in one clause. **Medium.** Fix: "[call onset − 1 s, call onset + call width + 1 s]". Verified: yes.

9. **Summaries at lines 599, 610 and 619.** "the leader calls many events CoactDetect does not" and "the leader misses many events CoactDetect calls". These are real recordings with no ground truth, so "events" and "misses" assert that one detector's calls are true. "only its own" is also clipped. **Medium.** Fix: "the leader makes 32 calls CoactDetect does not, and CoactDetect makes 1 the leader does not" (same pattern for all three). Verified: yes.

10. **Captions of Tables 6–8.** "…agree with two or more calls of the other, where a merge would hide" is cryptic. The captions also open lowercase ("fast stream:"). **Medium.** Fix: "…each such call may cover two events merged into one." Capitalize the opening. Verified: yes.

11. **"Read this first" box, line 590.** It comes *second*, after the viewer-setup box. Its payload is the most important sentence in section 2: these examples use a different CoactDetect, and they cannot test the leaderboard's top rows. **Low–medium.** Fix: swap the two boxes, or move the viewer instructions into a `<details>`. (This is a paragraph inside one section, so it is mine, not role 11's.) Verified: yes.

12. **"How to read it", ORX bullet, line 582 (~120 words).** It asks "Does the order hold…?" and never answers. The answer sits at the end, behind a list of top rows per stream: the order mostly holds (ρ 0.76–0.94), and 0 intervals cross from above zero to below. **Medium.** Fix: lead with "Mostly yes: ρ = 0.91 / 0.76 / 0.94 and no interval crosses zero in either direction." Put the top-row list after it or cut it. Verified: yes.

13. **ORX bullet (line 582) against Table 1.** The bullet's "top row" (flagged rows included) and Table 1's "top unflagged row" name different rows for fast and slow. A reader comparing the two sees a contradiction. **Medium.** Fix: write "top row, flagged or not" in the bullet. Verified: yes.

14. **Budgets bullet, line 582.** "(a stretch where the background rate is raised with nothing planted; outside on the quiet background, as the search gates it)" has a semicolon inside a parenthesis, and "as the search gates it" is opaque. "The worker's run notes" appears here and again in the ORX bullet without saying which worker or which file. **Medium.** Fix: split into two sentences, "outside the stretch, only on the quiet background". Name the notes by what they are ("the training run's own notes, `<file>`"). Verified: partly. The wording is on the page; I did not open the notes.

15. **Decoys: the bullet in line 582 and the Terms entry.** "ADR-0006 rules that such a call is coordination by construction, so the tables give F1 without decoy calls", and in Terms "…hence F1 without decoys". The step in between is missing: if a decoy is real coordination, a call on it is not plainly a false alarm. **Medium.** Fix: state that step once, in Terms, and cut it from the bullet. Verified: no (I did not open ADR-0006).

16. **Repeated definitions.**
    - "within 0.01 F1, the noise unit ADR-0010 uses for its focus rule" appears three times nearly word for word: Table 1 caption, line 582, Terms.
    - ΔF1 is defined four times: headline, line 582, Figure 1a caption, Terms.
    - "the glossary's distractors" appears twice.

    **Low.** Fix: keep Terms plus the Figure 1a caption, which should stand alone. Cut the rest. Table 1's caption can drop to about 50 words. Verified: yes.

17. **Byline, line 59.** "(the full panel, ADR-0010, the decision record that moved…)" chains appositives, so it reads as if the full panel *is* ADR-0010. "Every number is read from the night's files, and the budget limits from…" drops its verb. "The night of 2026-09-25" is also imprecise: the old bench and the count rows were scored the next evening (line 582 gives the times). **Medium.** Fix: split it. "The night of 2026-09-25 searched every coded detector and trained every learned model on the new bench (ADR-0010: planted events spaced as measured in real recordings). Scoring finished 2026-09-26 evening." Verified: yes, from the page's own timestamps.

18. **Detector list (line 65): chorus_gain_norm.** "chorus_norm with line's vote, a learnable gain and bias" leaves unclear whether "a learnable gain and bias" describes the vote or is a second addition. **Medium.** Fix: "chorus_norm plus line's vote, weighted by a learnable gain and bias" (or "plus … and a learnable gain and bias"), whichever is true. Verified: no (I did not open the model code).

19. **Detector list (line 65): locust.** "modified from CICADA … by what it is fed" is opaque. **Medium.** Fix: "CICADA's method, the Cossart lab's software, changed only in its input (ADR-0002)". Verified: no.

20. **Detector list (line 65): abbreviations.** "ISI" and "SCE" are never defined, and "generate_sce routine" is an index, not a name. **Medium** (define every abbreviation). Fix: expand ISI (inter-spike interval) and SCE (synchronous calcium event) at first use, or add them to Terms. Name the source by what it is. Verified: yes, neither is in Terms.

21. **Detector list (line 65): line.** "how much of the field is lit and how tightly" is a metaphor with no defined quantity. **Low.** Fix: name the two inputs (fraction of cells active; how close in time their onsets are), if that is what they are. Verified: no.

22. **Terms entries.**
    - "shipped: The setting a coded detector ships with" is circular.
    - "no pick: A family…" uses "family" where the page elsewhere says "model".
    - "(the count folder calls it 'shipped')" points to an unnamed folder.
    - "(the house clock's summer name)" is decoration.

    **Low.** Fix: define shipped as "the setting in the detector's code before this night". Write "model". Name the folder or cut the parenthesis. Cut the decoration. Verified: yes.

23. **"CoactDetect is the comparison side"** (lines 594 and 606). "Side" is jargon. **Low.** Fix: "(the comparison itself)". Verified: yes.

24. **Line 62: "Tony asked to see new against old".** The page is addressed to Tony but talks about him in the third person. **Low.** Fix: "you asked". Verified: yes.

25. **Line 62: "favour".** Must be "favor" under the American English rule. **Low.** Fix at `make_briefing.py:1213`. Verified: yes.

## Passage test, block by block (the one sentence it delivers · what the other words buy)

- **Byline:** payload is "One night's search and training on the new bench, scored on unseen seeds; nothing adopted." The appositive chain buys nothing. Split it (finding 17).
- **Headline box:** payload (unstated) is finding 1's sentence. The three near-identical bullets are the author being thorough, not evidence a sceptic needs; Table 1 already holds them. The decoy mechanism sentence is real evidence, so keep it. The closing caveat paragraph is needed; keep it.
- **Table 1 caption:** payload is "How to read the counts." About half repeats Terms and line 582 (finding 16).
- **Table 2 caption:** tight. Keep.
- **Detector list and _part note:** earns its place. Four sentences are unclear (findings 18–21).
- **Figure 1a–c captions:** tight. Keep.
- **"How to read it" (~560 words):** payload per bullet. Interval: "seeds only, uncorrected, fast narrower". Order: "sorted by new ΔF1". Decoys: "decoy calls are ambiguous, so F1 without decoys is shown". Budgets: "which limits are in force". ORX: "the order holds". Scoring times: provenance. The payload sits last in the ORX bullet (promote it, finding 12). The budgets bullet is longer than its point (finding 14).
- **Viewer box:** instructions. Every step earns its place, but it hides the "Read this first" box (finding 11).
- **"Read this first":** three sentences, all payload. This is the best block on the page. Move it up.
- **Examples rule (line 591):** payload is "leader = first eligible row in Figure 1's order; one median call per kind". The method details are warranted, but two sentences are broken (findings 6–8).
- **"Passed over…" lines:** these are the audit trail the rule promises, so they stay, but finding 5 is false as written. The "chosen by the rule among rows the leaderboard cannot separate" lines are good: they say the leader is not shown to be better. Keep them, and consider putting that sentence first in each stream's subsection.
- **One-line summaries after Tables 6–8:** right length, wrong verbs (finding 9).
- **Figure 2–10 captions:** dense but each clause is used. Findings 3 and 4.
- **Section 3 intro:** functional. Keep.
- **Terms:** mostly tight. Finding 22.

## Files
- `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`
- `<worktree>/briefing-page/tools/make_briefing.py`: `headline` at line 1173 (findings 1, 2, 24, 25), `viewer_box` at line 1239, `TERMS` at line 1546.
- `<worktree>/briefing-page/docs/writing_conventions.md` (American English section at line 142).
