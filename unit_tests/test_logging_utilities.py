import asyncio
import logging
import sys
import time
import unittest
from unittest.mock import Mock

from powerflex_logging_utilities import (
    JsonFormatter,
    TraceLogger,
    TRACE,
    log_slow_callbacks,
    forbid_toplevel_logging,
    init_loggers,
    DEFAULT_LOG_FORMAT,
)

log_methods = [
    "debug",
    "info",
    "error",
    "critical",
]


def add_stdout_handler():
    log_handler = logging.StreamHandler(stream=sys.stdout)
    log_handler.set_name("stdout")
    log_handler.setLevel("DEBUG")
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)


class Test(unittest.TestCase):
    def setUp(self):
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    def test_json_formatter(self):
        log_handler = logging.StreamHandler(stream=sys.stdout)
        log_handler.setLevel("DEBUG")
        log_handler.setFormatter(JsonFormatter(fmt=DEFAULT_LOG_FORMAT))
        logger = logging.getLogger("test-json-formatter")
        logger.addHandler(log_handler)
        logger.setLevel("DEBUG")

        logger.debug("test", extra={"test": True}, stack_info=True, exc_info=True)

        logger.debug(
            "test", extra={"override_lineno": 999}, stack_info=True, exc_info=True
        )
        logger.debug(
            "test",
            extra={1: "not a str key"},  # type:ignore
            stack_info=True,
            exc_info=True,
        )

    def test_log_slow_callbacks(self):
        # This won't work in a subclass of unittest.IsolatedAsyncioTestCase
        # Must use asyncio.run manually
        logger = Mock()
        logger.log = Mock()  # helps with type checking
        very_slow_async_task_threshold_sec = 0.1
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

    def test_init_loggers(self):
        add_stdout_handler()

        logger = logging.getLogger("test-init-loggers")
        third_party_loggers = ["asyncio", "py.warnings"]
        loggers = (logger, *[logging.getLogger(name) for name in third_party_loggers])

        logging.captureWarnings(True)
        init_loggers.init_loggers(
            loggers,
            log_level="DEBUG",
            file_level="DEBUG",
            filename="./logs/unit-test-debug.log",
            max_bytes=2000,
            backup_count=10,
            formatter=logging.Formatter,
            info_logger=logger,
        )

        for log_level in log_methods:
            with self.subTest(log_level=log_level):
                log_method = getattr(logger, log_level)
                log_method("test", extra={"test": True})

    def test_trace_logger(self):
        add_stdout_handler()
        logger = TraceLogger("test")
        logger.setLevel(TRACE)

        for log_level in ["trace"] + log_methods:
            with self.subTest(log_level=log_level):
                log_method = getattr(logger, log_level)
                log_method("test", extra={"test": True})

    def test_forbid_toplevel_logging(self):
        with self.subTest(
            test="does not raise exception when calling logging.info before forbidding it."
        ):
            logging.info("test")

        forbid_toplevel_logging.forbid_logging_with_logging_toplevel()

        with self.assertRaisesRegex(RuntimeError, "Do not use"):
            logging.info("test")
