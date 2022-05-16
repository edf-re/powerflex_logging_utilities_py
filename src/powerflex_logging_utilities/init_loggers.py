import logging
import logging.handlers
import os
import sys
from typing import Any, Collection, Dict, Optional, TextIO, Type, Union, cast

from powerflex_logging_utilities.default_log_format import DEFAULT_LOG_FORMAT
from powerflex_logging_utilities.json_formatter import JsonFormatter

DEFAULT_LOGFILE_MAX_BYTES = 1000 * 1000 * 10  # 10 megabytes
DEFAULT_LOGFILE_BACKUP_COUNT = 25


def min_log_level(level1: Union[str, int], level2: Optional[Union[str, int]]) -> int:
    if isinstance(level1, str):
        level1 = cast(int, logging.getLevelName(level1))
    if not isinstance(level2, int):
        level2 = cast(int, logging.getLevelName(level2 or "CRITICAL"))
    return min([level1, level2])


def add_stream_handler(
    logger_instance: logging.Logger,
    log_level: Union[str, int],
    formatter: Type[logging.Formatter],
    formatter_kwargs: Optional[Dict[str, Any]] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    stream: TextIO = sys.stdout,
) -> None:
    if formatter_kwargs is None:
        formatter_kwargs = {}
    log_handler = logging.StreamHandler(stream=stream)
    log_handler.set_name("stdout")
    log_handler.setFormatter(formatter(fmt=log_format, **formatter_kwargs))
    log_handler.setLevel(log_level)
    logger_instance.addHandler(log_handler)


def add_file_handler(
    logger_instance: logging.Logger,
    log_level: Union[str, int],
    filename: str,
    max_bytes: int,
    backup_count: int,
    formatter: Type[logging.Formatter],
    formatter_kwargs: Optional[Dict[str, Any]] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
) -> None:
    """Add a file handler to a Logger so it logs to a file.

    Creates the log file directory if it doesn't exist.
    """
    if formatter_kwargs is None:
        formatter_kwargs = {}

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    log_handler = logging.handlers.RotatingFileHandler(
        filename,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    log_handler.setFormatter(formatter(fmt=log_format, **formatter_kwargs))
    log_handler.setLevel(log_level)
    logger_instance.addHandler(log_handler)


def init_logger(
    log_level: Union[str, int],
    file_log_level: Optional[Union[str, int]],
    filename: Optional[str],
    logger_instance: Union[logging.Logger, str] = "",
    max_bytes: int = DEFAULT_LOGFILE_MAX_BYTES,
    backup_count: int = DEFAULT_LOGFILE_BACKUP_COUNT,
    stream: TextIO = sys.stdout,
    formatter: Type[logging.Formatter] = JsonFormatter,
    formatter_kwargs: Optional[Dict[str, Any]] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
) -> None:
    """Configure a logger to log to both the given stream and filename with the given formatter.

    logger_instance - Configure this Logger object.
        If a string, configure logging.getLogger(logger_instance)
    """
    if isinstance(logger_instance, str):
        logger_instance = logging.getLogger(logger_instance)

    # We need the minimum log level of the two so that we don't accidentally
    # set a logger to log at a higher level than is expected by either the
    # stdout or file handlers.
    min_level = min_log_level(log_level, file_log_level)

    logger_instance.setLevel(min_level)

    add_stream_handler(
        logger_instance,
        log_level,
        formatter,
        formatter_kwargs,
        log_format,
        stream=stream,
    )
    if not (file_log_level is None or filename is None):
        add_file_handler(
            logger_instance,
            file_log_level,
            filename,
            max_bytes,
            backup_count,
            formatter,
            formatter_kwargs,
            log_format,
        )


def init_loggers(
    loggers: Collection[Union[logging.Logger, str]],
    log_level: Union[str, int],
    file_log_level: Optional[Union[str, int]],
    filename: Optional[str],
    max_bytes: int = DEFAULT_LOGFILE_MAX_BYTES,
    backup_count: int = DEFAULT_LOGFILE_BACKUP_COUNT,
    stream: TextIO = sys.stdout,
    formatter: Type[logging.Formatter] = JsonFormatter,
    formatter_kwargs: Optional[Dict[str, Any]] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    info_logger: Optional[Union[logging.Logger, str]] = None,
) -> None:
    """Configure loggers to log to both the given stream and filename with the given formatter.

    loggers - Configure these Logger objects.
        If a string is passed instead of a Logger, configure logging.getLogger(logger_instance)

    info_logger - If not None, use it to log the logging configuration after setting up loggers.
        If a string is passed instead of a Logger, use logging.getLogger(info_logger)
    """
    for logger_instance in loggers:
        init_logger(
            log_level,
            file_log_level,
            filename,
            logger_instance,
            max_bytes,
            backup_count,
            stream,
            formatter,
            formatter_kwargs,
            log_format,
        )

    if info_logger is None:
        return

    if isinstance(info_logger, str):
        info_logger = logging.getLogger(info_logger)

    info_logger.info("Logging at level %s", log_level)
    if file_log_level is None or filename is None:
        info_logger.info("Not logging to a file")
    else:
        info_logger.info(
            "Logging at level %s to file %s",
            file_log_level,
            filename,
            extra={
                "config": dict(
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                )
            },
        )
