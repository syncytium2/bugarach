"""Every registered architecture as a zero-argument builder, by name.

    draughtsman trace bugarach.learn.registered:chorus_norm --input-shape 1,30,600

**Why this exists: a variant's own builder does not build the variant.** The
registry stores each architecture's configuration beside its builder, and
``ARCHITECTURES[name].make()`` merges the two — that is what the bake-off, the lab
server and every tool here construct. The builder called bare does not:
``build_chorus_norm()`` forwards an empty ``**cfg`` to ``build_chorus``, whose
defaults are ``norm=False`` and ``vote_gain=None``, so it returns plain ``chorus``,
the failed control. ``build_chorus_gain_norm()`` likewise, 1,897 parameters where
the registered model has 1,905.

draughtsman's tracer calls its target with no arguments, so pointing it at
``build_chorus_norm`` traced ``chorus`` and every downstream check passed: coverage
is over the graph it was given, and that graph was complete — of the wrong model.
Found drawing the fair comparison's four architectures, 2026-09-19. ``tube`` and
``line_length`` happen to be safe, because their builders' defaults equal their
registered configuration, but that is a coincidence of the defaults and not a
property anything checks.

A module ``__getattr__`` rather than a list, for the reason ``nets/__init__.py``
gives for auto-registration: a list of names here would be one more list to fall
behind the folder.
"""

from __future__ import annotations

from bugarach.learn.nets import ARCHITECTURES


def __getattr__(name: str):
    try:
        return ARCHITECTURES[name].make
    except KeyError:
        raise AttributeError(f"no registered architecture named {name!r}") from None
