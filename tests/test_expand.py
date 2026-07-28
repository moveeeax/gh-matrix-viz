from gh_matrix_viz.expand import expand_matrix


def test_plain_cartesian_product():
    combos = expand_matrix({"os": ["linux", "mac"], "py": ["3.9", "3.11"]})
    assert combos == [
        {"os": "linux", "py": "3.9"},
        {"os": "linux", "py": "3.11"},
        {"os": "mac", "py": "3.9"},
        {"os": "mac", "py": "3.11"},
    ]


def test_no_matrix_runs_once():
    assert expand_matrix(None) == [{}]
    assert expand_matrix({}) == [{}]


def test_exclude_is_a_partial_match():
    combos = expand_matrix(
        {
            "os": ["linux", "mac"],
            "py": ["3.9", "3.11"],
            "exclude": [{"os": "mac", "py": "3.9"}],
        }
    )
    assert {"os": "mac", "py": "3.9"} not in combos
    assert len(combos) == 3


def test_scalar_axis_is_wrapped():
    combos = expand_matrix({"os": ["linux", "mac"], "arch": "amd64"})
    assert all(c["arch"] == "amd64" for c in combos)
    assert len(combos) == 2


def test_include_only_lists_entries():
    combos = expand_matrix(
        {"include": [{"os": "linux", "py": "3.9"}, {"os": "mac", "py": "3.11"}]}
    )
    assert combos == [{"os": "linux", "py": "3.9"}, {"os": "mac", "py": "3.11"}]


def test_github_documented_include_example():
    # https://docs.github.com/actions ... "Expanding or adding matrix configurations"
    combos = expand_matrix(
        {
            "fruit": ["apple", "pear"],
            "animal": ["cat", "dog"],
            "include": [
                {"color": "green"},
                {"color": "pink", "animal": "cat"},
                {"fruit": "apple", "shape": "circle"},
                {"fruit": "banana"},
                {"fruit": "banana", "animal": "cat"},
            ],
        }
    )
    assert combos == [
        {"fruit": "apple", "animal": "cat", "color": "pink", "shape": "circle"},
        {"fruit": "apple", "animal": "dog", "color": "green", "shape": "circle"},
        {"fruit": "pear", "animal": "cat", "color": "pink"},
        {"fruit": "pear", "animal": "dog", "color": "green"},
        {"fruit": "banana"},
        {"fruit": "banana", "animal": "cat"},
    ]


def test_include_does_not_overwrite_original_value():
    combos = expand_matrix(
        {"os": ["linux"], "include": [{"os": "windows", "extra": "x"}]}
    )
    # os=windows cannot merge into os=linux, so it becomes a new combination
    assert combos == [{"os": "linux"}, {"os": "windows", "extra": "x"}]
