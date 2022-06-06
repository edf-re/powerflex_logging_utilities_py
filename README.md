# powerflex-logging-utilities

<!-- Badges (images) related to Python package information -->
[![PyPI - Version](https://img.shields.io/pypi/v/powerflex-logging-utilities) ![PyPI - License](https://img.shields.io/pypi/l/powerflex-logging-utilities) ![PyPI - Implementation](https://img.shields.io/pypi/implementation/powerflex-logging-utilities) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/powerflex-logging-utilities)](https://pypi.org/project/powerflex-logging-utilities/)

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

# Installation

You can install from [PyPi](https://pypi.org/project/powerflex-logging-utilities/) directly:
```shellscript
pip install powerflex-logging-utilities
```

# Sample usage

## Initializing Loggers

Setup **all Loggers** to output JSON to stdout and to a file:
 
```python
import logging
import sys

from powerflex_logging_utilities import (
    JsonFormatter,
    init_loggers,
)

LOG_LEVEL = "DEBUG"
FILE_LOG_LEVEL = "TRACE"
LOG_FILE = "./logs/trace.log"

MAX_LOG_FILE_MB = 10
MAX_TOTAL_LOG_FILE_MB = 10000

root_logger = logging.getLogger()

# Log warnings with the py.warnings logger
logging.captureWarnings(True)

# Fix iPython autocomplete
logging.getLogger("parso").propagate=False

init_loggers.init_loggers(
    [root_logger],
    log_level=LOG_LEVEL,
    file_log_level=FILE_LOG_LEVEL,
    filename=LOG_FILE,
    max_bytes=1000 * 1000 * MAX_LOG_FILE_MB,
    backup_count=MAX_TOTAL_LOG_FILE_MB // MAX_LOG_FILE_MB,
    stream=sys.stdout,
    formatter=JsonFormatter,
    info_logger=root_logger,
)

logger = logging.getLogger(__name__)
```

This uses Python's logger propagation feature.
We only need to configure the root Logger in order to make sure all other Loggers output in the desired format.

You can pass `formatter_kwargs` to enable logging with a different JSON serializer.

To use:

```skip_phmdoctest
logger = logging.getLogger(__name__)
logger.info("hello world")
```

### Explicitly listing loggers

You can also list the loggers you'd like to configure instead of configuring
the root logger.

This could be useful if you configure your package's main logger
`logging.getLogger("package")`. You can then use Python's logger propagation by calling
`logging.getLogger("package.submodule.a.b.c")` to get Logger instances for all
other submodules.

```python
import logging

from powerflex_logging_utilities import (
    JsonFormatter,
    init_loggers,
)

logger = logging.getLogger("your_package_name")

# Log warnings with the py.warnings logger
logging.captureWarnings(True)

init_loggers.init_loggers(
    [logger, "asyncio", "py.warnings"],
    log_level="DEBUG",
    file_log_level="TRACE",
    filename="./logs/trace-no-root.log",
    formatter=JsonFormatter,
    info_logger=logger,
)
```

**NOTICE**: if you use this method, any loggers you do not explicitly list will have non-JSON output.

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

To download several versions of Python, use `pyenv` or `asdf` 

To use `pyenv`, install it [here](https://github.com/pyenv/pyenv#installation) and run the following script:

```
./install_python_versions_pyenv.sh
```

To use `asdf`, install the core parts [here](http://asdf-vm.com/guide/getting-started.html) and run the following commands:

```
./install_python_versions_asdf.sh
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
