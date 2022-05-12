import os.path

from .default_log_format import DEFAULT_LOG_FORMAT
from .json_formatter import JsonFormatter
from .trace_logger import TRACE, TraceLogger

with open(os.path.normpath(os.path.join(__file__, "../", "VERSION"))) as versionfile:
    __version__ = versionfile.read().strip()
