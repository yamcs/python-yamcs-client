#!/bin/bash

protoc --proto_path=../yamcs/yamcs-api/src/main --python_out=yamcs/types ../yamcs/yamcs-api/src/main/*.proto
