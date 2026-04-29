import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.bind("tcp://0.0.0.0:5557")

for i in range(100):
    task = {"id": i, "data": f"process item {i}"}
    socket.send_json(task)
    print(f"Sent task {i}")
