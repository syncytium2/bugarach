"""A trained model that outlives the process that fitted it — as JSON, not a pickle.

Until this existed, `docs/pipeline.md`'s blocker list said it plainly: *"Nothing
saves a trained model, so the learned branch cannot be tested on a fresh batch,
cannot detect on the user's folder, and cannot accept a model the user brings."*
`tools/run_learned_on_folder.py` is the workaround it forced — train and predict in
one process, because a separate program had no way to be handed a model.

WHY JSON AND NOT ``torch.save``. Two reasons, and the second is the one that
settles it.

* **These models are tiny, and that is their claimed advantage.** The tube is 1,149
  parameters; the largest architecture here is 2,393. A checkpoint is tens of
  kilobytes of numbers, so the format can be the one a person can read, a diff can
  show and `JSON.parse` can load — which is what makes a model shareable in *both*
  directions between the command line and the browser, rather than only out of one.
* **``torch.save`` is pickle, and pickle executes code on load.** The target flow in
  ADR-0005 is a user downloading a folder of models from the site and running them.
  A format where opening somebody else's model runs their code cannot be the format
  for that. Nothing here needs it: the state dict is arrays of floats.

WHAT TRAVELS WITH THE WEIGHTS, and why each is not optional:

* **the architecture name AND the config it was built with.** Rebuilding from the
  registry's *current* defaults would silently produce a different model when a
  default moves — the checkpoint records what it was, not what the name means now.
* **the encoding contract.** ``dt``, the onset field, and the row-ordering rule.
  A model is a function of the raster it was shown, and `learn.encode`'s own
  docstring is emphatic that row order is a coordinate rather than a label. A
  checkpoint that carried weights but not the encoding would reload into a model
  that means something else and say nothing.
* **the operating point.** ``threshold`` and ``merge_gap_frames`` were chosen on
  held-out data; a model without them is not a detector.
* **provenance.** What it was trained on, at which seed, for how many steps, at how
  many torch threads — that last because `train.THREADS` records reduction order
  changing F1 by 0.018 on this very code.

WHAT IT REFUSES. A checkpoint whose tensors do not match the shapes the rebuilt
architecture wants is refused by name, with both shapes printed. That is the failure
mode a saved model has — the file outlives an edit to the architecture — and it must
not load a partially-matching model and score it.
"""
from __future__ import annotations

import json
from pathlib import Path

FORMAT = "bugarach.learned-model"
VERSION = 1

#: Facts about how a recording becomes a raster, fixed for every architecture by
#: `learn.encode`. Written into the file rather than assumed, so a checkpoint from
#: a tree whose encoder has moved can be refused instead of silently misread.
ENCODING = {
    "onset_field": "t50rise",
    "row_order": "descending event count, ties by onset sequence — busiest first",
    "cell_values": "binary: 1 where that ROI has an onset in that frame",
    "axis": "frames; seconds enter only at dt",
}


def canonical(value):
    """A config in one spelling: numbers as floats (so ``8`` and ``8.0`` are one setting),
    tuples as lists, keys sorted when serialised. Booleans stay booleans."""
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        return {str(k): canonical(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [canonical(v) for v in value]
    return str(value)


def config_key(arch: str, cfg: dict, training: dict | None = None) -> str:
    """A stable name for *what to build and how to fit it*, independent of any result.

    The key a tuning run files a configuration under, and the key that ties a fitted file
    back to the configuration it came from. It hashes the architecture name, the full
    as-built ``cfg`` and the training settings that are choices (optimiser settings, crop,
    batch, number of training recordings), and deliberately NOT the training seed, the
    thread count or the torch version, which say how one fit of the configuration was run.
    """
    import hashlib

    choice = {k: v for k, v in (training or {}).items()
              if k in ("optimizer", "lr", "steps", "crop_frames", "batch", "n_train")}
    doc = json.dumps({"arch": arch, "cfg": canonical(cfg), "training": canonical(choice)},
                     sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(doc.encode("utf-8")).hexdigest()[:16]


def _tensor_out(t):
    return {"shape": list(t.shape), "data": [float(x) for x in t.flatten().tolist()]}


def save(trained, path, *, trained_on=None, train_seed=None, steps=None,
         n_fit=None, n_threshold_val=None, note="") -> Path:
    """Write ``trained`` to ``path`` as JSON. Returns the path.

    ``trained_on`` is the name of the corpus the weights were fitted on — a spec
    file, a folder, a generator seed block. It is what makes the cross-dataset
    question answerable later (ADR-0005: *"every artifact names the input it came
    from"*), so it is a keyword rather than something to be reconstructed.
    """
    from bugarach.learn.nets import ARCHITECTURES

    arch = ARCHITECTURES.get(trained.name)
    if arch is None:
        raise ValueError(
            f"{trained.name!r} is not a registered architecture, so nothing could "
            f"rebuild this file. Registered: {', '.join(sorted(ARCHITECTURES))}")
    state = {k: _tensor_out(v) for k, v in trained.model.state_dict().items()}
    # The config AS BUILT, not the registry's current defaults. Until 2026-09-16 this line
    # wrote `dict(arch.cfg)` under that same comment, because nothing carried the overrides
    # a fit was made with: a model fitted at `n_scales=6` wrote a file that refused to load,
    # and one fitted at `max_ratio=80` wrote a file that loaded as `max_ratio=40` and said
    # nothing. Where the fit recorded no config, the defaults are written and SAID to be.
    if trained.cfg is not None:
        cfg, cfg_source = dict(trained.cfg), "as built"
        rebuilt = arch.make(**cfg).state_dict()
        mismatch = sorted(k for k, v in trained.model.state_dict().items()
                          if k not in rebuilt or tuple(rebuilt[k].shape) != tuple(v.shape))
        if mismatch or set(rebuilt) != set(trained.model.state_dict()):
            raise ValueError(
                f"the config recorded for this {trained.name!r} does not rebuild the model "
                f"it is saved with (tensors {mismatch or 'differ in name'}); refusing to "
                f"write a file that would not load as itself.")
    else:
        cfg = dict(arch.cfg)
        cfg_source = ("registry defaults at save time: whatever made this model did not "
                      "record the config it was built with")
    doc = {
        "format": FORMAT,
        "version": VERSION,
        "arch": trained.name,
        "cfg": cfg,
        "config_key": config_key(trained.name, cfg, trained.training),
        "operating_point": {
            "threshold": float(trained.threshold),
            "merge_gap_frames": int(trained.merge_gap_frames),
            "dt_sec": float(trained.dt),
        },
        "encoding": dict(ENCODING),
        "n_params": int(trained.n_params),
        # How it was fitted, kept apart from `cfg` (what to build) and from `provenance`
        # (where the data came from). `None` when the fit did not record it.
        "training": dict(trained.training) if trained.training is not None else None,
        "provenance": {
            "cfg_source": cfg_source,
            "trained_on": trained_on,
            "train_seed": train_seed,
            "steps": steps,
            "n_fit": n_fit,
            "n_threshold_val": n_threshold_val,
            "train_seconds": round(float(trained.train_seconds), 3),
            "threads": int(trained.threads),
            "note": note,
        },
        "state_dict": state,
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    return path


def peek(path) -> dict:
    """Everything except the weights — for a listing, or a table of models.

    Separate from :func:`load` because reading what a model IS must not require
    torch: a report tool, the site build and a person with `jq` all want the
    provenance and none of them want to instantiate a network.
    """
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if doc.get("format") != FORMAT:
        raise ValueError(
            f"{path}: not a bugarach model — its 'format' is "
            f"{doc.get('format')!r}, not {FORMAT!r}")
    return {k: v for k, v in doc.items() if k != "state_dict"}


def load(path):
    """Rebuild a :class:`~bugarach.learn.train.Trained` from ``path``.

    The architecture is rebuilt from the name and the config the file records, then
    the tensors are checked against it **shape by shape** before anything is loaded.
    A file that no longer matches its architecture is the failure a checkpoint has,
    and it is refused with both shapes named rather than allowed to half-load.
    """
    import numpy as np
    import torch

    from bugarach.learn.nets import ARCHITECTURES, n_params
    from bugarach.learn.train import Trained

    path = Path(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("format") != FORMAT:
        raise ValueError(
            f"{path}: not a bugarach model — its 'format' is "
            f"{doc.get('format')!r}, not {FORMAT!r}")
    if doc.get("version") != VERSION:
        raise ValueError(
            f"{path}: written by format version {doc.get('version')!r}; this tree "
            f"reads version {VERSION}.")
    name = doc["arch"]
    arch = ARCHITECTURES.get(name)
    if arch is None:
        raise ValueError(
            f"{path}: architecture {name!r} is not registered in this tree. "
            f"Registered: {', '.join(sorted(ARCHITECTURES))}. One file per "
            f"architecture — dropping {name}.py into learn/nets/ is what makes "
            f"this file loadable.")
    if doc.get("encoding") != ENCODING:
        differ = sorted(k for k in set(ENCODING) | set(doc.get("encoding") or {})
                        if (doc.get("encoding") or {}).get(k) != ENCODING.get(k))
        raise ValueError(
            f"{path}: written against a different encoding contract "
            f"({', '.join(differ)}). The weights are a function of the raster the "
            f"model was shown, so a changed encoder makes them mean something "
            f"else. Re-train rather than re-interpret.")

    model = arch.make(**doc.get("cfg", {}))
    want = model.state_dict()
    got = doc["state_dict"]
    missing = sorted(set(want) - set(got))
    extra = sorted(set(got) - set(want))
    if missing or extra:
        raise ValueError(
            f"{path}: does not match architecture {name!r} as this tree builds it"
            + (f" — missing {missing}" if missing else "")
            + (f" — unexpected {extra}" if extra else "")
            + ". The architecture has changed since this file was written.")
    for key, spec in got.items():
        shape = tuple(spec["shape"])
        if shape != tuple(want[key].shape):
            raise ValueError(
                f"{path}: tensor {key!r} is {shape}, but {name!r} wants "
                f"{tuple(want[key].shape)}. The architecture has changed since "
                f"this file was written; re-train rather than reshape.")
        want[key] = torch.from_numpy(
            np.asarray(spec["data"], dtype=np.float32).reshape(shape))
    model.load_state_dict(want)
    model.eval()

    op = doc["operating_point"]
    prov = doc.get("provenance", {})
    return Trained(
        name=name, model=model,
        threshold=float(op["threshold"]),
        n_params=n_params(model),
        dt=float(op["dt_sec"]),
        merge_gap_frames=int(op["merge_gap_frames"]),
        train_seconds=float(prov.get("train_seconds") or 0.0),
        threads=int(prov.get("threads") or 0),
        cfg=dict(doc.get("cfg") or {}),
        training=doc.get("training"),
    )
