"""Expand a GitHub Actions ``strategy.matrix`` into concrete job combinations.

The algorithm mirrors GitHub's documented semantics, including the subtle parts:

* ``exclude`` entries are partial matches removed from the cartesian product.
* ``include`` entries merge into the *original* combinations when they do not
  overwrite an original matrix value; entries that fit nowhere are appended as
  new combinations. Crucially, an appended ``include`` combination is **not** a
  merge target for later ``include`` entries — only the original expanded
  combinations are. That is what makes the classic ``banana`` example produce
  both ``{fruit: banana}`` and ``{fruit: banana, animal: cat}``.
"""
from __future__ import annotations

import itertools
from typing import Any, Dict, List


Combo = Dict[str, Any]


def _cartesian(axes: Dict[str, List[Any]]) -> List[Combo]:
    if not axes:
        return []
    keys = list(axes.keys())
    products = itertools.product(*(axes[k] for k in keys))
    return [dict(zip(keys, values)) for values in products]


def _matches(combo: Combo, partial: Combo) -> bool:
    """True when every key in ``partial`` is present in ``combo`` and equal."""
    return all(k in combo and combo[k] == v for k, v in partial.items())


def _compatible(combo: Combo, inc: Combo, original_keys: set) -> bool:
    """An include entry fits a combo when it never overwrites an original value."""
    for k, v in inc.items():
        if k in original_keys and combo.get(k) != v:
            return False
    return True


def expand_matrix(matrix: Dict[str, Any] | None) -> List[Combo]:
    """Return the concrete job combinations for a ``strategy.matrix`` mapping.

    A falsy matrix yields a single empty combination (a job with no matrix still
    runs once). ``include`` on its own (no axes) yields exactly those entries.
    """
    if not matrix:
        return [{}]

    include = matrix.get("include") or []
    exclude = matrix.get("exclude") or []
    axes = {
        k: (v if isinstance(v, list) else [v])
        for k, v in matrix.items()
        if k not in ("include", "exclude")
    }
    original_keys = set(axes.keys())

    base = _cartesian(axes)
    # exclude: drop any base combination matched by an exclude entry
    base = [c for c in base if not any(_matches(c, ex) for ex in exclude)]

    combos: List[Combo] = [dict(c) for c in base]  # merge targets
    extra: List[Combo] = []

    for inc in include:
        merged = False
        for combo in combos:
            if _compatible(combo, inc, original_keys):
                combo.update(inc)
                merged = True
        if not merged:
            extra.append(dict(inc))

    result = combos + extra
    # A matrix that is only include-with-no-axes should not carry the empty combo.
    return [c for c in result if c] or [{}]
