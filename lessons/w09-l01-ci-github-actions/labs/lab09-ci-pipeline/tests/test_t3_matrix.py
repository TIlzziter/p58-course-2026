from ci_tools import expand_matrix


def job(matrix):
    return {"strategy": {"matrix": matrix}}


def test_no_matrix():
    assert expand_matrix({}) == [{}]
    assert expand_matrix({"strategy": {"fail-fast": False}}) == [{}]


def test_product_order():
    assert expand_matrix(job({"py": ["3.12", "3.13"], "os": ["linux", "mac"]})) == [
        {"py": "3.12", "os": "linux"}, {"py": "3.12", "os": "mac"},
        {"py": "3.13", "os": "linux"}, {"py": "3.13", "os": "mac"},
    ]


def test_exclude():
    m = {"py": ["3.12", "3.13"], "os": ["linux", "mac"], "exclude": [{"py": "3.12", "os": "mac"}]}
    assert len(expand_matrix(job(m))) == 3
    assert {"py": "3.12", "os": "mac"} not in expand_matrix(job(m))


def test_exclude_partial_key():
    m = {"py": ["3.12", "3.13"], "os": ["linux", "mac"], "exclude": [{"os": "mac"}]}
    assert expand_matrix(job(m)) == [{"py": "3.12", "os": "linux"}, {"py": "3.13", "os": "linux"}]


def test_include_extends_matching():
    m = {"py": ["3.12", "3.13"], "include": [{"py": "3.13", "experimental": True}]}
    assert expand_matrix(job(m)) == [{"py": "3.12"}, {"py": "3.13", "experimental": True}]


def test_include_new_combo():
    m = {"py": ["3.12"], "include": [{"py": "3.14", "os": "linux"}]}
    assert expand_matrix(job(m)) == [{"py": "3.12"}, {"py": "3.14", "os": "linux"}]


def test_include_only():
    m = {"include": [{"name": "a"}, {"name": "b"}]}
    assert expand_matrix(job(m)) == [{"name": "a"}, {"name": "b"}]
