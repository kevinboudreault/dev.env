import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://publisher:5556")
socket.setsockopt_string(zmq.SUBSCRIBE, "orders")

print("Subscriber connected, waiting for messages...")

while True:
    message = socket.recv_string()
    topic, data = message.split(" ", 1)
    event = json.loads(data)
    print(f"Received {topic}: {event}")
