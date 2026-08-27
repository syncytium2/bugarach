# Murderboard run — the bench acceptance criteria

## What was at stake

The artifact is a todo doc arguing that an 18×-vs-17× disagreement across the
estate is not a typo but a defect in how the bake-off publishes its numbers — and
turning that into acceptance criteria for the bench replacement.

A document whose entire thesis is *"the bench published numbers loosely and four
readers each invented an integer"* has one obvious way to fail: publish its own
numbers loosely. It did. **Role 1 found that the draft's opening sentence
miscounted the very documents it was about** — it said four documents and three
saying seventeen, when the tree holds five and four. A document about a counting
defect shipped with a counting defect in its first line.

Three more of the same shape followed: a fold identified as an outlier it is not,
an F1 spread range that silently excluded the detector holding its low end, and a
claim about résumé text that no source in the estate can verify. All four were in
the half of the document doing the *arguing*, not the half doing the prescribing.

## What that says about the criteria themselves

The draft's four blocking criteria ask the bench to emit what it quotes, publish
dispersion, repeat its timings, and render its prose from source. Every defect
this review found in the draft is an instance of the first and last: quantities
carried by hand from a source into prose, with nothing between them that could
fail. **The document reproduced the defect it describes, which is the strongest
available evidence that the criteria are pointed at something real** — and it is
now recorded in the document's own provenance section that every quantity was
recomputed rather than transcribed.

## What would validate this

The criteria are checkable the moment the replacement bench emits its first
artifact: does a ratio it wants quoted exist as a field, does every headline
column carry a spread, does a timing cell have more than one measurement behind
it. Nothing here needs the replacement's design to be settled first.

The one thing this review could **not** establish is whether seventeen is
genuinely in circulation on sent application material. That claim is now flagged
inline and attributed, because it is the only argument that decides seventeen over
eighteen on grounds other than arithmetic.

---

# Appendix — run record

- upstream:  syncytium2/murderboard @ 3593c44
- copy:      vendored @ 3593c44 (re-vendored during this run — see below)
- freshness: current
- artifact:  `docs/todo/2026-08-27-nobody-typed-the-wrong-number.md` (`6a9fdf18` → `e21b8715`)
- roles:     11 of 11 run
- rounds:    1 blind verify round; stopping reason **severity floor reached**

## The freshness gate fired, and it was a stamp lag

The gate exited 1 (STALE) before any role could run: vendored 73dad04 against
upstream 3593c44. Re-vendoring with `murderboard_revendor.py` reported **zero body
changes and five stamp bumps** — `doc_review_process.md` is byte-identical between
the two commits, and upstream's only movement was its own traffic workflow and
metrics. So no review rule was missing; the gate was correct in mechanism and the
lag was cosmetic. It is recorded here rather than waved through because "the gate
fired and I judged it cosmetic" is exactly the reasoning the gate exists to
refuse — the judgement was made by diffing, not by assumption.

The gate also noted `.claude/hooks/require-commit-before-message.sh` stamped
`fae0eca`, outside the vendor family's five files. Not touched by this run.

## Conformance deviation — read this before quoting the run

The process prescribes **parallel subagents** for a substantial deliverable and
allows a single-pass self-review only for a small one. This run was executed
**single-pass**, walking all eleven checklists in turn, on a ~1,500-word sectioned
document that sits on the substantial side of that line.

The process's own appendix records a case where single-pass execution on a
substantial report coincided with a missed attribution defect, and names the
conformance shortfall as a confound. The same caveat applies here. The mitigating
facts: this artifact makes no external attribution and claims nothing as novel, so
the one role the size rule may never collapse — role 2 on an attribution
deliverable — is not engaged.

## Role ledger

| # | Role | Result |
|---|---|---|
| 1 | **Claim & data verifier — "Prove It."** | **4 findings (3 blocking, 1 major).** 23-row claim ledger, every quantity recomputed from `bakeoff.json` at full precision. Found the document miscount, the false fold-2 characterisation, the truncated F1 spread range, and the unverifiable circulation claim. |
| 2 | **Citation & reference validator — "DOI or Die."** | No findings, and here is what I checked: the document makes no external citation, attributes no method, and claims nothing as novel or "ours" — so the attribution carve-out does not fire. Its two internal links (`2026-08-14-generator-doc-numbers-are-transcribed.md`, `../../README.md`) both resolve, and the quoted sentence from the generator todo was checked verbatim against the source. |
| 3 | **Consistency auditor — "Cross-Examiner."** | **2 findings.** The document count disagreed with the tree (with role 1). Terminology drift between "learned model" and "learned detector" — partly fixed by defining the referent once; residual noted below. Glossary checked: no banned "modality", stream/detector axis vocabulary not misused. |
| 4 | **Adversarial reviewer — "Reviewer 2."** | **3 findings.** "There is no integer this quantity supports" was asserted without an interval — now carries a 95% *t*-interval (16.22–18.96). "Not a slip" implied the README author computed from folds, which is not established — restated. "Worth more than any individual figure" was unfalsifiable flourish — cut. Checked the "can the alarm ring?" lens on the draft's own central claim: a design with n=1 per cell genuinely cannot decompose its variance, so that criterion has power. |
| 5 | **Line editor — "Kill Your Darlings."** | **1 finding.** A quotation was silently recapitalised; restored verbatim. Otherwise each sentence asserts one thing; no filler found. |
| 6 | **Methods / domain expert — "RTFM."** | **1 finding.** The timing criterion asked for repeats but not for the right summary statistic. Timing interference is one-sided, so the mean is dragged by any descheduled run — the criterion now specifies **minimum or median** across repeats. Verified `detect_sec.n = 4` really is one measurement per fold against `per_fold`, and that the significant-figure bound (±4% from two-figure `0.014`) is correctly derived. |
| 7 | **Reuse auditor — "Reinventing the Wheel."** | **1 finding.** The draft prescribed a render step as though it were new work; the generator todo already names two candidate mechanisms, and its preferred one — *a test that re-derives every quoted number and asserts it* — is precisely what this doc needs. Now pointed at it as one job rather than two. No code ships with this deliverable. |
| 8 | **Naive-reader accessibility — "You Lost Me."** | **2 findings.** "The revamp" was used throughout with no referent, and the learned detector was never identified, so a cold reader could not map the argument onto the bake-off table. Both now defined in a standfirst paragraph. Internal identifiers (`detect_sec`, `bakeoff.json`) retained deliberately — the audience is a future session working in this tree. |
| 9 | **Density & figure-first — "Show, Don't Tell."** | **No findings; one judgement recorded.** Considered whether the fold ratios should be a figure, given this project's standing rule to render a visual finding rather than describe it. Declined with reason: the payload is four numbers straddling two integers, and a four-point chart would add ink without adding information — the table shows every value and both derived ratios directly. Thresholds used: prose-document conventions, not the slide word counts (which do not apply to a `docs/todo/` entry). |
| 10 | **Build & craft gate — "Ship It."** | **Table below.** Markdown deliverable, no render step. |
| 11 | **Argument order — "Start With the Problem."** | **1 finding.** The spine opened on the 18-vs-17 story and reached the document's actual job — acceptance criteria — only in the third paragraph, so a reader scanning `docs/todo/` would file it as a tidying note. A standfirst now states the job before the story. Arc used: problem → why it is not what it looks like → evidence → criteria → what is excluded. |

## Ship It — mechanical table

| Row | Checked against | Result |
|---|---|---|
| Frontmatter parses (`status`, `filed`) | the file | pass |
| Internal links resolve | both targets on disk | pass — 2 of 2 |
| Table well-formed | 6 rows, uniform column count | pass |
| Sapper (`--all`) | working tree | clear |
| Fingerprint changed after fixes | `git hash-object` | `6a9fdf18` → `e21b8715` |
| Word count / largest block | 1,529 words; largest block 140 | recorded — see residual |
| Renders to an image | n/a | Markdown; no build, no overlap surface |

## Findings by severity, per round

| Round | Blocking | Major | Minor |
|---|---|---|---|
| 1 (initial) | 3 | 6 | 5 |
| 2 (blind verify) | 0 | 0 | 2 |

Stopping reason: **severity floor reached** — the blind round produced no blocking
and no major findings. Not a round cap.

## Follow-up pass — original findings adjudicated

Every round-1 finding: **fixed**. The document count, the fold-2
characterisation, the F1 spread range, the undefined "revamp", the unidentified
detector, the missing interval, the "not a slip" overreach, the timing summary
statistic, the argument order, the recapitalised quote, the unfalsifiable
flourish, and the re-prescribed render step are all resolved in `e21b8715`. The
unverifiable circulation claim is **flagged, not removed** — see residual.

## Residual ⚠

1. **⚠ Seventeen's circulation outside the repo is unverified.** The document
   states it on Tony's word (2026-08-27) and says so inline. Searched
   `syncytium2-profile` and `tonydefazio.com`; the multipliers appear in neither,
   and the application material itself is not in the estate. **This is the claim
   that decides seventeen over eighteen on non-arithmetic grounds** — if it is
   wrong, that argument goes away and only the round-down convention remains.
2. **⚠ Minor, unfixed by design.** Two minors survived the blind round and are
   recorded rather than fixed, per the process's rule that fixing them opens a
   round already decided against: the opening sentence says all five documents
   quote how much *faster* the learned detector is, when two of them frame the
   same ratio as LoCo's *cost*; and one 140-word paragraph is long for its
   section.
3. **⚠ Single-pass execution on a substantial deliverable** — see the conformance
   deviation above.

## What this run does not warrant

This review found and fixed 14 defects. **It is not a correctness proof.** The
convergence table measures how quickly the reviewer stopped finding things, not
whether anything remains — and with a single-pass run there is one reviewer, so
it measures that even more narrowly than usual. A blind pass by someone who did
not write the draft would be worth more than the round count above suggests.
