from __future__ import annotations

from pathlib import Path

import pytest
from platformdirs import user_data_dir

from swing_analyzer.config.settings import (
    ApplicationConfiguration,
    default_config_path,
    load_settings,
    resolve_config_file,
)


def test_default_data_dir_uses_xdg() -> None:
    config = ApplicationConfiguration()
    expected = Path(user_data_dir("golf-swing-analyzer"))
    assert config.data_dir == expected


def test_log_dir_defaults_under_data_dir(tmp_path: Path) -> None:
    config = ApplicationConfiguration(data_dir=tmp_path)
    assert config.log_dir == tmp_path / "logs"


def test_invalid_semver_fails_fast() -> None:
    with pytest.raises(ValueError, match="invalid semver"):
        ApplicationConfiguration(ffmpeg_minimum_version="not-a-version")


def test_load_settings_missing_config_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.toml"
    with pytest.raises(ValueError, match="config file not found"):
        load_settings(config_file=missing)


def test_load_settings_from_toml(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    custom_data = tmp_path / "custom-data"
    config_path.write_text(
        f'data_dir = "{custom_data}"\nlog_level = "DEBUG"\n',
        encoding="utf-8",
    )
    config = load_settings(config_file=config_path)
    assert config.data_dir == custom_data
    assert config.log_level == "DEBUG"
    assert config.config_file == config_path


def test_ensure_directories_creates_paths(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    config = ApplicationConfiguration(data_dir=data_dir)
    config.ensure_directories()
    assert data_dir.is_dir()
    assert (data_dir / "logs").is_dir()


def test_load_settings_rejects_directory_as_config(tmp_path: Path) -> None:
    config_dir = tmp_path / "config-dir"
    config_dir.mkdir()
    with pytest.raises(ValueError, match="not a file"):
        load_settings(config_file=config_dir)


def test_resolve_config_file_uses_explicit_path(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text('log_level = "INFO"\n', encoding="utf-8")
    assert resolve_config_file(config_path) == config_path


def test_resolve_config_file_returns_none_when_no_default(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "swing_analyzer.config.settings.default_config_path",
        lambda: tmp_path / "missing" / "config.toml",
    )
    assert resolve_config_file(None) is None


def test_load_settings_from_xdg_default_config(tmp_path: Path, monkeypatch) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_path = config_dir / "config.toml"
    custom_data = tmp_path / "xdg-data"
    config_path.write_text(
        f'data_dir = "{custom_data}"\nlog_level = "ERROR"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "swing_analyzer.config.settings.default_config_path",
        lambda: config_path,
    )

    config = load_settings()
    assert config.data_dir == custom_data
    assert config.log_level == "ERROR"
    assert config.config_file == config_path


def test_default_config_path_under_xdg_config_dir() -> None:
    path = default_config_path()
    assert path.name == "config.toml"
    assert "golf-swing-analyzer" in str(path)


def test_to_effective_dict_includes_resolved_paths(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text('log_level = "WARNING"\n', encoding="utf-8")
    config = load_settings(config_file=config_path)
    effective = config.to_effective_dict()
    assert effective["log_level"] == "WARNING"
    assert effective["config_file"] == str(config_path.resolve())
    assert Path(effective["data_dir"]).is_absolute()
    assert Path(effective["log_dir"]).is_absolute()
