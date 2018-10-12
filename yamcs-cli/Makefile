.PHONY: docs build

clean:
	rm -rf build dist *.egg-info

build:
	python setup.py sdist bdist_wheel

deploy: build
	twine upload -r pypi dist/*

