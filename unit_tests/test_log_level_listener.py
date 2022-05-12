import asyncio
import json
import logging
import os
import sys
import unittest
from unittest.mock import AsyncMock
from nats.aio.msg import Msg
from pydantic import ValidationError

from powerflex_logging_utilities.log_level_listener.format_exception import (
    format_exception,
)
from powerflex_logging_utilities.log_level_listener import LogLevelRequestMessage
from powerflex_logging_utilities.log_level_listener.nats import (
    AsyncNatsLogLevelListener,
    NatsLogLevelListenerConfig,
)


TEST_DELAY = float(os.environ.get("TEST_DELAY", 0.1))

test_config = NatsLogLevelListenerConfig(NATS_LOG_LEVEL_LISTENER_SUBJECT="test-subject")


def make_nats_msg(subject: str, data: bytes, reply: str = "") -> Msg:
    return Msg(
        subject=subject,
        data=data,
        reply=reply,
        _client=None,  # type:ignore
    )


class Test(unittest.IsolatedAsyncioTestCase):
    def test_message(self):
        with self.subTest(test="valid input"):
            LogLevelRequestMessage(level="CRITICAL", duration=1)
            LogLevelRequestMessage(level="INFO", duration=0.5)

        test_bad_messages = [
            dict(level="critical", duration=1),
            dict(level="CRITICAL", duration=-1),
            dict(level="unknown", duration=1),
        ]

        for test_message in test_bad_messages:
            with self.subTest(test="invalid input"):
                with self.assertRaises(ValidationError):
                    LogLevelRequestMessage.parse_obj(test_message)

    def test_format_exception(self):
        test_msg = "test message"
        test_exception = RuntimeError(test_msg)

        result = format_exception(test_exception)

        self.assertIn(type(test_exception).__name__, result)
        self.assertIn(test_msg, result)

        result = format_exception(None)

        self.assertIsInstance(result, str)

    async def test_nats_log_level_listener(self):
        initial_level = "INFO"
        logger = logging.getLogger("test")
        log_handler = logging.StreamHandler(stream=sys.stdout)
        log_handler.set_name("stdout")
        log_handler.setLevel(initial_level)
        logger.addHandler(log_handler)

        mock_nats = AsyncMock()
        mock_nats.subscribe = AsyncMock()

        listener = await AsyncNatsLogLevelListener.create(
            nats_client=mock_nats, logger=logger, config=test_config
        )

        with self.subTest(
            test="handle_log_level_change_nats_message sets the log level for the stdout handler (with reset)"
        ):
            msg = make_nats_msg(
                subject="test",
                data=json.dumps({"level": "DEBUG", "duration": TEST_DELAY}).encode(),
            )
            self.assertEqual(listener.logger.handlers[0].level, logging.INFO)
            await listener.handle_log_level_change_nats_message(msg)
            self.assertEqual(listener.logger.handlers[0].level, logging.DEBUG)
            await asyncio.sleep(TEST_DELAY * 1.2)
            self.assertEqual(listener.logger.handlers[0].level, logging.INFO)

        with self.subTest(
            test="handle_log_level_change_nats_message sets the log level for the stdout handler (without reset)"
        ):
            msg = make_nats_msg(
                subject="test",
                data=json.dumps({"level": "DEBUG", "duration": 0}).encode(),
            )
            self.assertEqual(listener.logger.handlers[0].level, logging.INFO)
            await listener.handle_log_level_change_nats_message(msg)
            self.assertEqual(listener.logger.handlers[0].level, logging.DEBUG)
            await listener.reset_log_level(logger.handlers[0], logging.INFO, 0)

        with self.subTest(
            test="handle_log_level_change_nats_message sets the log level for the stdout handler (with reply)"
        ):
            mock_nats.publish = AsyncMock()

            msg = make_nats_msg(
                subject="test",
                reply="reply",
                data=json.dumps({"level": "DEBUG", "duration": TEST_DELAY}).encode(),
            )
            self.assertEqual(listener.logger.handlers[0].level, logging.INFO)
            await listener.handle_log_level_change_nats_message(msg)
            self.assertEqual(listener.logger.handlers[0].level, logging.DEBUG)
            mock_nats.publish.assert_called_once()

        with self.subTest(
            test="handle_log_level_change_nats_message replies with an error if the request is missing a required field"
        ):
            mock_nats.publish = AsyncMock()

            msg = make_nats_msg(
                subject="test",
                reply="reply",
                data=json.dumps(
                    {"bad_field_name": "DEBUG", "duration": TEST_DELAY}
                ).encode(),
            )
            await listener.handle_log_level_change_nats_message(msg)
            mock_nats.publish.assert_called_once()
            self.assertIn(b"validation error", mock_nats.publish.mock_calls[0].args[1])

        with self.subTest(
            test="handle_log_level_change_nats_message replies with an error if the request contains bad JSON"
        ):
            mock_nats.publish = AsyncMock()

            msg = make_nats_msg(
                subject="test",
                reply="reply",
                data="hello".encode(),
            )
            await listener.handle_log_level_change_nats_message(msg)
            mock_nats.publish.assert_called_once()
            self.assertIn(
                b"Error when parsing JSON", mock_nats.publish.mock_calls[0].args[1]
            )

    async def test_log_level_listener_no_stdout_handler(self):
        initial_level = "INFO"
        logger = logging.getLogger("no_stdout")
        logger.setLevel(initial_level)

        mock_nats = AsyncMock()
        mock_nats.subscribe = AsyncMock()

        listener = await AsyncNatsLogLevelListener.create(
            nats_client=mock_nats, logger=logger, config=test_config
        )

        with self.subTest(
            test="handle_log_level_change_nats_message sets the log level for its logger if no stdout handler exists"
        ):
            msg = make_nats_msg(
                subject="test",
                data=json.dumps({"level": "DEBUG", "duration": TEST_DELAY}).encode(),
            )
            self.assertEqual(listener.logger.level, logging.INFO)
            await listener.handle_log_level_change_nats_message(msg)
            self.assertEqual(listener.logger.level, logging.DEBUG)
            await asyncio.sleep(TEST_DELAY * 1.2)
            self.assertEqual(listener.logger.level, logging.INFO)
