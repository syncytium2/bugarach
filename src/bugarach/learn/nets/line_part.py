"""line_part — one architecture, one file.

ONE FILE IS ONE ARCHITECTURE. Drop a module in this folder with a ``@register``
line and it appears everywhere the registry is read — the bake-off, the lab
server's ``/api/capabilities``, the browser's model picker — with nothing else
edited. Delete the file and it is gone. That is what "added and removed at will"
has to mean to be worth saying (ADR-0005).

``nets/__init__.py`` imports every module in this folder at import time, so
registration is automatic; there is no list of architectures anywhere to fall
behind. Shared machinery — ``register``, ``_torch``, ``_dilated_stack``,
``receptive_field`` — lives there and is imported from there.

``line`` (with its orientation channel) plus participation (ADR-0010 part 5, preparation
only): a bounded vote per ROI whose sum is a count, the recording's floor as an input, and a
per-cell membership term in the loss. ``line`` itself is unchanged. See
``bugarach.learn.participation``.
"""
from bugarach.learn.nets import register
from bugarach.learn.nets.line import build_line
from bugarach.learn.participation import PART_TRAINING

__all__ = ["build_line_part"]


@register("line_part", note="line plus participation (ADR-0010 part 5): a bounded vote per ROI "
                            "summed into a count, the recording's floor as an input, and a "
                            "membership term in the loss",
          training=PART_TRAINING,
          n_scales=4, width=8, depth=6, max_center_frames=128, max_ratio=40.0,
          vote_gain=8.0, orientation=True, participation=True)
def build_line_part(**cfg):
    return build_line(**cfg)