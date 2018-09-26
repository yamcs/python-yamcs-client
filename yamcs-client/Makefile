.PHONY: docs

clean:
	rm -rf build dist *.egg-info

build:
	python setup.py sdist bdist_wheel

deploy: build
	twine upload -r pypi dist/*

docs:
	cd docs && make clean html
