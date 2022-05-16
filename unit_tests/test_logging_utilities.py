import asyncio
import itertools
import json
import logging
import os
import sys
import time
import unittest
from io import StringIO
from typing import List, Optional, Union
from unittest.mock import Mock

from powerflex_logging_utilities import (
    DEFAULT_LOG_FORMAT,
    TRACE,
    JsonFormatter,
    TraceLogger,
    forbid_toplevel_logging,
    init_loggers,
    log_slow_callbacks,
)

DEFAULT_LOG_METHODS = [
    "debug",
    "info",
    "error",
    "critical",
]

TEST_DELAY = float(os.environ.get("TEST_DELAY", 0.05))


def add_stdout_handler(logger, stream, handler_level: Union[str, int] = "DEBUG"):
    log_handler = logging.StreamHandler(stream=stream)
    log_handler.set_name("stdout")
    log_handler.setLevel(handler_level)
    logger.addHandler(log_handler)


class Test(unittest.TestCase):
    @staticmethod
    def reset_root_logger():
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    def setUp(self):
        self.reset_root_logger()

    # pylint: disable=no-self-use
    def test_json_formatter(self):
        log_handler = logging.StreamHandler(stream=sys.stdout)
        log_handler.setLevel("DEBUG")
        log_handler.setFormatter(JsonFormatter(fmt=DEFAULT_LOG_FORMAT))
        logger = logging.getLogger("test-json-formatter")
        logger.addHandler(log_handler)
        logger.setLevel("DEBUG")

        logger.debug("test", extra={"test": True}, stack_info=True, exc_info=True)

        logger.debug(
            "test",
            extra={1: "not a str key"},  # type:ignore
            stack_info=True,
            exc_info=True,
        )

    def test_async_log_slow_callbacks(self):
        # This won't work in a subclass of unittest.IsolatedAsyncioTestCase
        # Must use asyncio.run manually
        # The aiodebug module does not account for this use case
        logger = Mock()
        logger.log = Mock()  # helps with type checking
        very_slow_async_task_threshold_sec = TEST_DELAY
        log_slow_callbacks.log_slow_callbacks(
            logger,
            slow_async_task_threshold_sec=very_slow_async_task_threshold_sec / 2,
            very_slow_async_task_threshold_sec=very_slow_async_task_threshold_sec,
        )

        async def slow_callback():
            time.sleep(1.1 * very_slow_async_task_threshold_sec)

        asyncio.run(slow_callback())

        logger.log.assert_called_once()
        first_arg = logger.log.call_args_list[0].args[0]
        self.assertEqual(first_arg, logging.WARN)

    def _test_logger_output(
        self,
        logger: Union[logging.Logger, str],
        fake_stdout: StringIO,
        is_json: bool,
        log_methods: List[str],
    ):
        for i, log_method_name in enumerate(log_methods):
            with self.subTest(logger=logger, log_method=log_method_name):
                if isinstance(logger, str):
                    logger = logging.getLogger(logger)
                message = (
                    f"test message {i} logger={logger.name} method={log_method_name}"
                )
                extra_field, extra_value = "test field", True
                log_method = getattr(logger, log_method_name)

                log_method(message, extra={extra_field: extra_value})
                all_output = fake_stdout.getvalue()
                last_line = all_output.split("\n")[-2]

                self.assertEqual(all_output.count(message), 1)
                if is_json:
                    try:
                        output = json.loads(last_line)
                    except json.JSONDecodeError:
                        self.fail(f"Unable to decode as JSON: {last_line}")

                    self.assertEqual(output.get("message"), message)
                    self.assertEqual(output.get("severity"), log_method_name.upper())
                    self.assertEqual(output.get(extra_field), extra_value)
                    self.assertEqual(output.get("name"), logger.name)
                else:
                    self.assertIn(message, last_line)

    def _test_init_loggers_with_json(
        self,
        fake_stdout: StringIO,
        log_level: str,
        filename: Optional[str],
        use_info_logger: bool,
        loggers: List[Union[logging.Logger, str]],
    ):
        logging.captureWarnings(True)
        init_loggers.init_loggers(
            loggers=loggers,
            log_level=log_level,
            file_log_level=log_level,
            filename=filename,
            formatter=JsonFormatter,
            stream=fake_stdout,
            info_logger=loggers[0] if use_info_logger else None,
        )

        self.assertEqual(
            fake_stdout.getvalue().count(f"Logging at level {log_level}"),
            (2 if filename is not None else 1) if use_info_logger else 0,
        )

        for logger_instance in loggers:
            self._test_logger_output(
                logger_instance,
                fake_stdout=fake_stdout,
                is_json=True,
                log_methods=DEFAULT_LOG_METHODS,
            )

    def test_init_loggers_with_json(self):
        # Configure an explicit list of loggers
        log_level = "DEBUG"
        filenames = ["./logs/unit-test-debug.log", None]
        explicit_loggers_list = [
            logging.getLogger("test_logger"),
            "asyncio",
            "py.warnings",
        ]

        for filename, use_info_logger, use_root_logger in itertools.product(
            filenames, [True, False], [True, False]
        ):
            with self.subTest(use_info_logger=use_info_logger, filename=filename):
                fake_stdout = StringIO()
                self.reset_root_logger()
                self._test_init_loggers_with_json(
                    fake_stdout=fake_stdout,
                    log_level=log_level,
                    filename=filename,
                    use_info_logger=True,
                    loggers=[logging.getLogger()]
                    if use_root_logger
                    else explicit_loggers_list,
                )

                sublogger = logging.getLogger(
                    explicit_loggers_list[0].name + ".sublogger"
                )
                self._test_logger_output(
                    sublogger,
                    fake_stdout,
                    is_json=True,
                    log_methods=DEFAULT_LOG_METHODS,
                )

    def test_trace_logger(self):
        logger = TraceLogger("test")
        logger.setLevel(TRACE)
        fake_stdout = StringIO()
        add_stdout_handler(logger, fake_stdout, TRACE)

        self._test_logger_output(
            logger,
            fake_stdout=fake_stdout,
            is_json=False,
            log_methods=DEFAULT_LOG_METHODS + ["trace"],
        )

    def test_forbid_toplevel_logging(self):
        with self.subTest(
            test="does not raise exception when calling logging.info before forbidding it."
        ):
            logging.info("test")

        forbid_toplevel_logging.forbid_logging_with_logging_toplevel()

        with self.assertRaisesRegex(RuntimeError, "Do not use"):
            logging.info("test")
