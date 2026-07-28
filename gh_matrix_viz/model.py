"""Lightweight data model for a parsed workflow."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Job:
    """A single workflow job with its expanded matrix combinations."""

    id: str
    name: str
    needs: List[str] = field(default_factory=list)
    matrix_keys: List[str] = field(default_factory=list)
    combinations: List[Dict[str, Any]] = field(default_factory=lambda: [{}])

    @property
    def combo_count(self) -> int:
        return len(self.combinations)

    @property
    def has_matrix(self) -> bool:
        return bool(self.matrix_keys)


@dataclass
class Workflow:
    """A parsed workflow: a name plus its jobs in file order."""

    name: str
    jobs: List[Job] = field(default_factory=list)

    def job(self, job_id: str) -> Job | None:
        return next((j for j in self.jobs if j.id == job_id), None)

    @property
    def total_combinations(self) -> int:
        return sum(j.combo_count for j in self.jobs)
