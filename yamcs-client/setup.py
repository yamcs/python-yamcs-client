import io

import setuptools

with io.open("README.md", encoding="utf-8") as f:
    readme = f.read()

version = {}
with io.open("src/yamcs/clientversion.py", encoding="utf-8") as f:
    exec(f.read(), version)
version = version["__version__"]

setuptools.setup(
    name="yamcs-client",
    version=version,
    description="Yamcs API client library",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/yamcs/python-yamcs-client",
    author="Space Applications Services",
    author_email="yamcs@spaceapplications.com",
    license="LGPL",
    packages=setuptools.find_namespace_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    platforms="Posix; MacOS X; Windows",
    install_requires=["protobuf>=3.6", "requests", "setuptools", "websocket-client"],
    include_package_data=True,
    zip_safe=False,
)
