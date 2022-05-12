import logging
from typing import Any, Callable


def forbid_logging_with_logging_toplevel() -> None:
    """Forbid the use of logging using the top-level logging functions in the \
    logging module, such as logging.info and logging.critical.

    This should help you only use the non-root logger.

    When using a JSON logger, using logging functions from the logging module
    top-level could cause non-JSON formatted logs to appear alongside JSON
    logs. This is because the logging module configures itself when used like
    this for the first time.
    """

    def make_forbidden_log_function(name: str) -> Callable[[Any], None]:
        def forbidden_log_function(*_args: Any, **_kwargs: Any) -> None:
            raise RuntimeError(
                f"Do not use logging.{name}, use a named logger such as traffic_manager.log.logger instead"
            )

        return forbidden_log_function

    log_functions = [
        "info",
        "debug",
        "error",
        "warning",
        "warn",
        "critical",
        "log",
    ]
    for log_function in log_functions:
        setattr(logging, log_function, make_forbidden_log_function(log_function))
