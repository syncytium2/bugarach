# SAP017 — "freshly chosen", and the habit of reaching for an adjective

**Filed with the rule.** A one-phrase ban is a small rule; the reason it earned a BLOCK is that it was
the *third* word tried for the same idea in a single review.

## The ruling

Tony, 2026-09-16, reading a figure caption:

> "freshly chosen" is hereby banned in perpetuity

The caption said each program ran at its stored setting, *"not at the freshly chosen setting of Figure
14."*

## What is wrong with it

**"Freshly" is an adjective doing a noun's work.** It carries a whiff of approval — fresh is better than
stale — while answering none of the questions the sentence raises: chosen *by whom*, *out of what*, and
*how many times*?

All three mattered here, and the phrase concealed the most important one. Figure 14's rounds pick **one
setting per round**, from held-out simulated recordings. There are four rounds, and **four of the six
detectors' rounds disagreed with each other** — locust's picks ranged from 99.9 to 99.9999, a
thousandfold spread, off the same 24 recordings. "The freshly chosen setting" is a singular noun phrase
for something that does not exist in the singular. A reader who asked the obvious next question —
*why not just use that setting, then?* — would have been asking about a value that was never there.

## Why a BLOCK and not a warning

Three words were tried for one idea in one review, and all three failed differently:

| word | what happened |
| --- | --- |
| **shipped** | accurate, and banned as jargon (review note 1) |
| **default** | plain, and false — it named library defaults as the thing the project runs (note 30) |
| **freshly chosen** | plain and true, and decorative — it flattered the value and hid the procedure (note 35) |

The common cause is not vocabulary. It is **reaching for an adjective instead of naming the procedure.**
An adjective is cheap, fits the line, and reads fine; naming the procedure forces the writer to know it.
The repair is always the same: *"the setting each round picked from the recordings it was allowed to
see."* Longer, and it makes the disagreement between rounds sayable.

## Scope

Tree-wide, because a ban in perpetuity that covers one document is not a ban in perpetuity. Exempt:
`tools/sapper.py`, `docs/sapper_feedback/**` and `docs/reviews/**` — the three places whose job is to
record what was banned and why.

The pattern also catches `freshly picked`, `freshly selected`, `freshly tuned` and the hyphenated forms.
It deliberately does **not** catch "fresh" alone: a fresh copy of a recording is a fine thing to say.

## What it cannot catch

The habit, which has no fixed shape. Sibling forms a line matcher will not see:

- **"the better setting"**, **"the proper value"** — approval smuggled in as an adjective.
- **"the optimal setting"** where several were computed and they disagree.
- Any singular noun phrase for a thing that exists only in the plural. This is the real fault and it is
  not mechanizable; it needs someone who knows how many of the thing there are.

For those, the check is a reader asking *"which one?"* — which is exactly how this was caught.
