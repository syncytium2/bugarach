GRANT 7 ok — Read, Grep, Glob, Bash

**Reuse auditor (role 7): findings**

Format for each: location · issue · severity · suggested fix · verifiable against a source

---

**1.** `<darkroom>/bugarach/detector_history.html` (the darkroom copy, dated Aug 29) · The HTML was rebuilt only into the repo copy (`--out docs/learned`). The darkroom copy is the one a person opens (CLAUDE.md, FOUNDATIONS §5), and it still says `GO-CFAR (Hansen 1973)`, the exact claim this change withdraws. The tool's default destination does matter here: `tools/md_to_page.py` sends output to `darkroom()` unless told otherwise and takes `--also` for the repo copy, and a darkroom copy of this page already exists. I rebuilt to the scratchpad and the result is byte-identical to the committed `docs/learned/detector_history.html`, so the tool was used correctly. Only the destination is incomplete. · **major** · Once merged, claim the darkroom on the board and run `python tools/md_to_page.py docs/detector_history.md --also docs/learned` (default destination is the darkroom). Record the redeploy in the run record. · yes (grep of the darkroom file; `cmp` of the rebuild)

**2.** `docs/proposals/2026-09-10-coordination-without-labels.html:848` · A tree-wide copy of the old claim remains. The footer's "Detector lineage acknowledged" line credits *"the constant-false-alarm-rate family from the radar literature (Finn & Johnson 1968; Hansen 1973; Rohling 1983)"*. It is a public page in the repo, and INDEX.md and a handoff link to it. The diff does not touch it. · **major** · Either replace "Hansen 1973" with "Hansen & Sawyers 1980", or keep the dated proposal frozen and add a dated ⚠ note saying the origin is not established, pointing at §4 *Where greatest-of began*. Whichever you choose, write the choice down so the next grep doesn't raise it again. · yes

**3.** `<darkroom>/bugarach/2026-09-07-pilot-apv-cnqx-gz/REPORT.md:644` · A second copy outside the repo: *"LoCo's local maximum is greatest-of CFAR: Hansen V.G. (1973) … IEE Conf. Publ. 105, 325–332."* It is darkroom-only (not public) and hand-written, so no tool regenerates it. · minor · Add a one-line dated correction pointing at §4, or record it as a known stale copy in the follow-ups. · yes

**4.** `docs/detector_history.md` §4, *Where greatest-of began* (the Proc. IEE notice paragraph) · The text describes evidence that already sits on the shelf but doesn't name the files. The *Proc. IEE* 120(11) p. 1391 notice with ISBN 0 85296 114 6 is `<darkroom>/bugarach/lit/radar/iee_conf_105_1973_CONTENTS_ONLY.pdf` (confirmed with pdftotext). The author record is `gregers_hansen_AUTHOR_PROFILE_ieee.pdf`. The shelf's own `README.md` (Aug 22) has no entry for either, which breaks its rule of a read-status entry per work. It still says "two verified bibliographically but not read" and "two outstanding library orders", and §8 of the doc repeats the second phrase. So the doc now holds a second description of evidence that the shelf index does not record. · minor · Name the two shelf files in the §4 paragraph and add entries for them to the shelf README, so there is one registry. Correct the stale "two outstanding library orders" wording in §8 and the shelf README. · yes

**5.** README.md cite block, GLOSSARY.md CFAR paragraph, `docs/learned/cfar_scope.html` (table row and `VARIANTS` cite), `detector_history.md` lines 205 and 997 · "Origin not established" now appears in 6 places outside the canonical passage. Each one points back at §4, which limits drift. But README also repeats the withdrawn citation's details and the H&S DOI, and GLOSSARY repeats the shelf read dates. When the 1973 paper is finally read, all six must change together, and nothing checks that they do. · minor · Keep the pointers and drop the repeated bibliographic detail from README and GLOSSARY, leaving it only in §4. Also add `greatest-of, GO-CFAR, Hansen 1973, origin` to the keywords of `docs/INDEX.md` row 87, so the next lookup finds §4 rather than a copy. · yes

**6.** `docs/detector_history.md:474-479` (claim about how quotations are checked) · The new text says quotes are hand-checked against `pdftotext -layout` and that `verify_quotes.py` "traces some… not yet a gate". That matches the tool's own docstring. I ran it: 15 of 62 quotations traced. Of the 9 new quotes in §4, 5 traced and 4 missed. I hand-checked the 3 misses that come from shelf papers against `pdftotext -layout`: H&S *"based on a simplified analysis…"*, Rohling *"Moore et al. [3] proposed a different estimation method…"*, and G&K *"Hansen [9] has proposed…"*. All three are genuine; the misses come from column and line breaks. The 4th miss is the patent quote, which is off the shelf and cannot match, as the text says. **This is not a defect; it is what I checked.** A small inaccuracy follows from it: the traced title quote matched G&K's reference list, which prints it unhyphenated. The hyphenated form §4 quotes comes from the IEE contents PDF. · minor · Say which source the title quote is taken from (the IEE notice). Optional: the tool's docstring figure "11 of 30" is stale (it now traces 15 of 62). That wording predates this change. · yes

---

**What I checked and found clean**

- **Repo grep for the old claim:** searched `Hansen 1973`, `GO-CFAR (Hansen`, `Conf. Publ. 105`, `usually credited`, and greatest-of wording near origin/proposed/introduced/first, everywhere except `docs/reviews/` and `docs/todo/`.
  - `src/`, `tools/`, `tests/` and `docs/site/` have no Hansen or greatest-of attribution.
  - `docs/forks.md` and `docs/exports/…attribution.md` mention only Hansen & Sawyers or GO-CFAR in general.
  - The handoff lists the 1973 paper as outstanding, not as the origin.
- **`cfar_scope.html`:** it has no generator (only `cfar_scope_check.js` reads it), so editing it by hand is the project's normal way to change it. `node docs/learned/cfar_scope_check.js` exits 0 after the cite edit. There is no darkroom copy.
- **Site build:** `tools/build_site.py` does not republish README, detector_history or cfar_scope.
- **Tests:** `tests/test_index_resolves.py` and `tests/test_check_quotes.py` pass (238 passed).

Files: `<worktree>\docs\proposals\2026-09-10-coordination-without-labels.html`, `<darkroom>\bugarach\detector_history.html`, `<darkroom>\bugarach\2026-09-07-pilot-apv-cnqx-gz\REPORT.md`, `<darkroom>\bugarach\lit\radar\README.md`, `<worktree>\tools\md_to_page.py`, `<worktree>\docs\INDEX.md`
