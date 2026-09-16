"""tube_no_bypass — one architecture, one file.

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

# The body lives with the model it varies, so the control is the shipped tube with
# one channel removed and not a second copy of it.
from bugarach.learn.nets.tube import build_tube

__all__ = ["build_tube_no_bypass"]

@register("tube_no_bypass", note="CONTROL for gauge -- the shipped tube with its "
                                 "raw-brightness bypass removed and nothing else changed",
          n_scales=4, width=8, depth=6, max_center_frames=128, max_ratio=40.0,
          bypass=False)
def build_tube_no_bypass(**cfg):
    return build_tube(**cfg)
