import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from base_server import HoneypotServer
from logger import log_event

FAKE_RESPONSE = b"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
<html><body><h1>Router Admin</h1>
<form>Username: <input name='user'>
Password: <input type='password' name='pass'>
<button>Login</button></form></body></html>"""

def parse_http(raw):
    try:
        text = raw.decode("utf-8", errors="replace")
        lines = text.split("\r\n")
        first = lines[0].split()
        method = first[0] if len(first) > 0 else ""
        path   = first[1] if len(first) > 1 else ""
        headers = {}
        body = ""
        i = 1
        while i < len(lines) and lines[i] != "":
            if ":" in lines[i]:
                k, v = lines[i].split(":", 1)
                headers[k.strip()] = v.strip()
            i += 1
        if i < len(lines): body = "\r\n".join(lines[i+1:])
        return {"method": method, "path": path,
                "headers": headers, "body": body}
    except:
        return {}

class HTTPHoneypot(HoneypotServer):
    def __init__(self):
        super().__init__(8080, "HTTP")

    def handle_connection(self, conn, addr):
        src_ip, src_port = addr
        try:
            conn.settimeout(5)
            raw = conn.recv(4096)
            parsed = parse_http(raw)
            log_event("HTTP", src_ip, src_port, raw, extra=parsed)
            conn.send(FAKE_RESPONSE)
        finally:
            conn.close()