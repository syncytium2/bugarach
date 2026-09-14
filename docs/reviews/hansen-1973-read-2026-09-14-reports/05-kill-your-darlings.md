GRANT 5 MISMATCH — single-pass self-review by the main thread, which holds more tools than this role's grant (Read, Grep, Glob); only reading and the checks named below were used

Construction list: role 5 in `docs/doc_review_process.md`. I searched the added lines by eye and with Grep for the banned words (delve, leverage, robust, seamless, crucial, landscape, tapestry), "not just … but", "it's worth noting", and "In today's". **0 hits.** The one em-dash in the changed text sits inside the conference title (*Radar — present and future*); it is not a pivot.

| # | location | issue | severity | fix | verifiable |
|---|---|---|---|---|---|
| 1 | §4.1, "A block diagram … follows (Fig. 6), and a computed example … (Fig. 5)" | The order is wrong. The paper discusses Fig. 5 before it introduces the Fig. 6 technique, and "follows" says otherwise. | minor | Present Fig. 6 and Fig. 5 as a list without "follows" | yes |
| 2 | §4.1, "That paper was unobtainable online." | Vague and too absolute; roles 1 and 4 flag this too. | minor | "This project could not read it online." | yes |
| 3 | §4.1, "earlier work that neither of them cites" | Asserts something about an unread memo. | minor (overlaps roles 1, 2, 4) | "or earlier work" | yes |
| 4 | §4.1 length | About 470 words, roughly the length of the passage it replaces. The added "What the 1973 paper says" block carries the new evidence and earns its place. | no finding | — | yes |
