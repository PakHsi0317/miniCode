from devnotes.parser import parse


def test_parse_returns_line_count_and_keywords(tmp_path):
    f = tmp_path / "sample.py"
    f.write_text("def hello():\n    database = connect()\n")
    result = parse(f)

    assert result["line_count"] == 2
    keywords = dict(result["keywords"])
    assert keywords["hello"] == 1
    assert keywords["database"] == 1
    assert keywords["connect"] == 1


def test_parse_filters_stopwords(tmp_path):
    f = tmp_path / "stop.py"
    f.write_text("the the the import foo")
    result = parse(f)

    keywords = dict(result["keywords"])
    assert "the" not in keywords
    assert "import" not in keywords
    assert keywords["foo"] == 1


def test_parse_counts_frequency(tmp_path):
    f = tmp_path / "freq.py"
    f.write_text("database database connect database")
    result = parse(f)

    keywords = dict(result["keywords"])
    assert keywords["database"] == 3
    assert keywords["connect"] == 1


def test_parse_lowercases_keywords(tmp_path):
    f = tmp_path / "case.py"
    f.write_text("Database DATABASE database")
    result = parse(f)

    keywords = dict(result["keywords"])
    assert keywords["database"] == 3
    assert "Database" not in keywords
    assert "DATABASE" not in keywords


def test_parse_respects_max_keywords(tmp_path):
    f = tmp_path / "many.py"
    words = " ".join(f"word{i}" for i in range(100))
    f.write_text(words)
    result = parse(f, max_keywords=10)

    assert len(result["keywords"]) == 10


def test_parse_empty_file_returns_zero(tmp_path):
    f = tmp_path / "empty.py"
    f.write_text("")
    result = parse(f)

    assert result == {"line_count": 0, "keywords": []}


def test_parse_missing_file_returns_empty(tmp_path):
    f = tmp_path / "nonexistent.py"
    result = parse(f)

    assert result == {"line_count": 0, "keywords": []}


def test_parse_short_words_ignored(tmp_path):
    f = tmp_path / "short.py"
    f.write_text("a is of be database")
    result = parse(f)

    keywords = dict(result["keywords"])
    assert "a" not in keywords
    assert "is" not in keywords
    assert "of" not in keywords
    assert "be" not in keywords
    assert keywords["database"] == 1


def test_parse_line_count_no_trailing_newline(tmp_path):
    f = tmp_path / "noendline.py"
    f.write_text("line1\nline2")
    result = parse(f)
    assert result["line_count"] == 2


def test_parse_line_count_with_trailing_newline(tmp_path):
    f = tmp_path / "endline.py"
    f.write_text("line1\nline2\n")
    result = parse(f)
    assert result["line_count"] == 2
