# powerflex-logging-utilities

![PyPI - Version](https://img.shields.io/pypi/v/powerflex-logging-utilities)
![PyPI - License](https://img.shields.io/pypi/l/powerflex-logging-utilities)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/powerflex-logging-utilities)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/powerflex-logging-utilities)

Helpful code for logging in Python by PowerFlex.

| Module | Description |
|-----------------|--------------------------------------------|
| forbid_toplevel_logging |  Disable logging with the top-level root logging functions such as `logging.info`.
| log_slow_callbacks | Either warn or info log when an async callback runs for too long.
| init_loggers |  A function for easily setting up logging to a file and to stdout.

| Class | Description |
|-----------------|--------------------------------------------|
| JsonFormatter |  A JSON log formatter to enable structured logging. It depends on the `python-json-logger` package.
| TraceLogger | A Python Logger subclass that adds a TRACE logging level
| AsyncNatsLogLevelListener | A NATS interface for changing the program's log level by sending a NATS request

# Sample usage

## Initializing Loggers

Setup JSON logging to stdout and to a file:

```python
import logging
from typing import Optional

from powerflex_logging_utilities import (
    JsonFormatter,
    TraceLogger,
    init_loggers,
)

LOG_LEVEL: str = "DEBUG"
FILE_LOG_LEVEL: Optional[str] = "TRACE"
LOG_FILE: Optional[str] = "./logs/trace.log"

MAX_LOG_FILE_MB = 10
MAX_TOTAL_LOG_FILE_MB = 10000

logger = TraceLogger("main")
third_party_loggers = ["asyncio", "backoff", "py.warnings"]
loggers = (logger, *[logging.getLogger(name) for name in third_party_loggers])

logging.captureWarnings(True)

init_loggers.init_loggers(
    loggers,
    log_level=LOG_LEVEL,
    file_level=FILE_LOG_LEVEL,
    filename=LOG_FILE,
    max_bytes=1000 * 1000 * MAX_LOG_FILE_MB,
    backup_count=MAX_TOTAL_LOG_FILE_MB // MAX_LOG_FILE_MB,
    formatter=JsonFormatter,
    info_logger=logger,
)
```

To use: `logger.info("hello")`.

## Using several other utilities

```python
import logging
from powerflex_logging_utilities import (
    forbid_toplevel_logging,
    log_slow_callbacks,
)

logger = logging.getLogger(__name__)

# Log slow async callbacks with two log levels
log_slow_callbacks.log_slow_callbacks(logger)

# Forbid functions such as logging.info since they implicitly use the root logger
forbid_toplevel_logging.forbid_logging_with_logging_toplevel()
```

## Using the JSON formatter

```python
import logging
import sys
from powerflex_logging_utilities import JsonFormatter

log_handler = logging.StreamHandler(stream=sys.stdout)
log_handler.setLevel("DEBUG")
log_handler.setFormatter(JsonFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(log_handler)
logger.setLevel("DEBUG")

logger.info("hello world", extra={
    "data": ["log structured data", ":D"],
    1: "handles non string key",
})
```

```skip_phmdoctest
{
  "message": "hello world",
  "name": "__main__",
  "module": "<ipython-input-10-b016ce80d46f>",
  "lineno": 1,
  "funcName": "<cell line: 1>",
  "filename": "<ipython-input-10-b016ce80d46f>",
  "asctime": "2022-05-12 01:04:16,824",
  "data": [
    "log structured data",
    ":D"
  ],
  "severity": "INFO",
  "1": "handles non string key"
}
```

# Using pipenv

1. Run `make setup-with-pipenv` to install all dependencies.
   Make sure you have the version of Python specified in `.tool-versions` or simply change this file to your Python version (must be 3.8+).
2. Run `pipenv shell` or run the following `make` commands with `pipenv run make ...`.
   You could also alias `pmake` to `pipenv run make` for convenience.

# Tests

There is 100% code coverage.

```
make test-unit
```

To test in several versions of Python, run:

```
tox
```

## Testing the code in this README

```
make test-readme
```

# Checking code quality

The Github Actions will run all of the following checks on the code.

## Code formatting

```
make format-fix
```

## Linting

```
make lint
```

## Type checking

```
make type-check-strict
```


# Releasing to pypi


1. Make sure you have committed all code you wish to release.
1. Make sure all code checks have passed.
1. Set the version in [`./src/powerflex_logging_utilities/VERSION`](./src/powerflex_logging_utilities/VERSION)
   Please attempt to follow semantic versioning.
1. Run `make bump-version`
1. Run `make release`
