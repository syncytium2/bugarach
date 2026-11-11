# The minimum separation of two events (2026-10-25)

Tony, 2026-10-25: can the analytical approach determine the minimum separation of events we can
detect, and which parameters of the data set it? Three derivations answer it, each checked by
simulation. The goal page's section is *Aim 0, the minimum separation of two events*; the human
raters' curve is the rater sheet's separation test (PR #916).

| folder | question | result at the lab's parameters |
|---|---|---|
| `floor/` | the smallest separation **any method** could resolve from onset times and cell identity | 0.26–0.76 s at 80 % power and 5 % false alarm (σ 0.105–0.131 s, 7–13 of 33 cells, 0.0096 Hz). Jitter sets it; the 0.1 s frame does not bind |
| `assessor_split/` | the chance the **assessor** and the **count detector** report a pair as two | half the plateau at about 2.5 s (assessor) and 5 s (count detector): (merge rule + ½) × bin width, almost independent of σ, k, b and K. The data set only the plateau, f² (f the chance one event reaches K) |
| `real_intervals/` | the **coordination-rates prediction** when events can share a window | the shift surrogates still see the events' spacing (most of Aim 1a's rate excess); on real fast-stream gaps the page's form overstates rate about 13 % at the 4 s window and the joint fit reads jitter 1.5–1.65× high. A general form fixes both |

Each folder holds `derivation.md`, the script, its printed output, its results JSON and the
figure. Run the scripts from the repository root with `PYTHONPATH=src`:
- `split.py`: `--plot-only` redraws; a full run takes about 25 min on 44 workers.
- `intervals.py`: `--figure-only` redraws.
- `bound.py`: `--figure` redraws; a full run takes about 80 min on 24 cores.

**Checked independently** in the session that ran the agents:
- **The assessor's split rate.** Re-simulated with the shipped `assess._clusters` on freshly
  planted pairs, it matched the prediction within about 1–2 SE. Examples: 0.90 ± 0.01 against 0.91
  at σ = 0.105 s and Δ = 3 s; 0.55 ± 0.02 against 0.57 at σ = 0.5 s and Δ = 3 s.
- **The real-gap error.** Re-simulated with the shipped coordination-rates tool on renewal trains
  drawn from the fast stream's real gaps (24 recordings, 13 of 33 cells, σ = 0.105 s), the 4 s
  window measured rate 1.03 and participants 0.96 of planted. The page's form predicted 1.17 and
  0.89, as the agent found.

**Caveats.**
- `gaps.csv` merged events under 2 s apart, so its short tail is censored, and the real-interval
  effect at the 1–2 s windows is a lower bound.
- On real data the event rate is not one over the mean gap, which needs the Palm form. Not
  tested.
- The floor's likelihood-ratio tests are attainable, not proven optimal. Its entries marked †
  (wide jitter, few cells, background) run anti-conservative.
- The floor figure's panel letters are lower case (a–d), unlike the house style.
