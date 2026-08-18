"""Which animal, which group, and is this slice excluded — from the lab's workbook.

⚠ **This module is a bridge, not architecture, and it should be deleted rather than
extended.** Everything an analysis needs belongs in the folder the app reads.
Experimental group does not: it lives in a spreadsheet on a Dropbox mount, so a
corpus result computed through this module can only be reproduced on a machine that
happens to hold that file. The fix is a revision to the import contract — the
reasoning, the proposed columns, and the contradiction that makes the current spec
unable to satisfy FOUNDATIONS §9 are in
``docs/todo/2026-08-18-experimental-groups-are-not-in-the-import-contract.md``.
What follows is written to be replaced by ``slices.csv``.


A slice id alone cannot answer whether a result is admissible. FOUNDATIONS §9 says
effects run in opposite directions by group and a pooled across-group number is not
admissible on its own, so every corpus-level claim needs the group of each slice.
The lab keeps that in ``indiegroups_db4.xlsx``, and MATLAB has read it for years
(``interface2/groupData.m``) — this is the same table, read the same way, from
Python.

**Three things it carries that an analysis gets wrong without it.**

- **``exclude``.** Slices the lab has withdrawn. Nothing in this repo consulted the
  column before 2026-08-18, so every corpus result computed here up to that date
  silently included them.
- **``mouse_id``.** Slices are not independent — one animal contributes up to three,
  and 85 slices come from 48 dates. A per-slice count overstates how many
  independent observations stand behind it, and any combination of per-slice
  p-values is anti-conservative. ``by_animal`` is the honest unit.
- **``study``.** Pilot arms (``pilot-no-sham``, ``pilot-cadmium``) and the
  APV+CNQX / GABAZINE arms are marked here. They are not part of the main corpus and
  must be dropped from anything reported as the corpus.

**Where the file is, and why it is not written down.** The workbook lives in a
personal Dropbox path that carries a person's name, and this repo is public — sapper
SAP004 blocks that string from a tracked file. So the location is resolved, never
hardcoded, in this order:

1. ``BUGARACH_GROUPS_XLSX`` — an explicit answer always wins.
2. ``$BUGARACH_DATA_ROOT/indiegroups_db4.xlsx``.

Then ``None``, and the caller says so and skips rather than guessing. Finding is not
guessing: a wrong workbook would attach the wrong group to every slice, and a group
result is worse than useless if its labels are wrong.

**Timing is checked, not assumed.** The workbook's ``exp_timing`` sheet carries each
experiment's baseline window in MINUTES. ``check_baseline_windows`` compares it
against what the store's own region records say. On 2026-08-18 all 85 slices agreed
within one second, which is the evidence that the two sources describe the same
recordings — a check worth keeping, because if they ever diverge every window-based
number in this repo is measuring something the lab did not intend.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

__all__ = ["SliceMeta", "workbook_path", "load_groups", "load_timing",
           "check_baseline_windows", "by_animal", "MAIN_CORPUS_STUDIES"]

ENV_EXPLICIT = "BUGARACH_GROUPS_XLSX"
ENV_ROOT = "BUGARACH_DATA_ROOT"
WORKBOOK_NAME = "indiegroups_db4.xlsx"

#: A blank ``study`` cell means the main corpus. Every non-blank value names a
#: side arm — the pilots and the APV+CNQX / GABAZINE variants — and is excluded
#: from anything reported as "the corpus".
MAIN_CORPUS_STUDIES = (None, "")


@dataclass(frozen=True)
class SliceMeta:
    slice_id: str
    group: str | None
    """DI · MALE · OVX · ORX, the lab's own vocabulary."""
    mouse: object
    """The independence unit. Several slices share one."""
    excluded: bool
    study: str | None
    """None/blank for the main corpus; otherwise a side arm to drop."""
    treat: str | None
    """What this slice later received. Irrelevant to a BASELINE-only analysis,
    and carried so a caller restricting to one arm can do so without re-reading
    the workbook."""
    notes: str
    provisional: bool
    """The lab has marked something about this row as not final. Not an exclusion
    — a caveat to carry into any claim that rests on this slice's group."""

    @property
    def in_main_corpus(self) -> bool:
        return (not self.excluded) and (self.study in MAIN_CORPUS_STUDIES)


def workbook_path() -> Path | None:
    """Resolve the workbook, or ``None``. Never guesses."""
    explicit = os.environ.get(ENV_EXPLICIT, "").strip()
    if explicit:
        p = Path(explicit)
        return p if p.is_file() else None
    root = os.environ.get(ENV_ROOT, "").strip()
    if root:
        p = Path(root) / WORKBOOK_NAME
        return p if p.is_file() else None
    return None


def unresolved_message() -> str:
    return (f"group workbook not found — set {ENV_EXPLICIT} to {WORKBOOK_NAME}, "
            f"or {ENV_ROOT} to the folder holding it. Without it a corpus result "
            f"cannot be split by group, and FOUNDATIONS §9 does not admit a "
            f"pooled across-group number on its own.")


def _sheet(path: Path, name: str):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = list(wb[name].iter_rows(values_only=True))
    hdr = {str(h).strip(): i for i, h in enumerate(rows[0]) if h is not None}
    return hdr, rows[1:]


def load_groups(path: Path | None = None) -> dict[str, SliceMeta]:
    """``slice_id -> SliceMeta`` from the ``indiegroups`` sheet."""
    path = path or workbook_path()
    if path is None:
        raise FileNotFoundError(unresolved_message())
    ix, rows = _sheet(Path(path), "indiegroups")
    out: dict[str, SliceMeta] = {}
    for r in rows:
        eid = r[ix["experiment_id"]]
        if eid in (None, ""):
            continue
        def cell(col):
            return r[ix[col]] if col in ix else None
        notes = str(cell("notes")).strip() if cell("notes") else ""
        study = cell("study")
        out[str(eid).strip()] = SliceMeta(
            slice_id=str(eid).strip(),
            group=str(cell("group_id")).strip() if cell("group_id") else None,
            mouse=cell("mouse_id"),
            excluded=cell("exclude") not in (None, "", 0),
            study=str(study).strip() if study not in (None, "") else None,
            treat=str(cell("treat")).strip() if cell("treat") else None,
            notes=notes,
            provisional="PROVISIONAL" in notes.upper(),
        )
    return out


def load_timing(path: Path | None = None) -> dict[str, tuple[float, float]]:
    """``slice_id -> (baseline_start_sec, baseline_end_sec)`` from ``exp_timing``.

    The sheet records minutes; this returns seconds, because every window in this
    codebase is seconds and a unit that changes at a boundary is how a window ends
    up 60x wrong without anything failing.
    """
    path = path or workbook_path()
    if path is None:
        raise FileNotFoundError(unresolved_message())
    ix, rows = _sheet(Path(path), "exp_timing")
    out: dict[str, tuple[float, float]] = {}
    for r in rows:
        eid = r[ix["experiment_id"]]
        s, e = r[ix["baseline_start"]], r[ix["baseline_end"]]
        if eid in (None, "") or s is None or e is None:
            continue
        out[str(eid).strip()] = (float(s) * 60.0, float(e) * 60.0)
    return out


def check_baseline_windows(observed: dict[str, float], *, tol_sec: float = 1.0,
                           path: Path | None = None) -> dict:
    """Compare measured baseline window DURATIONS (seconds) against the workbook.

    ``observed`` is ``slice_id -> duration_sec`` as the analysis actually used it.
    Returns counts and the disagreements, so a caller can refuse to report rather
    than quietly analysing a window the lab did not intend.
    """
    timing = load_timing(path)
    agree, missing, disagree = [], [], []
    for sid, dur in observed.items():
        t = timing.get(str(sid))
        if t is None:
            missing.append(sid)
            continue
        want = t[1] - t[0]
        (agree if abs(want - float(dur)) <= tol_sec
         else disagree).append(sid if abs(want - float(dur)) <= tol_sec
                               else (sid, float(dur), want))
    return {"n": len(observed), "agree": len(agree), "missing": missing,
            "disagree": disagree}


def by_animal(records, meta: dict[str, SliceMeta], *, hit) -> dict[str, dict]:
    """Collapse per-slice records to per-animal counts, grouped by experimental group.

    ``hit`` is a predicate on a record. An animal counts as showing the effect if
    ANY of its slices does — the weakest defensible rule, chosen because the
    alternative (all slices) would let one thin slice veto an animal.
    """
    per_mouse: dict[object, dict] = {}
    for rec in records:
        m = meta.get(str(rec["slice_id"]))
        if m is None:
            continue
        d = per_mouse.setdefault(m.mouse, {"group": m.group, "any": False,
                                           "slices": 0, "slice_hits": 0})
        d["slices"] += 1
        if hit(rec):
            d["any"] = True
            d["slice_hits"] += 1
    out: dict[str, dict] = {}
    for d in per_mouse.values():
        g = out.setdefault(d["group"], {"animals": 0, "animals_hit": 0,
                                        "slices": 0, "slice_hits": 0})
        g["animals"] += 1
        g["animals_hit"] += int(d["any"])
        g["slices"] += d["slices"]
        g["slice_hits"] += d["slice_hits"]
    return out
