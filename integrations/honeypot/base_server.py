# File: honeypot/base_server.py
import socket
import threading
import datetime

class HoneypotServer:
    def __init__(self, port, service_name):
        self.port = port
        self.service_name = service_name
        self.running = False
        self.sock = None

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.port))
        self.sock.listen(10)
        self.running = True
        print(f"[{self.service_name}] Listening on port {self.port}")
        while self.running:
            try:
                conn, addr = self.sock.accept()
                t = threading.Thread(
                    target=self.handle_connection,
                    args=(conn, addr),
                    daemon=True
                )
                t.start()
            except OSError:
                break

    def handle_connection(self, conn, addr):
        # Subclass override ini
        src_ip, src_port = addr
        print(f"[{self.service_name}] Connection: {src_ip}:{src_port}")
        conn.close()

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()


