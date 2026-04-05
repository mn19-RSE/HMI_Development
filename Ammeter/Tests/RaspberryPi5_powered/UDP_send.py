import socket
import time

UDP_IP = "192.168.1.100"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_all_data(activeCup, value, scaled, currentPrefix):
    ts = time.time()

    msg = (
        f"Timestamp: {ts:.6f}\n"
        f"Input selection: {activeCup}\n"
        f"Range: {value}\n"
        f"Current value: {scaled:.6f}\n"
        f"Current unit: {currentPrefix}\n"
    )

    sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))