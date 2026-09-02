# Second note to Thomas Kreuz — open, copy, send

Paste-ready and unwrapped on purpose: no backticks, no hard wrapping, no tool
between this file and a mail client. Edit it in the mail, not here.

Why it exists: the PySpike PR went out on 2026-09-01 with his private mail quoted
verbatim in the description. It was removed about seventy-five minutes later, but
GitHub retains the edit history of a PR body, so the original is still one click
away for anyone who looks. He was never asked. Send as a reply on the existing
thread so it lands in context.

---

Subject: Re: oddity in PySpike — PR is open, and an apology

Thomas,

The PR is in: https://github.com/mariomulansky/PySpike/pull/89

An apology first. When I opened it, the description quoted your mail to me directly — your reading that tau_max stopped being tracked in the new get_tau in v0.8.0, your go-ahead to send it to Mario, and your point about giving users the options rather than imposing one variant. You wrote all of that to me in a private exchange and I put it in a public thread without asking you. That was my mistake and I am sorry for it.

I have taken it out. The description now argues from the code and the published papers only, and says nothing about our correspondence. The commit message named you too, and I rewrote that.

What I cannot undo, and would rather tell you than have you find: GitHub keeps both. The pull request description has an edit history anyone can open, and the superseded commit is still fetchable by its hash. So the original text is not really retracted, only no longer the version on display. It was the live version for a little over an hour and drew no comments or reviews in that time.

If you would rather this were handled differently — a note from me in the thread, or asking Mario to delete the PR so it can be reopened clean — say the word and I will do it.

On the substance, nothing has changed from what you saw. The patch bounds the returned window by max_tau/2 inside get_tau, since that function receives the already-doubled true_max; at MRTS = 0 it is the same function 0.7.0 computed. It adds test/test_max_tau.py, which pins the case the suite could not previously express — six caps against six pair separations, every expected value a sixth you can count by hand. Upstream's suite goes from 50 tests to 56, green on both backends.

Two things in it you have not seen, both flagged in the description as behaviour changes rather than slipped in. Under MRTS > 0 the cap now also bounds an MRTS-raised window; I take that to be right, since your 2017 paper introduces tau_max alongside the adaptive detection rather than instead of it, and Satuvuori's Eqs. 17-18 already limit each side to half the ISI. And with a tight cap, filter_by_spike_sync can now empty a train, which makes an existing crash in spike_directionality easier to reach — pre-existing, and I have offered to file it separately.

Thanks again for looking at this so quickly.

--Tony
