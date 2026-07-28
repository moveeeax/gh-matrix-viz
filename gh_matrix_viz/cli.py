"""Command-line entry point for gh-matrix-viz."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from .parse import WorkflowError, parse_workflow
from .render import render_markdown, render_mermaid


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gh-matrix-viz",
        description="Render a GitHub Actions workflow job matrix as a readable "
        "table or graph.",
    )
    p.add_argument("workflow", help="path to a workflow YAML file ('-' for stdin)")
    p.add_argument(
        "--format",
        "-f",
        choices=["table", "graph", "both"],
        default="table",
        help="output format (default: table)",
    )
    p.add_argument(
        "--job",
        "-j",
        action="append",
        help="only show this job id (repeatable)",
    )
    p.add_argument("--version", "-V", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        text = sys.stdin.read() if args.workflow == "-" else open(args.workflow).read()
    except OSError as exc:
        print(f"gh-matrix-viz: {exc}", file=sys.stderr)
        return 2

    try:
        wf = parse_workflow(text)
    except WorkflowError as exc:
        print(f"gh-matrix-viz: {exc}", file=sys.stderr)
        return 1

    if args.job:
        wanted = set(args.job)
        wf.jobs = [j for j in wf.jobs if j.id in wanted]
        if not wf.jobs:
            print(f"gh-matrix-viz: no matching job(s): {', '.join(args.job)}", file=sys.stderr)
            return 1

    parts: List[str] = []
    if args.format in ("table", "both"):
        parts.append(render_markdown(wf))
    if args.format in ("graph", "both"):
        parts.append(render_mermaid(wf))
    sys.stdout.write("\n".join(parts))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
