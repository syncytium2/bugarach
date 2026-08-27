# Murderboard run — the site's status banners

## The problem

The site is public and the work is not finished, and until now the pages said
neither (Tony, 2026-08-27). A page that carries no status reads as done, so the
site was making a claim about how finished the work is — by omission, on four
pages at once, two of which a stranger points at their own data.

Concept pages (Overview, Landscape) now carry **DRAFT**; the pipeline pages
(Raster viewer, Detector diagnostic) carry **⚠ UNDER CONSTRUCTION**. Both the
split and the full-width-bar prominence are Tony's calls, recorded because they
are public claims about the maturity of somebody's work.

## What was found

**One page got no banner at all, and it was one of the two that most needed it.**
The banner rides with the nav, so every page that gets a nav gets a label — except
`viewer.html`, which ships its own hand-written nav, so `add_nav` short-circuits
and never reaches it. The viewer is published **byte-for-byte** from
`docs/site/raster_viewer.html` and `tests/test_lab_server.py` pins that on purpose:
the page promises the reader it makes no network call, and a build that could
rewrite it could break the promise. So its nav, its date stamp and now its status
bar are all hand-written in the source, and a new test checks the bar against
`build_site.BANNERS` so the hand-written copy cannot drift from the constant.

This was caught by the test written alongside the change, not by looking at the
page — which is the argument for writing it that way round. A silent unlabelled
page is exactly the defect the banners exist to prevent.

## What would validate it, and where it generalises

Three tests: every page in `PAGES` has a `STATUS` entry, every *built* page carries
the banner its status names, and rebuilding does not stack two. A fifth page cannot
ship unlabelled by being forgotten.

The generalisation: **"it travels with the nav" is only true of pages the build
composes.** One page here is copied rather than composed, and that exemption —
correct, deliberate, and documented — is invisible from the injection site. Any
future site-wide chrome has the same hole in the same place.

---

## Appendix — run record

- upstream:  syncytium2/murderboard @ 73dad04
- copy:      vendored @ 73dad04
- freshness: current
- artifact:  `site/{index,viewer,diagnostic,landscape}.html`, all four rendered and
             inspected in light and dark
- roles:     11 of 11 run (single-pass, per the size rule: two sentences and two
             badges, with no attribution or novelty claim, so the role-2 exception
             does not apply)
- rounds:    2 blind verify rounds to clean

### Role ledger

| # | Role | Findings |
| --- | --- | --- |
| 1 | Claim & data verifier — "Prove It." | 0. Both sentences are checkable and modest. "Its claims are still moving" is true of the two pages it appears on — the landscape's own standfirst records a claim withdrawn after reading. "Live software still being built" is true of the viewer and the diagnostic. No numbers are asserted. |
| 2 | Citation & reference validator — "DOI or Die." | 0, and here is what was checked: the banner text contains no citation, DOI, attribution or external reference of any kind. The size rule's attribution exception therefore does not bite. |
| 3 | Consistency auditor — "Cross-Examiner." | 0 unresolved. Checked DRAFT against the front page's own "the training half is the plan, not yet the practice" — consistent. Checked ⚠ against the viewer's central promise, *"your files never leave this computer"*: a reader could in principle read "behaviour that changes without notice" as undercutting it. Adjudicated **no change** — the promise is mechanically enforced (the build refuses to publish a viewer containing `fetch`, and `audit_deployed_page.py` drives the live page), and narrowing the banner would weaken the warning that was asked for. |
| 4 | Adversarial reviewer — "Reviewer 2." | 0. A hostile reader takes "under construction" on a portfolio site as unfinished. That is the intended reading and the reason the change exists. |
| 5 | Line editor — "Kill Your Darlings." | 0 new. Both sentences are one line; "Read it as a position, not a result" earns its place by telling the reader what to *do*, which the badge alone does not. |
| 6 | Methods / domain expert — "RTFM." | 0. The concept/pipeline split is not derivable from the tree — it was asked for and recorded, in `STATUS`'s docstring and on the session board, with the date and the person. |
| 7 | Reuse auditor — "Reinventing the Wheel." | 0, and here is what was checked: no new analysis code. `STATUS` keys off the existing `PAGES` tuple rather than restating the page list, which is the same rule the nav, the manifest and the coherence tests already follow. The banner is injected through the existing `nav_html`, not a second injection path. |
| 8 | Naive-reader accessibility — "You Lost Me." | 0. Badge says what state the page is in, sentence says what that means for the reader in front of it. `role="note"` on the bar so it is announced rather than read as decoration. |
| 9 | Density & figure-first — "Show, Don't Tell." | 0. Chrome, not content; nothing here needs a figure. All four banners were rendered and looked at rather than reasoned about. |
| 10 | Build & craft gate — "Ship It." | **2.** (a) `viewer.html` received no banner — see above; fixed in the source page and pinned by a test. (b) Editing the viewer required bumping its `data-bugarach-version-date` *and* its `bugarach:version-date` meta *and* the visible "this version" line; the existing date tests caught all three. Rendered every page in both colour schemes: one banner each, visible, correct variant, no stacking, no horizontal overflow. The viewer's bar is flush-left where the other three indent to the text column — correct, because it matches that page's own full-width nav. |
| 11 | Argument order — "Start With the Problem." | 0. Badge first, consequence second, and the bar sits above the nav so it is met before anything else on the page. |

### Residual ⚠

1. **The diagnostic page stays light in dark mode** (Bokeh renders its own white
   background), so its dark banner sits above a white page. Pre-existing and not
   introduced here; noted because the banner is the first place it is visible.
