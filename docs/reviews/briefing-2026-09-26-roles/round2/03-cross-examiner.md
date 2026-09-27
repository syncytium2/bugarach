GRANT 3 ok: Read, Grep, Glob (SubagentHandback is the hand-off channel, not an editing tool)

# Role 3, Cross-Examiner: BLIND pass on the 2026-09-26 full-panel briefing

**Surface checked:**
- **Built page:** `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`, all 646 lines. That covers the headline, the three Figure 1 panels (SVG coordinates converted back to ΔF1), Table 1, the "How to read" and "What is compared" boxes, Tables 2–4, the examples section (Figures 2–9 and their three kind × group tables), Tables 5–6, and Terms.
- **briefing.json:** sources, orx, examples.
- **Generator:** `<worktree briefing-page>/tools/make_briefing.py`, only `glance()`, `flagged()`, `setting_words()` and `read_calls()`.
- **Companion files:** `065/README.md`, `065/RUN_C.md`, `064/README.md`, `064/count/README.md`, `docs/GLOSSARY.md`, and the CLAUDE.md plot conventions.
- Blind rule kept: I did not open `docs/reviews/briefing_2026-09-26-roles/` or the generator's git history.

## Verified clean

These are recounted from the figure coordinates and the table cells.
- **Table 1 counts.** Every count per stream and bench matches the Figure 1 intervals. The "above / includes zero / below" counts sum to 22, 18 and 20 rows. The "unflagged" counts (3, 1, 10, 0, 8, 1) and the "top unflagged row" all match.
- **Figure 1 against Tables 2–4.** Row order matches, the ΔF1 values match the plotted x positions, and the orange over-budget marks match the table marks for both benches, every row.
- **Proposals.** There are 12 proposals from the six coded detectors, and 11 carry †. The only bracketed one is SPIKE-synch on combined, at +0.039 [+0.012, +0.065]. All of this agrees with 065/README.
- **Learned picks.** All 24 training-run picks match 064/README. So do the held-out F1 ranges, including the collapsed combined chorus_norm run at 0.10.
- **Seeds and timestamps.** New bench 48/24/24 seeds, old bench 24/24/24, and all four "scored at" times agree with RUN_C, 064/count and briefing.json.
- **count rows.** F1, ΔF1, precision swing and merged calls all agree with 064/count.
- **Examples.** The three kind × group tables add up (91/32/1, 422/1/3, 388/3/71). The per-hour rates are consistent with briefing.json's unrounded hours. Each figure's "one of N" matches its table. Each example recording's group matches Table 6.
- **Tables 5–6.** 8 × 3 = 24 review pages. The recording chips sum to 11+6+9+8+8+5+9+10 = 66 recordings, matching 065/README.
- **Conventions.**
  - Group order is DI, OVX, MALE, ORX in every table and caption.
  - No "fire" wording, and "modality" does not appear.
  - Time labels use the minutes format.
  - Figure numbers are contiguous, 1a–c then 2–9.
  - The page says it departs from 065/README's single over-budget row, and says why.

## Findings

Columns: location · issue · severity · suggested fix · checked against a source

| # | Location | Issue | Sev | Fix | Verified |
|---|---|---|---|---|---|
| 1 | Headline "Fast… median F1 moves −0.127 (0.768 to 0.641)"; Table 1 "median F1 of the other rows"; generator `glance()` line 437 | The number labelled "median" is not the median when the row count is even. `others[len(others)//2]` returns the upper-middle value. Fast new: the 11th and 12th of 22 values are 0.637 and 0.641, so the median is 0.639 and the page shows 0.641. Fast old: the true median is 0.767, the page shows 0.768, so the headline's −0.127 should be about −0.128 to −0.129. Slow and combined happen to match within rounding. | Medium | Use `statistics.median`, or rename the column "upper median". Regenerate the headline sentence from the corrected value. | yes (Table 2 cells + generator source) |
| 2 | Headline "13 of 22 rows" vs Figure 1a header "fast stream · 23 rows" and Table 2 "23 rows" (likewise 18/19 slow, 20/21 combined) | One population is counted on two bases. The headline leaves out CoactDetect's own row; the figure and table headers include it. Nothing on the page reconciles the two. | Low–Med | Say "13 of the 22 rows besides CoactDetect shipped". Or make the figure headers say "22 rows + the reference". | yes |
| 3 | Headline "sit above CoactDetect's shipped setting"; Figure 1a | The headline says "sit above" but means "95% interval wholly above zero". It does not say so; only Table 1's caption does. A reader counting filled marks right of zero in Figure 1a finds 15, not 13 (line_part and chorus_norm have point estimates above zero but intervals that include it). The headline also leaves "unflagged" undefined. | Medium | Put "interval wholly above zero" and "unflagged = within every budget, not on a search limit" in the headline sentence itself. | yes |
| 4 | † on "count (binned) · proposal" (fast) and "count (sliding) · proposal" (combined); Terms "search limit (†)"; Table 1 unflagged counts | k at 0 is treated inconsistently, and the page departs from the companion without saying so. The mark text says "k 0 cells, at its lower limit **by design**". But Terms defines † only as an off value, a grid edge or an extension cap. 064/count/README says k 0 is a hard limit by design, "not a ruling-5 off-limit", and names fast binned as the best in-budget count setting. The page, by contrast, calls it "not adoptable as tuned". The "starting point (untuned)" rows also sit at k 0 (the same `limit` bracketing) and are counted as unflagged. So the same condition flags one row and not another, and it moves the fast and combined "unflagged" counts in Table 1 and the headline. | Med–High | Decide once. Either widen the † definition in Terms to cover "limit by design" and apply it to the starting-point rows too, or drop † for k 0. Either way, say that this departs from 064/count's reading. | yes (064/count README vs page) |
| 5 | Table 2 row 6: "Same scores as CoactDetect · proposal to every digit on the new bench: one result, shown twice"; headline and Table 1 | The page names this row a duplicate, yet counts it twice: in the "13 of 22" above-zero count, in the "4 of 22" old-bench count, and in the median. | Low–Med | Count unique results, or say in Table 1's caption that the duplicate is counted. | yes |
| 6 | How-to-read, ORX bullet: "4 intervals of 51 change side, and 0 cross" | This departs from 065/README ("17 of them move") and RUN_C's list of 17 without saying so. The page's 4 counts only intervals against CoactDetect **shipped**; the 17 also includes intervals against CoactDetect's proposal. The 51 also leaves out the count rows, which 064/count did score on ORX, although the bullet calls it "the same rows". | Medium | Say "4 of 51 against CoactDetect shipped (the worker's 17 also counts intervals against its proposal); the count rows are not in this check." | yes (RUN_C list: 4 entries with reference "shipped") |
| 7 | Examples, "Lanes in every figure below: …, X, CoactDetect · proposal (the runner-up, the next row meeting the rule)" (all three streams) | The parenthetical comes right after CoactDetect · proposal, so it reads as naming the reference as the runner-up. The rule itself excludes the reference and † rows. briefing.json shows the runner-up is actually line_part, line or chorus_norm_part. On slow, the runner-up (row 4) passes over row 2, count (sliding) starting point, and gives no reason; that row presumably did not run on the real recordings. | Low–Med | Put "(runner-up)" after the runner-up's name and "(reference)" after CoactDetect. For slow, list rows passed over for the runner-up as well. | yes (briefing.json `runner`) |
| 8 | Example tables "Calls on baseline windows by kind and group"; generator `read_calls()` | The counting basis of every example count and figure is not stated. The generator uses the `own_floor` variant for four coded detectors and `unfloored` for the rest. In the tables, the leader (a learned model, unfloored) and CoactDetect (own_floor) are counted on different bases. The viewer box says "one lane per detector and variant" but never says which variant the counts use. 065/README says "No floor removes a call", which a reader will take as the basis. | Medium | State the variant rule beside the first table, and note that it differs from "every call drawn". | yes (generator + briefing.json `variant` fields) |
| 9 | Table 4 row 13, binned SCE proposal (combined): "Merge gap: none, a value that switches it off" | 065/README says combined SCE "is recorded as unbracketed with no axis named, and I have not looked into why". The page names an axis where the companion says none is recorded. | Low–Med | Check candidates.json. If the page's reason is inferred, say so. If the data name it, note that the README missed it. | no (candidates.json not opened) |
| 10 | Terms "proposal … A detector whose search proposed nothing has no proposal row"; fast has no SPIKE-synch proposal | The two companions contradict each other, and the page picks one side silently. 064/README reports that the fast SPIKE-synch search moved tau_max from 0.25 to 0.5 s ("rescued", bracketed). 065/README lists SPIKE-synch fast among the searches that "proposed nothing". The page follows 065 and the scorer. | Low | Add one line: the rescue in 064's search was not taken as a proposal by the scorer. | yes (both READMEs) |
| 11 | "starting point (untuned)" (Terms, Tables 2–4) vs 064/count "count (binned) shipped" / "count (sliding) shipped" | The page renames the count rows' "shipped" label and does not say so. Anyone cross-reading 064/count will not find "starting point". | Low | Add to the Terms entry: "064/count calls it 'shipped'". | yes |
| 12 | Terms "floor" | The word "floor" is already taken in the glossary with different meanings. GLOSSARY has "floor, provisional floor *f*" (shortest within-ROI interval), "participant floor" (the recruitment level below which a detector stops finding events), and "K, the coactivity floor". The page defines "floor" as ADR-0008's per-window participation floor, which is none of those. | Medium | Call it "participation floor (ADR-0008)" on the page, and add or reconcile the glossary entry in the same change. | yes |
| 13 | Terms: decoy, new/old bench, simulation seed, training run, pick, no pick, proposal, starting point, search limit, combined stream, participants | None of these are in docs/GLOSSARY.md. The glossary's word for a planted look-alike is "distractor"; the page and ADR-0006 say "decoy", so one concept has two names. The glossary's merge-gap entry still describes the bench as "at least 120 s apart", which is only the old bench now. The glossary also has "training seed" and "refit", where the page says "training run". | Medium | Add the new terms to the glossary in the same change. Record decoy = distractor, and update the "120 s apart" wording to say "old bench". | yes |
| 14 | How-to-read, "The order is a reading of intervals, not a ranking" vs Examples, "the leader is the highest row in Figure 1…" | The examples section ranks by the order the page just said is not a ranking. "Figure 1" should also name the panel (1a, 1b or 1c). | Low | Say "the first row, in Figure 1a/b/c's order, that…", and acknowledge that the order is used as a tiebreak. | yes |
| 15 | Figures 6 and 8, "one of 3 calls of its kind… A one-off: read it as one call, not a pattern" | "A one-off" is attached to kinds with 3 calls. In Figure 4, where there is literally 1 call, the wording is right. | Low | Only say "one-off" when there is exactly 1 call; otherwise say "one of only 3 calls". | yes |
| 16 | Table 3 rows 3, 12, 14, 19 and Table 4 rows 14, 21 | Generator grammar: "Over budget on the both benches". Also "Synchronous-frame run 1 frames". | Low | "on both benches"; "1 frame". | yes |
| 17 | SVG `aria-label` "Figure 1, the fast/slow/combined stream" vs captions "Figure 1a/1b/1c" | The accessible label and the caption give different figure numbers. | Low | aria-label "Figure 1a, the fast stream", and so on. | yes |
| 18 | Tables 3–4 marks "C_min 0", "bin dt …" | Symbols are used without being defined. CLAUDE.md requires every symbol to be defined before use. | Low | Gloss them in the mark or in Terms. | yes |
| 19 | `briefing.json` line 2 (`night`) and `extra_files` | These fields carry personal absolute paths, while the page uses relative paths. The file lives in the darkroom, not the repo, so this is a portability and consistency point more than a leak. | Low (boundary: privacy belongs to another role) | Write the paths relative to the night folder. | yes |

## Note to the caller

The brief says "Figures 2–10", but the page runs Figures 2–9. The slow "only the leader" figure is left out, and the page explains why (no call of that kind lies 10 s or more inside a baseline window). The numbering is contiguous, so this is not a defect in the page. Only the brief's description is off.

**Relevant paths:**
- `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`
- `<darkroom>/bugarach/2026-09-26-full-panel/briefing/briefing.json`
- `<worktree briefing-page>/tools/make_briefing.py` (lines 406–449, 471–476)
- `<darkroom>/bugarach/2026-09-26-full-panel/065/README.md`
- `<darkroom>/bugarach/2026-09-26-full-panel/065/RUN_C.md`
- `<darkroom>/bugarach/2026-09-26-full-panel/064/README.md`
- `<darkroom>/bugarach/2026-09-26-full-panel/064/count/README.md`
- `docs/GLOSSARY.md`
