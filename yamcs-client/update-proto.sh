#!/bin/bash

rm -rf yamcs/api/ yamcs/protobuf/
cp -r ../../yamcs/yamcs-api/src/main/proto/yamcs .

protoc --proto_path=. --python_out=. `find yamcs/protobuf -name '*.proto'` `find yamcs/api -name '*.proto'`

for d in `find yamcs/protobuf -type d` `find yamcs/api -type d`; do
    rm $d/*.proto
done
