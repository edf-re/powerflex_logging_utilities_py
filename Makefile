SHELL=bash -o pipefail # Just in case
PYFILES=$(shell find unit_tests src -iname \*.py ; echo *.py)
STRICT_TYPED_FILES=$(shell find src -iname \*.py)
VERSION=src/powerflex_logging_utilities/VERSION

all: commitready

commitready: format-fix lint type-check-strict test-readme test-unit

setup-with-pipenv:
	python -m pip install --upgrade pip
	pip install pipenv
	# Avoid stale dependencies by removing the existing Pipfile
	rm -f Pipfile
	# Avoid using the Pipfile from a higher level directory
	touch Pipfile
	pipenv install --skip-lock \
		-e .[nats-and-pydantic] \
		-r requirements_dev.txt \
		--python $(shell grep python .tool-versions | cut -d' ' -f2)

setup-cicd:
	python -m pip install --upgrade pip
	pip install -e .[nats-and-pydantic] -r requirements_dev.txt

bump-version:
	git commit -m 'Bump version to $(shell cat $(VERSION))' $(VERSION)

release:
	git log -1 | grep 'Bump version' || \
		(echo Please make sure the last commit is only changing the VERSION file ; exit 1)
	python -m pip install --upgrade pip
	rm -rf dist
	python -m build
	twine upload dist/*
	git tag -a v$(shell cat $(VERSION)) -m "v$(shell cat $(VERSION)) (released to pypi)"

test-readme:
	phmdoctest README.md --outfile _generated_test_readme.py
	pytest _generated_test_readme.py

test-unit:
	# Pass -k to pytest to filter by test name or filename
	# Pass -s to pytest to show stdout
	# Add --show-capture=no to hide captured output on failure
	pytest \
		-v \
		--log-format="%(levelname)s %(asctime)s %(filename)s:%(module)s:%(funcName)s:%(lineno)s %(message)s" \
		--cov-report term --cov-report html --cov=src/powerflex_logging_utilities \
		--durations=0 --durations-min=0.005 \
		unit_tests

test-unit-all-python-versions:
	tox

tox-recreate:
	tox --recreate

lint:
	pydocstyle --add-ignore=D100,D101,D102,D103,D104,D105,D106,D107,D202,D412 src unit_tests
	pylint src unit_tests

type-check-strict:
	mypy --no-warn-unused-ignores --strict $(STRICT_TYPED_FILES)

format-fix:
	black ${PYFILES}
	isort ${PYFILES}

format-check:
	black --check ${PYFILES}
	isort --check ${PYFILES}

repl:
	ipython -i repl.py

clean:
	rm -rf logs/
	# Python files
	rm -rf .pytest_cache reqlib-metadata __pycache__ .mypy_cache htmlcov .coverage
	rm -rf src/.pytest_cache src/powerflex_logging_utilities.egg-info/
	rm -rf build/
	rm -rf dist/
	rm -rf _generated_test_readme.py
	# Remove __pycache__ directories
	rm -rf $(shell find . -type d -iname __pycache__)

clean-all:
	rm -rf .tox
