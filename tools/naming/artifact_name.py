#!/usr/bin/env python3
# vendored from syncytium2/armory @ d5d3efe (tools/naming/). This file is a COPY, and so are
# codes.json and cases.json beside it: edits here are overwritten whenever they are
# re-vendored. Change a code in armory's codes.json and re-vendor all three together.
# instrument: naming
"""artifact_name — build, check and audit output filenames against the estate scheme.

    [<source>_]<type>_<signal>_<stream>_<treatment>_<groups>_<win>_<date>[_v<N>].<ext>

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
LIST_FIELDS = ("stream", "treatment", "groups")
# every field between type and date, in the order a name writes them
FIELD_ORDER = ("signal", "stream", "treatment", "groups", "win")
SINGLE = {"signal": "signals", "win": "windows"}     # one registered code, no operators
# which separators each list field may use. `-` keeps things separate (side by side), `+`
# pools them into one, `-then-` is a sequence of treatment stages and means nothing elsewhere.
OPERATORS = {"stream": {"-"}, "groups": {"-", "+"}, "treatment": {"-", "+", "-then-"}}
CODE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LIST_CODE_RE = re.compile(r"^[a-z0-9]+$")   # no hyphen: in a list field every `-` separates
DATE_RE = re.compile(r"^\d{8}$")
VERSION_RE = re.compile(r"^v([2-9]|[1-9]\d+)$")
EXT_RE = re.compile(r"^[a-z0-9]+$")


class NameError_(ValueError):
    """A name, or a request to build one, that breaks the scheme. The message says how."""


# ----------------------------------------------------------------------------- the code list

def load_codes(path=CODES):
    raw = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    reg = {"banned": set(raw["banned"]), "reserved": set(raw["reserved"]),
           "sources": {}, "default_fields": raw["default_fields"]}
    problems = []
    for kind in ("types", "signals", "streams", "treatments", "groups", "windows"):
        entries, alias, compound = [], {}, {}
        for e in raw[kind]:
            code = e["code"]
            pattern = LIST_CODE_RE if kind in ("streams", "treatments", "groups") else CODE_RE
            if not pattern.match(code):
                problems.append(f"{kind}: {code!r} is not a valid code here")
            if code in reg["banned"] or code in reg["reserved"]:
                problems.append(f"{kind}: {code!r} is a banned or reserved word")
            entries.append(code)
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
        reg["sources"][s["code"]] = s
        if s["code"] in reg["types"]:
            problems.append(f"source {s['code']!r} is also a type: the first field would be ambiguous")
    for t in reg["types"]:
        if t.startswith("pilot-") or t == "pilot":
            problems.append(f"type {t!r} collides with the pilot source pattern")
    if problems:
        raise NameError_("codes.json is inconsistent:\n  " + "\n  ".join(problems))
    return reg


def source_spec(reg, token):
    """The source a first field names, or None if it is not a source (so it is the type)."""
    if token in reg["sources"]:
        return reg["sources"][token]
    m = re.fullmatch(r"pilot-(\d{8})(b|c|d)?", token)
    if m:
        _date(m.group(1), "pilot start date")
        return reg["sources"]["pilot"]
    return None


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
    kind = {"stream": "streams", "treatment": "treatments", "groups": "groups"}[field]
    alias, order = reg[kind + "_alias"], reg[kind]
    v = value.strip()
    v = v.lower()
    for a in sorted(reg[kind + "_compound"], key=len, reverse=True):
        v = v.replace(a, reg[kind + "_compound"][a])
    if not v:
        raise NameError_(f"{field} is empty")
    if "+" in v and "+" not in OPERATORS[field]:
        raise NameError_(f"{field} cannot pool with '+'")
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

def build(reg, *, type, ext, source=None, signal=None, stream=None, treatment=None,
          groups=None, win=None, date=None, version=None):
    parts = []
    spec_fields = reg["default_fields"]
    if source:
        spec = source_spec(reg, source)
        if spec is None:
            raise NameError_(f"source {source!r} is not registered (and is not pilot-YYYYMMDD)")
        spec_fields = spec["fields"]
        parts.append(source)
    t = reg["types_alias"].get(type.lower())
    if t is None:
        raise NameError_(f"type {type!r} is not registered (known: {', '.join(reg['types'])})")
    parts.append(t)
    given = {"signal": signal, "stream": stream, "treatment": treatment, "groups": groups,
             "win": win}
    for f in FIELD_ORDER:
        if f not in spec_fields:
            if given[f]:
                raise NameError_(f"this source has no {f} field, but one was given")
            continue
        if not given[f]:
            raise NameError_(f"{f} is required for this source")
        if f in SINGLE:
            kind = SINGLE[f]
            w = reg[kind + "_alias"].get(given[f].lower().replace(" ", ""))
            if w is None:
                raise NameError_(f"{f} {given[f]!r} is not registered "
                                 f"(known: {', '.join(reg[kind])})")
            parts.append(w)
        else:
            parts.append(canonical_list(reg, f, given[f]))
    parts.append(_date(date or dt.date.today().strftime("%Y%m%d")))
    if version not in (None, 1, "1"):
        v = f"v{int(version)}"
        if not VERSION_RE.match(v):
            raise NameError_(f"version {version!r}: versions start at 2 (the first file has none)")
        parts.append(v)
    e = ext.lower().lstrip(".")
    if not EXT_RE.match(e):
        raise NameError_(f"extension {ext!r} is not plain lowercase letters/digits")
    name = "_".join(parts) + "." + e
    check(reg, name)            # never hand back a name the checker would refuse
    return name


def parse(reg, name):
    """Split a name into its fields, checking every one. Raises NameError_ with every problem found."""
    if len(name) > MAX_LEN:
        raise NameError_(f"{len(name)} characters; the cap is {MAX_LEN}")
    if name != name.lower():
        raise NameError_("contains capitals")
    if not re.fullmatch(r"[a-z0-9_+.\-]+", name):
        raise NameError_("contains characters other than a-z 0-9 _ - + .")
    stem, dot, ext = name.rpartition(".")
    if not dot or not EXT_RE.match(ext) or "." in stem:
        raise NameError_("needs exactly one '.', before a plain extension")
    fields = stem.split("_")
    for tok in re.split(r"[_+\-]", stem):
        if tok in reg["banned"]:
            raise NameError_(f"{tok!r} is banned — name what it stands for")
    out = {"ext": ext}
    spec = source_spec(reg, fields[0])
    if spec is not None:
        out["source"] = fields.pop(0)
        want = spec["fields"]
    else:
        want = reg["default_fields"]
    if fields and VERSION_RE.match(fields[-1]):
        out["version"] = fields.pop()
    elif fields and re.fullmatch(r"v\d+", fields[-1]):
        raise NameError_(f"version {fields[-1]!r}: versions start at v2")
    order = ["type"] + [f for f in FIELD_ORDER if f in want] + ["date"]
    if len(fields) != len(order):
        raise NameError_(f"expected {len(order)} fields ({'_'.join(order)}), found {len(fields)}")
    for f, val in zip(order, fields):
        if f == "type":
            if val not in reg["types"]:
                raise NameError_(f"type {val!r} is not registered")
        elif f in SINGLE:
            if val not in reg[SINGLE[f]]:
                raise NameError_(f"{f} {val!r} is not registered")
        elif f == "date":
            _date(val)
        else:
            canon = canonical_list(reg, f, val)
            if canon != val:
                raise NameError_(f"{f} {val!r} should be written {canon!r}")
        out[f] = val
    return out


def check(reg, name):
    parse(reg, name)
    return True


# ----------------------------------------------------------------------------- audit

def audit(reg, root, days=None, exts=("html", "png", "pdf", "svg", "csv", "xlsx", "docx", "pptx", "tif", "tiff", "eps")):
    """Every deliverable-looking file under root that fails, with why. Hidden paths are skipped."""
    cutoff = None if days is None else dt.datetime.now().timestamp() - days * 86400
    bad, good = [], 0
    for p in sorted(pathlib.Path(root).rglob("*")):
        if not p.is_file() or any(part.startswith(".") for part in p.relative_to(root).parts):
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
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="print the name for these fields, or refuse with why")
    for f in ("type", "ext"):
        b.add_argument("--" + f, required=True)
    for f in ("source", "signal", "stream", "treatment", "groups", "win", "date", "version"):
        b.add_argument("--" + f)
    c = sub.add_parser("check", help="exit 1 if any name breaks the scheme")
    c.add_argument("names", nargs="+")
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
    if args.cmd == "build":
        kw = {k: v for k, v in vars(args).items() if k != "cmd" and v is not None}
        try:
            print(build(reg, **kw))
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
    good, bad = audit(reg, args.root, args.days)
    for p, why in bad:
        print(f"FAIL  {p}  — {why}")
    print(f"{good} conforming, {len(bad)} not")
    return 1 if (bad and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
