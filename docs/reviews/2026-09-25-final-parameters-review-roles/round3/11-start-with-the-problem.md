GRANT 11 ok — Read, Grep, Glob

Role 11, argument order ("Start With the Problem"), round 3, blind pass.
Artifact: <worktree>/docs/learned/runs/2026-09-25-final-parameters/README.md (547 lines). I read the whole file and nothing else. I did not look at the earlier review reports and did not edit anything.

## The spine (one claim per section, in document order)

1. **Title and lines 3–4:** nothing is adopted yet. The night re-searched every detector and retrained chorus under the ADR-0008 event floor.
2. **What the floor did (lines 6–15):** the floor makes weak planted events "don't care". That changes the bench (D4), makes four shipped points fail a budget (D3), and makes some thresholds stop mattering (D7, D8).
3. **Rules links (lines 17–23):** the runbook, ADR-0008 and ADR-0009 govern the night. Definitions are at the end.
4. **Decisions at a glance (lines 25–37):** nine asks, each marked for whether it can change today's adoption set.
5. **D1 (lines 39–122):** four proposals pass the strict rule and the paired fresh-seed check. Seven caveats weaken that result: SPIKE-synch changes identity, the gain comes from decoys, under-floor calls are lost, the held-out seeds also chose, some budget checks cannot fail, busy goes over a limit, other gaps. Line 108 says D2–D6 can change this set. Figure 1 comes last.
6. **D2:** one version on another stream's bench beats that stream's own version once, beyond noise. One such case bears on D1 (combined binned SCE).
7. **D3:** four shipped points fail a budget, two because of the floor or decoys and one because of the new bench layout. Figure 3 is here.
8. **D4:** much of the planted bench is now under the floor, so the weakest level no longer counts toward recall. The planted events raise their own null. Figure 4 is here.
9. **D5:** five proposals are held back only by a hard limit. If a limit counts as a bracket, nine are adoptable.
10. **D6:** slow binned SCE sits at the close-events allowance, within noise.
11. **D7–D9:** search rules for next time. They do not change today's set, and the section says so up front.
12. **Full tables:** how to read them, the methods caveats, and Tables 1–3.
13. **Real data:** on 66 recordings the per-window floor rises by about 17–20 ROIs under senktide in OVX and ORX. It can absorb the treatment-window co-activity the project studies.
14. **Definitions.**
15. **What ran.**

**Arc used.** For a decision memo I adapted the default arc: problem (the floor changed the bench) → what it costs (shipped points fail, the bench loses its weak events) → the method applied (the search) → what the method gets wrong (brackets, held-out bias, checks that cannot fail) → the fix (the proposals) → the evidence → the residual risk. The page instead runs bottom line first (D1 first), then the rulings ordered by whether they change the set, then the machinery at the end. Bottom line first is a defensible deviation, but the page states it only partly (see finding 1).

**Cold open.** The reader sees "Nothing here is adopted" first, then the problem ("What the floor did") within the first 10 lines, then the nine asks by line 25. The asks come before the machinery. That part works: the problem arrives early and the decisions come before the tables and "What ran". The defects are in where things sit relative to D1.

## Findings

| # | location | issue | severity | fix | verified against source |
|---|---|---|---|---|---|
| 1 | Line 39 (D1) against line 108 and the glance table's column 3 | D1 asks Tony to adopt a set that the page itself says D2, D3, D4, D5 and D6 can change. Line 108 ("What could change this set: Decisions 2…6") is the key to reading D1, but it comes at the end of D1, after the caveats and before Figure 1. So Tony reaches D1's "Decide" before the rulings that define what "adoptable" and "F1" mean. The intro orders the problem D4, then D3 (lines 10–13), but the body runs D2, D3, D4. That is an unstated deviation from both the intro's order and the logical dependency. | major | Keep D1 first as the bottom line, but move the line-108 sentence to the top of D1 and say plainly: "take this decision last; D2–D6 set its terms". Or keep D1's evidence where it is and move its "Decide" block to after D6. Reorder the rulings to D4 (what F1 measures) → D3 (what the budgets mean) → D5 → D6 → D2, so the most foundational ruling comes first and the order matches the intro's list. | yes (lines 10–14, 25–37, 108, 121) |
| 2 | Lines 91–100 (D1 caveats) | D1 relies on things introduced later. It cites **Figure 4** (introduced at line 225, in D4) and **Figure 3** (line 187, in D3) before Figure 1 appears at line 111. It also uses "the elevated-rate recording", "the stretch" and "calls outside the stretch", which are first explained in the Figure 3 caption in D3 (lines 189–195). Tony cannot judge "some budget checks cannot fail" or "over a limit on busy" when he reads them. | major | Put a two-line gloss of the elevated-rate recording at its first use in D1 (a 45-minute recording, nothing planted, 5 minutes at the 99th-percentile rate). Or move these two caveats into D3, where Figure 3 lives, and leave a one-line pointer in D1. | yes |
| 3 | Line 22, "Definitions, at the end" (lines 476–518) | The terms D1 needs first are defined only at the end, after about 450 lines. That covers "budget", "precision swing", "close-events test" (used at line 104 and in D3 and D6), "don't care" (line 71, which points to ADR-0009 only), "bracketed" and "extension cap" (glossed at line 44, but "cap/edge/limit" is not glossed until line 513, although D7 and D8 use it), and the seed sets. Keeping the glossary last is fine, but the terms the decisions depend on reach Tony only after he needs them. | major | Add a short "Terms you need for the decisions" block after the glance table: floor and don't care, decoy, budget (the four kinds), bracketed with cap/edge/limit, and the three seed sets. Leave the full Definitions at the end. | yes |
| 4 | "Real data" section (lines 448–474), after the full tables | The finding that could most unsettle the premise of all nine decisions comes last, after three appendix tables, and it maps to none of the nine asks. The per-window floor rises by about 17–20 ROIs under senktide in OVX and ORX, and "can absorb the treatment-window co-activity the project studies". It bears on ADR-0008 decision 4, which is still open. As placed, it is residual risk with no job in the decision spine, and it is sandwiched between appendices. | major | Move it before "The full tables" as a "Residual risk: what the floor does on real data" section. In the opening, name it in one line, either as an open item for Tony beyond the nine or as explicitly not asked today. | yes (lines 465–474) |
| 5 | Lines 49–54 against lines 84–90 | D1's table shows a "held-out gain" column before the reader learns, 30 lines later, that the held-out seeds also chose and that this gain is biased upward. Line 46 does flag the fresh-seed column as the independent check, which helps, but the biased column still arrives first with nothing to mark it. | minor | Add "(biased up: these seeds also chose, see below)" to the column header. Or move the "held-out seeds also chose" bullet to directly under the table. | yes |
| 6 | Figure 1 (lines 111–119), at the end of D1 | Figure 1 is the one overview picture of the night: every detector, shipped against proposal, adoptable or not, chorus included. It sits after seven caveat bullets, as the last item in D1, so the reader gets the text before the picture. As the overview, it could do the cold open's job of showing the problem and the outcome. | minor | Move Figure 1 up, either directly after the glance table or at the head of D1 before its table. | yes |
| 7 | Lines 3–25, the opening | The opening states the status and the problem, but the number of asks ("nine decisions for Tony") first appears at the glance table, after a paragraph of rule links. The rule links (lines 17–23) are background and sit between the problem and the ask. | minor | Say "nine decisions, below" in the first paragraph. Move the runbook and ADR links below the glance table, or into "What ran". | yes |
| 8 | D4 line 206 ("Table 3 gives every count"), D7 line 288 ("Table 2 shows…") | These are forward references into the appendix tables. That is acceptable for full detail, but D7's argument depends on the "sliding starting point" caveat, which is explained only under "How to read them" (lines 335–338). D7 relies on it without explaining it at that point. | minor | Explain the sliding-versus-binned starting point in one clause inside D7, where it first matters. | yes |

## What earns its position (the job each section does)

- The opening, the glance table, D2–D6, D7–D9 as a stated "next time" group, and the tables, Definitions and "What ran" as trailing appendices all have a clear job, and each is in a defensible slot apart from the dependencies above.
- Only "Real data" has no job in the decision spine where it sits (finding 4).

## Summary

- The page opens on the problem and puts the decisions before the machinery.
- Its main ordering defect is that D1, the decision the other rulings condition, is asked first, and the key to reading it is buried at its end (finding 1).
- D1 also leans on figures, terms and a recording that are introduced only later (findings 2 and 3).
- The one finding that challenges the floor itself sits after the appendix tables (finding 4).

No blocking findings; 4 major, 4 minor.
