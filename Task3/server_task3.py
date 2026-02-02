import socket
import threading
import json
import os
import tkinter as tk
from dotenv import load_dotenv

# Load .env from current folder OR parent folder (root)
load_dotenv()
SERVER_IP = os.getenv("SERVER_IP", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "6002"))


class HouseStorage:
    #Read/write house.json safely .. thread-safe
    def __init__(self, filename="house.json"):
        self.filename = filename
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
        # message example: "light:on,door:open,window:closed"
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


class HouseGUI:
    # Draw light/door/window and update colors
    def __init__(self, root):
        self.root = root
        self.root.title("Task 3 - House GUI (Server)")

        self.canvas = tk.Canvas(root, width=450, height=200)
        self.canvas.pack()

        # Shapes
        self.light_circle = self.canvas.create_oval(30, 30, 90, 90)
        self.door_triangle = self.canvas.create_polygon(180, 90, 210, 30, 240, 90)
        self.window_square = self.canvas.create_rectangle(350, 30, 410, 90)

        # Labels
        self.canvas.create_text(60, 110, text="Light")
        self.canvas.create_text(210, 110, text="Door")
        self.canvas.create_text(380, 110, text="Window")

    def update(self, state):
        # Light
        self.canvas.itemconfig(
            self.light_circle,
            fill=("yellow" if state.get("light") == "on" else "gray")
        )

        # Door
        self.canvas.itemconfig(
            self.door_triangle,
            fill=("green" if state.get("door") == "open" else "red")
        )

        # Window
        self.canvas.itemconfig(
            self.window_square,
            fill=("blue" if state.get("window") == "open" else "gray")
        )


class ClientHandler(threading.Thread):
    # Handle one client connection.
    def __init__(self, conn, addr, storage, gui, root):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.storage = storage
        self.gui = gui
        self.root = root

    def run(self):
        try:
            msg = self.conn.recv(1024).decode().strip()
            if not msg:
                return

            print("[CLIENT]", self.addr, "->", msg)

            # Update JSON
            new_state = self.storage.update_from_message(msg)

            # Update GUI in main thread
            self.root.after(0, self.gui.update, new_state)

            # Reply to client
            self.conn.sendall(b"OK: updated")

        finally:
            self.conn.close()


class HouseServer:
    # GUI + TCP server together
    def __init__(self, ip=SERVER_IP, port=SERVER_PORT):
        self.ip = ip
        self.port = port
        self.storage = HouseStorage("house.json")

        self.root = tk.Tk()
        self.gui = HouseGUI(self.root)

        # Load initial state into GUI
        self.gui.update(self.storage.read())

    def start_network_thread(self):
        t = threading.Thread(target=self.run_server, daemon=True)
        t.start()

    def run_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.ip, self.port))
        s.listen()
        print(f"[LISTENING] GUI Server on {self.ip}:{self.port}")

        while True:
            conn, addr = s.accept()
            ClientHandler(conn, addr, self.storage, self.gui, self.root).start()

    def start(self):
        self.start_network_thread()
        self.root.mainloop()


if __name__ == "__main__": # Run the server
    HouseServer().start()
