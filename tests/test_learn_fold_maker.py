"""The fitting set and the threshold-validation set must not overlap.

``pick_threshold``'s docstring has always called its seed separation *"explicit
and asserted rather than assumed"*, and the assertion in it has always passed —
because it compares **seeds**, and every caller supplied a ``make_recording``
that mapped every seed onto the same handful of **recordings**. The guarantee was
stated in one file and thrown away in the next.

So these tests check the property the assertions could not: that the recordings
handed to the two blocks are disjoint sets of objects. A seed test would pass
against the defect this file exists to prevent.
"""

from __future__ import annotations

import pytest

from bugarach.learn.train import (TRAIN_SEED_BLOCK, VAL_SEED_BLOCK, fold_maker,
                                  pin_threads)


def _rec(seed):
    """Stand-in for the generator: identity enough to tell recordings apart."""
    return (f"slice-{seed}", f"gt-{seed}")


def _drawn(mk, block, n):
    return {mk(block + i)[0] for i in range(n)}


def test_the_two_blocks_never_draw_the_same_recording():
    mk, n_fit, n_val = fold_maker(_rec, [1000, 1001, 1002, 1004, 1005, 1006])
    assert (n_fit, n_val) == (4, 2)
    # Drawn well past the set sizes, because the maker wraps modulo and the
    # defect this replaces only showed up once the wrap put both blocks on the
    # same recording.
    fit = _drawn(mk, TRAIN_SEED_BLOCK, 40)
    val = _drawn(mk, VAL_SEED_BLOCK, 40)
    assert not (fit & val), f"fit and val share {sorted(fit & val)}"
    assert len(fit) == 4 and len(val) == 2


def test_the_held_out_fold_is_unreachable():
    """Not by discipline — the scored fold is simply not in the list."""
    train_seeds = [1000, 1001, 1002, 1004, 1005, 1006]
    held_out = {"slice-1003", "slice-1007"}
    mk, _, _ = fold_maker(_rec, train_seeds)
    reached = _drawn(mk, TRAIN_SEED_BLOCK, 60) | _drawn(mk, VAL_SEED_BLOCK, 60)
    assert not (reached & held_out)


def test_a_fold_too_small_to_split_is_refused():
    """Rather than silently picking the operating point on the fitting set.

    One recording cannot be both, and returning it twice is the defect wearing a
    different shape.
    """
    with pytest.raises(ValueError, match="had just fitted"):
        fold_maker(_rec, [1000])


def test_n_val_cannot_consume_the_whole_fold():
    mk, n_fit, n_val = fold_maker(_rec, [1000, 1001, 1002], n_val=9)
    assert n_fit >= 1 and n_val >= 1
    assert not (_drawn(mk, TRAIN_SEED_BLOCK, 20) & _drawn(mk, VAL_SEED_BLOCK, 20))


def test_threads_are_pinned_and_pinning_is_idempotent():
    """The published bake-off reproduced only at 10 threads; 1 is portable."""
    pytest.importorskip("torch")
    assert pin_threads() == 1
    assert pin_threads() == 1
