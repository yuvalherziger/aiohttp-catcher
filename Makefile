#!make

VERSION ?= $(shell git describe --tags --exact-match 2>/dev/null || git rev-parse --abbrev-ref HEAD)
SRC_DIR = aiohttp_catcher
POETRY = poetry
POETRY_RUN := $(POETRY) run
PYLINT = $(POETRY_RUN) pylint
PYTEST = $(POETRY_RUN) pytest
BANDIT = $(POETRY_RUN) bandit
PYTEST_TESTS := tests
CI_TARGETS := lint test


.PHONY: ci
ci: $(CI_TARGETS)

.PHONY: lint
lint: lint/py

.PHONY: test
test: test/py

.PHONY: pylint
pylint:
	$(PYLINT) $(SRC_DIR)

.PHONY: pybandit
pybandit:
	$(BANDIT) -r $(SRC_DIR)

.PHONY: test/py
test/py: export CONFIG_PATH=./config/tests.yaml
test/py:
	$(PYTEST) \
	    --cov=$(SRC_DIR) \
	    $(PYTESTFLAGS) \
	    $(PYTEST_TESTS)

.PHONY: test/py/cov-xml
test/py/cov-xml: PYTESTFLAGS=--cov-report=xml
test/py/cov-xml: test/py

.PHONY: test/py/cov-html
test/py/cov-html: PYTESTFLAGS=--cov-report=html
test/py/cov-html: test/py

.PHONY: test/py/cov-all
test/py/cov-all: PYTESTFLAGS=--cov-report=term --cov-report=html --cov-report=xml
test/py/cov-all: test/py
