import json
from json import JSONDecodeError
from logging import Logger
from typing import Optional

from nats.aio.client import Client as NATSClient
from nats.aio.msg import Msg
from pydantic import Field, ValidationError

from powerflex_logging_utilities.log_level_listener import (
    BaseAsyncLogLevelListener,
    LogLevelListenerConfig,
)
from powerflex_logging_utilities.log_level_listener.format_exception import (
    format_exception,
)


class NatsLogLevelListenerConfig(LogLevelListenerConfig):
    """Pydantic settings object to configure a NATS log level listener."""

    NATS_LOG_LEVEL_LISTENER_SUBJECT: str = Field(
        description="NATS subject that will receive LogLevelRequestMessage messages"
    )


class AsyncNatsLogLevelListener(BaseAsyncLogLevelListener):
    """
    NATS listener that changes the log level of the logging handler with name="stdout".

    Changes the log level of the stdout logging handler (or the logger itself if no stdout logging
    handler is found) for a specified duration. These parameters are provided via a LogLevelRequestMessage.
    """

    nats_client: NATSClient
    logger: Logger
    config: NatsLogLevelListenerConfig

    def __init__(
        self,
        nats_client: NATSClient,
        logger: Logger,
        config: NatsLogLevelListenerConfig,
    ):
        self.nats_client = nats_client
        super().__init__(logger, config)

    async def async_init(self) -> None:
        self.logger.info(
            "Log Level Listener subscribing to subject %s",
            self.config.NATS_LOG_LEVEL_LISTENER_SUBJECT,
        )
        await self.nats_client.subscribe(
            subject=self.config.NATS_LOG_LEVEL_LISTENER_SUBJECT,
            cb=self.handle_log_level_change_nats_message,
        )

    @staticmethod
    async def create(
        nats_client: NATSClient,
        logger: Logger,
        config: Optional[NatsLogLevelListenerConfig] = None,
    ) -> "AsyncNatsLogLevelListener":
        if config is None:
            config = NatsLogLevelListenerConfig(
                # type: ignore
            )
        log_level_listener = AsyncNatsLogLevelListener(
            nats_client=nats_client, logger=logger, config=config
        )
        logger.info(
            f"Log Level Listener initialized with config {config}", extra=config.dict()
        )
        await log_level_listener.async_init()
        return log_level_listener

    async def handle_log_level_change_nats_message(self, msg: Msg) -> None:
        try:
            request = await self.handle_log_level_change_message(msg.data)
            if msg.reply:
                response = {"result": f"Log level set to {request.level}"}
                await self.nats_client.publish(msg.reply, json.dumps(response).encode())
        except ValidationError as ex:
            if msg.reply:
                response = {"error": format_exception(ex)}
                await self.nats_client.publish(msg.reply, json.dumps(response).encode())
        except JSONDecodeError as ex:
            if msg.reply:
                response = {"error": "Error when parsing JSON\n" + format_exception(ex)}
                await self.nats_client.publish(msg.reply, json.dumps(response).encode())
