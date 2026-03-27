# File: echo_server.py
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 9999))
server.listen(5)
print("Echo server listening on port 9999...")

while True:
    conn, addr = server.accept()
    print(f"Connection from {addr}")
    data = conn.recv(1024)
    conn.send(data)  # kirim balik
    conn.close()