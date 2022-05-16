import sys
import traceback
from typing import Optional


def format_exception(exception: Optional[BaseException] = None) -> str:
    if exception is None:
        _, exception, _ = sys.exc_info()
    if exception is None:
        return "No exception"
    return "".join(traceback.format_exception_only(type(exception), exception))
