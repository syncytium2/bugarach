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
