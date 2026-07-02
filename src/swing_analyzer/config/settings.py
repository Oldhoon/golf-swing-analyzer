from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Literal

from platformdirs import user_data_dir
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from pydantic_settings.sources import TomlConfigSettingsSource

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


def default_data_dir() -> Path:
    return Path(user_data_dir("golf-swing-analyzer"))


class ApplicationConfiguration(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SWING_ANALYZER_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    data_dir: Path = Field(default_factory=default_data_dir)
    log_dir: Path | None = None
    config_file: Path | None = None
    log_level: LogLevel = "INFO"
    ffmpeg_minimum_version: str = "6.0.0"
    opencv_minimum_version: str = "4.8.0"
    mediapipe_minimum_version: str = "0.10.0"

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return str(value).upper()

    @field_validator(
        "ffmpeg_minimum_version",
        "opencv_minimum_version",
        "mediapipe_minimum_version",
    )
    @classmethod
    def validate_semver(cls, value: str) -> str:
        if not re.match(r"^\d+\.\d+\.\d+", value):
            raise ValueError(f"invalid semver: {value}")
        return value

    @model_validator(mode="after")
    def resolve_log_dir(self) -> ApplicationConfiguration:
        if self.log_dir is None:
            self.log_dir = self.data_dir / "logs"
        return self

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        sources: list[PydanticBaseSettingsSource] = [init_settings, env_settings]
        config_file = cls._resolve_config_file(init_settings)
        if config_file is not None:
            sources.append(TomlConfigSettingsSource(settings_cls, toml_file=config_file))
        return tuple(sources)

    @classmethod
    def _resolve_config_file(cls, init_settings: PydanticBaseSettingsSource) -> Path | None:
        init_kwargs = init_settings()
        config_file = init_kwargs.get("config_file")
        if config_file is None:
            return None
        path = Path(config_file)
        if not path.exists():
            raise ValueError(f"config file not found: {path}")
        if not path.is_file():
            raise ValueError(f"config path is not a file: {path}")
        return path

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        assert self.log_dir is not None
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def to_effective_dict(self) -> dict[str, Any]:
        return {
            "data_dir": str(self.data_dir.resolve()),
            "log_dir": str(self.log_dir.resolve()) if self.log_dir else None,
            "log_level": self.log_level,
            "config_file": str(self.config_file.resolve()) if self.config_file else None,
            "ffmpeg_minimum_version": self.ffmpeg_minimum_version,
            "opencv_minimum_version": self.opencv_minimum_version,
            "mediapipe_minimum_version": self.mediapipe_minimum_version,
        }


def load_settings(config_file: Path | None = None) -> ApplicationConfiguration:
    kwargs: dict[str, Any] = {}
    if config_file is not None:
        kwargs["config_file"] = config_file
    return ApplicationConfiguration(**kwargs)
