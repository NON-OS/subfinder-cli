PY ?= python3

.PHONY: test coverage lint format format-check types check
test:
	PYTHONPATH=src $(PY) -m unittest discover -s tests -t .

coverage:
	PYTHONPATH=src $(PY) -m coverage run -m unittest discover -s tests -t .
	$(PY) -m coverage report

lint:
	ruff check src tests

format:
	ruff format src tests

format-check:
	ruff format --check src tests

types:
	mypy --strict src

check: lint format-check types coverage
