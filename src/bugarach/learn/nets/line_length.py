"""line_length — one architecture, one file.

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

__all__ = ["build_line_length"]


@register("line_length", note="line with the orientation channels removed — the ablation that "
                              "says what the second sensor is worth",
          n_scales=4, width=8, depth=6, max_center_frames=128, max_ratio=40.0,
          vote_gain=8.0)
def build_line_length(**cfg):
    """`line` with **one** sensor: how much of the field is lit, and no measure of how
    tightly.

    This is the model `line` was for its first day, kept as a registered architecture
    rather than as a flag, so the second sensor's contribution is measured in the same
    run, by the same scorer, on the same folds as everything else — the discipline
    `tube`'s 2x2 mechanism screen already follows, where `tube` itself is the control
    cell and is re-measured rather than quoted.

    Tony asked for both sensors (2026-09-15). If orientation does not earn its 72
    parameters here, this file is the honest default and `line` is the one to delete.
    """
    return build_line(orientation=False, **cfg)
