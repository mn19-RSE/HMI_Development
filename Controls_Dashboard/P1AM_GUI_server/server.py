import board
import digitalio
import busio
import time
import struct

import adafruit_wiznet5k.adafruit_wiznet5k as wiznet
import adafruit_wiznet5k.adafruit_wiznet5k_socket as socket
from adafruit_httpserver import Server, Request, Response

# -------------------------
# USER VARIABLES (GUI controlled)
# -------------------------
led_state = False
slider_value = 50

# UDP target
UDP_IP = "192.168.42.15"
UDP_PORT = 5005

# send interval (seconds)
SEND_INTERVAL = 0.5
last_send_time = 0

# -------------------------
# SPI + Ethernet Setup
# -------------------------
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D10)

eth = wiznet.WIZNET5K(
    spi,
    cs,
    is_dhcp=False,
    ip=(192, 168, 42, 50),   # match your network!
    subnet=(255, 255, 255, 0),
    gateway=(192, 168, 42, 1),
    dns=(8, 8, 8, 8)
)

socket.set_interface(eth)

print("My IP:", eth.pretty_ip(eth.ip_address))

# -------------------------
# UDP Socket
# -------------------------
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# -------------------------
# Web Server
# -------------------------
server = Server(socket, "/", debug=True)

HTML_PAGE = """\
<!DOCTYPE html>
<html>
<body>
<h1>P1AM Control</h1>

<p>LED: {led}</p>
<a href="/toggle"><button>Toggle</button></a>

<p>Value: {slider}</p>
<form action="/set">
<input type="range" name="val" min="0" max="100" value="{slider}">
<input type="submit">
</form>

</body>
</html>
"""

@server.route("/")
def index(request: Request):
    return Response(
        request,
        HTML_PAGE.format(led=led_state, slider=slider_value),
        content_type="text/html"
    )

@server.route("/toggle")
def toggle(request: Request):
    global led_state
    led_state = not led_state
    return Response(request, "OK <a href='/'>Back</a>")

@server.route("/set")
def set_value(request: Request):
    global slider_value
    try:
        slider_value = int(request.query_params.get("val"))
    except:
        pass
    return Response(request, "OK <a href='/'>Back</a>")

server.start(str(eth.pretty_ip(eth.ip_address)))

# -------------------------
# MAIN LOOP
# -------------------------
while True:
    try:
        server.poll()

        now = time.monotonic()

        # Send UDP periodically (non-blocking)
        if now - last_send_time > SEND_INTERVAL:
            last_send_time = now

            # Example analog value (replace with real ADC read)
            analog_value = slider_value  # placeholder

            # Pack data (2 integers)
            packet = struct.pack("HH", slider_value, analog_value)

            udp_sock.sendto(packet, (UDP_IP, UDP_PORT))

            print("Sent UDP:", slider_value, analog_value)

        # Example logic use
        if led_state:
            pass  # control output here

    except Exception as e:
        print("Error:", e)
