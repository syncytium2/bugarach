---
status: open
filed: 2026-08-29
rule: none-yet
---

# Our detector keeps getting published under another lab's name, and prose has not held it

The rename landed 2026-08-24. Since then the same defect has been found and fixed
**four separate times** by four sessions, and each fix looked complete:

- 2026-08-28, `site/index.html` — *"the lane marked locust **is** CICADA's method"*,
  beside this project's own benchmark numbers, on the public page. Two more sessions
  found further instances within the hour (#363, #365), and the handoff for that work
  says in terms: *"assume there are surfaces still saying it."*
- 2026-08-29, this pass — twenty more, in `detector_history.md`, `generator.md`,
  `lanes.md`, `forks.md`, `model_track.md`, `RESET.md`, `workflow_plan.md`,
  `webapp_completion_plan.md`, the viewer's own help text, and **`CITATION.cff`**,
  which is the machine-readable metadata Zenodo and indexers read.

**The damage is asymmetric, which is why this is worth mechanizing.** locust is the
detector that fires 214.8 times in a block built to contain nothing. Every sentence
that reports that number under the name CICADA tells a reader the Cossart lab's tool
is promiscuous, using this project's own benchmark as the evidence. A citation slip
can be corrected later; this one is a claim about another laboratory's software, and
it has now been made in public on four occasions.

## The rule, as narrowly as it can be written

Blocking `\bCICADA\b` everywhere is wrong — the word is legitimate wherever it names
the upstream tool, and the records **must** be free to quote the error.

**Scope to rendered and user-facing surfaces only:** `docs/learned/*.src.html`,
`docs/site/**`, `src/bugarach/ui/**`, `tools/make_*figure*.py`, `CITATION.cff`.
On those, a bare `\bCICADA\b` is a **BLOCK unless the same line also matches**
`cossartlab|Denis|derives|derived|upstream|MIT|Cossart lab`. On a rendered surface
the only legitimate CICADA is a citation of the upstream tool, which is exactly what
the escape hatch admits.

**Excluded, and this is load-bearing:** `docs/handoffs/**`, `docs/reviews/**`,
`docs/adr/**`, `docs/todo/**`, `docs/sapper_feedback/**` — dated records of what was
said at the time. Renaming inside them falsifies the record, and a rule that fires on
this very file is a rule people will disable.

**Self-test fixtures come free from the real tree** — the bad case from
`landscape.src.html:262` (*"of those six only CICADA is published work"*), the good
case from any line citing `gitlab.com/cossartlab/cicada`.

## The blind spot, stated rather than discovered later

It sees only the surfaces named. **`README.md` stays out of the include list** until
the diagnostic figures are rebuilt, because `README.md`'s figure alt text legitimately
says CICADA — the committed PNG draws that label, and describing the picture
accurately is not the defect. When
[the figures are regenerated](../todo/2026-08-23-the-diagnostic-figures-are-one-calibration-behind.md),
README can be added.

It also cannot see prose that gets the *direction* wrong without using the word — a
sentence crediting the Cossart lab for a rule published from Yuste's lab reads clean
to any regex. That failure mode belongs to the murderboard's role 2, not to sapper.
