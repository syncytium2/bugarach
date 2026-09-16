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

## 20. "Each cell holds a dye that glows brighter" is wrong (2026-09-16)

These are GCaMP6f-expressing neurons. Nothing is added to the cells: the mice carry the gene, and the
cells build the protein themselves.

**Applied**, in two sentences a sixth grader can follow, plus a word-list entry. Left out as more than
the reader needs: that GCaMP6f descends from a jellyfish protein, and that "6f" marks the fast variant.

## 21. "Active" is a loaded word here ⚠ (2026-09-16)

The follow-up to note 20, and the more important half. *"the word active is loaded (TTX fails to block
calcium events and coordinated events)"*. Saying a calcium event means the cell "became active" smuggles
in the mechanism that this lab's own data contradict — FOUNDATIONS §9, where calcium events and
coordination both persist under TTX.

**Applied.** The page now describes only what is observed: the calcium inside a cell goes up, the protein
brightens, the brightening fades as the calcium clears. A calcium event "says the calcium inside that
cell went up. It does not say why, and this document does not assume why" — with the forward pointer to
the TTX section, where the distinction pays off. "Active" is gone from the body text; cells *brighten*,
and where rate matters they are *busy*. High potassium is described by what it produces (calcium events
in healthy cells), not by making cells "active".

**Keep this rule for every future document out of this project**: describe the observation, not the
mechanism, wherever the mechanism is what the lab is still arguing about.

## 22. A sixth grader can handle "bin" (2026-09-16)

"Piece" was a euphemism, and it cost precision — the programs genuinely differ in their bin widths, and
"2-second piece" reads as an arbitrary chunk rather than a grid.

**Applied throughout**, not only in Section 3: a word that changes halfway through a document is worse
than either choice. *Bin* is defined where it first appears, in Section 3, and has a word-list entry.

### Caught while applying this: Figure 1's caption described the figure it replaced

The orienting figure (note 6) went in, and its caption still said "one minute of a recording with 33
cells ... this recording is simulated". The figure is ten minutes of a real one. No check would have
caught it: the build only verifies that tokens resolve.

**Fixed**, and made harder to repeat: the caption is now written from the figure's own numbers
(`{{T.orient_n_roi}}`, `{{T.orient_n_stripes}}`, `{{T.orient_biggest}}`), so a caption that drifts from its
figure now fails the build instead of reading plausibly.

## 23. Name the circular shift, in the literature's words (2026-09-16)

Tony authorized the jargon explicitly: *"this is called a circular shift in the literature"*.

**Applied** after the plain description, not in place of it, with why each half of the name fits and a
pointer to the reference list. The word-list entry is headed "Shifted copy (a *circular shift*, in the
research literature)".

*Not done:* naming the shuffle's literature term. The field uses several (spike shuffling, random
resampling, a Poisson surrogate) and picking one would assert more than we know. Say if you want one.

## 24. Do not sell the circular shift as the answer ⚠ (2026-09-16)

Tony: learned models seem able to **detect the circular shift itself as a cue**, so a shifted copy is not
an invisible stand-in for the recording. (Told not to go looking for the measurement, and did not.)

**Applied** as a subsection of Section 5, "The shift is the better choice, not the right answer", with
two limits: real recordings line up more than the shift predicts even where nothing is coordinated, and a
trained program can sometimes tell a shifted copy from the real thing. Section 4 no longer says a
surviving lineup *is* chance — it says "as far as the shift can tell" — and "What could be wrong here"
gains a matching bullet, because every bar in the document rests on the shift.

## 25. "reach 4" is vague (2026-09-16)

It never said reach *what*, and it was cells, not events.

**Applied:** the histograms now read "copies with 4 or more cells in the bin: 0.3%", and the figure's foot
says what makes a count a call ("a count that fewer than 5 copies in 100 reach is called").

## 26. Do not introduce a second word for simulated data (2026-09-16)

*"'invented' means something else to me, it does not signify simulated"*. Fair: I had split the vocabulary
— *simulated* for the simulator's output, *invented* for the teaching examples drawn by hand — which
buys nothing and costs the reader a distinction to track.

**Applied:** one word, **simulated**, everywhere.

### Caught while applying this: Figure 4's caption also described the data it replaced

Same failure as the opening figure, one section over: the caption still described a 2-second bin of the
33-cell bench recording with 7 cells in it, while the figure showed the six-cell example that replaced
it. **Fixed and tied to its data** — `{{T.steps_cells}}`, `{{T.steps_observed}}`, `{{T.steps_copies}}`,
`{{T.steps_share}}` — so it cannot drift again.

**Two for two.** Both times a figure was replaced, its caption survived and read plausibly. Captions are
now written from the figure's own measured numbers wherever they state a fact about the data, which is
the only form the build can check.

## 27. "Looking nearby means the bar rises" — the sentence that explains nothing ⚠ RULE (2026-09-16)

*"this is classic you. it sort of makes sense to a human ... but then 'looking' what do you mean? ...
What bar? how did it rise?"*

Three faults, no wrong fact: an activity with no actor ("looking" — nobody looks, the programs compute);
a definite article with no owner ("the bar"); and an intransitive verb that makes the mechanism
unstatable ("rises"). The chain was in my head and the conclusion went on the page.

**Applied.** The sentence is now two paragraphs that name the program, say what it computes, and then
say what follows — one for the three that measure chance from the surrounding seconds, one for the two
that measure it once from the whole recording.

**Mechanized as sapper SAP016**, which matches a gerund made the subject of an explanation
(`Looking … means`) in the plain-language templates only. Its first draft could not fire on the very
sentence it was written for, because the page says `Looking <b>nearby</b> means` and `\w+` does not match
a tag — a prose rule scanning HTML has to read through markup. What it cannot catch, and why the scope is
two files, is in
[`sapper_feedback/2026-09-16-an-activity-standing-in-for-an-actor.md`](../sapper_feedback/2026-09-16-an-activity-standing-in-for-an-actor.md).

## 28. Text overlap in the algorithm figures, and an unreadable x-axis (2026-09-16)

*"TEXT OVERLAP! UGH! I HATE TEXT OVERLAP ON FIGURES!"* — my line labels (note 15) were placed inside the
panel, and "the average nearby" landed on the average it named. Also: *"the x-axis for A and B is
absolute shite. they are both 1 minute long but you need to be a math major to figure it out"* — the two
panels were labelled with clock times (8m–8m30s against 22m30s–23m30s), so their equal width was
invisible.

**Both applied, in the form that cannot regress:**
- The labels moved **above the panel frame**, where collision is impossible by construction, rather than
  being nudged around inside it. They are printed once, beside the left panel, and the foot of the figure
  now carries only the two triangles — everything else is named where it is drawn.
- Both x-axes count **seconds from the start of their own minute** (0s … 1m), so the panels are visibly
  the same width; where each minute sits in the recording is in its panel's subtitle.

The house rule this belongs under already existed — CLAUDE.md, nothing competing with the marks — and the
first version broke it by putting text on the data.

## 29. The open symbol in the scores figure (2026-09-16)

*"figure 14 the open symbol is confusing"* — binned SCE's second score was drawn as a hollow marker, and
nothing on the page said a hollow marker meant anything. A reader has to guess that it is the same
program.

**Applied.** Both scores are now solid dots in binned SCE's own colour, joined by a dashed hairline, with
one short line in the figure saying both dots are binned SCE and the caption carrying the reason. The
first attempt put that line where it crossed the "best possible" rule — the overlap complaint of note 28,
one figure later — so it was shortened and anchored clear of it.

## 30. "Every program here uses its default setting" — is that optimized? (2026-09-16)

*"figure 15 says every program uses default setting, is that optimized?"*

**The caption was wrong, and wrong in the direction that hides something.** "Default" reads as *untouched,
straight out of the code*. What the figure actually runs is `bugarach.bench.OPERATING_POINTS` — the
declared operating point for each program — and that table is half tuned:

| program | stored setting | where it came from |
| --- | --- | --- |
| CoactDetect | `alpha=1e-4`, 2 s bins, 60 s surround | tuned — the explore_sce FAST point, **not** the `coact_detect` signature default of `alpha=0.01`, a hundred times looser |
| LoCo | `threshold_pctile=99.9` | tuned — measured-regime F1 optimum |
| locust | `sce_percentile=99.999` | tuned — calibrated FAST pair; retuned from 99.99 on 2026-08-20 |
| rate+context | `excess_threshold_hz=5.0` | the function's own defaults |
| binned SCE | `threshold_pctile=99.0`, 10 s bins | the function's own defaults (generate_sce contract) |
| SPIKE-synch | `C_threshold=0.1` | the viewer's FAST defaults |

`bench.py`'s own module docstring makes the point in terms: it **refuses** to run a detector at whatever
its signature defaults to, because CoactDetect at `alpha=0.01` scores F1 0.72 where the calibrated point
scores 1.00 on the sparse regime. So the one word "default" asserted the exact thing the bench was built
to prevent.

The older document called this setting **"shipped"**, which was accurate and which Tony banned as jargon
(note 1). Replacing it with "default" swapped a jargon word for a *false* word — the failure mode worth
remembering: when a banned term goes, check that its replacement still means the same thing.

**Applied**, in two places rather than one, because the question is really about the whole document:
- The caption now says the program runs at the setting the project uses on the real recordings, and
  points at the scores figure as the one that does **not**.
- Section 9 gains a paragraph naming the two kinds of setting, saying which three programs were tuned and
  which three were untouched, and closing with the part a reader should carry away — **the tuned three
  were tuned on recordings from the same simulator that made the test recordings.**

## 31. "everyday setting" — a word I coined and then defined with itself (2026-09-16)

*"what does 'everyday' mean?"*

Note 30 replaced a false word ("default") with an invented one. The sentence read:

> each program runs at its **everyday setting**, the one the project runs it at.

**The gloss is the term restated.** "Everyday setting" is defined as "the one the project runs it at",
which tells a reader nothing they could not have guessed from the adjective, and hides the two facts that
actually matter: it is a *single stored value*, and it is *the same one on every recording*. Bolding it
made it worse — bold announces a defined term, so a reader waits for a definition that never comes.

This is note 27's fault wearing different clothes, one revision later. There the writing skipped the
mechanism; here it skipped the definition. Both times the chain was in my head.

**Applied — by deleting the term rather than renaming it.** A reader does not need a name for this; they
need to know what runs. The paragraph now says each program runs at a single stored value for its main
setting, the same on every recording, and that Figure {{NUM:fig_scores}} is the only place that value is
set aside. The two kinds are then told apart by where they came from — tuned on simulated recordings, or
the value the program was first written with — which is the distinction the section exists to make.

**The rule worth keeping:** when a banned word goes, the replacement needs the same scrutiny the original
got. "shipped" → "default" was false (note 30); "default" → "everyday" was undefined (this note). Three
passes to say a simple thing, because each fix was checked against the complaint instead of against the
reader.

## 32. "mid-sized planted events (18% of cells take part)" (2026-09-16)

*"what is 'mid-sized planted events found (18% of cells take part)? figure 15. i think you mean detection
of coordinated events with a minimum number of ROIs? not sure how to say that to a sixth grader, but what
we've got now is not it"*

**Not a minimum — a size, and the label buried the one fact that makes it interesting.** Planted events
come in three sizes, 30 / 18 / 10% of the 33 cells: **10, 6 and 3 cells**. Figure 15 scores only the
middle one.

Two faults:

1. **A percentage against a total the panel never gives.** "18% of cells" is arithmetic homework, and
   `bugarach.ui` house rules already say every number carries its unit — a count is a number.
2. **"mid-sized" says it sits between the other two, which is the least important thing about it.**
   `bench.py`'s own table records the measurement: `participation` was a 50–100% guess until 2026-08-13,
   and the measured value is **6 of ~33 ROI = 18%**. So 18% is not a middle band — **it is the size a real
   coordinated event actually is.** Figure 15 scores the programs at the realistic size, which is the
   whole reason that row was chosen, and the label hid it.

Worth separating from the thing Tony guessed it might be: `min_rois=3` is the detectors' own floor
(coact, loco and sce all refuse fewer than 3 cells) and is a different quantity. The 10% size = 3 cells
sits right at that floor, which is why it is the hardest case on the bench.

**Applied.** Panel A's title is now *"events joined by 6 of the 33 cells — the usual real size"*. Section
7 introduces all three sizes as counts, says 6 cells is what the lab measured, and says three of the six
programs will not call anything smaller than 3 cells. The simulator figure's legend read
"mid-sized: 18% of cells (6 cells)" and now reads "planted event, 6 cells — the usual real size". The
body's "of mid-sized events" became "of the 6-cell events". The word is gone from the document.

## 33. Figure 15B: "false alarms per minute in the busy stretch" (2026-09-16)

Read against the code, the count is narrower than the label. `_blockrecall_one` counts calls whose
**start** lies in `BLOCK_PLACE` (1240–1460 s, a 220 s window inset in the 5-minute busy stretch) **and**
which are more than 10 s from either of the two events planted inside it, over a denominator of
220 s minus 20 s per planted event.

So it is not "per minute of the busy stretch" — it is *per minute of the part of the busy stretch with no
planted event near it*, which is the right thing to count and was not what the label said.

**Applied.** The panel title is now "false alarms in the busy stretch" with the per-minute scale named on
the axis below it, and the caption says what a false alarm is here: *the calls a program made inside the
busy stretch with no planted event near them.*

## 34. Section 10's title, and four rows nobody explained (2026-09-16)

*"part 10. change to 'detection on real recordings'. put a note that tube refers to learned models
underdevelopment, outside the scope of the current document"*

**Applied**, and the second half was a real hole rather than a wording preference. Note 21 cut the learned
models out of this document into a companion — but the real-recording figures are drawn from
`ALL10 = CODED + LEARNED4`, so **five figures still show four lanes named tube, tube-guard, tube-ratio and
tube-ratio-guard**, and after the cut the word "tube" appeared nowhere in the prose. A reader met four
unexplained rows and had nothing to look them up with. Grep could not find it either: those figures are
PNG, so the names are not in the page text.

Section 10 now opens with a note saying the four rows are learned models — shown examples and worked out
their own rule, rather than following written steps — still being built, not among this document's six
algorithms, and neither tested nor judged here. They stay drawn so the rows are not silently missing.

**The lesson is about the cut, not the note.** Removing a subject from prose does not remove it from
figures that were built from a detector list. When something leaves a document, grep the *builders* for
the list that still includes it.
