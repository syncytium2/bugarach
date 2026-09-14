GRANT 5 ok — Read, Grep, Glob

**Scope.** I read the diff at `...\scratchpad\go_diff_r3.patch` plus the surrounding text in the worktree's `docs/detector_history.md` (lines 197–219, 440–560, 982–1014). I also read `docs/writing_conventions.md` and the role-5 list in `docs/doc_review_process.md`, lines 567–574. I opened nothing under `docs/reviews/`, `docs/todo/` or `docs/lit_needed.md`.

## 1. Construction search: hand-run Grep, not `murderboard_prose.sh`

**List used:** role 5 in `docs/doc_review_process.md`, lines 567–574, applied only to the added (`+`) lines of the diff.

| diff line | construction | kind |
|---|---|---|
| — | not just / it's not about / worth noting / delve / leverage / robust / seamless / crucial / landscape / tapestry / In today's | **no matches** (case-insensitive) |
| — | but / however / instead / rather (checked as possible "not X, but Y" pivots) | **no matches** |
| 61 (GLOSSARY) | `None of it is a problem — this project's own priority is closed … the reason to care is the engineering the radar literature is offering` | **em-dash pivot into an uplifting close. Hit.** The line was reworded in this diff. |
| 77, 90, 125–126, 144 | em-dashes | parenthetical, a list, or a title (*Radar — present and future*). Not pivots. |
| §4.1 "What we do not know" | three-item list | three separate questions, not rhythm. Not a hit, but see finding 9 on overlap. |

## 2. Counts and the passage test

These are hand counts, so allow ±3 words.

| block | words | sentences | payload (the one sentence) | where it sits | what the other words buy |
|---|---|---|---|---|---|
| A. `detector_history` revision ⚠ (lines 207–209) | 25 | 2 | The Hansen 1973 credit is withdrawn; the audit found the mechanism, not the origin. | first | Nothing extra. Right size. |
| B. §4 table cell, LoCo `maxlt` | ~21 | fragment | origin not established | first | The 1980 citation, needed. The `held?` column now reads ambiguously (finding 11). |
| C. Paragraph after the table (473–479) | ~82 | 4 | The 1973 Hansen paper is not among the papers read. | **sentence 3 of 4** | S1 is needed. S2 (who supplied what, on which date, "closing item 2 of §7") is a lookup key. S4 is a needed walk-back of "matched mechanically". |
| D. §4.1 total | **~644** | ~28 | Nobody here has read the 1973 paper; the sources we hold disagree about who proposed greatest-of. | top, then repeated | See rows D1–D8. |
| D1. Opening paragraph | ~113 | 5 | S1 | first | S2 is a 65-word sentence: name variants, IEE vs IEEE, conference dates. It works as a search aid, but it is one sentence doing a bibliography's job. |
| D2. "The search" | ~98 | 6 | No library request for the volume has been made. | **last** | The ISBN mismatch has no consequence stated. Tool names and a HathiTrust record ID are thoroughness. |
| D3. Hansen & Sawyers bullet | ~113 | 4 | They cite the 1973 paper for a loss rule on greatest-of, and a 1972 memo as the exact analysis behind their loss curves. | S1 + S3 | S2 ("By their account, then…") restates S1. S4 (acknowledgment) has no consequence stated. |
| D4. Patent bullet | ~79 | 3 | The patent's account of the 1973 processor averages both sides and never mentions greatest-of. | **last two** | The Goldstein aside. "Paginates 1–8", said again in D6. |
| D5. Rohling bullet | ~71 | 3 | Rohling credits Moore & Lawrence (1980) and does not cite the 1973 paper. | S1 + S2 | S3 is inference. |
| D6. Gandhi & Kassam bullet | ~87 | 2 | G&K credit the 1973 paper with proposing greatest-of. | first | S2 (pages, IEEE venue) is useful evidence, but the reader has to link it back to D1 alone. |
| D7. "What we do not know" | ~75 | 4 | the three unknowns | — | Bullets 1–2 largely restate D1 S3–S4. |
| E. §7 item 2 ⚠ (1011–1014) | ~38 new (+5 kept) | 2 (+1) | That attribution is withdrawn as unverified (§4.1). | **last** | S1 explains how the check missed it, but "could not tell the two apart" is unclear (finding 7). |
| F. Sources entry | ~46 | 2 | Quotations come from shelf PDFs, except the patent's. | last | Fine in size. Consistency problem (finding 3). |
| G. GLOSSARY CFAR paragraph | ~130 | 6 | The words below name the mechanisms; where greatest-of began is not established. | S4 + **S6** | S2 is the paragraph's own revision history, which a glossary reader does not need. S5 is the pivot hit. |
| H. README bullet | ~92 | 3 | `maxlt` is greatest-of selection; its origin is not established (§4.1). | S1 + S3 | S2 (1980 loss citation) is needed. "This README no longer cites…" is change history. |
| I. `cfar_scope.html` lede, row, JS cite | ~16 / 7 / 5 | 1 / — / — | §4.1 records that the origin is not established. | — | Right size. |
| J. Proposal footer correction | 25 | 2 | The Hansen 1973 credit is withdrawn. | first | Right size. |

**Against the brief ("leave it at that", brevity):** one citation became about 640 words. The payload fits in about 250. Every cut in finding 1 removes a word that serves the author's thoroughness, not a sceptic.

## 3. Findings

Each finding gives location · issue · severity · suggested fix · verifiable against a source.

1. **§4.1 as a whole** · About 644 words and 28 sentences to deliver "not read; sources disagree; here is who says what". That contradicts "brevity is part of the brief". · **major** · Cut:
   - the name-variant parenthetical in D1 S2;
   - the ISBN-mismatch sentence and the HathiTrust record ID in D2;
   - "By their account, then…" in D3;
   - the acknowledgment sentence in D3, unless its consequence is stated;
   - the Goldstein aside and "paginates the paper 1–8" in D4, keeping it only in D6;
   - Rohling S3 in D5;
   - "What we do not know" bullets 1–2, which D1 already says.
   
   Put the bibliographic detail for the 1973 paper in one citation line. Target is under 300 words. · no (judgement)

2. **§4.1, Hansen & Sawyers bullet, S3** · "as they describe it, that memo is the earliest dated treatment of greatest-of in the sources we hold". This is the one sentence a reader will lift as the new origin, which is the thing the brief said not to write. "As they describe it" also attaches to the wrong claim: H&S describe the memo, they do not call it earliest. The link from the memo's "'Split' mean level" title to greatest-of is never stated. · **major** · Say what the source says and stop: "Their introduction also cites an internal Hughes Aircraft memo by J.H. Sawyers, dated 15 February 1972, as the exact analysis behind their loss curves." Cut the "earliest dated treatment" clause. · yes (the H&S 1980 PDF on the shelf)

3. **Paragraph after the table, S4, vs. Sources entry** · The paragraph says radar quotations are checked against "those PDFs" with no exception. The Sources entry says every quotation is from a shelf PDF "except those from US patent 4,318,101". §4.1 also quotes the Proc. IEE notice ("GREGERS HANSEN, V."), and neither sentence says where that comes from. Two sentences in the same diff make different absolute claims about the same quotations. · **major** · Name the exceptions once (the patent text, and the Proc. IEE notice if it is not on the shelf) in the Sources entry, and have the table paragraph say "from those PDFs, except as noted in Sources". · partly (shelf README; I could not open the darkroom)

4. **GLOSSARY CFAR paragraph, S1–S2 vs S6** · The paragraph's story is still "the attributions were unverified, and that stopped being true twice". Its last sentence now says one origin is not established, so it argues one way and ends the other. S2 is also the paragraph's own revision history, which a glossary reader does not need. · **major** · Replace S1–S2 with one sentence of present fact: "`rate_detect` is cell-averaging CFAR (Finn & Johnson 1968), `maxlt` uses greatest-of selection, and the percentile-of-pool is kin to OS-CFAR (Rohling 1983)." Keep S4 and S6. · no

5. **GLOSSARY, diff line 61, em-dash pivot** · "None of it is a problem — … the reason to care is the engineering the radar literature is offering." This is a banned construction and the line was edited in this diff. "This project's own priority is closed" also uses *priority* (of discovery) as unexplained jargon for an outside reader. · minor · Either state why it stays, or write plainly: "Who was first does not matter here (Tony's ruling, 2026-08-24); the radar engineering does, and the attribution note sets it out." Note that "sets out" also appears twice in two sentences. · no

6. **Paragraph after the table, sentence order and S2** · The payload for this change (the 1973 paper is not on the shelf) sits third of four. S2's "on 2026-08-22, closing item 2 of §7" is a date plus an index, both lookup keys under writing_conventions. It also names that item "item 2 of §7" while the Sources entry, in the same diff, still calls it "§7.2". · minor · Promote S3 to follow S1. Reduce S2 to "Tony supplied the two IEEE papers." Pick one name for the §7 item in both places, preferably its short name, "the CFAR primaries check". · no

7. **§7 item 2 ⚠, "and could not tell the two apart"** · The subject is "this check", so it reads as if someone could not tell the two papers apart. The intended meaning seems to be that the check's pass did not separate "read the 1980 analysis" from "verified the 1973 credit". The ⚠ also follows "All four primaries are read", which now leads a reader to count the 1973 paper among them. · minor · "⚠ 2026-09-14: the check read the 1980 loss analysis and recorded that as verifying the 1973 credit. That credit is withdrawn as unverified (§4.1)." · no

8. **§4.1 "The search" paragraph** · The ISBN mismatch has no stated consequence: does it suggest the catalogue record is a different volume? "Could not be queried with this project's automated tools" and "has not been searched from here" name neither the tool nor the place, against the writing_conventions rule that a finding about an environment names the environment. The dates in the bold lead are lookup keys. · minor · Cut the ISBN sentence, or give its consequence in one clause. Say why the queries failed (paywall, bot block). Replace "from here" with "by this project". Use "A four-day search" or drop the dates. · no

9. **§4.1, "What we do not know" bullets 1–2 vs opening paragraph S3–S4** · Both say the same two things: the paper has not been read, and the sources disagree about who proposed it. It is a recap, and it hurts more under a brevity brief. · minor · Keep the list, since the brief asks for "known / not known", and cut D1 S3–S4, leaving S1 and S5. Or keep D1 and cut bullets 1–2. · no

10. **§4.1, last bullet, "None of them is on the shelf"** · "Them" could mean all of Hansen's early papers or only the two cited. The Zottl citation has no pages while the Ward citation does. · minor · "Neither is on the shelf." Give pages for Zottl, or drop them from Ward. · no

11. **§4 table, LoCo `maxlt` row** · The `attribution` cell now holds a non-attribution plus the 1980 citation, and `held?` = **read in full** sits next to "origin not established", so a skimming reader can apply "read in full" to the origin. "Loss analysis of the cell-averaging form" means CAGO, but that name was taken out of this row. **CAGO** now first appears undefined, inside the Rohling quotation in §4.1. · minor · Cell: "origin not established (§4.1). Detection-loss analysis: Hansen & Sawyers, …". Define CAGO once, either as "(cell-averaging greatest-of, CAGO)" in the row or before the Rohling quotation. · yes (the grep confirms CAGO's first use is at line 544)

12. **README bullet, S3** · "and this README no longer cites a 1973 Hansen conference paper as its origin" is change history inside a citation list. The link to §4.1 already covers it. "…over plain cell-averaging, in radar, is computed in…" is clumsy with "in radar" set off by commas. · minor · "Where greatest-of began is not established ([§4.1](…))." For S2: "In radar, the added detection loss of greatest-of over plain cell-averaging is computed in …". The author may keep the no-longer-cites clause as a public correction, but should say so. · no

13. **README S1, "larger of two local thresholds"** · I checked this against the code and it matches the `loco.py` docstring (lines 9–10: "MAX of the trailing and leading half-context thresholds"). · no finding · — · yes

14. **`cfar_scope.html`, table row vs JS `VARIANTS`** · The same page says "loss: Hansen & Sawyers 1980" in the table and "loss analysis: Hansen & Sawyers 1980" in the JS. A bare "loss" does not tell an outside reader it means detection loss. · minor · Use "detection-loss analysis: Hansen & Sawyers 1980" in both places. · yes (same file)

15. **Revision ⚠ in `detector_history` (A), "For greatest-of the audit identified…"** · Without a comma it garden-paths as "greatest-of the audit". The ⚠ also does not say whether the enclosing sentence's conclusion ("has … become the attribution") still stands for greatest-of. · minor · "For greatest-of, the audit identified the mechanism, not its origin; the mechanism claim stands. See §4.1, Where greatest-of began." · no

16. **Wording repeated across surfaces** · "withdrawn as unverified" appears in the revision block, §7, and the proposal. "Not established … sets out what is known and what is not" appears in the README, the GLOSSARY and §4.1. Each file is a separate entry point, so the repetition across files is fine. Within `detector_history.md` the withdrawal is stated four times (revision block, table paragraph, §4.1, §7). · minor · Keep the revision-block and §7 notes, since each corrects its own place. Cut "used to cite … (§4.1)" from the table paragraph if finding 6 is not taken. · no

**No findings:**
- **INDEX.md row:** only keywords were added, and they are search terms.
- **Proposal footer correction:** 25 words; greatest-of is already named on that page at line 255; the date format matches the footer.
- **GLOSSARY bullet "(GO)/(OS)":** the abbreviations are defined. OS-CFAR is used in the paragraph above before this bullet defines it, but that was already true before this diff.
- **README ° legend:** the removed clause leaves a correct, shorter sentence.

**Summary:** 16 findings. 4 are major (1–4): §4.1 runs too long for the brief; one sentence in §4.1 reads as a new origin claim; the diff's own quotation-sourcing claims disagree with each other; and the GLOSSARY paragraph argues against its own last sentence. There is 1 construction hit (finding 5).
