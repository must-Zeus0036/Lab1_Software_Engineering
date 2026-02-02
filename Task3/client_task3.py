import socket
import os
from dotenv import load_dotenv

# Load .env from root
load_dotenv()
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "6002"))


class HouseClient:
    def __init__(self, ip=SERVER_IP, port=SERVER_PORT):
        self.ip = ip
        self.port = port

    def send(self, msg):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.port))
        sock.sendall(msg.encode())
        reply = sock.recv(1024).decode()
        print("Server reply:", reply)
        sock.close()

    def run(self):
        while True:
            msg = input("Enter command (or quit): ").strip()
            if msg.lower() == "quit":
                break
            self.send(msg)


if __name__ == "__main__":
    HouseClient().run()
