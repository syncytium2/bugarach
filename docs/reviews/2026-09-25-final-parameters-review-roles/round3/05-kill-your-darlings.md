GRANT 5 ok — Read, Grep, Glob

**Run note (about the run, not the artifact).** The checklist tells me to run `murderboard_prose.sh <artifact>` and paste what it prints. I could not. The script is not in the repo: Glob finds only `tools/murderboard_{agents.py,freshness.sh,revendor.py,roster.sh}`. I also hold no Bash. So there is no per-block word or sentence count, and I have not made one up. I did the banned-construction search by hand with Grep instead; the results are below. Count that step as **not run** in the ledger, not as clean.

**Banned-construction search (the house list in doc_review_process.md role 5).**
- **Words searched:** delve, leverage, robust, seamless, crucial, landscape, tapestry, "worth noting", "not just", "it's not about", "In today's". **0 hits.**
- **House-rule words:** fire/fires/fired/firing, modality, singular "data". **0 hits.** "Data" appears only in the heading "Real data".
- **Em-dash pivots:** every " — " is an empty table cell. None is in prose.
- **Three-item lists built for rhythm:** none. "Three things follow" (line 8) introduces three real items.

## Findings
Columns: location · issue · severity · fix · could I verify it against a source.

1. **L301 and L306–307, with Table 1 L363** · "Every LoCo search lowered its `threshold_pctile` to the 1st percentile" reads as if the chosen value went down. Table 1 shows fast LoCo's value going **up**, 99.5 → 99.99. L306 then says 99.99 is the top of the grid and was never extended, yet the table marks it "cap" rather than "edge". A reader cannot tell what "cap" means for this setting. · **major** · Write "extended its `threshold_pctile` grid downward to the 1st percentile". Then say plainly why a proposal sitting at the unextended top of the grid is labelled cap and not edge, or correct the label. · partly (Table 1 only)

2. **L66–69** · The heading says the gain is "mostly" fewer calls on decoys, and L69 says flatly that it "comes from rejecting decoys". L67–68 say F1 without decoy calls is near 1 "for the shipped points too". Combined rate+context's shipped point is 0.855 without decoys (Table 1 L381), which is not near 1, so part of that gain is not decoys. · **major** · Pick one strength of claim and name the exception, e.g. "except combined rate+context, whose F1 without decoys also rises, 0.855 → 0.978". · yes (Table 1)

3. **L388–389, L341, Table 2 cells** · Four terms name what may be only two states: "not checked" (the caption, which no cell uses), "not recorded", "not run" and "not measured" (L341). · **major** · Use one term per state, define each in the caption, and drop "not checked" if no cell uses it.

4. **L465** · "each recording's own floor minus its baseline floor". L451–452 defines the comparison per **treatment window**: the window's own floor against its recording's baseline floor. · **major** · Write "each treatment window's own floor minus its recording's baseline floor". Units are also missing after +17, +1 and +20; write "+17 ROIs" and so on. · yes (L451–452)

5. **Real data, L448–474** · The payload is at the end. L471–472 says the floor rises under senktide mainly in the gonadectomized groups, so it can absorb the co-activity the project studies. It arrives after run provenance (L454–459) and combination counts (L460–464). · **major** (passage test) · Promote L471–472 to open the section, and move "Where it ran" to *What ran*, which already has a row for it (L532).

6. **L285–286** · "The search did extend it to 240 s, which the validity rule rejected, so the bracketing record does not flag it." "Validity rule" is never defined, and the "so" does not follow: the reader cannot tell whether the context counts as bracketed. · minor · Write something like "counts it as bracketed although it sits at the bench's 120 s maximum", and define the validity rule or point to where it is defined.

7. **L70** · "calls on real planted events" collides with the "Real data" section, and every planted event is simulated. · minor · Write "calls on coordinated planted events (not decoys)".

8. **L72** · "The proposals call far fewer of them." The table right below has rows of 6 → 5 and 55 → 54. · minor · Write "fewer, and far fewer at the lowest level".

9. **L82–83** · The key to the table (calls matched to under-floor events, shipped → proposal, fresh seeds) comes after the table. The denominators 85 and 55 are not explained. · minor · Put the key before the table and say the denominators are the events under the floor (Table 3).

10. **L96–97** · "those two" could mean detectors or proposals; there are three affected proposals across two detectors. "is really tested by it": "really" adds nothing and "it" is ambiguous. · minor · Write "binned SCE and SPIKE-synch" and "tested by the elevated-rate recording".

11. **L98** · "goes over a limit on the background that is not checked" is hard to parse. · minor · Write "exceeds the outside-the-stretch limit on the busy background, where that limit is not checked".

12. **L166** · "the busy floor blocks most of them". The floor does not block decoys; it blocks calls for detectors whose minimum it sets. · minor · Write "blocks calls on most of them".

13. **L170–171** · "setting events aside can deepen it" does not say which events or why. · minor · Name them ("treating under-floor events as don't care") and name the mechanism.

14. **L181–183** · Two chained "so"s, and "it" means the search. · minor · Write "Their shipped points fail, as did every neighboring setting the search tried, leaving it no allowed move."

15. **L194** · "an open (busy) marker above its bar": it is unclear whether "bar" means a limit line or a bar mark. · minor · Name the mark.

16. **L214–215 and L222–223** · L215 repeats L214 (and L10–11). L222–223 repeats L91–92. · minor · Cut L215. Replace L222–223 with a cross-reference.

17. **L216–217** · "Fast busy loses 57%" does not say 57% of what (205 of 360 events), and combined busy (175 of 360, 49%) is left out. L217 has bare counts ("25 of 40"). · minor · Write "57% of its planted events (205 of 360)", add combined, and give every count a unit.

18. **L33** · "4 → 9 adoptable" has no unit. · minor · Write "4 → 9 adoptable proposals".

19. **L31** · The row mixes an imperative with a question. · minor · Write "Re-measure those budgets under the new bench? Should decoys under the floor…".

20. **Jargon used before or without a definition** · The at-a-glance table (L29–36) uses "strict rule", "decoys", "bracketed" and "extension cap" before Decision 1 or the Definitions define them. Never defined anywhere: "bench", "shipped point", "proposal", "guard" (used in Table 1 and L246; only defined inline at L314–315), "participation minimum" / "floor-set minimum", the detector names (CoactDetect, LoCo, locust, rate+context, SPIKE-synch), and TTX and K⁺ (L451). "Coded detector" (L4) is ambiguous. · minor · Add these to the Definitions, and consider pointing to them in the first sentence.

21. **L488–493** · The "don't care" rule sits inside the Event floor (ADR-0008) definition, so it reads as ADR-0008's. It is ADR-0009's (decision 2), as L71 correctly says. · minor · Attribute don't care to ADR-0009 in the definition. · yes (docs/adr/0009…md:58)

22. **L7 against L488** · The floor is defined per window (ADR-0008 title, Definitions), but L7 says each simulated recording gets one. · minor · Say that on the bench a recording is one window, or use "window" throughout.

23. **L57–58 and L108–109** · "Before deciding, read these:" is a preview. L108–109 restates the at-a-glance column. · minor · Cut the first. Cut the second or shrink it to a pointer.

24. **L324** · "the same PR as this page" is an index, not a name. · minor · Give the PR number and what it fixed.

25. **L463–464** · "calls under one floor become no calls under the other" is awkward. · minor · Write "one floor yields calls and the other yields none".

26. **L505 and L509** · "as little as 6 s apart" should be "as close as 6 s". "*rounds* moves" has a number mismatch. · minor · Fix both.

27. **Table 3 caption L434–435** · The caption says "participants" but the cells say "ROIs". · minor · Use one term.

28. **Generated tables (Table 1 L383 and others; Table 2 L394–397)** · The generator's output has these problems:
   - "1 frames"
   - "99.5 percentile" where it should say "99.5th percentile"
   - `0.0001 → 1.4e-09` in the table against `1e-4 → 1.4e-9` in the prose
   - `isi_adaptive` in the table against "adaptive" in the prose
   - two parentheticals in a row: "(precision swing not recorded) (the sliding starting point)"
   · minor · Fix these in `tools/make_final_parameters_report.py`, not by hand.

29. **L524–526** · The labels "PR A" / "PR B" and "`pilot-chorus-prb-only`" point to things without naming them. In L533 the code column holds a tool name, not a commit. · minor · Name the PRs by content, and keep that column to one kind of entry.

## Passage test (main blocks)
- **Opening (L3–23):** the payload ("nothing adopted; the floor changed what counts") is up front. It holds.
- **Decision 1 bullets (L60–106):** each bullet opens with its point in bold. The problem is the decoy claim (finding 2).
- **Decision 3 (L151–203):** the payload is in the header. It holds.
- **Decision 4 (L204–235):** about a third of the bullets repeat earlier text (finding 16).
- **Decisions 5–9:** tight, apart from the LoCo contradiction (finding 1).
- **Real data:** the payload is last (finding 5).

Artifact: `<worktree>/docs/learned/runs/2026-09-25-final-parameters/README.md` (worktree `floor-and-grids`).
