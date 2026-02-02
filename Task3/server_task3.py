"""
server_task3.py (Task 3 - Class-based GUI TCP Server)

- Server listens on SERVER_BIND_IP and TASK3_PORT from root .env
- Receives commands like: "light:on,door:open,window:closed"
- Updates house.json
- Tkinter GUI reads house.json every 500 ms and updates colors
"""

import socket
import threading
import json
import os
import tkinter as tk
from dotenv import load_dotenv

# Load .env (works from Task3 folder because .env is in parent/root)
load_dotenv()

BIND_IP = os.getenv("SERVER_BIND_IP", "0.0.0.0")
PORT = int(os.getenv("TASK3_PORT", "6005"))


class HouseStorage:
    """Read/write house.json safely (thread-safe)."""

    def __init__(self, filename="house.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(base_dir, filename)

        self.lock = threading.Lock()

        # Create file if missing
        if not os.path.exists(self.filename):
            self.write({"light": "off", "door": "closed", "window": "closed"})

    def read(self):
        with self.lock:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)

    def write(self, state):
        with self.lock:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)

    def update_from_message(self, message):
        """
        message example: "light:on,door:open,window:closed"
        Updates JSON file and returns new state dict.
        """
        state = self.read()

        parts = message.split(",")
        for p in parts:
            p = p.strip()
            if ":" not in p:
                continue
            key, value = p.split(":", 1)
            key = key.strip().lower()
            value = value.strip().lower()
            state[key] = value

        self.write(state)
        return state


class HouseGUI:
    #Tkinter GUI that shows light/door/window with shapes

    def __init__(self, root, storage):
        self.root = root
        self.storage = storage

        self.root.title("Task 3 - House GUI (Server)")

        self.canvas = tk.Canvas(root, width=450, height=220, bg="white")
        self.canvas.pack(padx=10, pady=10)

        # Shapes
        self.light_circle = self.canvas.create_oval(30, 30, 90, 90)                 # circle
        self.door_triangle = self.canvas.create_polygon(180, 90, 210, 30, 240, 90)  # triangle
        self.window_square = self.canvas.create_rectangle(350, 30, 410, 90)         # square

        # Labels
        self.canvas.create_text(60, 120, text="Light")
        self.canvas.create_text(210, 120, text="Door")
        self.canvas.create_text(380, 120, text="Window")

        # Start loop
        self.update_loop()

    def update_gui(self, state):
        # Light
        self.canvas.itemconfig(
            self.light_circle,
            fill="yellow" if state.get("light") == "on" else "gray"
        )

        # Door
        self.canvas.itemconfig(
            self.door_triangle,
            fill="green" if state.get("door") == "open" else "red"
        )

        # Window
        self.canvas.itemconfig(
            self.window_square,
            fill="blue" if state.get("window") == "open" else "gray"
        )

    def update_loop(self):
        #Read JSON repeatedly and refresh GUI
        state = self.storage.read()
        self.update_gui(state)
        self.root.after(500, self.update_loop)  # refresh every 0.5 sec


class ClientHandler(threading.Thread):
    #One thread per client; updates JSON based on client message

    def __init__(self, conn, addr, storage):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.storage = storage

    def run(self):
        try:
            msg = self.conn.recv(1024).decode().strip()
            if not msg:
                return

            print("[RECEIVED]", self.addr, "->", msg)

            new_state = self.storage.update_from_message(msg)
            print("[UPDATED JSON]", new_state)

            self.conn.sendall(b"OK: updated")

        finally:
            self.conn.close()


class HouseServer:
    #tarts TCP server in background + runs GUI in main thread

    def __init__(self, ip=BIND_IP, port=PORT):
        self.ip = ip
        self.port = port
        self.storage = HouseStorage("house.json")

        self.root = tk.Tk()
        self.gui = HouseGUI(self.root, self.storage)

    def run_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.ip, self.port))
        s.listen()

        print(f"[LISTENING] Server on {self.ip}:{self.port}")

        while True:
            conn, addr = s.accept()
            print("[NEW CONNECTION]", addr)
            ClientHandler(conn, addr, self.storage).start()

    def start(self):
        threading.Thread(target=self.run_server, daemon=True).start()
        self.root.mainloop()


if __name__ == "__main__":
    HouseServer().start()
