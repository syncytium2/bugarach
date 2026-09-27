> Archived verbatim except repository paths, shown as `<repo>` (SAP004).

GRANT 8 ok — Read, Grep, Glob

Role 8 (You Lost Me), blind pass. I did not open docs/reviews/briefing_2026-09-26-roles/.

**What I checked:** `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`, all 693 lines, including the collapsed details. I opened the renders of Figure 1a in full and the rows and axis of 1b and 1c. I read the PNGs for Figures 2, 3, 4, 6 and 9, plus one thumbnail from section 3 (`../065/review/pages/DI_TTX_fast.png`). In `viewer.html` I read the markup for the setup steps (the left-rail "Open a folder" panel, the buttons, the deep-link handler, `importLanes` / `importLabel` / `DET_SHORT`) and the header of `detections.csv`. To test the combined stream I read `src/bugarach/combined.py`. Per the constraints, I quote no recording ids and no values from individual calls.

## Per-section verdicts

| Section | Terms and identifiers first used here | Defined here? | Can a cold reader follow? |
|---|---|---|---|
| Byline | full panel, ADR-0010, coded detector, learned model, simulation seeds, budget, `src/bugarach/bench*.py` | ADR-0010 inline. Full panel and seeds only in the Terms table at the end. Coded/learned not until the details block. Code path left raw | yes, just about |
| §1 lead box | ΔF1, F1, CoactDetect, shipped setting, proposal, decoys, recall, F1 without decoys, unflagged, merged calls, "ADR-0010 ruling 2", top unflagged row, level | ΔF1 and level here. The other **7+** only in the Terms table at the end or the collapsed details | **BLOCKING**: 3 or more undefined terms, and the one-line conclusion is missing (F-2) |
| Table 1 | interval wholly above zero, unflagged, above CoactDetect's proposal, `chorus_gain_norm_part`, "starting point (untuned)", "pick: training run n of 5" | unflagged in the caption. The rest only at the end | no |
| Table 2 | recall quiet · busy, planted events scored, calls on decoys, merged calls | quiet/busy only at the end | yes |
| Details: what each row is | rolling circular-shift null, surrogate threshold, `generate_sce`, ISI-adaptive, hysteresis, roll null, participation floor, offset k, "line's vote", center-surround, participation (ADR-0010 part 5) | ISI never expanded. "line's vote" is used two items before line is defined. Three different null names are never related to each other | no |
| Figure 1a–c | ΔF1, shipped, over a budget, no pick, † search limit, new/old bench | mostly, in the caption and the in-figure legend. "no pick" only at the end | **yes** (false-friend check passes, see F-12) |
| Details: how to read it | percentile bootstrap, focus rule, admissibility rule, elevated-rate test, precision swing, close-events test, "the worker's run notes", ρ | only the elevated-rate stretch is defined. **Focus rule, worker, close-events test, admissibility rule** are defined nowhere | **BLOCKING** (4 undefined terms) |
| Tables 3–5 | guard, merge gap, context window, extension cap, minimum run of synchronous frames, ADR-0009 decision 5, ruling 7 | none of the settings are defined | no |
| §2 viewer box | viewer, left rail, export folder (raw folder name), detections.csv, floor variant, lanes | floor variant only at the end. No location given for the export folder | **no**: the steps match the markup, but the promise fails (F-1, F-3) |
| §2 "read this first" box | proposal vs shipped | yes | yes |
| §2 leader rule paragraphs | leader, runner-up, baseline window, review pages, "the four detectors that take the participation floor as their minimum", participants, span, tolerance | participants and agreement inline. The four detectors are never named | no |
| §2 stream subsections plus Tables 6–8 | code-id headings, "search limit: guard 0 s", "where a merge would hide" | no | partly |
| Figures 2–10 | this call ▼, lane names, ROI | ROI only at the end | mostly. **Figures 3 and 9 read as the opposite of their label** (F-4) |
| §3 rasters | review pages, first treatment, thumbnails | partly | yes (thumbnail legibility belongs to agent 10/9) |
| Terms | "the glossary's distractors", "the count folder calls it shipped", "house clock" | leaks internal names | yes |

## Findings

**F-1: most combined-stream viewer links cannot work.**
- **Where:** §2 viewer box, Figures 8–10, and every "combined" link in Table 9.
- **Issue:** `viewer.html` has no notion of a combined stream. Grep finds "combined" once, in unrelated prose. The deep-link code builds its streams from the folder's own `stream` column (`STREAMS_SEEN`). `combined.py` builds that stream in Python and says never to add it to a slice. So a `stream=combined` link lands on the viewer's error "The link asks for stream combined, which … does not hold". `importLanes` also drops rows whose stream is not in view, so combined calls never draw. That is a third of the links the box promises.
- **Severity:** blocking.
- **Fix:** either have the viewer build a combined stream, or drop the combined links. If you drop them, say in the box that combined calls can only be seen on the review pages.
- **Verified:** yes against the viewer markup and `combined.py`. Not run. I did not inspect the export folder to see whether it carries a combined stream (unlikely, since `combined.py` derives it).

**F-2: the lead box gives counts but no conclusion, and relies on 7+ terms defined elsewhere.**
- **Where:** §1 box.
- **Issue:** a stranger reads "12 of 21 above the shipped setting … 0 of 20 above CoactDetect's own proposal". The sentence that matters is never written. The four-way comparison (shipped vs proposal, new vs old bench) is stated as three near-identical paragraphs of counts. Decoys, proposal, unflagged, shipped, F1 without decoys and merged calls are defined only in the Terms table at the end.
- **Severity:** blocking.
- **Fix:** open with the plain-language finding for each stream. Put a one-line definition of shipped, proposal and decoy in the box itself.
- **Verified:** yes (read).

**F-3: the viewer's lane names do not match the briefing's names.**
- **Where:** §2 viewer box versus the viewer.
- **Issue:** the viewer labels lanes through `DET_SHORT`:
  - CoactDetect appears as "coact".
  - SPIKE-synch appears as "sync".
  - rate+context appears as "rate".
  - **locust appears as "sixth"** (its CSV id is `cicada`).
  - Floor variants show as raw `own_floor` / `baseline_floor`.
  - Learned models show under raw ids with no "pick: training run n" and no shipped/proposal tag.
  - Every detector × variant gets a lane, roughly 20+, against the 3 in each figure.

  A reader hunting for "CoactDetect · proposal" or "locust" finds neither. The review pages in §3 do use the briefing's names, so only the viewer disagrees.
- **Severity:** major.
- **Fix:** map the ids to the briefing names in the viewer's lane labels, or add a translation line to the box ("coact = CoactDetect, sixth = locust, own_floor = the window's own floor, which the examples use").
- **Verified:** yes against the markup and the CSV header and rows.

**F-4: two "calls it, CoactDetect does not" examples read as "both called it".**
- **Where:** Figure 3 (fast) and Figure 9 (combined).
- **Issue:** with the caption covered, a stranger sees:
  - Figure 9: a CoactDetect mark right beside the ▼ on the same column of ticks.
  - Figure 3: a thin second call from the leader trailing a burst both detectors called, which reads as a double call on one event.

  Both captions give the distance to the nearest CoactDetect call. In one case that distance rounds to the tolerance itself yet is called "beyond" it, which reads as a contradiction. Meanwhile the stream text says the leader "calls many events CoactDetect does not". The chosen examples are timing near-misses, not events one detector missed.
- **Severity:** major.
- **Fix:** give the distance with enough decimals to show it is past the tolerance. Say in the caption that this is a timing split and not a missed event, or pick a median example with no CoactDetect call nearby. Either way, draw the ±tolerance band in the lane above.
- **Verified:** yes (renders read). Whether the examples are representative is for agent 4.

**F-5: internal code identifiers in audience-facing text.**
- **Where:** headings in §2, Tables 1 and 3–8, Figure 1 rows, figure lanes and captions, the byline, the details.
- **Issue:**
  - Learned-model names with underscores (`chorus_gain_norm_part`, `line_part`, `chorus_norm`, …) are used as display names everywhere, including h3 headings.
  - Also: `src/bugarach/bench*.py` twice, `generate_sce` in the details, the raw export folder name in the viewer box, and "the count folder calls it shipped" in Terms.
- **Severity:** major.
- **Fix:** give each model a plain display name (for example "chorus, gain + normalization, with participation") and keep the id in the details only. Drop the source paths and the folder-internal wording.
- **Verified:** yes.

**F-6: ADR citations stand in for explanations.**
- **Where:** throughout: "ADR-0010 ruling 5: a finding, not a tuned value", "ruling 2", "part 1/3/4/5", "ADR-0009 decision 5", "ruling 7", "ADR-0006 rules it coordination by construction".
- **Issue:** the reader cannot tell what a ruling says without opening the repo. "A finding, not a tuned value" is opaque without it.
- **Severity:** major.
- **Fix:** state the content in a clause and keep the citation in parentheses. For example: "guard 0 s turns the guard off; the search preferring 'off' is reported as a finding (ADR-0010 ruling 5)".
- **Verified:** yes.

**F-7: "guard" is never defined, yet it headlines two of three stream subsections.**
- **Where:** §2 stream notes, Tables 3–5.
- **Issue:** "CoactDetect · proposal is itself on a search limit: guard 0 s, a value that switches it off" is load-bearing, because it says the comparison side's setting is degenerate. No reader can tell what a guard does. The same applies to merge gap, context window and extension cap.
- **Severity:** major.
- **Fix:** add these settings to Terms, and define guard inline where it first appears in §2.
- **Verified:** yes.

**F-8: "How to read it" has 4 terms defined nowhere.**
- **Where:** details under Figure 1.
- **Issue:** focus rule, admissibility rule, close-events test, and "the worker's run notes" ("worker" names an internal session or machine). "Precision swing" is only loosely defined: a swing in what, measured how?
- **Severity:** blocking under the 3-term rule (the block is collapsed, which softens it).
- **Fix:** define each or cut it. Replace "the worker's run notes" with the name of the document meant.
- **Verified:** yes.

**F-9: the leader-rule paragraph has an unparseable sentence.**
- **Where:** §2, the paragraph after the boxes.
- **Issue:** "the four detectors that take the participation floor as their minimum at their own window's floor, the rest as they ran". Which four detectors is never said, and the grammar does not parse. "Review pages" and "window" are used before either is introduced.
- **Severity:** major.
- **Fix:** name the four detectors, and split the sentence in two: which floor variant the examples use, and why.
- **Verified:** yes.

**F-10: the detector glossary uses undefined jargon and three null names.**
- **Where:** details "What each row is".
- **Issue:**
  - ISI is never expanded.
  - "Rolling circular-shift null", "per-cell roll null" and (in Terms) "rigid-shift null" appear without saying whether they are the same thing.
  - "line's vote" is used before line is defined.
  - "Hysteresis detection", "surrogate threshold" and "center-surround in time" have no gloss.
- **Severity:** minor.
- **Fix:** expand ISI. Use one name for the shuffle null, or say how the three differ. Move line above chorus_gain_norm.
- **Verified:** yes.

**F-11: the example figures do not say which lane plays which role.**
- **Where:** Figures 2–10.
- **Issue:** lanes are labelled by name only. The leader / runner-up / comparison mapping lives in a muted paragraph above. The "this call" lane does not say whose call it is.
- **Severity:** minor.
- **Fix:** prefix the lane labels ("leader: …", "comparison: …") and label the marker lane "this call (leader's)".
- **Verified:** yes (renders).

**F-12: false-friend check on Figure 1 (a–c): pass, no finding.**
- It resembles a forest plot (dot and whisker per row, with a vertical no-difference line).
- In that idiom, x is the effect against a reference and the line at 0 is "no difference".
- Here the meaning is the same. The grey joiner between the filled new-bench mark and the open old-bench mark reads as a dumbbell, which is the intended reading.
- Minor label inconsistencies: "pick, run 5 of 5" in the figure against "pick: training run 5 of 5" in the tables, and "count (binned) · starting point" missing its "(untuned)".
- **Severity:** minor (labels only).
- **Verified:** yes.

**F-13: false-friend check on Figures 2–10: pass.**
- They are genuine rasters (x is time in the recording, rows are cells), with a lane above and a ▼ pointing down. The idiom matches its meaning.
- Two minor issues:
  - In Figure 3, the cells with no events in the window fill the bottom third of the rows and read as missing data. The sort order is stated in the page, but not near the figure.
  - Figures 8–10 (combined) draw fast and slow onsets in one ink, so a reader cannot see what "combined" adds.
- **Fix:** add a caption clause such as "rows below N have no events in this window; combined draws fast and slow onsets alike".
- **Severity:** minor.
- **Verified:** yes.

**F-14: the viewer box's first step does not say where the export folder is.**
- **Where:** §2 viewer box.
- **Issue:** it names a long raw folder name "from the bugarach exports folder", with no location or hint. The steps themselves match the markup exactly:
  - The "Open a folder" `<summary>` is in the left rail (`#side`).
  - The "Choose folder…" button is `#pickDir`.
  - "Open results (detections.csv)…" is `#pickResults`, in the same panel.
  - The "upload" caveat matches the viewer's own hint.
  - "Opens at its start" matches `applyDeep`, which shows the recording and does not seek.
- **Severity:** minor.
- **Fix:** give the location in the form Tony would recognise, and add "floor variant: the examples use own_floor" (ties to F-3).
- **Verified:** yes against the markup.

**F-15: small unexplained phrases.**
- "where a merge would hide" in the captions of Tables 6–8.
- "the glossary's distractors" points to an internal glossary.
- "house clock".
- **Severity:** minor.
- **Fix:** rephrase in plain words ("these calls overlap two or more of the other detector's calls, so a merge between events could be hiding there").
- **Verified:** yes.

**Tone:** sentence case is consistent, there is no all-caps emphasis in the prose, lists are formatted as lists, and "fire" does not appear. No finding.

**Boundaries:** thumbnail legibility in §3 (150 px crops show only the page headers) is for agent 10/9. Whether the example calls are representative (F-4) is for agent 4.

**Files:**
- `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`
- `<darkroom>/bugarach/2026-09-26-full-panel/briefing/viewer.html`
- `<darkroom>/bugarach/2026-09-26-full-panel/briefing/detections.csv`
- `<repo>\src\bugarach\combined.py`
