from __future__ import print_function

import websocket

ws = websocket.WebSocket()
wsaddr = "ws://localhost:8090/_websocket/simulator"
ws.connect(wsaddr)

ws.send('[1,1,3,{"management":"subscribe"}]')
while True:
    result = ws.recv()
    print("Received '%s'" % result)
