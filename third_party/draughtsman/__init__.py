# vendored from draughtsman @ 62a13e5 — canonical source; do NOT edit here,
# update upstream (syncytium2/draughtsman) and re-copy the whole package.
"""draughtsman — readable architecture diagrams for PyTorch models.

Three stages, and the split between them is the design (SPEC.md §4):

    model -> [trace] -> graph.json -> [abstract] -> spec.json -> [render] -> figure.svg
              facts                    judgement                  deterministic

``trace`` needs torch. ``check`` and ``render`` need neither torch nor any system
binary, so a machine that only draws a figure installs almost nothing.
"""

__version__ = "0.1.0"

FORMAT = "0"  # bumped when graph.json / spec.json change shape

__all__ = ["FORMAT", "__version__"]
