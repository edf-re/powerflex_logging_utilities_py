import logging
from typing import Optional

from powerflex_logging_utilities import (
    JsonFormatter,
    TraceLogger,
    forbid_toplevel_logging,
    init_loggers,
    log_slow_callbacks,
)

LOG_LEVEL: str = "DEBUG"
FILE_LOG_LEVEL: Optional[str] = "TRACE"
LOG_FILE: Optional[str] = "./logs/trace.log"


MAX_LOG_FILE_MB = 10
MAX_TOTAL_LOG_FILE_MB = 10000

MAX_LOG_FILE_BACKUP_COUNT = MAX_TOTAL_LOG_FILE_MB // MAX_LOG_FILE_MB
MAX_LOG_FILE_BYTES = 1000 * 1000 * MAX_LOG_FILE_MB

logger = TraceLogger("main")
# Configure all of these loggers
third_party_loggers = ["asyncio", "backoff", "py.warnings", "pymodbus OPTIONAL"]
loggers = (logger, *[logging.getLogger(name) for name in third_party_loggers])

logging.captureWarnings(True)

init_loggers.init_loggers(
    loggers,
    log_level=LOG_LEVEL,
    file_level=FILE_LOG_LEVEL,
    filename=LOG_FILE,
    max_bytes=MAX_LOG_FILE_BYTES,
    backup_count=MAX_LOG_FILE_BACKUP_COUNT,
    formatter=JsonFormatter,
    info_logger=logger,
)

# Log slow async callbacks
log_slow_callbacks.log_slow_callbacks(logger)

# Forbid functions such as logging.info since they implicitly use the root logger
forbid_toplevel_logging.forbid_logging_with_logging_toplevel()
