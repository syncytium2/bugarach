"""chorus_norm — one architecture, one file.

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
from bugarach.learn.nets.chorus import build_chorus

__all__ = ["build_chorus_norm"]

@register("chorus_norm", note="chorus with each cell's encoder output standardised over "
                              "time before the vote",
          roi_width=4, roi_depth=4, head_width=8, head_depth=8, top_m=4, norm=True)
def build_chorus_norm(**cfg):
    return build_chorus(**cfg)
