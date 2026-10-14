# Murderboard run — the coordinated-share explainer

**What was at stake.** [`learned/coordination_share_explainer/`](../learned/coordination_share_explainer/README.md)
is the page a reader is meant to hold in mind while reading treatment results through
`tools/measure_coordination_rates.py`: what share of calcium events is coordinated, counted without
deciding which onsets belong together. A wrong account of what the measure counts becomes a wrong
reading of every treatment window. The review's three rounds turned on exactly that.

![Figure 5 of the page](../learned/coordination_share_explainer/explainer_coordinated-share-fig5-what-else-counts_20261014.png)

**Figure 1 (the page's Figure 5). What the measure counts with nothing planted.** A: share reported
coordinated for a field-wide busy stretch, by its length. B: by how much busier. C: pairs beyond
chance before (open) and after (filled) subtracting the shifted copies.

**What the review found, in the order it found it.**

1. **Round 1** found that the first draft's explanation of what the measure cannot see was wrong
   twice over. It said slow shared changes are counted. In fact they are subtracted: 98% of a
   threefold rise is removed. Its test of that could not fail, because a linear rise at the quiet
   background adds no triples. It also showed that "the adopted model reads a fifth low" was a
   property of the planted size mix. With one moment size the fixed model reads 5% low and the
   binomial 17% high.
2. **Round 2**, blind, found that the round-1 replacement ("how fast the rate changes matters, not
   how long") was refuted by its own figure. With nothing planted, a busy stretch leaves about the
   same false excess at every length from a minute up: 350 to 380 extra pairs per recording, from
   its first and last half minute, which the copies' slides of at most about half a minute cannot
   reach. The share falls with length only because a longer stretch adds more real onsets. Round 2
   also found that the page never connected this to its purpose. A drug wash-in inside a
   treatment window is exactly such a change.
3. **Round 3**, blind, found that two of the three numbers FOUNDATIONS §11 will report under
   treatment are off by 26% to 69% on every simulated set and are checked by nothing. It also
   found that every simulation's settings, not just one, come from the data set now under the
   contamination stop.

The page now says all of this, first, in *The question*.

**What would validate it, and how it generalises.** The figures are simulations with known
answers. What they cannot show is how big moment-size variation and shared rate changes are in
real recordings, so the page states the direction of each error, not its size on real data. The
general lesson is the second round's. A corrected mechanism is a new claim, and it was wrong
until a blind reviewer re-ran it.

## Decisions for Tony

1. **ADR-0014 against a cold reader** (role 8, blocking in all three rounds). The page follows
   ADR-0014 as an explainer: all six figures first, each with only its key. For its stated reader
   that puts about 40 uses of undefined terms before any definition. Options: treat a static,
   controlless explainer as a report under point 5 (main figure first, the others where the text
   discusses them), or allow first-use definitions in figure legends. This is the one structural
   finding that patching cannot retire.
2. **Moments per minute and cells per moment under treatment** (§11 names them). They are off by
   26% to 69% here, and pooling a baseline with its treatment window gives both the same *k* by
   construction. Should they be reported as treatment readouts?
3. **The bench's real-derived settings and the contamination stop.** The backgrounds, cell count,
   moment sizes, stretch level and intervals were measured on `senktide_ttx`, which is stopped. The
   page discloses this. Whether the stop reaches this page, or the bench itself, is your call.
4. **The adopted model.** The fixed model is adopted to match the bench. The bench mixes three
   moment sizes, where the fixed model reads low, and on the bench itself the binomial model is
   closer. The check cannot choose between them, because all six medians pass.
5. **Correspondence.** Nobody has asked the Rotter or Grün groups about this two-number variant of
   CuBIC. The reading log already names one open question to the Grün group, so one letter could
   cover both.

## Appendix: run record

- upstream:  syncytium2/murderboard @ 08f5ddb
- copy:      vendored @ 08f5ddb
- freshness: current
- artifact:  docs/learned/coordination_share_explainer/README.md (6411ebd7 -> 0c30c08b) and six PNGs, built by explain_coordination_share.py
- roles:     11 of 11 run (named agents), in each of 3 rounds
- reports:   coordination-share-explainer-2026-10-14-roles/
- rounds:    3 blind verify rounds; stopped at the round cap, unconverged

Mode: standard

**Stopping reason: round cap reached, not severity floor.** One structural finding (decision 1)
stayed blocking through all three rounds. Round 3's other blocking and high findings were
corrected **after the cap, in `180af410`, without a fourth review**; the commit lists them. This
run is delivered unconverged.

**Findings by severity per round.** Blocking counts each role's blocking or HIGH labels. Majors
are counted from the reports as the roles labeled them, and are approximate across roles, since
the roles do not share a scale.

| round | blocking (all) | of which the layout (role 8) | blocking, not layout | major (approx.) |
|---|---|---|---|---|
| 1 (first draft) | 16 | 6 | 10 | ~60 |
| 2 (blind) | 10 | 5 | 5 | ~45 |
| 3 (blind) | 12 | 7 | 5 | ~35 |

The non-layout blocking count went 10 → 5 → 5, and the findings were different each round. Round
2's were the round-1 replacement mechanism and the missing treatment caveat. Round 3's were the
§11 readouts, false sentences, and Figure 5C's dropped points. All of these are fixed: round 1's
and round 2's before the next round, and round 3's after the cap.

**What a clean run does not warrant.** This review found and fixed many defects. It is not a
correctness proof. The convergence table measures how quickly reviewers stopped finding things,
not whether anything remains, and this run did not stop finding things.

**Tooling gaps, stated.**
- `murderboard_prose.sh` is not vendored here. Role 5 ran its banned-construction search by hand
  with Grep in every round, and said so.
- One phrase in round 2's role-2 report is reworded in the archive, and marked where it stands.
  `tools/check_quotes.py` read the role's advice on how to cite a conversation, sitting beside its
  quotations of published papers, as quoted correspondence. Nothing in the report is
  correspondence.
- The vendored `murderboard_roster.sh` strips every `_` from the `reports:` line before resolving
  it, so an archive folder with underscores in its name can never pass `--require-reports`. The
  archive is therefore named with hyphens. The defect belongs upstream, in syncytium2/murderboard.

## Role ledger

Each role's grant declaration is the first line of its report, copied here verbatim from round 1,
except role 5's, copied from round 2: its round-1 line added, in parentheses, that it also held
the hand-back channel and no editing tool, which the grants check reads as part of the tool list.
Rounds 2 and 3 declared the same grants (files `round2/`, `round3/`); round 3's role 9 added the
same note about the hand-back channel.

| # | role | grant (round 1) | round 1 | round 2 (blind) | round 3 (blind) |
|---|---|---|---|---|---|
| 1 | Prove It | GRANT 1 ok — Read, Grep, Glob, Bash | 17 findings (1 blocking: the "a minute" rule refuted by the page's own case); full claim ledger | 16 (fireflies misattributed; the 41 s from the stopped folder; null pooling is chance) | 10 (real-derived settings; pooled 7 moments hides DI 15 to ORX 1.6) |
| 2 | DOI or Die | GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 8 (no literature cited; CuBIC, Kuhn verified; ⚠ nobody asked) | 10 (Ehm 2007 already estimates rate and size; CuBIC infers a lower bound; Staude 2008, Reimer 2012 owed) | 8 (multiple-shift is a coincidence count; CuBIC's own moment ratio; Qian & Elson unsearched) |
| 3 | Cross-Examiner | GRANT 3 ok — Read, Grep, Glob | 17 (1 blocking: the bench's spacing stale since 2026-10-07) | 16 (3C counts decoys; one set under two names; λ units) | 17 (real-derived settings; λ units; pooling claims overstated; glossary values) |
| 4 | Reviewer 2 | GRANT 4 ok — Read, Grep, Glob, Bash | 16 (3 blocking: the ramp test cannot fail; no boundary at a minute; pooling widens one recording) | 15 (2 blocking: mechanism refuted by its own figure; no treatment caveat) | 18 (1 blocking: §11's k and λ readouts unvalidated; no paired-change test; fast stream only) |
| 5 | Kill Your Darlings | GRANT 5 ok — Read, Grep, Glob | 22 (one em-dash; "a fifth" overstates; medium pairs "nothing") | 30 (bench undefined; bold sentence contradicts its own numbers; k and λ name drift) | 24 (3 false sentences: "every recording", "size variation alone… one size", "narrow end") |
| 6 | RTFM | GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 9 (3 high: window-edge loss is a third of the bias; pooling widens; the stretch mechanism) | 14 (excess constant from a minute up; CAL_NO_PROBE contradicts; one ramp, not two) | 5 (one size has no size variation: the 5% is edges; analytic −14%; tool check rerun at 2 s and 4 s passes) |
| 7 | Reinventing the Wheel | GRANT 7 ok — Read, Grep, Glob, Bash | 7 (bench's background and decoys omitted; bench null and elevated recordings exist) | 8 (house time axis exists; decoys in 3C's truth; spacing unrecorded) | 9 (no estimator re-implemented; constants re-typed; subprocess naming) |
| 8 | You Lost Me | GRANT 8 ok — Read, Grep, Glob | 29 (6 blocking rows: layout, undefined terms, internal names) | 26 (layout escalated to Tony; Fig 3, 5, 6 legends blocking) | 15 (all six figures blocking under ADR-0014; Fig 5C reads bimodal; Fig 3 medians read as data) |
| 9 | Show, Don't Tell | GRANT 9 ok — Read, Grep, Glob, Bash | 12 (k derivation shown nowhere; Fig 5 under half its canvas) | 8 (medians not drawn; mechanism prose-only; numbers live only in text) | 11 (set design in prose; slide ladder not drawn; lineage table) |
| 10 | Ship It | GRANT 10 ok — Read, Grep, Glob, Bash | 16 (close pair merges; lines unlabeled; text too small on GitHub) | 10 (5B unlabeled; 5C quiet rows hidden; Fig 3 x ranges differ) | 13 (1 high: Fig 5C dropped 14 of 48 points; dead review link) |
| 11 | Start With the Problem | GRANT 11 ok — Read, Grep, Glob | 8 (validation after limits; spacing before window) | 8 (sets defined after results; pooling promise undercut) | 7 (mixed set used before defined; Fig 5's place unstated) |

**Adjudication.** The following were fixed:
- every confirmed factual error;
- every unverifiable claim was flagged inline or removed;
- every named construction role 5 found (one em-dash, British spellings).

These are not fixed, and are carried as open items, either because they are design-level work
beyond this page or because they need a ruling:
- the layout (decision 1);
- a figure of planted paired changes, to show whether the alarm can ring under treatment (role 4,
  round 3);
- slow-stream and busy-background versions of Figure 5;
- simulations of 15-minute windows with 2–3 moments;
- the lineage table and the set-design timeline (role 9);
- the code docstrings the page lists under *For developers* (`CAL_NO_PROBE`, "bracket",
  `bench.REGIMES`, `population_cumulants`), noted for the tool's next editor;
- constants re-typed in the generator (role 7, round 3).
