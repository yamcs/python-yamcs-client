#!/bin/bash

rm -rf src/yamcs/api/ src/yamcs/protobuf/
cp -r ../../yamcs/yamcs-api/src/main/proto/yamcs src/

protoc --proto_path=. --python_out=. `find src/yamcs/protobuf -name '*.proto'` `find src/yamcs/api -name '*.proto'`

for d in `find src/yamcs/protobuf -type d` `find src/yamcs/api -type d`; do
    rm $d/*.proto
done
