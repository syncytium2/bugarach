> Archived verbatim except machine-local paths (shown as `<darkroom>`, `<worktree>`, `<scratchpad>`, `<repo>`, SAP004) and one redaction: four call times from real recordings in finding F-2 are replaced by
> `[t]`, because nothing derived from real data goes into this public repo (FOUNDATIONS §5). The arithmetic the
> finding rests on is unchanged: each quoted time is a call past the half-minute, printed a minute late.

GRANT 5 ok — Read, Grep, Glob

(I also hold SubagentHandback, which is only the hand-off channel. I have no Edit, Write, NotebookEdit or shell.)

# Role 5, line editor: full-panel briefing, round 1

**Artifact read:** the built page `<darkroom>\bugarach\2026-09-26-full-panel\briefing\index.html`, all 487 lines. I skimmed the SVG coordinate block and read every prose, caption, table-mark and Terms line. Generator cross-checked: `<worktree>\tools\make_briefing.py` (render path, lines 568–581, 662–663, 740–779).

**Tool receipt:** `murderboard_prose.sh` is **not run**. It does not exist: no match for `**/murderboard_prose*` under `<repo>`. I also hold no shell, so I could not have run it anyway. Treat this as a gap, not a clean result. I did the construction search by reading and by Grep over the HTML and the generator. The word counts below are my hand counts (±5 words), not tool output.

**Banned-construction list used:** the house list in the role-5 checklist of `doc_review_process.md` as given to me, with CLAUDE.md's "data" plural and no-"fire" rules added.

## Construction search (by Grep and by reading)

| construction | hits | where |
|---|---|---|
| delve, leverage, robust, seamless, crucial, landscape, tapestry | 0 | Grep over the HTML and `make_briefing.py` |
| "not just X but Y", "it's not about A", "it's worth noting", "In today's ___" | 0 | same |
| "fire", "fires", "fired", "firing" (house rule) | 0 | same |
| singular "data" (data is, was, shows, itself) | 0 | same |
| em-dash pivot into an uplifting close | 0 | the one prose em-dash (line 464) is a pivot, but into a count, not an uplift; it is garbled for another reason (F-12) |
| three-item list built for rhythm | 0 | the one three-item list (line 448: both call it, only the leader does, only CoactDetect does) is three real categories |

## Block table (hand count) with the passage test

| block | words | sentences | the one sentence it exists to deliver | what the other words buy | verdict |
|---|---|---|---|---|---|
| Byline (l.41) | ~35 | 3 | "Every number is read from the run's own files; nothing here is adopted." | Date and build time are evidence. | Keep. Payload is last; promote it. |
| "How to read it" box (l.44) | ~117 prose + ~40 metadata | 5 + 2 lines | "Each row is its paired F1 difference from CoactDetect's shipped setting; an interval clear of zero is one the seeds resolve." | S3 (same candidates) is ambiguous. S4 is a needed caveat but unparseable. The metadata repeats "seeds per background" six times. | Trim. Rewrite S4 (F-3). Compress metadata (F-4). |
| Table 1 caption (l.45) | ~45 | 1 | "Per stream and bench: how many rows beat, tie or trail CoactDetect's shipped setting." | A misplaced "including zero" makes it self-contradictory. | Rewrite (F-5). |
| Page as a whole / Table 1 | n/a | n/a | **Nothing states it.** No sentence says what the night found. | n/a | Major (F-1). |
| Figure 1 caption (l.443) | ~50 | 4 | "Paired ΔF1 per row; filled = new bench, open = old, red = over budget." | The §5 gloss duplicates Terms, but a reader needs it at the figure. | Keep. |
| Row marks, Tables 2–4 | 10–25 each | n/a | "Over budget on [bench]: [quantity] X against Y." | The same sentence printed twice when both benches give identical values. | Collapse (F-7). |
| Examples intro (l.448) | ~105 | 6 | "Per stream, three real baseline calls: both call it, only the leader, only CoactDetect." | The file path indexes rather than names. "Lanes sit above the raster; nothing is drawn on it" tells Tony his own rule back and buys nothing. The median-choice sentence earns its place. | Trim (F-9). |
| "Passed over" note (l.450) | ~45 | 4 | "LoCo · proposal ranks higher but never disagrees with CoactDetect, so it has nothing to show." | The middle sentence is garbled, and the last sentence is the payload. | Rewrite and promote (F-8). |
| Figure captions 2–10 | ~50 each | 3–4 | "[kind]. Recording, group, time, participant count, window." | "Hover a call in the viewer for its participants and floors." is said nine times, plus once more in the §3 box. | Say it once (F-10). |
| §3 "Opening one recording" box (l.463) | ~150 | 7 | "Links open the viewer. The first time, point it at the export folder and then at detections.csv." | These are instructions, and a reader needs them. "Nothing leaves the machine" is reassurance; keep it if Tony has asked about it, otherwise cut. | Mostly earned (F-13, F-14). |
| Table 5 lead-in (l.464) | ~25 | 1 | "Table 5 links the night's 24 review pages." | The rest is garbled. | Rewrite (F-12). |
| Terms (l.466–486) | ~200 | 9 entries | Glossary | The slash-pair entries are ambiguous, and several terms are missing. | F-11, F-15. |

## Findings

| # | location | issue | severity | suggested fix | verified |
|---|---|---|---|---|---|
| F-1 | Page, between the byline and §1 / Table 1 | No block states what the night found. Table 1 carries the result: most rows beat CoactDetect's shipped setting on the new bench, few or none on the old, and the new-bench top rows are over budget. No sentence says so, so the one-page briefing has no payload sentence. | major | Add one or two sentences above Table 1 stating the finding as the data show it. Boundary: role 11 owns section order. This finding is only that the sentence does not exist. | yes (read whole page) |
| F-2 | Figure 2, 3, 6, 9 captions; generator l.769 `{t / 60:.0f}m{t % 60:02.0f}s` | **The time stamp is wrong.** `.0f` rounds the minutes instead of flooring them, so any call past the half-minute gains a minute. Figure 2 reads one minute late for a call at [t]. Figure 3 reads one minute late for [t]. Figure 9 reads one minute late for [t]. Figure 6 reads "20m60s" for [t]. Four of nine captions send the reader to the wrong minute, one with an impossible seconds field. | blocking | `m, s = divmod(round(t), 60)`, then `f"{m}m{s:02d}s"`. Boundary: a factual defect more than a prose one (roles 4 and 10). Filed here because I found it and it is mechanical. | yes (arithmetic against the href `t=` values in the HTML and the generator line) |
| F-3 | "How to read it" box, sentence 4 | "…the shipped settings, the reference among them, date from before ADR-0010, when the old bench was the only one: each column is partly a field some rows were chosen on and others were not." This is 47 words with two nested clauses. "Field" is undefined jargon, and "each column" means each bench, which a reader must work out. | major | "Proposals and picks were tuned on the new bench. The shipped settings, CoactDetect's included, were tuned before it existed. So the new bench favours proposals and picks, and the old bench favours shipped settings." | yes |
| F-4 | Same box, sentence 3, and the two metadata lines | "The new and old benches score the same candidates." "Candidates" is undefined; it means rows. The metadata repeats "seeds per background" six times, and "background" (quiet or busy) is never defined. | minor | "Both benches score the same rows." Metadata: "new bench, scored [time]: seeds per background, fast 48 · slow 24 · combined 24." Define "background" in Terms. | yes |
| F-5 | Table 1 caption | "…a 95% interval wholly above CoactDetect's shipped setting, including zero, or wholly below it". "Including zero" attaches to "wholly above" and contradicts it. | major | "…how many rows have a 95% interval wholly above zero, one that includes zero, or one wholly below zero, on each bench." | yes |
| F-6 | Table 1 cells ("1 rows", twice); marks "1 calls/h", "1 calls/min" (generator l.106–108, l.662–663) | Number agreement. | minor | Pluralise by count, or drop "rows" from the cells, since the column header already says rows. | yes |
| F-7 | Row marks, Tables 2–4 (e.g. Table 3 row 3: "2.44 calls/h" printed once for the new bench and once for the old) | The same over-budget sentence is printed twice with identical values. It reads as two measurements when it is likely one, because the empty recording does not depend on bench spacing. The Table 4 mark "0.10 against a limit of 0.1" is flagged red but reads as not over, because rounding hides the excess. | major | When both benches share the value, write "over budget on both benches: …". Print enough digits that the flagged number visibly exceeds the limit (e.g. 0.104 against 0.10). | yes (text); the cause of identical values is inferred |
| F-8 | "Passed over" note (l.450; generator l.750–755) | "…none gives an example of: LoCo · proposal calls it; CoactDetect does not; CoactDetect calls it; LoCo · proposal does not." The two list items are joined with "; " while each contains a semicolon, so it reads as four clauses. The payload is the last sentence. | major | "Passed over: LoCo · proposal ranks higher, but on its 91 baseline calls it never disagrees with CoactDetect, so there is no disagreement to show." Join items in the generator with " / " or number them. | yes |
| F-9 | Examples intro (l.448) | The leader is used ("only the leader does") before it is defined. The first sentence defines it only implicitly and indexes a machine-folder path (`065/review/...`), where the house rule is to name things, not index them. "Lanes sit above the raster; nothing is drawn on it." earns nothing for this reader. | minor | Open with "The leader is the highest-ranked row that ran on the real recordings and is within every budget (CoactDetect excluded)." Move the path to a title attribute or the JSON. Cut the lanes sentence. | yes |
| F-10 | Figures 2–10 captions and the §3 box | "Hover a call in the viewer for its participants and floors." appears ten times. "Floors" and "floor variant" are undefined jargon. The captions also list a third lane (LoCo on fast, line on slow, chorus_norm_part on combined) without saying why it is there. On fast this is doubly confusing, because LoCo is the row just passed over. | major | Say it once in the §2 intro. Define "floor" in Terms. Add half a clause giving the rule for the third lane (e.g. "the next-ranked row"). | yes (text); the reason for the third lane is unknown to me |
| F-11 | Terms "new bench / old bench", "shipped / proposal" | The slash-paired definitions force the reader to align halves. "…/ at least 120 s apart, as before it" has an ambiguous "it" (ADR-0010). | minor | Split into separate entries: "old bench: events planted at least 120 s apart, the spacing used before ADR-0010." | yes |
| F-12 | Table 5 lead-in (l.464) | "Every recording in a group whose first treatment was the same, stacked and aligned at the end of its own baseline — the night's review pages, 24 pages:" is garbled. "Group whose first treatment" misattaches the treatment to the group, and "pages, 24 pages" repeats itself. | minor | "Table 5 links the night's 24 review pages, one per group, first treatment and stream. Each stacks its recordings, aligned at the end of each one's baseline." | yes |
| F-13 | §3 box | It prints a full personal absolute path (a person's name inside a Dropbox path). This is harmless in the darkroom, but a repo copy made with `--also` would carry it (CLAUDE.md, SAP004). | minor | Say "the `detections.csv` beside this page". Boundary: publication belongs to another role. Flagged because it is also wordier than the name. | yes (text); whether a repo copy exists: no |
| F-14 | §3 box, last sentence | It suggests copying the results file into the export folder. CLAUDE.md treats the export folder as the producer's input, and this sentence invites writing into it. | minor | Drop the suggestion, or say "keep it beside this page". Boundary: role 4 or a foundations check. | yes (against CLAUDE.md) |
| F-15 | Terms, and table labels generally | **"Seed" has two meanings.** It means simulation seeds in "mean over seeds" and ΔF1, and a learned model's training seed in "pick, seed 4". There is also an undefined label "best seed, seed 4" (Table 3 row 3, Figure 1). Undefined terms: SCE (in "binned SCE"), stream, baseline window, background, ADR, the probe (Terms says "promiscuity probe", the tables say "the probe"). CLAUDE.md requires every abbreviation to be defined. | major (the "seed" collision); minor (the rest) | Write "simulation seeds" wherever the statistics are meant, and "training seed N" in the setting column. Define "best seed" or relabel it "no pick (best training seed 4)". Add the missing Terms. | yes |
| F-16 | Tables 2–4 marks; Figure 1 labels | The ruling-5 flags use five words for one idea: "at its limit", "at its grid floor", "at its grid ceiling", "at its cap", "at its edge". One flag, "unbracketed, no axis named", is opaque. "Proposal §5" in labels is an index where the page could use a name. | minor | Pick one pair of words: "at the grid edge (floor)" and "at the grid edge (ceiling)". Gloss "unbracketed". Label rows "proposal (on grid edge)". | yes |
| F-17 | Byline vs. how-to box | Time formats are mixed: "20:29 EDT" against "1:33 AM EDT" and "8:03 PM EDT". | minor | Use one format. | yes |
| F-18 | Byline, how-to box, Terms | "ADR-0010" appears seven or more times and is never named. The house rule is to name things, not index them. | minor | Name it once, e.g. "the realistic-spacing ruling (ADR-0010)", then use the name. | yes |

**No findings on:** banned words or constructions, the "data" plural, "fire" for calcium events, throat-clearing openers, and recap closers. The page has no closing summary paragraph, which is correct.

**Boundary note for the main thread:** F-2 (a wrong timestamp) is factual and mechanical. I filed it here because I computed it from the page itself. It should not be dropped as out of lane.

**Public-repo constraint honoured:** no recording or slice id is quoted in this report; examples are referred to as Figure N.
