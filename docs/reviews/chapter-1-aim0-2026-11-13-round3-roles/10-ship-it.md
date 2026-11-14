I checked the figures for reproducibility, legibility and production quality. I edited nothing: the repo is frozen during the review round, `git status` is unchanged, and everything I regenerated went to scratch only.

**Reproducibility: passes for the 13 figures with scripts in docs/dissertation/figures/**
- I re-ran `ch1_new_figures.py` (10 figures) and `ch1_intro_figures.py` (3 figures) from HEAD f8e4d8c0 into scratch. Every PNG matches the committed file pixel for pixel (0 differing pixels).
- The numbers `ch1_intro_figures.py` prints still match Table 1.1 and the CFAR figures in the text, for example 5 false alarms in 200 min, chance hit 0.21 / 0.34 / 0.01, and HWHM 0.177 / 0.821 s.
- I did not re-run the six figures from docs/learned/synthetic_validation (`aim0_figures.py`, `aim1_figure.py`, `separation/floor/bound.py`, `separation/assessor_split/split.py`). They were rendered 2026-10-29. Their inputs have not changed since, apart from real-data paths in `tools/measure_coordination_rates.py` and `tools/measure_jitter_correlogram.py`, which the synthetic figures do not use.

**Defects visible in the figures**
1. **Fig 1.2:** the x-label "time" collides with the "false alarm" legend entry.
2. **Fig 1.10:** the row titles run over panel letters B and D ("slow" sits on B, "events" on D).
3. **Fig 1.3, enlargements B and C:** the 2 s and 4 s window bars are clipped at the +1.5 s axis edge, and the "10" labels in C's 2 s and 4 s rows and B's 4 s row are cut off.
4. **Fig 1.2 colours:** found, missed and false alarm are told apart by colour alone; every mark is the same ▼. Under simulated colour-blindness the contrast is weak:
   - found against missed: ΔE 26 (deutan), 20 (protan)
   - missed against false alarm: ΔE 28 (deutan)
   An open marker for "missed" or a different shape would fix it.
5. **Fig 1.4 C:** the dashed chance line at 1 and the dotted settle-levels the caption describes are hidden under the data points.
6. **Fig 1.7 B:** the legend says "full prediction" but the caption says "Yellow dashes are the hard-core form". Use one term. The yellow dashes also crowd the markers.

**Caption and text**
7. **Fig 1.10 caption:** a parenthesis is never closed: "A, B: one event per mean interval (25.5 and 53.6 events per recording; C, D: …".
8. **Table 1.1 in the PDF (p. 7):** the column headers wrap to 5–6 lines and cells such as "1.00 (0.21 by chance)" or "1.82 per min (364 in 200 min)" to 3–4. Shorter headers, putting the "(… by chance)" counts in a note, or a landscape page would fix it.

**Type size is uneven across the chapter**
- The intro figures are drawn about 7 in wide at 9–10 pt, so they print at roughly 8–9 pt.
- `ch1_new_figures.py` draws at 12 pt (ticks 11) on 10–11 in canvases (1500–1650 px at 150 dpi). At a 6.5 in text width that prints at about 7 pt, with ticks near 6.5 pt.
- The learned-folder figures are 11–12 in at 12 pt, which is the same problem.
- The fix is to draw these generators at about 7 in, as the intro script already does.

**Minor**
- The PNG Title metadata of the learned figures still carries the old numbering, for example "Figure 1, recovery against planted jitter (Aim 1a)" and "Figure 6, …". It is not visible on the page.
- The README's draft captions use round-3 numbering. The README already says the chapter is authoritative.
- PDF pages 44 and 46 each have one line about 0.05 in past the right margin. It is not noticeable on the page.

Everything is in <scratch>\mb3\role10\ — the regenerated figures in `regen_new` and `regen_intro`, the zoom crops (`c12_bottom.png`, `c110_top.png`, `c110_mid.png`, `c13_right.png`, `c14_C.png`, `c17_B.png`, `p07.png`), and the check scripts in `scripts\` (`cmp.py`, `cvd.py`, `overflow.py`).
