GRANT 3 ok — Read, Grep, Glob (single-pass self-review by the main thread, not a separate agent; the main thread holds more tools than this grant, and used only reading here)

Checked the round-1 draft of `detector_history.md` (the §4 table row, the paragraph after it, §4.1, the 2026-08-24 ⚠ and the §7 item 2 ⚠), `GLOSSARY.md`, the proposal footer, `lit_needed.md` and the two todos. Each was compared with the others and with README, `cfar_scope.html` and INDEX.

| # | location | issue | severity | fix | verifiable |
|---|---|---|---|---|---|
| 1 | §4 paragraph after the table | Says "Four of the table's papers are held and read in full", but the edited row now marks Hansen 1973 read too, so there are five. | major | Five, and name them | yes |
| 2 | §4.1 vs README bullet and `cfar_scope.html` | README says "Where greatest-of began is not established" and `cfar_scope` says "origin unknown". Both are still consistent with §4.1, which keeps the origin not established. | no finding | — | yes |
| 3 | §4.1 title spelling | §4.1 quotes the paper's own title page (no hyphens). `lit_needed` quotes the *Proc. IEE* notice (hyphenated). The two spellings come from different sources and both are quoted correctly. | no finding (noted) | — | yes |
| 4 | Revision note, §7, GLOSSARY, footer | All say "without citing or claiming it" in the same form. Consistent across files, but role 4 finds the phrasing reads as causal (not a consistency matter). | no finding here | — | yes |
| 5 | `docs/learned/detector_history.html` | Not yet rebuilt from the edited markdown. | major (overlaps role 10) | rebuild | yes |
