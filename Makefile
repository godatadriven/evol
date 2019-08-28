.PHONY: docs

flake:
	flake8 evol
	flake8 tests
	flake8 setup.py

install:
	pip install -e .

develop:
	pip install -e ".[dev]"
	python setup.py develop

test:
	python setup.py test

check: test flake

docs:
	sphinx-apidoc -f -o doc/api evol
	sphinx-build doc docs

clean:
	rm -rf .cachew
	rm -rf .pytest_cache
	rm -rf build
	rm -rf dist
	rm -rf evol.egg-info
	rm -rf .ipynb_checkpoints
