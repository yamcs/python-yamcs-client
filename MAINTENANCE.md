## Dependencies

    pip install wheel twine

## Build Release

Build source, binary wheel and rpm to `dist/`:

    rm -rf dist/
    python setup.py sdist bdist_wheel bdist_rpm

## Publish to PyPI

Upload to test PyPI (assumes a repository testpypi in `~/.pypirc`):

    twine upload -r testpypi dist/*

Upload to PyPI (assumes a repository pypi in `~/.pypirc`):

    twine upload -r pypi dist/*

Be careful as both testpypi and pypi do not allow to reupload files under any circumstances (even after delete). So when using testpypi multiple times you may need to play with the version number beyond the third digit. PEP 440 convention for beta releases is to use string like `1.0.0b1`
