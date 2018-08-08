#!/bin/bash

protoc --proto_path=../yamcs/yamcs-api/src/main \
       --include_source_info \
       --descriptor_set_out=yamcs/types/message.desc \
       --python_out=yamcs/types \
       ../yamcs/yamcs-api/src/main/*.proto
