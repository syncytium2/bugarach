---
status: open
opened: 2026-08-30
owner: unassigned
---

# The landscape page is withheld from the public build, and here is what it owes before it comes back

Tony, 2026-08-30, going through the site page by page: *"suppress landscape page
until we can update it. many changes to incorporate. way too long."*

Done in the same pass. `landscape.html` is out of `build_site.PAGES`, out of
`STATUS`, out of `PUBLISHED` (which derives from `PAGES`), and the copy step that
published it is gone. The three inbound links went with it — the index's *"full
landscape →"* line and two on the learned-detector page.

**Withheld, not deleted.** `docs/learned/landscape.html` and
`docs/learned/landscape.src.html` are untouched in the tree, and
`docs/learned/next_stage.md` and `README_for_the_webapp.md` still link to them by
relative in-repo path, which still resolves. Restoring the page is three lines and
a copy step.

## Why withheld rather than unlisted

`nav_html` and `status_html` both key off `PAGES`. A page dropped from that tuple
while still being *shipped* arrives with no nav bar and no draft banner — a dead
end on a public site, which is the exact defect `nav_html`'s own docstring records
having fixed. There is no halfway. The precedent for taking something out of the
public build entirely is `487fbc9`, which withheld the sixth detector, name and
all.

## What it owes before it returns

1. **Length.** Tony's first complaint. Six `<h2>` sections and 303 source lines,
   written when it was the only page carrying the project's position. It is no
   longer: the learned-detector page now does the *"what does this entitle us to
   claim"* work for the model, which was section 2's job here.
2. **The changes it has not incorporated.** It was last built before the fitted
   background, the tolerance move from 1.5 s to 2.5 s, the bake-off rerun, and
   locust's withholding from the public build. Any number on it should be assumed
   stale until checked against the store that produced it.
3. **A detector-count audit.** Same trap as the front page (below): the page was
   written when the answer was six, and the public build now ships five. Whatever
   replaces it should not state a count it cannot derive.
4. **A decision about whether it is one page.** Section 3 is a measured comparison
   against neighbouring methods; section 5 is a limits statement. Those have
   different half-lives and the second is the one other pages keep needing to cite.

## The dependency this block used to claim, which did not exist

`build_site`'s comment justifying the copy said the page "has to travel" because
*"the coordination report's retraction points at it too — a relative href to a
file that was not shipped is a dead end where the correction should be."*

Checked before acting on it: `coordination_report.src.html` and
`coordination_report.html` contain the string `landscape` **zero** times. The
dependency was not real. Recorded here rather than quietly dropped, because a
comment asserting that a file is load-bearing — and naming a dependent that does
not depend on it — is how a later session ends up keeping something for a reason
nobody can retest.

## Related

- The front page's detector count was threaded through seven reader-facing strings
  and four of them disagreed (`<h1>` six, next paragraph five, three paragraphs on
  six again). Tony's instruction there was *"maybe just rewrite the text so it is
  independent of how many detectors are currently enabled?"* — parked, not done,
  because the front-page copy is also where a possible recall-led rewrite lands and
  the two want the same paragraphs.
- Nothing here is deployed. The site build and the live site are held while
  `bench-background-is-not-flat` is undecided; landing it re-quotes roughly four
  published numbers.
