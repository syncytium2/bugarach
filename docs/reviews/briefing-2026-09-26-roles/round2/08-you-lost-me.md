GRANT 8 ok — Read, Grep, Glob

Role 8 (You Lost Me), blind pass. I did not open anything under docs/reviews/briefing_2026-09-26-roles/.

**What I checked:**
- `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`, all 646 lines. I read the prose, the captions, Tables 1–6, the Terms table and the SVG text of the three inline Figure 1 panels.
- Every example PNG the page embeds, 8 of them, opened with the caption covered.
- Only the parts of `viewer.html` behind the setup box: the folder picker and the Reopen logic.

I read as Tony: expert in the preparation, but not the author and not steeped in the bench, the search or the model code. No recording ids or individual call values appear below.

## Per-section verdict

| Section | Terms first used here | Defined here? | Can a cold reader follow? |
|---|---|---|---|
| Title and byline | "full-panel", "ADR-0010", "bench", "event spacing", "fresh simulation seeds", "the search", "the training", "adopted" | None on the spot. ADR and bench are in Terms at the page foot; "full-panel", "search" and "adopted" are defined nowhere | **BLOCKING**: 3 or more undefined terms, and the title's own noun ("full panel") is never explained |
| §1 summary box | new/old bench, CoactDetect, "shipped setting", F1, "rows", "unflagged", "the search's proposals", "learned picks" | No. "Unflagged" is defined later, in the Table 1 caption. CoactDetect is defined later, in "What is compared". Why CoactDetect is the reference is never said | **BLOCKING**: this is the first thing read, and it is a wall of numbers resting on 6 or more undefined terms |
| Figure 1a/b/c (forest plots) | ΔF1, 95% interval, "over a budget", "†", "proposal", "pick, training run N of 5", "starting point (untuned)", and the row names chorus_gain_norm_part, chorus_norm, line_part, tube_part, tube, line, locust, LoCo, SPIKE-synch, binned SCE, rate+context | Partly. The caption defines ΔF1 and the marks. The row names are explained two boxes further down. "Budget" and "search limit" are only in Terms | **No**: the chart itself is readable, but half the row labels are code identifiers |
| Table 1 | "interval above zero", "unflagged", "top unflagged row" | Yes, in the caption | Yes |
| "How to read it" box | percentile bootstrap, "noise unit", decoy, ADR-0006, "admissibility rule", "no-coordination recording", "elevated-rate test inside and outside its stretch", "precision swing between backgrounds", "close-events test", "the worker's README", machine-folder paths (`064/...candidates.json`, `065/...`), "ADR-0010 ruling 1/2", "slow ORX recordings" | Partly. Decoy is defined. "Stretch", "close-events test", "worker" and "admissibility" are not. The paths are internal | **No** (see findings F5 and F6) |
| "What is compared" box | coded vs learned, "SPIKE-synchronization profile with hysteresis", "circular-shift null", "roll null", CICADA, "surrogate threshold", "centre-surround kernel", "vote gain and bias", "participation (ADR-0010 part 5)", "floor", "offset k" | Partly. "Coded" and "learned" are never defined. CICADA is not expanded. chorus_gain_norm is defined in terms of chorus_norm, which is listed three entries later | **No**: circular order, code-name keys, and a stutter ("SPIKE-synch: SPIKE-synch: …") |
| Tables 2–4 (collapsed) | held-out F1, "merged calls", Guard, Context window, Merge gap, C_min, "SPIKE-synch bin dt", "Synchronous-frame run", "Count offset k", "grid's edge", "extension cap", "bracketed" | Merged calls, budget and search limit are in Terms. The parameter names are not. "Held-out F1" is not | **No** for the budget/limit mark rows. The number rows are fine |
| §2 viewer-setup box | "the site's viewer", "lanes", "variant", "participants and floors", export folder, `python -m bugarach.dataset`, Reopen | No: floors, variant and "the site" are undefined, and the Python command is a code instruction | **BLOCKING as a procedure**: see F9–F11. A first-time user will probably not get the promised one-click reopen |
| §2 leader paragraph | leader, "search limit", "baseline windows", "span", "the review tool's way", "ROIs", runner-up | Partly. The leader is defined well. ROI, baseline and span are only in Terms or not at all | Mostly yes. The trap is that the §2 reference is not the Figure 1 reference (F12) |
| §2 fast (group table, Figures 2–4) | "kind", "both call it / only the leader / only CoactDetect", "/h" | "Kind" is carried by the row labels. The runner-up lane is misattributed (F13) | Partly: Figure 3 reads as agreement (F15) |
| §2 slow (Figures 5–6) | same | same | Yes |
| §2 combined (Figures 7–9) | same | same | Partly: Figure 8 reads as agreement (F15) |
| §3 Tables 5–6 | "review pages", "first treatment", "aligned at the end of its own baseline" | Adequate for this reader (TTX and senktide are the PI's own conditions) | Yes |
| Terms | — | — | Useful, but it sits at the bottom, is linked only from the nav, and misses many terms used above (see F1) |

## False-friend check (render open, caption covered)

- **Figure 1a–c.** It looks like a forest plot. In that idiom each row is one item, the x axis is an effect size with an interval, and a vertical line marks the null. Here the axes mean the same thing, so it is **not a false friend**. One minor risk: each row carries two marks on offset sub-rows, joined by a grey *diagonal*. That reads as a slope or time-trend chart, where a dumbbell chart would use a horizontal join. It is low risk and the caption explains it. The sort order also invites "ranking", which the page disclaims in the "How to read it" box.
- **Figures 2–9.** Each is a spike-raster-style plot (x = time, one row per ROI) with event lanes above it. The axes mean exactly that here, so **not a false friend**. The ▼ lane points down at the raster, which follows the house rule.
- **One case of manufactured structure, in Figures 3 and 8** (see F15). The ▼ marks a leader call with a CoactDetect call only seconds beside it. With the caption covered, a stranger reads "both detectors call this event". The disagreement is really the 2.5 s span tolerance, or the leader splitting one burst into two calls. The panel is honest, but it demonstrates something other than what its caption says.

**One sentence per panel on what a cold reader sees:**
- Figure 2: a clear vertical column in the raster with all three lanes marked above it, plus a second column a few seconds later that all three also call.
- Figure 3: two nearby columns. CoactDetect calls the first; the ▼ sits on a thin second leader call just after it.
- Figure 4: one isolated column, called by CoactDetect and by the runner-up lane, with the leader's lane empty.
- Figure 5: a regular train of columns that all three lanes call; the ▼ is one of them.
- Figure 6: a small column that CoactDetect and the second lane call and the leader does not.
- Figure 7: a tall column called by all three.
- Figure 8: a pair of leader marks around the ▼ with a CoactDetect mark beside the second one. It reads as agreement.
- Figure 9: an isolated column called only by CoactDetect.

In the combined panels (Figures 7–9) the top rows of the raster form a dense band. If the ROIs are sorted, for example by event rate, nothing on the page says so, and the band reads as a distinct subpopulation (F16).

## Findings

Each finding gives location · issue · severity · fix · verified.

**F1.** Byline and §1 box.
- Issue: the title's "full-panel night" is never defined. The first box uses bench, CoactDetect, shipped setting, F1, unflagged, proposals and picks before any of them is defined. The Terms table is at the very bottom. The box also never says why CoactDetect is the reference.
- Severity: **BLOCKING**.
- Fix: open with a 3–4 sentence plain-language lede covering:
  - what ran overnight;
  - what the bench is, and new vs old;
  - why CoactDetect at its shipped setting is the yardstick;
  - what "unflagged" means;
  - a link to Terms.
  Then the numbers.
- Verified: yes (page text).

**F2.** Figure 1 row labels, Tables 1–4, §2 headings, figure lane labels and captions.
- Issue: internal code identifiers are used as audience names: chorus_gain_norm_part, chorus_norm_part, chorus_gain_norm, chorus_norm, line_part, tube_part (underscores and all). They are the headline "leader" in two of the three §2 comparisons.
- Severity: high.
- Fix: give each learned model a plain display name, e.g. "per-cell pooling network, with gain, with participation". Keep the code name only in a key.
- Verified: yes.

**F3.** Every "pick, training run N of 5" label.
- Issue: the index starts at zero, so "training run 0 of 5" reads as nonsense to a cold reader, and "4 of 5" is really the fifth run.
- Severity: medium.
- Fix: number runs 1–5, or write "run 1 (of 5)".
- Verified: yes.

**F4.** "What is compared" box.
- Issue:
  - chorus_gain_norm is defined as "chorus_norm with…" before chorus_norm is defined.
  - Entries stutter ("SPIKE-synch: SPIKE-synch: …", "rate+context: rate+context:", "binned SCE: binned SCE:", "locust: locust:").
  - "(coded)" and "(learned)" are never defined.
  - CICADA is not expanded.
  - The box sits *below* Figure 1, which needs it.
- Severity: medium.
- Fix: move the box above Figure 1 and order it so bases come before variants. Remove the doubled names. Add a one-line gloss: "coded = a hand-written rule with settings; learned = a trained network".
- Verified: yes.

**F5.** "How to read it" box, last three bullets.
- Issue: machine-folder paths (`064/count/fresh-realistic/candidates.json`, `065/fresh-bench-count/…`, `065/fresh-orx/…`) and "the worker's README" are internal plumbing in audience text. "Worker" and "064/065" mean nothing to the reader.
- Severity: medium.
- Fix: say "a follow-up run the same evening" and move the paths to a provenance footnote or a collapsed details block.
- Verified: yes.

**F6.** "How to read it" box (Budgets) and the Terms entry for budget.
- Issue: "admissibility rule", "elevated-rate test … inside and outside its stretch" ("stretch" of what?), "close-events test" and "precision swing between backgrounds" are named but never described in plain words. The ADR ruling and part numbers cannot be followed from the page, because none is linked.
- Severity: medium.
- Fix: give one plain clause per test, e.g. "a stretch of recording where the background rate is raised with nothing planted". Link the ADRs, or restate each ruling in a clause.
- Verified: yes.

**F7.** Tables 2–4, the mark rows.
- Issue: detector parameter names appear bare: Guard, Context window, Merge gap, C_min, "SPIKE-synch bin dt", "Synchronous-frame run", "Count offset k". "At the search's extension cap, so not bracketed" is jargon. A value of "99.9922th percentile" is shown to 4 decimals with a wrong ordinal suffix.
- Severity: low-medium. The tables are collapsed, which softens it.
- Fix: gloss each parameter once, in the What-is-compared box or Terms. Write "the search stopped at the edge of its range, so the best value may lie beyond it". Round the percentile.
- Verified: yes.

**F8.** Tables 2–4.
- Issue: "held-out F1 of the 5 runs" is not defined (held out from what?). "Over budget on the both benches" is ungrammatical and appears repeatedly.
- Severity: low.
- Fix: define held-out in Terms. Fix the template string to read "on both benches".
- Verified: yes.

**F9.** §2 viewer-setup box.
- Issue: the box promises that after the first time "a link needs one click on *Reopen*". In `viewer.html` the Reopen button is only revealed after `showDirectoryPicker()` succeeds. The viewer's own source comment says Chrome refuses that API on a `file://` origin, "which is exactly how this page is meant to be opened", and that the fallback file input is used instead. Opened from the darkroom as a local file, the reader will most likely **never see Reopen**. Every one of the 9 figure links and roughly 200 recording links would then be a fresh page load needing both pickers again.
- Severity: **BLOCKING** for "a briefing I can click on".
- Fix: test the flow once from `file://` in Chrome and Edge, and describe what actually happens. Better: make the links carry state (open in the same viewer tab via hash change without reloading), or pre-bundle what the viewer needs.
- Verified: partly. Checked against the `viewer.html` source and its comment; not run in a browser.

**F10.** §2 viewer-setup box.
- Issue: "Choose folder…" is inside the viewer's collapsed "Open a folder" accordion (a `<details>` element without `open` in the markup). A first-time user has to expand it first, and the box does not say so. Nothing says which browsers work. "The site's viewer" (which site?), "variant" and "floors" are undefined.
- Severity: medium.
- Fix: step 0, "expand *Open a folder* in the left rail". Name the supported browser. Replace "the site's" with "a copy of the bugarach viewer". Point to Terms for floor.
- Verified: partly. The markup shows `<details class="acc" id="accOpen">` without `open`; I did not check whether JavaScript opens it.

**F11.** §2 viewer-setup box.
- Issue: the reader is told to run `python -m bugarach.dataset` to find the export folder. That is a code command in audience text, and it assumes a configured venv on Tony's machine. The link also opens at the recording's start, so the reader must scrub to the call time in each caption by hand.
- Severity: medium.
- Fix: print the folder location on the page, resolved at build time with the machine-specific part shown as a data-root placeholder. Have the link open at the call time; the viewer already takes a hash, so add a `t=` parameter.
- Verified: yes (page text); the hash format was checked in the page's links.

**F12.** §2 leader paragraph.
- Issue: the examples set the leader against CoactDetect at its *proposal* setting, which is not Figure 1's reference (the shipped setting) and is itself on a search limit. This is stated once, in italics, mid-paragraph. A reader moving from §1 to §2 will assume the same yardstick.
- Severity: high.
- Fix: put it in the §2 section heading or a callout, e.g. "Note: here CoactDetect runs at its proposed setting, not the shipped one used in Figure 1, because …". Say why.
- Verified: yes.

**F13.** §2, the "Lanes in every figure below: A, B, CoactDetect · proposal (the runner-up, the next row meeting the rule)" line, in all three streams.
- Issue: the parenthetical grammatically attaches to CoactDetect · proposal, but the runner-up is plainly the *middle* lane (line_part / line / chorus_norm_part). Nothing else explains why that middle lane is there.
- Severity: medium-high. A reader will think CoactDetect is the runner-up.
- Fix: "Lanes: the leader (A); the runner-up, the next row meeting the rule (B); and CoactDetect at its proposal setting."
- Verified: yes.

**F14.** Figure 4 caption, and the same template in Figures 6 and 8.
- Issue: the counts read awkwardly: "one of 1 call of its kind (1 away from window edges)". The per-group rates "8.1/h" are an abbreviated unit.
- Severity: low.
- Fix: write "the only call of its kind", and "8.1 calls per baseline hour" in the column header.
- Verified: yes.

**F15.** Figures 3 and 8 (the leader-only examples), caption covered.
- Issue: in each, the ▼ leader call has a CoactDetect call within a few seconds on the same burst:
  - in Figure 3, CoactDetect calls the adjacent burst and the leader adds a second, thin call;
  - in Figure 8, CoactDetect's mark sits beside the leader's second mark.
  A stranger reads "both call it". The "leader-only" count therefore mixes split or offset calls with genuinely missed events. The caption's "CoactDetect · proposal does not [call it]" does not explain what the reader is looking at.
- Severity: high. It affects how the "only the leader: 32 calls" row is read.
- Fix: say in the caption how far the nearest reference call is and why it does not count (the 2.5 s span tolerance). Or choose, or additionally show, an example where the reference is silent on the whole burst. Consider splitting "only the leader" into "reference silent" and "reference nearby but outside tolerance".
- Verified: partly. Read from the render geometry; spans were not checked against detections.csv.

**F16.** Figures 7–9 (combined) and Figure 3 rasters.
- Issue: the top rows are densely active and the lower rows sparse. If the ROIs are ordered, for example by event count, this is an artefact of the ordering but reads as a distinct, highly active subpopulation. The y label ("combined · 44 ROI") does not say how rows are ordered.
- Severity: low-medium.
- Fix: state the row order in the y label or the §2 intro ("ROIs ordered by …").
- Verified: no. I could not confirm how the rows are ordered.

**F17.** Terms table.
- Issue: it is incomplete relative to the page. Missing: full-panel, the search, proposal-vs-search, coded/learned, held-out, stretch, variant, span, noise unit, CICADA, runner-up, leader. "ROI: one cell's trace" also conflicts slightly with the rasters, where a row shows events, not a trace.
- Severity: low.
- Fix: add these, and link first uses to their Terms anchors.
- Verified: yes.

**F18.** Figure 1 header text versus the §1 box.
- Issue: the panel headers say "fast stream · 23 rows" and the tables say 23/19/21 rows, while the box and Table 1 say "13 of 22 rows". The reader has to infer that CoactDetect-shipped is excluded.
- Severity: low.
- Fix: write "22 rows besides CoactDetect-shipped" in the box.
- Verified: yes.

**F19.** Tone.
- Issue: sentence case is mostly consistent. Group codes (DI/OVX/MALE/ORX) are in capitals, which is the house convention, so no finding there. Figure lists are properly formatted as lists; items are not smuggled into titles.
- Severity: none.
- Verified: yes.

## Boundary notes for other roles (not scored here)

- `figure1_leaderboard.svg` and `example_slow_leader_only.png` sit in the folder but are not referenced by the page. The page says no slow leader-only call qualified. That is agent 10's call.
- The page body contains real recording ids, including in figure captions and Table 6. That is fine for the darkroom copy, but it matters if any repo copy is made.

**Blocking rows, by section:**
- The byline and §1 summary box (F1): 3 or more undefined terms at the top.
- The §2 viewer-setup procedure (F9): the promised Reopen path very likely does not exist for a page opened from disk.
