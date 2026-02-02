
import os
import socket

ip = os.getenv("SERVER_IP", "127.0.0.1")
port = int(os.getenv("SERVER_PORT", 7000))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ip, port))

print(client.recv(1024).decode())
client.send("Hi from Client 1".encode())
print(client.recv(1024).decode())

client.close()
