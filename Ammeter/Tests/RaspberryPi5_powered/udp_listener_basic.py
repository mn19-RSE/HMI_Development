import socket

LISTEN_PORT = 1196

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("192.168.0.111", LISTEN_PORT))
print(f"Listening for UDP packets on port {LISTEN_PORT}...")

while True:
    data, addr = sock.recvfrom(1024)
    print(f"Received {len(data)} bytes from {addr}: {data.decode(errors='ignore')}")