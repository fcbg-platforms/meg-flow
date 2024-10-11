import time

import zmq


def control_main(action):
    """Send an action message to the server."""
    context = zmq.Context()
    socket = context.socket(zmq.REQ)  # REQ: Client side for REQ/REP pattern
    socket.connect("tcp://localhost:5555")  # Connect to server's address and port

    # Send the control message
    socket.send_string(action)

    # Wait for acknowledgment from the server
    reply = socket.recv_string()
    print(f"Server reply: {reply}")


if __name__ == "__main__":
    control_main("hold")  # Sends the hold command
    time.sleep(5)  # Wait for 5 seconds
    control_main("continue")  # Sends the continue command
