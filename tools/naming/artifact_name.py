#!/usr/bin/env python3
# vendored from syncytium2/armory @ 4cefdb2 (tools/naming/). This file is a COPY, and so are
# codes.json and cases.json beside it: edits here are overwritten whenever they are
# re-vendored. Change a code in armory's codes.json and re-vendor all three together.
# instrument: retrieval
"""artifact_name — build, check and audit output filenames against the estate scheme.

    Export folders and their data files have their own layout: README.md "Exports",
    `build --type export`, `build-file`, `parse PATH`, `check-export DIR`.

    [<source>_]<type>_<signal>_<stream>_<treatment>_<groups>_<win>_<date>[_v<N>].<ext>
    synth_<type>_<form>[_<stream>][_<treatment>][_<groups>][_<win>][_<topic>]_<date>[_v<N>][.<ext>]

    raster_roi_combined_senktide-ttx_di_win20min_20261007.html
    pilot-20260811_raster_roi_combined_apv+cnqx+gz_male_win20min_20261006.html

The scheme itself, and why each rule is there, is README.md beside this file. This tool is
the only thing that should ever spell a name: producers call `build`, nobody types one.

WHY THIS EXISTS. On 2026-10-06 a page went outside the lab as `ALL_APV+CNQX+GZ_combined.html`.
`ALL` meant "every group, as separate rows" and `combined` meant a specific stream, and a reader
outside could recover neither. bugarach built that name by hand at one f-string
(tools/make_group_raster_summary.py:934). Four producers (interface2, bugarach, fireflies,
colonel_kernel) in three languages each build names their own way, so the fix is one builder
and one list of codes, not a style guide.

ONE IMPLEMENTATION, CALLED FROM EVERY LANGUAGE. interface2 is MATLAB and fireflies is R. A
second and third implementation would drift from this one the same way the treatment
dictionaries did (interface2 CLAUDE.md: `^ap`/`^ga` were in R and missing from MATLAB for five
days). So R and MATLAB shell out to `build`, and the parity question never arises:

    R:       system2("python3", c(tool, "build", "--type", "raster", ...), stdout = TRUE)
    MATLAB:  [st, out] = system(sprintf('python3 "%s" build --type raster ...', tool));

THE CODES ARE DATA. codes.json lists every code with its full name and the spellings each
producer already uses (`DiIVF`, `diestrus`, `TTX`), so a producer can pass its own label and
get the canonical code back. Adding a code is a one-line data change, reviewed like any other.

  python3 artifact_name.py build --type raster --signal roi --stream combined --treatment apv+cnqx+gz \\
          --groups di --win win20min --ext html [--source pilot-20260811] [--date 20261007]
  python3 artifact_name.py check NAME [NAME ...]        exit 1 if any name fails
  python3 artifact_name.py audit DIR [--days N]         list non-conforming files under DIR
  python3 artifact_name.py --selftest
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
CODES = pathlib.Path(os.environ.get("ARMORY_NAMING_CODES", HERE / "codes.json"))
CASES = HERE / "cases.json"

MAX_LEN = 100
LIST_FIELDS = ("stream", "treatment", "groups", "moco")
LIST_KINDS = {"stream": "streams", "treatment": "treatments", "groups": "groups", "moco": "mocos"}
# every field between type and date, in the order a name writes them
FIELD_ORDER = ("form", "topic", "signal", "stream", "treatment", "groups", "win", "thr", "moco", "review")
# A topic is free words, not a registered code: an explainer is about an idea, and ideas are
# not a closed list. Lowercase words joined by hyphens, at most this many.
TOPIC_WORDS = 6
# one registered code, no operators
SINGLE = {"signal": "signals", "win": "windows", "thr": "thresholds", "review": "reviews",
          "form": "forms"}
# which separators each list field may use. `-` keeps things separate (side by side), `+`
# pools them into one, `-then-` is a sequence of treatment stages and means nothing elsewhere.
OPERATORS = {"stream": {"-"}, "groups": {"-", "+"}, "treatment": {"-", "+", "-then-"},
             "moco": {"+"}}
# What an export's data files may carry after their table code, in this order. Each is ONE
# code: a file holds one stream and one window. (README "Exports".)
FILE_FIELDS = (("stream", "streams"), ("win", "windows"), ("keep", "keeps"))
CODE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LIST_CODE_RE = re.compile(r"^[a-z0-9]+$")   # no hyphen: in a list field every `-` separates
DATE_RE = re.compile(r"^\d{8}$")
VERSION_RE = re.compile(r"^v([2-9]|[1-9]\d+)$")
EXT_RE = re.compile(r"^[a-z0-9]+$")
# What a person is handed: rendered pages, figures and documents. Data tables (csv, json),
# fixed contract files and sidecars are inputs to the next tool, not deliverables, and a
# check that counted them reported 4,485 failures where far fewer were fixable (2026-10-07).
DELIVERABLES = ("html", "png", "pdf", "svg", "pptx", "docx", "xlsx", "tif", "tiff", "eps")
# Folders whose contents are not ours to name: other people's papers (`lit`), and work moved
# out of the way unchanged (`archive`), which is renamed when it next goes out, not before.
SKIP_DIRS = ("archive", "lit")


class NameError_(ValueError):
    """A name, or a request to build one, that breaks the scheme. The message says how."""


# ----------------------------------------------------------------------------- the code list

def load_codes(path=CODES):
    raw = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    reg = {"banned": set(raw["banned"]), "reserved": set(raw["reserved"]),
           "sources": {}, "default_fields": raw["default_fields"], "type_fields": {},
           "type_optional": {}, "table_fields": {},
           "default_optional": set(raw.get("default_optional", [])),
           "export_files": raw["export_files"], "export_rules": raw["export_rules"]}
    problems = []
    for kind in ("types", "forms", "signals", "streams", "treatments", "groups", "windows",
                 "thresholds", "mocos", "reviews", "keeps", "tables"):
        entries, alias, compound = [], {}, {}
        for e in raw[kind]:
            code = e["code"]
            pattern = LIST_CODE_RE if kind in LIST_KINDS.values() else CODE_RE
            if not pattern.match(code):
                problems.append(f"{kind}: {code!r} is not a valid code here")
            if code in reg["banned"] or code in reg["reserved"]:
                problems.append(f"{kind}: {code!r} is a banned or reserved word")
            entries.append(code)
            if kind == "types" and "fields" in e:
                # a deliverable that is not about a dataset (an explainer) has its own layout
                reg["type_fields"][code] = e["fields"]
                opt = e.get("optional", [])
                # an optional field is found by counting fields, so a type may have one
                if len(opt) > 1 or not set(opt) <= set(e["fields"]):
                    problems.append(f"type {code!r}: at most one optional field, from its fields")
                reg["type_optional"][code] = set(opt)
            if kind == "tables":
                reg["table_fields"][code] = e["fields"]
            for a in [code, *e.get("aliases", [])]:
                key = a.lower().replace(" ", "")
                if alias.get(key, code) != code:
                    problems.append(f"{kind}: alias {a!r} names both {alias[key]} and {code}")
                alias[key] = code
                if "+" in a or " " in a:        # e.g. "high K+": rewritten before splitting on +
                    compound[a.lower()] = code
                    compound[key] = code
        reg[kind] = entries                 # list order IS the canonical order
        reg[kind + "_alias"] = alias
        reg[kind + "_compound"] = compound
    for s in raw["sources"]:
        s["optional"] = set(s.get("optional", []))
        if s.get("flexible") and not set(s.get("required", [])) <= set(s["fields"]):
            problems.append(f"source {s['code']!r}: required fields must be among its fields")
        reg["sources"][s["code"]] = s
        if s["code"] in reg["types"]:
            problems.append(f"source {s['code']!r} is also a type: the first field would be ambiguous")
    for t in reg["types"]:
        if t.startswith(("pilot-", "pilots-")) or t in ("pilot", "pilots"):
            problems.append(f"type {t!r} collides with the pilot source pattern")
    if problems:
        raise NameError_("codes.json is inconsistent:\n  " + "\n  ".join(problems))
    return reg


PILOT = r"(\d{8})(b|c|d)?"


def source_spec(reg, token):
    """The source a first field names, or None if it is not a source (so it is the type)."""
    if token in reg["sources"]:
        return reg["sources"][token]
    m = re.fullmatch(r"pilot-" + PILOT, token)
    if m:
        _date(m.group(1), "pilot start date")
        return reg["sources"]["pilot"]
    if token.startswith("pilots-"):
        if canonical_source(token) != token:
            raise NameError_(f"source {token!r} should be written {canonical_source(token)!r}")
        return reg["sources"]["pilots"]
    return None


def canonical_source(source):
    """The source field as it must be written. Several pilots become ONE field,
    `pilots-<day>-<day>[...]`, oldest first: a deliverable that sets studies side by side
    (2026-10-14: the coordinated fraction of the August and September pilots on one page).

    Accepts the canonical form in any order, or the pilots' own codes separated by commas or
    spaces. Refuses a single pilot (that is `pilot-<day>`) and a pilot named twice."""
    s = source.strip().lower()
    if s.startswith("pilots-"):
        days = s[len("pilots-"):].split("-")
    elif re.search(r"[,\s]", s):
        days = []
        for tok in re.split(r"[,\s]+", s):
            if not re.fullmatch(r"pilot-" + PILOT, tok):
                raise NameError_(f"{tok!r} is not a pilot: only pilots can share a source field")
            days.append(tok[len("pilot-"):])
    else:
        return s
    for d in days:
        m = re.fullmatch(PILOT, d)
        if not m:
            raise NameError_(f"{d!r} in {source!r} is not a pilot's day (YYYYMMDD, maybe b/c/d)")
        _date(m.group(1), "pilot start date")
    if len(days) < 2:
        raise NameError_(f"{source!r} names one pilot: write it pilot-{days[0] if days else '<day>'}")
    if len(set(days)) != len(days):
        raise NameError_(f"{source!r} names the same pilot twice")
    return "pilots-" + "-".join(sorted(days))


def _date(s, what="date"):
    if not DATE_RE.match(s):
        raise NameError_(f"{what} {s!r} is not YYYYMMDD")
    try:
        dt.datetime.strptime(s, "%Y%m%d")
    except ValueError:
        raise NameError_(f"{what} {s!r} is not a real calendar date") from None
    return s


# ----------------------------------------------------------------------------- list fields

def _split_list(field, value):
    """'apv+cnqx-then-gz' -> [[['apv','cnqx'], ['gz']]]: sides, each a list of stages, each a pool."""
    sides = []
    for side in value.split("-") if "-then-" not in value else _split_sides_with_then(value):
        stages = side.split("-then-") if field == "treatment" else [side]
        sides.append([stage.split("+") for stage in stages])
    return sides


def _split_sides_with_then(value):
    # protect `-then-` while splitting sides on the remaining hyphens
    marker = "\x00"
    return [s.replace(marker, "-then-") for s in value.replace("-then-", marker).split("-")]


def canonical_list(reg, field, value):
    """Resolve aliases, put codes in canonical order, and return the field as it must be written."""
    kind = LIST_KINDS[field]
    alias, order = reg[kind + "_alias"], reg[kind]
    v = value.strip()
    v = v.lower()
    if field == "moco":         # "mixed" is a pool of both kinds, and is written as one
        v = reg["export_rules"]["moco_pools"].get(v.replace(" ", ""), v)
    for a in sorted(reg[kind + "_compound"], key=len, reverse=True):
        v = v.replace(a, reg[kind + "_compound"][a])
    if not v:
        raise NameError_(f"{field} is empty")
    if "+" in v and "+" not in OPERATORS[field]:
        raise NameError_(f"{field} cannot pool with '+'")
    if "-" in v.replace("-then-", "") and "-" not in OPERATORS[field]:
        raise NameError_(f"{field} cannot list things side by side with '-'")
    if "-then-" in v and "-then-" not in OPERATORS[field]:
        raise NameError_(f"'-then-' (a sequence) only means something in the treatment field")
    sides_out = []
    for side in _split_list(field, v):
        stages_out = []
        for pool in side:
            codes = []
            for tok in pool:
                key = tok.lower().replace(" ", "")
                if key in reg["banned"]:
                    raise NameError_(f"{field}: {tok!r} is banned — name what it stands for")
                if key not in alias:
                    raise NameError_(f"{field}: {tok!r} is not a registered code "
                                     f"(known: {', '.join(order)})")
                codes.append(alias[key])
            if len(set(codes)) != len(codes):
                raise NameError_(f"{field}: {'+'.join(codes)} names a code twice")
            stages_out.append("+".join(sorted(codes, key=order.index)))   # within a pool: canonical
        sides_out.append("-then-".join(stages_out))                       # stages: as applied
    if len(set(sides_out)) != len(sides_out):
        raise NameError_(f"{field}: the same thing appears twice side by side")
    # side by side: canonical order, by each side's first code
    first = lambda s: order.index(re.split(r"[+]|-then-", s)[0])
    return "-".join(sorted(sides_out, key=first))


# ----------------------------------------------------------------------------- build / parse

def _topic(val):
    words = val.split("-")
    if not CODE_RE.match(val) or len(words) > TOPIC_WORDS:
        raise NameError_(f"topic {val!r} must be 1-{TOPIC_WORDS} lowercase words joined by '-'")
    return val


def _single(reg, f, val, kind=None):
    """The registered code a producer's label names, for a field that holds one code."""
    kind = kind or SINGLE[f]
    w = reg[kind + "_alias"].get(val.lower().replace(" ", ""))
    if w is None:
        raise NameError_(f"{f} {val!r} is not registered (known: {', '.join(reg[kind])})")
    return w


def build(reg, *, type, ext=None, source=None, form=None, topic=None, signal=None, stream=None,
          treatment=None, groups=None, win=None, thr=None, moco=None, review=None,
          date=None, version=None):
    key = source.strip().lower() if source else None
    if key in reg["sources"] and reg["sources"][key].get("flexible"):
        return _build_flexible(reg, reg["sources"][key], type=type, ext=ext, date=date,
                               version=version, form=form, topic=topic, signal=signal,
                               stream=stream, treatment=treatment, groups=groups, win=win,
                               thr=thr, moco=moco, review=review)
    if form:
        raise NameError_("only a synthetic name has a form field (plot or dataset)")
    parts = []
    spec_fields = reg["default_fields"]
    optional = reg["default_optional"]
    if source:
        source = canonical_source(source)
        spec = source_spec(reg, source)
        if spec is None:
            raise NameError_(f"source {source!r} is not registered (and is not pilot-YYYYMMDD)")
        spec_fields = spec["fields"]
        optional = spec["optional"]
        parts.append(source)
    t = reg["types_alias"].get(type.lower())
    if t is None:
        raise NameError_(f"type {type!r} is not registered (known: {', '.join(reg['types'])})")
    _several_studies(reg, source, t)
    parts.append(t)
    if t in reg["type_fields"]:
        spec_fields = reg["type_fields"][t]
        optional = reg["type_optional"].get(t, set())
    given = {"form": form, "topic": topic, "signal": signal, "stream": stream, "treatment": treatment,
             "groups": groups, "win": win, "thr": thr, "moco": moco, "review": review}
    for f in FIELD_ORDER:
        if f not in spec_fields:
            if given[f]:
                raise NameError_(f"a {t} name has no {f} field, but one was given")
            continue
        if not given[f]:
            if f in optional:
                continue
            raise NameError_(f"{f} is required for a {t} name")
        if f == "topic":
            parts.append(_topic(re.sub(r"[\s_]+", "-", given[f].strip().lower())))
        elif f in SINGLE:
            parts.append(_single(reg, f, given[f]))
        else:
            parts.append(canonical_list(reg, f, given[f]))
    parts.append(_date(date or dt.date.today().strftime("%Y%m%d")))
    if version not in (None, 1, "1"):
        v = f"v{int(version)}"
        if not VERSION_RE.match(v):
            raise NameError_(f"version {version!r}: versions start at 2 (the first file has none)")
        parts.append(v)
    name = "_".join(parts)
    if t == "export":
        if ext:
            raise NameError_("an export is a folder: its name has no extension")
    else:
        if not ext:
            raise NameError_(f"a {t} name needs an extension")
        e = ext.lower().lstrip(".")
        if not EXT_RE.match(e):
            raise NameError_(f"extension {ext!r} is not plain lowercase letters/digits")
        name += "." + e
    check(reg, name)            # never hand back a name the checker would refuse
    return name


def _flex_type(reg, spec, t):
    if t in reg["type_fields"]:
        raise NameError_(f"a {spec['code']} name cannot have type {t}, which has its own layout")


def _build_flexible(reg, spec, *, type, ext, date, version, **given):
    """A synthetic name (README "Synthetic"). Every dataset field is optional and written only
    when the simulation mimics it. The parser finds each one by its registered codes, so the
    builder refuses a topic that would read back as a code."""
    t = reg["types_alias"].get(type.lower())
    if t is None:
        raise NameError_(f"type {type!r} is not registered (known: {', '.join(reg['types'])})")
    _flex_type(reg, spec, t)
    for f, val in given.items():
        if val and f not in spec["fields"]:
            raise NameError_(f"a {spec['code']} name has no {f} field, but one was given")
    parts = [spec["code"], t]
    for f in spec["fields"]:
        val = given.get(f)
        if not val:
            if f in spec.get("required", []):
                raise NameError_(f"{f} is required for a {spec['code']} name"
                                 + (f" (one of {', '.join(reg['forms'])})" if f == "form" else ""))
            continue
        if f == "topic":
            parts.append(_topic(re.sub(r"[\s_]+", "-", val.strip().lower())))
        elif f in SINGLE:
            parts.append(_single(reg, f, val))
        else:
            parts.append(canonical_list(reg, f, val))
    if len(parts) == 3:
        raise NameError_(f"a {spec['code']} name needs at least one of "
                         f"{', '.join(f for f in spec['fields'] if f != 'form')}: "
                         "say what was simulated")
    parts.append(_date(date or dt.date.today().strftime("%Y%m%d")))
    if version not in (None, 1, "1"):
        v = f"v{int(version)}"
        if not VERSION_RE.match(v):
            raise NameError_(f"version {version!r}: versions start at 2 (the first file has none)")
        parts.append(v)
    name = "_".join(parts)
    if ext:
        e = ext.lower().lstrip(".")
        if not EXT_RE.match(e):
            raise NameError_(f"extension {ext!r} is not plain lowercase letters/digits")
        name += "." + e
    got = parse(reg, name)      # never hand back a name the checker would refuse, or misread
    for f in spec["fields"]:
        if given.get(f) and f not in got:
            raise NameError_(f"{f} {given[f]!r} would read back as another field; "
                             "reword the topic so no word of it stands alone as a registered code")
    return name


def _parse_flexible(reg, spec, fields, out, ext):
    """Fields of a synthetic name, after its source. Each optional field is found by its
    codes, in order; whatever is left before the date is the topic."""
    t = fields.pop(0) if fields else None
    if t not in reg["types"]:
        raise NameError_(f"type {t!r} is not registered")
    _flex_type(reg, spec, t)
    out["type"] = t
    if fields and VERSION_RE.match(fields[-1]):
        out["version"] = fields.pop()
    elif fields and re.fullmatch(r"v\d+", fields[-1]):
        raise NameError_(f"version {fields[-1]!r}: versions start at v2")
    if not fields:
        raise NameError_("a name ends with its date")
    out["date"] = _date(fields.pop())
    rest = list(fields)
    found = 0
    for f in spec["fields"]:
        if f == "topic" or not rest:
            continue
        tok = rest[0]
        if f in SINGLE:
            ok = tok in reg[SINGLE[f]]
            canon = reg[SINGLE[f] + "_alias"].get(tok)
            if not ok and canon is not None:
                raise NameError_(f"{f} {tok!r} should be written {canon!r}")
        else:
            try:
                ok = canonical_list(reg, f, tok) == tok
            except NameError_:
                ok = False
        if ok:
            out[f] = rest.pop(0)
            found += f != "form"
    for f in spec.get("required", []):
        if f not in out:
            raise NameError_(f"a {spec['code']} name needs its {f} right after the type"
                             + (f" ({', '.join(reg['forms'])})" if f == "form" else ""))
    if len(rest) > 1:
        raise NameError_(f"{'_'.join(rest)!r}: after its codes a {spec['code']} name holds one "
                         "topic; something here is out of order or not registered")
    if rest:
        for f in spec["fields"]:          # an alias left over is a code misspelt, not a topic
            if f in ("topic", "form") or f in out:
                continue
            try:
                canon = (_single(reg, f, rest[0]) if f in SINGLE
                         else canonical_list(reg, f, rest[0]))
            except NameError_:
                continue
            raise NameError_(f"{rest[0]!r} reads as the {f} {canon!r}: write it {canon!r}, "
                             "or reword the topic")
        out["topic"] = _topic(rest[0])
        found += 1
    if not found:
        raise NameError_(f"a {spec['code']} name needs at least one dataset field or a topic: "
                         "say what was simulated")
    if out.get("form") == "plot" and not ext:
        raise NameError_("a plot is a file: it needs an extension")
    return out


def _several_studies(reg, source, t):
    """A deliverable that sets studies side by side has the dataset fields of a figure. A type
    with its own layout -- an export (one cohort's data) or an explainer (no data) -- does not
    span studies, so the combination is refused rather than given that type's fields."""
    if source and source.startswith("pilots-") and t in reg["type_fields"]:
        raise NameError_(f"a {t} covers one study; several pilots can share a figure, not a {t}")


def _basic(name):
    """The rules every name obeys, whatever it names."""
    if len(name) > MAX_LEN:
        raise NameError_(f"{len(name)} characters; the cap is {MAX_LEN}")
    if name != name.lower():
        raise NameError_("contains capitals")
    if not re.fullmatch(r"[a-z0-9_+.\-]+", name):
        raise NameError_("contains characters other than a-z 0-9 _ - + .")


def _banned(reg, stem):
    for tok in re.split(r"[_+\-]", stem):
        if tok in reg["banned"]:
            raise NameError_(f"{tok!r} is banned — name what it stands for")


def parse(reg, name):
    """Split a name into its fields, checking every one. Raises NameError_ with every problem found."""
    _basic(name)
    stem, dot, ext = name.rpartition(".")
    if not dot:
        stem, ext = name, None          # only an export (a folder) has no extension
    elif not EXT_RE.match(ext) or "." in stem:
        raise NameError_("needs exactly one '.', before a plain extension")
    fields = stem.split("_")
    _banned(reg, stem)
    out = {"ext": ext} if ext else {}
    spec = source_spec(reg, fields[0])
    if spec is not None and spec.get("flexible"):
        out["source"] = fields.pop(0)
        return _parse_flexible(reg, spec, fields, out, ext)
    if spec is not None:
        out["source"] = fields.pop(0)
        want, optional = spec["fields"], spec["optional"]
    else:
        want, optional = reg["default_fields"], reg["default_optional"]
    t = fields[0] if fields else None
    _several_studies(reg, out.get("source"), t)
    if t in reg["type_fields"]:
        want = reg["type_fields"][t]
        optional = reg["type_optional"].get(t, set())
    if t == "export" and ext:
        raise NameError_("an export is a folder: its name has no extension")
    if t != "export" and not ext:
        raise NameError_("needs exactly one '.', before a plain extension")
    if fields and VERSION_RE.match(fields[-1]):
        out["version"] = fields.pop()
    elif fields and re.fullmatch(r"v\d+", fields[-1]):
        raise NameError_(f"version {fields[-1]!r}: versions start at v2")
    order = ["type"] + [f for f in FIELD_ORDER if f in want] + ["date"]
    if optional and len(fields) == len(order) - 1:
        order = [f for f in order if f not in optional]
    if len(fields) != len(order):
        raise NameError_(f"expected {len(order)} fields ({'_'.join(order)}), found {len(fields)}")
    for f, val in zip(order, fields):
        if f == "type":
            if val not in reg["types"]:
                raise NameError_(f"type {val!r} is not registered")
        elif f in SINGLE:
            if val not in reg[SINGLE[f]]:
                canon = reg[SINGLE[f] + "_alias"].get(val)
                raise NameError_(f"{f} {val!r} should be written {canon!r}" if canon
                                 else f"{f} {val!r} is not registered")
        elif f == "date":
            _date(val)
        elif f == "topic":
            _topic(val)
        else:
            canon = canonical_list(reg, f, val)
            if canon != val:
                raise NameError_(f"{f} {val!r} should be written {canon!r}")
        out[f] = val
    return out


def check(reg, name):
    parse(reg, name)
    return True


# ----------------------------------------------------------------------------- exports
#
# An export is a folder; its data files name only what tells them apart. Every field is
# written once on the path: in the folder when every file shares it, in the file when files
# differ on it, in manifest.json when no name needs it (README "Exports").

def parse_export_file(reg, name, folder=None):
    """Fields of a data file inside an export. `folder` is the folder's parsed fields, when
    known; without it, a field the folder could carry is not demanded of the file."""
    ef = reg["export_files"]
    _basic(name)
    stem, dot, ext = name.rpartition(".")
    if not dot or "." in stem or not EXT_RE.match(ext):
        raise NameError_("needs exactly one '.', before a plain extension")
    if name in ef["fixed"]:
        return {"fixed": name, "ext": ext}
    if re.match(ef["recording"], name):
        return {"recording": stem, "ext": ext}
    _banned(reg, stem)
    tokens = stem.split("_")
    table = tokens.pop(0)
    if table not in reg["tables"]:
        raise NameError_(f"{table!r} is not a registered table (known: {', '.join(reg['tables'])}),"
                         f" nor a fixed name ({', '.join(ef['fixed'])}), nor a recording "
                         f"(<slice_id>.csv)")
    out = {"table": table, "ext": ext}
    for f, kind in FILE_FIELDS:
        if tokens and tokens[0] in reg[kind]:
            out[f] = tokens.pop(0)
    for f, kind in FILE_FIELDS:
        canon = reg[kind + "_alias"].get(tokens[0]) if tokens else None
        if canon and canon != tokens[0]:
            raise NameError_(f"{f} {tokens[0]!r} should be written {canon!r}")
    if tokens:
        raise NameError_(f"{'_'.join(tokens)!r}: after the table a file carries only "
                         f"<stream>, <win> and <keep>, in that order, one code each")
    need = reg["table_fields"][table]
    for f, _ in FILE_FIELDS:
        in_folder = bool(folder and folder.get(f))
        if f in out and in_folder:
            raise NameError_(f"{f} {out[f]!r} is already in the folder name; write it once")
        if f in need and f not in out:
            if in_folder or (folder is None and f == "win"):
                continue
            raise NameError_(f"a {table} table needs its {f} in the file name")
        if f in out and f not in need and f != "keep":
            raise NameError_(f"a {table} table has no {f}")
    return out


def build_file(reg, *, table, ext, stream=None, win=None, keep=None, folder=None):
    """The name of a data file inside an export folder. Pass `folder` (its name) so a field the
    folder already carries is refused rather than written twice."""
    t = reg["tables_alias"].get(table.lower())
    if t is None:
        raise NameError_(f"table {table!r} is not registered (known: {', '.join(reg['tables'])})")
    parts = [t]
    for f, kind, val in (("stream", "streams", stream), ("win", "windows", win),
                         ("keep", "keeps", keep)):
        if val:
            parts.append(_single(reg, f, val, kind))
    name = "_".join(parts) + "." + ext.lower().lstrip(".")
    parse_export_file(reg, name, parse(reg, folder) if folder else None)
    return name


def parse_path(reg, path):
    """Every field a path states: an export folder's and its file's merged, or one name's."""
    p = pathlib.PurePath(path)
    try:
        folder = parse(reg, p.parent.name) if p.parent.name else None
    except NameError_ as e:
        if "_export_" in f"_{p.parent.name}_":     # it means to be an export: say what is wrong
            raise NameError_(f"folder {p.parent.name!r}: {e}") from None
        folder = None
    if folder and folder.get("type") == "export":
        f = parse_export_file(reg, p.name, folder)
        return {**folder, **f, "folder": p.parent.name, "file": p.name}
    return parse(reg, p.name)


def check_manifest(reg, folder):
    """Problems with an export's manifest.json: the screens and provenance a name leaves out."""
    ef = reg["export_files"]
    path = pathlib.Path(folder) / "manifest.json"
    try:
        m = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ["manifest.json is missing: it records the screens and the archive the name "
                "leaves out"]
    except (OSError, ValueError) as e:
        return [f"manifest.json is unreadable: {e}"]
    probs = [f"manifest.json has no {k!r}" for k in ef["manifest_required"] if k not in m]
    if m.get("name") not in (None, path.parent.name):
        probs.append(f"manifest.json names {m['name']!r}, not its folder")
    screens = m.get("screens") if isinstance(m.get("screens"), dict) else {}
    for s, allowed in ef["screens_required"].items():
        if "screens" in m and s not in screens:
            probs.append(f"manifest.json screens has no {s!r}")
        elif allowed and s in screens:
            state = screens[s].get("state") if isinstance(screens[s], dict) else screens[s]
            if state not in allowed:
                probs.append(f"manifest.json screens.{s} is {state!r}, not one of {allowed}")
    return probs


def check_export(reg, folder, entries=None):
    """(name, why) for everything wrong with one export folder: its name, its data files, its
    manifest. `entries` limits the file checks to those names (the hook passes what changed)."""
    folder = pathlib.Path(folder)
    bad = []
    try:
        fields = parse(reg, folder.name)
        if fields.get("type") != "export":
            raise NameError_(f"a folder in an export inbox is an export; type is {fields['type']!r}")
    except NameError_ as e:
        return [(folder.name + "/", str(e))]       # its files cannot be judged against it
    ef = reg["export_files"]
    names = sorted(os.listdir(folder)) if entries is None else sorted(entries)
    for n in names:
        if n.startswith("."):
            continue
        if (folder / n).is_dir():
            bad.append((f"{folder.name}/{n}/", "an export holds its files directly: one folder "
                        "per export, so a variant (3x, a window) is a sibling folder"))
            continue
        if n.rsplit(".", 1)[-1].lower() not in ef["checked_exts"]:
            continue                                # prose (README.md) is not checked
        try:
            parse_export_file(reg, n, fields)
        except NameError_ as e:
            bad.append((f"{folder.name}/{n}", str(e)))
    bad += [(f"{folder.name}/manifest.json", p) for p in check_manifest(reg, folder)]
    return bad


# ----------------------------------------------------------------------------- audit

def audit(reg, root, days=None, exts=DELIVERABLES, skip=SKIP_DIRS):
    """Every deliverable under root that fails, with why. Hidden paths and SKIP_DIRS are skipped."""
    cutoff = None if days is None else dt.datetime.now().timestamp() - days * 86400
    bad, good = [], 0
    for p in sorted(pathlib.Path(root).rglob("*")):
        parts = p.relative_to(root).parts
        if not p.is_file() or any(q.startswith(".") or q in skip for q in parts[:-1]) \
                or parts[-1].startswith("."):
            continue
        if p.suffix.lower().lstrip(".") not in exts:
            continue
        if cutoff is not None and p.stat().st_mtime < cutoff:
            continue
        try:
            check(reg, p.name)
            good += 1
        except NameError_ as e:
            bad.append((p, str(e)))
    return good, bad


# ----------------------------------------------------------------------------- selftest

def selftest():
    reg = load_codes()
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    fails = []
    for name in cases["valid"]:
        try:
            check(reg, name)
        except NameError_ as e:
            fails.append(f"valid name refused: {name} — {e}")
    for c in cases["invalid"]:
        try:
            check(reg, c["name"])
            fails.append(f"invalid name accepted: {c['name']} ({c['why']})")
        except NameError_:
            pass
    for c in cases["build"]:
        try:
            got = build(reg, **c["args"])
            if got != c["expect"]:
                fails.append(f"build {c['args']} gave {got}, expected {c['expect']}")
        except NameError_ as e:
            fails.append(f"build {c['args']} refused: {e}")
    for c in cases["build_refused"]:
        try:
            got = build(reg, **c["args"])
            fails.append(f"build {c['args']} should be refused ({c['why']}) but gave {got}")
        except NameError_:
            pass
    for folder, f in cases["export_files"]["valid"]:
        try:
            parse_export_file(reg, f, parse(reg, folder))
        except NameError_ as e:
            fails.append(f"export file refused: {folder}/{f} — {e}")
    for c in cases["export_files"]["invalid"]:
        try:
            parse_export_file(reg, c["file"], parse(reg, c["folder"]))
            fails.append(f"export file accepted: {c['folder']}/{c['file']} ({c['why']})")
        except NameError_:
            pass
    # a path's fields are the folder's and the file's together
    ex = cases["export_files"]["valid"][0]
    got = parse_path(reg, f"{ex[0]}/{ex[1]}")
    if (got.get("stream"), got.get("win"), got.get("thr")) != ("fast", "win20min", "thr4x"):
        fails.append(f"parse_path did not merge folder and file: {got}")
    # check_export on a real folder: a clean one passes; each defect is reported
    import tempfile as _tf
    with _tf.TemporaryDirectory() as d:
        good = pathlib.Path(d, ex[0])
        good.mkdir()
        for n in ("metrics_fast_win20min.csv", "fsw_win5min.csv", "dead_roi_verdict.csv",
                  "README_win20min.md"):
            (good / n).write_text("x")
        manifest = {"name": ex[0], "consumer": "fireflies", "archive": "event_store_onset_x",
                    "producer": "selftest", "screens": {
                        "dead_roi": {"state": "excluded", "rule": "full-trace"},
                        "field_steps": {"state": "unscanned"}, "moco_pin": "excluded",
                        "f0_displaced": "excluded"}}
        (good / "manifest.json").write_text(json.dumps(manifest))
        if check_export(reg, good):
            fails.append(f"a clean export folder was refused: {check_export(reg, good)}")
        (good / "pilot_fsw_factor4_20min.csv").write_text("x")
        (good / "4x_sigma_est").mkdir()
        manifest["screens"]["field_steps"] = {"state": "maybe"}
        del manifest["archive"]
        (good / "manifest.json").write_text(json.dumps(manifest))
        got = {n.split("/")[-1] for n, _ in check_export(reg, good)}
        want = {"pilot_fsw_factor4_20min.csv", "", "manifest.json"}   # "" = the subfolder
        if got != want or len(check_export(reg, good)) != 4:
            fails.append(f"check_export found {sorted(check_export(reg, good))}")
        bad = pathlib.Path(d, "pilot_apv_cnqx_gz_20261012_BLANKED_DEADROI")
        bad.mkdir()
        if len(check_export(reg, bad)) != 1:
            fails.append("a badly named export folder was not reported once, by its name")
    # a name the builder makes must parse back to the fields it was built from
    n = build(reg, type="raster", signal="roi", stream="combined", treatment="gz+apv+cnqx", groups="orx-di",
              win="win20min", date="20261007", ext="html")
    p = parse(reg, n)
    if (p["treatment"], p["groups"]) != ("apv+cnqx+gz", "di-orx"):
        fails.append(f"round trip lost canonical order: {p}")
    # the codes file must refuse an inconsistent edit, not load it
    import tempfile
    raw = json.loads(CODES.read_text(encoding="utf-8"))
    raw["groups"].append({"code": "all"})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(raw, fh)
    try:
        load_codes(fh.name)
        fails.append("codes.json with a banned word as a code was loaded")
    except NameError_:
        pass
    finally:
        os.unlink(fh.name)
    # audit must find a bad file and pass a good one
    with tempfile.TemporaryDirectory() as d:
        pathlib.Path(d, "ALL_APV+CNQX+GZ_combined.html").write_text("x")
        pathlib.Path(d, cases["valid"][0]).write_text("x")
        pathlib.Path(d, "notes.txt").write_text("x")
        pathlib.Path(d, "table.csv").write_text("x")           # data, not a deliverable
        pathlib.Path(d, "lit").mkdir()
        pathlib.Path(d, "lit", "Abney_2015.pdf").write_text("x")  # someone else's paper
        good, bad = audit(reg, d)
        if (good, len(bad)) != (1, 1):
            fails.append(f"audit counted good={good} bad={len(bad)}, expected 1 and 1")
    for f in fails:
        print("  " + f)
    print("selftest: " + ("RED" if fails else "PASS"))
    return 1 if fails else 0


# ----------------------------------------------------------------------------- CLI

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if "--selftest" in argv[:1]:
        try:
            return selftest()
        except Exception as e:      # a crash is a failure, never a silent non-answer
            print(f"  selftest crashed: {type(e).__name__}: {e}\nselftest: RED")
            return 1
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="print the name for these fields, or refuse with why")
    b.add_argument("--type", required=True)
    b.add_argument("--ext", help="required, except for an export (a folder)")
    for f in ("source", "form", "topic", "signal", "stream", "treatment", "groups", "win", "thr",
              "moco", "review", "date", "version"):
        b.add_argument("--" + f)
    bf = sub.add_parser("build-file", help="name a data file inside an export folder")
    bf.add_argument("--table", required=True)
    bf.add_argument("--ext", required=True)
    for f in ("stream", "win", "keep"):
        bf.add_argument("--" + f)
    bf.add_argument("--folder", help="the export folder's name, so nothing is written twice")
    c = sub.add_parser("check", help="exit 1 if any name breaks the scheme")
    c.add_argument("names", nargs="+")
    pa = sub.add_parser("parse", help="print a name's or a path's fields as JSON (exit 1 if bad)")
    pa.add_argument("path")
    ce = sub.add_parser("check-export", help="check export folders: name, files, manifest.json")
    ce.add_argument("folders", nargs="+")
    a = sub.add_parser("audit", help="list non-conforming deliverables under a directory")
    a.add_argument("root")
    a.add_argument("--days", type=float, help="only files modified in the last N days")
    a.add_argument("--strict", action="store_true", help="exit 1 if anything fails")
    args = ap.parse_args(argv)
    try:
        reg = load_codes()
    except NameError_ as e:
        print(e, file=sys.stderr)
        return 2
    if args.cmd in ("build", "build-file"):
        kw = {k.replace("-", "_"): v for k, v in vars(args).items()
              if k != "cmd" and v is not None}
        try:
            print((build if args.cmd == "build" else build_file)(reg, **kw))
            return 0
        except NameError_ as e:
            print(f"refused: {e}", file=sys.stderr)
            return 2
    if args.cmd == "check":
        rc = 0
        for n in args.names:
            try:
                check(reg, pathlib.Path(n).name)
                print(f"ok    {n}")
            except NameError_ as e:
                print(f"FAIL  {n}  — {e}")
                rc = 1
        return rc
    if args.cmd == "parse":
        try:
            print(json.dumps(parse_path(reg, args.path), sort_keys=True))
            return 0
        except NameError_ as e:
            print(json.dumps({"error": str(e)}))
            return 1
    if args.cmd == "check-export":
        rc = 0
        for d in args.folders:
            bad = check_export(reg, d)
            for n, why in bad:
                print(f"FAIL  {n}  — {why}")
            if not bad:
                print(f"ok    {d}")
            rc |= bool(bad)
        return rc
    good, bad = audit(reg, args.root, args.days)
    for p, why in bad:
        print(f"FAIL  {p}  — {why}")
    print(f"{good} conforming, {len(bad)} not")
    return 1 if (bad and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
