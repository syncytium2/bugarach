"""A person's verdicts on the assessor's candidates, and what they license.

**The assessor proposes; a person disposes; and until 2026-08-24 nothing wrote
down the second half.** `assess_coactivity` returns candidate coordinated events —
their centres, their member ROIs — and the browser drew markers for them. Whether
a human agreed was held in a variable that died with the tab, which is what
[`docs/RESET.md`](../../docs/RESET.md) §1 means by *"an assessment is a record
containing a judgement, not a number with a caveat beside it"*.

## Why this is a sample and says so

Annotating everything is not available at any K. Measured on the approved export
folder, 84 recordings, both streams:

    K       fast    slow    both
    3      2,558   1,009   3,567
    4      1,375     752   2,127
    6        430     562     992
    8        174     467     641

and the spread is savage — fast at K=3 has a median of 8 per recording, a mean of
30.5, a maximum of 200, and 18 recordings with none at all. So the design Tony
chose (2026-08-24) is **a drawn sample plus an agreement rate**: a person judges
enough candidates to say what the machine's candidates are worth, that rate is
recorded per K, and the analyst reads K off it *having looked* rather than picking
it before looking.

**This makes K a measurement rather than a convention**, which is the thing
`docs/todo/2026-08-16-assessment-needs-a-human-in-the-loop.md` asked for and
`tools/derive_spec.py` still requires a bare `--k` for.

## What a verdict has to carry, and why the view is in it

A judgement is a property of (recording × rendering × observer), not of the
recording — RESET §1 again. A verdict recorded without the window it was made in
cannot be reproduced or disputed, so `view_t0`/`view_t1`, the ROI ordering and the
stream travel in every row. **A row missing them is refused at write time**, not
warned about.

## What this module does not do

- **It does not decide anything.** No default verdict, no auto-confirm, no
  threshold above which a candidate counts as agreed.
- **It does not filter recordings.** Which recordings are analysable is the
  producer's call, applied before the folder exists (CLAUDE.md).
- **It makes no viability claim.** A rejected candidate says a person did not
  think that moment was coordinated. It says nothing about the ROIs in it.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

#: Written where a value is absent, matching `emit.NA`.
NA = "NA"

#: The three things a person may say. **"unsure" is not a failure to answer** —
#: it is the answer for a candidate that cannot be judged from the view, and it is
#: kept out of BOTH sides of the agreement rate rather than counted as a rejection.
VERDICTS = ("confirmed", "rejected", "unsure")

#: Column order of `annotations.csv`.
COLUMNS = (
    "slice_id", "stream", "centre_sec", "k_survived", "n_members", "members",
    "span_sec", "jitter_sd_sec",
    "verdict", "annotator", "decided_at",
    "view_t0_sec", "view_t1_sec", "view_roi_order", "view_stream",
    "assess_bin_sec", "assess_surrogates", "assess_seed",
)

#: Columns that record what the person was looking at. Missing any of them makes
#: the row unreproducible, so writing is refused rather than warned about.
VIEW_COLUMNS = ("view_t0_sec", "view_t1_sec", "view_roi_order", "view_stream")


class ViewNotRecorded(ValueError):
    """A verdict arrived without the rendering it was made in."""


@dataclass
class Verdict:
    """One person's judgement of one candidate — one row of `annotations.csv`."""

    slice_id: str
    stream: str
    centre_sec: float
    """Absolute seconds on the recording's own clock, not window-relative. The
    browser's assessor returns centres relative to the window start; converting
    once, here, is why `view_t0_sec` is meaningful next to it."""
    k_survived: int
    """The highest K at which this candidate still exists. Candidates nest — a
    moment with 8 co-active ROIs also has 3 — so one verdict answers every K at or
    below this, which is what makes the per-K agreement table computable from a
    single pass."""
    n_members: int
    members: tuple[int, ...]
    span_sec: float
    """First-to-last participating event time in this candidate."""
    jitter_sd_sec: float
    """SD of the participating onsets — the assessor's tightness measure for this
    one cluster.

    **This and `span_sec` and `n_members` are here so the file can parameterise a
    simulation on its own.** The generator needs participation, span and jitter;
    if a verdict carried only yes-or-no, a later step would have to re-run the
    assessor and re-match candidates to verdicts by time, which is a join nobody
    should have to get right twice. Carrying the three numbers beside the verdict
    makes `annotations.csv` sufficient."""
    verdict: str
    annotator: str
    decided_at: str
    view_t0_sec: float
    view_t1_sec: float
    view_roi_order: str
    view_stream: str
    assess_bin_sec: float | None = None
    assess_surrogates: int | None = None
    assess_seed: int | None = None

    def __post_init__(self) -> None:
        if self.verdict not in VERDICTS:
            raise ValueError(
                f"verdict must be one of {VERDICTS}, got {self.verdict!r}")
        missing = [c for c in VIEW_COLUMNS if getattr(self, c) in (None, "")]
        if missing:
            raise ViewNotRecorded(
                f"{self.slice_id} at {self.centre_sec}s: no {', '.join(missing)}. "
                "A judgement is a property of (recording x rendering x observer); "
                "a verdict without the view it was made in cannot be reproduced "
                "or disputed (docs/RESET.md section 1).")
        if not np.isfinite(self.view_t0_sec) or not np.isfinite(self.view_t1_sec):
            raise ViewNotRecorded(
                f"{self.slice_id} at {self.centre_sec}s: the view bounds are not "
                "finite numbers")

    def row(self) -> dict[str, str]:
        out = {}
        for c in COLUMNS:
            v = getattr(self, c)
            if c == "members":
                out[c] = ";".join(str(int(m)) for m in v) if len(v) else NA
            elif v is None:
                out[c] = NA
            elif isinstance(v, float):
                out[c] = f"{v:.6g}"
            else:
                out[c] = str(v)
        return out


@dataclass
class Agreement:
    """How often a person agreed with the assessor, at one K."""

    k: int
    confirmed: int
    rejected: int
    unsure: int

    @property
    def judged(self) -> int:
        """Confirmed plus rejected. **`unsure` is not in the denominator** — a
        candidate a person could not judge is evidence about the view, not about
        the candidate."""
        return self.confirmed + self.rejected

    @property
    def rate(self) -> float:
        """Fraction of judged candidates a person confirmed, or NaN if none were
        judged. **NaN rather than 0.0**: no agreement measured is not agreement
        of zero, and a spec quoting 0% where nobody looked would be a claim
        nobody made."""
        return self.confirmed / self.judged if self.judged else float("nan")


def write_annotations(path: Path | str, verdicts, *, identity_cols=()) -> Path:
    """Write `annotations.csv`. Refuses an empty set rather than writing a header.

    An empty file is indistinguishable from "a person looked and confirmed
    nothing", which is a real and different result — the same reason
    `bugarach detect` refuses to write nothing.
    """
    verdicts = list(verdicts)
    if not verdicts:
        raise ValueError(
            "no verdicts to write. An empty annotations.csv cannot be told apart "
            "from a session where a person rejected everything, which is a "
            "finding rather than an absence.")
    path = Path(path)
    cols = list(COLUMNS) + list(identity_cols)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for v in verdicts:
            w.writerow(v.row())
    return path


def read_annotations(path: Path | str) -> list[Verdict]:
    """Read `annotations.csv` back, re-validating every row.

    Re-validation is the point: a file hand-edited into a state the writer would
    have refused is exactly what a later analysis must not silently consume.
    """
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        for i, r in enumerate(csv.DictReader(fh), start=2):
            mem = r.get("members", NA)
            members = tuple(int(x) for x in mem.split(";")) if mem != NA else ()
            try:
                out.append(Verdict(
                    slice_id=r["slice_id"], stream=r["stream"],
                    centre_sec=float(r["centre_sec"]),
                    k_survived=int(r["k_survived"]),
                    n_members=int(r["n_members"]), members=members,
                    span_sec=float(r["span_sec"]),
                    jitter_sd_sec=float(r["jitter_sd_sec"]),
                    verdict=r["verdict"], annotator=r["annotator"],
                    decided_at=r["decided_at"],
                    view_t0_sec=float(r["view_t0_sec"]),
                    view_t1_sec=float(r["view_t1_sec"]),
                    view_roi_order=r["view_roi_order"],
                    view_stream=r["view_stream"],
                    assess_bin_sec=_opt_float(r.get("assess_bin_sec")),
                    assess_surrogates=_opt_int(r.get("assess_surrogates")),
                    assess_seed=_opt_int(r.get("assess_seed")),
                ))
            except (KeyError, ValueError) as exc:
                raise ValueError(f"{path}, line {i}: {exc}") from exc
    return out


def _opt_float(v):
    return None if v in (None, "", NA) else float(v)


def _opt_int(v):
    return None if v in (None, "", NA) else int(v)


def agreement_by_k(verdicts, ks=(3, 4, 6, 8)) -> dict[int, Agreement]:
    """Per-K confirm rate, using the nesting of candidates.

    A candidate that survives to K=8 is also a candidate at K=3, so one verdict
    counts at every K at or below `k_survived`. That is what lets a person judge
    one list and read a scan off it.
    """
    out = {k: Agreement(k, 0, 0, 0) for k in ks}
    for v in verdicts:
        for k in ks:
            if v.k_survived >= k:
                a = out[k]
                setattr(a, v.verdict, getattr(a, v.verdict) + 1)
    return out


def confirmed_at(verdicts, k: int) -> list[Verdict]:
    """The confirmed candidates that exist at `k` — what a spec should be built
    from, in place of every candidate the machine proposed."""
    return [v for v in verdicts
            if v.verdict == "confirmed" and v.k_survived >= k]


def confirmed_summary(verdicts, k: int) -> dict:
    """The numbers a generator spec needs, over confirmed candidates only.

    **This is what annotation is for.** `tools/derive_spec.py` currently takes
    the medians over every candidate the assessor proposed; with a person's
    verdicts in hand it should take them over the ones that survived a look.

    `confirm_rate` is the multiplier for the event *frequency*: if a person
    believed 45% of what the machine proposed, the confirmed event rate is 45% of
    the machine's, and a simulator told the unfiltered rate plants roughly twice
    the coordination the recording is agreed to contain.

    Returns NaN medians rather than raising when nothing was confirmed at `k` —
    the caller has to decide whether that is "K is too strict" or "this folder has
    no agreed coordination", and those are different conversations.
    """
    conf = confirmed_at(verdicts, k)
    ag = agreement_by_k(verdicts, ks=(k,))[k]

    def _med(vals):
        vals = [v for v in vals if np.isfinite(v)]
        return float(np.median(vals)) if vals else float("nan")

    return dict(
        k=k,
        n_confirmed=len(conf),
        n_judged=ag.judged,
        n_unsure=ag.unsure,
        confirm_rate=ag.rate,
        part_n_med=_med([v.n_members for v in conf]),
        span_med=_med([v.span_sec for v in conf]),
        jitter_sd_med=_med([v.jitter_sd_sec for v in conf]),
    )


@dataclass
class Sample:
    """Which candidates a person was asked to judge, and how they were chosen."""

    picked: list                     # (slice_id, stream, index) triples
    seed: int
    budget: int
    per_recording_cap: int
    population: int
    """How many candidates existed to draw from. The pair (len(picked),
    population) is what a spec has to quote: a rate measured on 60 of 3,567 is a
    different claim from one measured on 60 of 60."""
    recordings_drawn: int
    recordings_available: int

    @property
    def coverage(self) -> float:
        return len(self.picked) / self.population if self.population else float("nan")


def draw_sample(candidates, *, seed: int, budget: int = 60,
                per_recording_cap: int = 8) -> Sample:
    """Choose which candidates to put in front of a person. Seeded, so the draw
    is part of the record rather than a thing that happened once.

    `candidates` is an iterable of `(slice_id, stream, index)` — whatever
    identifies one of the assessor's candidates.

    **Capped per recording, and that is the whole design.** On the approved
    folder one recording carries 200 candidates at K=3 where the median is 8, so
    an uncapped draw spends most of a person's attention on whichever recording
    happens to be busiest and reports an agreement rate that is really a
    statement about that one slice. The cap costs coverage and buys a rate that
    means something across the folder.

    **Recordings are visited in shuffled order**, so a budget that runs out does
    not systematically favour whatever the folder lists first.
    """
    if budget <= 0 or per_recording_cap <= 0:
        raise ValueError("budget and per_recording_cap must both be positive")
    rng = np.random.RandomState(seed)

    by_rec: dict[tuple[str, str], list] = {}
    for c in candidates:
        by_rec.setdefault((c[0], c[1]), []).append(c)
    population = sum(len(v) for v in by_rec.values())

    keys = sorted(by_rec)                       # sorted first, so the shuffle —
    order = rng.permutation(len(keys))          # and only the shuffle — is the
    picked: list = []                           # source of order
    drawn = 0
    for i in order:
        if len(picked) >= budget:
            break
        pool = by_rec[keys[i]]
        take = min(per_recording_cap, len(pool), budget - len(picked))
        if take <= 0:
            continue
        idx = rng.choice(len(pool), size=take, replace=False)
        picked.extend(pool[j] for j in sorted(idx))
        drawn += 1

    return Sample(picked=picked, seed=seed, budget=budget,
                  per_recording_cap=per_recording_cap, population=population,
                  recordings_drawn=drawn, recordings_available=len(by_rec))


# --------------------------------------------------------------------------
# K, derived from what a person accepted rather than picked off a scan
# --------------------------------------------------------------------------

#: A proposal list may not be censored at or above the floor it is being used to
#: estimate. If the machine only ever proposed moments with 3+ co-active ROIs and
#: a person confirmed from that list, the smallest K the data can speak about is
#: 3 — and "K is 3" is then the assumption returning under a new name. Same
#: circularity `docs/RESET.md` §1 caught in the validation test, so the estimate
#: refuses a list whose smallest judged candidate sits above this.
#: `docs/todo/2026-08-28-derive-k-from-confirmed-events.md`, "The trap".
MAX_PROPOSAL_FLOOR = 2

#: Below this separation the co-active count is not what the expert was judging
#: on. That is a finding about the assessor rather than a value of K, so it comes
#: back as "not identified" with the quality attached, never as a number.
MIN_SEPARATION = 0.30

#: Two thresholds whose separation differs by less than this are not
#: distinguishable by these labels. The width of that band is reported, because a
#: wide one says what a low separation says, more legibly.
BAND_TOLERANCE = 0.05

#: Fewer judged candidates than this and the estimate is noise. Not a
#: significance test — a floor below which the curve is a handful of points and
#: the argmax moves with one relabelled candidate.
MIN_JUDGED = 20

#: And at least this many on EACH side. Twenty confirmations and no rejections
#: cannot locate a boundary: every threshold at or below the smallest confirmed
#: count scores identically, and the argmax is then tie-breaking rather than
#: measurement.
MIN_PER_SIDE = 3


@dataclass
class KEstimate:
    """K as a threshold chosen against labelled calls, and how well it separates.

    **A bare integer is not the output.** The design asks for K "reported with its
    separation quality rather than as a bare integer", because the interesting
    failure is not a wrong K — it is a K that does not separate, which says the
    co-active count is not the quantity the expert is judging and that the
    assessor is measuring the wrong thing.
    """

    k: int | None
    """The threshold that best separates confirmed from rejected, ties to the
    smaller K. ``None`` whenever the estimate is not identified."""
    separation: float
    """Youden's J — sensitivity + specificity − 1. Chance is 0, perfect is 1.
    Deliberately not accuracy: how many candidates are confirmed and how many
    rejected is set by how the sample was drawn, so a prevalence-weighted score
    would be reporting the sampling design back."""
    band: tuple[int, int] | None
    """Lowest and highest threshold within :data:`BAND_TOLERANCE` of the best. A
    band wider than one or two values is the finding, not a detail."""
    curve: dict[int, float]
    """Threshold -> separation, so a caller can show what was not chosen. The scan
    is the evidence; the argmax is one reading of it."""
    n_confirmed: int
    n_rejected: int
    n_unsure: int
    """Excluded from the fit, and reported, for the reason
    :attr:`Agreement.judged` excludes it: a candidate a person could not judge is
    evidence about the view, not about the candidate."""
    proposal_floor: int | None
    """Smallest co-active count among judged candidates — what the proposal stage
    let through, checked against :data:`MAX_PROPOSAL_FLOOR`."""
    confirmed_median: float
    rejected_median: float
    identified: bool
    why: str
    """Why it is or is not identified, in a sentence a person can act on. Always
    populated, success included."""
    annotators: tuple[str, ...] = ()
    """Who labelled. **K inherits whoever labelled** — one observer gives one K,
    and a second observer on a subset is what says whether it is stable or is a
    fact about one person (RESET §1: a judgement is a property of recording ×
    rendering × observer)."""

    def __bool__(self) -> bool:
        return self.identified


def _separation(judged, k: int) -> float:
    """Youden's J for the rule *confirmed iff n_members >= k*."""
    tp = sum(1 for v in judged if v.verdict == "confirmed" and v.n_members >= k)
    fn = sum(1 for v in judged if v.verdict == "confirmed" and v.n_members < k)
    fp = sum(1 for v in judged if v.verdict == "rejected" and v.n_members >= k)
    tn = sum(1 for v in judged if v.verdict == "rejected" and v.n_members < k)
    sens = tp / (tp + fn) if (tp + fn) else 0.0
    spec = tn / (tn + fp) if (tn + fp) else 0.0
    return sens + spec - 1.0


def derive_k(verdicts) -> KEstimate:
    """Estimate K from a person's verdicts instead of taking it as an input.

    Every proposed moment carries an observed co-active count and, after review, a
    human verdict; K is the count that best separates the two. This is the step
    that makes the human-in-the-loop claim operational. Until it exists K is a
    number somebody chose off a scan, and everything downstream inherits the
    choice: the generator's cluster rate, the simulated data set, the operating
    points fitted against it, and every F1 quoted from them.

    **It refuses more often than it answers, and each refusal is a different
    conversation.** A censored proposal list, too few labels, labels all on one
    side, and a count that does not separate are four distinct findings; returning
    a plausible integer for any of them would be this project's own failure class,
    a plausible answer instead of an error.

    **What comes back is a recorded judgement, never ground truth.** RESET §10
    reserves that phrase for planted events in simulation. These are the calls,
    the view they were made in, and who made them.
    """
    verdicts = list(verdicts)
    judged = [v for v in verdicts if v.verdict in ("confirmed", "rejected")]
    n_unsure = sum(1 for v in verdicts if v.verdict == "unsure")
    n_conf = sum(1 for v in judged if v.verdict == "confirmed")
    n_rej = len(judged) - n_conf
    who = tuple(sorted({v.annotator for v in verdicts if v.annotator}))

    def _med(vals):
        vals = [float(x) for x in vals if np.isfinite(x)]
        return float(np.median(vals)) if vals else float("nan")

    conf_med = _med([v.n_members for v in judged if v.verdict == "confirmed"])
    rej_med = _med([v.n_members for v in judged if v.verdict == "rejected"])
    floor = min((int(v.n_members) for v in judged), default=None)

    def _no(why: str) -> KEstimate:
        return KEstimate(
            k=None, separation=float("nan"), band=None, curve={},
            n_confirmed=n_conf, n_rejected=n_rej, n_unsure=n_unsure,
            proposal_floor=floor, confirmed_median=conf_med,
            rejected_median=rej_med, identified=False, why=why, annotators=who)

    if len(judged) < MIN_JUDGED:
        return _no(
            f"only {len(judged)} judged candidate(s), and {MIN_JUDGED} is the "
            f"floor below which the curve is a handful of points and the argmax "
            f"moves with one relabelled candidate. Annotate more before reading "
            f"a K off this.")
    if n_conf < MIN_PER_SIDE or n_rej < MIN_PER_SIDE:
        return _no(
            f"{n_conf} confirmed and {n_rej} rejected, and a boundary needs at "
            f"least {MIN_PER_SIDE} on each side. With one side that thin every "
            f"threshold scores alike and the argmax is tie-breaking rather than "
            f"a measurement.")
    if floor is not None and floor > MAX_PROPOSAL_FLOOR:
        return _no(
            f"the proposal list was censored at {floor} co-active ROI — nothing "
            f"below that was ever offered for judgement, so the smallest K these "
            f"labels can speak about is {floor}, and \"K is {floor}\" would be "
            f"the assumption returning under a new name. Propose at "
            f"K={MAX_PROPOSAL_FLOOR} or with no floor at all and annotate again "
            f"(the trap in "
            f"docs/todo/2026-08-28-derive-k-from-confirmed-events.md).")

    counts = sorted({int(v.n_members) for v in judged})
    curve = {k: _separation(judged, k) for k in range(counts[0], counts[-1] + 1)}
    best = max(curve.values())
    k = min(kk for kk, j in curve.items() if j == best)
    within = sorted(kk for kk, j in curve.items() if j >= best - BAND_TOLERANCE)
    band = (within[0], within[-1])

    if best < MIN_SEPARATION:
        return _no(
            f"the best threshold separates confirmed from rejected at only "
            f"J={best:.2f}, where chance is 0. The co-active count is not what "
            f"the expert is judging on, which is a finding about the assessor "
            f"rather than a value of K — confirmed median {conf_med:.1f} "
            f"co-active against rejected median {rej_med:.1f}.")

    wide = "" if band[1] - band[0] <= 2 else (
        f" The band is wide ({band[0]}–{band[1]}): these labels do not "
        f"distinguish those thresholds, so quote the band and not the point.")
    return KEstimate(
        k=k, separation=best, band=band, curve=curve,
        n_confirmed=n_conf, n_rejected=n_rej, n_unsure=n_unsure,
        proposal_floor=floor, confirmed_median=conf_med, rejected_median=rej_med,
        identified=True, annotators=who,
        why=(f"K={k} separates {n_conf} confirmed from {n_rej} rejected at "
             f"J={best:.2f}, proposed from a floor of {floor} co-active ROI, "
             f"labelled by {', '.join(who) or 'an unnamed annotator'}.{wide}"))
