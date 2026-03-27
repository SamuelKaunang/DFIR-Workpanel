import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from base_server import HoneypotServer
from logger import log_event

class FTPHoneypot(HoneypotServer):
    def __init__(self):
        super().__init__(2121, "FTP")

    def handle_connection(self, conn, addr):
        src_ip, src_port = addr
        username = ""
        try:
            conn.send(b"220 ProFTPD 1.3.8 Server ready.\r\n")
            conn.settimeout(30)
            while True:
                line = conn.recv(1024).decode("utf-8",
                                errors="replace").strip()
                if not line: break
                cmd = line.split()[0].upper()
                arg = line[len(cmd):].strip()

                if cmd == "USER":
                    username = arg
                    conn.send(b"331 Password required.\r\n")
                elif cmd == "PASS":
                    log_event("FTP", src_ip, src_port,
                        extra={"username": username,
                            "password": arg})
                    conn.send(b"530 Login incorrect.\r\n")
                    break
                elif cmd == "QUIT":
                    conn.send(b"221 Goodbye.\r\n")
                    break
                else:
                    conn.send(b"500 Unknown command.\r\n")
        except: pass
        finally:
            conn.close()
