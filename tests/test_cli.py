import io
from contextlib import redirect_stdout, redirect_stderr

from gh_matrix_viz.cli import main

WF_PATH = "examples/ci.yml"


def _run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


def test_table_format_default(tmp_path):
    code, out, _ = _run([WF_PATH, "--format", "table"])
    assert code == 0
    assert "## `build`" in out
    assert "| # |" in out


def test_graph_format():
    code, out, _ = _run([WF_PATH, "--format", "graph"])
    assert code == 0
    assert "graph TD" in out
    assert "-->" in out


def test_both_format():
    code, out, _ = _run([WF_PATH, "--format", "both"])
    assert code == 0
    assert "graph TD" in out and "## `build`" in out


def test_job_filter():
    code, out, _ = _run([WF_PATH, "--job", "build", "--format", "graph"])
    assert code == 0
    assert 'build[' in out
    assert "deploy[" not in out


def test_missing_file_exit_2():
    code, _, err = _run(["does-not-exist.yml"])
    assert code == 2
    assert "gh-matrix-viz:" in err


def test_bad_job_filter_exit_1():
    code, _, err = _run([WF_PATH, "--job", "nope"])
    assert code == 1
    assert "no matching job" in err
