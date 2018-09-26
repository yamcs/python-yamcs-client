# Development Setup

Install build dependencies (you may want to do this in a virtualenv):

    pip install -r requirements.txt


Install `yamcs-client` from the source base:

    python setup.py develop

Changes to any source file have immediate impact.

# Release Procedure

## Dependencies

    pip install wheel twine

## Build Release

Build source and binary wheel to `dist/`:

    rm -rf dist/
    make clean build

## Publish to PyPI

Upload to test PyPI (assumes a repository testpypi in `~/.pypirc`):

    twine upload -r testpypi dist/*

Upload to PyPI (assumes a repository pypi in `~/.pypirc`):

    twine upload -r pypi dist/*

Be careful as both testpypi and pypi do not allow to reupload files under any circumstances (even after delete). So when using testpypi multiple times you may need to play with the version number beyond the third digit. PEP 440 convention for beta releases is to use string like `1.0.0b1`

## RPM Generation

Only done for specific targets.

- Modify setup.cfg as desired
- Tweak setup.py as desired (e.g. change name to python2-yamcs-client).
- Run: `python setup.py bdist_rpm`
- Revert changes to setup.py and setup.cfg

