---
status: open
filed: 2026-09-14
---

# What the greatest-of review left for later

The murderboard on `detector_history.md` §4.1, *Where greatest-of began*
([run record](../reviews/greatest-of-origin_2026-09-14.md)) found these. Each one is outside that
change's scope or needs a resource the change did not claim. None of them reopens Tony's ruling
that the origin stays *not established*.

- **The darkroom copy of the history page is stale.** The repo copy,
  `docs/learned/detector_history.html`, was rebuilt in the same change. The copy under
  `<darkroom>/bugarach/` dates from 2026-08-29 and still reads "GO-CFAR (Hansen 1973)". Rebuild it
  with `tools/md_to_page.py docs/detector_history.md --also docs/learned`, after claiming the
  darkroom on `docs/SESSIONS.md`. A hand-written darkroom report,
  `<darkroom>/bugarach/2026-09-07-pilot-apv-cnqx-gz/REPORT.md`, carries the same citation.
- **`tools/md_to_page.py` mis-renders two things in `detector_history.md`**, and GitHub renders
  both correctly. It has no strikethrough extension, so `~~…~~` shows as literal tildes. It also
  collapses the 3-space continuations in §7's numbered list into one paragraph, so items 3–5 run
  into item 2. Both were already on main. At 400 px, its tables also overflow the column.
- **The shelf's read-status README has no entries for two PDFs that §4.1 relies on:**
  `lit/radar/iee_conf_105_1973_CONTENTS_ONLY.pdf` and `lit/radar/gregers_hansen_AUTHOR_PROFILE_ieee.pdf`.
  The first filename also misdescribes its file. It is a notice of the volume in *Proc. IEE*
  120(11), November 1973, p. 1391, not the volume's contents page. The README's provenance line
  says two papers were "confirmed from Rohling's printed reference list", but one of them is
  Gandhi & Kassam 1988, which a 1983 paper cannot list.
- **LoCo's `maxlt` threshold is not calibrated the way greatest-of CFAR's is.** Role 6 raised this,
  and the code confirms it. In radar greatest-of, the scale factor is re-solved for the maximum,
  so the design false-alarm rate holds (Hansen & Sawyers 1980, eq. 7; Rohling 1983, Table I).
  `loco.py` takes `max(tl, tr)` of two per-half thresholds, each already set at the nominal
  percentile. The combined bar's null exceedance rate is therefore at or below the nominal
  percentile, not equal to it. §4's `maxlt` paragraph says the rule matches and the estimator
  differs, but not that the calibration differs as well. In radar terms the construction is
  closer to OSGO-CFAR (greatest-of over order-statistic halves).
- **The other attributions have not been held to §4.1's standard.** Role 4 raised this. Finn &
  Johnson 1968 as the origin of cell-averaging rests on the interface2 audit. Gandhi & Kassam cite
  it only in a group of seven references, and that group includes Steenson, *Detection
  performance of a mean-level threshold*, 1968. Trunk 1978, Weiss 1982 and Rickard & Dillard
  (cited in `cfar_scope.html`) are not on the shelf.
- **Questions for Tony (role 2):**
  - Has anyone written to the IET archives, to V. Gregers Hansen, or to Technology Service
    Corporation (thanked in the 1980 paper)?
  - ~~Is a library request wanted?~~ **Answered 2026-09-14: Tony placed an interlibrary-loan
    request**, identified by OCLC 952520 and ISBN 0-85296-112-X. What to do when the copy arrives
    is recorded in `docs/lit_needed.md`. Until then, the search-only HathiTrust scans (records
    001618382 and 011456921) remain the quicker way to check whether the paper uses "greatest"
    or "split" at all.

- **Found in the review's third round, outside this change:**
  - `detector_history.md` §7 item 4 says Rohling 1983 is "a greatest-of combination rule and an
    order-statistic estimator, in print". Role 4 reads Rohling as describing the two as separate
    processors (eq. 7 versus eqs. 9–10), which would make that sentence an origin claim for
    LoCo's hybrid. Check it against the PDF before changing it.
  - `docs/learned/cfar_scope.html` names a detector row "binned SCE, CICADA". The port is
    **locust** and must not be reported as CICADA (§6.3, README).
  - `docs/handoffs/2026-09-10-the-surrogate-is-the-design.md` still says "the chronology leans
    toward 1973" and "do not change the column until someone has read the 1973 paper". It needs
    a dated note pointing at §4.1.
  - The README ° legend now claims unmarked works were read here. Amarasingham et al. 2012 is
    marked ° but is on the surrogates shelf, read in part. Whether Cossart, Aronov & Yuste 2003
    was read here is unrecorded.
  - `tests/test_index_resolves.py` checks paths but not `#anchors`, so a renamed §4.1 heading
    would silently break the README and GLOSSARY links.
  - The CiNii and OpenAlex records also give 325–332, probably derived from citations. Japanese
    Weibull-clutter papers that cite the 1973 paper, radar handbooks, and patents from before
    1973 have not been searched.

  Moore & Lawrence 1980, and Hansen's other pre-1974 detection papers, are not on the shelf either.
  Under the 2026-09-14 ruling none of this is being pursued unless Tony says so.
