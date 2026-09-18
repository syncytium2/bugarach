"""line_bound — one architecture, one file.

ONE FILE IS ONE ARCHITECTURE. Drop a module in this folder with a ``@register``
line and it appears everywhere the registry is read — the bake-off, the lab
server's ``/api/capabilities``, the browser's model picker — with nothing else
edited. Delete the file and it is gone. That is what "added and removed at will"
has to mean to be worth saying (ADR-0005).

``nets/__init__.py`` imports every module in this folder at import time, so
registration is automatic; there is no list of architectures anywhere to fall
behind. Shared machinery — ``register``, ``_torch``, ``_dilated_stack``,
``receptive_field`` — lives there and is imported from there.
"""

from bugarach.learn.nets import register
from bugarach.learn.nets.line import build_line

__all__ = ["build_line_bound"]


@register("line_bound", note="line with its vote bounded in time as well as height, and the "
                             "empty-field floor subtracted — the variant that says whether "
                             "line's soft cap matters",
          n_scales=4, width=8, depth=6, max_center_frames=128, max_ratio=40.0,
          vote_gain=8.0, orientation=True, bound_vote=True)
def build_line_bound(**cfg):
    """`line` with **"one ROI, one vote" made true of the integral**, not only the height.

    A murderboard of the `line` report (2026-09-16) found that `line`'s sigmoid caps a
    vote's height and not how long it lasts, so a four-onset burst delivers 1.7–2.7x the
    integrated vote of one onset to a stage that reads the integral. It also found the
    concentration channels reading a ratio of two vote floors on an empty field. Asked
    whether to rewrite the docstring or the architecture, Tony chose to measure both:
    `line` stays as it was measured, and this file is the fixed build beside it, fitted
    in the same run by the same scorer. ``build_line``'s docstring says what
    ``bound_vote`` changes.

    If the bound earns nothing here, `line` keeps its place and this file is the one to
    delete.
    """
    cfg.setdefault("bound_vote", True)
    return build_line(**cfg)
