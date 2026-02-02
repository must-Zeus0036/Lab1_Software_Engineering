import socket
import threading
import json
import os
from dotenv import load_dotenv

# Load .env from current folder OR parent folder (root)
load_dotenv()
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "7000"))


class HouseStorage:
    #read/write House.json safely
    def __init__(self, filename="House.json"):
        self.filename = filename
        self.lock = threading.Lock()

        # Create file if missing
        if not os.path.exists(self.filename):
            self.write({"light": "on", "door": "open", "window": "open"})

        # Requirement 2c: read and show initial content
        print("[HOUSE] Initial:", self.read())

    def read(self):
        with self.lock:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)

    def write(self, state):
        with self.lock:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)

    def update_from_message(self, message):
        #message example: "light:off,door:closed,window:closed" Updates JSON file
        state = self.read()

        parts = message.split(",")
        for p in parts:
            p = p.strip()
            if ":" not in p:
                continue
            key, value = p.split(":", 1)
            state[key.strip()] = value.strip()

        self.write(state)
        return state


class ClientHandler(threading.Thread):
    # handle each client in a separate thread 
    def __init__(self, conn, addr, client_id, storage):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.client_id = client_id
        self.storage = storage

    def run(self):
        print(f"[NEW] Client {self.client_id} connected from {self.addr}")

        try:
            # Requirement 2a: unique welcome message
            welcome = f"Welcome Client {self.client_id}!"
            self.conn.sendall(welcome.encode())

            # Receive update message (Requirement 2d)
            msg = self.conn.recv(1024).decode().strip()
            if not msg:
                return

            print(f"[CLIENT {self.client_id}] Received: {msg}")

            # Update JSON (Requirement 2e)
            new_state = self.storage.update_from_message(msg)
            print("[HOUSE] Updated:", new_state)

            self.conn.sendall(b"OK: JSON updated")

        finally:
            self.conn.close()
            print(f"[CLOSE] Client {self.client_id} disconnected")


class Server:
    #Main multi-client TCP server
    def __init__(self, ip=SERVER_IP, port=SERVER_PORT):
        self.ip = ip
        self.port = port
        self.storage = HouseStorage("House.json")
        self.client_counter = 0

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.ip, self.port))
        s.listen()

        print(f"[LISTENING] Server on {self.ip}:{self.port}")

        while True:
            conn, addr = s.accept()
            self.client_counter += 1
            ClientHandler(conn, addr, self.client_counter, self.storage).start()


if __name__ == "__main__": # Run the server
    Server().start()
