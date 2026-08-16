# Murderboard run — docs/learned/report.html
- upstream:  syncytium2/murderboard @ f43a07b
- vendored:  f43a07b
- freshness: current
- artifact:  docs/learned/report.html (163993c -> a11011a -> 4b4d723, rebuilt after the last fix)
- roles:     11 of 11 run
- rounds:    2 (round 1 on the original page; round 2 after the finding changed)

Single-pass self-review walking every role's checklist in turn. Every role ran;
what scaled was how, not which.

**The artifact is the built page, not its source.** `report.src.html` +
`architecture.svg` are inputs; `tools/build_learned_report.py` inlines the figures
as data URIs and produces `report.html`, which is what was reviewed and what
ships. Every fix below was applied to the source and the page **rebuilt before
re-inspection** — the hash moved three times and the final render post-dates the
final fix.

---

## Role ledger

| # | role | findings | outcome |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | **1 major** | fixed (see below) |
| 2 | Citation & reference validator — "DOI or Die." | 0 | no findings — the page cites no papers, DOIs or external attributions. Its only references are internal (PR #52, `tools/make_learned_figures.py`); both exist and are correctly named. Nothing to verify against a bibliography. |
| 3 | Consistency auditor — "Cross-Examiner." | **2** | both fixed |
| 4 | Adversarial reviewer — "Reviewer 2." | **2** | both fixed |
| 5 | Line editor — "Kill Your Darlings." | **1** | fixed |
| 6 | Methods / domain expert — "RTFM." | 0 | no findings — checked the three method claims against the code that produced them: receptive field (2 078 samples, matches `receptive_field(4)+receptive_field(10)`), the circular-shift null as described in `assess.py`, and the pos_weight arithmetic quoted in the next-steps list. All correct as stated. |
| 7 | Reuse auditor — "Reinventing the Wheel." | 0 | no findings — the figure script calls `bugarach.bench`, `bugarach.assess` and `bugarach.score` rather than recomputing scores, and the report builder reuses `make_generator_figures._write`. No metric is re-derived in the tooling. |
| 8 | Naive-reader accessibility — "You Lost Me." | **2** | both fixed |
| 9 | Density & figure-first — "Show, Don't Tell." | 0 | no findings — 3 rendered figures plus a purpose-built schematic across ~2 000 words, and the two claims that are hardest in prose (the four-stage signal path, the flat loss curve) are both pictures. The one list left as prose is "what is ruled out", which is four negatives and has no figure form. |
| 10 | Build & craft gate — "Ship It." | **3** | all fixed |
| 11 | Argument order — "Start With the Problem." | **1** | fixed |

---

## Findings

### Role 1 — Prove It (1, major)

**Every quoted number was recomputed against `learned_results.json`, and one class
of them was wrong.** The draft carried **CoactDetect 0.66 as the best of six**.
That came from a **2-seed** run; the bench's canonical three seeds give different
values *and a different leader* — RateDetect 0.64, CoactDetect 0.63, LoCo 0.63,
CICADA 0.56, spike-sync 0.51, SCE 0.36.

The wrong figure had already propagated into
`docs/todo/2026-08-16-learned-detector-does-not-converge.md`, which was corrected
in the same pass with a note recording what changed and why.

Ledger of the rest, all confirmed against the cached results or the code:

| quoted | recomputed | verdict |
|---|---|---|
| learned F1 0.12 / 0.15, recall 0.07 / 0.09 | as quoted | match |
| 2 393 / 2 065 parameters | `n_params` | match |
| receptive field "about 2 000 samples" | 2 078 | match |
| event "about four samples" at our rate; "eleven" at 30 Hz | 3.6 / 10.8 | match |
| positives "0.5% of frames" | 135 of 26 922 | match |
| single crop reaches "0.75 confidence", loss halves | 0.751; 1.395 -> 0.677 | match |
| participants 7 vs planted 5.9 at K=4 | as quoted | match |
| tightness "~9% loose" | 0.394 vs 0.360 | match |
| frequency "within 7%" at K=4; "+60%" at K=3; "misses three quarters" at K=6 | −6.7% / +60% / −77% | match |
| `tiny` "fired three times in total" | 3 detections | match |

### Role 3 — Cross-Examiner (2)

1. **The prose said "cells" while every figure axis says "ROI".** Two vocabularies
   for one thing, and the reader has to guess they are the same. The plain word is
   right for a human-facing page, so it stays — but the equivalence is now stated
   once, at first use, rather than left to be inferred.
2. **The verdict strip and the table had to agree after the role-1 correction.**
   Re-checked cell by cell: strip 0.64 / 0.15, table rows RateDetect 0.64 and
   `trace` 0.15. Consistent, and the step chips match the sections they summarise.

### Role 4 — Reviewer 2 (2)

1. **"Best of the six" was over-precise on three seeds.** 0.64, 0.63 and 0.63 are
   not separable at n=3, and presenting a winner implies a resolution the data does
   not have. Restated as "top of the six — the leading three are tied within
   noise", with the point made explicit: *the gap that matters is to 0.15, not
   between the leaders.*
2. **"Mostly dissolves the standing objection" overstated what a per-lab loop
   does.** Fitting each lab's generator to its own recordings **moves** the
   domain-gap problem rather than answering it. Rewritten to say so — "a better
   place for it to sit, not a proof that it has closed."

Checked and clean: the one flattering number on the page (`tiny` precision 1.00)
is disclosed in the same caption as an artifact of three detections; the failure
claims rest on measurements rather than on the absence of a result; the footer
states plainly that nothing here rests on real data.

### Role 5 — Kill Your Darlings (1)

"The compute this design pays for" appeared in both the diagram label and the
paragraph directly beneath it. The caption was rewritten; the diagram keeps the
phrase, since that is where it earns its place.

### Role 8 — You Lost Me (2)

1. **"Planted truth" was used in the verdict footnote without definition**, and it
   carries the whole logic of the evaluation. Now glossed in place: *detections
   matched to the events the generator actually planted.*
2. **`baseline_busy` — an internal config name — appeared in audience-facing
   text.** Replaced with "the bench's busy regime", which is what it means.

Checked and clean: K is defined where it first appears (the round-trip caption);
every figure carries a caption saying what it shows and why it matters; no other
code identifiers appear outside `<code>` spans where they are being named as
things to run.

### Role 10 — Ship It (3)

Table, checked against the rendered page at 1100 px and 420 px, in both themes.

| region | render | overflow | theme | verdict |
|---|---|---|---|---|
| verdict strip | report.html | none | both | **FAIL round 1 -> fixed** |
| step list | report.html | none | both | pass |
| architecture schematic | report.html | none | both | **FAIL round 1 -> fixed** |
| three figures + table | report.html | table scrolls in its own container | both | pass |

1. **Hair-space thousands separators rendered as full spaces.** `2&#8202;393` read
   as two numbers in the verdict, and worse, "about 2 000 samples" **broke across a
   line** so the paragraph ended on "about 2". Replaced with commas.
2. **The architecture bracket ended in the wrong place.** It spanned to the middle
   of the pooling stage while the shape labels show the cell axis disappearing
   *at* pooling — the drawing contradicted its own annotation. It now stops where
   N does, and the label says "then pooling consumes it".
3. **Dark theme was unverified.** Now checked: `body` resolves to
   `rgb(17,21,26)` from a token, no element computes transparent text, and the
   schematic's red highlight holds against the dark ground. No color is defined
   only inside a media or `[data-theme]` block.

Also confirmed: no horizontal page scroll at 1100 px or 420 px; the wide table
scrolls inside its own container; focus styles are present.

### Role 11 — Start With the Problem (1)

Spine, one claim per section: the measurement works and the model does not ·
the target is a per-lab loop, which redefines "mass" · here is where the four
steps stand · the measurement half, and what it recovers · why this network and
not another · what it scored · what is ruled out · what to do next.

**The arc deviates from the default and did not say so.** It is not
problem→cost→method→fix; it opens on the verdict because the reader approved this
work and needs the outcome before the reasoning. Now stated in the standfirst,
which names all four steps and their status in the first three sentences.

---

## Residual ⚠

**None.** Every finding was applied to the source and the page rebuilt; the final
render post-dates the final fix.

One limit worth stating rather than flagging: the scoreboard is **three
recordings**, which is the bench's own default. It separates the learned models
from the hand-written ones by a wide margin and does **not** separate the top
three hand-written detectors from each other. The page now says so where the
numbers appear.


---

# Round 2 — 2026-08-16, after the result changed

The page was rewritten rather than edited, so this is a second review and not a
verify pass. **The conclusion inverted**: Tony proposed a centre-surround
architecture, it was built, and it scores **F1 0.56** where the two models the
first version reported scored 0.12 and 0.15. A page whose headline was "does not
converge" cannot be patched into a page whose headline is "here is how to find
it".

Two structural notes from Tony drove the rewrite, and both were defects in the
first version that no role had caught:

1. **"Always lead with a figure showing the problem."** The first page opened on a
   headline and a stat strip. It now opens on the problem drawn — a raster where
   the planted events are genuinely indistinguishable, the brightness trace where
   they appear alongside impostors, and the centre-surround trace that separates
   them. This is role 9's territory and role 9 had passed the page clean, which is
   the finding: *the rule I checked was "should any of this prose be a picture",
   not "does the reader see the problem before the solution".*
2. **"I don't see the network design, layers and their function."** The first
   version explained the architecture in four prose subsections with a schematic.
   It now carries a **layer table** — index, layer, what it does, why it is there,
   output shape, parameter count — which is what "a quick scan" requires. The
   schematic stays; it answers a different question (the shape of the signal path)
   than the table (what each stage costs and buys).

## Findings, round 2

**Role 1 — Prove It.** Every headline number re-verified against the regenerated
`learned_results.json` by assertion rather than by eye: F1 0.56, 1 149
parameters, learned centres [1.83, 4.21, 6.49, 9.91], and the threshold curve's
0.90 row (recall 0.80, precision 0.25). All match.

⚠ **One correction applied during the rewrite.** An interim summary quoted "recall
0.76 at precision 0.35" for the high-recall operating point. That was the 0.95
threshold, measured before the grid was widened. The page now carries the full
five-point curve straight from the cache, and the 0.76 figure appears nowhere.

**Role 4 — Reviewer 2.** The tempting overclaim is that the model beats the six
because it reaches recall 0.89. It does not: at that threshold precision is 0.10.
The page reports the whole curve as a table with plain-language consequences on
each row, and names the F1 optimum as the point the scoreboard shows, so the
reader can see what the recall costs rather than being handed the flattering end.

**Role 6 — RTFM.** The claim that a difference of Gaussians "integrates to zero on
a flat field" was checked against the implementation: both lobes are
area-normalised before subtraction, so it holds by construction rather than
approximately. The claim that the centres "started at one sample" was checked
against the initialiser.

**Role 10 — Ship It.** Re-run against the new render at 1100 px in both themes:
7 008 px tall, no horizontal scroll, **zero broken or unloaded images** (checked
programmatically, not by eye), all four figures present, the two new tables
scroll inside their own containers. Dark theme re-verified after the rewrite
because the rewrite touched no CSS but did add table rows with a tinted
background — `color-mix` on the accent resolves in both themes.

**Roles 2, 3, 5, 7, 8, 9, 11.** Re-walked against the new page. Two changes worth
recording: the argument order is now problem → mechanism → evidence, which is the
default arc rather than the deviation the first version had to justify; and the
figure-to-prose ratio improved by adding a figure rather than by cutting text,
which is the trade role 9 asks for.

## Residual ⚠ — round 2

**One.** The scoreboard, the threshold curve, and the learned centre widths all
come from **a single training run at one seed**. The architecture comparison is
therefore a comparison of one fit each. It is a large enough gap (0.56 against
0.12) that seed variance is unlikely to explain it, but no error bar is reported
and none should be inferred. The next run should be a sweep, which is now worth
doing precisely because the model trains.
