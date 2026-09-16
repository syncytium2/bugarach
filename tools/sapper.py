#!/usr/bin/env python3
# instrument: retrieval
"""sapper — bugarach's mechanized rule gate (ported pattern from interface2).

A sapper clears mines from ground others are about to cross: each rule is a
hard-won lesson converted into a check that fires by itself. Every rule MUST
prove it can fire — `--selftest` runs each rule against embedded bad/good
fixtures; a check that cannot fire is worse than no check.

Usage:
  tools/sapper.py --selftest   prove every rule can fire (and stay silent)
  tools/sapper.py --all        scan all tracked files; exit 1 on BLOCK
  tools/sapper.py --staged     scan ADDED lines of the staged diff (pre-commit)
  tools/sapper.py --list       print the rule table

Wiring: tests/test_sapper.py runs --selftest and --all under pytest, so CI
enforces the rules; the optional pre-commit hook (.githooks/pre-commit,
enable with `git config core.hooksPath .githooks`) catches them earlier.
New-rule requests / disputes: file under docs/sapper_feedback/.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class Rule:
    id: str
    level: str            # "BLOCK" | "WARN"
    pattern: str          # regex, matched per line
    include: list[str]    # fnmatch globs of paths the rule applies to
    exclude: list[str]    # fnmatch globs exempt from the rule
    message: str
    fixture_bad: str      # one line the rule MUST fire on
    fixture_good: str     # one line the rule must NOT fire on


# Patterns for self-referential strings are assembled by concatenation so this
# file never trips its own rules when scanned.
_UM = "University of " + "Michigan"
#: The retired spelling of the instrument (SAP014), assembled so this file does
#: not trip its own rule even if the exclude were ever dropped.
_OLD_INSTRUMENT = "MAH" + "DCE"

RULES = [
    Rule(
        id="SAP001", level="BLOCK",
        pattern=r"np\.percentile\s*\(",
        include=["src/bugarach/**"], exclude=["src/bugarach/detectors/_shared.py"],
        message="MATLAB prctile matches NO numpy.percentile mode — use "
                "matlab_prctile from detectors/_shared (incident: LoCo port).",
        fixture_bad="thr = np.percentile(pool, 99.9)",
        fixture_good="thr = matlab_prctile(pool, 99.9)",
    ),
    Rule(
        id="SAP002", level="BLOCK",
        pattern=r"default_rng\s*\(",
        include=["src/bugarach/**"], exclude=[],
        message="Parity requires MATLAB's twister stream: rng(seed) == "
                "np.random.RandomState(seed). default_rng breaks every "
                "surrogate-based parity fixture.",
        fixture_bad="rng = np.random.default_rng(7)",
        fixture_good="rng = np.random.RandomState(7)",
    ),
    Rule(
        id="SAP003", level="BLOCK",
        pattern=r"^\s*(import|from)\s+pyspike",
        include=["src/bugarach/**"], exclude=[],
        message="PySpike's max_tau cap has been broken since 0.8.0"
                " (see detectors/sync.py; fixed upstream in PySpike#89,"
                " unreleased as of 2026-09-01)"
                " — PySpike is a TEST-ONLY cross-check in the uncapped regime,"
                " never a runtime dependency.",
        fixture_bad="import pyspike",
        fixture_good="from bugarach.detectors.sync import adaptive_profile",
    ),
    Rule(
        id="SAP004", level="BLOCK",
        # The last alternative is the one that was missing. This rule matched
        # `DeFazio/` and `Dropbox/` and was believed to cover personal paths, but
        # a home directory spelled in lowercase — `/Users/tonydefazio/Developer/…`
        # — matched none of them, and `tools/matlab_ref/prep_ref_input.py` carried
        # two of those in a PUBLIC repo from the day it was written until
        # 2026-08-20. A rule that covers the shape you thought of is worth less
        # than it looks; this one now matches any absolute home-directory path.
        pattern=r"(" + _UM + r"|DeFazio/|Dropbox/|/(?:Users|home)/[A-Za-z0-9._-]+/)",
        include=["**"],
        # test_paths.py is the path-RESOLVER's own test: inventing
        # `/Users/rd/Dropbox-UM/Someone` is precisely its job, and the strings are
        # synthetic. Excluding the test that exercises a rule's subject matter is
        # not a backlog entry, it is the rule staying out of its own way.
        exclude=["tools/sapper.py", "tests/test_paths.py"],
        message="Machine-local personal path in a tracked file — real data "
                "stays behind BUGARACH_DATA_ROOT (FOUNDATIONS §5; public-repo "
                "scrub incident 2026-08-11).",
        fixture_bad='sys.path.insert(0, "/Users/somebody/Developer/bugarach/src")',
        fixture_good='sys.path.insert(0, str(Path(__file__).parents[2] / "src"))',
    ),
    Rule(
        id="SAP005", level="BLOCK",
        pattern=r"""["']{1,3}\s*<\s*(html\b|head\b|title\b)""",
        include=["**/*.py"], exclude=["tools/sapper.py"],
        message="An HTML document built here must open with "
                '<meta charset="utf-8">. Opened from disk (file://) a page '
                "with no declared charset is read as Latin-1, and every "
                "en-dash, ×, · and — in it renders as mojibake. Cost a review "
                "document 2026-08-13; the artifact pipeline hides this because "
                "it supplies its own head. (Known gap: sapper matches per line, "
                "so a literal opening '<!doctype html>' on its own line is not "
                "checked — see docs/sapper_feedback/.)",
        fixture_bad='page = f"""<title>Report</title><style>...',
        fixture_good='page = f"""<meta charset="utf-8">\\n<title>Report</title>',
    ),
    Rule(
        id="SAP006", level="BLOCK",
        pattern=r'add_argument\(\s*["\']--out["\'][^)]*required\s*=\s*True',
        # Deliberately NARROW: page and report builders only. Tools that write
        # data for a pipeline (derive_spec, assess_archive, fair_bakeoff) are
        # right to require an explicit --out, and a rule that fires on correct
        # code is a rule someone switches off. Figure tools that still require
        # --out are listed in docs/todo/2026-08-18-figure-tools-require-out.md.
        include=["tools/build_*.py", "tools/md_to_page.py"], exclude=[],
        message="A deliverable's destination must DEFAULT to the darkroom, never "
                "be required. Every figure tool here takes --out with "
                "`default=None` and falls back to bugarach.paths.darkroom(); a "
                "required --out means the output lands wherever the caller "
                "happened to point it. The report builder had this and the one "
                "deliverable meant for a person to read was the only one that "
                "never reached the darkroom — it sat in docs/learned until Tony "
                "asked where it was (2026-08-18). Use `default=None` plus "
                "`out = args.out or darkroom()`.",
        fixture_bad='p.add_argument("--out", type=Path, required=True)',
        fixture_good='p.add_argument("--out", type=Path, default=None)',
    ),
    Rule(
        id="SAP007", level="BLOCK",
        pattern=r"(load_slice\s*\(|load_store\s*\(|[\"'][^\"']*\.mat[\"']|\*\.mat)",
        # The store READER is allowed to read stores; that is what it is for, and
        # FOUNDATIONS §4 keeps the two input paths deliberately separate. So are
        # the tests that prove it works and the parity chain that regenerates
        # fixtures from MATLAB. Every ANALYSIS goes through the export folder.
        include=["src/bugarach/**", "tools/**"],
        # THE EXCLUSION LIST IS THE BACKLOG. store.py is the store reader and
        # stays; matlab_ref regenerates parity fixtures from MATLAB and stays;
        # lab_excluded.py reads the spreadsheet on purpose, to answer what the
        # lab withdrew. The six below are the tools that were reading stores
        # when this rule was written, and every one of them is a defect —
        # `make_assembly_closed_figure.py` and `modularity_null.py` are the two
        # that produced the numbers containing withdrawn recordings. They are
        # named rather than pattern-matched so that fixing one means DELETING A
        # LINE HERE, and the list shrinking is the progress.
        # docs/todo/2026-08-20-six-tools-still-read-stores.md
        # `cli.py` and `ui/app.py` are the STORE PATH'S OWN ENTRY POINTS — the
        # half of FOUNDATIONS §4 that exists to browse a store, as against the
        # webapp which reads folders. They are not analyses. Whether that path
        # should survive at all is a product question, not a gate's.
        exclude=["src/bugarach/store.py", "src/bugarach/cli.py",
                 "src/bugarach/ui/app.py", "tools/matlab_ref/**",
                 "tools/sapper.py", "tools/lab_excluded.py",
                 # different case: this one already PREFERS the folder and keeps
                 # the store as a documented fallback. Whether the fallback
                 # should exist at all is the open question in the todo.
                 "tools/assess_archive.py",
                 # A THIRD CATEGORY, and NOT backlog: an IMPORTER. It reads
                 # ANOTHER lab's published source data (DANDI:000219, CC-BY-4.0,
                 # extracted to .mat) in order to WRITE an export folder — the
                 # same role interface2's exporter plays for this lab, and its
                 # output is what analyses then read. It cannot go around this
                 # lab's exclusions because it never touches this lab's data.
                 # This makes "the list shrinking is the progress" above true of
                 # only half the list; see
                 # docs/sapper_feedback/2026-08-28-sap007-cannot-tell-an-importer-from-an-analysis.md
                 "tools/import_dandi.py"],
        message="Analysis must read the EXPORT FOLDER, never a .mat store. The "
                "folder is what the lab approved: the exporter honours "
                "db4's `exclude` flag, drops what was withdrawn, and records it "
                "in PROVENANCE.md. A store carries every recording ever "
                "processed and cannot say which are usable. On 2026-08-20 two "
                "withdrawn recordings were found inside every number this "
                "project had published about the assembly question — the export "
                "was correct and the analyses had gone around it. Read the "
                "folder (bugarach.io.load_folder); if you genuinely need the "
                "store reader, it is store.py and it is excluded here.",
        fixture_bad='s = load_slice(root / "recording.mat")',
        fixture_good='slices = load_folder(export_dir)',
    ),
    Rule(
        id="SAP008", level="BLOCK",
        pattern=r"CI does not (run|install)",
        # Narrow to tests/ on purpose. Prose elsewhere describing the history of
        # the runner is fine; what must not go stale is a TEST telling its reader
        # that the green tick does not cover it.
        include=["tests/**"], exclude=[],
        message="CI HAS A BROWSER since 2026-08-19 (04f667f): ci.yml runs "
                "`playwright install --with-deps chromium` and sets "
                "BUGARACH_REQUIRE_BROWSER=1, so a runner that loses it fails "
                "test_browser_available.py loudly instead of skipping the webapp "
                "suite quietly. Eight test docstrings went on saying the opposite "
                "for six days, and on 2026-08-25 one was read back to Tony as a "
                "live gap in the coverage while he was weighing a decision. Each "
                "was true when written, on 2026-08-18. A claim about what the "
                "green tick COVERS is the one thing a reader cannot check for "
                "themselves, so it does not get to go stale quietly. Say what CI "
                "does today, or say nothing.",
        fixture_bad="⚠ **CI does not run this** — it needs a chromium CI does not install.",
        fixture_good="**CI runs this** — the runner installs chromium and sets "
                     "BUGARACH_REQUIRE_BROWSER=1.",
    ),
    Rule(
        id="SAP009", level="BLOCK",
        pattern=r"(raster_panel\([^\n]*\)\s*\*|\braster\w*\s*\*\s*hv\.)",
        # Deliberately crude, and it works BY NAMING — the message says so. A
        # rule that tracked "is this variable a raster" across statements would
        # need a parser, and sapper is a line matcher on purpose. The convention
        # (hold a raster in a variable called `raster`) is what lets a one-line
        # regex see the thing it guards. Its blind spot is honest and recorded in
        # docs/sapper_feedback/2026-08-26-sap009-sees-only-what-is-named.md.
        include=["tools/**", "src/bugarach/ui/**"], exclude=[],
        message="NOTHING IS DRAWN ON THE RASTER (Tony, 2026-08-26). The raster is "
                "black and white: one ink, one mark per event, and nothing "
                "competing with it. Detections, planted events, treatment "
                "windows, anchors and labels go in a LANE ABOVE it — symbols, or "
                "hashes where the cue needs rows — x-linked through the shared "
                "`t`. Stack ui.diagnostic.lane_panel over raster_panel in a "
                "Column; do not overlay onto the raster with `*`. raster_panel "
                "already refuses detection spans in its own docstring, and the "
                "way to break that is to overlay from OUTSIDE the module, which "
                "is what tools/make_benchmark_figures.py did the day before this "
                "rule existed. Identity and counts belong in the y-axis label or "
                "a header outside the plot, never as text over the marks. THIS "
                "CHECK SEES ONLY WHAT IS NAMED: hold the raster in a variable "
                "called `raster`.",
        # Assembled by concatenation, like _UM above: written whole, this
        # fixture is itself a line that draws on a raster, and the scan would
        # fire on the rule that forbids it. Fourth time a self-describing
        # string has tripped its own rule in this file.
        fixture_bad="raster = raster " + "* hv.VLine(t).opts(color='#a03623')",
        fixture_good="page = pn.Column(lane_panel(lanes, ext=ext), raster)",
    ),
    Rule(
        id="SAP010", level="BLOCK",
        # A maker that indexes the training recordings by the seed modulo the
        # set length answers BOTH of `train`'s seed blocks with one set, so
        # `pick_threshold` picks the operating point on the data the model was
        # just fitted to. The assertion inside `pick_threshold` compares SEEDS
        # and passes anyway, which is why this survived a murderboard.
        pattern=r"seed\s*%\s*len\s*\(",
        # PROSE WOULD NOT HAVE CAUGHT THIS. #356 fixed two call sites, said so
        # in its own commit message, and missed three more — one already on main
        # (`ablate_tube.py`) and two on an unmerged branch, written AFTER the fix
        # landed. Every number those three produced had its threshold picked on
        # the fitting recordings. A grep finds the fifth copy; a grep that runs
        # on every commit is what stops the sixth.
        include=["tools/**", "src/bugarach/**"], exclude=[],
        message="THE OPERATING POINT WOULD BE PICKED ON THE FITTING RECORDINGS. "
                "`learn.train.train` draws recordings from TRAIN_SEED_BLOCK and "
                "`pick_threshold` from VAL_SEED_BLOCK — disjoint on purpose, and "
                "asserted. But a maker that indexes by the seed " + "% len(recs) "
                "maps BOTH blocks onto one set, and the assertion still passes "
                "because it compares seeds rather than recordings. Use "
                "`learn.train.fold_maker(rec, train_seeds)`, which splits the "
                "training folds again and returns (mk, n_fit, n_val). It exists "
                "so the boundary has ONE implementation instead of one per call "
                "site — which is how three sites were still wrong a day after "
                "two were fixed.",
        fixture_bad="mk = lambda seed, _t=tuple(tr): rec(_t[seed " + "% len(_t)])",
        fixture_good="mk, n_fit, _ = fold_maker(rec, tr_seeds)",
    ),
    Rule(
        # SAP011 is spoken for by an unbuilt proposal
        # (docs/sapper_feedback/2026-08-28-a-negative-claim-about-code-went-stale-
        # in-a-contract.md), so this takes the next free id rather than the next
        # number. Two sessions reserved SAP010 on one day (#389); not again.
        id="SAP012", level="BLOCK",
        # Any arithmetic pairing two of the three event-time fields is a duration
        # being derived. `locs - t50rise` is the one that was actually written;
        # `peak - locs` is the plausible repair, and it is equally forbidden,
        # which is why the rule names the operation rather than the operands.
        # The comma catches the zip-the-two-fields form the original used to
        # spread the subtraction over two lines and out of a per-line grep.
        pattern=r"\.(locs|peak|t50rise)\b[^\n]*[-,][^\n]*\.(locs|peak|t50rise)\b",
        include=["src/bugarach/**", "tools/**"],
        # The MATLAB reference generator is the PRODUCER side by definition: it
        # reproduces explore_sce's prep to make the parity fixture, which is the
        # one context where computing this is the correct thing to do.
        exclude=["tools/matlab_ref/**"],
        message="BUGARACH DOES NOT DERIVE EVENT DURATIONS AND HAS NO OPINION ON "
                "WHAT ONE MEANS. Tony, 2026-08-29: \"matlab decides duration. "
                "bugarach python and webapp is not responsible for what the "
                "duration is derived from\" — and \"bugarach doesn't care what you "
                "put in the duration column. your mother's social security number "
                "works fine for 5 of 6 detectors.\" That is literal: five of the "
                "six never read the column, and the sixth paints each cell active "
                "for that many seconds without interpreting it. A number arrives "
                "in `width_sec` under the `width_def` naming the producer's rule; "
                "re-deriving one here duplicates a decision already made and "
                "overrides what was sent. It also silently returned ZERO for all "
                "2,215 events on folder input, because `locs` in a folder holds "
                "the t50rise — right shape, right dtype, no error, wrong number. "
                "Read `stream.width` (guarded by `stream.has_width`). "
                "FOUNDATIONS section 7.",
        fixture_bad="dur = [pk - on for pk, on in zip(st.locs, st." + "t50rise)]",
        fixture_good="dur = st.width if st.has_width else None",
    ),
    Rule(
        id="SAP013", level="BLOCK",
        # SAP012 stops the code computing a duration. This stops the PROSE
        # explaining what one means, which is the half that kept coming back.
        # Ten surfaces said locust "paints the rise interval". That was the SLOW
        # stream's rule; `fast` — the stream the bench actually scores — carries a
        # half-prominence width, so the sentence was false for every published
        # locust number, and stayed false through a session that was cleaning up
        # this exact area. Naming a producer's rule here cannot be kept true,
        # because it is not this repo's fact to maintain.
        pattern=r"rise[ -]interval",
        include=["src/bugarach/**", "tools/**", "README.md", "docs/GLOSSARY.md",
                 "docs/FOUNDATIONS.md", "docs/detector_history.md",
                 "docs/site/**"],
        # matlab_ref reproduces the producer's prep to build parity fixtures, and
        # export_folder_spec/ADR-0002/dated records are the producer contract and
        # the historical record — neither is this repo forming an opinion.
        exclude=["tools/matlab_ref/**", "tools/sapper.py"],
        message="BUGARACH DOES NOT DESCRIBE WHAT A DURATION MEANS. Tony, "
                "2026-08-29: \"there should be no reference to duration "
                "definitions in this repo. bugarach doesn't care what you put in "
                "the duration column.\" A number arrives in `width_sec` under the "
                "producer's `width_def`; five of the six detectors never read it "
                "and the sixth does not interpret it. Naming the rule that made it "
                "is not a fact this repo can keep true: ten surfaces said locust "
                "\"paints the rise interval\", which is the SLOW stream's rule — "
                "`fast`, the stream the bench scores, carries a half-prominence "
                "width, so the sentence was false for every published locust "
                "number. Say what the code does (paints the producer's duration) "
                "and stop. The producer contract (`docs/export_folder_spec.md`) is "
                "where rules are discussed with the people who write them.",
        fixture_bad="it paints each cell active for the rise interval instead",
        fixture_good="it paints each cell active for the producer's width_sec",
    ),
    Rule(
        id="SAP014", level="BLOCK",
        # One instrument, one acronym. The centrepiece of the loop was coined
        # MAHDCE on 2026-08-24 and is MAHICE from 2026-09-03 — and the D was
        # wrong by the glossary's own two-axis rule, which reserves "detection"
        # for the algorithm and not for the person. Two spellings of one term is
        # what GLOSSARY.md exists to prevent, and the window where both were live
        # in this tree lasted one afternoon. This closes it.
        pattern=_OLD_INSTRUMENT,
        include=["src/bugarach/**", "tools/**", "README.md", "docs/**"],
        # GLOSSARY.md is where the retired spelling is DEFINED as retired, so a
        # reader grepping it lands somewhere. The two dated documents record what
        # was written on the day and are not edited for later vocabulary — the
        # same posture the withdrawn paragraphs in the export contract keep.
        exclude=["docs/GLOSSARY.md", "tools/sapper.py",
                 "docs/todo/2026-08-24-the-null-leaks-and-the-excess-is-"
                 "mostly-selection.md",
                 "docs/handoffs/2026-08-25-the-adr-that-did-not-land.md"],
        message="ONE INSTRUMENT, ONE ACRONYM — it is MAHICE, machine-assisted "
                "human IDENTIFICATION of coordinated events (Tony, 2026-09-03). "
                "The retired spelling put \"detection\" in it, which "
                "docs/GLOSSARY.md reserves for the DETECTOR axis — \"Never "
                "'detection' (that's the detector axis)\" — so it spent a "
                "reserved word on the half of the pair that is a person. "
                "Identification is the more accurate verb besides: the machine "
                "detects candidates, and what the person adds is saying which of "
                "them are the thing. The retired spelling is defined, as retired, "
                "in docs/GLOSSARY.md; two dated records keep it and are exempt.",
        fixture_bad="the assessor is the machine half of " + _OLD_INSTRUMENT,
        fixture_good="the assessor is the machine half of MAHICE",
    ),
    Rule(
        id="SAP015", level="WARN",
        # House rule, Tony 2026-09-14: "data" is plural. A WARN, not a BLOCK: the
        # tree held 73 singular uses when this was written, some inside other
        # people's quoted words, which are not ours to regrammar. A determiner is
        # required before "data" so the rule reads prose and not code — `data is
        # None` has none, "the data is" does.
        pattern=r"(?i)\b(the|this|that|our|their|its|real|raw|input|source|no|"
                r"synthetic|simulated|recorded|new|more|less|much|enough|which|"
                r"whose|all|any|such|foreign|observed|imaging|calcium|same|your|"
                r"my|his|her) data (is|was|has|does|doesn't|isn't|wasn't|hasn't|"
                r"shows|says|suggests|indicates|contains|supports|refutes|lives|"
                r"sits|comes|goes|looks|reads|means|needs|makes|gives|arrives|"
                r"exists|stays|changes|tells|agrees|disagrees|belongs|matches|"
                r"fits|lacks|carries|holds|reaches|lands|remains|seems|appears|"
                r"allows|requires|proves|confirms|reveals|itself)\b",
        include=["*.md", "*.py", "*.html", "*.sh", "*.js", "*.txt"],
        # This file; vendored copies, which are re-copied rather than edited;
        # the producer's own delivery notes; and the built viewer, whose
        # template is already scanned. writing_conventions.md is where the wrong
        # form is shown AS wrong, the way GLOSSARY.md is exempt from SAP014.
        exclude=["tools/sapper.py", "docs/writing_conventions.md",".claude/agents/murderboard/*",
                 ".claude/skills/murderboard/*", "docs/session_protocol.md",
                 ".claude/hooks/session-start.sh", "tools/murderboard_freshness.sh",
                 "docs/exports/*", "docs/site/raster_viewer.html"],
        message="\"DATA\" IS PLURAL — house rule (Tony, 2026-09-14). Make its "
                "verb and pronoun agree: the data ARE, the data SHOW, the data "
                "WERE, the data HAVE, the data THEMSELVES, THESE data. "
                "\"Metadata\" and \"dataset\" keep their own grammar. If this "
                "line quotes someone, leave their words as they said them. "
                "docs/writing_conventions.md, \"Data\" is plural.",
        fixture_bad="the fit reaches 847 mHz where the data reaches 486",
        fixture_good="the fit reaches 847 mHz where the data reach 486, and data is None",
    ),
    Rule(
        id="SAP016", level="BLOCK",
        # THE SENTENCE THAT READS FINE AND EXPLAINS NOTHING. Tony, 2026-09-16, on
        # "Looking nearby means the bar rises when cells get busy, so chance lineups
        # in a busy stretch are not called": "it sort of makes sense to a human, and
        # there's nothing wrong at first, but then 'looking' what do you mean? ...
        # What bar? how did it rise?"
        #
        # The shape is an ACTIVITY STANDING IN FOR AN ACTOR: a gerund phrase is made
        # the subject of an explanation, so nobody does anything, and the verb after
        # "means" describes a result whose mechanism is now unstatable. The writer
        # knows the chain and skips it; the reader gets the conclusion and a fog.
        #
        # The repair is always the same and is always available: name who does it,
        # say what they compute, then say what follows. "CoactDetect draws its chance
        # copies from the surrounding minute, so a busier stretch gives bigger copy
        # counts, which raises the count a bin has to beat."
        #
        # DELIBERATELY NARROW — the plain-language templates only, where sixth-grade
        # prose is the requirement and every sentence is meant to survive a reader
        # with no background. Tree-wide it would fire on working notes, where the
        # shorthand is between people who share the chain. See docs/sapper_feedback/.
        # `[^.]` rather than `\w+\s+` between the two halves, because the first draft of
        # this rule could not fire on the sentence it was written for: the page says
        # "Looking <b>nearby</b> means", and inline markup does not match \w. A prose rule
        # scanning HTML has to be able to read through the tags.
        pattern=r"\b(Looking|Judging|Counting|Shifting|Choosing|Using|Taking|Setting|"
                r"Measuring|Comparing|Scoring|Picking|Running|Keeping|Drawing)\b"
                r"[^.]{0,45}?\bmeans\b",
        include=["tools/plain_*_template.html"], exclude=["tools/sapper.py"],
        message="AN ACTIVITY IS STANDING IN FOR AN ACTOR, and the mechanism is "
                "gone with it (Tony, 2026-09-16). \"Looking nearby means the bar "
                "rises\" — looking by whom? which bar? raised by what? A gerund "
                "made the subject of an explanation lets the writer skip the chain "
                "they already know. Name the program, say what it computes, then "
                "say what follows: \"CoactDetect draws its chance copies from the "
                "surrounding minute, so a busier stretch gives bigger copy counts, "
                "which raises the count a bin has to beat.\"",
        fixture_bad="<p>Looking nearby means the bar rises when cells get busy.</p>",
        fixture_good="<p>CoactDetect draws its copies from the surrounding minute, so a "
                     "busier stretch raises the count a bin has to beat.</p>",
    ),
    Rule(
        id="SAP017", level="BLOCK",
        # BANNED IN PERPETUITY. Tony, 2026-09-16, reading a figure caption that said a
        # program ran at its stored setting "not at the freshly chosen setting of Figure
        # 14": *"'freshly chosen' is hereby banned in perpetuity"*.
        #
        # The phrase is an adjective doing a noun's work. "Freshly" carries a whiff of
        # approval — fresh is better than stale — while saying nothing about WHO chose,
        # FROM WHAT, or WHEN, and here all three mattered: the rounds choose one value per
        # round, from held-out simulated recordings, and for four of the six detectors the
        # rounds disagreed with each other. A caption that says "freshly chosen" hides that
        # there is no single chosen value to speak of.
        #
        # It is also the THIRD word tried for the same idea in one review — "shipped" was
        # jargon, "default" was false, and this was decorative. The pattern behind all three
        # is reaching for an adjective instead of naming the procedure, so the repair is
        # always to name it: "the setting each round picked from the recordings it was
        # allowed to see".
        #
        # Tree-wide, because a ban in perpetuity that only covers one document is not one.
        # Exempt: this file, and the two places whose job is to record what was banned.
        pattern=r"\bfresh(ly)?[\s-]+(chosen|picked|selected|tuned)\b",
        include=["**"],
        exclude=["tools/sapper.py", "docs/sapper_feedback/**", "docs/reviews/**"],
        message="\"freshly chosen\" is BANNED IN PERPETUITY (Tony, 2026-09-16). The "
                "adjective flatters the value and hides the procedure: who chose it, "
                "out of what, and how many times? Name the procedure instead — \"the "
                "setting each round picked from the recordings it was allowed to see\" "
                "— which also makes it sayable that different rounds picked "
                "differently.",
        fixture_bad="at the freshly chosen setting of Figure 14.",
        fixture_good="at the setting each round picked from the recordings it could see.",
    ),
    Rule(
        id="SAP018", level="BLOCK",
        # SAY WHAT WAS OBSERVED, IN ONE VOCABULARY. Tony, 2026-09-16, on "a cell brightened 13.4
        # times an hour": not ok — "a cell with 13.4 events per hour" is. The house vocabulary for
        # the plain-language documents:
        #   * a CALCIUM EVENT is defined once, at the start, as an increase followed by a decrease in
        #     brightness; after that the text says calcium event, or event — never "brighten",
        #     "light up", "lit up";
        #   * a COORDINATED EVENT is a coordinated calcium event;
        #   * "synchronized" / "synchronous" appear only as another author's term, in quotes.
        # "Brightness" itself stays legal: the definition needs it once. Paper titles containing
        # "synchronization" stay legal too, which is why the synchron- half matches only the -ized and
        # -ous forms, and only when no opening quote precedes them.
        pattern=r"\bbright(en|ens|ened|ening|enings)\b|\blights? up\b|\blit up\b"
                r"|(?<![\"“‘'])\b[Ss]ynchroni[sz]ed\b|(?<![\"“‘'])\b[Ss]ynchronous\b",
        include=["tools/plain_*_template.html", "tools/make_plain_detector_review.py"],
        exclude=["tools/sapper.py"],
        message="PLAIN-DOCUMENT VOCABULARY (Tony, 2026-09-16). Say calcium event (one cell) or "
                "coordinated event (many cells), not \"brighten\" / \"light up\": a calcium event is "
                "defined once as an increase followed by a decrease in brightness, and after that it "
                "is an event. Use \"synchronized\" only as another author's term, inside quotes.",
        fixture_bad="<p>In the most recent paper, a cell brightened 13.4 times an hour.</p>",
        fixture_good='<p>neurons had 13.4 calcium events per neuron per hour, and "synchronized events".</p>',
    ),
    Rule(
        id="SAP019", level="BLOCK",
        # NEURONS, NOT CELLS. Tony, 2026-09-16: "we can call brain cells neurons. i think we can replace
        # cells with neurons throughout." The recordings are of neurons, and a second word for the same
        # thing makes a reader wonder whether it is a second thing.
        #
        # Templates only. The builder's code is full of `cells` as an identifier and a data key, and a
        # line matcher cannot tell those from drawn text; its display strings were converted with the
        # tokenizer instead. Two titles keep their words: Lehman et al. 2010's "(KNDy) cells of the
        # arcuate nucleus", and the journal Cell Reports.
        #
        # AND COORDINATED EVENTS, NOT LINEUPS. Tony, same day: spell the idea out once, then say
        # "coordinated event" — for the ones chance produces too. A coined second noun made a reader
        # ask whether a lineup and a coordinated event were different things.
        pattern=r"(?<!\(KNDy\) )\bcells?\b|(?<!\(KNDy\) )\bcell's\b|\bCells?\b(?! Reports)"
                r"|\b[Ll]ineups?\b|\b[Ll]in(e|es|ed|ing) up\b",
        include=["tools/plain_*_template.html"],
        exclude=["tools/sapper.py"],
        message="PLAIN-DOCUMENT NOUNS (Tony, 2026-09-16): say neuron / neurons, not cell / cells (paper "
                "titles and the journal Cell Reports excepted); and say coordinated event, not lineup or "
                "line up — including the coordinated events chance produces.",
        fixture_bad="<p>Each row is one cell, and each tick is one calcium event.</p>",
        fixture_good="<p>Each row is one neuron. B/dynorphin (KNDy) cells of the arcuate nucleus. "
                     "<i>Cell Reports</i></p>",
    ),
]


def _tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                         encoding="utf-8", check=True)   # see scan_staged
    return out.stdout.splitlines()


#: Paths no rule applies to, whatever its own include list says.
#:
#: VENDORED CODE CANNOT BE EDITED IN PLACE (CLAUDE.md, "Vendored copies"): a
#: refresh is a re-copy, so any edit sapper provoked here would be reverted by the
#: next one. A gate that fires on something you are forbidden to fix is a gate
#: that gets answered with the escape hatch every time, and an escape hatch used
#: routinely stops being an escape hatch.
#:
#: The first case was real and was a false positive on top of that: SAP005 wants
#: `<meta charset>` beside a `<title>`, and matched draughtsman's SVG `<title>`
#: elements -- an SVG has no head to put a charset in. Upstream is where a genuine
#: finding belongs, reported as a bug rather than patched into the copy.
GLOBAL_EXCLUDE = ("third_party/*",)


def _applies(rule: Rule, path: str) -> bool:
    if any(fnmatch.fnmatch(path, g) for g in GLOBAL_EXCLUDE):
        return False
    hit = any(fnmatch.fnmatch(path, g) for g in rule.include)
    exempt = any(fnmatch.fnmatch(path, g) for g in rule.exclude)
    return hit and not exempt


def _scan_lines(rule: Rule, path: str, lines) -> list[tuple[str, int, str]]:
    rx = re.compile(rule.pattern)
    return [(path, i, line.rstrip("\n"))
            for i, line in lines if rx.search(line)]


def scan_all() -> list[tuple[Rule, str, int, str]]:
    findings = []
    files = _tracked_files()
    for rule in RULES:
        for path in files:
            if not _applies(rule, path):
                continue
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    numbered = list(enumerate(f, 1))
            except OSError:
                continue
            for p, i, line in _scan_lines(rule, path, numbered):
                findings.append((rule, p, i, line))
    return findings


def scan_staged() -> list[tuple[Rule, str, int, str]]:
    # encoding="utf-8" is load-bearing on Windows: without it the diff is decoded in
    # the locale codepage, the reader thread swallows the UnicodeDecodeError, and
    # .stdout comes back None — so any staged ▼ or ✕ crashed the pre-commit hook
    # (2026-09-14). check_quotes.py hit and fixed the same thing in #535.
    out = subprocess.run(["git", "diff", "--cached", "--unified=0"],
                         capture_output=True, text=True, encoding="utf-8",
                         errors="replace", check=True).stdout
    findings = []
    path = None
    lineno = 0
    for raw in out.splitlines():
        if raw.startswith("+++ b/"):
            path = raw[6:]
        elif raw.startswith("@@"):
            m = re.search(r"\+(\d+)", raw)
            lineno = int(m.group(1)) - 1 if m else 0
        elif raw.startswith("+") and not raw.startswith("+++") and path:
            lineno += 1
            for rule in RULES:
                if _applies(rule, path) and re.search(rule.pattern, raw[1:]):
                    findings.append((rule, path, lineno, raw[1:]))
    return findings


def selftest() -> int:
    failures = 0
    for rule in RULES:
        rx = re.compile(rule.pattern)
        if not rx.search(rule.fixture_bad):
            print(f"SELFTEST FAIL {rule.id}: cannot fire on its bad fixture")
            failures += 1
        if rx.search(rule.fixture_good):
            print(f"SELFTEST FAIL {rule.id}: fires on its good fixture")
            failures += 1
    print(f"selftest: {len(RULES)} rules, {failures} failures")
    return 1 if failures else 0


def report(findings) -> int:
    blocked = False
    for rule, path, lineno, line in findings:
        print(f"{rule.level} {rule.id} {path}:{lineno}: {line.strip()}")
        print(f"    {rule.message}")
        blocked = blocked or rule.level == "BLOCK"
    if not findings:
        print("sapper: clear")
    return 1 if blocked else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--all", action="store_true")
    g.add_argument("--staged", action="store_true")
    g.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.list:
        for r in RULES:
            print(f"{r.id} {r.level:5s} {r.pattern}")
            print(f"    {r.message}")
        return 0
    return report(scan_staged() if args.staged else scan_all())


if __name__ == "__main__":
    sys.exit(main())
