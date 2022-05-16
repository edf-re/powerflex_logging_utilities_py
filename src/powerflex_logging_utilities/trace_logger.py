"""This module defines a Logger with a .trace method for logging at the TRACE level.

Import this module to enable trace logging.
"""
import logging
from typing import Mapping, Union

TRACE = 5

logging.addLevelName(TRACE, "TRACE")


class TraceLogger(logging.Logger):
    """A logging.Logger subclass that can log at the trace severity level."""

    def trace(
        self,
        msg: object,
        *args: object,
        exc_info: bool = False,
        stack_info: bool = False,
        stacklevel: int = 0,
        extra: Union[Mapping[str, object], None] = None,
    ) -> None:
        """Log at the trace severity level.

        Usage is the same as other logging methods, such as Logger.info.
        """
        self.log(
            TRACE,
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )
