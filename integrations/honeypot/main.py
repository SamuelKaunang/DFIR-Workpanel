import threading
import signal
import sys
from services.ssh_honeypot import SSHHoneypot
from services.http_honeypot import HTTPHoneypot
from services.ftp_honeypot import FTPHoneypot

servers = [SSHHoneypot(), HTTPHoneypot(), FTPHoneypot()]

def shutdown(sig, frame):
    print("\nShutting down...")
    for s in servers: s.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)

for s in servers:
    threading.Thread(target=s.start, daemon=True).start()

print("Honeypot running on ports: 2222 (SSH), 8080 (HTTP), 2121 (FTP)")
try:
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    shutdown(None, None)