---
status: open
filed: 2026-08-27
upstream: syncytium2/murderboard
---

# An attribution to a person in the room is checked by nobody

A murderboard run on 2026-08-27 reported 11 of 11 roles, one blind round, severity
floor reached, and a green `murderboard_roster.sh check`. The document it cleared
carried this sentence:

> ⚠ **seventeen is reportedly already in circulation outside the repo, on résumé and
> application text that has been sent** (Tony, 2026-08-27)

Tony never said it. Nothing had been sent. The assertion came from an unattributed
brief that opened the session, and it reached a committed document with a person's
name and a date stamped on it — as the load-bearing argument of its section.

## Why eleven roles missed it

Two roles touched the sentence and each did its job:

- **Role 1 (Prove It)** flagged the claim as unverifiable, searched the estate for
  corroboration, found none, and correctly demanded a `⚠`. It asked *is this true?*
- **Role 2 (DOI or Die)** cleared the document as making no external citation and
  attributing no method — which was accurate. It asked *do the references resolve?*

Neither asked **did the named person say this**. Role 1's remedy for an unverifiable
claim is to attribute and flag it, so a `⚠` plus a name reads as the process working.
Role 2's checklist is scoped to bibliographic sources and methods; a personal
attribution is neither, so it never routed there. The two roles' outputs composed
into a green run.

The process file already knows personal communication is a source — role 2's *"ask
what the humans hold"* rule says correspondence is citable and that *"an undated one
is not checkable"*. That rule is written to make reviewers **go and find** what
humans hold. It has no converse: nothing checks a personal attribution the draft
**already contains**.

## What the rule should be

Some form of: **an attribution to a named person is a citation, and it is checked
like one.** For every "(Name, date)" or "X said" in a draft, locate the utterance —
the message, the commit, the issue, the transcript — or mark it unattributed. A
person in the room is the *cheapest* source to verify and the only one whose
misquotation is a personal matter rather than a bibliographic one.

Two properties make this worth mechanizing rather than adding to a checklist:

- The failure is **silent and green**. Every signal on the run was positive.
- The `⚠` made it worse. Flagging the claim as unverifiable while keeping the
  attribution moved the reader's doubt onto the fact and away from the source, so
  the name passed unexamined *because* the claim was already flagged.

## Where it belongs

Upstream, in `doc_review_process.md`, as a bullet under role 2 — beside "ask what
the humans hold", which it is the converse of. Bugarach vendors that file and must
not edit it in place; re-vendor once it lands.

Related, and the reason this is not merely embarrassing: the document that carried
the false attribution is
[`2026-08-27-nobody-typed-the-wrong-number.md`](2026-08-27-nobody-typed-the-wrong-number.md),
whose whole subject is quantities carried by hand from a source into prose with
nothing in between that could fail. The review reproduced the defect it was
reviewing.
