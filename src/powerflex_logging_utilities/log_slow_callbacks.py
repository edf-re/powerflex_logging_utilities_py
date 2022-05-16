from logging import INFO, WARN, Logger

# For some reason, mypy doesn't detect this package's type hints
import aiodebug.log_slow_callbacks  # type: ignore


def log_slow_callbacks(
    logger: Logger,
    slow_async_task_threshold_sec: float = 0.15,
    very_slow_async_task_threshold_sec: float = 0.5,
) -> None:
    """Log at INFO or WARN severity levels when an async task runs too slowly.

    slow_async_task_threshold_sec - INFO log if an async task runs longer than
        this many seconds. Python's default is 0.1sec, but our default is
        higher.

    very_slow_async_task_threshold_sec - WARN log if an async task runs longer
        than this many seconds.
    """

    def on_slow_callback(task_name: str, duration: float) -> None:
        level = INFO
        if duration > very_slow_async_task_threshold_sec:
            level = WARN
        logger.log(
            level,
            "Executing task %s blocked async loop for %s seconds",
            task_name,
            duration,
            extra={"task_name": task_name, "duration": duration},
        )

    aiodebug.log_slow_callbacks.enable(
        slow_async_task_threshold_sec, on_slow_callback=on_slow_callback
    )
