import socket
import urllib.request
import time

def simulate_http():
    print("[SIMULATOR] Sending malicious HTTP request...")
    try:
        # Simulate an attack payload (e.g. attempting to read /etc/passwd or login brute force)
        req = urllib.request.Request(
            'http://127.0.0.1:8080/cgi-bin/admin.cgi?cmd=cat%20/etc/passwd',
            data=b"username=admin&password=dev123",
            method='POST',
            headers={'User-Agent': 'Hydra/9.1', 'Content-Type': 'application/x-www-form-urlencoded'}
        )
        urllib.request.urlopen(req, timeout=2)
    except Exception as e:
        # The honeypot might abruptly close or we just don't care about the response
        pass

def simulate_ftp():
    print("[SIMULATOR] Sending malicious FTP login...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(('127.0.0.1', 2121))
        # Optional: wait for banner
        s.recv(1024)
        s.send(b"USER admin\r\n")
        time.sleep(0.5)
        s.recv(1024)
        s.send(b"PASS root123\r\n")
        time.sleep(0.5)
        s.close()
    except Exception as e:
        print(f"FTP err: {e}")

def simulate_ssh():
    print("[SIMULATOR] Sending SSH handshake / brute-force attempt...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(('127.0.0.1', 2222))
        # Receive server banner
        s.recv(1024)
        # Send fake SSH protocol version/client banner
        s.send(b"SSH-2.0-OpenSSH_7.2p2 Ubuntu-4ubuntu2.2\r\n")
        # Send typical fake payload bytes (which would be the SSH key exchange init)
        time.sleep(1)
        s.send(b"\x00\x00\x00\x1c\x06\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        s.close()
    except Exception as e:
        print(f"SSH err: {e}")

if __name__ == "__main__":
    print("-" * 50)
    print("Initiating Honeypot Attack Simulation Sequence")
    print("-" * 50)
    
    simulate_http()
    time.sleep(2)
    simulate_ftp()
    time.sleep(2)
    simulate_ssh()
    
    print("-" * 50)
    print("Simulation Complete. Check the Dashboard (Cases & Timeline).")
