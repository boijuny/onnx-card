from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .core import count_operators, sorted_counts


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="onnx-card",
        description="Print an operator histogram for an ONNX model.",
    )
    p.add_argument("model", help="Path to .onnx model file")
    p.add_argument(
        "--sort",
        choices=["count", "name"],
        default="count",
        help="Sort operators by count (desc) or name (asc)",
    )
    p.add_argument("--top", type=int, default=0, help="Show only top N operators (0 = all)")
    p.add_argument("--json", action="store_true", help="Output JSON instead of a table")
    return p


def main(argv: list[str] | None = None) -> int:
    console = Console()
    args = build_parser().parse_args(argv)

    model_path = Path(args.model)
    if not model_path.exists():
        console.print(f"[red]Error:[/red] file not found: {model_path}")
        return 2

    try:
        counts = count_operators(model_path)
    except Exception as e:
        console.print(f"[red]Error:[/red] failed to read ONNX: {e}")
        return 1

    items = list(sorted_counts(counts, sort=args.sort))
    if args.top and args.top > 0:
        items = items[: args.top]

    if args.json:
        payload = {
            "model": str(model_path),
            "total_nodes": sum(counts.values()),
            "unique_operators": len(counts),
            "operators": {op: cnt for op, cnt in items},
        }
        console.print(json.dumps(payload, indent=2))
        return 0

    table = Table(title=f"Operator Counts — {model_path.name}")
    table.add_column("Operator", no_wrap=True)
    table.add_column("Count", justify="right")

    for op, cnt in items:
        table.add_row(op, str(cnt))

    table.caption = f"Unique operators: {len(counts)} • Total nodes: {sum(counts.values())}"
    console.print(table)
    return 0
