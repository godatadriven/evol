install:
	python setup.py install

develop:
	python setup.py develop

test: develop
	pytest

lint: develop
	flake8 evol
	flake8 tests

check: test lint