# SAP016 — the sentence that reads fine and explains nothing

**Filed with the rule, not after it.** What SAP016 catches, what it cannot, and why its scope is two
files.

## The sentence

> Looking **nearby** means the bar rises when cells get busy, so chance lineups in a busy stretch are not
> called.

Tony, 2026-09-16, reading the plain-language detector review:

> this is classic you. it sort of makes sense to a human, and there's nothing wrong at first, but then
> "looking" what do you mean? nearby means i look on the floor by my chair when i drop something, here I
> don't know what it means. What bar? how did it rise?

Three failures in one clause, and none of them is a wrong fact:

1. **"Looking nearby"** is an activity with no actor. Nobody looks. The programs compute.
2. **"the bar"** arrives with a definite article and no owner — which program's, over what?
3. **"rises"** is intransitive, so the cause is unstatable. The copies drawn from a busier minute produce
   bigger counts, and the count a bin must beat is computed from those copies. That is the mechanism, and
   the sentence cannot contain it.

The writer had the chain in mind and skipped to its conclusion. A reader who already knows the chain
nods; a reader who does not has no way in, and no way to tell that anything is missing. That is what
makes it worse than an error: it does not look like one.

## What the rule matches

A gerund made the subject of an explanation — `Looking … means`, `Counting … means`, `Using … means` —
within one clause. The gerund list is the verbs this project reaches for when describing what a detector
does.

**It reads through inline markup.** The first draft used `\w+\s+` between the two halves and could not
fire on the sentence it was written for, because the page says `Looking <b>nearby</b> means`. A prose rule
scanning HTML must expect tags mid-sentence; `[^.]{0,45}?` does, and the bound keeps it inside one clause.

## What it cannot catch, and what to do instead

The rule matches one syntactic shape. The fault is a **habit**, and the habit has other forms:

- **"The bar rises."** Intransitive verbs on defined nouns, with the cause omitted. A rule could match
  `the bar (rises|moves|goes up)` but would fire on legitimate uses in captions where the mechanism was
  given two sentences earlier, and sapper cannot see two sentences earlier.
- **"This is why X."** A conclusion pointing back at reasoning that was never written down.
- **Definite articles with no antecedent** — "the copies", "the count", "the window" — where the noun has
  never been introduced. This is probably the most common form and is not mechanizable line by line: the
  antecedent may be legitimately three paragraphs up.

For those, the check is a person reading the document cold — which is how this one was found. The rule
exists to stop the single most repeatable form from coming back, not to make the reading unnecessary.

## Why the scope is two files

`include=["tools/plain_*_template.html"]` — the two plain-language templates. Those are the documents
written for a reader with no background, where every sentence is supposed to survive cold.

Tree-wide it would be wrong. Working notes, handoffs and run records are written between people who share
the chain, and compressing it there is not a defect; `docs/` is full of sentences this rule would flag
that are doing their job. A BLOCK that fires on correct writing teaches people to route around sapper,
which costs more than the rule is worth (the SAP006 precedent: deliberately narrow, page and report
builders only).

If a third plain-language document appears, name it `plain_*_template.html` and it is covered.
