#!/bin/bash

cd src
# Keep yamcs/protobuf/_runtime.py (hand-written runtime selection)
rm -rf yamcs/api/
find yamcs/protobuf -mindepth 1 -maxdepth 1 ! -name _runtime.py -exec rm -rf {} +
cp -r ../../../yamcs/yamcs-api/src/main/proto/yamcs .

# Copy protobuf sources to yamcs/protobuf/_vendor
# (see vendorize.toml)
cd ..; python-vendorize; cd src


# Current code is generated with 35.0
# (when changing, update GENCODE_VERSION in yamcs/protobuf/_runtime.py
# and the protobuf extra in setup.py)
protoc --proto_path=. --python_out=. `find yamcs/protobuf -name '*.proto'` `find yamcs/api -name '*.proto'`


# Detect OS and set sed command
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS (BSD sed)
  SED_CMD=(sed -i '')
else
  # Linux (GNU sed)
  SED_CMD=(sed -i)
fi

# Redirect 'from google.protobuf' imports to yamcs.protobuf._runtime, which
# selects either the installed protobuf package or the vendored copy.
find yamcs/protobuf yamcs/api -path "*/_vendor" -prune -o -name "*_pb2.py" -exec "${SED_CMD[@]}" -E \
    -e 's/^from google\.protobuf(\.internal)? import /from yamcs.protobuf._runtime import /' {} +


# Delete all .proto files, skipping the _vendor directory entirely
find yamcs/protobuf yamcs/api -path "*/_vendor*" -prune -o -name "*.proto" -exec rm -f {} +

# Delete platform-specific upb
rm -rf yamcs/protobuf/_vendor/google/_upb/
