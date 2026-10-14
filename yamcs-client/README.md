# Yamcs Client Library for Python
[![PyPI](https://img.shields.io/pypi/v/yamcs-client.svg)](https://pypi.python.org/pypi/yamcs-client)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/yamcs-client.svg)](https://pypi.python.org/pypi/yamcs-client/)


## Features

* MDB retrieval
* Telemetry updates
* Command History updates
* Alarm updates
* Event updates
* Archive retrieval
* Histogram retrieval


## Installation

Install with pip

    pip install yamcs-client

For better performance when decoding large or frequent messages (for example
high-rate parameter subscriptions), also install the official `protobuf` runtime:

    pip install yamcs-client[protobuf]

Without this extra, yamcs-client uses a bundled pure-Python copy of protobuf.
This avoids version conflicts with other packages, but decodes messages
considerably slower. When a compatible `protobuf` package is installed, it is
used automatically.


## License

LGPL-3.0. See [LICENSE](https://github.com/yamcs/python-yamcs-client/blob/master/LICENSE)


## Third-Party Software

This project vendors the following third-party libraries:

- **protobuf** (BSD-3-Clause) - Copyright 2008 Google Inc. Located in `src/yamcs/protobuf/_vendor`. Used when no compatible `protobuf` package is installed.
