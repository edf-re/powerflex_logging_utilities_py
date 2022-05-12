# powerflex_logging_utilities_py

Helpful code for logging in Python

# Sample usage

See [`sample.py`](./sample.py) for how to use this package.

# Using `pipenv`

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

