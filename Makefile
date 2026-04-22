PYTHON = python3
MAIN = a_maze_ing.py
CONFIG = config.txt
PUSH_DIR = ~/Documents/maze_push

install:
	pip install flake8 mypy --break-system-packages

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf __pycache__ .mypy_cache || true
	rm -f *.pyc || true

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

build:
	python3 -m build
	cp ./dist/mazegen-1.0.0.tar.gz ./mazegen.tar.gz
	rm -rf build dist

push:
	cp -r * $(PUSH_DIR)

.PHONY: install run debug clean lint lint-strict push