from __future__ import annotations

import logging
import sys

import structlog

from swing_analyzer.config.settings import ApplicationConfiguration


def configure_logging(config: ApplicationConfiguration) -> None:
    config.ensure_directories()
    assert config.log_dir is not None
    log_file = config.log_dir / "swing-analyzer.log"

    level = getattr(logging, config.log_level, logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger("swing_analyzer.file")
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(level)
    root_logger.propagate = False

    structlog_file = structlog.wrap_logger(
        logging.getLogger("swing_analyzer.file"),
        processors=[
            *shared_processors,
            structlog.processors.JSONRenderer(),
        ],
    )
    structlog.contextvars.bind_contextvars(_file_logger=structlog_file)


def get_logger(name: str = "swing_analyzer"):
    return structlog.get_logger(name)


def write_file_log(message: str, **kwargs: object) -> None:
    file_logger = structlog.contextvars.get_contextvars().get("_file_logger")
    if file_logger is not None:
        file_logger.info(message, **kwargs)
    else:
        logging.getLogger("swing_analyzer.file").info(message)
