from devnotes.scanner import scan


def test_scan_finds_default_extensions(tmp_path):
    (tmp_path / "a.py").write_text("a")
    (tmp_path / "b.md").write_text("b")
    (tmp_path / "c.txt").write_text("c")
    (tmp_path / "d.jpg").write_text("d")  # not in defaults

    results = scan(tmp_path)
    names = {p.name for p in results}

    assert names == {"a.py", "b.md", "c.txt"}


def test_scan_skips_default_ignore_dirs(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config.txt").write_text("ignored")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "lib.py").write_text("ignored")
    (tmp_path / "good.py").write_text("good")

    results = scan(tmp_path)
    names = {p.name for p in results}

    assert "good.py" in names
    assert "config.txt" not in names
    assert "lib.py" not in names


def test_scan_recurses_into_subdirs(tmp_path):
    (tmp_path / "a" / "b" / "c").mkdir(parents=True)
    (tmp_path / "a" / "b" / "c" / "deep.py").write_text("deep")

    results = scan(tmp_path)

    assert any(p.name == "deep.py" for p in results)


def test_scan_custom_extensions(tmp_path):
    (tmp_path / "a.py").write_text("a")
    (tmp_path / "b.rst").write_text("b")

    results = scan(tmp_path, extensions={".rst"})
    names = {p.name for p in results}

    assert names == {"b.rst"}


def test_scan_custom_ignore_dirs(tmp_path):
    (tmp_path / "skipme").mkdir()
    (tmp_path / "skipme" / "x.py").write_text("x")
    (tmp_path / "keep.py").write_text("y")

    results = scan(tmp_path, ignore_dirs={"skipme"})
    names = {p.name for p in results}

    assert names == {"keep.py"}


def test_scan_empty_dir_returns_empty(tmp_path):
    results = scan(tmp_path)
    assert results == []


def test_scan_does_not_return_directories(tmp_path):
    (tmp_path / "subdir").mkdir()
    (tmp_path / "file.py").write_text("f")

    results = scan(tmp_path)

    assert all(p.is_file() for p in results)
