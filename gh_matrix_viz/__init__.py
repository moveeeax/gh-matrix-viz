"""Render a GitHub Actions workflow job matrix as a readable table or graph."""

from .model import Job, Workflow
from .expand import expand_matrix
from .parse import parse_workflow
from .render import render_markdown, render_mermaid

__version__ = "0.2.0"

__all__ = [
    "Job",
    "Workflow",
    "expand_matrix",
    "parse_workflow",
    "render_markdown",
    "render_mermaid",
]
