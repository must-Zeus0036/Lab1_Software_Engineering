import socket
import os
from dotenv import load_dotenv


load_dotenv()
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "7000"))


class HouseClient:
    #Connects to server, receives welcome, sends update, gets response
    def __init__(self, ip=SERVER_IP, port=SERVER_PORT):
        self.ip = ip
        self.port = port

    def send_update(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.port))

        # Receive welcome (Requirement 2a)
        welcome = sock.recv(1024).decode()
        print("Server says:", welcome)

        # Send update (Requirement 2d)
        print("Sending:", message)
        sock.sendall(message.encode())

        # Receive server confirmation
        reply = sock.recv(1024).decode()
        print("Server reply:", reply)

        sock.close()


if __name__ == "__main__":
    client = HouseClient()

    # Type the message like=light:off,door:closed,window:closed
    msg = input("Enter update (example: light:off,door:closed,window:closed): ").strip()
    client.send_update(msg)
