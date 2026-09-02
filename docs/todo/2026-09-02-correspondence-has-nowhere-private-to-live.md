---
status: open
filed: 2026-09-02
kind: decision — Tony's; the diagnosis is done and the workaround is "paraphrase"
---

# Correspondence has nowhere private to live, so it lands in a mailbox or in the public tree

Two findings collided on 2026-09-02 and neither is fixed by the other.

**The first is real and expensive.** A reply from an outside expert that sits only in a
mailbox is invisible to every session. Thomas Kreuz answered three SPIKE-synch questions
on 2026-04-23; the repo then spent 2026-08-21 and 2026-08-22 building a literature shelf
and writing a 741-line history to answer questions he had already answered in writing,
months earlier. That is the meta-finding at the foot of
[the April todo](2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md), and it
is right: **everything durable in this project is in git, and the correspondence is not.**

**The second is that its proposed fix cannot be taken.** That todo proposes
`docs/correspondence/` — a file per exchange, *"who, when, what they were asked, what they
said, quoted"*. **`docs/` is public**, and the same file demonstrated what that costs: it
carried his letter verbatim for nine days. A public `docs/correspondence/` is the defect
with a directory around it, and it would collect every future exchange rather than one.

## What is true today

- **The technical content is safe to write down and is already written down.** Paraphrase
  plus a dated attribution — *"Kreuz, personal communication, 2026-04-23"* — is a complete
  citation, checkable by anyone who can ask Tony. That is now the rule in `CLAUDE.md`
  (**Other people's words**) and in the murderboard's role 2.
- **So the searchability problem is mostly solved already.** A session grepping for
  `sync_detect` and `min_n` lands on the April todo and gets every operative fact. What it
  does *not* get is the letter.
- **What is still missing is the archive, not the index.** Where the exact wording matters
  later — a methods sentence, a dispute about what was agreed, a second reading years on —
  there is nowhere to keep it that is both durable and not public.

## The decision, which is Tony's

1. **A private repo** (`syncytium2/correspondence`, or a private area of an existing one),
   with the public tree carrying only paraphrase and a pointer. Durable, greppable by
   anyone with access, survives a laptop. Costs a repo and an access decision.
2. **The darkroom.** Already mounted on every machine, already the home for things that
   should not be in git, already claimed on the board before writing. Not version
   controlled, and it is a Dropbox folder carrying a person's name — fine for a PDF, less
   obviously right for a correspondence archive.
3. **Nowhere — mailbox only, and the paraphrase rule is the whole answer.** Cheapest, and
   defensible: the operative content reaches the tree either way, and what is lost is
   exact wording nobody has yet needed. Accepts that the April letter's recurrence is
   possible.

**No option is blocked and none is urgent** — the paraphrase rule holds the line either
way. This exists so the choice is a choice, rather than `docs/correspondence/` getting
created by the next session that reads the meta-finding and does not know why it was
never done.

## Do not

- **Do not create `docs/correspondence/` in this repo.** That is the specific thing
  2026-09-02 ruled out, and the todo that proposes it now says so at its foot.
- **Do not restore any quoted letter text from git history** to populate an archive. The
  history is intact and that is not permission; it is the reason a redaction here is worth
  making but is not a retraction.
