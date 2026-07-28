"""Render a parsed :class:`~gh_matrix_viz.model.Workflow` as Markdown or Mermaid."""
from __future__ import annotations

from typing import Any, List

from .model import Job, Workflow


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, dict)):
        import json

        return "`" + json.dumps(value, separators=(",", ":")) + "`"
    return str(value)


def _columns(job: Job) -> List[str]:
    """Matrix keys first, then any extra keys introduced by ``include`` entries."""
    cols = list(job.matrix_keys)
    for combo in job.combinations:
        for k in combo:
            if k not in cols:
                cols.append(k)
    return cols


def render_markdown(wf: Workflow) -> str:
    lines: List[str] = [f"# {wf.name}", ""]
    lines.append(
        f"{len(wf.jobs)} job(s), {wf.total_combinations} concrete job "
        f"combination(s).\n"
    )
    for job in wf.jobs:
        title = f"## `{job.id}`"
        if job.name and job.name != job.id:
            title += f" — {job.name}"
        lines.append(title)
        if job.needs:
            lines.append(f"*needs:* {', '.join('`' + n + '`' for n in job.needs)}")
        lines.append("")

        cols = _columns(job)
        if not cols:
            lines.append("_No matrix — runs as a single job._\n")
            continue

        lines.append("| # | " + " | ".join(cols) + " |")
        lines.append("|---|" + "|".join(["---"] * len(cols)) + "|")
        for i, combo in enumerate(job.combinations, 1):
            row = " | ".join(_cell(combo.get(c)) for c in cols)
            lines.append(f"| {i} | {row} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _node_label(job: Job) -> str:
    label = job.id
    if job.has_matrix or job.combo_count > 1:
        label += f" ({job.combo_count})"
    # Mermaid node text in double quotes; escape any embedded quotes.
    return label.replace('"', "'")


def render_mermaid(wf: Workflow) -> str:
    lines: List[str] = ["```mermaid", "graph TD"]
    for job in wf.jobs:
        lines.append(f'    {job.id}["{_node_label(job)}"]')
    for job in wf.jobs:
        for dep in job.needs:
            lines.append(f"    {dep} --> {job.id}")
    lines.append("```")
    return "\n".join(lines) + "\n"
