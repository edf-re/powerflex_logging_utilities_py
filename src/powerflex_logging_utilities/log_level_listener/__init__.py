import json
from asyncio import ensure_future, sleep
from logging import Handler, Logger
from typing import Literal, Union

from pydantic import BaseModel, BaseSettings, Field

DEFAULT_DURATION_SECONDS = 60


class LogLevelListenerConfig(BaseSettings):
    """Pydantic settings object to configure a log level listener."""

    FALLBACK_LOG_LEVEL: str = Field(
        description="Log level to reset to after the duration specified in the LogLevelRequestMessage",
        default="INFO",
    )


class LogLevelRequestMessage(BaseModel):
    """Message representing a request to temporarily change the log level."""

    level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = Field(
        description="a valid Python logging level (CRITICAL, ERROR, WARNING, INFO, DEBUG)"
    )
    duration: float = Field(
        description="length of time in seconds before the log level is reset; "
        "setting this value to 0 or a negative integer will cause the log level to not be reset",
        default=DEFAULT_DURATION_SECONDS,
        ge=0,
    )


class BaseAsyncLogLevelListener:
    """
    Log level listener that changes the log level of the logging handler with name="stdout".

    Changes the log level of the stdout logging handler (or the logger itself if no stdout logging
    handler is found) for a specified duration. These parameters are provided via a LogLevelRequestMessage.
    """

    logger: Logger
    config: LogLevelListenerConfig

    def __init__(self, logger: Logger, config: LogLevelListenerConfig):
        self.logger = logger
        self.config = config

    def _get_stdout_handler_or_logger(self) -> Union[Handler, Logger]:
        for handler in self.logger.handlers:
            if handler.get_name() == "stdout":
                return handler
        return self.logger

    async def reset_log_level(
        self,
        handler_or_logger: Union[Handler, Logger],
        level: Union[str, int],
        delay: float,
    ) -> None:
        """Reset the log level after a certain delay."""
        await sleep(delay)
        self.logger.info(f"Resetting log level to {level}")
        handler_or_logger.setLevel(level)

    def set_log_level(
        self, level: str, duration: float = DEFAULT_DURATION_SECONDS
    ) -> None:
        """Set the log level and starts and async task to reset it later."""
        self.logger.info(f"Setting log level to {level}")
        handler_or_logger = self._get_stdout_handler_or_logger()
        handler_or_logger.setLevel(level)

        if duration > 0:
            self.logger.info(f"Log level will be reset in {duration} seconds")
            ensure_future(
                self.reset_log_level(
                    handler_or_logger, self.config.FALLBACK_LOG_LEVEL, duration
                )
            )
        else:
            self.logger.warning("Log level will not be automatically reset")

    async def handle_log_level_change_message(
        self, json_message: Union[str, bytes]
    ) -> LogLevelRequestMessage:
        body = json.loads(json_message)
        request = LogLevelRequestMessage(**body)
        self.set_log_level(level=request.level, duration=request.duration)
        return request
