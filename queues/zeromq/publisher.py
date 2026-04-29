import zmq
import json
import time

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://0.0.0.0:5556")

print("Publisher started on port 5556")

while True:
    event = {
        "type": "order.created",
        "order_id": 1234,
        "timestamp": time.time()
    }
    # Topic-based routing: "orders " prefix
    socket.send_string(f"orders {json.dumps(event)}")
    time.sleep(1)
