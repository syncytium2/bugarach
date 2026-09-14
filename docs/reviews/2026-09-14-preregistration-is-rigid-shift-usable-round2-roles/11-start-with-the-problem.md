GRANT 11 ok — Read, Grep, Glob

# Argument order review: the rigid-shift pre-registration (blob 2c9813d)

**The main problem:** someone who reads top-down and executes will use the signed rule. The top of the page never says amendments exist, and it tells the reader to use the page "as written". The outcome logic ends up split across four places, 130 lines apart.

I read the artifact and the inbound link in `docs/goals/unsupervised-learning.md`. Following the blind rule, I did not open the run record in `docs/reviews/`.

## Spine (one claim per section)

**Signed body**
1. **Banner (L3–13):** Everything above the sign-off is frozen, and the run reads its result "against this page as written". The screen went in circles because its verdict rules were written after the data; this page sets the rule first.
2. **The question (L15–23):** Rigid shift is usable if a coordination-blind classifier can't tell it from real data and it still removes planted coordination. If yes, the goal moves to the model; if no, the goal stops.
3. **Why rigid shift (L25–38):** It's the only exploratory candidate the leak test couldn't catch at a realistic displacement, so a STOP here stops the goal. It also says "Joint-ISI was never measured".
4. **What this run cannot claim (L40–46):** The data are the same; only the rule and the randomness are fresh. VIABLE means "held up under a rule declared in advance".
5. **Data (L50–61):** The lab folder, baseline windows only, with fast and slow read separately. Cossart is used for the leak test only. Zero-event ROIs and motion-pinned recordings stay in.
6. **Displacements (L63–74):** Three *J* per stream, and every bound is a 98.3 % interval.
7. **Leak gate (L82–97):** The upper 98.3 % bound must be below 0.55. Uniform dither must be caught. The stream is void if 4 or more of 20 real-vs-real seeds flag.
8. **Count gate (L99–109):** The onset-count difference must lie within ±2 %, and `edge_thinning` must fail.
9. **Destruction gate (L111–131):** Scored at a 1.0 s bin; retained share must be at most 0.25. Controls are do-nothing and homogeneous resample. A saturated *J* is void. Cossart isn't scored.
10. **Outcome (L135–154):** A stream passes if any *J* passes, is VOID if controls fail at every *J*, and **FAILs otherwise**. A four-row table follows. STOPPED falls back to simulator models and hand-written detectors.
11. **Not in this run (L156–161):** Band statistics, other candidates and model training are out of scope.
12. **What has to be built (L163–173):** A runner, a bin parameter, a seed-voiding rule and a count statistic.
13. **Review, once (L175–178):** The murderboard runs before signing.
14. **Sign-off (L182–190):** Accepted as written.

**Amendments**

15. **Preamble (L192–196):** The page was signed before review; the review runs now.
16. **Status note (L198–204):** Eleven amendments are proposed, **none is adopted yet, "Do not run"**.
17. **Adopted amendments preamble (L208–216):** All eleven are adopted and override the body. They are post-exposure.
18. **Terms (L218–220):** Defines window, interior window, cell and bootstrap.
19. **The outcome, completed (L222–251):** Four results per cell. A void or undecided cell can never make a stream FAIL. Adds an UNRESOLVED outcome and rerun rules.
20. **The leak gate (L253–271):** Interior windows only, one-sided bounds, a bootstrap that refits, a can-pass check, and the negative control relabelled as a machinery check.
21. **The count gate (L273–285):** Counts occupied frames on interior windows, uses a two-one-sided-tests interval, and fixes `edge_thinning` at 5 s.
22. **The destruction gate (L287–312):** Slow is also scored at 2.0 s. Adds replication, gated K, a saturation table committed first, and `freeze_half` as the graded control.
23. **Randomness (L314–318):** Every key is salted with the run tag, and a test checks that no key matches the 2026-09-11 scheme.
24. **What was known before signing (L320–329):** Exploratory results existed at nearly every cell, so VIABLE becomes "a rule fixed after an exploratory look".
25. **What a PASS may claim (L331–338):** Narrows what leak, offsets, largest *J* and destruction results may claim.
26. **What STOPPED means (L340–348):** STOPPED stops the goal only when the failure is intrinsic. Corrects the Joint-ISI sentence. Requires the aggregate-channel leak test before any pooling model.
27. **Groups (L350–355):** Per-group reporting. A pooled pass with any group at or above 0.55 becomes NARROWED.

## Arc used

**For the signed body:** problem → question → why this candidate → limits → data → parameters → gates → outcome → what each outcome commits to → build → sign-off. The body follows it well:
- **Cold open:** the page opens on the problem (post-hoc verdict rules made the screen go in circles) and then the question. That is correct.
- **Order within the body:** gates come before the outcome that combines them, and limits are stated before the parameters.
- **One exception:** the build list depends on everything above it but arrives after the commitments. That's acceptable.

**For an amended pre-registration:** a pointer before the first overridable sentence → the frozen body → sign-off → amendment log with current status → overrides in body order, each naming what it replaces → new disclosures. The page departs from this in four ways, and none of the departures is stated:
- there is no early pointer;
- the log shows a stale status;
- the overrides are not in body order;
- the overrides don't name what they replace.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified |
|---|---|---|---|---|---|
| F1 | Banner L3–6; first override at L213 | **The page never says, before line 208, that overrides exist.** The banner describes amendments only as a possibility ("a change found necessary… goes in as a dated amendment"). It also says the run reads its result "against this page as written", which the amendments reverse. A top-down reader meets about 170 lines of superseded rule first, and is told they are authoritative. | critical | The page's own rule forbids editing above the line. Two options: (a) ask Tony to rule that a dated navigation note with no rule content ("⚠ 2026-09-14: adopted amendments below override the leak, count, destruction and outcome sections; read them first") may sit directly under the title; (b) failing that, record a residual ⚠ and add the fixes in F2 and F9. | yes |
| F2 | "What has to be built" L163–173 | **The build list a session will build from is stale.** It omits most of what the amendments require: interior-window scoring, the pair-count report, the refitting bootstrap with fold seeds per resample, the can-pass check, the occupied-frame statistic, `edge_thinning` at 5 s, the second slow bin, the replication counts, gated K, the saturation table as the runner's first step, the `freeze_half` control, the salted keys and their test, and per-group reporting. A session reading top-down builds the signed runner. | critical | Add a dated subsection, "What has to be built, as amended", inside Adopted amendments. Restate the full build list there so the build has one list. | yes |
| F3 | Outcome L137–139 vs "The outcome, completed" L232–234 | **Superseded before the override.** The signed rule says "FAIL otherwise", so a stream with void or undecided cells FAILs. Combined with L22 and L36, that can STOP the goal. The override appears 95 lines later. This is the most consequential wrong application available to a top-down reader. | critical | Covered by F1's pointer. The override should also say explicitly that it replaces the whole signed outcome section, including its table (see F9). | yes |
| F4 | Status note L198–204 | **The stale state comes before the current state.** "None is adopted yet… Do not run until Tony has ruled on each" reads as an instruction. The adoption comes four lines later, under a different heading, and nothing marks the note as superseded. A careful reader may stop here. | major | Add a dated line straight after L204: "Superseded 2026-09-14: all eleven adopted, see below." Leave the note itself, since it is a log entry. | yes |
| F5 | Adopted amendments as a whole (L222–355) | **The overrides are in a different order from the body, and none names what it replaces.** The body runs leak → count → destruction → outcome. The amendments run outcome → leak → count → destruction → randomness → disclosures → claims → STOPPED → groups. A reader can't hold a signed section next to its override without searching. No subsection says "replaces L90–97" or "replaces the table at L141–146". | major | Add a supersession map in a dated note at the top of Adopted amendments: each body section with its lines, the amendment that overrides it, and whether the replacement is total or partial. If adopted text may move, also reorder the subsections to follow the body. | yes |
| F6 | "The outcome, completed" L230 → "The leak gate" L267–269; also "gated K" L298–302 | **Terms are used before they are defined.** The outcome section uses the can-pass check ("see *The leak gate*") and void-for-destruction ("no K is gated") to define UNDECIDED and VOID. Both are defined 30–70 lines later. The body got this order right, with gates before the outcome; the amendments reverse it. | major | Include in F5's reorder: gates first, outcome last. Or note in the map that the outcome subsection should be read last. | yes |
| F7 | Outcome logic split across L238–251, L342–344, L354–355 and body L148–154 | **The verdict can't be read from one place.** The amended table gives an outcome. "What STOPPED means" then narrows STOPPED (only an intrinsic failure stops the goal), and "Groups" can downgrade a PASS to NARROWED. Both come after "What a PASS may claim". A reader who stops at the table has an incomplete verdict. The table has no group column and no intrinsic-failure qualifier. | major | In the reading-order note, state that the verdict is the table, then the STOPPED scope, then the group downgrade. Better, add a dated "verdict procedure" of three numbered steps right after the table. | yes |
| F8 | "Why rigid shift" L34, corrected at L345 | **A correction is filed in the wrong section.** The Joint-ISI correction concerns the candidate rationale, but it sits under "What STOPPED means". A reader checking the rationale won't find it. The tube requirement (L347) has the same problem: it belongs with the body's "What each outcome commits to next" (L148–151). | minor | In the supersession map, point the rationale section to L345 and the commitments to L347. | yes |
| F9 | "What this run cannot claim" L42–46 vs L328–329; "The question" L22 and L36 vs L342 | **Early framing is superseded with no pointer.** The body's reporting language ("a rule declared in advance") and its consequence ("a STOP stops the goal") are what a reader carries through the whole page. Both are narrowed only in the last three amendment subsections. Anyone writing up a result may quote the early version. | major | Put both in the F5 map. The reporting sentence at L328–329 should say explicitly that it replaces L45–46. | yes |
| F10 | Negative control L95–97 vs L270–271 | **Unclear whether the override is total or partial.** The amendment says "unchanged, 4 or more of 20 seeds", and then "Nothing decides on its P values". But the signed rule decides VOID on seeds that flag at α = 0.05. An executing reader can't tell whether the negative control still voids a stream. This is an ordering defect, not just a content one: the override doesn't name what it keeps and what it drops. | major | A dated clarification: "the 4-of-20 rule still voids the stream" or "it no longer voids anything". | yes |
| F11 | L198, L210 ("eleven") vs subsections L222–350 | **The eleven amendments don't map to the page.** There are nine subsections under Adopted amendments, so a reader can't check that all eleven arrived or which is which. (I can't see the run record's own list because this pass is blind.) | minor | Label each amendment (by name, not number) where it lands, or say which subsections combine several. | partly: the nine-subsection count is verified; the mapping to the eleven is not |
| F12 | Post-exposure caveat at L202, L213–216, L326–329 | **The same caveat appears three times.** Only the last states the reporting consequence, so the first two ask the reader to weigh something they can't yet act on. | minor | No change needed above the line. The map could point the caveat straight to L328. | yes |
| F13 | `docs/goals/unsupervised-learning.md` L36–42 (outside the artifact; this is how readers arrive) | **The entry point is half right.** It correctly says the amendments win, but it links to the page top rather than the amendments anchor. It also says the page "carries the exit criterion in its outcome table", which is ambiguous because the signed table is superseded. This file isn't frozen, so it is the cheapest place to give a pointer before the first superseded line. | minor | Link to `#adopted-amendments--2026-09-14` and say "the amended outcome table". | yes |

## Direct answers

- **Can a top-down reader apply superseded text before reaching the override?** Yes. It happens at the leak bounds (L90), the count statistic (L105), the destruction bin and controls (L119–129), the outcome rule (L137–146), the STOPPED consequence (L22, L36, L152), the reporting language (L45), and above all the build list (L163–173).
- **Is there a pointer early enough?** Not on the page. The first sign that overrides exist is L194. The only early pointer is in the goal file, which links to the page top.
- **Does anything arrive before the reader can evaluate it?**
  - In the body, no, apart from vocabulary, which belongs to the plain-reading reviewer.
  - In the amendments, yes: the outcome subsection depends on the can-pass check and gated K, which are defined later (F6). The verdict is also finished by "Groups" and "What STOPPED means" after the table has already been read as final (F7).
