import logging
import logging.handlers
import os
import sys
from typing import Iterable, Optional, Type

from powerflex_logging_utilities.default_log_format import DEFAULT_LOG_FORMAT


def min_log_level(level1: str, level2: Optional[str]) -> str:
    return min([level1, level2 or "CRITICAL"], key=logging.getLevelName)


def add_stdout_handler(
    logger_instance: logging.Logger,
    log_level: str,
    formatter: Type[logging.Formatter],
    log_format: str = DEFAULT_LOG_FORMAT,
) -> None:
    log_handler = logging.StreamHandler(stream=sys.stdout)
    log_handler.set_name("stdout")
    log_handler.setFormatter(formatter(fmt=log_format))
    log_handler.setLevel(log_level)
    logger_instance.addHandler(log_handler)


def add_file_handler(
    logger_instance: logging.Logger,
    log_level: str,
    filename: str,
    max_bytes: int,
    backup_count: int,
    formatter: Type[logging.Formatter],
    log_format: str = DEFAULT_LOG_FORMAT,
) -> None:
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    log_handler = logging.handlers.RotatingFileHandler(
        filename,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    log_handler.setFormatter(formatter(fmt=log_format))
    log_handler.setLevel(log_level)
    logger_instance.addHandler(log_handler)


def init_logger(
    logger_instance: logging.Logger,
    log_level: str,
    file_level: Optional[str],
    filename: Optional[str],
    max_bytes: int,
    backup_count: int,
    formatter: Type[logging.Formatter],
    log_format: str = DEFAULT_LOG_FORMAT,
) -> None:
    # We need the minimum log level of the two so that we don't accidentally
    # set a logger to log at a higher level than is expected by either the
    # stdout or file handlers.
    min_level = min_log_level(log_level, file_level)

    logger_instance.setLevel(min_level)

    add_stdout_handler(logger_instance, log_level, formatter, log_format)
    if not (file_level is None or filename is None):
        add_file_handler(
            logger_instance,
            file_level,
            filename,
            max_bytes,
            backup_count,
            formatter,
            log_format,
        )


def init_loggers(
    loggers: Iterable[logging.Logger],
    log_level: str,
    file_level: Optional[str],
    filename: Optional[str],
    max_bytes: int,
    backup_count: int,
    formatter: Type[logging.Formatter],
    log_format: str = DEFAULT_LOG_FORMAT,
    info_logger: Optional[logging.Logger] = None,
) -> None:
    print("Initializing loggers", log_level, file_level, filename, loggers)

    for logger_instance in loggers:
        init_logger(
            logger_instance,
            log_level,
            file_level,
            filename,
            max_bytes,
            backup_count,
            formatter,
            log_format,
        )

    if info_logger is None:
        return

    info_logger.info("Logging at level %s", log_level)
    if file_level is None or filename is None:
        info_logger.info("Not logging to a file")
    else:
        info_logger.info(
            "Logging at level %s to file %s",
            file_level,
            filename,
            extra={
                "config": dict(
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                )
            },
        )
