GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1: claim and data verification of the greatest-of passages

**Summary:** 6 major and 8 minor findings, none blocking. Most of the numbers, dates and quotations check out against the shelf PDFs. The problems are in how the passage describes what the papers say: Rohling 1983's credit is misstated, a "usually credited" consensus claim has no source, and two relevant statements from the 1980 paper are left out. The unchanged sentences right after the table, and the rendered HTML copy, now contradict the change.

**Method:** I extracted every shelf PDF with `pdftotext -layout`, plus a raw extraction of Gandhi & Kassam to get its reference numbering. I recomputed each date gap and ran `tools/verify_quotes.py` on the worktree's `detector_history.md`. Every quotation it missed I checked by hand against the layout text.

## Claim ledger

| # | Quoted claim (location) | Cited source | What the source actually holds | Verdict |
|---|---|---|---|---|
| L1 | Title "Constant-false-alarm-rate processing in search radars", author V. Gregers Hansen (§4) | contents listing PDF | "GREGERS HANSEN,V.: Constant-false-alarm-rate process-/ing in search radars" | match |
| L2 | IEE Conf. Publ. 105, *Radar — present and future*, London, 23–25 October 1973 | listing | "(23rd-25th October 1973, Savoy Place, London, England)" | match |
| L3 | "The volume's contents listing" | listing | The page's own footer reads **Proc. IEE vol. 120, no. 11, November 1973, p. 1391**. It is a sales notice ("437 pp., 68 papers… Price £12") printed in a journal, not the volume's own contents page | mismatch (minor, F8) |
| L4 | "IEEE Xplore does not index this IEE volume" | author profile | The profile lists 19 items, 1965–1982. The 1972 entries are followed directly by 1974, with no 1973 entry. That shows *his paper* is absent. It says nothing about the volume as a whole | partly verifiable (F9) |
| L5 | Searched 2026-09-10 to 2026-09-14, no copy found | `lit_needed.md`, 09-10 todo | The records open on 09-10 and close on 09-14 | match (records only) |
| L6 | 1980 §I quote, "a simple rule for determining the detectability loss…" | 1980 PDF | Genuine. The source uses double quotes around "greatest of". The tool missed it because the sentence crosses a column; confirmed by hand | match |
| L7 | "The same paragraph cites an earlier analysis" | 1980 PDF | [2] first appears in the **second** paragraph of §I, not in the paragraph holding the quote | mismatch (minor, F5) |
| L8 | Memo by J.H. Sawyers, Hughes Aircraft, 15 Feb 1972, quoted as *"'Conventional' and 'Split' mean level threshold detectors"* | 1980 ref [2] | Full title: "Detection losses of the 'Conventional' and 'Split' mean level threshold detectors," internal memo, Hughes Aircraft Co., Feb. 15, 1972 | match, but the title is cut short (F6) |
| L9 | "The 1980 paper derives greatest-of's detection performance from it" | 1980 §II | "The detection performance of this processor was derived as follows [2]"; the graphs "were prepared from [2]" | match |
| L10 | Memo "predates the conference by twenty months" | recomputed | 15 Feb 1972 to 23 Oct 1973 is 20 months and 8 days | match |
| L11 | Memo "was not published" | 1980 | Cited as "Internal memo"; the Conclusions say "previously unpublished results". That only establishes it was unpublished as of 1980 | match within that limit (F7) |
| L12 | Gandhi & Kassam quote, "Hansen [9] has proposed…"; [9] is the 1973 paper | G&K 1988 | Quote is genuine (the tool missed it). I counted the reference list: [6] Moore & Lawrence, [8] Rickard & Dillard, **[9] Hansen 1973**, [10] Hansen & Sawyers, [13] Rohling. [13] matches the in-text "Rohling [13]" | match |
| L13 | Pages 325–332, and G&K is "our only source" for them | G&K refs, 1980 ref [1], listing, Rohling | G&K gives "pp. 325-332". The 1980 citation and the listing give no pages, and Rohling does not cite the paper | match |
| L14 | "Rohling 1983 credits greatest-of to the 1980 paper and to Moore & Lawrence 1980" | Rohling | *"Moore et al. [3] **proposed** a different estimation method. The CAGO CFAR applies the maximum…"* and *"Hansen et al. [2] have **investigated** CAGO CFAR and have found… minor losses"*. Rohling splits the credit: Moore & Lawrence proposed it, Hansen & Sawyers analysed it | mismatch (major, F1) |
| L15 | Rohling "does not cite the 1973 paper" | Rohling refs | Not cited | match |
| L16 | Hansen & Zottl 1971 (Siebert and Dicke-Fix detectors); Hansen & Ward 1972 (cell-averaging LOG/CFAR receiver) | profile, 1980 ref [4] | AES-7(4) 1971; AES-8(5) 1972, pp. 648–652 | match |
| L17 | Neither of those two is on the shelf | `lit/` tree | No such files anywhere under `lit/` | match |
| L18 | "Those are" Hansen's earlier CFAR papers (reads as a complete list) | profile | The profile also has 1970 "nonparametric rank tests… application to radar" and 1971 "Nonparametric Radar Extraction Using a Generalized Sign Test". Both are distribution-free (CFAR-type) detectors | overstated (minor, F10) |
| L19 | "what the 1973 paper contains beyond its author's one-sentence description" | 1980 §I | The 1980 paper says **three** things about [1]: it gives the loss rule; the rule "is based on a simplified analysis and simulation results of limited accuracy"; and its loss "is somewhat larger than predicted from an exact analysis contained in [2]" | mismatch (major, F3) |
| L20 | "The work usually credited" (README and §4) | none | Of the other shelf papers that cite greatest-of work, only G&K credits 1973. Rohling credits Moore & Lawrence as proposers. Weinberg 2017 cites only the 1980 paper, as one of several examples ("[3]-[7]"). The only other "credits" are earlier repo reviews that assert it with no source (`loco_coact_as_cfar_2026-08-25.md` E1; `roles-1-6.md` row 4, "confirmed independently", source not named) | unverifiable (major, F2) |
| L21 | README: Hansen & Sawyers, IEEE T-AES AES-16(1):115–118 | 1980 PDF | Page footers 115–118, "VOL. AES-16, NO. 1 JANUARY 1980" | match |
| L22 | README: a 1972 memo "already analysed the same split detector" | 1980 §I–II | Memo title says "'Split' mean level threshold detectors", and the greatest-of derivation is credited to [2] | match |
| L23 | Table: "1980 **read in full**; 1973 **no copy found**" | shelf | Consistent | match |

## Findings

| # | Location | Issue | Severity | Suggested fix | Checkable against a source? |
|---|---|---|---|---|---|
| F1 | `detector_history.md` §4, Rohling bullet (also `lit_needed.md` table, and the 09-10 todo line 48, which drops Moore) | Rohling 1983 does not credit greatest-of to both papers alike. He says Moore et al. [3] **proposed** it and Hansen et al. [2] **investigated** its loss. On the one question this passage is about, that is a second, different proposer, and the bullet blurs it | major | "Rohling 1983 says Moore & Lawrence (1980) *proposed* CAGO and Hansen & Sawyers (1980) *investigated* its loss; he does not cite the 1973 paper." Consider adding Moore & Lawrence to the "not on the shelf" list | yes |
| F2 | README bullet and §4 first sentence: "The work usually credited" | This is a new claim about what the literature generally does, and nothing backs it. On the shelf, only G&K 1988 credits 1973. The other sources behind "usually" are earlier repo reviews with no source. This partly brings back the origin claim Tony said not to replace | major | Name who credits it: "The work Gandhi & Kassam (1988) credit with proposing greatest-of, and which this repo previously cited as its origin…" | yes (shelf); the wider "usually" is not verifiable |
| F3 | §4, first "What we do not know" bullet: "its author's one-sentence description" | Undercounts what we know. §I of the 1980 paper also says the 1973 rule rested on "a simplified analysis and simulation results of limited accuracy" and overstated the loss compared with [2]. That is known content, and the brief asks for what we know | major | Add both statements to the 1980 bullet and drop "one-sentence" | yes |
| F4 | §4, 1980 and memo bullets | Leaves out the 1980 Acknowledgment: *"The results reported in this paper are derived from independent work performed by the two authors. They are indebted to David Shanks… for informing each of the other's work."* This bears directly on the memo-versus-talk question: the two were independent lines of work, not one building on the other | major | Add a bullet (paraphrase or short quote, since it is a published paper) | yes |
| F5 | §4: "The same paragraph cites an earlier analysis" | [2] is cited in the next paragraph of §I | minor | "The next paragraph" or "the same section" | yes |
| F6 | §4 memo title | Title cut to its second half; the dropped "Detection losses of the" shows the memo was a loss analysis | minor | Quote the full title | yes |
| F7 | §4: "and it was not published" | The source only supports "unpublished as of 1980" | minor | "…which the 1980 paper calls 'previously unpublished results'" | yes |
| F8 | §4: "The volume's contents listing" (same wording in `lit_needed.md` and the todos) | The PDF is a notice in *Proc. IEE* 120(11), Nov 1973, p. 1391, not the volume's own contents page | minor | "a listing of the volume's contributions printed in *Proc. IEE* 120(11), November 1973" | yes |
| F9 | §4: "IEEE Xplore does not index this IEE volume" | The shelf evidence (the profile's 1972-to-1974 gap) supports only "his 1973 paper is not in his Xplore profile" | minor | Narrow the wording, or cite the search record in `lit_needed.md` | partly |
| F10 | §4: "Those are Hansen & Zottl 1971… and Hansen & Ward 1972" | Reads as a complete list; the profile has two more distribution-free detector papers from 1970–71 | minor | "the two with CFAR in the title" | yes |
| F11 | `detector_history.md` lines 473–476, directly above the new text (unchanged, but contradicted by it) | (a) "**All four primaries are now held and read**" now sits under a table row saying "1973 **no copy found**". (b) "Every radar quotation in this document is matched mechanically against a PDF on that shelf" is false. `tools/verify_quotes.py` traces **12 of 57** quotations, calls itself "not a gate", and **2 of the 4 new quotations miss** (L6, L12; both genuine by hand) | major | Change (a) to say which works are held and that the 1973 paper is not. Change (b) to "hand-checked against `pdftotext -layout`; the mechanical checker is provisional" | yes |
| F12 | `docs/learned/detector_history.html` (rendered copy, last touched 1f13973, 2026-08-29) | Still reads "GO-CFAR (Hansen 1973)" with no flag (line 243). Its table (lines 486–487) still puts Hansen & Sawyers 1980 in the attribution cell, which is exactly the error the 08-25 todo just closed. This is only disclosed inside the 09-10 todo, which no reader of the public page will see | major | Rebuild the HTML in this change, or put a visible "out of date" flag on the rendered page | yes |
| F13 | `GLOSSARY.md` paragraph: "closed every lineage row" and "it is the attribution" | Same sentence now says the `maxlt` attribution is not established | minor | "closed every *mechanism* row… attributions as in §4" | yes |
| F14 | §4 passage, README, table | The surname is inconsistent even inside the new passage: "V. Gregers Hansen" once, "Hansen" everywhere else. The canonical-surname todo is still open and says to use Gregers Hansen | minor (deferred on purpose per the 09-14 todo) | At least make the new passage consistent with itself | yes |
| F15 | Shelf `lit/radar/README.md` (supporting record) | No entries for `iee_conf_105_1973_CONTENTS_ONLY.pdf` or `gregers_hansen_AUTHOR_PROFILE_ieee.pdf`, and its header still says "Five works". That breaks its own rule: "A PDF with no entry is indistinguishable from a PDF someone downloaded and forgot." The passage leans on both files | minor | Add the two entries | yes |
| F16 | Run record, not the artifact | `git diff origin/main` on the branch shows unrelated deletions (`tools/make_intro_figures.py`, `make_mechanism_figure.py`, two 09-14 todos). This is because the branch base b1c8b2b is behind origin/main 3092d8c; the branch also carries the murderboard re-vendor. The supplied patch was filtered to 3 files. Six other changed files are companion records reviewed for context only (the three todos, `lit_needed.md`, `INDEX.md`, `doc_review_process.md`) | minor | Build the review diff from `git merge-base`, and list the companion-record edits as part of the change | yes |

## Other checks

- **Retractions:** the new text does not repeat the withdrawn "1973 is the origin" claim, or the pre-ruling todo's "earliest published treatment" replacement, except for the unsourced "usually credited" in F2. The inline ⚠ flag at line 204 is accurate. The `lit_needed.md` fix changing "nine years" to "fifteen years after the talk" is correct: 1988 − 1973 = 15.
- **Design and group-membership record:** does not apply. This is a literature attribution with no experimental units, so there is no membership record to consult. The equivalent here is sources the passage did not use. Moore & Lawrence 1980 is one: Rohling names them as proposers (F1). Finn & Johnson 1968 is on the shelf; I searched it and found no split window or greatest-of rule, only a half-in-clutter edge case, so it has no bearing.

## Files

- `<worktree>\docs\detector_history.md`
- `<worktree>\docs\learned\detector_history.html`
- `<worktree>\docs\GLOSSARY.md`
- `<worktree>\README.md`
- `<worktree>\docs\lit_needed.md`
- `<worktree>\tools\verify_quotes.py`
- `<darkroom>\bugarach\lit\radar\` (the shelf PDFs and `README.md`)
