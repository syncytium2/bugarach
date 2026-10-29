GRANT 10 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__{batch,update,guide}, plus deferred NotebookEdit and other MCP tools (a fallback grant). I used only Read, Grep, Glob and Bash, and wrote only in my scratch folder. This mismatch is a finding about the run: the `roles:` line has to say this review took a fallback path.

# Role 10 — Ship It: build and craft gate for Chapter 1 (Aim 0)

**Artifact:** `docs/dissertation/chapter-1-aim0.md`, hash-object a3d06b0468b8165c09ad294df82ca56abc381a29 (confirmed).

**How it was rendered.** The full markdown went through GitHub's own renderer (`gh api POST /markdown`). The output was wrapped in github-markdown-css 5.5.1 at GitHub's 1012 px content width. Chromium (Playwright from `venvs/surrogate-screen`) captured it as a full-page screenshot and ten 1800 px slices, and each figure was captured as an element.
- **Rendered:** the whole page, 17,133 px tall. All six images loaded (`complete`, natural sizes read). All three tables fit their column (scrollWidth equals clientWidth). At 390 px phone width there is no horizontal scroll.
- **Not rendered:**
  - the live github.com page chrome;
  - relative links inside the published repo, which I checked on the filesystem instead;
  - mermaid and math, because the chapter uses neither.

All renders are in `<scratchpad>\mb\work-10\`:
- `full.png` (whole page)
- `page_01.png` to `page_10.png` (slices)
- `img1.png` to `img6.png` (each figure as rendered)
- `z11_D.png`, `z12_FG.png`, `z12_G.png`, `z16_a.png` (2–3× zoom crops of the source PNGs)
- `r15_legend.png`, `r16_a.png` (crops at rendered size)

**Links and image paths.** All 18 relative links in the chapter resolve, including all six image paths.

**Build currency.**
- Figs 1.1–1.4 were built 2026-10-24 01:34 by `aim1_figure.py` / `aim0_figures.py`. Their inputs (`aim1_one_source.json`, `theory_check.json`, `membership_limit.json`, `order_limit.json`) have not changed since.
- `theory.py`, `event_train.py` and `measure_coordination_rates.py` changed on 10-28 (f168f5b0). That commit states the no-train output is byte-identical, so Fig 1.1's joint fit stands.
- Figs 1.5–1.6 were built at 8acd9c3a. `split.py`'s later edit (eadc0904) only renames variables; no plotted label changed.
- **One exception:** the Fig 1.4 PNG predates the derivation that its text relies on (row F4 below).

**Figure numbering.**
- Figures 1.1–1.6 and Tables 1.1–1.2 are numbered in sequence. Section cross-references (1.3.5, 1.6, 1.9, "1.10, Limitations") all resolve.
- Only Figure 1.1 is cited in the prose (D and H, lines 307–308). Figures 1.2–1.6 are never cited by number outside their own captions.

## Table: one row per section or figure

| # | Unit | Checked against | Rendered box (px; share of 1012 px column; scale from native) | Result | Findings (severity) |
|---|---|---|---|---|---|
| S0 | Title + exercise blockquote | page_01.png | — | pass | Links resolve. |
| S1 | 1.1 Introduction, Contributions | page_01–02 | — | pass | Unicode k̂, g₃/g₂ render. Plain `g_n`, `(k)_r`, `R_n` show as literal underscores next to Unicode subscripts, an inconsistent notation (minor). |
| S2 | 1.2 Background, Table 1.1 | page_02 | table 841 px | pass | Table renders and fits. |
| S3 | **1.3.2 expected excess counts** | **page_03.png** | — | **FAIL** | **Lines 207–208 (f₂ and f₃) are one paragraph, so GitHub runs them together on one line: "f₂ = p (k)₂ g₂ − (pk)² (1 − 1/N) f₃ = p (k)₃ g₃ − …". The two equations read as one (major).** Fix: a blank line between them, or a fenced/indented block. |
| S3b | 1.3.1, 1.3.3, 1.4 display equations | page_03 | — | minor | The two-space "display" lines render as ordinary left-aligned paragraphs, not set off as equations (minor). |
| S4 | 1.5 text, 1.6 text, Table 1.2 | page_04–06 | Table 1.2 688 px | pass | Table renders. |
| S5 | 1.7, 1.8, 1.9 table, 1.10–1.11, References | page_07–10 | 1.9 table 922 px | pass | Table fits, links resolve. |
| F1 | **Figure 1.1** (`synth_recovery_plot_one-source-jitter_20261023.png`) | native PNG; z11_D.png; img1.png | 922×561; 100% of column; 0.57× | **FAIL (1 major, 1 minor)** | • **Panel D: the pink K = 4 assessor series is completely hidden under the green K = 6 series and the violet joint fit (zoom z11_D). Yet line 307 cites "K = 4 … 0.07, 0.23, 0.49, 0.72 s (Figure 1.1 D)", so a reader cannot find the cited values in the panel (major).** Fix: dodge markers horizontally as panels A–C do, or cite K = 6. • The caption says "(top)" and "(bottom)" for the rows; use the panel letters (A–D, E–H) instead (minor). • Checked and passing: axes carry name and units; panel letters A–H; the IQR glyph and dotted identity line are in the legend; y-limits are shared across A–C/E–G (and across D/H); colors are distinguishable through marker and line-style redundancy. |
| F2 | **Figure 1.2** (`…predicted-against-measured_20261023.png`) | native; z12_FG.png, z12_G.png; img2.png | 922×525; 100%; 0.55× | **FAIL (minor)** | • Panel F: the annotation "2 above, 1 below" is printed over data (a 5-cell triangle and a grey point at about (1.0, 0.5)). In G, "1 above" nearly touches a triangle. Move the annotations to an empty corner (minor). • Checked and passing: axes named and dimensionless, or per minute in D/H; A–C and E–G share y; every marker is in the legend; D/H use log axes with the identity line legended. |
| F3 | **Figure 1.3** (`synth_assembly-membership_…_20261023.png`) | native; img3.png | 922×386; 100%; 0.64× | minor ×3 | • The caption lists "both reject in 1 of 60 and either in 3 of 60 (dashed and dotted lines)". In that order, "both" is matched to dashed, but the legend has dashed = either (5%) and dotted = both (2%). Reorder to "(dotted and dashed)" (minor). • The on-figure note "M = 1 (rightmost)" uses a spatial word; label the point itself (minor). • The caption gives "M from 1 to 10 000" while the x-axis is E/M; state it as the E/M range 0.0045–45 (minor). • Checked and passing: axes named, the percentage base stated, lines legended. |
| F4 | **Figure 1.4** (`synth_recovery_plot_order-indicator-closed-forms_20261023.png`) | native; page_06.png; git log | 922×340; 100%; 0.55× | **FAIL — stale (major)** | • **Panel C labels the score-sort line "fitted 0.38/√n̄". The text (lines 428–430) says the constant is exact, 0.376, "with nothing fitted". The PNG (Creation Time 2026-10-24 01:28) predates the derivation commit `kendall_w/derivation.md` (28d9c5f4, 2026-10-24 15:01). The figure was never rebuilt, and `aim0_figures.py:225` still writes "fitted" (major).** Fix: rebuild with the closed-form c(N, k) line, labeled as predicted, and keep "fitted" only for the local search. • The caption "C: no order planted, under both sorts" does not say what the lines are (minor). • The closed-form line is blue in A and B but orange in C, so one concept has two glyphs (minor). • Checked and passing: shared y-limits across A–C; axes named; legends present. |
| F5 | **Figure 1.5** (`separation/assessor_split/…_20261025.png`) | native; r15_legend.png; img5.png | 922×521; 100%; **0.36×** | **FAIL (1 major, 2 minor)** | • **Rendered at 36% of native size, the legend, axis labels and panel subtitles are about 5 px tall (r15_legend.png) and unreadable on the GitHub page unless the image is clicked open (major).** Fix: re-export near 1000 px wide with larger fonts, or split A–D from E–H. • The axis labels "centre to centre" break the house rule's American spelling (`writing_conventions.md:144`) (minor). • The legend writes "+-1" and ">= 20" in ASCII (minor). • Checked and passing: y is shared at 0–1; panel letters A–H; dotted and dash-dot reference lines are legended; filled and open glyphs are explained. |
| F6 | **Figure 1.6** (`separation/floor/…_20261025.png`) | native; z16_a.png; r16_a.png; img6.png; `bound.py` | 922×358; 100%; **0.36×** | **FAIL (3 major, 3 minor)** | • **Unexplained clipped values: orange and green series drop to a flat line at about 0.035 s. `bound.py:753` clamps "'any' (resolves at every separation tested) drawn at the floor", but nothing on the figure or in the caption says so. They read as measured values of 0.035 s (major).** • **The reference labels "unimodal below 2σ = 0.21 s" and "frame 0.1 s" in panel a are struck through by the green line and the dark diamond line and marker (z16_a); the same happens to "frame 0.1 s" in b (major).** • **At 0.36× the reference-line labels and legend are about 4 px tall (r16_a), which is illegible (major).** • The figure draws "assessor floor 3 s" (hardcoded at `bound.py:767`), while §1.7 says the assessor splits at about 2.5 s. The figure and text disagree; I defer the value to the numbers roles (minor here). • Panels are lettered a–d in lowercase (caption "(a–c)", "Panel d") while every other figure uses uppercase (minor). • "centres" in the panel d axis label (minor). • Checked and passing: a–c share y; all series legended; the d legend is adjacent to d. |
| P | PNG document properties | PIL `im.info` | — | minor | • Figs 1.5 and 1.6 carry no Title, Author or Creation Time. • Figs 1.1–1.4 carry the titles "Figure 1"–"Figure 4" (the goal page's numbering), not 1.1–1.4 (minor). |
| A | Image alt text | gh_body.html | — | minor | All six alt texts are just "Figure 1.x" with no description (minor). |

## Structured findings (location · issue · severity · fix · verified)

1. **§1.3.2, lines 207–208.** "f₂ = … f₃ = …" merges into one rendered line. Severity: major. Fix: separate the lines or use a code/indented block. Verified: yes (page_03.png).
2. **Fig 1.4 C.** "fitted 0.38/√n̄" contradicts "with nothing fitted". The PNG predates the derivation. Severity: major. Fix: regenerate from the closed form. Verified: yes (git log, `aim0_figures.py:225`).
3. **Fig 1.1 D, and line 307.** The K = 4 series cited in the text is invisible under K = 6 and the joint fit. Severity: major. Fix: dodge the markers or change the citation. Verified: yes (z11_D.png).
4. **Fig 1.6 a–c.** Values clamped to 0.035 s are drawn with no explanation. Severity: major. Fix: mark them with a distinct "resolves at all Δ tested" glyph and a legend entry. Verified: yes (`bound.py:753`).
5. **Fig 1.6 a and b.** Reference-line labels are overprinted by data. Severity: major. Fix: move the labels to the left margin or to the right outside the axes. Verified: yes (z16_a.png).
6. **Figs 1.5 and 1.6.** Rendered at 36% scale, the text is about 4–5 px tall and illegible at page width. Severity: major. Fix: re-export with larger fonts or split each figure. Verified: yes (r15_legend.png, r16_a.png).
7. **Fig 1.2 F.** The annotation overlaps data. Severity: minor. Verified: yes (z12_FG.png).
8. **Fig 1.3 caption.** The dashed/dotted order is reversed against the legend. Severity: minor. Verified: yes.
9. **Fig 1.1 caption ("top"/"bottom") and Fig 1.3 ("rightmost").** Spatial words where panel letters should be. Severity: minor. Verified: yes.
10. **Fig 1.6.** Lowercase panel letters, inconsistent with the other figures. Severity: minor. Verified: yes.
11. **Figs 1.5 and 1.6.** British "centre(s)" in axis labels. Severity: minor. Verified: yes (house rule).
12. **Fig 1.6 against §1.7.** "assessor floor 3 s" against "about 2.5 s". Severity: minor here; refer to the numbers roles. Verified: yes (`bound.py:767`).
13. **Fig 1.4.** The closed-form line changes color between panels. Severity: minor. Verified: yes.
14. **Figs 1.2–1.6.** Never cited by number in the prose. Severity: minor. Verified: yes (grep).
15. **Notation, all sections.** `g_n`, `(k)_r` and `R_n` render as literal underscores beside Unicode subscripts. Severity: minor. Verified: yes (page_03.png).
16. **PNG metadata and alt text.** Missing or stale. Severity: minor. Verified: yes.

## Figure size on the page (not a defect in itself)

Every figure is placed at the full 922 px image width inside the 1012 px column, and none has empty margins beside it. Whether Figs 1.5 and 1.6 should be split for a larger rendered size is agent 9's call. Their legibility at the current size is finding 6.

---
*Archivist's note (main thread, 2026-10-29): for this public repository (sapper SAP004), the session scratch folder's absolute path became `<scratchpad>/`. Nothing else in the report was changed by this pass.*
