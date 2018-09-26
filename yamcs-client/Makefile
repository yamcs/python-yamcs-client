.PHONY: docs

build:
	python setup.py sdist bdist_wheel

deploy: build
	twine upload -r pypi dist/*

docs:
	cd docs && make html
