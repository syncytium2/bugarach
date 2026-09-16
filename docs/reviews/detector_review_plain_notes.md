# Tony's review of the plain-language detector review — running notes

The page under review: `<darkroom>/bugarach/2026-09-15-detector-review-plain/detector_review_plain.html`,
built by `tools/make_plain_detector_review.py` from `tools/plain_detector_review_template.html`.

Notes were taken while Tony read, and **applied on his word** ("start with that feedback for the next
revision") in the revision of 2026-09-16. Each note below carries what was done.

**Status: notes 1–5 APPLIED.** Later notes are collected the same way — written down as they arrive,
applied when Tony says to.

---

## 1. "Films" is wrong — the imaging is digital (2026-09-16)

Nothing is filmed. Film has not been a technique in this field since the 1970s; these recordings are
digital imaging.

**Where it appears** (`tools/plain_detector_review_template.html`):

| line | text |
|---|---|
| 37 | "The lab **films** brain cells that flash when they are active." |
| 70 | "keeps thin slices of mouse brain alive in a dish and **films them** under a microscope." |
| 481 | word list, *Calcium event*: "A short brightening of one cell in the **movie**." |

**Applied 2026-09-16.** §1 reads "records them through a microscope with a digital camera, about ten
pictures a second"; the short version says the same. "Movie" is gone with it — a calcium event is now a
brightening "in the recording". "Film" appears nowhere in the page.

**Decided:** "movie" also goes. It is ordinary usage for an imaging time
series, but it carries the same picture, and the page uses it in the word list only. Candidate
wording: the lab *images* / *records* the slice, and what it produces is a *recording* (already the
page's word everywhere else) or an *image series*.

## 2. Pronouns with no clear owner, and the cooking metaphor (2026-09-16)

Two problems, both in the same sentence: *"Each one does it with a different recipe."*

**(a) "it" and "each one" make the reader hunt for the noun.** The subject of the paragraph shifts
between programs, cells and lineups, so a bare pronoun points at whichever noun the reader happened to
hold on to. Every pronoun should be replaced by the noun itself where there is any doubt, even at the
cost of repeating "the program".

Pronoun sentence-starts to re-read with this in mind (`tools/plain_detector_review_template.html`):
lines 41, 72, 92, 105, 109, 158, 160, 195, 225, 275, 330, 335, 496, 497. Several are fine (the noun is
one clause back and unambiguous); the fix is a pass over all of them, not a blanket rule.

**(b) "recipe" is a cooking word and does not belong.** It was doing the work of explaining
"algorithm", which cannot carry a metaphor a reader has to translate. Occurrences: lines 41, 157, 158,
173, 225, 474 (the word list), plus two code comments in `make_plain_detector_review.py` (878, 884).

**Applied 2026-09-16.** "Recipe" is gone from the page and from the builder's own comments. Each flagged
pronoun was replaced by its noun: "each program marked", "LoCo takes whichever side", "No figure here
can show", "In this lab's recordings TTX does not stop it".

**Wording chosen:** an algorithm is *a fixed list of steps, written out by a person, that a computer
carries out in the same order every time*. Then the six are *step-by-step
programs* or simply *the six algorithms*, and §7's contrast becomes *the other four programs were not
written as steps; their numbers were set by training*. Avoid "recipe", "cookbook", "ingredients".

## 3. "Made-up recordings" arrive with no preface (2026-09-16)

Simplifying the word is fine; dropping the *reason* is not. The page uses "made-up recordings" from
the short version onward (first at line 42, then 78, 101, 117 …, 16 places) but does not say until
§8, six sections later, **why anyone would make up data at all**.

The missing step is the argument, not the definition: a real recording has no answer key, so one way
to test a program is to **produce recordings ourselves — simulate them — where we decide in advance
where the coordinated events are**. Then a program's calls can be checked against what we put in.

**Where the preface belongs:** §2 "The problem", right where the page says a real recording has no
answer key (around line 92), and one clause in the short version's third bullet so the term is not
used before its reason. §8's heading and opening then follow from it rather than introducing it.

**Applied 2026-09-16.** The argument is now its own bullet in the short version, ends §2, and opens §8
("Simulated recordings, where we know the answer"). "Made-up" is gone throughout: **simulated** for
anything the simulator wrote, **invented** for the six teaching cells of Figure 5 and the grading minute
of Figure 14, which are drawings rather than simulator output. The word list defines *simulate*.

**Decided:** the page moves to **simulated**, with
"simulate" defined once in that preface. "Simulated" is the word the rest of the project uses, it is
not baby talk, and it reads as deliberate rather than casual — "made-up" can suggest invented in the
sense of *not serious*. The word list already carries *Simulator*.

## 4. "Clear stripes" arrives from nowhere, and a HOUSE RULE: lead with the figure (2026-09-16)

`{{PROSE:short_real}}` puts **clear stripes** in the second bullet of the short version. The term is
not defined until §12 (line 353), and the figure that shows one — Figure 21, panel A — is further down
still. The reader meets a named thing, in bold, with no picture of it.

**The rule Tony wants written down: ALWAYS LEAD WITH A FIGURE.** A term that names something visible
gets its picture *first*, then its name, then its definition — never the other way round. This is
stronger than the existing CLAUDE.md rule ("Show the picture — don't describe it"), which says to
render the figure but not that it must come *before* the words that depend on it.

**Applied 2026-09-16.** The rule is in CLAUDE.md under "Show the picture — don't describe it". In the
page, §§1, 2, 3, 4, 5, 7, 8, 9, 10 and 12 now open with their figure, and *clear stripe* is defined in
the caption of the figure that shows the ▼ marks. It no longer appears in the short version at all.

**Done in the edit pass:**
- Add the rule to CLAUDE.md under "Show the picture — don't describe it", in those terms.
- In the page: either show a small stripe figure where the term first appears, or keep the short
  version free of the term and let §12 introduce it under its own figure. §12 already opens with
  prose and puts Figure 21 after it — the figure should come first there too.
- Check the same failure for every other bolded term: *coordinated event* (line 76, figure is above it
  — fine), *call* (see note 5), *decoy*, *busy stretch*, *analysis window*, *planted event*.

## 5. "What's a call?" (2026-09-16)

Asked while reading, which is the answer to whether the definition arrives in time: it does not.
**calls** first appears inside `{{PROSE:short_real}}` ("one program made 131 calls and another made
2", line 44 of the built page) and is not defined until §2, line 85: *"Each program marks the moments
it thinks are coordinated events. We call each mark a call."*

Same shape as note 4: the word is used before both its picture and its meaning. The definition itself
is also weak — "we call each mark a call" is circular-sounding, and it hides what matters, which is
that **a call is a claim by a program, not a fact about the cells**. The word list already says that;
the body text should say it where the word first appears.

**Applied 2026-09-16.** The short version no longer uses the word: it says a program "marked 131
moments". §2 defines it beside Figure 2, in the sentence describing that figure's marks — *"One such
mark is a call. A call is a claim by a program, not a fact about the cells: it can be right or wrong."*

**Done in the edit pass — see note 8: Figure 2 is being replaced, so "beside Figure 2" moves with it.**
Define it at first use, beside the figure that shows the marks, in one
sentence that says what it is and what it is not, e.g. *each mark is one moment the program claims
cells acted together — we call that a call, and a call can be wrong*. Then keep the short version's
first mention after, not before, that.

## 6. Open on a busy raster with a few coordinated events (2026-09-16)

The document opened on a quiet simulated minute holding one planted event: it showed the machinery and
not the phenomenon. A naive reader needs to see the thing itself first.

**Applied.** Figure 1 is now ten minutes of a real recording with every clear stripe marked, plus a
20-second close-up so a tick is a visible object. Picked by the builder as the ten minutes with the most
clear stripes inside one analysis window (`best_orienting`), so it is the best available example rather
than a chosen one.

## 7. "A part of the recording those programs were never given to look at" (2026-09-16)

Opaque, and it used *analysis window* before that term exists. It means: the lab marks which stretches
to study, four of the six programs run only inside them, so the stripe was never shown to them — the
program did not look and decide against it.

**Applied**, in those words, in the short version.

## 8. Figure 2 is a poor example: no clear coordinated events in it (2026-09-16)

Correct, and measurable: **that recording holds zero clear stripes in the 13 minutes shown** (the
stand-out rule of note 4). It is a good picture of programs disagreeing and a bad picture of coordination.

**Applied in part.** The orienting figure (note 6) now carries the burden of showing what a coordinated
event looks like, and Figure 2 is explicitly the disagreement figure, with the dense stretch it comes
from re-used as panel B of the close-up figure. ⚠ **Still open:** whether Figure 2 should be replaced
outright by a recording that has both clear events and disagreement.

## 9. Resurrect the numbered events in the shifted-copy figure (2026-09-16)

*"humans can't see the pattern shift without cues"*. The lab's older MATLAB slide
(`constellation/coord_explainer/step1_shift.png`) numbered each cell's events in firing order and
labelled each row's shift.

**Applied.** Figure 4 is rebuilt that way: numbers, not ticks, and the shift given to each row printed
beside it. It also moved off the bench recording onto six invented cells — on a quiet recording every
cell has one event per minute, so every number read "1" and there was no pattern to follow.

## 10. Figure 2 names programs that have not been introduced (2026-09-16)

**Applied.** A short roster follows Figure 2: the six names, who built each, and a line saying the names
are labels until Section 6. The caption says the same.

## 11. locust must be identified as a modification of CICADA's coordination detector (2026-09-16)

**Applied** in three places: the roster under Figure 2, the "where it comes from" column of the table in
Section 6, and the locust figure's caption, which says what was changed (fed the lab's own event list,
its own bar) and that its results have never been compared with CICADA's.

## 12. Name the human behind each detector (2026-09-16)

Tony's account: rate+context he built himself; CoactDetect and LoCo were his idea; binned SCE is Yuste
and coworkers; SPIKE-synch is Kreuz's measure with his peak-detection idea on top to make the calls.

**Applied** as a "where it comes from" column in the Section 6 table, and in the roster under Figure 2.
The tube networks' attribution moved to the companion document with them.

## 13. Show rate+context's two windows (2026-09-16)

*"rate is 1s window, context is a centered 60s window (note these are parameters for optimizatoin
too)"*. **Applied:** the figure now draws the 1-second counting window inside the 60-second context
window, to scale, with the moment being scored marked, and says in as many words that both widths are
settings that could be tuned and so far have not been — only the bar has.

## 14. Figure 7 was not understandable to its own author (2026-09-16)

**Applied in part**, via the raster and labelling fixes of notes 15 and 17, which reach every algorithm
figure. The historical version worth mining is
`constellation/coord_explainer/loco_vs_coactdetect.png`, which puts the whole decision on one
histogram: the pooled null, the observed count, the bar, and the arithmetic that puts the bar there.
⚠ **Still open:** rebuilding CoactDetect's figure around that single histogram.

## 15. Figure 8: what is the purple line, what is the dashed line (2026-09-16)

The key sat at the foot of the figure, far from the marks it named.

**Applied:** every line in every algorithm figure is now labelled in its own colour, beside the line, in
panel A. The key stays as a backstop.

## 16. locust's durations: fixed 1 second, not the measured event width ⚠ FINDING (2026-09-16)

Tony: *"locust is duration based ... i hope we are actually using FWHM and t_peak - t50rise"*. **We are
not.** `cicada_detect` supports `active_duration_mode="per_event"` (the producer's own `width_sec`), but
`bench.OPERATING_POINTS["cicada"]` passes `active_duration_sec=1.0` and leaves the mode at `"fixed"`.
Every locust number in this project used a flat 1 second, and its 99.999 percentile was tuned against
that. Filed as
[`todo/2026-09-16-locust-ran-at-a-fixed-one-second.md`](../todo/2026-09-16-locust-ran-at-a-fixed-one-second.md),
waiting on Tony. The document now says the fixed second is what ran and flags it ⚠.

*Also noted:* "no need to mention fast and slow for this document" — taken narrowly, as not tying
duration rules to the two streams. The two lists are still named where the real figures are split by
them. ⚠ Say if they should go entirely.

## 17. SPIKE-synch: a per-event synchrony score, made continuous, then peak-detected (2026-09-16)

**Applied** to the step list and the caption. Confirmed in `sync.py`, which has both a threshold scan and
a `peak` mode over the same continuous trace; the runs here use the threshold scan, and the document says
the peaks are what turn scores into calls.

## 18. Cut the learned models; keep them for a separate document (2026-09-16)

**Applied.** Section 7 and its figure are gone; the networks are out of the scores, busy-stretch and
close-up figures, the word list and the references. Nothing was discarded: they now have their own page,
`learned_detectors_plain.html`, built by the same tool from the same measurements, marked as held back
and not reviewed. The four real-recording figures were **redrawn here** rather than reused from the first
review, which carried a lane per network.

Two things followed from the cut and are worth keeping:

- **Section numbers are no longer typed.** The template names sections by key (`{{SEC:eye}}`) and the
  builder counts them, because this restructure would otherwise have left every "Section 8" pointing one
  section too far. It refuses to build on a reference to a section that does not exist.
- **Raster geometry** now follows what the project already settled (`bugarach.ui.diagnostic`): marks at a
  third of the row pitch rather than 0.8 of it, and rows sorted by how busy each cell is. The earlier
  figures made every column look solid, which is the exact failure that docstring warns about.

## 19. Elaborate the motivation for decoys (2026-09-16)

**Applied** as its own subsection in Section 7: calling everything would otherwise score well and prove
nothing; decoys stand for lineups that are real coincidence and should not count; and the honest price —
no program reading only event times can tell a decoy from a planted event, which is why the best possible
score is about 0.83 and why that ceiling is in the test on purpose.
