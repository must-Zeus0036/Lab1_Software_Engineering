
import os
import socket

ip = os.getenv("SERVER_IP", "127.0.0.1")
port = int(os.getenv("SERVER_PORT", 7000))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP socket
server.bind((ip, port))
server.listen(1)


print("Server is waiting...")

client_socket, addr = server.accept() # Accept a connection
print("Client connected:", addr)

client_socket.send("Hi from Server".encode())

msg = client_socket.recv(1024).decode()
print("Client says:", msg)

client_socket.send("Welcome Client 1".encode())

client_socket.close()
server.close()

