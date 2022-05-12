from typing import Any, Dict, Optional

# Wait for an update or write type stubs
from pythonjsonlogger import jsonlogger  # type: ignore

from powerflex_logging_utilities.default_log_format import DEFAULT_LOG_FORMAT


class JsonFormatter(jsonlogger.JsonFormatter):  # type: ignore
    """A custom JSON formatter.

    - Replaces the "levelname" field with "severity".
    - Replaces non-string keys in the log record with their __str__ representation
    """

    def __init__(self, fmt: Optional[str] = DEFAULT_LOG_FORMAT, **kwargs: Any):
        super().__init__(fmt=fmt, **kwargs)

    def process_log_record(self, log_record: Dict[str, Any]) -> Any:
        log_record["severity"] = log_record["levelname"]
        del log_record["levelname"]

        for key in log_record.copy():
            if not isinstance(key, str):
                log_record[str(key)] = log_record[key]
                del log_record[key]

        return super().process_log_record(log_record)
