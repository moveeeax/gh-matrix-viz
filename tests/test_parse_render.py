import pytest

from gh_matrix_viz.parse import parse_workflow, WorkflowError
from gh_matrix_viz.render import render_markdown, render_mermaid

WF = """
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        py: ["3.9", "3.11"]
        os: [ubuntu-latest, macos-latest]
        exclude:
          - os: macos-latest
            py: "3.9"
  test:
    needs: build
    runs-on: ubuntu-latest
  deploy:
    needs: [build, test]
    runs-on: ubuntu-latest
"""


def test_parse_jobs_and_needs():
    wf = parse_workflow(WF)
    assert wf.name == "CI"
    assert [j.id for j in wf.jobs] == ["build", "test", "deploy"]
    assert wf.job("deploy").needs == ["build", "test"]
    # 2x2 minus one exclude
    assert wf.job("build").combo_count == 3
    assert wf.job("test").combo_count == 1


def test_needs_string_and_list_normalize():
    wf = parse_workflow(WF)
    assert wf.job("test").needs == ["build"]
    assert wf.job("deploy").needs == ["build", "test"]


def test_missing_jobs_raises():
    with pytest.raises(WorkflowError):
        parse_workflow("name: nope\non: push\n")


def test_markdown_has_table_with_headers_and_rows():
    md = render_markdown(parse_workflow(WF))
    assert "# CI" in md
    assert "## `build`" in md
    assert "| py | os |" in md or "| py | os |".replace(" ", "") in md.replace(" ", "")
    # 3 data rows for build
    assert md.count("\n| 1 |") == 1
    assert "_No matrix — runs as a single job._" in md  # test/deploy


def test_mermaid_lists_nodes_and_edges():
    mm = render_mermaid(parse_workflow(WF))
    assert mm.startswith("```mermaid\ngraph TD")
    assert 'build["build (3)"]' in mm
    assert "build --> test" in mm
    assert "build --> deploy" in mm
    assert "test --> deploy" in mm
    assert mm.rstrip().endswith("```")


def test_include_adds_columns_in_table():
    wf = parse_workflow(
        """
name: inc
on: push
jobs:
  b:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        os: [linux]
        include:
          - os: linux
            toolchain: nightly
"""
    )
    md = render_markdown(wf)
    assert "toolchain" in md
    assert "nightly" in md
