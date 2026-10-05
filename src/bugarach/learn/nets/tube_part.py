"""tube_part — one architecture, one file.

ONE FILE IS ONE ARCHITECTURE. Drop a module in this folder with a ``@register``
line and it appears everywhere the registry is read — the bake-off, the lab
server's ``/api/capabilities``, the browser's model picker — with nothing else
edited. Delete the file and it is gone. That is what "added and removed at will"
has to mean to be worth saying (ADR-0005).

``nets/__init__.py`` imports every module in this folder at import time, so
registration is automatic; there is no list of architectures anywhere to fall
behind. Shared machinery — ``register``, ``_torch``, ``_dilated_stack``,
``receptive_field`` — lives there and is imported from there.

``tube`` plus participation's count (ADR-0010 part 5, preparation only): the number of
ROIs with an onset in a centred 20-frame window and the recording's floor as inputs. Tube
averages cells away before any per-cell stage, so it has no vote to train and no membership
loss. ``tube`` itself is unchanged. See ``bugarach.learn.participation``.
"""
from bugarach.learn.nets import register
from bugarach.learn.nets.tube import build_tube
from bugarach.learn.participation import PART_TRAINING_NO_MEMBERSHIP

__all__ = ["build_tube_part"]


@register("tube_part", note="tube plus a count (ROIs with an onset in a 20-frame window) and "
                            "the recording's floor as inputs (ADR-0010 part 5); no membership "
                            "loss, since tube has no per-cell stage",
          training=PART_TRAINING_NO_MEMBERSHIP,
          n_scales=4, width=8, depth=6, max_center_frames=128, max_ratio=40.0,
          participation=True, count_frames=20)
def build_tube_part(**cfg):
    return build_tube(**cfg)