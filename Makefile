PYTHON ?= python3
VENV := .venv
VENV_PY := $(VENV)/bin/python3
CONFIG = config.txt

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install flake8 mypy build

build: install
	rm -rf build dist *.egg-info
	$(VENV_PY) -m build
	cp dist/mazegen-*.whl .
	cp dist/mazegen-*.tar.gz .

package: build

run:
	$(VENV_PY) a_maze_ing.py $(CONFIG)

debug:
	$(VENV_PY) -m pdb a_maze_ing.py $(CONFIG)

lint:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy --strict .

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache build dist *.egg-info $(VENV)
