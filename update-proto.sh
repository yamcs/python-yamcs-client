#!/bin/bash

mkdir -p yamcs/client/proto
protoc --proto_path=../yamcs/yamcs-api/src/main --python_out=yamcs/proto ../yamcs/yamcs-api/src/main/*.proto
