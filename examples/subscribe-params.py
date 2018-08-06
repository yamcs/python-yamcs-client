from __future__ import print_function

import websocket

ws = websocket.WebSocket()
wsaddr = "ws://localhost:8090/_websocket/simulator"
ws.connect(wsaddr)

ws.send('[1,1,3, {"parameter": "subscribe", "data": { "id" : [ \
           {"name": "/YSS/SIMULATOR/Alpha"},\
           {"name": "/YSS/SIMULATOR/Heading"}, \
           {"name": "SIMULATOR_PrimBusVoltage1", "namespace": "MDB:OPS Name"}\
        ], "updateOnExpiration": true }}]')

while True:
    result = ws.recv()
    print("Received '%s'" % result)
