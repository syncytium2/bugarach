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

**Done in the edit pass:** define it at first use, beside Figure 2 (which shows the marks), in one
sentence that says what it is and what it is not, e.g. *each mark is one moment the program claims
cells acted together — we call that a call, and a call can be wrong*. Then keep the short version's
first mention after, not before, that.
