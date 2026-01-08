from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, Tuple

import onnx


def count_operators(model_path: str | Path) -> Counter[str]:
    """
    Count operator types (node.op_type) in the top-level ONNX graph.
    """
    model_path = Path(model_path)
    model = onnx.load(str(model_path))
    return Counter(node.op_type for node in model.graph.node)


def sorted_counts(counts: Counter[str], sort: str = "count") -> Iterable[Tuple[str, int]]:
    """
    Return operator counts sorted either by:
      - sort="count": descending count, then name
      - sort="name": ascending name, then descending count
    """
    items = list(counts.items())
    if sort == "name":
        items.sort(key=lambda kv: (kv[0], -kv[1]))
    else:
        items.sort(key=lambda kv: (-kv[1], kv[0]))
    return items


def counts_as_dict(counts: Counter[str], sort: str = "count") -> Dict[str, int]:
    """
    Convenience helper for JSON export or other integrations.
    """
    return {k: v for k, v in sorted_counts(counts, sort=sort)}
