"""tube_guard — one architecture, one file.

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

from bugarach.learn.nets import _dilated_stack, _torch, receptive_field, register

# The variant body lives with the model it varies: three of these differ from
# tube by a kernel change alone, so duplicating the builder would make the
# comparison a comparison of two copies.
from bugarach.learn.nets.tube import _build_tube_variant

__all__ = ["build_tube_guard"]

@register("tube_guard", note="V1 -- centre minus GUARDED surround: the reference stops "
                             "abutting the sample it judges",
          mode="subtract", guard_frames=8, n_scales=4, width=8, depth=6,
          max_center_frames=128, max_ratio=40.0)
def build_tube_guard(**cfg):
    return _build_tube_variant(**cfg)
