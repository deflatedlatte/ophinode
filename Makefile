.PHONY: build docs test test-docker

build:
	python3 -m build

docs:
	python3 docs/src/main.py

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

test-docker:
	./scripts/test-docker
