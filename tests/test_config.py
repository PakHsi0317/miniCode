import pytest

from devnotes.config import DEFAULTS, _deep_merge, load_config


def test_load_config_returns_defaults_when_no_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert config == DEFAULTS


def test_load_config_returns_defaults_for_missing_path(tmp_path):
    config = load_config(tmp_path / "missing.yaml")
    assert config == DEFAULTS


def test_load_config_merges_user_overrides(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("keywords:\n  max_per_file: 50\n")

    config = load_config(cfg)

    assert config["keywords"]["max_per_file"] == 50
    assert config["scan"]["extensions"] == DEFAULTS["scan"]["extensions"]


def test_load_config_user_list_replaces_default(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("scan:\n  extensions: ['.rst']\n")

    config = load_config(cfg)

    assert config["scan"]["extensions"] == [".rst"]


def test_load_config_invalid_yaml_raises(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("- not\n- a\n- mapping\n")

    with pytest.raises(ValueError, match="must contain a YAML mapping"):
        load_config(cfg)


def test_load_config_empty_file_uses_defaults(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("")

    config = load_config(cfg)

    assert config == DEFAULTS


def test_deep_merge_recursive():
    base = {"a": {"b": 1, "c": 2}, "d": 3}
    overrides = {"a": {"b": 99}}

    result = _deep_merge(base, overrides)

    assert result == {"a": {"b": 99, "c": 2}, "d": 3}


def test_deep_merge_does_not_mutate_base():
    base = {"a": {"b": 1}}
    overrides = {"a": {"b": 99}}

    _deep_merge(base, overrides)

    assert base == {"a": {"b": 1}}


def test_deep_merge_replaces_lists():
    base = {"x": [1, 2, 3]}
    overrides = {"x": [9]}

    result = _deep_merge(base, overrides)

    assert result == {"x": [9]}


def test_deep_merge_adds_new_keys():
    base = {"a": 1}
    overrides = {"b": 2}

    result = _deep_merge(base, overrides)

    assert result == {"a": 1, "b": 2}
