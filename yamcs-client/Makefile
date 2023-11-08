.PHONY: clean lint build deploy

clean:
	rm -rf build dist *.egg-info

lint:
	flake8 src --exclude '*pb2.py' --count --show-source --statistics

build_legacy: lint
	python setup.py sdist bdist_wheel

build: lint
	python -m build

deploy: clean build
	twine upload -r pypi dist/*
