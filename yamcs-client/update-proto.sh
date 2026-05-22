#!/bin/bash

cd src
rm -rf yamcs/api/ yamcs/protobuf/
cp -r ../../../yamcs/yamcs-api/src/main/proto/yamcs .

# Copy protobuf sources to yamcs/protobuf/_vendor
# (see vendorize.toml)
cd ..; python-vendorize; cd src


# Current code is generated with 35.0
protoc --proto_path=. --python_out=. `find yamcs/protobuf -name '*.proto'` `find yamcs/api -name '*.proto'`


# Detect OS and set sed command
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS (BSD sed)
  SED_CMD=(sed -i '')
else
  # Linux (GNU sed)
  SED_CMD=(sed -i)
fi

# This targets the 'from google.protobuf' string and redirects it to the vendor folder
find yamcs/protobuf yamcs/api -name "*_pb2.py" -exec "${SED_CMD[@]}" \
    -e 's/^from google\.protobuf/from yamcs.protobuf._vendor.google.protobuf/g' \
    -e 's/^import google\.protobuf/import yamcs.protobuf._vendor.google.protobuf/g' {} +


# Delete all .proto files, skipping the _vendor directory entirely
find yamcs/protobuf yamcs/api -path "*/_vendor*" -prune -o -name "*.proto" -exec rm -f {} +

# Delete platform-specific upb
rm -rf yamcs/protobuf/_vendor/google/_upb/
