"""Parse a GitHub Actions workflow YAML into the :mod:`model` types."""
from __future__ import annotations

from typing import Any, Dict, List

import yaml

from .expand import expand_matrix
from .model import Job, Workflow


class WorkflowError(ValueError):
    """Raised when the input is not a usable workflow file."""


def _normalize_needs(raw: Any) -> List[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return [str(x) for x in raw]
    raise WorkflowError(f"invalid 'needs' value: {raw!r}")


def _ordered_matrix_keys(matrix: Dict[str, Any] | None) -> List[str]:
    if not matrix:
        return []
    keys = [k for k in matrix if k not in ("include", "exclude")]
    if keys:
        return keys
    # include-only matrix: derive the columns from the include entries, in
    # first-seen order, so the table still has meaningful headers.
    seen: List[str] = []
    for entry in matrix.get("include") or []:
        for k in entry:
            if k not in seen:
                seen.append(k)
    return seen


def parse_workflow(text: str) -> Workflow:
    """Parse workflow YAML text into a :class:`Workflow`.

    ``on`` is intentionally ignored — YAML parses the bare word ``on`` as the
    boolean ``True``, but this tool only cares about ``jobs``.
    """
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as exc:  # pragma: no cover - passthrough
        raise WorkflowError(f"could not parse YAML: {exc}") from exc

    if not isinstance(doc, dict):
        raise WorkflowError("workflow is not a mapping")
    jobs_raw = doc.get("jobs")
    if not isinstance(jobs_raw, dict) or not jobs_raw:
        raise WorkflowError("workflow has no 'jobs' mapping")

    name = doc.get("name") or "workflow"
    jobs: List[Job] = []
    for job_id, spec in jobs_raw.items():
        spec = spec or {}
        matrix = (spec.get("strategy") or {}).get("matrix")
        combinations = expand_matrix(matrix)
        jobs.append(
            Job(
                id=str(job_id),
                name=str(spec.get("name") or job_id),
                needs=_normalize_needs(spec.get("needs")),
                matrix_keys=_ordered_matrix_keys(matrix),
                combinations=combinations,
            )
        )
    return Workflow(name=str(name), jobs=jobs)
