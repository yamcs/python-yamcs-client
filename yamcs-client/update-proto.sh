#!/bin/bash

# Important to generate from the root of the proto package
# structure. protoc python_out will then generate inter-module
# imports that work on both python 2 and python 3.
# Details: https://github.com/google/protobuf/issues/1491

rm -rf yamcs/protobuf/
cp -r ../../yamcs/yamcs-api/src/main/proto/ .

protoc --proto_path=. --python_out=. `find yamcs/protobuf -name '*.proto'`

for d in `find yamcs/protobuf -type d`; do
    rm $d/*.proto
    cat << EOF > $d/__init__.py
"""Yamcs Protobuf namespace package."""

import pkg_resources

pkg_resources.declare_namespace(__name__)
EOF
done
