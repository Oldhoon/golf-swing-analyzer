from __future__ import annotations

from pathlib import Path

import pytest

from swing_analyzer.config.settings import ApplicationConfiguration


@pytest.fixture
def config(tmp_path: Path) -> ApplicationConfiguration:
    return ApplicationConfiguration(data_dir=tmp_path / "data")
