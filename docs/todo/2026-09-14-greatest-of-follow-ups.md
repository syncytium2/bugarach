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
  - HathiTrust record 001618382 is a search-only scan of a US university library's copy of
    Conf. Publ. 105 (item `mdp.39015000988512`). Its full-text search could show whether the
    paper uses "greatest" or "split" at all, and that library's print copy could be requested.
    Is either wanted?
  - The notice's ISBN (0 85296 114 6) and the catalogue's (0 85296 112 X) disagree, so any
    library request should use the HathiTrust record.

  Moore & Lawrence 1980, and Hansen's other pre-1974 detection papers, are not on the shelf either.
  Under the 2026-09-14 ruling none of this is being pursued unless Tony says so.
