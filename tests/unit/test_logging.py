from __future__ import annotations

from unittest.mock import MagicMock, patch

from swing_analyzer.logging.setup import write_file_log


def test_write_file_log_without_configured_context() -> None:
    mock_logger = MagicMock()
    with (
        patch(
            "swing_analyzer.logging.setup.structlog.contextvars.get_contextvars",
            return_value={},
        ),
        patch(
            "swing_analyzer.logging.setup.logging.getLogger",
            return_value=mock_logger,
        ),
    ):
        write_file_log("fallback message", operation="test")
    mock_logger.info.assert_called_once_with("fallback message")


def test_write_file_log_uses_bound_file_logger() -> None:
    file_logger = MagicMock()
    with patch(
        "swing_analyzer.logging.setup.structlog.contextvars.get_contextvars",
        return_value={"_file_logger": file_logger},
    ):
        write_file_log("structured", capability="gpu")
    file_logger.info.assert_called_once_with("structured", capability="gpu")
