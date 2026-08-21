"""One `--dataset` flag for every analysis, plus whatever aliases a tool has earned.

Import and call `add(parser, want=..., aliases=...)`, then `get(args, want=...)`. Two
lines per tool, and the tool stops owning the question of what a directory is.

**Aliases are per tool and deliberate, not a blanket compatibility shim.** A first pass
here added `--store` and `--folder` to every analysis and tripped
`test_the_tool_takes_a_folder_and_not_a_store`, which exists because
`modularity_null.py` once read a `.mat` store plus a lab workbook plus a vendored ROI
roster, and the detour wrongly excluded a recording. That guard is right: on a tool
whose entire input contract is the export folder, a `--store` flag is the old mistake
wearing a new name. So each caller names the aliases it wants and `--store` only
appears where a store is genuinely readable.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))

from bugarach import dataset as ds  # noqa: E402

__all__ = ["add", "get"]

_WANT_HELP = {
    "export_folder": "an export folder (one CSV per recording)",
    "mat_store": "a .mat store (one .mat per recording)",
    "any": "an export folder or a .mat store",
}


def add(parser, *, want: str = "any", aliases: tuple[str, ...] = (),
        required: bool = True) -> None:
    """Add `--dataset`, plus only the aliases this tool should answer to.

    `aliases` is explicit because it is a contract question, not a convenience one:
    `--store` on a folder-only analysis re-invites the input the folder contract exists
    to exclude. Pass `("--folder",)` on a folder-only tool and `("--store",)` only
    where a `.mat` store is genuinely readable.
    """
    for a in aliases:
        if a == "--store" and want == "export_folder":
            raise ValueError(
                f"--store on a folder-only analysis: {_WANT_HELP[want]} is the whole "
                f"input contract, and a store flag is how that gets eroded")
    parser.add_argument(
        "--dataset", *aliases, dest="dataset", required=required,
        metavar="PATH_OR_NAME",
        help=(f"{_WANT_HELP[want]}. A path, or a bare name looked up under "
              f"${ds.ENV_VAR} (or the Dropbox data directory, found automatically) — "
              f"e.g. 2026-08-17_revised_2v_v2."))


def get(args, *, want: str = "any", quiet: bool = False) -> Path:
    """Resolve `--dataset`, check its shape, and print what was resolved.

    Printing is the point as much as resolving: a run that read the wrong corpus
    should be visible in its own log, not reconstructed afterwards from the numbers.
    Exits 2 with the reason rather than raising, because these are user errors at the
    command line and a traceback buries the sentence that helps.
    """
    try:
        path = ds.require(args.dataset, want=want, flag="--dataset")
    except ds.DataError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
    if not quiet:
        print(f"dataset: {path}")
        print(f"         {ds.describe(path)}")
    return path
