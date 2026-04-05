import socket
import time

UDP_IP = "192.168.42.100" # Change to 42.15 for final implementation
UDP_PORT = 1194

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_all_data(activeCup, value, scaled, currentPrefix):
    ts = time.time()

    msg = (
        f"Timestamp: {ts:.6f}\n"
        f"Input selection: {activeCup}\n"
        f"Current value: {scaled:.6f}\n"
        f"Current unit: {currentPrefix}\n"
    )

    sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))