from daqhats import mcc118
import pygame
import time
from gpiozero import LED, Button
import socket

# daqhats init
hat = mcc118(0)

# network variables
UDP_IP = "192.168.0.111" # Change to 42.15 for final implementation
UDP_PORT = 1196 # destination port
LISTEN_PORT = 5005 # port to listen on 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", LISTEN_PORT))
sock.setblocking(False) # needed for listening to not pause script

# gpio init
# scale output pins (LSB - MSB)
pins = [LED(21), LED(19), LED(20)]
# scale button pins
btn_up = Button(4, pull_up=True, bounce_time=0.1)
btn_down = Button(27, pull_up=True, bounce_time=0.1)
# cup input rotary switch pins
input_button_pins = [1, 0, 22, 23, 16, 6, 5, 25, 24, 18, 17]
input_buttons = [Button(pin, pull_up=True, bounce_time=0.05) for pin in input_button_pins]
ERROR_INDEX = len(input_button_pins) 

# pygame init
screen_width = 1280
screen_height = 400
pygame.init()
screen = pygame.display.set_mode((400, 1280), pygame.FULLSCREEN)
canvas = pygame.Surface((1280, 400))
pygame.mouse.set_visible(False)
# canvas.fill((0, 255, 0))
rotated = pygame.transform.rotate(canvas, 90)
screen.blit(rotated, (0, 0))
pygame.display.flip()
# time.sleep(2)
# pygame font sizes
font_small = pygame.font.SysFont(None, 50)
font_large = pygame.font.SysFont(None, 180)

# color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
GRAY = (100, 100, 100)
CYAN = (0, 255, 255)
RED = (255, 0, 0)

# input selections
input_names = ["OD CUP", "LE CUP", "HE CUP", "OBJ CUP", "IMG CUP", "R45 TARGET", "R30 TARGET", "L30 TARGET", "", "", "", "ERROR: INVALID INPUT"] 
activeCup = 0

# scale selections
scale_names = ["1 nA", "10 nA", "100 nA", "1 μA", "10 μA", "100 μA", "1 mA", "10 mA"]
scale_voltage_multipliers = [.1, 1, 10, .1, 1, 10, .1, 1]
scale_units = ["nA", "nA", "nA", "μA", "μA", "μA", "mA", "mA"]
scale_value = 0  

voltage = 0.0
scaled_voltage = 0.0


def draw_bar(voltage):

    # Map absolute value of -10V-+10V to screen width
    bar_x = 0
    bar_y = screen_height - 50
    bar_width = screen_width 
    bar_height = 50

    pygame.draw.rect(canvas, GRAY, (bar_x, bar_y, bar_width, bar_height))

    # Normalize voltage
    norm = abs(voltage / 10)  # 0 to 1
    fill_width = int(norm * bar_width)

    pygame.draw.rect(canvas, DYNAMIC_COLOR, (bar_x, bar_y, fill_width, bar_height))

def draw_screen(voltage, scaled_voltage):
    global DYNAMIC_COLOR
    if voltage < 0:
        DYNAMIC_COLOR = CYAN
    elif voltage >= 0:
        DYNAMIC_COLOR = RED 
    canvas.fill(BLACK)

    # Top text
    if activeCup == ERROR_INDEX:
        INPUT_COLOR = RED
    else:
        INPUT_COLOR = CYAN
    input_text = font_small.render(f"Input: {input_names[activeCup]}", True, INPUT_COLOR)
    range_text = font_small.render(f"Range: Max Value = ±{scale_names[scale_value]}", True, CYAN)

    canvas.blit(input_text, (20, 20))
    canvas.blit(range_text, (600, 20))

    # Big voltage display
    if abs(voltage) < 10: 
        volt_text = font_large.render(f"{scaled_voltage:+.5f} {scale_units[scale_value]}", True, DYNAMIC_COLOR)
        canvas.blit(volt_text, (450, 220))
    elif abs(voltage) >= 10:
        over_limit = font_large.render("OL", True, GREEN)
        canvas.blit(over_limit, (1000, 220))
    # Bar graph
    draw_bar(voltage)

    rotated = pygame.transform.rotate(canvas, 90)
    screen.blit(rotated, (0, 0))
    pygame.display.flip()

def read_voltage():
    return hat.a_in_read(0)

# set scale output decimal to binary 
def update_outputs():
    for i in range(3):
        if (scale_value >> i) & 1:
            pins[i].on()
        else:
            pins[i].off()

def increment():
    global scale_value
    scale_value = (scale_value + 1) % 8
    update_outputs()

def decrement():
    global scale_value
    scale_value = (scale_value - 1) % 8
    update_outputs()

def send_all_data():
    ts = time.time()
    # UDP message string
    msg = (
        f"Timestamp: {ts:.6f}\n"
        f"Input selection: {input_names[activeCup]}\n"
        f"Current value: {scaled_voltage:.5f}\n"
        f"Current unit: {scale_units[scale_value]}\n"
    )

    sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))

# reads rotary switch
 
def get_active_cup():
    for i, btn in enumerate(input_buttons):
        if btn.is_pressed:
            return i
    return ERROR_INDEX   # nothing selected → ERROR

# Main loop
running = True
clock = pygame.time.Clock()
btn_up.when_pressed = increment
btn_down.when_pressed = decrement
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    activeCup = get_active_cup()
    voltage = read_voltage() 
    scaled_voltage = voltage * scale_voltage_multipliers[scale_value]
    # reduces zero hunting 
    # remove if not needed with current amp
    if abs(voltage) < .01:
        scaled_voltage = 0
        voltage = 0
    draw_screen(voltage, scaled_voltage)
    # set scale binary word
    update_outputs()
    send_all_data()
    try:
        data, addr = sock.recvfrom(1024)
        cmd = data.decode().strip()
        if cmd == "UP":
            increment()
        elif cmd == "DOWN":
            decrement()
    except BlockingIOError:
        pass

    clock.tick(60)  # 60 FPS

pygame.quit()

