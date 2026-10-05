"""chorus_line — one architecture, one file.

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

__all__ = ["build_chorus_line"]

@register("chorus_line", note="line's per-cell stage with chorus's two extra pooled "
                              "channels: vote spread over ROIs and the loudest four",
          n_scales=4, width=8, depth=6, max_center_frames=128, max_ratio=40.0,
          vote_gain=8.0, extra_pools=True, top_m=4)
def build_chorus_line(**cfg):
    return build_line(**cfg)
