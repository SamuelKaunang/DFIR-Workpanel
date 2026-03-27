import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from base_server import HoneypotServer
from logger import log_event

SSH_BANNER = b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6\r\n"

class SSHHoneypot(HoneypotServer):
    def __init__(self):
        super().__init__(2222, "SSH")

    def handle_connection(self, conn, addr):
        src_ip, src_port = addr
        try:
            conn.send(SSH_BANNER)
            # Baca semua yang dikirim dalam 10 detik
            conn.settimeout(10)
            chunks = []
            while True:
                try:
                    data = conn.recv(1024)
                    if not data: break
                    chunks.append(data)
                except: break
            raw = b"".join(chunks)
            log_event("SSH", src_ip, src_port, raw)
        finally:
            conn.close()