#!/bin/bash

cd src
rm -rf yamcs/api/ yamcs/protobuf/
cp -r ../../../yamcs/yamcs-api/src/main/proto/yamcs .

# Current code is generated with 5.29.3

protoc --proto_path=. --python_out=. `find yamcs/protobuf -name '*.proto'` `find yamcs/api -name '*.proto'`

for d in `find yamcs/protobuf -type d` `find yamcs/api -type d`; do
    rm $d/*.proto
done
