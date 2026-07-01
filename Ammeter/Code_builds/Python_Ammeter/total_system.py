from daqhats import mcc118
import pygame
import time
from gpiozero import LED, Button
import socket
import os
import json 
from collections import deque
import SM16relind

# daqhats init
hat = mcc118(0)
ema_voltage = 0.0
EMA_ALPHA = 0.1  # 0.1 = very smooth, 0.3 = more responsive

# relay board init
rel0 = SM16relind.SM16relind(0) # 1-12 (closest to inputs)
rel1 = SM16relind.SM16relind(1) # 13-24

#oversample definitions
SAMPLE_COUNT = 8  # adjust (8–32 is typical)
samples = deque(maxlen=SAMPLE_COUNT)

# network variables
UDP_IP = "192.168.42.15" # Change to 42.15 for final implementation
UDP_PORT = 60000 # destination port
LISTEN_PORT = 60000 # port to listen on 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", LISTEN_PORT))
sock.setblocking(False) # needed for listening to not pause script

# gpio init
# scale output pins (LSB - MSB)
pins = [LED(21), LED(20), LED(19)] # tested, seems correct 21, 20, 19
# scale button pins
btn_up = Button(4, pull_up=True, bounce_time=0.1)
btn_down = Button(27, pull_up=True, bounce_time=0.1) 

# input button pins
cup_btn_up = Button(23, pull_up=True, bounce_time=0.1)
cup_btn_down = Button(22, pull_up=True, bounce_time=0.1)

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

# pygame font sizes
font_small = pygame.font.SysFont(None, 50)
font_large = pygame.font.SysFont(None, 180)
# static image load
vdg_logo = pygame.image.load("vdg.png").convert_alpha()

# color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (100, 0, 255)
PINK = (255, 0, 255)

# input selections
input_names = ["OD CUP", "LE CUP", "HE CUP", "OBJ CUP", "IMG CUP", "6", "7", "8", "9", "10", "11", "12"] 
input_xlocations = [750, 610, 360, 290, 245, 10000, 10000, 10000, 10000, 10000, 10000, 10000]
input_ylocations = [127, 127, 127, 127, 170, 10000, 10000, 10000, 10000, 10000, 10000, 10000]

activeCup = 1 # defaults to LE cup when power cycled
input_key = "ch_lecup_ival"
previous_cup = 0

# scale selections
'''
scale_names = ["100 pA", "1 nA", "10 nA", "100 nA", "1 μA", "10 μA", "100 μA", "1 mA"]
scale_voltage_multipliers = [10, .1, 1, 10, .1, 1, 10, .1]
scale_units = ["pA", "nA", "nA", "nA", "μA", "μA", "μA", "mA"]
scale_value = 2
'''
# testing truncating scales that dont work or are not needed
scale_names = ["10 nA", "100 nA", "1 μA", "10 μA", "100 μA"]
scale_voltage_multipliers = [1, 10, .1, 1, 10]
scale_units = ["nA", "nA", "μA", "μA", "μA"]
scale_value = 0

# daq read vairables
voltage = 0.0
scaled_voltage = 0.0

# screen mirroring variables
last_save_time = 0
SAVE_INTERVAL = 0.1  # 10 FPS

# UDP send rate
last_udp_time = 0
UDP_INTERVAL = 1  # 1 Hz 

# text display rate
last_text_voltage = 0.0
last_volt_time = 0
VOLT_INTERVAL = 1 # 1 Hz

# zero clamp width
DEADBAND = 0.1


def set_cup(activeCup):
    global previous_cup	
    if activeCup != previous_cup:
        # close conductor relay, open shield relay
        # keep all other shield relays closed and conductor relays open
        rel0.set_all(1) # connect all shields to conductors 
        rel1.set_all(0) # disconnect all conductors from input
        time.sleep(.1) # small debaounce
        rel0.set(activeCup+1, 0) # disconnect active cup condcutor from shield 
        rel1.set(activeCup+1, 1) # connect active cup conductor to input

        global input_key
        if activeCup == 0:
            input_key = "ch_odcup_ival"
        if activeCup == 1:
            input_key = "ch_lecup_ival"
        if activeCup == 2:
            input_key = "ch_hecup_ival"
        if activeCup == 3:
            input_key = "ch_objcup_ival"
        if activeCup == 4:
            input_key = "ch_imgcup_ival"
        if activeCup == 5:
            input_key = "ch_6cup_ival"
        if activeCup == 6:
            input_key = "ch_7cup_ival"
        if activeCup == 7:
            input_key = "ch_8cup_ival"
        if activeCup == 8:
            input_key = "ch_9cup_ival"
        if activeCup == 9:
            input_key = "ch_10cup_ival"
        if activeCup == 10:
            input_key = "ch_11cup_ival"
        if activeCup == 11:
            input_key = "ch_12cup_ival"

        previous_cup = activeCup

def increment_cup():
    global activeCup
    activeCup = (activeCup + 1) % 11
    
def decrement_cup():
    global activeCup
    activeCup = (activeCup - 1) % 11
    
def draw_active_cup():
    pygame.draw.circle(canvas, PINK, (input_xlocations[activeCup], input_ylocations[activeCup]), 10, 10)

def draw_bar(voltage):

    # Map absolute value of -10V to +10V to screen width
    bar_x = 0
    bar_height = 50
    bar_y = screen_height - bar_height
    bar_width = screen_width 
    
    pygame.draw.rect(canvas, GRAY, (bar_x, bar_y, bar_width, bar_height))

    # Normalize voltage
    norm = abs(voltage / 10)  # 0 to 1
    fill_width = int(norm * bar_width)
    pygame.draw.rect(canvas, DYNAMIC_COLOR, (bar_x, bar_y, fill_width, bar_height))

def draw_screen(voltage, scaled_voltage):
    global last_volt_time
    global last_text_voltage
    global DYNAMIC_COLOR
    if voltage < 0:
        DYNAMIC_COLOR = BLUE
    elif voltage >= 0:
        DYNAMIC_COLOR = GREEN
    canvas.fill(BLACK)

    # Top text
    if activeCup == len(input_names):
        INPUT_COLOR = RED
    else:
        INPUT_COLOR = CYAN
    input_text = font_small.render(f"Input: {input_names[activeCup]}", True, INPUT_COLOR)
    canvas.blit(input_text, (20, 20))

    range_text = font_small.render(f"Range: Max Value = ±{scale_names[scale_value]}", True, CYAN)
    rect = range_text.get_rect()
    rect.topright = (1260, 20)
    canvas.blit(range_text, rect)
    
    # vdg logo draw
    canvas.blit(vdg_logo, (175, 87))

    if activeCup < 5:
        draw_active_cup()

    now = time.time()
    if now - last_volt_time > VOLT_INTERVAL:
        last_volt_time = now
        last_text_voltage = scaled_voltage

    if abs(last_text_voltage) < 10:
        volt_text = font_large.render(f"{last_text_voltage:+.5f} {scale_units[scale_value]}", True, DYNAMIC_COLOR)
        rect = volt_text.get_rect()
        rect.topright = (1260, 220)
        canvas.blit(volt_text, rect)
    else:
            over_limit = font_large.render("OL", True, RED)
            rect = over_limit.get_rect()
            rect.topright = (1260, 220)
            canvas.blit(over_limit, rect)
            DYNAMIC_COLOR = RED
         
    # Bar graph
    draw_bar(voltage)

    rotated = pygame.transform.rotate(canvas, 90)
    screen.blit(rotated, (0, 0))
    pygame.display.flip()

def read_voltage_oversampled(n=4): #4 is default (2-4)
    # average multiple reads per loop
    total = 0
    for _ in range(n):
        total += hat.a_in_read(0)
    return total / n

def apply_ema(new_value):
    global ema_voltage
    ema_voltage = (EMA_ALPHA * new_value) + ((1 - EMA_ALPHA) * ema_voltage)
    return ema_voltage

# set scale output decimal to binary 
def update_outputs():
    if scale_value == 0:
        pins[2].off()
        pins[1].on()
        pins[0].off()
    if scale_value == 1:
        pins[2].off()
        pins[1].on()
        pins[0].on()
    if scale_value == 2:
        pins[2].on()
        pins[1].off()
        pins[0].off()
    if scale_value == 3:
        pins[2].on()
        pins[1].off()
        pins[0].on()
    if scale_value == 4:
        pins[2].on()
        pins[1].on()
        pins[0].off()

def increment():
    global scale_value
    scale_value = (scale_value + 1) % 5
    update_outputs()

def decrement():
    global scale_value
    scale_value = (scale_value - 1) % 5
    update_outputs()

def send_all_data():
    try:
        value_nA = convert_to_nA(scaled_voltage, scale_units[scale_value])
        msg = {
            "ts": time.time(),
            input_key: float(value_nA)
        }
        msg_bytes = json.dumps(msg).encode('utf-8')
        sock.sendto(msg_bytes, (UDP_IP, UDP_PORT))
    except Exception as e:
        print("UDP send error:", e)

# converts all values to nA for easier graphing
def convert_to_nA(value, unit):
    if unit == "μA":
        return value * 1e3
    else:
        return value


# Main loop
running = True
clock = pygame.time.Clock()
btn_up.when_pressed = increment
btn_down.when_pressed = decrement
cup_btn_up.when_pressed = increment_cup
cup_btn_down.when_pressed = decrement_cup
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # set cup
    set_cup(activeCup)     

    # oversampling
    raw = read_voltage_oversampled() # default is 4

    # rolling average
    samples.append(raw)
    avg_voltage = sum(samples) / len(samples)

    # Exponential moving average 
    voltage = apply_ema(avg_voltage)

    # less abrupt zero clamp
    if abs(voltage) < DEADBAND:
        voltage *= 0.2

    scaled_voltage = voltage * scale_voltage_multipliers[scale_value]

    draw_screen(voltage, scaled_voltage)

    # UDP packet send at reduced rate
    now = time.time()
    if now - last_udp_time > UDP_INTERVAL:
        send_all_data()
        last_udp_time = now

    try:
        data, addr = sock.recvfrom(1024)
        cmd = data.decode().strip()
        if cmd == "UP":
            increment()
        elif cmd == "DOWN":
            decrement()
        elif cmd == "CUP_UP":
            increment_cup()
        elif cmd == "CUP_DOWN":
            decrement_cup()
    except BlockingIOError:
        pass

    # saving a frame at a set interval to mirror on web
    now = time.time()
    if now - last_save_time > SAVE_INTERVAL:
        pygame.image.save(canvas, "/tmp/frame_tmp.jpg")
        os.replace("/tmp/frame_tmp.jpg", "/tmp/frame.jpg") # flicker reducing swap
        last_save_time = now

    clock.tick(60)  # FPS

pygame.quit()